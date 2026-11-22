"""`python -m db.migrate_partitions`: plain logs → daily partitions with logs_legacy attached.

The integration tests need a disposable PostgreSQL (see tests/test_partitioning.py
for the ULI_TEST_PG_DSN setup) and are skipped without it. They build the
pre-partitioning table through the real boot path, so every production index
exists, then migrate it.
"""

import re
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from db import migrate_partitions as mp
from db import partitioning
from tests.test_partitioning import (  # noqa: F401  (fresh_db is a fixture)
    PG_DSN, _boot_warnings, _connect, _index_valid, _insert, _legacy_plain_ddl, _one, fresh_db,
)

pg = pytest.mark.skipif(not PG_DSN, reason="ULI_TEST_PG_DSN not set (needs a disposable PostgreSQL)")


# ── Pure logic (always runs) ─────────────────────────────────────────────────

def test_next_cutover_is_a_utc_midnight_at_least_48h_ahead():
    """Cutover leaves 48-72 h before the CHECK can reject anything."""
    for hour in (0, 1, 13, 23):
        now = datetime(2026, 11, 22, hour, 30, tzinfo=timezone.utc)
        cutover = mp.next_cutover(now)
        assert cutover.time() == datetime.min.time() and cutover.tzinfo == timezone.utc
        assert timedelta(hours=48) <= cutover - now < timedelta(hours=72)


def test_cli_requires_an_explicit_mode():
    """No flag → usage error, nothing runs."""
    with pytest.raises(SystemExit) as exc:
        mp.main([])
    assert exc.value.code == 2


# ── Real PostgreSQL ──────────────────────────────────────────────────────────

def _plain_install(fresh_db, days=10, per_day=200):
    """A pre-partitioning install: plain logs through the real boot, with rows."""
    params, raw, opened = fresh_db
    with raw.cursor() as cur:
        cur.execute(_legacy_plain_ddl())
    db = _connect(params, opened)
    db.get_config = lambda key, default=None: False if key == 'unifi_enabled' else default
    db.ensure_post_boot_indexes()
    with raw.cursor() as cur:
        cur.execute("""
            INSERT INTO logs (timestamp, log_type, rule_action, raw_log)
            SELECT now() - (g * interval '1 minute') * %s, 'firewall', 'block', 'x'
            FROM generate_series(1, %s) g""", [days * 24 * 60 / (days * per_day), days * per_day])
    assert _one(raw, "SELECT relkind FROM pg_class WHERE relname = 'logs'") == 'r'
    return db, raw


def _parent_indexes(raw):
    """{name: valid} of the indexes defined on public.logs."""
    with raw.cursor() as cur:
        cur.execute("SELECT c.relname, i.indisvalid FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid "
                    "WHERE i.indrelid = 'public.logs'::regclass")
        return dict(cur.fetchall())


@pg
def test_dry_run_changes_nothing(fresh_db):
    """The plan lists every production index and touches nothing."""
    _db, raw = _plain_install(fresh_db)
    with raw.cursor() as cur:
        plan = mp.inspect_plan(cur)
    names = {name for name, _ in plan['parent_indexes']}
    assert {'idx_logs_timestamp', 'idx_logs_type_id', 'idx_logs_spgist_dst_ip_firewall'} <= names
    assert 'logs_pkey' in {name for name, _ in plan['skipped_indexes']}
    assert plan['twin_needed'] and plan['bound'] == {}
    lines = []
    mp._print_plan(plan, out=lines.append)
    assert any('cutover' in line for line in lines)
    assert _index_valid(raw, mp.ID_TWIN) is None
    assert _one(raw, "SELECT count(*) FROM pg_constraint WHERE conname LIKE 'logs_legacy_before_%'") == 0


@pg
def test_migration_end_to_end(fresh_db, caplog):
    """Plain → partitioned with history intact, indexes valid, boot clean, legacy droppable."""
    db, raw = _plain_install(fresh_db)
    rows = _one(raw, "SELECT count(*) FROM logs")
    some_id = _one(raw, "SELECT max(id) FROM logs")
    expected_indexes = set(_parent_indexes(raw)) - {'logs_pkey'} | {'idx_logs_id'}

    summary = mp.migrate(raw, out=lambda _l: None)
    cutover = summary['cutover']

    assert _one(raw, "SELECT relkind FROM pg_class WHERE relname = 'logs'") == 'p'
    assert _one(raw, "SELECT pg_get_expr(c.relpartbound, c.oid) FROM pg_class c WHERE relname = 'logs_legacy'") \
        .startswith('FOR VALUES FROM (MINVALUE) TO (')
    parent = _parent_indexes(raw)
    assert set(parent) == expected_indexes and all(parent.values())
    # No rebuild under the swap lock: logs_legacy's attached indexes are the
    # original ones (renamed *_legacy) plus the twin, not fresh auto-named copies.
    with raw.cursor() as cur:
        cur.execute("SELECT c.relname FROM pg_index x JOIN pg_class c ON c.oid = x.indexrelid "
                    "JOIN pg_inherits i ON i.inhrelid = x.indexrelid "
                    "WHERE x.indrelid = 'public.logs_legacy'::regclass")
        attached_legacy = {r[0] for r in cur.fetchall()}
    assert attached_legacy == {f"{n}_legacy" for n in parent if n != 'idx_logs_id'} | {mp.ID_TWIN}
    for part in ['logs_legacy', 'logs_default'] + [
            partitioning.partition_name(cutover.date() + timedelta(days=i)) for i in range(8)]:
        attached = _one(raw, "SELECT count(*) FROM pg_index x JOIN pg_inherits i ON i.inhrelid = x.indexrelid "
                             "WHERE x.indrelid = %s::regclass", [part])
        assert attached == len(parent), part
    assert _one(raw, "SELECT count(*) FROM logs") == rows
    assert _one(raw, "SELECT count(*) FROM logs WHERE id = %s", [some_id]) == 1
    assert _insert(raw, datetime.now(timezone.utc)) == 'logs_legacy'
    assert _insert(raw, cutover + timedelta(hours=1)) == partitioning.partition_name(cutover.date())
    assert _one(raw, "SELECT value FROM system_config WHERE key = %s", [mp.CUTOVER_KEY]) is None
    assert mp.migrate(raw, out=lambda _l: None) == {'already_done': True}

    # Boot after migration: no warnings, no overlapping day partitions attempted.
    for _ in range(2):
        assert _boot_warnings(caplog, db._ensure_schema) == []
        assert _boot_warnings(caplog, db.ensure_post_boot_indexes) == []
        assert _boot_warnings(caplog, lambda: partitioning.ensure_partitions(db)) == []

    # Retention eventually drops logs_legacy whole; the sequence survives it.
    assert partitioning.drop_expired_partitions(db, cutover) == ['logs_legacy']
    assert _insert(raw, cutover + timedelta(hours=2)) == partitioning.partition_name(cutover.date())


@pg
def test_inserts_keep_flowing_during_migration(fresh_db):
    """A writer inserting every few ms sees no error; the swap lock is brief."""
    _db, raw = _plain_install(fresh_db)
    import psycopg2
    params = fresh_db[0]
    stop, errors, inserted = threading.Event(), [], [0]

    def writer():
        """Insert 'now' rows until stopped, recording any failure."""
        conn = psycopg2.connect(**params)
        conn.autocommit = True
        with conn.cursor() as cur:
            while not stop.is_set():
                try:
                    cur.execute("INSERT INTO logs (timestamp, log_type, raw_log) VALUES (now(), 'firewall', 'w')")
                    inserted[0] += 1
                except Exception as e:  # noqa: BLE001 - the test reports it
                    errors.append(e)
                time.sleep(0.002)
        conn.close()

    thread = threading.Thread(target=writer)
    thread.start()
    try:
        time.sleep(0.2)
        summary = mp.migrate(raw, out=lambda _l: None)
        time.sleep(0.2)
    finally:
        stop.set()
        thread.join()
    assert errors == []
    assert inserted[0] > 0
    assert summary['swap_seconds'] < 2


@pg
def test_resume_after_interruption_before_swap(fresh_db):
    """Phases 1-3 done by a killed run: a re-run reuses them and completes."""
    _db, raw = _plain_install(fresh_db)
    with raw.cursor() as cur:
        cutover = mp.inspect_plan(cur)['cutover']
        mp._store_cutover(cur, cutover)
        mp._ensure_twin(cur)
        mp._ensure_bound(cur, cutover)
    lines = []
    summary = mp.migrate(raw, out=lines.append)
    assert summary['cutover'] == cutover
    assert any('already valid' in line for line in lines)
    assert _one(raw, "SELECT relkind FROM pg_class WHERE relname = 'logs'") == 'p'


@pg
def test_failed_swap_disarms_the_bound(fresh_db, monkeypatch):
    """If the swap fails, the CHECK that would reject post-cutover rows is removed."""
    _db, raw = _plain_install(fresh_db)

    def broken(_indexes, _cutover):
        """Swap generator that fails mid-transaction."""
        def gen(_cur):
            """Yield one statement, then fail."""
            yield "LOCK TABLE logs IN ACCESS EXCLUSIVE MODE", None
            raise RuntimeError("simulated swap failure")
        return gen

    monkeypatch.setattr(mp, '_swap_statements', broken)
    with pytest.raises(RuntimeError):
        mp.migrate(raw, out=lambda _l: None)
    assert _one(raw, "SELECT relkind FROM pg_class WHERE relname = 'logs'") == 'r'
    assert _one(raw, "SELECT count(*) FROM pg_constraint WHERE conname LIKE 'logs_legacy_before_%'") == 0
    assert _insert(raw, datetime.now(timezone.utc) + timedelta(days=5)) == 'logs'


@pg
def test_mismatched_index_aborts_before_any_rebuild(fresh_db, monkeypatch):
    """A parent index logs_legacy cannot satisfy is detected on the empty probe:
    abort (no minutes-long rebuild under lock), table and CHECK back to normal."""
    _db, raw = _plain_install(fresh_db)
    real = mp._swap_statements
    monkeypatch.setattr(mp, '_swap_statements', lambda indexes, cutover: real(
        [(n, d.split(' WHERE ')[0]) for n, d in indexes], cutover))  # drop partial predicates
    with pytest.raises(mp.MigrationError, match='would rebuild them under lock'):
        mp.migrate(raw, out=lambda _l: None)
    assert _one(raw, "SELECT relkind FROM pg_class WHERE relname = 'logs'") == 'r'
    assert _one(raw, "SELECT to_regclass('public.logs_attach_probe')") is None
    assert _one(raw, "SELECT count(*) FROM pg_constraint WHERE conname LIKE 'logs_legacy_before_%'") == 0


@pg
def test_abort_restores_the_plain_table(fresh_db):
    """--abort removes the twin index, the CHECK and the stored cutover."""
    _db, raw = _plain_install(fresh_db)
    with raw.cursor() as cur:
        cutover = mp.inspect_plan(cur)['cutover']
        mp._store_cutover(cur, cutover)
        mp._ensure_twin(cur)
        mp._ensure_bound(cur, cutover)
    mp.abort(raw, out=lambda _l: None)
    assert _index_valid(raw, mp.ID_TWIN) is None
    assert _one(raw, "SELECT count(*) FROM pg_constraint WHERE conname LIKE 'logs_legacy_before_%'") == 0
    assert _one(raw, "SELECT value FROM system_config WHERE key = %s", [mp.CUTOVER_KEY]) is None


@pg
def test_hourly_job_drops_a_bound_left_armed_near_its_cutover(fresh_db):
    """Safety net: a killed migration's CHECK is dropped before its cutover arrives."""
    db, raw = _plain_install(fresh_db)
    soon = datetime.now(timezone.utc).date() + timedelta(days=1)
    later = datetime.now(timezone.utc).date() + timedelta(days=5)
    with raw.cursor() as cur:
        for day in (soon, later):
            name = f"logs_legacy_before_{day:%Y%m%d}"
            cur.execute(f"ALTER TABLE logs ADD CONSTRAINT {name} CHECK (timestamp < %s) NOT VALID",
                        [partitioning.day_bounds(day)[0]])
    partitioning.ensure_partitions(db)
    remaining = _one(raw, "SELECT string_agg(conname, ',') FROM pg_constraint "
                          "WHERE conname LIKE 'logs_legacy_before_%'")
    assert remaining == f"logs_legacy_before_{later:%Y%m%d}"


@pg
def test_refuses_when_rows_are_dated_after_the_cutover(fresh_db):
    """A device clock far ahead would fail VALIDATE: refuse up front with the fix."""
    _db, raw = _plain_install(fresh_db)
    _insert(raw, datetime.now(timezone.utc) + timedelta(days=30))
    with raw.cursor() as cur:
        with pytest.raises(mp.MigrationError, match='DELETE FROM logs WHERE timestamp >='):
            mp.inspect_plan(cur)


# ── The wiki's post-swap rollback, executed verbatim ─────────────────────────

WIKI_PAGE = Path(__file__).resolve().parents[2] / 'docs' / 'wiki' / 'Logs-Partitioning.md'


def _wiki_rollback_sql():
    """The SQL block that follows the `<!-- rollback-sql -->` marker in the wiki page."""
    text = WIKI_PAGE.read_text()
    m = re.search(r'<!-- rollback-sql -->\s*```sql\n(.*?)```', text, re.S)
    assert m, "rollback SQL block not found in the wiki page"
    return m.group(1)


@pg
def test_wiki_rollback_restores_a_plain_table(fresh_db, caplog):
    """After a swap and post-cutover rows, the documented SQL gives back the original
    plain table: every row, original index names, PK, a working sequence, clean boot."""
    db, raw = _plain_install(fresh_db)
    original_indexes = set(_parent_indexes(raw))
    summary = mp.migrate(raw, out=lambda _l: None)
    cutover = summary['cutover']
    assert _insert(raw, cutover + timedelta(hours=3)) == partitioning.partition_name(cutover.date())
    assert _insert(raw, cutover + timedelta(days=40)) == 'logs_default'
    rows = _one(raw, "SELECT count(*) FROM logs")
    copied = _one(raw, "SELECT count(*) FROM logs WHERE tableoid <> 'logs_legacy'::regclass")
    assert copied == 2

    with raw.cursor() as cur:
        cur.execute(_wiki_rollback_sql())

    assert _one(raw, "SELECT relkind FROM pg_class WHERE relname = 'logs'") == 'r'
    assert _one(raw, "SELECT count(*) FROM logs") == rows
    assert set(_parent_indexes(raw)) == original_indexes  # names back, extra id index gone
    assert _one(raw, "SELECT to_regclass('public.logs_default')") is None
    assert _one(raw, "SELECT count(*) FROM pg_constraint WHERE conname LIKE 'logs_legacy_before_%'") == 0
    assert _one(raw, "SELECT pg_get_serial_sequence('logs', 'id')") == 'public.logs_id_seq'
    assert _insert(raw, datetime.now(timezone.utc)) == 'logs'
    assert _boot_warnings(caplog, db._ensure_schema) == []
    assert _boot_warnings(caplog, db.ensure_post_boot_indexes) == []
    # ...and the migration can be run again later. The two synthetic rows dated
    # after the (still future) cutover would rightly be refused; in real life
    # they are in the past by the time anyone rolls back.
    with raw.cursor() as cur:
        cur.execute("DELETE FROM logs WHERE timestamp >= %s", [cutover])
    assert mp.migrate(raw, out=lambda _l: None)['already_done'] is False
    assert _one(raw, "SELECT relkind FROM pg_class WHERE relname = 'logs'") == 'p'
