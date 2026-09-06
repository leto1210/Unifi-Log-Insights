"""Regression tests for the external database migration route helpers."""

import sys
import threading
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

import routes.migration as migration


class FakeMigrationCursor:
    """Cursor stub for scripted migration route database interactions."""

    def __init__(self, existing_tables, failing_count_tables=None):
        """Store visible tables and any tables whose counts should fail."""
        self.existing_tables = set(existing_tables)
        self.failing_count_tables = set(failing_count_tables or [])
        self.last_count_table = None

    def execute(self, sql, params=None):
        """Record enough SQL intent to drive fetchone/fetchall responses."""
        sql_text = str(sql)
        self.last_count_table = None
        if sql_text.startswith("SELECT count(*) FROM "):
            table = sql_text.rsplit(" ", 1)[-1]
            if table in self.failing_count_tables:
                raise RuntimeError(f"cannot count {table}")
            self.last_count_table = table

    def fetchone(self):
        """Return a small positive count for existing app tables."""
        if self.last_count_table:
            return (3,)
        return None

    def fetchall(self):
        """Return visible public tables for information_schema queries."""
        return [(table,) for table in sorted(self.existing_tables)]

    def __enter__(self):
        """Return self for context manager use."""
        return self

    def __exit__(self, exc_type, exc, tb):
        """Do not swallow exceptions."""
        return False


class FakeMigrationConn:
    """Connection stub exposing cursor, rollback, and close methods."""

    def __init__(self, cursor):
        """Attach a scripted cursor and mocked connection methods."""
        self.cursor_obj = cursor
        self.autocommit = False
        self.rollback = MagicMock()
        self.close = MagicMock()

    def cursor(self):
        """Return the scripted cursor."""
        return self.cursor_obj


@pytest.fixture(autouse=True)
def reset_migration_state():
    """Reset global migration state after each test."""
    yield
    migration._update_state(
        status='idle',
        step='',
        message='',
        progress_pct=0,
        details={},
    )


def test_source_count_failure_marks_migration_failed(monkeypatch):
    """A visible source table that cannot be counted must fail validation."""
    params = migration.MigrationParams(host='db.example', password='secret')
    preflight_conn = FakeMigrationConn(FakeMigrationCursor(existing_tables=[]))
    target_conn = FakeMigrationConn(FakeMigrationCursor(existing_tables={'logs'}))
    source_conn = FakeMigrationConn(
        FakeMigrationCursor(existing_tables={'logs'}, failing_count_tables={'logs'})
    )
    connect = MagicMock(side_effect=[preflight_conn, target_conn])

    monkeypatch.setattr(migration.psycopg2, 'connect', connect)
    monkeypatch.setattr(
        migration.subprocess,
        'run',
        MagicMock(return_value=SimpleNamespace(returncode=0, stderr='')),
    )
    monkeypatch.setitem(
        sys.modules,
        'deps',
        SimpleNamespace(get_conn=lambda: source_conn, put_conn=MagicMock()),
    )

    migration._do_migration(params)

    assert migration._migration_state['status'] == 'failed'
    assert migration._migration_state['step'] == 'Source count failed'
    assert 'logs' in migration._migration_state['message']


def test_absent_legacy_app_table_does_not_block_migration(monkeypatch):
    """Absent legacy app tables are ignored instead of counted as failures."""
    params = migration.MigrationParams(host='db.example', password='secret')
    preflight_conn = FakeMigrationConn(FakeMigrationCursor(existing_tables=[]))
    target_conn = FakeMigrationConn(FakeMigrationCursor(existing_tables={'logs'}))
    source_conn = FakeMigrationConn(FakeMigrationCursor(existing_tables={'logs'}))

    monkeypatch.setattr(
        migration.psycopg2,
        'connect',
        MagicMock(side_effect=[preflight_conn, target_conn]),
    )
    monkeypatch.setattr(
        migration.subprocess,
        'run',
        MagicMock(return_value=SimpleNamespace(returncode=0, stderr='')),
    )
    monkeypatch.setitem(
        sys.modules,
        'deps',
        SimpleNamespace(get_conn=lambda: source_conn, put_conn=MagicMock()),
    )

    migration._do_migration(params)

    assert migration._migration_state['status'] == 'complete'
    validation = migration._migration_state['details']['validation']
    assert validation['logs'] == {'source': 3, 'target': 3, 'status': 'ok'}
    assert 'mcp_tokens' not in validation


def test_missing_current_app_table_marks_migration_failed(monkeypatch):
    """A current app table present in source but missing in target is partial."""
    params = migration.MigrationParams(host='db.example', password='secret')
    preflight_conn = FakeMigrationConn(FakeMigrationCursor(existing_tables=[]))
    target_conn = FakeMigrationConn(FakeMigrationCursor(existing_tables={'logs'}))
    source_conn = FakeMigrationConn(
        FakeMigrationCursor(existing_tables={'api_tokens', 'logs'})
    )

    monkeypatch.setattr(
        migration.psycopg2,
        'connect',
        MagicMock(side_effect=[preflight_conn, target_conn]),
    )
    monkeypatch.setattr(
        migration.subprocess,
        'run',
        MagicMock(return_value=SimpleNamespace(returncode=0, stderr='')),
    )
    monkeypatch.setitem(
        sys.modules,
        'deps',
        SimpleNamespace(get_conn=lambda: source_conn, put_conn=MagicMock()),
    )

    migration._do_migration(params)

    assert migration._migration_state['status'] == 'failed'
    validation = migration._migration_state['details']['validation']
    assert validation['api_tokens'] == {'source': 3, 'target': -1, 'status': 'mismatch'}


def test_start_migration_allows_only_one_concurrent_worker(monkeypatch):
    """Concurrent start requests must publish running state atomically."""
    params = migration.MigrationParams(host='db.example', password='secret')
    request = SimpleNamespace(state=SimpleNamespace(auth_info={'sub': 'admin'}))
    barrier = threading.Barrier(2)
    real_thread = threading.Thread
    started_workers = []
    results = []
    errors = []

    class FakeWorkerThread:
        """Thread replacement that records migration worker starts."""

        def __init__(self, target, args=(), daemon=False):
            """Store the requested worker target without running it."""
            self.target = target
            self.args = args
            self.daemon = daemon

        def start(self):
            """Record that the endpoint attempted to start a worker."""
            started_workers.append((self.target, self.args, self.daemon))

    def fake_is_external_db():
        """Synchronize both callers after the initial running-state check."""
        barrier.wait(timeout=5)
        return False

    def call_start():
        """Invoke start_migration and capture success or HTTP errors."""
        try:
            results.append(migration.start_migration(request, params))
        except HTTPException as exc:
            errors.append(exc)

    monkeypatch.setattr(migration, 'is_external_db', fake_is_external_db)
    monkeypatch.setattr(migration.threading, 'Thread', FakeWorkerThread)

    callers = [real_thread(target=call_start), real_thread(target=call_start)]
    for caller in callers:
        caller.start()
    for caller in callers:
        caller.join(timeout=5)

    assert len(started_workers) == 1
    assert results == [{'success': True, 'message': 'Migration started'}]
    assert [exc.status_code for exc in errors] == [409]
