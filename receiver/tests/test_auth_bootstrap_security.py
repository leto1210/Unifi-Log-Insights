"""Exercise the real auth middleware during first-admin enrollment."""

import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient


@pytest.fixture
def protected_app(monkeypatch):
    """Build the production auth middleware with isolated routes and DB state."""
    for name in list(sys.modules):
        if name == 'api' or name.startswith('routes'):
            monkeypatch.delitem(sys.modules, name, raising=False)

    state = {'admin': False, 'users': False, 'auth_enabled': False}
    deps = MagicMock(APP_VERSION='test')
    deps.enricher_db = object()
    monkeypatch.setitem(sys.modules, 'deps', deps)
    db = MagicMock()
    db.get_config.side_effect = lambda _db, key, default=None: state.get(key, default)
    db.set_config.side_effect = lambda _db, key, value: state.__setitem__(key, value)
    monkeypatch.setitem(sys.modules, 'db', db)

    # Keep the production auth and token routers, and supply harmless route
    # targets for the other API routers. Only middleware policy is under test.
    route_names = ('logs', 'stats', 'setup', 'unifi', 'abuseipdb', 'health',
                   'threats', 'flows', 'mcp', 'views', 'migration', 'pihole',
                   'adguard')
    for name in route_names:
        module = ModuleType(f'routes.{name}')
        module.router = APIRouter()
        if name == 'logs':
            module.router.add_api_route('/api/logs', lambda: {'logs': []})
        elif name == 'setup':
            module.router.add_api_route('/api/config', lambda: {'secret': 'synthetic'})
            module.router.add_api_route('/api/config/export', lambda: {'secret': 'synthetic'})
            module.router.add_api_route('/api/setup/status', lambda: {'ready': True})
        elif name == 'health':
            module.router.add_api_route('/api/health', lambda: {'ok': True})
        monkeypatch.setitem(sys.modules, f'routes.{name}', module)

    monkeypatch.setenv('AUTH_ENABLED', 'true')
    from routes import auth
    from routes import tokens
    import api

    monkeypatch.setattr(auth, '_has_admin', lambda: state['admin'])
    monkeypatch.setattr(auth, '_has_users', lambda: state['users'])
    monkeypatch.setattr(auth, 'PROXY_AUTH_TOKEN', 'a' * 64)
    return TestClient(api.app), auth, tokens, state


def test_enrollment_blocks_anonymous_application_routes(protected_app):
    """Protected installation must expose only health and enrollment routes."""
    client, _auth, _tokens, _state = protected_app
    for path in ('/api/logs', '/api/config', '/api/config/export',
                 '/api/setup/status', '/api/tokens'):
        assert client.get(path).status_code == 401, path
    assert client.get('/api/health').status_code == 200
    status = client.get('/api/auth/status')
    assert status.status_code == 200
    assert status.json()['has_admin'] is False
    assert status.json()['auth_enabled_effective'] is True


def test_token_creation_blocked_before_first_admin(protected_app):
    """HTTPS alone must not permit ownerless token creation in bootstrap."""
    client, _auth, _tokens, _state = protected_app
    response = client.post('/api/tokens', json={'name': 'x', 'scopes': ['logs.read']},
                           headers={'x-forwarded-proto': 'https',
                                    'x-uli-proxy-auth': 'a' * 64})
    assert response.status_code == 401


def test_auth_disabled_keeps_single_user_mode(protected_app, monkeypatch):
    """The explicit no-auth deployment mode remains open."""
    client, auth, _tokens, _state = protected_app
    monkeypatch.setattr(auth, 'AUTH_ENABLED', False)
    assert client.get('/api/logs').status_code == 200
    assert client.get('/api/config').status_code == 200


def test_after_admin_requires_authentication(protected_app):
    """A completed installation must enforce login on application routes."""
    client, _auth, _tokens, state = protected_app
    state.update(admin=True, users=True, auth_enabled=True)
    assert client.get('/api/logs').status_code == 401
    assert client.get('/api/health').status_code == 200


def test_viewer_session_remains_read_only(protected_app, monkeypatch):
    """Established viewer sessions read logs but cannot change configuration."""
    client, auth, _tokens, state = protected_app
    state.update(admin=True, users=True, auth_enabled=True)
    monkeypatch.setattr(auth, '_validate_session', lambda _token: {
        'user_id': 9, 'role_name': 'viewer', 'username': 'viewer',
    })
    client.cookies.set('uli_session', 'synthetic-session')
    assert client.get('/api/logs').status_code == 200
    assert client.post('/api/tokens', json={'name': 'x', 'scopes': ['logs.read']}).status_code == 403


def test_setup_requires_token_and_trusted_https(protected_app, monkeypatch):
    """Enrollment stays reachable but rejects missing proof or insecure transport."""
    client, _auth, _tokens, _state = protected_app
    monkeypatch.setenv('SETUP_TOKEN', 'synthetic-enrollment-secret')
    body = {'username': 'admin', 'password': 'synthetic-password'}
    assert client.post('/api/auth/setup', json=body).status_code == 401
    bad = client.post('/api/auth/setup', json=body,
                      headers={'x-setup-token': 'incorrect'})
    assert bad.status_code == 401
    insecure = client.post('/api/auth/setup', json=body,
                           headers={'x-setup-token': 'synthetic-enrollment-secret',
                                    'x-forwarded-proto': 'https',
                                    'x-uli-proxy-auth': 'wrong'})
    assert insecure.status_code == 403


def test_setup_creates_first_admin_then_closes_public_setup(protected_app, monkeypatch):
    """Valid enrollment creates a session and activates normal auth gating."""
    client, auth, _tokens, state = protected_app
    monkeypatch.setenv('SETUP_TOKEN', 'synthetic-enrollment-secret')
    cursor = MagicMock()
    cursor.fetchone.side_effect = [(False,), (1,), (42,)]

    def execute(query, _params=None):
        """Reflect the inserted admin in the isolated DB state."""
        if 'INSERT INTO users' in query:
            state.update(admin=True, users=True)

    cursor.execute.side_effect = execute
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    monkeypatch.setattr(auth, 'get_conn', lambda: conn)
    monkeypatch.setattr(auth, 'put_conn', lambda _conn: None)
    monkeypatch.setattr(auth, '_write_audit', lambda *args: None)
    monkeypatch.setattr(auth, '_create_session', lambda *_args: 'synthetic-session')
    response = client.post('/api/auth/setup',
                           json={'username': 'admin', 'password': 'synthetic-password'},
                           headers={'x-setup-token': 'synthetic-enrollment-secret',
                                    'x-forwarded-proto': 'https',
                                    'x-uli-proxy-auth': 'a' * 64})
    assert response.status_code == 200
    assert state['auth_enabled'] is True
    assert 'uli_session=synthetic-session' in response.headers['set-cookie']
    assert client.get('/api/logs').status_code == 401
    assert client.post('/api/auth/setup', json={},
                       headers={'x-setup-token': 'synthetic-enrollment-secret'}).status_code == 400


@pytest.mark.parametrize('owner_permissions, expected_status', [
    ([], 403),
    (['stats.read'], 403),
    (['logs.read'], 200),
    (['*'], 200),
])
def test_owner_permissions_limit_token(protected_app, monkeypatch,
                                       owner_permissions, expected_status):
    """The real token validator and middleware must respect empty intersections."""
    client, auth, _tokens, state = protected_app
    state.update(admin=True, users=True, auth_enabled=True)
    monkeypatch.setattr(auth, '_validate_api_token', lambda _token: {
        'token_id': 7, 'owner_user_id': 42, 'scopes': ['logs.read'],
        'user_permissions': owner_permissions, 'role_name': 'viewer',
    })
    response = client.get('/api/logs', headers={'authorization': 'Bearer synthetic'})
    assert response.status_code == expected_status


def test_ownerless_token_retains_intentional_scopes(protected_app, monkeypatch):
    """Older ownerless tokens retain their explicitly assigned scopes."""
    client, auth, _tokens, state = protected_app
    state.update(admin=True, users=True, auth_enabled=True)
    monkeypatch.setattr(auth, '_validate_api_token', lambda _token: {
        'token_id': 8, 'owner_user_id': None, 'scopes': ['logs.read'],
        'user_permissions': [], 'role_name': None,
    })
    assert client.get('/api/logs', headers={'authorization': 'Bearer synthetic'}).status_code == 200
