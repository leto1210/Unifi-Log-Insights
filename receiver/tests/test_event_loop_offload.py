"""Blocking DB work in async handlers must run in the threadpool, not on the event loop.

The API is a single uvicorn worker: a sync DB call on the event loop (auth
check, MCP tool query) stalls every concurrent request until it returns.
"""

import sys
import threading
from types import ModuleType
from unittest.mock import MagicMock

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient


def _loop_thread_route(seen):
    """Return an async route that records the event-loop thread id."""
    async def loop_thread():
        """Record which thread async handlers run on."""
        seen['loop'] = threading.get_ident()
        return {}
    return loop_thread


@pytest.fixture
def api_module(monkeypatch):
    """Import api with every router stubbed, so only the middleware is real."""
    for name in list(sys.modules):
        if name == 'api' or name.startswith('routes'):
            monkeypatch.delitem(sys.modules, name, raising=False)
    deps = MagicMock(APP_VERSION='test')
    monkeypatch.setitem(sys.modules, 'deps', deps)
    monkeypatch.setitem(sys.modules, 'db', MagicMock())
    for name in ('logs', 'stats', 'setup', 'unifi', 'abuseipdb', 'health', 'threats',
                 'flows', 'mcp', 'views', 'migration', 'pihole', 'adguard', 'tokens'):
        module = ModuleType(f'routes.{name}')
        module.router = APIRouter()
        monkeypatch.setitem(sys.modules, f'routes.{name}', module)
    import api
    return api


def test_auth_middleware_runs_require_auth_off_the_event_loop(api_module, monkeypatch):
    """require_auth does DB reads, so the middleware must not call it on the loop."""
    seen = {}

    def fake_require_auth(_request):
        """Record the calling thread; auth disabled."""
        seen['auth'] = threading.get_ident()
        return None

    monkeypatch.setattr(api_module, 'require_auth', fake_require_auth)
    api_module.app.add_api_route('/api/_loop_probe', _loop_thread_route(seen))

    assert TestClient(api_module.app).get('/api/_loop_probe').status_code == 200
    assert seen['auth'] != seen['loop']


@pytest.fixture
def mcp_module(monkeypatch):
    """Import routes.mcp with its dependencies stubbed."""
    for name in list(sys.modules):
        if name.startswith('routes'):
            monkeypatch.delitem(sys.modules, name, raising=False)
    for name in ('deps', 'db', 'routes.logs', 'routes.stats', 'routes.setup',
                 'routes.unifi', 'routes.health', 'routes.threats', 'routes.auth'):
        monkeypatch.setitem(sys.modules, name, MagicMock())
    import routes.mcp as mcp
    return mcp


def test_mcp_post_runs_auth_and_tools_off_the_event_loop(mcp_module, monkeypatch):
    """MCP pre-checks and tool calls hit the DB; both must leave the event loop."""
    seen = {}

    def fake_authorize(_request):
        """Record the calling thread and accept the token."""
        seen['authorize'] = threading.get_ident()
        return {'token_id': 1}

    def fake_handle_request(_body, _token_info):
        """Record the calling thread and return an empty JSON-RPC result."""
        seen['tool'] = threading.get_ident()
        return {'jsonrpc': '2.0', 'id': 1, 'result': {}}

    monkeypatch.setattr(mcp_module, '_authorize', fake_authorize)
    monkeypatch.setattr(mcp_module, '_handle_request', fake_handle_request)
    app = FastAPI()
    app.include_router(mcp_module.router)
    app.add_api_route('/_loop_probe', _loop_thread_route(seen))
    client = TestClient(app)

    client.get('/_loop_probe')
    resp = client.post('/api/mcp', json={'jsonrpc': '2.0', 'id': 1, 'method': 'ping'})

    assert resp.status_code == 200
    assert seen['authorize'] != seen['loop']
    assert seen['tool'] != seen['loop']


def test_lifespan_runs_auth_route_coverage_check(api_module, monkeypatch):
    """Startup must still fail closed on an /api/ route outside the auth policy."""
    monkeypatch.setattr(api_module, 'init_proxy_token', lambda: None)
    monkeypatch.setattr(api_module, 'log_proxy_token', lambda: None)
    api_module.app.add_api_route('/api/_uncovered_probe', lambda: {})

    with pytest.raises(RuntimeError, match='_uncovered_probe'):
        with TestClient(api_module.app):
            pass
