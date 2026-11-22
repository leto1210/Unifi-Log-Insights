"""API token auth writes last_used_at at most once per token per interval."""

import hmac
import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def auth(monkeypatch):
    """Import routes.auth with deps/db stubbed and a fresh throttle map."""
    for name in list(sys.modules):
        if name.startswith('routes'):
            monkeypatch.delitem(sys.modules, name, raising=False)
    monkeypatch.setitem(sys.modules, 'deps', MagicMock())
    monkeypatch.setitem(sys.modules, 'db', MagicMock())
    import routes.auth as module
    return module


def _token_db(auth, token, salt='s'):
    """Wire get_conn to a cursor returning one row whose HMAC matches `token`."""
    row = {'token_id': 7, 'token_hash': hmac.new(salt.encode(), token.encode(), 'sha256').hexdigest(),
           'token_salt': salt, 'scopes': ['logs.read']}
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchall.return_value = [row]
    conn = MagicMock()
    conn.cursor.return_value = cur
    auth.get_conn = lambda: conn
    auth.put_conn = lambda _c: None
    return cur


def _updates(cur):
    """Number of last_used_at UPDATEs issued on the cursor."""
    return sum('UPDATE api_tokens SET last_used_at' in str(c) for c in cur.execute.call_args_list)


def test_repeated_auth_writes_last_used_once_per_interval(auth, monkeypatch):
    """Ten validations inside one minute → one UPDATE; after the interval → another."""
    clock = [1000.0]
    monkeypatch.setattr(auth.time, 'monotonic', lambda: clock[0])
    cur = _token_db(auth, 'uli_abcdefgh123')

    for _ in range(10):
        assert auth._validate_api_token('uli_abcdefgh123')['token_id'] == 7
    assert _updates(cur) == 1

    clock[0] += auth._TOKEN_USE_WRITE_INTERVAL_SECS + 1
    auth._validate_api_token('uli_abcdefgh123')
    assert _updates(cur) == 2


def test_throttle_is_per_token(auth, monkeypatch):
    """Two tokens used in the same minute are both recorded."""
    monkeypatch.setattr(auth.time, 'monotonic', lambda: 1000.0)
    assert auth._should_record_token_use(1) is True
    assert auth._should_record_token_use(2) is True
    assert auth._should_record_token_use(1) is False
