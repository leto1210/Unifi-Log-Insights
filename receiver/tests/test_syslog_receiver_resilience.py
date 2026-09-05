"""Regression tests for malformed syslog packet isolation."""

from unittest.mock import Mock

import pytest

from parsers import parse_log
from service import syslog_receiver as receiver_module


@pytest.mark.parametrize(
    'line',
    [
        'Jan 99 12:00:00 gateway systemd[1]: invalid day',
        'Jan 01 99:00:00 gateway systemd[1]: invalid hour',
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


def test_enrichment_failure_isolated_to_current_packet(monkeypatch):
    """An enrichment exception should reject only the packet being processed."""
    parsed = {'log_type': 'system', 'raw_log': 'valid'}
    monkeypatch.setattr(receiver_module, 'parse_log', Mock(return_value=parsed))

    db = Mock()
    db.get_config.side_effect = lambda _key, default=None: default
    enricher = Mock()
    enricher.enrich.side_effect = RuntimeError('temporary enrichment failure')
    receiver = receiver_module.SyslogReceiver(db, enricher)

    receiver._handle_message(b'valid packet', ('192.0.2.1', 514))

    assert receiver.stats['received'] == 1
    assert receiver.stats['parsed'] == 1
    assert receiver.stats['failed'] == 1
    assert receiver.batch == []
