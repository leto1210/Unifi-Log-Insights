"""Test the production random proxy secret and forwarded-header trust rules."""

import sys
from unittest.mock import MagicMock

import pytest
from starlette.requests import Request


@pytest.fixture
def auth_module(monkeypatch):
    """Import the real auth helpers without opening a database pool."""
    for name in list(sys.modules):
        if name.startswith('routes'):
            monkeypatch.delitem(sys.modules, name, raising=False)
    deps = MagicMock()
    deps.enricher_db = object()
    monkeypatch.setitem(sys.modules, 'deps', deps)
    db = MagicMock()
    db.get_config.return_value = None
    monkeypatch.setitem(sys.modules, 'db', db)
    from routes import auth
    return auth, db


def _request(headers=None, scheme='http'):
    """Construct a Starlette request with an internal peer address."""
    scope = {
        'type': 'http', 'method': 'GET', 'path': '/', 'scheme': scheme,
        'server': ('internal.test', 80), 'client': ('192.0.2.5', 4321),
        'headers': [(name.lower().encode(), value.encode())
                    for name, value in (headers or {}).items()],
    }
    return Request(scope)


def test_proxy_token_is_random_and_persisted(auth_module):
    """A new proxy credential is random and stored for later restarts."""
    auth, db = auth_module
    first = auth._generate_or_retrieve_proxy_token()
    second = auth._generate_or_retrieve_proxy_token()
    assert len(first) == len(second) == 64
    assert first != second
    assert db.set_config.call_count == 2
    db.get_config.return_value = first
    assert auth._generate_or_retrieve_proxy_token() == first
    assert db.set_config.call_count == 2


@pytest.mark.parametrize('header, trusted', [
    ('a' * 64, True),
    ('wrong', False),
    (None, False),
])
def test_forwarded_headers_require_proxy_secret(auth_module, monkeypatch,
                                                header, trusted):
    """Both forwarded protocol and client IP need the exact shared secret."""
    auth, _db = auth_module
    monkeypatch.setattr(auth, 'PROXY_AUTH_TOKEN', 'a' * 64)
    headers = {'x-forwarded-proto': 'https', 'x-forwarded-for': '198.51.100.7'}
    if header is not None:
        headers['x-uli-proxy-auth'] = header
    request = _request(headers)
    assert auth._is_trusted_proxy(request) is trusted
    assert auth.get_forwarded_proto(request) == ('https' if trusted else 'http')
    assert auth.get_real_client_ip(request) == ('198.51.100.7' if trusted else '192.0.2.5')


def test_uninitialized_proxy_token_fails_closed(auth_module):
    """No startup token means forwarded headers never gain authority."""
    auth, _db = auth_module
    auth.PROXY_AUTH_TOKEN = None
    request = _request({'x-uli-proxy-auth': 'a' * 64,
                        'x-forwarded-proto': 'https'})
    assert auth._is_trusted_proxy(request) is False
    assert auth.get_forwarded_proto(request) == 'http'
