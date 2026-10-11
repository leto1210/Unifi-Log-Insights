"""Regression tests for malformed syslog packet isolation."""

import logging
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from parsers import parse_log
from service import syslog_receiver as receiver_module


@pytest.mark.parametrize(
    'line',
    [
        'Jan 99 12:00:00 gateway systemd[1]: invalid day',
        'Jan 01 99:00:00 gateway systemd[1]: invalid hour',
        'Feb 99999999999999999999 10:00:00 host kernel: overflow day',
    ],
)
def test_invalid_timestamp_is_rejected(line):
    """Malformed RFC3164 timestamps should be treated as unparseable input."""
    assert parse_log(line) is None


def test_parser_failure_does_not_prevent_next_packet(monkeypatch):
    """One parser exception must not prevent the following packet from being queued."""
    parsed = {'log_type': 'system', 'raw_log': 'valid'}
    parser = Mock(side_effect=[ValueError('invalid timestamp'), parsed])
    monkeypatch.setattr(receiver_module, 'parse_log', parser)

    db = Mock()
    db.get_config.side_effect = lambda _key, default=None: default
    enricher = Mock()
    enricher.enrich.side_effect = lambda entry: entry
    receiver = receiver_module.SyslogReceiver(db, enricher)

    receiver._handle_message(b'bad packet', ('192.0.2.1', 514))
    receiver._handle_message(b'valid packet', ('192.0.2.1', 514))

    assert receiver.stats['received'] == 2
    assert receiver.stats['failed'] == 1
    assert receiver.stats['parsed'] == 1
    assert receiver.batch == [parsed]
    enricher.enrich.assert_called_once_with(parsed)


def _receiver():
    """Build a receiver with a stub DB and a pass-through enricher."""
    db = Mock()
    db.get_config.side_effect = lambda _key, default=None: default
    enricher = Mock()
    enricher.enrich.side_effect = lambda entry: entry
    return receiver_module.SyslogReceiver(db, enricher)


def test_enrichment_failure_keeps_unenriched_row(monkeypatch):
    """An enrichment exception must store the parsed row un-enriched, not drop it."""
    parsed = {'log_type': 'firewall', 'raw_log': 'valid', 'src_ip': '203.0.113.5'}
    monkeypatch.setattr(receiver_module, 'parse_log', Mock(return_value=parsed))

    def _partial_enrich(entry):
        entry['country'] = 'XX'  # half-applied mutation must not leak into the stored row
        raise RuntimeError('temporary enrichment failure')

    receiver = _receiver()
    receiver.enricher.enrich.side_effect = _partial_enrich

    receiver._handle_message(b'valid packet', ('192.0.2.1', 514))

    assert receiver.stats['parsed'] == 1
    assert receiver.stats['failed'] == 0
    assert receiver.stats['enrich_exceptions'] == 1
    assert receiver.batch == [{'log_type': 'firewall', 'raw_log': 'valid', 'src_ip': '203.0.113.5'}]


def test_burst_of_parser_exceptions_logs_one_warning_per_interval(monkeypatch, caplog):
    """A flood of crashing packets yields one WARNING per minute, not one per packet."""
    import log_utils
    monkeypatch.setattr(receiver_module, 'parse_log', Mock(side_effect=RuntimeError('boom')))
    clock = [1000.0]
    monkeypatch.setattr(log_utils, 'time', SimpleNamespace(monotonic=lambda: clock[0]))
    receiver = _receiver()

    def _warnings():
        return [r for r in caplog.records if r.name == 'receiver' and r.levelno >= logging.WARNING]

    with caplog.at_level(logging.WARNING, logger='receiver'):
        for i in range(1000):
            clock[0] = 1000.0 + i * 0.05  # 1000 packets over 50 s
            receiver._handle_message(b'any payload', ('192.0.2.1', 514))
        assert receiver.stats['parse_exceptions'] == 1000
        assert len(_warnings()) == 1
        assert _warnings()[0].exc_info is not None

        clock[0] = 1000.0 + log_utils.WARN_INTERVAL_SECONDS + 1
        receiver._handle_message(b'any payload', ('192.0.2.1', 514))

    assert len(_warnings()) == 2
    assert '999 similar suppressed' in _warnings()[1].getMessage()
    assert 'total 1001' in _warnings()[1].getMessage()


def test_heartbeat_reports_counters_and_flushes_suppressed(monkeypatch, caplog):
    """The heartbeat shows exception counters and reports a burst's suppressed count once."""
    import log_utils
    monkeypatch.setattr(receiver_module, 'parse_log', Mock(side_effect=RuntimeError('boom')))
    clock = [2000.0]
    monkeypatch.setattr(log_utils, 'time', SimpleNamespace(monotonic=lambda: clock[0]))
    receiver = _receiver()

    with caplog.at_level(logging.DEBUG, logger='receiver'):
        for _ in range(5):
            receiver._handle_message(b'any payload', ('192.0.2.1', 514))
        clock[0] += log_utils.WARN_INTERVAL_SECONDS + 1
        receiver.last_heartbeat = 0
        receiver._maybe_log_heartbeat()
        receiver.last_heartbeat = 0
        receiver._maybe_log_heartbeat()  # nothing left to flush

    messages = [r.getMessage() for r in caplog.records]
    assert any('parse_exc=5' in m and 'failed=5' in m for m in messages if 'Heartbeat' in m)
    assert [m for m in messages if m.startswith('receiver.parse_exceptions:')] == \
        ['receiver.parse_exceptions: 4 similar suppressed since the previous warning']
