"""Tests for runtime network identity gating in main.py.

Covers:
- _use_log_identity_detection()
- _refresh_network_identity_from_logs()

main.py imports routes.auth which triggers deps.py's PostgreSQL init.
We stub all heavy transitive dependencies before importing the functions
under test.
"""

import sys
from unittest.mock import MagicMock, patch

# Stub heavy transitive dependencies of main.py before import.
# Order matters: deps must be stubbed before routes.auth.
_stubs = (
    'schedule', 'parsers', 'db', 'enrichment', 'backfill', 'blacklist',
    'unifi_api', 'pihole_api', 'adguard_poller',
    'deps', 'routes', 'routes.auth',
)
_originals = {}
for _mod in _stubs:
    if _mod in sys.modules:
        _originals[_mod] = sys.modules[_mod]
    else:
        sys.modules[_mod] = MagicMock()

# Now safe to import the functions under test
from main import _use_log_identity_detection, _refresh_network_identity_from_logs, _log_periodic_stats

# Restore original module state so stubs don't leak to other test files
for _mod, _orig in _originals.items():
    sys.modules[_mod] = _orig
for _mod in _stubs:
    if _mod not in _originals:
        sys.modules.pop(_mod, None)


class TestUseLogIdentityDetection:

    def test_returns_true_when_unifi_disabled(self):
        db = MagicMock()
        db.get_config.return_value = False
        assert _use_log_identity_detection(db) is True

    def test_returns_false_when_unifi_enabled(self):
        db = MagicMock()
        db.get_config.return_value = True
        assert _use_log_identity_detection(db) is False

    def test_returns_true_when_config_missing(self):
        db = MagicMock()
        db.get_config.return_value = None
        assert _use_log_identity_detection(db) is True


class TestRefreshNetworkIdentityFromLogs:

    def test_noop_when_unifi_enabled(self):
        db = MagicMock()
        db.get_config.return_value = True
        _refresh_network_identity_from_logs(db)
        db.detect_wan_ip.assert_not_called()
        db.detect_gateway_ips.assert_not_called()

    def test_calls_detection_when_unifi_disabled(self):
        db = MagicMock()
        db.get_config.return_value = False
        _refresh_network_identity_from_logs(db)
        db.detect_wan_ip.assert_called_once()
        db.detect_gateway_ips.assert_called_once()

    def test_gateway_still_runs_when_wan_detection_fails(self):
        db = MagicMock()
        db.get_config.return_value = False
        db.detect_wan_ip.side_effect = Exception("WAN failed")
        _refresh_network_identity_from_logs(db)
        db.detect_gateway_ips.assert_called_once()


class TestIdentityReloadAfterRefresh:
    """A changed persisted identity is reloaded into the running parsers."""

    def _run(self, db):
        mod = sys.modules['service.network_identity']
        with patch.object(mod, 'parsers') as fake_parsers:
            _refresh_network_identity_from_logs(db)
        return fake_parsers.reload_config_from_db

    def setup_method(self):
        sys.modules['service.network_identity']._loaded_identity = None

    def test_reloads_once_per_identity_change(self):
        config = {'unifi_enabled': False, 'wan_ip': '1.1.1.1'}
        db = MagicMock()
        db.get_config.side_effect = lambda key, default=None: config.get(key, default)

        assert self._run(db).call_count == 1   # first refresh loads
        assert self._run(db).call_count == 0   # unchanged: no reload
        config['wan_ip'] = '2.2.2.2'
        assert self._run(db).call_count == 1   # changed: reload

    def test_failed_reload_retries_next_run(self):
        db = MagicMock()
        db.get_config.side_effect = lambda key, default=None: False if key == 'unifi_enabled' else None
        mod = sys.modules['service.network_identity']
        with patch.object(mod, 'parsers') as fake_parsers:
            fake_parsers.reload_config_from_db.side_effect = Exception("db down")
            _refresh_network_identity_from_logs(db)  # must not raise
        assert self._run(db).call_count == 1


class TestPeriodicStatsLogging:

    def test_skips_db_queries_when_not_debug(self):
        db = MagicMock()
        enricher = MagicMock()

        with patch('main.logger.isEnabledFor', return_value=False):
            _log_periodic_stats(db, enricher)

        db.get_stats.assert_not_called()
        enricher.get_stats.assert_not_called()

    def test_collects_stats_when_debug_enabled(self):
        db = MagicMock()
        enricher = MagicMock()
        db.get_stats.return_value = {'total': 1, 'last_hour': 1}
        enricher.get_stats.return_value = {'ok': True}

        with patch('main.logger.isEnabledFor', return_value=True):
            _log_periodic_stats(db, enricher)

        db.get_stats.assert_called_once_with()
        enricher.get_stats.assert_called_once_with()
