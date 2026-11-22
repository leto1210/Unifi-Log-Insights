"""Convert an existing plain `logs` table into daily partitions, online and resumably.

Run inside the app container, when you choose (never automatic):

    python -m db.migrate_partitions --dry-run   # show the plan, change nothing
    python -m db.migrate_partitions --yes       # migrate
    python -m db.migrate_partitions --abort     # undo phases 2-3 (before the swap only)

The current table becomes the partition `logs_legacy` covering everything
before a cutover date (UTC midnight, 48-72 h ahead); new day partitions
start at the cutover. History stays queryable, and logs_legacy is dropped
whole by retention once it is entirely expired.

Phases — each checks its own state, so re-running resumes where it stopped:
  1. cutover  pick and store the cutover date (system_config.logs_partition_cutover)
  2. twin     CREATE INDEX CONCURRENTLY idx_logs_id_legacy ON logs (id): the
              partitioned parent's idx_logs_id cannot reuse the unique PK
  3. bound    ADD CHECK (timestamp < cutover) NOT VALID, then VALIDATE
              (one full scan, inserts keep flowing) so ATTACH needs no scan
  4. swap     one short transaction (lock_timeout 5 s, retried): new
              partitioned parent with the same indexes, renames, sequence
              re-owned, ATTACH logs_legacy, DEFAULT + day partitions
  5. analyze  ANALYZE logs (planner statistics for the new parent)

Between phase 3 and the swap, a row timestamped at or after the cutover is
rejected by the CHECK. The command drops the CHECK again if it fails before
the swap, and the receiver's hourly partition job drops a leftover CHECK
whose cutover is less than a day away (see partitioning.heal_stale_bound).
"""

import argparse
import logging
import re
import sys
import time
from datetime import datetime, time as dtime, timedelta, timezone

import psycopg2
from psycopg2.extras import Json

from . import partitioning
from .connection import build_conn_params
from .schema import POST_BOOT_DROPS

logger = logging.getLogger('db.migrate_partitions')

MIN_SERVER_VERSION = 120000          # pg_partition_tree, ATTACH under SHARE UPDATE EXCLUSIVE
ID_TWIN = 'idx_logs_id_legacy'
PROBE = 'logs_attach_probe'
CUTOVER_KEY = 'logs_partition_cutover'
SWAP_LOCK_TIMEOUT = '5s'
SWAP_ATTEMPTS = 10
SWAP_RETRY_PAUSE_SECS = 10
LEAD_TIME = timedelta(hours=48)      # cutover is the first UTC midnight after now + 48 h

_DROPPED_NAMES = {name for name, _sql in POST_BOOT_DROPS}
_INDEXDEF_RE = re.compile(r'^CREATE INDEX (\S+) ON public\.logs (USING .+)$')


class MigrationError(RuntimeError):
    """The migration cannot proceed safely; nothing irreversible was done."""


def bound_constraint_name(cutover: datetime) -> str:
    """CHECK constraint name; the date in it lets a stale bound be recognised."""
    return f"logs_legacy_before_{cutover:%Y%m%d}"


def next_cutover(now: datetime) -> datetime:
    """First UTC midnight at least LEAD_TIME after now."""
    return datetime.combine((now + LEAD_TIME).date() + timedelta(days=1), dtime.min,
                            tzinfo=timezone.utc)


def _connect():
    """Autocommit connection (CONCURRENTLY/VALIDATE need it), no statement timeout."""
    conn = psycopg2.connect(**build_conn_params())
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SET statement_timeout = 0")
    return conn


def _one(cur, sql, args=None):
    """First column of the first row, or None."""
    cur.execute(sql, args)
    row = cur.fetchone()
    return row[0] if row else None


def _relkind(cur):
    """relkind of public.logs ('r' plain, 'p' partitioned)."""
    return _one(cur, "SELECT c.relkind FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
                     "WHERE n.nspname = 'public' AND c.relname = 'logs'")


def _stored_cutover(cur):
    """Cutover saved by phase 1, or None."""
    raw = _one(cur, "SELECT value FROM system_config WHERE key = %s", [CUTOVER_KEY])
    return datetime.fromisoformat(raw) if raw else None


def _store_cutover(cur, cutover):
    """Persist (or clear, when None) the cutover so a re-run reuses it."""
    if cutover is None:
        cur.execute("DELETE FROM system_config WHERE key = %s", [CUTOVER_KEY])
        return
    cur.execute("INSERT INTO system_config (key, value, updated_at) VALUES (%s, %s, NOW()) "
                "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()",
                [CUTOVER_KEY, Json(cutover.isoformat())])


def _bound_constraints(cur):
    """{name: validated} of logs_legacy_before_* CHECKs on logs."""
    cur.execute("SELECT conname, convalidated FROM pg_constraint "
                "WHERE conrelid = 'public.logs'::regclass AND conname LIKE 'logs_legacy_before_%'")
    return dict(cur.fetchall())


def inspect_plan(cur, now=None):
    """Read-only plan: what each phase would do. Raises MigrationError if unsafe."""
    now = now or datetime.now(timezone.utc)
    version = int(_one(cur, "SHOW server_version_num"))
    if version < MIN_SERVER_VERSION:
        raise MigrationError(f"PostgreSQL {version} is too old; 12 or later is required")
    kind = _relkind(cur)
    if kind == 'p':
        return {'done': True}
    if kind != 'r':
        raise MigrationError("public.logs not found")

    cur.execute("""
        SELECT c.relname, pg_get_indexdef(i.indexrelid), i.indisvalid, i.indisunique,
               i.indisprimary, pg_relation_size(i.indexrelid)
        FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid
        WHERE i.indrelid = 'public.logs'::regclass ORDER BY c.relname""")
    twins, skipped, pkey_bytes = [], [], 0
    for name, indexdef, valid, unique, primary, size in cur.fetchall():
        if primary:
            pkey_bytes = size
            skipped.append((name, 'primary key: replaced by idx_logs_id on the parent'))
        elif name == ID_TWIN:
            continue
        elif unique:
            raise MigrationError(f"unique index {name}: a partitioned table cannot enforce it")
        elif not valid:
            skipped.append((name, 'invalid (interrupted build): stays on logs_legacy only'))
        elif name in _DROPPED_NAMES:
            skipped.append((name, 'scheduled for drop: stays on logs_legacy only'))
        else:
            m = _INDEXDEF_RE.match(indexdef)
            if not m or m.group(1) != name:
                raise MigrationError(f"unexpected definition for {name}: {indexdef}")
            twins.append((name, m.group(2)))

    stored = _stored_cutover(cur)
    cutover = stored if stored and stored - now >= timedelta(days=1) else next_cutover(now)
    # Rows already dated at/after the cutover (device clock ahead) would make
    # VALIDATE fail: refuse up front with the fix. Index range count, fast.
    ahead = _one(cur, "SELECT count(*) FROM logs WHERE timestamp >= %s", [cutover])
    if ahead:
        raise MigrationError(
            f"{ahead} row(s) are timestamped at/after the cutover {cutover.isoformat()} "
            f"(device clock ahead). Remove them first: "
            f"DELETE FROM logs WHERE timestamp >= '{cutover.isoformat()}';")
    twin_valid = _one(cur, "SELECT i.indisvalid FROM pg_index i WHERE i.indexrelid = to_regclass(%s)",
                      [f'public.{ID_TWIN}'])
    return {
        'done': False,
        'server_version': version,
        'rows_estimate': _one(cur, partitioning.LOGS_ROW_ESTIMATE_SQL),
        'cutover': cutover,
        'twin_needed': twin_valid is not True,
        'twin_bytes_estimate': pkey_bytes,
        'bound': _bound_constraints(cur),
        'parent_indexes': twins,
        'skipped_indexes': skipped,
    }


def _ensure_twin(cur):
    """Phase 2: valid non-unique id index on the plain table (rebuilt if a prior build died)."""
    valid = _one(cur, "SELECT i.indisvalid FROM pg_index i WHERE i.indexrelid = to_regclass(%s)",
                 [f'public.{ID_TWIN}'])
    if valid is True:
        return False
    if valid is False:
        cur.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {ID_TWIN}")
    cur.execute(f"CREATE INDEX CONCURRENTLY {ID_TWIN} ON logs (id)")
    return True


def _with_lock_retries(cur, statements, attempts=SWAP_ATTEMPTS):
    """Run statements in one transaction under SWAP_LOCK_TIMEOUT, retrying lock timeouts."""
    for attempt in range(1, attempts + 1):
        try:
            cur.execute("BEGIN")
            cur.execute(f"SET LOCAL lock_timeout = '{SWAP_LOCK_TIMEOUT}'")
            for sql, args in statements(cur):
                cur.execute(sql, args)
            cur.execute("COMMIT")
            return attempt
        except psycopg2.errors.LockNotAvailable:
            cur.execute("ROLLBACK")
            logger.warning("Lock not available (attempt %d/%d), retrying in %ds",
                           attempt, attempts, SWAP_RETRY_PAUSE_SECS)
            time.sleep(SWAP_RETRY_PAUSE_SECS)
        except Exception:
            cur.execute("ROLLBACK")
            raise
    raise MigrationError(f"could not get the lock on logs after {attempts} attempts; "
                         "re-run when the dashboard is idle")


def _ensure_bound(cur, cutover):
    """Phase 3: exactly one CHECK (timestamp < cutover), validated."""
    wanted = bound_constraint_name(cutover)
    existing = _bound_constraints(cur)
    for name in existing:
        if name != wanted:
            _with_lock_retries(cur, lambda _c, n=name: [(f"ALTER TABLE logs DROP CONSTRAINT {n}", None)])
    if wanted not in existing:
        _with_lock_retries(cur, lambda _c: [(
            f"ALTER TABLE logs ADD CONSTRAINT {wanted} CHECK (timestamp < %s) NOT VALID", [cutover])])
    if not existing.get(wanted):
        cur.execute(f"ALTER TABLE logs VALIDATE CONSTRAINT {wanted}")


def _swap_statements(parent_indexes, cutover):
    """Phase 4 statements, generated inside the swap transaction."""
    def gen(cur):
        """Yield (sql, args) for the swap; validity is checked before COMMIT."""
        yield "LOCK TABLE logs IN ACCESS EXCLUSIVE MODE", None
        yield "CREATE TABLE logs_part (LIKE logs INCLUDING DEFAULTS) PARTITION BY RANGE (timestamp)", None
        yield f"CREATE INDEX idx_logs_id ON logs_part USING btree (id)", None
        for name, definition in parent_indexes:
            yield f"ALTER INDEX {name} RENAME TO {name}_legacy", None
            yield f"CREATE INDEX {name} ON logs_part {definition}", None
        yield f"ALTER TABLE logs RENAME TO {partitioning.LEGACY_PARTITION}", None
        yield "ALTER TABLE logs_part RENAME TO logs", None
        yield "ALTER SEQUENCE logs_id_seq OWNED BY logs.id", None
        # Probe: ATTACH silently *builds* any parent index it cannot match, which
        # on logs_legacy would run for minutes under this lock. Attach an empty
        # copy carrying the same indexes first; if PostgreSQL had to add one,
        # abort before touching the real table.
        yield (f"CREATE TABLE {PROBE} (LIKE {partitioning.LEGACY_PARTITION} INCLUDING INDEXES)", None)
        before = _one(cur, f"SELECT count(*) FROM pg_index WHERE indrelid = 'public.{PROBE}'::regclass")
        yield f"ALTER TABLE logs ATTACH PARTITION {PROBE} FOR VALUES FROM (MINVALUE) TO (%s)", [cutover]
        after = _one(cur, f"SELECT count(*) FROM pg_index WHERE indrelid = 'public.{PROBE}'::regclass")
        if after != before:
            raise MigrationError(
                f"{after - before} parent index(es) match no index of logs_legacy, so ATTACH "
                "would rebuild them under lock; aborted, nothing changed")
        yield f"ALTER TABLE logs DETACH PARTITION {PROBE}", None
        yield f"DROP TABLE {PROBE}", None
        # The validated CHECK proves the bound: no scan; identical indexes attach as-is.
        yield (f"ALTER TABLE logs ATTACH PARTITION {partitioning.LEGACY_PARTITION} "
               f"FOR VALUES FROM (MINVALUE) TO (%s)", [cutover])
        yield f"CREATE TABLE {partitioning.DEFAULT_PARTITION} PARTITION OF logs DEFAULT", None
        for offset in range(partitioning.DAYS_AHEAD + 1):
            day = cutover.date() + timedelta(days=offset)
            start, end = partitioning.day_bounds(day)
            yield (f"CREATE TABLE {partitioning.partition_name(day)} PARTITION OF logs "
                   f"FOR VALUES FROM (%s) TO (%s)", [start, end])
        # Guard: an index ATTACH could not match would leave the parent invalid
        # (and a later CREATE would rebuild under lock). Abort instead.
        invalid = _one(cur, "SELECT string_agg(c.relname, ', ') FROM pg_index i "
                            "JOIN pg_class c ON c.oid = i.indexrelid "
                            "WHERE i.indrelid = 'public.logs'::regclass AND NOT i.indisvalid")
        if invalid:
            raise MigrationError(f"parent index(es) left invalid after ATTACH: {invalid}")
    return gen


def migrate(conn, out=print, now=None):
    """Run every pending phase. Returns a summary dict (with 'swap_seconds')."""
    with conn.cursor() as cur:
        plan = inspect_plan(cur, now)
        if plan['done']:
            out("logs is already partitioned — nothing to do.")
            return {'already_done': True}
        cutover = plan['cutover']
        _store_cutover(cur, cutover)
        out(f"[1/5] cutover: {cutover.isoformat()}")

        try:
            t = time.monotonic()
            built = _ensure_twin(cur)
            out(f"[2/5] {ID_TWIN}: {'built' if built else 'already valid'} "
                f"({time.monotonic() - t:.1f}s)")

            t = time.monotonic()
            _ensure_bound(cur, cutover)
            out(f"[3/5] {bound_constraint_name(cutover)}: validated ({time.monotonic() - t:.1f}s)")

            t = time.monotonic()
            attempts = _with_lock_retries(cur, _swap_statements(plan['parent_indexes'], cutover))
            swap_seconds = time.monotonic() - t
            out(f"[4/5] swap: done in {swap_seconds:.2f}s (attempt {attempts})")
        except BaseException:
            if _relkind(cur) == 'r':  # swap did not happen: never leave the CHECK armed
                for name in _bound_constraints(cur):
                    try:
                        _with_lock_retries(cur, lambda _c, n=name: [
                            (f"ALTER TABLE logs DROP CONSTRAINT {n}", None)], attempts=3)
                    except Exception:
                        logger.exception("Could not drop %s; the receiver drops it within "
                                         "a day of the cutover", name)
            raise

        t = time.monotonic()
        cur.execute("ANALYZE logs")
        out(f"[5/5] ANALYZE logs ({time.monotonic() - t:.1f}s)")
        _store_cutover(cur, None)
    out(f"Done. {partitioning.LEGACY_PARTITION} holds everything before {cutover:%Y-%m-%d} "
        "and is dropped automatically once it is past retention.")
    return {'already_done': False, 'cutover': cutover, 'swap_seconds': swap_seconds,
            'swap_attempts': attempts}


def abort(conn, out=print):
    """Undo phases 2-3 on a still-plain table (CHECK, twin index, stored cutover)."""
    with conn.cursor() as cur:
        if _relkind(cur) != 'r':
            raise MigrationError("logs is already partitioned: abort only works before the swap")
        for name in _bound_constraints(cur):
            _with_lock_retries(cur, lambda _c, n=name: [(f"ALTER TABLE logs DROP CONSTRAINT {n}", None)])
            out(f"dropped constraint {name}")
        cur.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {ID_TWIN}")
        _store_cutover(cur, None)
        out(f"dropped {ID_TWIN} (if present); logs is back to its pre-migration state")


def _print_plan(plan, out=print):
    """Human-readable dry-run output."""
    if plan['done']:
        out("logs is already partitioned — nothing to do.")
        return
    gib = plan['twin_bytes_estimate'] / 2 ** 30
    out(f"PostgreSQL {plan['server_version']}, ~{plan['rows_estimate']:,} rows in logs")
    out(f"cutover: {plan['cutover'].isoformat()} (rows before it stay in {partitioning.LEGACY_PARTITION})")
    out(f"phase 2: {ID_TWIN} {'to build (~%.1f GiB, CONCURRENTLY)' % gib if plan['twin_needed'] else 'already valid'}")
    out(f"phase 3: bound constraint {'present ' + str(plan['bound']) if plan['bound'] else 'to add + VALIDATE (one full scan)'}")
    out(f"phase 4: parent gets idx_logs_id + {len(plan['parent_indexes'])} index(es):")
    for name, definition in plan['parent_indexes']:
        out(f"    {name}: {definition}")
    for name, reason in plan['skipped_indexes']:
        out(f"    (not on parent) {name}: {reason}")


def main(argv=None):
    """CLI entry point. Exit codes: 0 ok, 1 refused/failed, 2 usage."""
    parser = argparse.ArgumentParser(prog='python -m db.migrate_partitions',
                                     description=__doc__.split('\n\n')[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true', help='show the plan, change nothing')
    mode.add_argument('--yes', action='store_true', help='run the migration')
    mode.add_argument('--abort', action='store_true', help='undo phases 2-3 (before the swap)')
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    conn = _connect()
    try:
        if args.dry_run:
            with conn.cursor() as cur:
                _print_plan(inspect_plan(cur))
        elif args.abort:
            abort(conn)
        else:
            migrate(conn)
        return 0
    except MigrationError as e:
        print(f"Refused: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())
