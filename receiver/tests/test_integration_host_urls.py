"""Regression tests for Pi-hole and AdGuard host URL handling."""

import sys
from unittest.mock import MagicMock, call

import pytest

from adguard_poller import _build_adguard_url
from pihole_api import _validate_pihole_url


def _clear_route_modules(monkeypatch):
    """Remove imported route modules so each test can inject lightweight deps."""
    for mod_name in list(sys.modules):
        if mod_name.startswith('routes.'):
            monkeypatch.delitem(sys.modules, mod_name, raising=False)


@pytest.fixture
def mocked_settings_deps(monkeypatch):
    """Install minimal route dependencies for DNS integration settings tests."""
    _clear_route_modules(monkeypatch)

    mock_db = MagicMock()
    mock_db.get_config = MagicMock(return_value='')
    mock_db.set_config = MagicMock()
    mock_db.encrypt_api_key = MagicMock(return_value='encrypted')
    monkeypatch.setitem(sys.modules, 'db', mock_db)

    mock_deps = MagicMock()
    mock_deps.enricher_db = MagicMock()
    mock_deps.pihole_poller = MagicMock()
    mock_deps.signal_receiver = MagicMock(return_value=True)
    mock_deps.get_conn = MagicMock()
    mock_deps.put_conn = MagicMock()
    monkeypatch.setitem(sys.modules, 'deps', mock_deps)

    return mock_db, mock_deps


@pytest.mark.parametrize(
    ('raw_url', 'expected'),
    [
        ('http://192.168.1.2', 'http://192.168.1.2'),
        ('https://pihole.lan:8443/', 'https://pihole.lan:8443'),
        ('pihole.home.arpa', 'http://pihole.home.arpa'),
        ('http://pi.hole/admin/', 'http://pi.hole'),
        ('http://[fd00::10]:8080', 'http://[fd00::10]:8080'),
    ],
)
def test_pihole_accepts_real_home_hosts(raw_url, expected):
    """Pi-hole validation should accept normal LAN hosts and UI URLs."""
    assert _validate_pihole_url(raw_url) == expected


@pytest.mark.parametrize(
    ('raw_host', 'api_path', 'expected'),
    [
        ('http://192.168.1.3', '/control/status', 'http://192.168.1.3/control/status'),
        ('https://adguard.lan:8443/', '/control/status', 'https://adguard.lan:8443/control/status'),
        ('adguard.home.arpa', '/control/querylog', 'http://adguard.home.arpa/control/querylog'),
        ('https://dns.example.net/adguard', '/control/status', 'https://dns.example.net/adguard/control/status'),
        ('http://[fd00::20]:8080/ui', '/control/status', 'http://[fd00::20]:8080/ui/control/status'),
    ],
)
def test_adguard_accepts_real_home_hosts(raw_host, api_path, expected):
    """AdGuard URL builder should accept LAN hosts and preserve reverse-proxy prefixes."""
    assert _build_adguard_url(raw_host, api_path) == expected


@pytest.mark.parametrize(
    'raw_url',
    [
        'ftp://192.168.1.2',
        'http://user:pass@192.168.1.2',
        'http://192.168.1.2/path;params',
        'http://192.168.1.2?token=secret',
        'http://192.168.1.2/#fragment',
        'http://192.168.1.2:99999',
    ],
)
def test_integration_hosts_reject_ambiguous_urls(raw_url):
    """Host inputs should remain plain HTTP(S) bases, not full request URLs."""
    with pytest.raises(ValueError):
        _validate_pihole_url(raw_url)
    with pytest.raises(ValueError):
        _build_adguard_url(raw_url, '/control/status')


def test_pihole_settings_persist_normalized_real_host(mocked_settings_deps):
    """Pi-hole settings persist the normalized host accepted by the poller."""
    mock_db, mock_deps = mocked_settings_deps

    from routes.pihole import update_pihole_settings

    assert update_pihole_settings({
        'enabled': True,
        'host': 'pihole.home.arpa',
        'poll_interval': 60,
        'enrichment': 'both',
    }) == {'success': True}

    mock_db.set_config.assert_has_calls([
        call(mock_deps.enricher_db, 'pihole_host', 'http://pihole.home.arpa'),
        call(mock_deps.enricher_db, 'pihole_last_cursor', 0),
    ], any_order=True)


def test_adguard_settings_persist_normalized_real_host(mocked_settings_deps):
    """AdGuard settings persist the normalized host used by API builders."""
    mock_db, mock_deps = mocked_settings_deps

    from routes.adguard import AdGuardConfig, put_adguard_config

    response = put_adguard_config(AdGuardConfig(
        enabled=True,
        host='https://dns.example.net/adguard/',
        username='admin',
        password='',
        poll_interval=30,
    ))

    assert response == {'ok': True, 'reload_signaled': True}
    mock_db.set_config.assert_any_call(
        mock_deps.enricher_db,
        'adguard_host',
        'https://dns.example.net/adguard',
    )
