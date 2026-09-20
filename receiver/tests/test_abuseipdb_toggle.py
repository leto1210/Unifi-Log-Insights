"""Tests for the AbuseIPDB master kill-switch (abuseipdb_enabled).

Covers:
- AbuseIPDBEnricher: master toggle (env > DB > default true) gates enabled/lookup
- AbuseIPDBEnricher.reload_config() recomputes enabled at runtime
- BlacklistFetcher: fetch_and_store() skips (no network) when disabled
"""

from unittest.mock import MagicMock, patch

from enrichment import AbuseIPDBEnricher
from blacklist import BlacklistFetcher


def _db_with_toggle(value):
    """Return a mock Database whose get_config('abuseipdb_enabled', ...) yields value."""
    db = MagicMock()

    def _get_config(key, default=None):
        if key == 'abuseipdb_enabled':
            return value
        return default

    db.get_config.side_effect = _get_config
    return db


# ── Enricher master toggle ────────────────────────────────────────────────────

class TestAbuseIPDBEnricherToggle:
    def test_key_present_default_true_enabled(self):
        """No env, no db → master defaults to true; key present → enabled."""
        enricher = AbuseIPDBEnricher(api_key='k')
        assert enricher.enabled is True

    def test_db_toggle_off_disables_even_with_key(self):
        db = _db_with_toggle(False)
        enricher = AbuseIPDBEnricher(api_key='k', db=db)
        assert enricher.enabled is False
        assert enricher.lookup('1.2.3.4') == {}

    def test_db_toggle_on_with_key_enabled(self):
        db = _db_with_toggle(True)
        enricher = AbuseIPDBEnricher(api_key='k', db=db)
        assert enricher.enabled is True

    def test_no_key_never_enabled_even_if_toggle_on(self):
        db = _db_with_toggle(True)
        enricher = AbuseIPDBEnricher(api_key='', db=db)
        assert enricher.enabled is False

    @patch.dict('os.environ', {'ABUSEIPDB_ENABLED': 'false'})
    def test_env_off_overrides_db_on(self):
        db = _db_with_toggle(True)
        enricher = AbuseIPDBEnricher(api_key='k', db=db)
        assert enricher.enabled is False

    @patch.dict('os.environ', {'ABUSEIPDB_ENABLED': 'true'})
    def test_env_on_overrides_db_off(self):
        db = _db_with_toggle(False)
        enricher = AbuseIPDBEnricher(api_key='k', db=db)
        assert enricher.enabled is True

    def test_reload_config_recomputes_enabled(self):
        """A DB toggle flip is picked up by reload_config() without a restart."""
        db = MagicMock()
        state = {'v': True}
        db.get_config.side_effect = (
            lambda key, default=None: state['v'] if key == 'abuseipdb_enabled' else default
        )
        enricher = AbuseIPDBEnricher(api_key='k', db=db)
        assert enricher.enabled is True

        state['v'] = False
        assert enricher.reload_config() is False
        assert enricher.enabled is False
        assert enricher.lookup('1.2.3.4') == {}

        state['v'] = True
        assert enricher.reload_config() is True
        assert enricher.enabled is True

    @patch('enrichment.requests.get')
    def test_disabled_lookup_makes_no_http_call(self, mock_get):
        db = _db_with_toggle(False)
        enricher = AbuseIPDBEnricher(api_key='k', db=db)
        assert enricher.lookup('8.8.8.8') == {}
        mock_get.assert_not_called()


# ── Blacklist fetcher master toggle ───────────────────────────────────────────

class TestBlacklistFetcherToggle:
    @patch('blacklist.requests.get')
    def test_disabled_skips_without_network(self, mock_get):
        db = _db_with_toggle(False)
        fetcher = BlacklistFetcher(db=db, api_key='k')
        assert fetcher.fetch_and_store() == 0
        mock_get.assert_not_called()

    @patch('blacklist.requests.get')
    def test_no_key_skips_without_network(self, mock_get):
        db = _db_with_toggle(True)
        fetcher = BlacklistFetcher(db=db, api_key='')
        assert fetcher.fetch_and_store() == 0
        mock_get.assert_not_called()

    @patch.dict('os.environ', {'ABUSEIPDB_ENABLED': 'false'})
    @patch('blacklist.requests.get')
    def test_env_off_skips_without_network(self, mock_get):
        db = _db_with_toggle(True)
        fetcher = BlacklistFetcher(db=db, api_key='k')
        assert fetcher.fetch_and_store() == 0
        mock_get.assert_not_called()
