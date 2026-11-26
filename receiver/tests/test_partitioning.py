"""Daily partitioning of `logs` against a real PostgreSQL (>= 14).

Skipped unless ULI_TEST_PG_DSN points at a disposable server, e.g.:

    docker run -d --rm --name uli-pg -e POSTGRES_PASSWORD=test -p 55433:5432 postgres:16-alpine
    ULI_TEST_PG_DSN="host=127.0.0.1 port=55433 user=postgres password=test dbname=postgres" \
        pytest tests/test_partitioning.py

Each test creates and drops its own database: never point this at a real install.
"""

import inspect
import logging
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from db import Database, partitioning

PG_DSN = os.environ.get('ULI_TEST_PG_DSN')
pytestmark = pytest.mark.skipif(not PG_DSN, reason="ULI_TEST_PG_DSN not set (needs a disposable PostgreSQL)")

INIT_SQL = Path(__file__).resolve().parents[2] / 'init.sql'


def _admin():
    """Autocommit connection to the server's maintenance database."""
    import psycopg2
    conn = psycopg2.connect(PG_DSN)
    conn.autocommit = True
    return conn


@pytest.fixture
def fresh_db():
    """Yield (conn_params, raw_conn) for a brand-new empty database; drop it afterwards."""
    import psycopg2
    from psycopg2.extensions import parse_dsn
    name = f"uli_part_{uuid.uuid4().hex[:10]}"
    admin = _admin()
    with admin.cursor() as cur:
        cur.execute(f"CREATE DATABASE {name}")
    params = {**parse_dsn(PG_DSN), 'dbname': name}
    raw = psycopg2.connect(**params)
    raw.autocommit = True
    opened = []
    yield params, raw, opened
    for db in opened:
        db.close()
    raw.close()
    with admin.cursor() as cur:
        cur.execute(f"DROP DATABASE {name} WITH (FORCE)")
    admin.close()


def _connect(params, opened):
    """Run the real boot path (pool + _ensure_schema) and remember the Database."""
    db = Database(conn_params=params, min_conn=1, max_conn=4)
    db.connect()
    opened.append(db)
    return db


def _one(raw, sql, args=None):
    """First column of the first row."""
    with raw.cursor() as cur:
        cur.execute(sql, args)
        row = cur.fetchone()
        return row[0] if row else None


def _insert(raw, ts, log_type='firewall'):
    """Insert one minimal row and return the partition it landed in."""
    with raw.cursor() as cur:
        cur.execute("INSERT INTO logs (timestamp, log_type, raw_log) VALUES (%s, %s, 'x') "
                    "RETURNING tableoid::regclass::text", [ts, log_type])
        return cur.fetchone()[0]


def _legacy_plain_ddl():
    """The pre-partitioning logs DDL: current columns, PRIMARY KEY, no PARTITION BY."""
    source = inspect.getsource(Database._ensure_schema)
    ddl = re.search(r'CREATE TABLE IF NOT EXISTS logs \(.*?\) PARTITION BY RANGE \(timestamp\)',
                    source, re.S).group(0)
    return (ddl.replace(' PARTITION BY RANGE (timestamp)', '')
               .replace('BIGSERIAL NOT NULL', 'BIGSERIAL PRIMARY KEY'))


def _boot_warnings(caplog, fn):
    """Run fn and return WARNING+ records it logged.

    Ignores the pre-existing, planned warning for the optional
    log_autovacuum_min_duration setting, which PostgreSQL 16 refuses at
    session level (unrelated to partitioning).
    """
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        fn()
    return [r for r in caplog.records if r.levelno >= logging.WARNING
            and 'log_autovacuum_min_duration' not in r.getMessage()]


def _index_valid(raw, name):
    """indisvalid of an index, or None if it does not exist."""
    return _one(raw, "SELECT i.indisvalid FROM pg_index i WHERE i.indexrelid = to_regclass(%s)",
                [f'public.{name}'])


def test_fresh_install_is_partitioned_and_boot_is_idempotent(fresh_db, caplog):
    """Empty DB → partitioned logs; re-running every boot step changes nothing and warns nothing."""
    params, raw, opened = fresh_db
    db = _connect(params, opened)

    assert _one(raw, "SELECT relkind FROM pg_class WHERE relname = 'logs'") == 'p'
    assert _one(raw, "SELECT to_regclass('public.logs_default')") is not None
    assert _index_valid(raw, 'idx_logs_id') is True

    today = datetime.now(timezone.utc).date()
    created = partitioning.ensure_partitions(db)
    assert created == [partitioning.partition_name(today + timedelta(days=i)) for i in range(8)]
    assert partitioning.ensure_partitions(db) == []

    # The anti-outage guard: a partitioned DB must boot cleanly, repeatedly.
    db.get_config = lambda key, default=None: False if key == 'unifi_enabled' else default
    for _ in range(2):
        assert _boot_warnings(caplog, db._ensure_schema) == []
        assert _boot_warnings(caplog, db.ensure_post_boot_indexes) == []
    for name in ('idx_logs_type_id', 'idx_logs_nondns_timestamp', 'idx_logs_spgist_dst_ip_firewall',
                 'idx_logs_block_src_cover', 'idx_logs_threat_cover'):
        assert _index_valid(raw, name) is True, name
    assert _index_valid(raw, 'idx_logs_direction') is None  # POST_BOOT_DROPS applied

    # SP-GiST gate both ways (UniFi authoritative → dropped, then back).
    db.get_config = lambda key, default=None: True if key == 'unifi_enabled' else default
    assert _boot_warnings(caplog, db.ensure_post_boot_indexes) == []
    assert _index_valid(raw, 'idx_logs_spgist_dst_ip_firewall') is None
    db.get_config = lambda key, default=None: False if key == 'unifi_enabled' else default
    assert _boot_warnings(caplog, db.ensure_post_boot_indexes) == []
    assert _index_valid(raw, 'idx_logs_spgist_dst_ip_firewall') is True

    # Rows route by day; every partition carries every parent index.
    assert _insert(raw, datetime.now(timezone.utc)) == partitioning.partition_name(today)
    parent_indexes = _one(raw, "SELECT count(*) FROM pg_indexes WHERE tablename = 'logs'")
    for part in created + ['logs_default']:
        attached = _one(raw, """
            SELECT count(*) FROM pg_index x JOIN pg_inherits i ON i.inhrelid = x.indexrelid
            WHERE x.indrelid = %s::regclass""", [part])
        assert attached == parent_indexes, part


def test_init_sql_then_boot(fresh_db, caplog):
    """Embedded fresh install: init.sql, then the app's _ensure_schema, validates cleanly."""
    params, raw, opened = fresh_db
    # entrypoint.sh runs init.sql through psql without ON_ERROR_STOP, which
    # skips the optional log_autovacuum_min_duration block PostgreSQL 16
    # refuses; psycopg2 runs the file as one statement, so drop that block.
    sql = re.sub(r'DO \$\$(?:(?!DO \$\$).)*?log_autovacuum_min_duration.*?END \$\$;', '',
                 INIT_SQL.read_text(), flags=re.S)
    with raw.cursor() as cur:
        cur.execute(sql)
    assert _one(raw, "SELECT relkind FROM pg_class WHERE relname = 'logs'") == 'p'
    db = _connect(params, opened)
    assert _one(raw, "SELECT to_regclass('public.logs_default')") is not None
    assert partitioning.ensure_partitions(db)  # day partitions created


def test_existing_plain_table_is_left_alone(fresh_db, caplog):
    """A pre-partitioning install boots as before: plain table, DELETE retention, no partition work."""
    params, raw, opened = fresh_db
    with raw.cursor() as cur:
        cur.execute(_legacy_plain_ddl())
    old = datetime.now(timezone.utc) - timedelta(days=40)
    _insert(raw, old)
    _insert(raw, datetime.now(timezone.utc))

    db = _connect(params, opened)
    assert _one(raw, "SELECT relkind FROM pg_class WHERE relname = 'logs'") == 'r'
    assert 'autovacuum_vacuum_scale_factor=0.01' in _one(
        raw, "SELECT array_to_string(reloptions, ',') FROM pg_class WHERE relname = 'logs'")
    assert _one(raw, "SELECT to_regclass('public.logs_default')") is None
    assert partitioning.ensure_partitions(db) == []
    assert _boot_warnings(caplog, db.ensure_post_boot_indexes) == []

    result = db.run_retention_cleanup(30, 10)
    assert result['status'] == 'complete' and result['partitions_dropped'] == []
    assert result['non_dns_deleted'] == 1
    with raw.cursor() as cur:
        cur.execute("ANALYZE logs")
    assert _one(raw, partitioning.LOGS_ROW_ESTIMATE_SQL) == 1


def test_retention_drops_expired_partitions(fresh_db):
    """Whole expired days are DROPped; DELETE still enforces DNS, the edge day and DEFAULT."""
    params, raw, opened = fresh_db
    db = _connect(params, opened)
    now = datetime.now(timezone.utc)
    today = now.date()
    partitioning.ensure_partitions(db, days_ahead=12, today=today - timedelta(days=10))
    for d in range(10, -1, -1):
        ts = now - timedelta(days=d)
        _insert(raw, ts)
        _insert(raw, ts, log_type='dns')
    assert _insert(raw, datetime(2001, 1, 1, tzinfo=timezone.utc)) == 'logs_default'

    result = db.run_retention_cleanup(5, 2)

    general_cutoff, dns_cutoff = now - timedelta(days=5), now - timedelta(days=2)
    expected = [partitioning.partition_name(today - timedelta(days=d)) for d in range(10, 5, -1)]
    assert sorted(result['partitions_dropped']) == sorted(expected)
    for name in expected:
        assert _one(raw, "SELECT to_regclass(%s)", [f'public.{name}']) is None
    assert _one(raw, "SELECT count(*) FROM logs WHERE log_type <> 'dns' AND timestamp < %s",
                [general_cutoff]) == 0
    assert _one(raw, "SELECT count(*) FROM logs WHERE log_type = 'dns' AND timestamp < %s",
                [dns_cutoff]) == 0
    assert _one(raw, "SELECT count(*) FROM logs_default") == 0
    assert _one(raw, "SELECT count(*) FROM logs WHERE timestamp >= %s", [general_cutoff]) > 0


def test_ensure_partitions_moves_rows_out_of_default(fresh_db):
    """A day already holding rows in DEFAULT gets its partition, rows moved into it."""
    params, raw, opened = fresh_db
    db = _connect(params, opened)
    future = datetime.now(timezone.utc) + timedelta(days=20)
    assert _insert(raw, future) == 'logs_default'
    rows_before = _one(raw, "SELECT count(*) FROM logs")

    partitioning.ensure_partitions(db, days_ahead=20)

    target = partitioning.partition_name(future.date())
    assert _one(raw, "SELECT tableoid::regclass::text FROM logs WHERE timestamp = %s", [future]) == target
    assert _one(raw, "SELECT count(*) FROM logs") == rows_before
    assert _one(raw, "SELECT count(*) FROM logs_default") == 0


def test_row_estimate_sums_leaf_partitions(fresh_db):
    """Health/stats estimate counts each row once (leaves only, not the analyzed parent)."""
    params, raw, opened = fresh_db
    db = _connect(params, opened)
    partitioning.ensure_partitions(db, days_ahead=3)
    for d in range(4):
        for _ in range(5):
            _insert(raw, datetime.now(timezone.utc) + timedelta(days=d))
    with raw.cursor() as cur:
        cur.execute("ANALYZE logs")
    assert _one(raw, partitioning.LOGS_ROW_ESTIMATE_SQL) == 20
