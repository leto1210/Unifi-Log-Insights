"""Tests for the /api/services and /api/protocols dropdown endpoints in routes/logs.py.

Regression: these DISTINCT scans over the 24h window of the large logs table are
cheap when warm but can exceed the pool's 30s statement_timeout on a cold buffer
cache, returning 500s. Each handler must raise the per-transaction
statement_timeout via `SET LOCAL statement_timeout = '90s'` before the scan.

deps.py opens DB connections at import time, so we mock the deps module before
importing routes.logs.
"""

import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def _clear_response_cache():
    """The endpoints are wrapped in a 600s ttl_cache; clear it between tests so a
    prior cached payload does not short-circuit the DB-mocked path."""
    yield
    try:
        from routes._response_cache import clear_cache
        clear_cache()
    except ImportError:
        pass


@pytest.fixture
def client(monkeypatch):
    """FastAPI TestClient over routes.logs with a mocked deps module."""
    for mod_name in list(sys.modules):
        if mod_name.startswith('routes'):
            monkeypatch.delitem(sys.modules, mod_name, raising=False)

    # routes.logs does `from deps import ... ttl_cache`. We mock deps, but the
    # cache decorator must be the REAL one — a MagicMock decorator replaces the
    # endpoint with a MagicMock whose (*args, **kwargs) signature makes FastAPI
    # demand args/kwargs query params (422). Use the genuine ttl_cache.
    from response_cache import ttl_cache

    mock_deps = MagicMock()
    mock_deps.get_conn = MagicMock()
    mock_deps.put_conn = MagicMock()
    mock_deps.enricher_db = MagicMock()
    mock_deps.ttl_cache = ttl_cache
    monkeypatch.setitem(sys.modules, 'deps', mock_deps)

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from routes.logs import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app), mock_deps


def _mock_conn(mock_deps, rows):
    """Wire get_conn() to a cursor whose fetchall() returns `rows` (list of tuples)."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall = MagicMock(return_value=rows)
    mock_cursor.execute = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    mock_deps.get_conn.return_value = mock_conn
    return mock_conn, mock_cursor


def _executed_sql(mock_cursor):
    return [call.args[0] for call in mock_cursor.execute.call_args_list]


class TestServices:
    def test_returns_services(self, client):
        test_client, mock_deps = client
        _mock_conn(mock_deps, [('dns',), ('https',), ('ntp',)])

        resp = test_client.get('/api/services')

        assert resp.status_code == 200
        assert resp.json() == {'services': ['dns', 'https', 'ntp']}

    def test_raises_statement_timeout_before_scan(self, client):
        test_client, mock_deps = client
        _, mock_cursor = _mock_conn(mock_deps, [])

        resp = test_client.get('/api/services')

        assert resp.status_code == 200
        sql = _executed_sql(mock_cursor)
        # SET LOCAL must run first, and inside the same txn as the scan.
        assert sql[0] == "SET LOCAL statement_timeout = '90s'"
        assert any('DISTINCT service_name' in s for s in sql[1:])


class TestProtocols:
    def test_returns_protocols(self, client):
        test_client, mock_deps = client
        _mock_conn(mock_deps, [('tcp',), ('udp',), ('icmp',)])

        resp = test_client.get('/api/protocols')

        assert resp.status_code == 200
        assert resp.json() == {'protocols': ['tcp', 'udp', 'icmp']}

    def test_raises_statement_timeout_before_scan(self, client):
        test_client, mock_deps = client
        _, mock_cursor = _mock_conn(mock_deps, [])

        resp = test_client.get('/api/protocols')

        assert resp.status_code == 200
        sql = _executed_sql(mock_cursor)
        assert sql[0] == "SET LOCAL statement_timeout = '90s'"
        assert any('DISTINCT protocol' in s for s in sql[1:])
