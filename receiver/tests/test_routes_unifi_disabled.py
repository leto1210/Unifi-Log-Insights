"""Tests for UniFi outbound-endpoint gating (kill-switch vs not-configured).

_require_unifi_enabled() must return 409 'integration disabled' when creds are
present but the master toggle is off, and 400 'UniFi API not configured' when
the integration was never set up.
"""

import sys
from unittest.mock import MagicMock

import pytest


def _clear_route_modules(monkeypatch):
    for mod_name in list(sys.modules):
        if mod_name.startswith('routes'):
            monkeypatch.delitem(sys.modules, mod_name, raising=False)


@pytest.fixture
def unifi_client(monkeypatch):
    """TestClient for routes/unifi.py with deps/db/unifi_api mocked."""
    _clear_route_modules(monkeypatch)

    mock_deps = MagicMock()
    mock_deps.enricher_db = MagicMock()
    mock_deps.unifi_api = MagicMock()
    mock_deps.signal_receiver = MagicMock()
    mock_deps.get_conn = MagicMock()
    mock_deps.put_conn = MagicMock()
    monkeypatch.setitem(sys.modules, 'deps', mock_deps)

    config_store = {}
    mock_db = MagicMock()
    mock_db.get_config.side_effect = (
        lambda db, key, default=None: config_store.get(key, default)
    )
    monkeypatch.setitem(sys.modules, 'db', mock_db)

    # firewall_policy_matcher is imported by routes.unifi
    mock_fw = MagicMock()
    monkeypatch.setitem(sys.modules, 'firewall_policy_matcher', mock_fw)

    mock_uapi = MagicMock()

    class _PermErr(Exception):
        pass

    mock_uapi.UniFiPermissionError = _PermErr
    from unifi_api import UniFiAPI as _RealUniFiAPI
    mock_uapi.UniFiAPI = _RealUniFiAPI
    monkeypatch.setitem(sys.modules, 'unifi_api', mock_uapi)

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from routes.unifi import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app), mock_deps, config_store


class TestUniFiDisabledGating:
    def test_disabled_with_host_returns_409(self, unifi_client):
        client, mock_deps, store = unifi_client
        mock_deps.unifi_api.enabled = False
        mock_deps.unifi_api.host = 'https://192.168.2.1'
        store['unifi_enabled'] = False
        resp = client.get('/api/setup/unifi-network-config')
        assert resp.status_code == 409
        assert resp.json()['detail'] == 'integration disabled'

    def test_not_configured_returns_400(self, unifi_client):
        client, mock_deps, store = unifi_client
        mock_deps.unifi_api.enabled = False
        mock_deps.unifi_api.host = ''
        store['unifi_enabled'] = False
        resp = client.get('/api/setup/unifi-network-config')
        assert resp.status_code == 400
        assert resp.json()['detail'] == 'UniFi API not configured'
