"""Requests carrying integration secrets must not follow HTTP redirects."""

from unittest.mock import patch
import threading

import requests
from requests.adapters import BaseAdapter

from pihole_api import PiHolePoller
from unifi.core import UniFiAPI


class RedirectAdapter(BaseAdapter):
    """Return a redirect without contacting any network endpoint."""

    def __init__(self):
        self.urls = []

    def send(self, request, **kwargs):
        """Record the URL and redirect to a synthetic second host."""
        self.urls.append(request.url)
        response = requests.Response()
        response.status_code = 307
        response.headers['Location'] = 'https://other.lan/capture'
        response.request = request
        response.url = request.url
        return response

    def close(self):
        """No resources are held by this fake adapter."""


def _redirect_session_factory(adapter):
    """Make real in-memory sessions with only a fake HTTP adapter."""
    original_session = requests.Session

    def make():
        session = original_session()
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    return make


def test_unifi_api_key_redirect_never_reaches_second_host():
    """A 307 must not forward X-API-KEY to a redirected destination."""
    adapter = RedirectAdapter()
    client = UniFiAPI.__new__(UniFiAPI)
    with patch('unifi.core.requests.Session', side_effect=_redirect_session_factory(adapter)):
        result = client.test_connection('https://controller.lan', api_key='fake-key')
    assert result['success'] is False
    assert adapter.urls == [
        'https://controller.lan/proxy/network/api/s/default/stat/sysinfo',
    ]


def test_pihole_password_redirect_never_reaches_second_host():
    """A 307 must not forward a Pi-hole password to another host."""
    adapter = RedirectAdapter()
    poller = PiHolePoller.__new__(PiHolePoller)
    poller.host = 'https://pihole.lan'
    poller._password = 'fake-password'
    poller.TIMEOUT = 10
    poller._config_lock = threading.RLock()
    with patch('pihole_api.requests.Session', side_effect=_redirect_session_factory(adapter)):
        result = poller.test_connection()
    assert result['success'] is False
    assert adapter.urls == ['https://pihole.lan/api/auth']


def test_self_hosted_login_redirect_never_carries_password_to_second_host():
    """A self hosted login 307 must stop before the synthetic target."""
    adapter = RedirectAdapter()
    client = UniFiAPI.__new__(UniFiAPI)
    with patch('unifi.core.requests.Session', side_effect=_redirect_session_factory(adapter)):
        result = client.test_connection(
            'https://controller.lan', controller_type='self_hosted',
            username='fake-user', password='fake-password')
    assert result['success'] is False
    assert adapter.urls == ['https://controller.lan/api/login']
