"""Tests for the SIGUSR2 config-reload handler in service/signals.py."""
import sys
from unittest.mock import MagicMock


def test_reload_config_runs_every_step_when_one_fails(monkeypatch):
    """One failing reload step must not skip the others or the retention rebuild."""
    fake_parsers = MagicMock()
    fake_parsers.reload_config_from_db.side_effect = RuntimeError('db down')
    monkeypatch.setitem(sys.modules, 'parsers', fake_parsers)
    for name in ('enrichment', 'routes.auth'):
        monkeypatch.setitem(sys.modules, name, MagicMock())
    monkeypatch.delitem(sys.modules, 'service.scheduler', raising=False)
    monkeypatch.delitem(sys.modules, 'service.signals', raising=False)
    from service import signals
    signals._retention_reload_requested.clear()

    unifi_api, pihole, enricher, adguard, receiver = (MagicMock() for _ in range(5))
    unifi_api.reload_config.side_effect = RuntimeError('boom')
    handler = signals.make_reload_config_handler(
        MagicMock(), receiver, unifi_api, pihole, enricher, adguard)

    handler(None, None)

    pihole.reload_config.assert_called_once()
    enricher.reload_config.assert_called_once()
    adguard.reload_config.assert_called_once()
    receiver._load_disabled_types.assert_called_once()
    assert signals._retention_reload_requested.is_set()
    signals._retention_reload_requested.clear()
