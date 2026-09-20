"""Tests for the AbuseIPDB master kill-switch (abuseipdb_enabled).

Covers:
- AbuseIPDBEnricher: master toggle (env > DB > default true) gates enabled/lookup
- AbuseIPDBEnricher.reload_config() recomputes enabled at runtime
- BlacklistFetcher: fetch_and_store() skips (no network) when disabled
"""

from unittest.mock import MagicMock, patch

from enrichment import AbuseIPDBEnricher, resolve_abuseipdb_enabled
from blacklist import BlacklistFetcher


def _db_with_toggle(value):
    """Return a mock Database whose get_config('abuseipdb_enabled', ...) yields value."""
    db = MagicMock()

    def _get_config(key, default=None):
        """Return the supplied toggle value for the AbuseIPDB config key."""
        if key == 'abuseipdb_enabled':
            return value
        return default

    db.get_config.side_effect = _get_config
    return db


# ── Enricher master toggle ────────────────────────────────────────────────────

class TestAbuseIPDBEnricherToggle:
    """Verify AbuseIPDB enrichment honours the effective master toggle."""
    def test_master_toggle_defaults_to_true(self):
        """The master toggle defaults on when neither env nor DB supplies a value."""
        assert resolve_abuseipdb_enabled(None) is True

    @patch.dict('os.environ', {'ABUSEIPDB_ENABLED': 'false'})
    def test_master_toggle_env_off_overrides_db_on(self):
        """An explicit environment override wins over an enabled DB setting."""
        assert resolve_abuseipdb_enabled(_db_with_toggle(True)) is False

    @patch.dict('os.environ', {'ABUSEIPDB_ENABLED': 'true'})
    def test_master_toggle_env_on_overrides_db_off(self):
        """An explicit environment override wins over a disabled DB setting."""
        assert resolve_abuseipdb_enabled(_db_with_toggle(False)) is True

    def test_key_present_default_true_enabled(self):
        """No env, no db → master defaults to true; key present → enabled."""
        enricher = AbuseIPDBEnricher(api_key='k')
        assert enricher.enabled is True

    def test_db_toggle_off_disables_even_with_key(self):
        """A disabled persisted toggle prevents lookups despite credentials."""
        db = _db_with_toggle(False)
        enricher = AbuseIPDBEnricher(api_key='k', db=db)
        assert enricher.enabled is False
        assert enricher.lookup('1.2.3.4') == {}

    def test_db_toggle_on_with_key_enabled(self):
        """An enabled persisted toggle permits enrichment when a key exists."""
        db = _db_with_toggle(True)
        enricher = AbuseIPDBEnricher(api_key='k', db=db)
        assert enricher.enabled is True

    def test_no_key_never_enabled_even_if_toggle_on(self):
        """The master toggle cannot enable an integration without credentials."""
        db = _db_with_toggle(True)
        enricher = AbuseIPDBEnricher(api_key='', db=db)
        assert enricher.enabled is False

    @patch.dict('os.environ', {'ABUSEIPDB_ENABLED': 'false'})
    def test_env_off_overrides_db_on(self):
        """The enricher also applies an explicit environment disable first."""
        db = _db_with_toggle(True)
        enricher = AbuseIPDBEnricher(api_key='k', db=db)
        assert enricher.enabled is False

    @patch.dict('os.environ', {'ABUSEIPDB_ENABLED': 'true'})
    def test_env_on_overrides_db_off(self):
        """The enricher also applies an explicit environment enable first."""
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
        """A disabled enricher returns an empty result without a network call."""
        db = _db_with_toggle(False)
        enricher = AbuseIPDBEnricher(api_key='k', db=db)
        assert enricher.lookup('8.8.8.8') == {}
        mock_get.assert_not_called()


# ── Blacklist fetcher master toggle ───────────────────────────────────────────

class TestBlacklistFetcherToggle:
    """Verify blacklist preloading shares the AbuseIPDB master-toggle semantics."""
    @patch('blacklist.requests.get')
    def test_disabled_skips_without_network(self, mock_get):
        """A disabled DB toggle prevents the daily blacklist request."""
        db = _db_with_toggle(False)
        fetcher = BlacklistFetcher(db=db, api_key='k')
        assert fetcher.fetch_and_store() == 0
        mock_get.assert_not_called()

    @patch('blacklist.requests.get')
    def test_no_key_skips_without_network(self, mock_get):
        """Blacklist loading remains disabled without an API key."""
        db = _db_with_toggle(True)
        fetcher = BlacklistFetcher(db=db, api_key='')
        assert fetcher.fetch_and_store() == 0
        mock_get.assert_not_called()

    @patch.dict('os.environ', {'ABUSEIPDB_ENABLED': 'false'})
    @patch('blacklist.requests.get')
    def test_env_off_skips_without_network(self, mock_get):
        """An environment disable prevents the daily blacklist request."""
        db = _db_with_toggle(True)
        fetcher = BlacklistFetcher(db=db, api_key='k')
        assert fetcher.fetch_and_store() == 0
        mock_get.assert_not_called()
