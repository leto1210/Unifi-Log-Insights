"""Regression tests for AdGuard data/checkpoint atomicity."""

from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

import adguard_poller
from adguard_poller import AdGuardHomePoller
from db import Database


class FakeAdGuardCursor:
    """Cursor stub that records SQL and returns a stable expected host."""

    def __init__(self, host='http://adguard.lan'):
        """Store the host returned by the in-transaction guard query."""
        self.host = host
        self.executed = []

    def execute(self, sql, params=None):
        """Record SQL statements and parameters."""
        self.executed.append((str(sql), params))

    def fetchone(self):
        """Return the configured AdGuard host for host mismatch checks."""
        return (self.host,)

    def __enter__(self):
        """Return self for context manager usage."""
        return self

    def __exit__(self, exc_type, exc, tb):
        """Do not swallow exceptions."""
        return False


class FakeAdGuardConn:
    """Connection stub returning one recording cursor."""

    def __init__(self, cursor):
        """Attach the cursor used by the Database method."""
        self.cursor_obj = cursor

    def cursor(self):
        """Return the recording cursor."""
        return self.cursor_obj


def _entry(timestamp='2026-09-05T12:00:00.123456789Z'):
    """Build a minimal parsed AdGuard log row."""
    return {
        'timestamp': datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc),
        'client_ip': '192.168.1.10',
        'client_name': 'desktop',
        'domain': 'example.org',
        'record_type': 'A',
        'reason': 'NotFiltered',
        'dns_status': 'NOERROR',
        'upstream': '1.1.1.1',
        'elapsed_ms': 1.2,
        'cached': False,
        'answer_dnssec': False,
        'rule_text': None,
        'filter_list_id': None,
        'raw_time': timestamp,
    }


def test_insert_adguard_batch_updates_checkpoints_in_same_transaction(monkeypatch):
    """AdGuard cursor and backfill checkpoints should share the insert transaction."""
    cursor = FakeAdGuardCursor()
    database = Database(conn_params={'user': 'unifi'})

    @contextmanager
    def fake_get_conn():
        """Yield the fake connection used for all writes."""
        yield FakeAdGuardConn(cursor)

    monkeypatch.setattr(database, 'get_conn', fake_get_conn)
    monkeypatch.setattr('db.core.extras.execute_batch', MagicMock())

    inserted = database.insert_adguard_batch(
        [_entry()],
        new_cursor='2026-09-05T12:00:00.123456789Z',
        expected_host='http://adguard.lan',
        config_updates={
            'adguard_backfill_older_than': None,
            'adguard_backfill_highwater': None,
        },
    )

    assert inserted == 1
    update_keys = [
        params[0]
        for sql, params in cursor.executed
        if 'INSERT INTO system_config' in sql and params
    ]
    assert update_keys == [
        'adguard_cursor',
        'adguard_backfill_older_than',
        'adguard_backfill_highwater',
    ]


def test_capped_adguard_poll_persists_checkpoint_through_batch(monkeypatch):
    """Capped backfill polls should not write checkpoint config outside the batch."""
    poller = AdGuardHomePoller.__new__(AdGuardHomePoller)
    poller._db = MagicMock()
    poller._db.insert_adguard_batch = MagicMock(return_value=1)
    poller._stop = MagicMock()
    poller._thread = None
    poller._clients = adguard_poller._ClientCache()
    poller._clients_refreshed = 0.0
    poller._enabled = True
    poller._host = 'http://adguard.lan'
    poller._username = 'admin'
    poller._password = 'secret'

    def fake_get_config(_db, key, default=None):
        """Return poll config with no existing cursor/checkpoint."""
        values = {
            'adguard_host': 'http://adguard.lan',
            'adguard_cursor': None,
            'adguard_backfill_older_than': None,
            'adguard_backfill_highwater': None,
        }
        return values.get(key, default)

    response = MagicMock()
    response.json.return_value = {
        'data': [{
            'time': '2026-09-05T12:00:00.123456789Z',
            'client': '192.168.1.10',
            'question': {'name': 'example.org', 'type': 'A'},
            'reason': 'NotFiltered',
            'status': 'NOERROR',
            'elapsedMs': 1.2,
        }],
        'oldest': '2026-09-05T12:00:00.123456789Z',
    }
    response.raise_for_status = MagicMock()

    def forbidden_set_config(_db, key, value):
        """Fail if poller writes AdGuard checkpoint state outside insert batch."""
        if key.startswith('adguard_backfill_'):
            raise AssertionError(f"checkpoint {key} written outside transaction")

    monkeypatch.setattr(adguard_poller, 'get_config', fake_get_config)
    monkeypatch.setattr(adguard_poller, 'set_config', forbidden_set_config, raising=False)
    monkeypatch.setattr(adguard_poller.requests, 'get', MagicMock(return_value=response))
    monkeypatch.setattr(adguard_poller, '_POLL_BATCH', 1)
    monkeypatch.setattr(adguard_poller, '_MAX_POLL_PAGES', 1)
    monkeypatch.setattr(AdGuardHomePoller, '_refresh_clients', lambda *args: None)

    poller._poll()

    poller._db.insert_adguard_batch.assert_called_once()
    _args, kwargs = poller._db.insert_adguard_batch.call_args
    assert kwargs['new_cursor'] is None
    assert kwargs['config_updates'] == {
        'adguard_backfill_older_than': '2026-09-05T12:00:00.123456789Z',
        'adguard_backfill_highwater': '2026-09-05T12:00:00.123456789Z',
    }
