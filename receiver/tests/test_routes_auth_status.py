"""Regression tests for GET /api/auth/status.

The endpoint fires on every SPA page load. It must derive `setup_complete`
straight from `system_config` and must NOT trigger the COUNT(*) over the
42 M-row `logs` table that `routes.setup.setup_status()` runs for its
(wizard-only) `logs_count` field.
"""

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def auth_module(monkeypatch):
    """Import routes.auth with deps/db mocked so no real DB pool is created."""
    for mod_name in list(sys.modules):
        if mod_name.startswith('routes'):
            monkeypatch.delitem(sys.modules, mod_name, raising=False)

    config_values = {'setup_complete': True, 'auth_session_ttl_hours': 168}

    mock_deps = MagicMock()
    mock_deps.enricher_db = MagicMock()
    mock_deps.get_conn = MagicMock()
    mock_deps.put_conn = MagicMock()
    monkeypatch.setitem(sys.modules, 'deps', mock_deps)

    mock_db = MagicMock()
    mock_db.get_config = MagicMock(side_effect=lambda db, key, default=None: config_values.get(key, default))
    monkeypatch.setitem(sys.modules, 'db', mock_db)

    import routes.auth as auth
    # Neutralise the collaborators that would otherwise need a live cursor;
    # this test is about which data sources auth_status touches, not their SQL.
    monkeypatch.setattr(auth, '_auth_enabled', lambda: False)
    monkeypatch.setattr(auth, '_has_users', lambda: True)
    monkeypatch.setattr(auth, '_has_admin', lambda: True)
    monkeypatch.setattr(auth, '_is_trusted_proxy', lambda request: False)
    monkeypatch.setattr(auth, 'get_forwarded_proto', lambda request: 'https')
    return auth, mock_db, config_values


def test_status_reads_setup_complete_from_config(auth_module):
    """setup_complete comes straight from system_config, honouring its value."""
    auth, mock_db, config_values = auth_module
    result = auth.auth_status(SimpleNamespace())
    assert result['setup_complete'] is True

    config_values['setup_complete'] = False
    assert auth.auth_status(SimpleNamespace())['setup_complete'] is False

    # It queried the config key rather than deriving from log volume.
    assert any(call.args[1] == 'setup_complete' for call in mock_db.get_config.call_args_list)


def test_status_does_not_count_logs(auth_module):
    """The hot bootstrap path must not run the 42 M-row COUNT(*) from setup_status."""
    auth, mock_db, _ = auth_module
    auth.auth_status(SimpleNamespace())
    mock_db.count_logs.assert_not_called()
