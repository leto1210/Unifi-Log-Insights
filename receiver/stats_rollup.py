"""Hourly pre-aggregates of `logs` for the dashboard's low-cardinality widgets.

`logs_hourly_stats` holds per-hour counts over three grouping sets, told
apart by `dim` (= GROUPING(geo_country, service_name)):

    DIM_BASE     (log_type, rule_action, direction)               → totals, by_type,
                                                                     by_direction, charts
    DIM_COUNTRY  (log_type, rule_action, direction, geo_country)  → top countries
    DIM_SERVICE  (log_type, rule_action, service_name)            → top services

`logs_hourly_ip_stats` holds per-hour, per-IP counts (plus the MAX() detail
columns the top-N tables show) for the three IP slices in `_IP_KINDS`. Its
cardinality is bounded by distinct IPs per hour (scanners, destinations), far
below the raw rows the per-IP tables used to scan.

`logs_hourly_stats_hours` lists the hours that have been computed, so an
hour with no logs is distinguishable from one not rolled up yet. Its
`version` lets a schema change (new table or dimension) re-backfill every
hour without a destructive migration: hours below ROLLUP_VERSION count as
missing on both the write and the read side.

Write side (receiver process): `StatsRollupTask` recomputes the last
`RECENT_HOURS` closed hours every `REFRESH_INTERVAL_SECS` (late Pi-hole /
syslog arrivals), then backfills older hours newest-first, one hour per
statement with a pause between, so 7d/24h benefit first and ingest I/O is
not starved.

Read side (API): `plan()` returns the closed-hour span the rollup fully
covers; `counts()` sums raw `logs` on the partial edges and the rollup in the
middle. Ranges under `MIN_RANGE` or not fully covered stay on raw `logs`.

Not rolled up on purpose: threat_score (backfilled hours/days after insert);
readers re-join `ip_threats` for the current score instead.

Dependency-free (no db/deps imports) so the API and tests can import it alone.
"""

import logging
import threading
import time
from datetime import datetime, timedelta, timezone

logger = logging.getLogger('stats_rollup')

HOUR = timedelta(hours=1)
DIM_COUNTRY, DIM_SERVICE, DIM_BASE = 1, 2, 3
ROLLUP_VERSION = 2  # 2: + logs_hourly_ip_stats

# Per-IP slices: kind → (IP column, filter). Runtime filters (WAN/gateway
# exclusions, public/private split of blocked sources) are left to readers.
IP_BLOCKED_SRC, IP_ALLOWED_INTERNAL_SRC, IP_ALLOWED_PUBLIC_DST = 1, 2, 3
_IP_KINDS = {
    IP_BLOCKED_SRC: ('src_ip', "rule_action = 'block' AND src_ip IS NOT NULL"),
    IP_ALLOWED_INTERNAL_SRC: ('src_ip', "rule_action = 'allow' AND src_ip IS NOT NULL "
                                        "AND NOT is_public_inet(src_ip)"),
    IP_ALLOWED_PUBLIC_DST: ('dst_ip', "rule_action = 'allow' AND is_public_inet(dst_ip)"),
}

REFRESH_INTERVAL_SECS = 300
RECENT_HOURS = 2            # closed hours recomputed on every refresh
BACKFILL_PAUSE_SECS = 2.0   # between backfilled hours
MIN_RANGE = timedelta(hours=24)  # shorter ranges are cheap enough raw

# Columns usable in counts() WHERE clauses: present in both logs and the rollup.
# `{ts}` in a group expression is replaced by `timestamp` (raw) or `hour` (rollup).

_ROLLUP_SQL = """
    INSERT INTO logs_hourly_stats
        (hour, dim, log_type, rule_action, direction, geo_country, service_name, count)
    SELECT %(h)s, GROUPING(geo_country, service_name),
           log_type, rule_action, direction, geo_country, service_name, COUNT(*)
    FROM logs
    WHERE timestamp >= %(h)s AND timestamp < %(h)s + interval '1 hour'
    GROUP BY GROUPING SETS (
        (log_type, rule_action, direction),
        (log_type, rule_action, direction, geo_country),
        (log_type, rule_action, service_name)
    )
"""


def _ip_raw_sql(kind: int, bounded: bool) -> str:
    """Per-(ip, log_type) partial aggregate of raw logs for one kind.

    Columns: ip, log_type, n, last_seen, geo_country, geo_city, asn_name, rdns.

    Binds timestamp >= %s, plus < %s when bounded.
    """
    col, where = _IP_KINDS[kind]
    return (f"SELECT {col} AS ip, log_type, COUNT(*) AS n, MAX(timestamp) AS last_seen, "
            "MAX(geo_country) AS geo_country, MAX(geo_city) AS geo_city, "
            "MAX(asn_name) AS asn_name, MAX(rdns) AS rdns "
            "FROM logs WHERE timestamp >= %s" + (" AND timestamp < %s" if bounded else "")
            + f" AND {where} GROUP BY {col}, log_type")


def floor_hour(ts: datetime) -> datetime:
    """Truncate a datetime to the start of its hour."""
    return ts.replace(minute=0, second=0, microsecond=0)


def ceil_hour(ts: datetime) -> datetime:
    """Round a datetime up to the next hour boundary (unchanged if already on one)."""
    floored = floor_hour(ts)
    return floored if floored == ts else floored + HOUR


# ── Write side ────────────────────────────────────────────────────────────────

def rollup_hour(db, hour: datetime) -> None:
    """(Re)compute one hour from raw logs and mark it covered, atomically."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM logs_hourly_stats WHERE hour = %s", [hour])
            cur.execute(_ROLLUP_SQL, {'h': hour})
            cur.execute("DELETE FROM logs_hourly_ip_stats WHERE hour = %s", [hour])
            for kind in _IP_KINDS:
                cur.execute(
                    "INSERT INTO logs_hourly_ip_stats (hour, kind, ip, log_type, count, last_seen, "
                    "geo_country, geo_city, asn_name, rdns) "
                    f"SELECT %s, %s, r.* FROM ({_ip_raw_sql(kind, True)}) r",
                    [hour, kind, hour, hour + HOUR],
                )
            cur.execute(
                "INSERT INTO logs_hourly_stats_hours (hour, version) VALUES (%s, %s) "
                "ON CONFLICT (hour) DO UPDATE SET computed_at = NOW(), version = EXCLUDED.version",
                [hour, ROLLUP_VERSION],
            )


def purge(db, general_days: int, dns_days: int) -> None:
    """Drop rollup rows past retention, mirroring the general/DNS split of logs."""
    now = datetime.now(timezone.utc)
    general_cutoff = now - timedelta(days=general_days)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            for table in ('logs_hourly_stats', 'logs_hourly_ip_stats', 'logs_hourly_stats_hours'):
                cur.execute(f"DELETE FROM {table} WHERE hour < %s", [general_cutoff])
            for table in ('logs_hourly_stats', 'logs_hourly_ip_stats'):
                cur.execute(f"DELETE FROM {table} WHERE log_type = 'dns' AND hour < %s",
                            [now - timedelta(days=dns_days)])


def _next_missing_hour(db, horizon: datetime, last_closed: datetime):
    """Newest hour in [horizon, last_closed] not rolled up yet, or None."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT h FROM generate_series(%s::timestamptz, %s::timestamptz, interval '1 hour') h "
                "WHERE NOT EXISTS (SELECT 1 FROM logs_hourly_stats_hours c "
                "                 WHERE c.hour = h AND c.version >= %s) "
                "ORDER BY h DESC LIMIT 1",
                [horizon, last_closed, ROLLUP_VERSION],
            )
            row = cur.fetchone()
            return row[0] if row else None


def _backfill_horizon(db, retention_days: int, now: datetime):
    """Oldest hour worth rolling up: the oldest log, but no further back than retention."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT MIN(timestamp) FROM logs")
            oldest = cur.fetchone()[0]
    if oldest is None:
        return None
    return floor_hour(max(oldest, now - timedelta(days=retention_days)))


class StatsRollupTask:
    """Daemon thread keeping logs_hourly_stats fresh and backfilling history."""

    def __init__(self, db, retention_days_fn):
        """retention_days_fn() returns the current general retention in days."""
        self.db = db
        self._retention_days = retention_days_fn

    def start(self):
        """Start the background thread."""
        threading.Thread(target=self._run, name='stats-rollup', daemon=True).start()

    def run_once(self, budget_secs: float = REFRESH_INTERVAL_SECS) -> int:
        """Refresh recent hours, then backfill until the budget is spent. Returns hours backfilled."""
        now = datetime.now(timezone.utc)
        last_closed = floor_hour(now) - HOUR
        for i in range(RECENT_HOURS):
            rollup_hour(self.db, last_closed - i * HOUR)

        horizon = _backfill_horizon(self.db, self._retention_days(), now)
        if horizon is None:
            return 0
        deadline = time.monotonic() + budget_secs
        done, oldest = 0, None
        while time.monotonic() < deadline:
            hour = _next_missing_hour(self.db, horizon, last_closed)
            if hour is None:
                break
            rollup_hour(self.db, hour)
            done, oldest = done + 1, hour
            time.sleep(BACKFILL_PAUSE_SECS)
        if done:
            logger.info("Stats rollup backfilled %d hour(s), oldest now %s", done, oldest.isoformat())
        return done

    def _run(self):
        """Loop forever; a failed pass is logged and retried next interval."""
        while True:
            started = time.monotonic()
            try:
                self.run_once()
            except Exception:
                logger.exception("Stats rollup pass failed")
            time.sleep(max(1.0, REFRESH_INTERVAL_SECS - (time.monotonic() - started)))


# ── Read side ────────────────────────────────────────────────────────────────

def plan(cur, cutoff: datetime, now: datetime):
    """Return (h0, h1): the closed-hour span [h0, h1) served by the rollup, or None.

    None means: range too short, or the rollup does not cover every hour from
    ceil_hour(cutoff) contiguously (e.g. backfill still running) — callers then
    query raw logs exactly as before. Expects a dict-row cursor.
    """
    if now - cutoff < MIN_RANGE:
        return None
    h0 = ceil_hour(cutoff)
    cur.execute(
        "SELECT COUNT(*) AS n, MAX(hour) AS last FROM logs_hourly_stats_hours "
        "WHERE hour >= %s AND hour < %s AND version >= %s",
        [h0, floor_hour(now), ROLLUP_VERSION],
    )
    row = cur.fetchone()
    if not row or not row['n']:
        return None
    # hour is a primary key, so n rows ending at `last` are contiguous from h0.
    if h0 + (row['n'] - 1) * HOUR != row['last']:
        return None
    return h0, row['last'] + HOUR


def counts(cur, cutoff: datetime, span, group, where: str = 'TRUE', params=(),
           dim: int = DIM_BASE) -> dict:
    """{group-values tuple: count} over [cutoff, now): raw edges + rollup middle.

    group: [(alias, sql_expr)], where sql_expr may use `{ts}` for the time column.
    where: SQL on columns shared by logs and the rollup; params bind its %s.
    span: (h0, h1) from plan().
    """
    h0, h1 = span
    aliases = [a for a, _ in group]
    result = {}

    def run(table_sql, ts_col, count_sql, lo, hi, extra_where='', extra_params=()):
        """Run one grouped count and add it into result."""
        cols = ', '.join(f"{expr.format(ts=ts_col)} AS {alias}" for alias, expr in group)
        sql = (f"SELECT {cols + ', ' if cols else ''}{count_sql} AS n FROM {table_sql} "
               f"WHERE {ts_col} >= %s" + (f" AND {ts_col} < %s" if hi else '')
               + extra_where + f" AND ({where})")
        if aliases:
            sql += " GROUP BY " + ', '.join(aliases)
        cur.execute(sql, [lo] + ([hi] if hi else []) + list(extra_params) + list(params))
        for r in cur.fetchall():
            key = tuple(r[a] for a in aliases)
            result[key] = result.get(key, 0) + int(r['n'] or 0)

    if cutoff < h0:
        run('logs', 'timestamp', 'COUNT(*)', cutoff, h0)
    run('logs_hourly_stats', 'hour', 'SUM(count)', h0, h1, ' AND dim = %s', [dim])
    run('logs', 'timestamp', 'COUNT(*)', h1, None)  # open-ended, like the raw queries
    return result


def ip_source(cutoff: datetime, span, kind: int):
    """(sql, params): a FROM-clause relation `u` of per-IP partial aggregates over [cutoff, now).

    Columns as in _ip_raw_sql(), one row per (part, ip, log_type): callers re-aggregate
    with GROUP BY ip — SUM(n), MAX() of the rest — and can filter on `ip`.
    span None (plan() declined) → raw logs only; otherwise raw head + rollup
    middle + open raw tail, as in counts(), but in one statement so the
    caller's ORDER BY … LIMIT ranks the merged totals.
    """
    # ponytail: cost is distinct IPs/hour × hours (~6 s for 7d at 38k allowed
    # destinations/hour); add a daily compaction of logs_hourly_ip_stats if
    # 30d+ ranges must answer that fast too.
    if span is None:
        return f"({_ip_raw_sql(kind, False)}) AS u", [cutoff]
    h0, h1 = span
    parts, params = [], []
    if cutoff < h0:
        parts.append(_ip_raw_sql(kind, True))
        params += [cutoff, h0]
    parts.append("SELECT ip, log_type, count AS n, last_seen, geo_country, geo_city, asn_name, rdns "
                 "FROM logs_hourly_ip_stats WHERE hour >= %s AND hour < %s AND kind = %s")
    params += [h0, h1, kind]
    parts.append(_ip_raw_sql(kind, False))
    params.append(h1)
    return "(" + " UNION ALL ".join(parts) + ") AS u", params
