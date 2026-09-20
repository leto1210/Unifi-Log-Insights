"""Tests for AbuseIPDB settings toggle route and enrich gating.

Covers:
- GET /api/settings/abuseipdb reports enabled/configured/active
- PUT /api/settings/abuseipdb persists toggle, reloads, signals receiver
- POST /api/enrich/{ip}: 400 not-configured vs 409 disabled distinction
"""

import sys
from unittest.mock import MagicMock, patch

import pytest


def _clear_route_modules(monkeypatch):
    for mod_name in list(sys.modules):
        if mod_name.startswith('routes'):
            monkeypatch.delitem(sys.modules, mod_name, raising=False)


@pytest.fixture
def abuse_client(monkeypatch):
    """TestClient for routes/abuseipdb.py with deps/db/enrichment mocked."""
    _clear_route_modules(monkeypatch)

    # ── mock deps module ──
    mock_deps = MagicMock()
    mock_deps.enricher_db = MagicMock()
    mock_deps.signal_receiver = MagicMock()
    mock_deps.abuseipdb = MagicMock()
    mock_deps.abuseipdb.api_key = 'k'
    mock_deps.abuseipdb.enabled = True
    monkeypatch.setitem(sys.modules, 'deps', mock_deps)

    # ── mock db module ──
    config_store = {'abuseipdb_enabled': True}
    mock_db = MagicMock()
    mock_db.get_config.side_effect = (
        lambda db, key, default=None: config_store.get(key, default)
    )

    def _set_config(db, key, value):
        config_store[key] = value

    mock_db.set_config.side_effect = _set_config
    mock_db.get_wan_ips_from_config.return_value = []
    monkeypatch.setitem(sys.modules, 'db', mock_db)

    # ── mock enrichment module ──
    mock_enrich = MagicMock()
    mock_enrich.is_public_ip.return_value = True
    mock_enrich.get_abuseipdb_stats.return_value = None
    monkeypatch.setitem(sys.modules, 'enrichment', mock_enrich)

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from routes.abuseipdb import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app), mock_deps, config_store


class TestAbuseIPDBSettingsRoute:
    def test_get_reports_state(self, abuse_client):
        client, mock_deps, _ = abuse_client
        resp = client.get('/api/settings/abuseipdb')
        assert resp.status_code == 200
        body = resp.json()
        assert body == {'enabled': True, 'configured': True, 'active': True}

    def test_put_persists_and_signals(self, abuse_client):
        client, mock_deps, store = abuse_client
        resp = client.put('/api/settings/abuseipdb', json={'enabled': False})
        assert resp.status_code == 200
        assert store['abuseipdb_enabled'] is False
        mock_deps.abuseipdb.reload_config.assert_called_once()
        mock_deps.signal_receiver.assert_called_once()

    def test_put_missing_field_400(self, abuse_client):
        client, _, _ = abuse_client
        resp = client.put('/api/settings/abuseipdb', json={})
        assert resp.status_code == 400


class TestEnrichGating:
    def test_not_configured_returns_400(self, abuse_client):
        client, mock_deps, _ = abuse_client
        mock_deps.abuseipdb.api_key = ''
        mock_deps.abuseipdb.enabled = False
        resp = client.post('/api/enrich/8.8.8.8')
        assert resp.status_code == 400
        assert resp.json()['detail'] == 'AbuseIPDB not configured'

    def test_disabled_returns_409(self, abuse_client):
        client, mock_deps, _ = abuse_client
        mock_deps.abuseipdb.api_key = 'k'      # configured
        mock_deps.abuseipdb.enabled = False    # but toggled off
        resp = client.post('/api/enrich/8.8.8.8')
        assert resp.status_code == 409
        assert resp.json()['detail'] == 'integration disabled'
