"""Independent security regressions across setup, MCP and CSV boundaries."""

import csv
import importlib
import io
import itertools
import re
import sys
from unittest.mock import MagicMock

import pytest

from query_helpers import sanitize_csv_cell
from unifi_api import UniFiAPI


@pytest.mark.parametrize('old_host', ['https://old.lan', ''])
def test_host_only_import_keeps_legacy_self_hosted_credentials_on_old_host(
        monkeypatch, old_host):
    """A backup host edit must not retarget login secrets from a legacy install."""
    for name in list(sys.modules):
        if name.startswith('routes.'):
            monkeypatch.delitem(sys.modules, name, raising=False)

    monkeypatch.delenv('UNIFI_HOST', raising=False)
    monkeypatch.delenv('UNIFI_API_KEY', raising=False)
    config = {
        'unifi_host': old_host,
        'unifi_controller_type': 'self_hosted',
        'unifi_enabled': True,
        'unifi_username': 'encrypted-user',
        'unifi_password': 'encrypted-password',
        # Existing installs before destination binding have no credentials host.
    }
    db_module = MagicMock()
    db_module.get_config.side_effect = lambda _db, key, default='': config.get(key, default)
    db_module.set_config.side_effect = lambda _db, key, value: config.__setitem__(key, value)
    deps = MagicMock(APP_VERSION='test')
    deps.enricher_db.get_config.side_effect = lambda key, default='': config.get(key, default)
    deps.enricher_db.set_config.side_effect = lambda key, value: config.__setitem__(key, value)
    monkeypatch.setitem(sys.modules, 'db', db_module)
    monkeypatch.setitem(sys.modules, 'deps', deps)
    route = importlib.import_module('routes.setup')

    result = route.import_config({'config': {'unifi_host': 'https://new.lan'}})
    if old_host:
        assert result['imported_keys'] == ['unifi_host']
        assert config['unifi_host'] == 'https://new.lan'
        assert config.get('unifi_credentials_host') == old_host
    else:
        assert 'unifi_host' in result['failed_keys']
        assert config['unifi_host'] == ''
        assert not config.get('unifi_credentials_host')

    api = UniFiAPI.__new__(UniFiAPI)
    api._db = deps.enricher_db
    api._decrypt_db_credential = lambda key: config[key].removeprefix('encrypted-')
    api._decrypt_db_key = lambda: ''
    api._resolve_config()
    assert api.host == ('https://new.lan' if old_host else '')
    assert api._username == api._password == ''
    assert api.enabled is False


def test_mcp_rejects_token_when_owner_has_no_effective_scope(monkeypatch):
    """MCP must use the role intersection, including the empty set."""
    monkeypatch.setitem(sys.modules, 'deps', MagicMock(APP_VERSION='test'))
    from routes import auth, mcp

    monkeypatch.setattr(auth, '_validate_api_token', lambda _token: {
        'token_id': 7,
        'owner_user_id': 42,
        'scopes': ['logs.read'],
        'user_permissions': [],
    })
    # mcp imports the validator by name at module import; keep the real
    # validator while replacing its database lookup only.
    monkeypatch.setattr(mcp, 'validate_token_with_effective_scopes',
                        auth.validate_token_with_effective_scopes)
    token_info = mcp._lookup_token('synthetic')
    assert token_info['effective_scopes'] == set()
    with pytest.raises(PermissionError):
        mcp._require_scope(token_info, ['logs.read'])


def test_csv_formula_stays_quoted_after_alternate_delimiter_split():
    """Probe short cells reinterpreted with comma, semicolon or tab delimiters."""
    atoms = ['=', '+', '@', '-', '-1', '-1+1', ' ', '\t', ';', ',', 'a', '\n',
             '\r', '\x0b', '\u00a0', '\x00', '-.5', '1', '"']
    dangerous = re.compile(
        r'^[\s\x00-\x1f\x7f]*(?:[=+@]|-(?!(?:\d+(?:\.\d+)?|\.\d+)(?:$|[;,\x00-\x1f\x7f])))'
    )
    for length in (1, 2, 3, 4):
        for parts in itertools.product(atoms, repeat=length):
            raw = ''.join(parts)
            output = io.StringIO()
            csv.writer(output).writerow([sanitize_csv_cell(raw)])
            cell = next(csv.reader(io.StringIO(output.getvalue())))[0]
            for separator in (';', '\t'):
                for segment in cell.split(separator):
                    segment = segment.lstrip('\r\n ')
                    assert not dangerous.match(segment), (raw, cell, segment)
            assert not dangerous.match(cell) or cell.startswith("'"), (raw, cell)
