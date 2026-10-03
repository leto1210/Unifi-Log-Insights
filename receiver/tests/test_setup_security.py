"""Regression checks for public setup status and configuration secrets."""

import importlib
import sys
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from starlette.requests import Request
from db import Database as RealDatabase


@pytest.fixture
def setup_route(monkeypatch):
    """Load the production setup handlers with isolated settings."""
    for name in list(sys.modules):
        if name.startswith('routes.'):
            monkeypatch.delitem(sys.modules, name, raising=False)

    config = {'setup_complete': False, 'unifi_host': 'https://old.lan',
              'unifi_api_key': 'old-cipher', 'unifi_api_key_host': 'https://old.lan'}
    db = MagicMock()
    db.get_config.side_effect = lambda _db, key, default=None: config.get(key, default)
    db.set_config.side_effect = lambda _db, key, value: config.__setitem__(key, value)
    db.encrypt_api_key.side_effect = lambda value: f'encrypted:{value}'
    db.decrypt_api_key.side_effect = lambda value: value.removeprefix('encrypted:')
    deps = MagicMock(APP_VERSION='test')
    deps.enricher_db = MagicMock()
    deps.enricher_db.set_config_many.side_effect = lambda values: config.update(values)
    deps.enricher_db.get_config_many.side_effect = lambda keys: {
        key: config[key] for key in keys if key in config
    }
    monkeypatch.setitem(sys.modules, 'db', db)
    monkeypatch.setitem(sys.modules, 'deps', deps)
    route = importlib.import_module('routes.setup')
    return route, config, db, deps


def _request(auth_info):
    """Build a request carrying the production middleware's auth state."""
    request = Request({'type': 'http', 'method': 'GET', 'path': '/api/config/export',
                       'headers': [], 'query_string': b''})
    request.state.auth_info = auth_info
    return request


@pytest.mark.parametrize('complete', [False, True])
def test_status_has_no_exact_count_query_or_ambiguous_count_field(setup_route, complete):
    """Public status exposes only setup state without counting the logs table."""
    route, config, db, _deps = setup_route
    config['setup_complete'] = complete
    assert route.setup_status() == {'setup_complete': complete}
    db.count_logs.assert_not_called()


@pytest.mark.parametrize('auth_info,status', [
    ({'user_id': None}, 401),
    ({'user_id': 1, 'token_id': 2, 'role_name': 'admin'}, 403),
    ({'user_id': 1, 'role_name': 'viewer'}, 403),
])
def test_secret_export_rejects_non_admin_sessions(setup_route, auth_info, status):
    """Only interactive admin sessions may request the plaintext UniFi key."""
    route, _config, db, _deps = setup_route
    with pytest.raises(HTTPException) as exc:
        route.export_config(_request(auth_info), include_api_key=True)
    assert exc.value.status_code == status
    db.decrypt_api_key.assert_not_called()


def test_secret_export_allows_admin_and_explicit_no_auth_mode(setup_route, monkeypatch):
    """Admin sessions and intentional single-user deployments retain export."""
    route, config, _db, deps = setup_route
    config['unifi_api_key'] = 'encrypted:synthetic-key'
    conn = MagicMock()
    conn.cursor.return_value.__enter__.return_value.fetchall.return_value = []
    deps.get_conn.return_value = conn
    for info in ({'user_id': 1, 'role_name': 'admin'}, None):
        result = route.export_config(_request(info), include_api_key=True)
        assert result['config']['unifi_api_key'] == 'synthetic-key'


def test_secret_export_round_trip_keeps_bound_host_under_env_override(setup_route, monkeypatch):
    """Backup from DB host A with key bound to env host B restores B safely."""
    route, config, _db, deps = setup_route
    config.update(unifi_host='https://db.lan', unifi_api_key_host='https://env.lan',
                  unifi_api_key='encrypted:synthetic-key')
    deps.get_conn.return_value.cursor.return_value.__enter__.return_value.fetchall.return_value = []
    monkeypatch.setenv('UNIFI_HOST', 'https://env.lan')
    backup = route.export_config(_request({'user_id': 1, 'role_name': 'admin'}),
                                 include_api_key=True)
    assert backup['includes_api_key'] is True
    assert backup['config']['unifi_host'] == 'https://env.lan'
    monkeypatch.delenv('UNIFI_HOST')
    config.update(unifi_host='https://other.lan', unifi_api_key_host='https://other.lan')
    route.import_config(backup)
    assert config['unifi_host'] == config['unifi_api_key_host'] == 'https://env.lan'
    assert config['unifi_api_key'] == 'encrypted:synthetic-key'


def test_secret_export_rejects_missing_binding(setup_route):
    """An unbound legacy key cannot be exported beside an unrelated DB host."""
    route, config, _db, _deps = setup_route
    config.update(unifi_api_key='encrypted:synthetic-key', unifi_api_key_host='')
    with pytest.raises(HTTPException) as exc:
        route.export_config(_request({'user_id': 1, 'role_name': 'admin'}),
                            include_api_key=True)
    assert exc.value.status_code == 409


def test_secret_export_uses_one_key_host_snapshot(setup_route):
    """A concurrent key replacement cannot mix the old key with a new host."""
    route, config, _db, deps = setup_route
    config.update(unifi_api_key='encrypted:old-key',
                  unifi_api_key_host='https://old.lan')
    deps.get_conn.return_value.cursor.return_value.__enter__.return_value.fetchall.return_value = []

    def replace_after_snapshot(keys):
        """Simulate another transaction committing after the snapshot read."""
        saved = {key: config[key] for key in keys}
        config.update(unifi_api_key='encrypted:new-key',
                      unifi_api_key_host='https://new.lan')
        return saved

    deps.enricher_db.get_config_many.side_effect = replace_after_snapshot
    backup = route.export_config(_request({'user_id': 1, 'role_name': 'admin'}),
                                 include_api_key=True)
    assert backup['config']['unifi_api_key'] == 'old-key'
    assert backup['config']['unifi_host'] == 'https://old.lan'
    deps.enricher_db.get_config_many.assert_called_once_with(
        ('unifi_api_key', 'unifi_api_key_host'))


def test_import_new_key_binds_imported_host(setup_route):
    """A restored key is tied to the destination restored alongside it."""
    route, config, _db, deps = setup_route
    result = route.import_config({'config': {'unifi_host': 'https://new.lan',
                                             'unifi_api_key': 'new-key'}})
    assert 'failed_keys' not in result
    assert config['unifi_api_key_host'] == 'https://new.lan'
    assert config['unifi_api_key'] == 'encrypted:new-key'
    deps.enricher_db.set_config_many.assert_called_once_with({
        'unifi_api_key': 'encrypted:new-key',
        'unifi_api_key_host': 'https://new.lan',
    })


def test_import_host_only_does_not_rebind_existing_key(setup_route):
    """Changing only the host leaves the old credential bound to its old host."""
    route, config, _db, _deps = setup_route
    route.import_config({'config': {'unifi_host': 'https://new.lan'}})
    assert config['unifi_api_key_host'] == 'https://old.lan'
    assert config['unifi_api_key'] == 'old-cipher'


def test_import_host_only_binds_legacy_key_to_old_host(setup_route):
    """Legacy unbound keys must not be auto-associated with the imported host."""
    route, config, _db, _deps = setup_route
    config['unifi_api_key_host'] = ''
    route.import_config({'config': {'unifi_host': 'https://new.lan'}})
    assert config['unifi_api_key_host'] == 'https://old.lan'


def test_import_host_only_rejects_move_when_legacy_key_has_no_old_host(setup_route):
    """Without an old destination, importing a new host cannot migrate a key."""
    route, config, _db, _deps = setup_route
    config['unifi_host'] = ''
    config['unifi_api_key_host'] = ''
    result = route.import_config({'config': {'unifi_host': 'https://new.lan'}})
    assert 'unifi_host' in result['failed_keys']
    assert config['unifi_host'] == ''


def test_import_replaces_unbound_key_and_unknown_host_as_pair(setup_route):
    """A fresh complete pair can replace an unusable legacy credential."""
    route, config, _db, deps = setup_route
    config['unifi_host'] = ''
    config['unifi_api_key_host'] = ''
    result = route.import_config({'config': {'unifi_host': 'https://new.lan',
                                             'unifi_api_key': 'new-key'}})
    assert 'failed_keys' not in result
    assert config['unifi_host'] == config['unifi_api_key_host'] == 'https://new.lan'
    assert config['unifi_api_key'] == 'encrypted:new-key'
    deps.enricher_db.set_config_many.assert_called_once_with({
        'unifi_api_key': 'encrypted:new-key',
        'unifi_api_key_host': 'https://new.lan',
        'unifi_host': 'https://new.lan',
    })


def test_failed_new_key_leaves_unknown_legacy_host_unchanged(setup_route, monkeypatch):
    """A rejected pair cannot move the old unbound key to a new host."""
    route, config, _db, _deps = setup_route
    config['unifi_host'] = ''
    config['unifi_api_key_host'] = ''
    monkeypatch.setenv('UNIFI_HOST', 'https://other.lan')
    result = route.import_config({'config': {'unifi_host': 'https://new.lan',
                                             'unifi_api_key': 'new-key'}})
    assert {'unifi_host', 'unifi_api_key'} <= set(result['failed_keys'])
    assert config['unifi_host'] == config['unifi_api_key_host'] == ''
    assert config['unifi_api_key'] == 'old-cipher'


def test_encryption_failure_does_not_move_unknown_legacy_host(setup_route):
    """Failure preparing the replacement key leaves the old pair in place."""
    route, config, db, _deps = setup_route
    config['unifi_host'] = ''
    config['unifi_api_key_host'] = ''
    db.encrypt_api_key.side_effect = ValueError('synthetic encryption failure')
    result = route.import_config({'config': {'unifi_host': 'https://new.lan',
                                             'unifi_api_key': 'new-key'}})
    assert {'unifi_host', 'unifi_api_key'} <= set(result['failed_keys'])
    assert config['unifi_host'] == config['unifi_api_key_host'] == ''
    assert config['unifi_api_key'] == 'old-cipher'


def test_batch_failure_does_not_move_unknown_legacy_host(setup_route):
    """The route leaves the old pair intact if atomic persistence fails."""
    route, config, _db, deps = setup_route
    config['unifi_host'] = ''
    config['unifi_api_key_host'] = ''
    deps.enricher_db.set_config_many.side_effect = RuntimeError('synthetic write failure')
    result = route.import_config({'config': {'unifi_host': 'https://new.lan',
                                             'unifi_api_key': 'new-key'}})
    assert {'unifi_host', 'unifi_api_key'} <= set(result['failed_keys'])
    assert config['unifi_host'] == config['unifi_api_key_host'] == ''
    assert config['unifi_api_key'] == 'old-cipher'


def test_database_config_batch_rolls_back_second_upsert_failure():
    """An error after one UPSERT rolls back the entire key/host transaction."""
    database = RealDatabase.__new__(RealDatabase)
    database.pool = MagicMock()
    conn = database.pool.getconn.return_value
    conn.closed = False
    conn.cursor.return_value.__enter__.return_value.execute.side_effect = [
        None, RuntimeError('synthetic second UPSERT failure'),
    ]
    with pytest.raises(RuntimeError, match='second UPSERT'):
        database.set_config_many({'unifi_api_key': 'new-cipher',
                                  'unifi_api_key_host': 'https://new.lan'})
    assert conn.cursor.return_value.__enter__.return_value.execute.call_count == 2
    conn.commit.assert_not_called()
    conn.rollback.assert_called_once()


def test_database_config_pair_is_selected_in_one_query():
    """The DB helper reads key and bound host from the same SQL statement."""
    database = RealDatabase.__new__(RealDatabase)
    database.pool = MagicMock()
    conn = database.pool.getconn.return_value
    conn.closed = False
    cursor = conn.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [
        ('unifi_api_key', 'encrypted:old-key'),
        ('unifi_api_key_host', 'https://old.lan'),
    ]
    assert database.get_config_many(('unifi_api_key', 'unifi_api_key_host')) == {
        'unifi_api_key': 'encrypted:old-key',
        'unifi_api_key_host': 'https://old.lan',
    }
    cursor.execute.assert_called_once()


def test_import_new_key_without_host_binds_effective_host(setup_route, monkeypatch):
    """A key-only restore uses the env-overridden effective UniFi host."""
    route, config, _db, _deps = setup_route
    monkeypatch.setenv('UNIFI_HOST', 'https://env.lan')
    route.import_config({'config': {'unifi_api_key': 'new-key'}})
    assert config['unifi_api_key_host'] == 'https://env.lan'


def test_import_key_for_different_host_rejected_under_env_override(setup_route, monkeypatch):
    """A backup key for another controller cannot attach to UNIFI_HOST."""
    route, config, _db, _deps = setup_route
    monkeypatch.setenv('UNIFI_HOST', 'https://env.lan')
    result = route.import_config({'config': {'unifi_host': 'https://backup.lan',
                                             'unifi_api_key': 'new-key'}})
    assert 'unifi_api_key' in result['failed_keys']
    assert config['unifi_api_key'] == 'old-cipher'
    assert config['unifi_api_key_host'] == 'https://old.lan'


def test_rejected_new_key_does_not_rebind_legacy_key(setup_route, monkeypatch):
    """Failed key import must not let a legacy key follow a new DB host."""
    route, config, _db, _deps = setup_route
    config['unifi_api_key_host'] = ''
    monkeypatch.setenv('UNIFI_HOST', 'https://env.lan')
    result = route.import_config({'config': {'unifi_host': 'https://backup.lan',
                                             'unifi_api_key': 'new-key'}})
    assert 'unifi_api_key' in result['failed_keys']
    assert config['unifi_api_key_host'] == 'https://old.lan'


def test_import_key_for_equivalent_env_host_uses_effective_host(setup_route, monkeypatch):
    """Equivalent backup/env URLs still permit an explicit fresh key."""
    route, config, _db, _deps = setup_route
    monkeypatch.setenv('UNIFI_HOST', 'https://CONTROLLER.lan:443/')
    result = route.import_config({'config': {'unifi_host': 'https://controller.lan',
                                             'unifi_api_key': 'new-key'}})
    assert 'failed_keys' not in result
    assert config['unifi_api_key_host'] == 'https://CONTROLLER.lan:443/'


def test_import_key_without_any_host_is_rejected(setup_route, monkeypatch):
    """A new key cannot be stored if no destination is known."""
    route, config, _db, _deps = setup_route
    config['unifi_host'] = ''
    monkeypatch.delenv('UNIFI_HOST', raising=False)
    result = route.import_config({'config': {'unifi_api_key': 'new-key'}})
    assert 'unifi_api_key' in result['failed_keys']
    assert config['unifi_api_key'] == 'old-cipher'
