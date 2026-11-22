"""The UDP receive thread must not block on rDNS, threat-cache misses or config reads.

enrich() runs inline in the single syslog receive loop: any DB round trip or
PTR query there stops the socket being drained and the kernel drops packets.
"""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest

import firewall_policy_matcher
from enrichment import AbuseIPDBEnricher, Enricher, RDNSEnricher
from service import syslog_receiver as receiver_module

REMOTE = '8.8.8.8'
FIREWALL_IN = {'log_type': 'firewall', 'direction': 'inbound',
               'src_ip': REMOTE, 'dst_ip': '192.168.1.5', 'rule_action': 'allow'}


@pytest.fixture
def enricher(monkeypatch):
    """Enricher with a real RDNSEnricher (no DB) and inert GeoIP/AbuseIPDB."""
    monkeypatch.setattr('enrichment.GeoIPEnricher', MagicMock)
    monkeypatch.setattr('enrichment.AbuseIPDBEnricher', MagicMock)
    e = Enricher(db=None)
    e.geoip.lookup = MagicMock(return_value={})
    e.rdns = RDNSEnricher(db=Mock())
    return e


def _wait_for(predicate, timeout=2.0):
    """Poll predicate until true or timeout; return its last value."""
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        time.sleep(0.01)
    return predicate()


class TestRdnsDeferred:
    def test_miss_is_submitted_not_resolved_inline(self, enricher):
        """A cold IP must not hit the DB cold tier or PTR on the receive thread."""
        enricher.rdns.submit = MagicMock()
        with patch('enrichment.socket.gethostbyaddr', side_effect=AssertionError('inline PTR')):
            parsed = enricher.enrich(dict(FIREWALL_IN))

        enricher.rdns.submit.assert_called_once_with(REMOTE)
        enricher.rdns._db.get_rdns_cache.assert_not_called()
        assert 'rdns' not in parsed
        assert parsed[Enricher.RDNS_PENDING_KEY] == REMOTE

    def test_hot_hit_is_applied_without_submit(self, enricher):
        """A fresh in-memory entry enriches the row immediately."""
        enricher.rdns.cache.set(REMOTE, {'rdns': 'dns.google', 'status': 'success',
                                         'expires_at': time.time() + 60})
        enricher.rdns.submit = MagicMock()

        parsed = enricher.enrich(dict(FIREWALL_IN))

        assert parsed['rdns'] == 'dns.google'
        assert Enricher.RDNS_PENDING_KEY not in parsed
        enricher.rdns.submit.assert_not_called()

    def test_background_resolver_populates_hot_tier(self):
        """submit() resolves on its own thread; the result lands in memory."""
        rdns = RDNSEnricher(db=None)
        with patch('enrichment.socket.gethostbyaddr', return_value=('dns.google', [], [])):
            rdns.submit(REMOTE)
            assert _wait_for(lambda: rdns.lookup_cached(REMOTE) is not None)
        assert rdns.lookup_cached(REMOTE) == {'rdns': 'dns.google'}
        assert _wait_for(lambda: not rdns._pending)

    def test_full_queue_drops_without_blocking(self):
        """Overflow is dropped (next packet retries) rather than blocking the caller."""
        rdns = RDNSEnricher(db=None)
        rdns._worker = object()  # pretend started, so nothing drains the queue
        for i in range(RDNSEnricher.RESOLVE_QUEUE_MAX + 5):
            rdns.submit(f'8.8.{i // 256}.{i % 256}')
        assert rdns._queue.qsize() == RDNSEnricher.RESOLVE_QUEUE_MAX
        assert len(rdns._pending) == RDNSEnricher.RESOLVE_QUEUE_MAX

    def test_fill_pending_rdns_late_binds_and_strips_marker(self, enricher):
        """Resolved-by-flush rows get rdns; the marker never reaches the INSERT."""
        enricher.rdns.cache.set(REMOTE, {'rdns': 'dns.google', 'status': 'success',
                                         'expires_at': time.time() + 60})
        resolved = {Enricher.RDNS_PENDING_KEY: REMOTE}
        unresolved = {Enricher.RDNS_PENDING_KEY: '1.1.1.1'}

        enricher.fill_pending_rdns([resolved, unresolved])

        assert resolved == {'rdns': 'dns.google'}
        assert unresolved == {}


def test_receiver_flush_late_binds_before_insert():
    """_flush_batch hands rows to fill_pending_rdns before inserting them."""
    db = Mock()
    db.get_config.side_effect = lambda _key, default=None: default
    enricher = Mock()
    order = []
    enricher.fill_pending_rdns.side_effect = lambda rows: order.append('fill')
    db.insert_logs_batch.side_effect = lambda rows: order.append('insert')
    receiver = receiver_module.SyslogReceiver(db, enricher)
    receiver.batch = [{'log_type': 'firewall'}]

    receiver._flush_batch()

    assert order == ['fill', 'insert']


def test_receiver_flush_survives_fill_failure():
    """A late-rDNS failure must not cost the batch."""
    db = Mock()
    db.get_config.side_effect = lambda _key, default=None: default
    enricher = Mock()
    enricher.fill_pending_rdns.side_effect = RuntimeError('boom')
    receiver = receiver_module.SyslogReceiver(db, enricher)
    receiver.batch = [{'log_type': 'firewall'}]

    receiver._flush_batch()

    db.insert_logs_batch.assert_called_once()
    assert receiver.stats['inserted'] == 1


class TestThreatMissCache:
    def test_repeated_miss_reads_db_once(self):
        """Packets from an unscored IP must not each repeat the ip_threats SELECT."""
        db = MagicMock()
        db.get_threat_cache.return_value = None
        a = AbuseIPDBEnricher(api_key='k', db=db)
        a.enabled = True

        assert a.lookup_cached(REMOTE) == {}
        assert a.lookup_cached(REMOTE) == {}
        assert db.get_threat_cache.call_count == 1

    def test_api_score_clears_miss(self):
        """Once the backfill scores the IP, the live path sees it immediately."""
        a = AbuseIPDBEnricher(api_key='k', db=None)
        a.enabled = True
        assert a.lookup_cached(REMOTE) == {}

        resp = MagicMock(status_code=200, headers={})
        resp.json.return_value = {'data': {'abuseConfidenceScore': 90}}
        with patch('enrichment.requests.get', return_value=resp):
            a.lookup(REMOTE)

        assert a.lookup_cached(REMOTE)['threat_score'] == 90


def test_vpn_networks_read_once_and_on_reload(monkeypatch):
    """zone_index rule resolution uses cached vpn_networks, refreshed by reload_config."""
    monkeypatch.setattr('enrichment.GeoIPEnricher', MagicMock)
    monkeypatch.setattr('enrichment.AbuseIPDBEnricher', MagicMock)
    config = {'vpn_networks': {'wg0': {'cidr': '10.8.0.0/24'}}}
    db = MagicMock()
    db.get_config.side_effect = lambda key, default=None: config.get(key, default)
    monkeypatch.setattr(firewall_policy_matcher, 'parse_firewall_rule',
                        lambda *_a, **_k: {'format': 'zone_index'})
    resolve = MagicMock(return_value='allow')
    monkeypatch.setattr(firewall_policy_matcher, 'resolve_rule_action', resolve)
    unifi = MagicMock(enabled=True)
    unifi.resolve_name.return_value = None
    e = Enricher(db=db, unifi=unifi)
    e._rdns_enabled = False
    db.get_config.reset_mock()

    e.enrich(dict(FIREWALL_IN))
    e.enrich(dict(FIREWALL_IN))

    assert all(c.args[0] != 'vpn_networks' for c in db.get_config.call_args_list)
    assert resolve.call_args.kwargs['vpn_networks'] == {'wg0': {'cidr': '10.8.0.0/24'}}

    config['vpn_networks'] = {}
    e.reload_config()
    e.enrich(dict(FIREWALL_IN))
    assert resolve.call_args.kwargs['vpn_networks'] == {}
