"""Daily RANGE partitioning of `logs` on `timestamp` (UTC days).

Shape:
    logs                    partitioned parent (relkind 'p'), no PRIMARY KEY
                            (it would have to include timestamp); idx_logs_id
                            is a plain index on id instead.
    logs_pYYYYMMDD          one partition per UTC day, created DAYS_AHEAD ahead.
    logs_default            DEFAULT partition: catches rows whose timestamp has
                            no day partition (device clock far off). Rows of a
                            day are moved out when that day's partition is created.
    logs_legacy             only on migrated installs: the former plain table,
                            attached FROM (MINVALUE) TO (cutover). Dropped whole
                            once it is entirely past retention.

Every helper is a no-op on a plain (unmigrated) `logs`, so callers need not
branch. PostgreSQL refuses DETACH ... CONCURRENTLY while a DEFAULT partition
exists, so expired partitions are dropped with a plain DROP TABLE bounded by
a short lock_timeout and retried on the next pass when it times out.
"""

import logging
from datetime import date, datetime, time as dtime, timedelta, timezone

logger = logging.getLogger('db.partitioning')

DEFAULT_PARTITION = 'logs_default'
LEGACY_PARTITION = 'logs_legacy'
DAYS_AHEAD = 7
DDL_LOCK_TIMEOUT = '2s'   # partition create/drop: never queue ingestion for long
INDEX_DROP_LOCK_TIMEOUT = '5s'

_RELKIND_SQL = ("SELECT c.relkind FROM pg_class c "
                "JOIN pg_namespace n ON n.oid = c.relnamespace "
                "WHERE n.nspname = 'public' AND c.relname = 'logs'")

# Upper bound of each direct partition (NULL for DEFAULT / MAXVALUE).
_BOUNDS_SQL = r"""
    SELECT c.relname,
           substring(pg_get_expr(c.relpartbound, c.oid) FROM $$TO \('([^']+)'\)$$)::timestamptz
    FROM pg_inherits i
    JOIN pg_class c ON c.oid = i.inhrelid
    WHERE i.inhparent = 'public.logs'::regclass
    ORDER BY c.relname
"""

# Row estimate that works for both shapes: sum of leaf partitions, or the plain
# table itself (pg_partition_tree returns no rows for a non-partitioned table).
# The parent of a partitioned table gets its own reltuples after ANALYZE, so it
# must not be added to the leaves.
LOGS_ROW_ESTIMATE_SQL = """
    SELECT COALESCE(
        (SELECT SUM(GREATEST(c.reltuples, 0))
           FROM pg_partition_tree('public.logs') t
           JOIN pg_class c ON c.oid = t.relid
          WHERE t.isleaf),
        (SELECT GREATEST(c.reltuples, 0)
           FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
          WHERE n.nspname = 'public' AND c.relname = 'logs'),
        0)::bigint
"""


def is_partitioned(cur) -> bool:
    """True when public.logs is a partitioned table (tuple-row cursor)."""
    cur.execute(_RELKIND_SQL)
    row = cur.fetchone()
    return bool(row) and row[0] == 'p'


def partition_name(day: date) -> str:
    """Name of the partition holding one UTC day, e.g. logs_p20261205."""
    return f"logs_p{day:%Y%m%d}"


def day_bounds(day: date) -> tuple[datetime, datetime]:
    """[start, end) of a UTC day as aware datetimes."""
    start = datetime.combine(day, dtime.min, tzinfo=timezone.utc)
    return start, start + timedelta(days=1)


def partition_bounds(cur) -> list[tuple[str, datetime | None]]:
    """(name, upper bound) of every direct partition of logs; None = DEFAULT/MAXVALUE."""
    cur.execute(_BOUNDS_SQL)
    return [(name, upper) for name, upper in cur.fetchall()]


def _create_day_partition(cur, day: date) -> None:
    """Create one day partition, moving that day's rows out of DEFAULT first.

    PostgreSQL rejects the CREATE while logs_default holds rows of the new
    range, so they are lifted into a temp table and re-inserted (now routed
    to the new partition) in the same transaction.
    """
    start, end = day_bounds(day)
    name = partition_name(day)
    cur.execute(
        f"CREATE TEMP TABLE _moved ON COMMIT DROP AS "
        f"WITH d AS (DELETE FROM {DEFAULT_PARTITION} "
        f"           WHERE timestamp >= %s AND timestamp < %s RETURNING *) "
        f"SELECT * FROM d", [start, end])
    cur.execute(f"CREATE TABLE {name} PARTITION OF logs FOR VALUES FROM (%s) TO (%s)",
                [start, end])
    cur.execute("INSERT INTO logs SELECT * FROM _moved")
    moved = cur.rowcount
    if moved:
        logger.info("Partition %s created; moved %d row(s) out of %s",
                    name, moved, DEFAULT_PARTITION)
    else:
        logger.info("Partition %s created", name)


def ensure_partitions(db, days_ahead: int = DAYS_AHEAD, today: date | None = None) -> list[str]:
    """Create missing day partitions from today to today + days_ahead.

    No-op on a plain logs table. Each partition is its own transaction with a
    short lock_timeout; a failure is logged and retried on the next call
    (partitions are created a week ahead, so there is ample time).
    """
    today = today or datetime.now(timezone.utc).date()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            if not is_partitioned(cur):
                return []
            existing = {name for name, _ in partition_bounds(cur)}
    created = []
    for offset in range(days_ahead + 1):
        day = today + timedelta(days=offset)
        if partition_name(day) in existing:
            continue
        try:
            with db.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"SET LOCAL lock_timeout = '{DDL_LOCK_TIMEOUT}'")
                    _create_day_partition(cur, day)
            created.append(partition_name(day))
        except Exception as e:
            logger.warning("Could not create partition %s (will retry): %s",
                           partition_name(day), e)
    return created


def drop_expired_partitions(db, cutoff: datetime) -> list[str]:
    """Drop every partition whose upper bound is <= cutoff (never DEFAULT).

    Includes logs_legacy once its cutover is past retention. No-op on a plain
    table. A lock timeout skips that partition until the next pass.
    """
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            if not is_partitioned(cur):
                return []
            expired = [name for name, upper in partition_bounds(cur)
                       if upper is not None and upper <= cutoff]
    dropped = []
    for name in expired:
        try:
            with db.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"SET LOCAL lock_timeout = '{DDL_LOCK_TIMEOUT}'")
                    cur.execute(f"DROP TABLE {name}")
            dropped.append(name)
            logger.info("Retention dropped partition %s", name)
        except Exception as e:
            logger.warning("Could not drop partition %s (will retry): %s", name, e)
    return dropped


# ── Online index maintenance (autocommit connection) ─────────────────────────

def create_index_online(conn, name: str, definition: str) -> None:
    """Build a partitioned index without blocking writes; resumable.

    CREATE INDEX CONCURRENTLY is impossible on a partitioned parent, so: an
    (invalid) parent index ON ONLY logs, then CONCURRENTLY on each partition
    and ATTACH; the parent turns valid once every partition is attached.
    `definition` is everything after `ON logs`, e.g. "(log_type, id)".
    `conn` must be in autocommit mode.
    """
    with conn.cursor() as cur:
        cur.execute(f"CREATE INDEX IF NOT EXISTS {name} ON ONLY logs {definition}")
        cur.execute(
            "SELECT c.relname FROM pg_inherits i JOIN pg_class c ON c.oid = i.inhrelid "
            "WHERE i.inhparent = 'public.logs'::regclass ORDER BY c.relname")
        partitions = [r[0] for r in cur.fetchall()]
        for part in partitions:
            cur.execute(
                "SELECT 1 FROM pg_inherits i JOIN pg_index x ON x.indexrelid = i.inhrelid "
                "WHERE i.inhparent = %s::regclass AND x.indrelid = %s::regclass",
                [name, part])
            if cur.fetchone():
                continue  # this partition's index is already attached
            child = f"{name}__{part}"
            cur.execute(f"CREATE INDEX CONCURRENTLY IF NOT EXISTS {child} ON {part} {definition}")
            cur.execute(f"ALTER INDEX {name} ATTACH PARTITION {child}")


def drop_index(conn, name: str) -> None:
    """Drop a partitioned index (and its partition indexes) under a short lock_timeout.

    DROP INDEX CONCURRENTLY is impossible on a partitioned index; the plain
    DROP holds its lock for milliseconds, lock_timeout bounds the wait.
    """
    with conn.cursor() as cur:
        cur.execute(f"SET lock_timeout = '{INDEX_DROP_LOCK_TIMEOUT}'")
        cur.execute(f"DROP INDEX IF EXISTS {name}")
