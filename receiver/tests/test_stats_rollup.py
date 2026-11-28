"""Hourly dashboard rollup: plan/merge logic, and raw-vs-rollup equality on real PostgreSQL.

The equality tests need a disposable PostgreSQL and are skipped unless
ULI_TEST_PG_DSN is set, e.g.:

    docker run -d --rm --name uli-pg -e POSTGRES_PASSWORD=test -p 55432:5432 postgres:16-alpine
    ULI_TEST_PG_DSN="host=127.0.0.1 port=55432 user=postgres password=test dbname=postgres" \
        pytest tests/test_stats_rollup.py

They DROP and recreate `logs` and the rollup tables: never point them at a real install.
"""

import os
import random
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

import stats_rollup
from stats_rollup import HOUR, ceil_hour, floor_hour

NOW = datetime(2026, 11, 22, 20, 17, 42, tzinfo=timezone.utc)


class FakeCursor:
    """Dict-row cursor returning scripted results in order; records executed SQL."""

    def __init__(self, results):
        """results: list of fetchone dicts / fetchall lists, consumed in order."""
        self.results = list(results)
        self.executed = []

    def execute(self, sql, params=None):
        """Record the statement."""
        self.executed.append((sql, params))

    def fetchone(self):
        """Next scripted single row."""
        return self.results.pop(0)

    def fetchall(self):
        """Next scripted row list."""
        return self.results.pop(0)


class TestHourMath:
    def test_floor_and_ceil(self):
        """ceil_hour leaves exact boundaries alone."""
        assert floor_hour(NOW) == NOW.replace(minute=0, second=0)
        assert ceil_hour(NOW) == NOW.replace(minute=0, second=0) + HOUR
        on_boundary = NOW.replace(minute=0, second=0)
        assert ceil_hour(on_boundary) == on_boundary


class TestPlan:
    def test_short_range_stays_raw_without_querying(self):
        """Under MIN_RANGE the rollup is not even consulted."""
        cur = FakeCursor([])
        assert stats_rollup.plan(cur, NOW - timedelta(hours=6), NOW) is None
        assert cur.executed == []

    def test_contiguous_coverage_returns_span(self):
        """n hours ending at `last` from h0 → span [h0, last + 1h)."""
        cutoff = NOW - timedelta(hours=24)
        h0 = ceil_hour(cutoff)
        last = floor_hour(NOW) - HOUR
        n = int((last - h0) / HOUR) + 1
        cur = FakeCursor([{'n': n, 'last': last}])
        assert stats_rollup.plan(cur, cutoff, NOW) == (h0, last + HOUR)

    def test_gap_or_missing_head_falls_back_to_raw(self):
        """A hole (backfill still running) means raw, never a partial answer."""
        cutoff = NOW - timedelta(hours=24)
        last = floor_hour(NOW) - HOUR
        assert stats_rollup.plan(FakeCursor([{'n': 3, 'last': last}]), cutoff, NOW) is None
        assert stats_rollup.plan(FakeCursor([{'n': 0, 'last': None}]), cutoff, NOW) is None


class TestCountsMerge:
    def test_sums_head_rollup_and_tail(self):
        """Raw head [cutoff, h0), rollup [h0, h1) and open raw tail [h1, …) are summed per key."""
        cutoff = NOW - timedelta(hours=24)
        h0, h1 = ceil_hour(cutoff), floor_hour(NOW)
        cur = FakeCursor([
            [{'log_type': 'firewall', 'n': 2}],
            [{'log_type': 'firewall', 'n': 40}, {'log_type': 'dns', 'n': 5}],
            [{'log_type': 'dns', 'n': 1}],
        ])
        result = stats_rollup.counts(cur, cutoff, (h0, h1), [('log_type', 'log_type')])

        assert result == {('firewall',): 42, ('dns',): 6}
        (head_sql, head_p), (mid_sql, mid_p), (tail_sql, tail_p) = cur.executed
        assert 'FROM logs ' in head_sql and head_p == [cutoff, h0]
        assert 'FROM logs_hourly_stats' in mid_sql and mid_p == [h0, h1, stats_rollup.DIM_BASE]
        assert 'FROM logs ' in tail_sql and tail_p == [h1] and 'timestamp <' not in tail_sql


class TestIpSource:
    def test_raw_only_when_plan_declined(self):
        """span None → a single open-ended raw part over [cutoff, …)."""
        cutoff = NOW - timedelta(hours=6)
        sql, params = stats_rollup.ip_source(cutoff, None, stats_rollup.IP_BLOCKED_SRC)
        assert params == [cutoff]
        assert 'logs_hourly_ip_stats' not in sql and 'UNION' not in sql

    def test_head_rollup_tail_in_one_statement(self):
        """Raw head, rollup middle (filtered on kind) and raw tail, params in SQL order."""
        cutoff = NOW - timedelta(days=7)
        h0, h1 = ceil_hour(cutoff), floor_hour(NOW)
        kind = stats_rollup.IP_ALLOWED_PUBLIC_DST
        sql, params = stats_rollup.ip_source(cutoff, (h0, h1), kind)
        assert sql.count('UNION ALL') == 2 and 'dst_ip AS ip' in sql
        assert params == [cutoff, h0, h0, h1, kind, h1]
        assert sql.count('%s') == len(params)

    def test_head_skipped_on_hour_boundary(self):
        """cutoff already on an hour → no raw head part."""
        cutoff = floor_hour(NOW) - timedelta(days=7)
        h1 = floor_hour(NOW)
        sql, params = stats_rollup.ip_source(cutoff, (cutoff, h1), stats_rollup.IP_BLOCKED_SRC)
        assert sql.count('UNION ALL') == 1
        assert params == [cutoff, h1, stats_rollup.IP_BLOCKED_SRC, h1]


# ── Real PostgreSQL: rollup path must equal the raw path ─────────────────────

PG_DSN = os.environ.get('ULI_TEST_PG_DSN')
pg = pytest.mark.skipif(not PG_DSN, reason="ULI_TEST_PG_DSN not set (needs a disposable PostgreSQL)")

_SCHEMA = """
DROP TABLE IF EXISTS logs, logs_hourly_stats, logs_hourly_stats_hours, logs_hourly_ip_stats,
    ip_threats, unifi_clients;
CREATE OR REPLACE FUNCTION is_public_inet(addr inet) RETURNS boolean AS $$
    SELECT addr IS NOT NULL AND NOT (addr << '10.0.0.0/8' OR addr << '172.16.0.0/12'
        OR addr << '192.168.0.0/16' OR addr << 'fc00::/7' OR addr << 'fe80::/10')
$$ LANGUAGE sql IMMUTABLE;
CREATE TABLE logs (
    id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMPTZ NOT NULL, log_type VARCHAR(20) NOT NULL,
    direction VARCHAR(20), rule_action VARCHAR(20), geo_country VARCHAR(2),
    service_name TEXT, threat_score INTEGER, src_ip INET, dst_ip INET,
    geo_city VARCHAR(100), asn_name VARCHAR(255), rdns VARCHAR(255));
CREATE INDEX ON logs (timestamp DESC);
CREATE TABLE logs_hourly_stats (
    hour TIMESTAMPTZ NOT NULL, dim SMALLINT NOT NULL, log_type VARCHAR(20),
    rule_action VARCHAR(20), direction VARCHAR(20), geo_country VARCHAR(2),
    service_name TEXT, count BIGINT NOT NULL);
CREATE TABLE logs_hourly_stats_hours (
    hour TIMESTAMPTZ PRIMARY KEY, computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version SMALLINT NOT NULL DEFAULT 1);
CREATE TABLE logs_hourly_ip_stats (
    hour TIMESTAMPTZ NOT NULL, kind SMALLINT NOT NULL, ip INET NOT NULL, log_type VARCHAR(20),
    count BIGINT NOT NULL, last_seen TIMESTAMPTZ NOT NULL, geo_country VARCHAR(2),
    geo_city VARCHAR(100), asn_name VARCHAR(255), rdns VARCHAR(255));
CREATE TABLE ip_threats (
    ip INET PRIMARY KEY, threat_score INTEGER NOT NULL DEFAULT 0, threat_categories TEXT[]);
CREATE TABLE unifi_clients (
    ip INET, device_name TEXT, hostname TEXT, oui TEXT, last_seen TIMESTAMPTZ);
"""

WAN_IP = '203.0.113.1'
_SCANNERS = [f'198.51.{i // 250}.{i % 250 + 1}' for i in range(300)]
_INTERNAL = [f'192.168.1.{i}' for i in range(2, 30)]
_DESTS = [f'8.{i // 250}.{i % 250 + 1}.8' for i in range(150)]


class _DB:
    """Minimal Database stand-in: get_conn() commits on success like the real one."""

    def __init__(self, conn):
        """Wrap one psycopg2 connection."""
        self.conn = conn

    @contextmanager
    def get_conn(self):
        """Yield the connection, commit on exit, roll back on error."""
        try:
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise


def _seed(cur, now, hours=8 * 24, rows=12000):
    """Random but reproducible logs over the last `hours`, NULLs included."""
    rnd = random.Random(42)
    span = hours * 3600
    data = []
    for _ in range(rows):
        log_type = rnd.choice(['firewall'] * 6 + ['dns', 'dhcp', 'wifi', 'system'])
        fw = log_type == 'firewall'
        action = rnd.choice(['allow', 'allow', 'block', 'redirect', None]) if fw else None
        if log_type == 'dns':  # Pi-hole: client → resolver, allow/block
            action = rnd.choice(['allow', 'block'])
        src = rnd.choice(_SCANNERS[:40] + _SCANNERS + _INTERNAL + [WAN_IP, None])
        dst = rnd.choice(_DESTS[:20] + _DESTS + _INTERNAL + [WAN_IP, None])
        data.append((
            now - timedelta(seconds=rnd.randrange(span)),
            log_type,
            rnd.choice(['inbound', 'outbound', 'inter_vlan', None]) if fw else None,
            action,
            rnd.choice(['FR', 'US', 'CN', 'DE', None]) if fw else None,
            rnd.choice(['HTTPS', 'SSH', 'DNS', None]) if fw else None,
            rnd.choice([None, None, 10, 80]),
            src, dst,
            rnd.choice(['Paris', 'Berlin', None]),
            rnd.choice(['AS1 Foo', 'AS2 Bar', None]),
            rnd.choice(['a.example', 'b.example', None]),
        ))
    cur.executemany(
        "INSERT INTO logs (timestamp, log_type, direction, rule_action, geo_country, "
        "service_name, threat_score, src_ip, dst_ip, geo_city, asn_name, rdns) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", data)
    cur.executemany(
        "INSERT INTO ip_threats (ip, threat_score, threat_categories) VALUES (%s, %s, %s)",
        [(ip, rnd.choice([20, 60, 90, 100]), ['Port Scan']) for ip in _SCANNERS[::3]])
    cur.executemany(
        "INSERT INTO unifi_clients (ip, device_name, last_seen) VALUES (%s, %s, %s)",
        [(ip, f'dev-{ip}', now) for ip in _INTERNAL[::2]])


@pytest.fixture
def pg_stats(monkeypatch):
    """Real PG seeded + rolled up, and routes.stats wired to it (deps/db mocked)."""
    import psycopg2
    from psycopg2.extras import RealDictCursor

    conn = psycopg2.connect(PG_DSN)
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(_SCHEMA)
        _seed(cur, now)
    conn.commit()

    monkeypatch.setattr(stats_rollup, 'BACKFILL_PAUSE_SECS', 0)
    db = _DB(conn)
    stats_rollup.StatsRollupTask(db, lambda: 30).run_once(budget_secs=60)

    for name in list(sys.modules):
        if name.startswith('routes'):
            monkeypatch.delitem(sys.modules, name, raising=False)
    deps = MagicMock()
    deps.get_conn = lambda: conn
    deps.put_conn = lambda _c: None
    db_mod = MagicMock()
    db_mod.get_config = lambda _db, key, default=None: (
        [_INTERNAL[0]] if key == 'gateway_ips' else default)
    db_mod.get_wan_ips_from_config = lambda _db: [WAN_IP]
    ip_identity = MagicMock()
    ip_identity.annotate_ip = lambda _cfg, _ip, _name: (None, None, None)
    monkeypatch.setitem(sys.modules, 'deps', deps)
    monkeypatch.setitem(sys.modules, 'db', db_mod)
    monkeypatch.setitem(sys.modules, 'ip_identity', ip_identity)
    import routes.stats as stats
    from routes._response_cache import clear_cache

    yield stats, conn, db, clear_cache, RealDictCursor
    clear_cache()
    conn.close()


def _both_paths(monkeypatch, stats, clear_cache, endpoint, time_range):
    """Call an endpoint on the rollup path, then on the raw path, with one fixed cutoff."""
    cutoff = stats.parse_time_range(time_range)
    monkeypatch.setattr(stats, 'parse_time_range', lambda _tr: cutoff)
    clear_cache()
    via_rollup = endpoint(time_range=time_range)
    real_plan = stats_rollup.plan
    monkeypatch.setattr(stats_rollup, 'plan', lambda *_a, **_k: None)
    clear_cache()
    via_raw = endpoint(time_range=time_range)
    monkeypatch.setattr(stats_rollup, 'plan', real_plan)
    return via_rollup, via_raw


@pg
@pytest.mark.parametrize('tz', ['UTC', 'Europe/Paris'])
def test_rollup_matches_raw_on_real_postgres(pg_stats, monkeypatch, tz):
    """Overview, charts (hour + day buckets) and countries/services are identical on both paths."""
    stats, conn, _db, clear_cache, RealDictCursor = pg_stats
    with conn.cursor() as cur:
        cur.execute(f"SET TIME ZONE '{tz}'")
    conn.commit()

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        assert stats_rollup.plan(cur, cutoff, datetime.now(timezone.utc)) is not None
    conn.commit()

    for time_range in ('24h', '7d'):  # 'hour' and 'day' chart buckets
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            assert stats_rollup.plan(cur, stats.parse_time_range(time_range),
                                     datetime.now(timezone.utc)) is not None, time_range
        conn.commit()
        rollup, raw = _both_paths(monkeypatch, stats, clear_cache, stats.get_stats_overview, time_range)
        assert rollup == raw and rollup['total'] > 0, time_range
        rollup, raw = _both_paths(monkeypatch, stats, clear_cache, stats.get_stats_charts, time_range)
        assert rollup == raw, time_range

    # tables: per-IP tops included, for the day-scale and multi-day spans
    for time_range in ('24h', '7d'):
        rollup, raw = _both_paths(monkeypatch, stats, clear_cache, stats.get_stats_tables, time_range)
        assert rollup == raw, time_range
        for key in ('top_blocked_ips', 'top_blocked_internal_ips', 'top_threat_ips',
                    'top_allowed_destinations', 'top_active_internal_ips'):
            assert rollup[key], (time_range, key)
        ips = {r['ip'] for k in ('top_blocked_ips', 'top_threat_ips', 'top_allowed_destinations')
               for r in rollup[k]}
        assert WAN_IP not in ips
        assert _INTERNAL[0] not in {r['ip'] for r in rollup['top_active_internal_ips']}
        assert all(r['threat_score'] > 50 for r in rollup['top_threat_ips'])

    # countries/services through counts() directly, against a plain GROUP BY
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        span = stats_rollup.plan(cur, cutoff, datetime.now(timezone.utc))
        for where, col, dim in ((stats._COUNTRIES_WHERE, 'geo_country', stats_rollup.DIM_COUNTRY),
                                (stats._SERVICES_WHERE, 'service_name', stats_rollup.DIM_SERVICE)):
            rolled = stats_rollup.counts(cur, cutoff, span, [('k', col), ('rule_action', 'rule_action')],
                                         where, dim=dim)
            cur.execute(f"SELECT {col} AS k, rule_action, COUNT(*) AS n FROM logs "
                        f"WHERE timestamp >= %s AND {where} GROUP BY 1, 2", [cutoff])
            assert rolled == {(r['k'], r['rule_action']): r['n'] for r in cur.fetchall()}
    conn.commit()


@pg
def test_gap_in_coverage_falls_back_and_refresh_fills_it(pg_stats):
    """A missing middle hour disables the rollup until the next pass recomputes it."""
    _stats, conn, db, _clear, RealDictCursor = pg_stats
    now = datetime.now(timezone.utc)
    hole = floor_hour(now) - 5 * HOUR
    stale = floor_hour(now) - 9 * HOUR
    with conn.cursor() as cur:
        cur.execute("DELETE FROM logs_hourly_stats_hours WHERE hour = %s", [hole])
        # rolled up by a release without the per-IP table: must count as missing
        cur.execute("UPDATE logs_hourly_stats_hours SET version = 1 WHERE hour = %s", [stale])
        cur.execute("DELETE FROM logs_hourly_ip_stats WHERE hour = %s", [stale])
    conn.commit()
    for restore in ("INSERT INTO logs_hourly_stats_hours (hour, version) VALUES (%s, 1)", None):
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            assert stats_rollup.plan(cur, now - timedelta(hours=24), now) is None
            if restore:  # old-version hour alone still blocks the plan
                cur.execute(restore, [hole])
        conn.commit()

    stats_rollup.StatsRollupTask(db, lambda: 30).run_once(budget_secs=60)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        assert stats_rollup.plan(cur, now - timedelta(hours=24), now) is not None
        cur.execute("SELECT COUNT(*) AS n FROM logs_hourly_ip_stats WHERE hour = %s", [stale])
        assert cur.fetchone()['n'] > 0
    conn.commit()


@pg
def test_purge_follows_general_and_dns_retention(pg_stats):
    """General cutoff drops every row and coverage; the DNS cutoff drops DNS rows only."""
    _stats, conn, db, _clear, _rdc = pg_stats
    stats_rollup.purge(db, general_days=1, dns_days=0)
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM logs_hourly_stats WHERE log_type = 'dns'")
        assert cur.fetchone()[0] == 0
        cur.execute("SELECT MIN(hour) FROM logs_hourly_stats_hours")
        assert cur.fetchone()[0] >= datetime.now(timezone.utc) - timedelta(days=1, hours=1)
        cur.execute("SELECT COUNT(*) FROM logs_hourly_stats WHERE log_type = 'firewall'")
        assert cur.fetchone()[0] > 0
        cur.execute("SELECT COUNT(*) FILTER (WHERE log_type = 'dns'), "
                    "COUNT(*) FILTER (WHERE log_type = 'firewall') FROM logs_hourly_ip_stats")
        dns_ip_rows, fw_ip_rows = cur.fetchone()
        assert dns_ip_rows == 0 and fw_ip_rows > 0
    conn.commit()
