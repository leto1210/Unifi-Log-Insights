"""Regression tests for stored integration secrets and test destinations."""

import importlib
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from pihole_api import PiHolePoller
from service.integration_urls import same_integration_destination


@pytest.fixture
def unifi_route(monkeypatch):
    """Load the UniFi route with isolated settings and outbound client."""
    for name in list(sys.modules):
        if name.startswith('routes.'):
            monkeypatch.delitem(sys.modules, name, raising=False)
    db = MagicMock()
    db.get_config.side_effect = lambda _db, key, default='': {
        'unifi_host': 'https://controller.lan',
        'unifi_api_key_host': 'https://controller.lan',
        'unifi_credentials_host': 'https://controller.lan',
        'unifi_api_key': 'encrypted-key',
        'unifi_username': 'encrypted-user',
        'unifi_password': 'encrypted-password',
    }.get(key, default)
    db.decrypt_api_key.return_value = 'stored-secret'
    db.encrypt_api_key.return_value = 'new-cipher'
    deps = MagicMock()
    deps.unifi_api.test_connection.return_value = {'success': False}
    monkeypatch.setitem(sys.modules, 'db', db)
    monkeypatch.setitem(sys.modules, 'deps', deps)
    unifi = importlib.import_module('routes.unifi')
    return unifi, deps, db


def test_unifi_saved_key_cannot_move_to_another_host(unifi_route):
    """Reject reuse before the outbound client sees the stored key."""
    route, deps, db = unifi_route
    with pytest.raises(HTTPException) as exc:
        route.test_unifi_connection({
            'host': 'https://other.lan', 'use_saved_key': True,
        })
    assert exc.value.status_code == 400
    deps.unifi_api.test_connection.assert_not_called()
    db.set_config.assert_not_called()


def test_unifi_saved_key_accepts_equivalent_host(unifi_route):
    """Default HTTPS port and hostname case keep the destination unchanged."""
    route, deps, _ = unifi_route
    route.test_unifi_connection({
        'host': 'https://CONTROLLER.lan:443/', 'use_saved_key': True,
    })
    deps.unifi_api.test_connection.assert_called_once()


def test_unifi_explicit_new_key_clears_old_key_before_host_change(unifi_route):
    """A host edit clears the old key before a new destination is saved."""
    route, _, db = unifi_route
    route.update_unifi_settings({'host': 'https://other.lan', 'api_key': 'new-key'})
    calls = [(args[1], args[2]) for args, _ in db.set_config.call_args_list]
    assert calls.index(('unifi_api_key', '')) < calls.index(('unifi_host', 'https://other.lan'))
    assert calls.index(('unifi_api_key_host', 'https://other.lan')) < calls.index(
        ('unifi_api_key', 'new-cipher'))


def test_pihole_omitted_password_cannot_move_to_another_host():
    """The poller must not reuse its stored password for a supplied host."""
    poller = PiHolePoller.__new__(PiHolePoller)
    poller.host = 'https://pihole.lan'
    poller._password = 'stored-secret'
    poller.TIMEOUT = 10
    poller._config_lock = threading.RLock()
    with patch('pihole_api.requests.Session') as session:
        result = poller.test_connection('https://other.lan', '')
    assert result['success'] is False
    session.assert_not_called()


@pytest.mark.parametrize(('left', 'right', 'same'), [
    ('https://controller.lan', 'https://CONTROLLER.lan:443/', True),
    ('http://controller.lan', 'http://controller.lan:80', True),
    ('https://controller.lan', 'http://controller.lan', False),
    ('https://controller.lan:8443', 'https://controller.lan', False),
    ('https://controller.lan/proxy', 'https://controller.lan', False),
])
def test_destination_identity(left, right, same):
    """Canonical comparison includes scheme, effective port and base path."""
    assert same_integration_destination(left, right) is same


@pytest.mark.parametrize('bad', [
    'https://user@controller.lan', 'https://controller.lan/a/../b',
    'https://controller.lan/a%2fb', 'https://controller.lan\\@other.lan',
])
def test_destination_identity_rejects_ambiguous_urls(bad):
    """Ambiguous URL forms cannot silently inherit saved credentials."""
    with pytest.raises(ValueError):
        same_integration_destination(bad, 'https://controller.lan')


def test_unifi_put_host_change_requires_new_credentials(unifi_route):
    """A settings edit cannot reload an old key against another host."""
    route, deps, db = unifi_route
    with pytest.raises(HTTPException) as exc:
        route.update_unifi_settings({'host': 'https://other.lan'})
    assert exc.value.status_code == 400
    db.set_config.assert_not_called()
    deps.unifi_api.reload_config.assert_not_called()


def test_unifi_saved_self_hosted_credentials_cannot_move(unifi_route):
    """The self hosted login path has the same destination binding."""
    route, deps, _ = unifi_route
    with pytest.raises(HTTPException) as exc:
        route.test_unifi_connection({
            'host': 'https://other.lan', 'controller_type': 'self_hosted',
            'use_saved_credentials': True,
        })
    assert exc.value.status_code == 400
    deps.unifi_api.test_connection.assert_not_called()


@pytest.mark.parametrize(('binding_key', 'test_body'), [
    ('unifi_api_key_host', {'use_saved_key': True}),
    ('unifi_credentials_host', {
        'controller_type': 'self_hosted', 'use_saved_credentials': True,
    }),
])
def test_unifi_saved_secret_without_persisted_binding_is_rejected(
        unifi_route, binding_key, test_body):
    """A failed legacy migration cannot rebind a secret after a host import."""
    route, deps, db = unifi_route
    original_get = db.get_config.side_effect
    db.get_config.side_effect = lambda database, key, default='': (
        '' if key == binding_key else original_get(database, key, default))
    with pytest.raises(HTTPException) as exc:
        route.test_unifi_connection({
            'host': 'https://controller.lan', **test_body,
        })
    assert exc.value.status_code == 400
    deps.unifi_api.test_connection.assert_not_called()


def test_pihole_put_host_change_requires_new_password(monkeypatch):
    """Changing Pi-hole destination cannot retain the saved password."""
    for name in list(sys.modules):
        if name.startswith('routes.'):
            monkeypatch.delitem(sys.modules, name, raising=False)
    db = MagicMock()
    db.get_config.return_value = 'https://pihole.lan'
    deps = MagicMock()
    monkeypatch.setitem(sys.modules, 'db', db)
    monkeypatch.setitem(sys.modules, 'deps', deps)
    pihole = importlib.import_module('routes.pihole')
    with pytest.raises(HTTPException) as exc:
        pihole.update_pihole_settings({'host': 'https://other.lan'})
    assert exc.value.status_code == 400
    db.set_config.assert_not_called()


def test_unifi_saved_key_is_disabled_after_host_changes_in_db(monkeypatch):
    """A legacy key and host edit cannot form a new active pair on reload."""
    from unifi.core import UniFiAPI
    monkeypatch.delenv('UNIFI_HOST', raising=False)
    monkeypatch.delenv('UNIFI_API_KEY', raising=False)
    config = {
        'unifi_host': 'https://new.lan',
        'unifi_api_key_host': 'https://old.lan',
        'unifi_api_key': 'cipher',
        'unifi_enabled': True,
    }
    db = MagicMock()
    db.get_config.side_effect = lambda key, default=None: config.get(key, default)
    api = UniFiAPI(db)
    assert api.host == 'https://new.lan'
    assert api.api_key == ''
    assert api.enabled is False


def test_unifi_legacy_key_gets_bound_on_initial_load(monkeypatch):
    """Legacy saved keys acquire a durable host before a later config import."""
    from unifi.core import UniFiAPI
    monkeypatch.delenv('UNIFI_HOST', raising=False)
    monkeypatch.delenv('UNIFI_API_KEY', raising=False)
    config = {
        'unifi_host': 'https://old.lan', 'unifi_api_key': 'cipher',
        'unifi_enabled': True,
    }
    db = MagicMock()
    db.get_config.side_effect = lambda key, default=None: config.get(key, default)
    db.set_config.side_effect = lambda key, value: config.__setitem__(key, value)
    api = UniFiAPI(db)
    assert config['unifi_api_key_host'] == 'https://old.lan'
    config['unifi_host'] = 'https://new.lan'
    api._resolve_config()
    assert api.api_key == ''
    assert api.enabled is False


def test_pihole_saved_password_is_disabled_after_host_changes_in_db(monkeypatch):
    """A Pi-hole password remains bound to its original host on reload."""
    monkeypatch.delenv('PIHOLE_HOST', raising=False)
    monkeypatch.delenv('PIHOLE_PASSWORD', raising=False)
    config = {
        'pihole_host': 'https://new.lan',
        'pihole_password_host': 'https://old.lan',
        'pihole_password': 'cipher',
        'pihole_enabled': True,
    }
    db = MagicMock()
    db.get_config.side_effect = lambda key, default=None: config.get(key, default)
    poller = PiHolePoller(db)
    assert poller.host == 'https://new.lan'
    assert poller._password == ''
    assert poller.enabled is False


def test_pihole_legacy_password_gets_bound_on_initial_load(monkeypatch):
    """Legacy Pi-hole passwords keep their original destination on reload."""
    monkeypatch.delenv('PIHOLE_HOST', raising=False)
    monkeypatch.delenv('PIHOLE_PASSWORD', raising=False)
    config = {
        'pihole_host': 'https://old.lan', 'pihole_password': 'cipher',
        'pihole_enabled': True,
    }
    db = MagicMock()
    db.get_config.side_effect = lambda key, default=None: config.get(key, default)
    db.set_config.side_effect = lambda key, value: config.__setitem__(key, value)
    poller = PiHolePoller(db)
    assert config['pihole_password_host'] == 'https://old.lan'
    config['pihole_host'] = 'https://new.lan'
    poller._resolve_config()
    assert poller._password == ''
    assert poller.enabled is False


@pytest.mark.parametrize(('env_host', 'env_key', 'enabled'), [
    ('', 'fake-key', False),
    ('https://env.lan', 'fake-key', True),
])
def test_unifi_env_key_requires_env_host(monkeypatch, env_host, env_key, enabled):
    """An environment key has a destination only when paired with env host."""
    from unifi.core import UniFiAPI
    if env_host:
        monkeypatch.setenv('UNIFI_HOST', env_host)
    else:
        monkeypatch.delenv('UNIFI_HOST', raising=False)
    monkeypatch.setenv('UNIFI_API_KEY', env_key)
    db = MagicMock()
    db.get_config.side_effect = lambda key, default=None: {
        'unifi_host': 'https://db.lan', 'unifi_enabled': True,
    }.get(key, default)
    api = UniFiAPI(db)
    assert api.enabled is enabled


def test_pihole_env_password_requires_env_host(monkeypatch):
    """A Pi-hole env password cannot attach to a mutable DB host."""
    monkeypatch.delenv('PIHOLE_HOST', raising=False)
    monkeypatch.setenv('PIHOLE_PASSWORD', 'fake-password')
    db = MagicMock()
    db.get_config.side_effect = lambda key, default=None: {
        'pihole_host': 'https://db.lan', 'pihole_enabled': True,
    }.get(key, default)
    poller = PiHolePoller(db)
    assert poller.enabled is False


def test_unifi_reload_waits_for_inflight_secret_bearing_request(monkeypatch):
    """A reload cannot swap host while an authenticated request is in flight."""
    from unifi.core import UniFiAPI
    monkeypatch.delenv('UNIFI_HOST', raising=False)
    monkeypatch.delenv('UNIFI_API_KEY', raising=False)
    entered = threading.Event()
    release = threading.Event()
    reloaded = threading.Event()
    urls = []
    response = MagicMock(status_code=200)
    response.json.return_value = {'data': []}
    session = MagicMock()

    def get(url, **_kwargs):
        urls.append(url)
        entered.set()
        assert release.wait(2)
        return response

    session.get.side_effect = get
    config = {'unifi_host': 'https://new.lan', 'unifi_enabled': False}
    db = MagicMock()
    db.get_config.side_effect = lambda key, default=None: config.get(key, default)
    api = UniFiAPI.__new__(UniFiAPI)
    api._db = db
    api._config_lock = threading.RLock()
    api._poll_thread = None
    api._session = session
    api._site_uuid = None
    api._csrf_token = None
    api._controller_type = 'unifi_os'
    api.host = 'https://old.lan'
    api.site = 'default'

    def reload():
        api.reload_config()
        reloaded.set()

    with ThreadPoolExecutor(max_workers=2) as pool:
        request = pool.submit(api._get, 'stat/sysinfo')
        assert entered.wait(2)
        pending_reload = pool.submit(reload)
        assert not reloaded.wait(0.05)
        release.set()
        request.result(timeout=2)
        pending_reload.result(timeout=2)
    assert urls == ['https://old.lan/proxy/network/api/s/default/stat/sysinfo']
    assert api.host == 'https://new.lan'
