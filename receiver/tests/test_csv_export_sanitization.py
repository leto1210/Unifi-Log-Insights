"""Exercise CSV formula protection through both export endpoints with fake rows."""

import asyncio
import csv
import io
import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def export_routes(monkeypatch):
    """Import real export handlers with their application globals isolated."""
    monkeypatch.delitem(sys.modules, 'routes.logs', raising=False)
    monkeypatch.delitem(sys.modules, 'routes.stats', raising=False)
    fake_deps = MagicMock()
    fake_deps.ttl_cache = lambda *_args, **_kwargs: lambda func: func
    monkeypatch.setitem(sys.modules, 'deps', fake_deps)
    from routes import logs, stats
    yield logs, stats
    monkeypatch.delitem(sys.modules, 'routes.logs', raising=False)
    monkeypatch.delitem(sys.modules, 'routes.stats', raising=False)


class FakeCursor:
    """Return controlled rows to the export handlers without a database."""

    description = [('source_ip',), ('destination_ip',), ('port',),
                   ('protocol',), ('service',), ('allow_count',), ('block_count',)]

    def __init__(self, rows):
        """Keep the rows used by fetchall and iteration."""
        self.rows = rows

    def __enter__(self):
        """Support the route's cursor context manager."""
        return self

    def __exit__(self, *_args):
        """Leave cleanup to the fake connection."""
        return False

    def execute(self, *_args):
        """Accept the query built by the real route."""

    def fetchall(self):
        """Return all rows for the logs export."""
        return self.rows

    def __iter__(self):
        """Stream rows for the stats export."""
        return iter(self.rows)


class FakeConnection:
    """Record transaction completion while avoiding external services."""

    def __init__(self, rows):
        """Store fake CSV data and transaction state."""
        self.rows = rows
        self.committed = False

    def cursor(self):
        """Open a controlled cursor."""
        return FakeCursor(self.rows)

    def commit(self):
        """Record successful export completion."""
        self.committed = True

    def rollback(self):
        """Fail the test if the route unexpectedly rolls back."""
        raise AssertionError('unexpected rollback')


async def _csv_text(response):
    """Consume the same response a CSV importer downloads."""
    chunks = [chunk async for chunk in response.body_iterator]
    return ''.join(chunks)


def _assert_alt_delimiters_safe(csv_text):
    """Alternate semicolon and tab importers cannot expose a formula cell."""
    for delimiter in (';', '\t'):
        cells = [cell for row in csv.reader(io.StringIO(csv_text), delimiter=delimiter)
                 for cell in row]
        assert not any(cell.lstrip().startswith(('=', '+', '@', '-1+')) for cell in cells)


def test_logs_export_quotes_formula_but_preserves_negative_number(monkeypatch, export_routes):
    """Exported log text cannot become a spreadsheet formula."""
    logs, _stats = export_routes
    row = [None] * 32  # 30 DB columns, followed by two device names.
    row[8] = '-1+1'    # service_name
    row[10] = '-5'     # rule_desc
    row[16] = 'label;=1+1'  # dns_query
    row[17] = 'label\t=1+1'  # dns_type
    row[18] = 'label\n=1+1'  # dns_answer
    conn = FakeConnection([row])
    monkeypatch.setattr(logs, 'get_conn', lambda: conn)
    monkeypatch.setattr(logs, 'put_conn', lambda _conn: None)
    monkeypatch.setattr(logs, 'get_config', lambda *_args: 'off')
    monkeypatch.setattr(logs, 'load_identity_config', lambda _db: {})
    monkeypatch.setattr(logs, 'annotate_ip', lambda *_args: (None, None, None))

    filters = dict.fromkeys([
        'log_type', 'time_from', 'time_to', 'src_ip', 'dst_ip', 'ip',
        'direction', 'rule_action', 'rule_name', 'country', 'threat_min',
        'search', 'service', 'interface', 'asn', 'dst_port', 'src_port',
        'protocol',
    ])
    response = logs.export_csv_endpoint(time_range='24h', vpn_only=False, limit=1, **filters)
    csv_text = asyncio.run(_csv_text(response))
    header, exported = csv.reader(io.StringIO(csv_text))

    assert exported[header.index('service_name')] == "'-1+1"
    assert exported[header.index('rule_desc')] == '-5'
    assert exported[header.index('dns_query')] == "label;'=1+1"
    assert exported[header.index('dns_type')] == "'label\t'=1+1"
    assert exported[header.index('dns_answer')] == "'label\n'=1+1"
    _assert_alt_delimiters_safe(csv_text)
    assert conn.committed


def test_ip_pairs_export_quotes_formula_but_preserves_negative_number(monkeypatch, export_routes):
    """Streamed IP-pair CSV applies the same cell protection."""
    _logs, stats = export_routes
    conn = FakeConnection([('192.0.2.1', '198.51.100.2', 443,
                            'tcp', 'label;=1+1', -5, 0)])
    monkeypatch.setattr(stats, 'get_conn', lambda: conn)
    monkeypatch.setattr(stats, 'put_conn', lambda _conn: None)

    filters = dict.fromkeys([
        'time_from', 'time_to', 'rule_action', 'direction', 'interface',
        'service', 'src_ip', 'dst_ip', 'dst_port', 'protocol',
        'interface_in', 'interface_out',
    ])
    response = stats.get_ip_pairs_csv(time_range='24h', log_type='firewall', **filters)
    csv_text = asyncio.run(_csv_text(response))
    header, exported = csv.reader(io.StringIO(csv_text))

    assert exported[header.index('service')] == "label;'=1+1"
    assert exported[header.index('allow_count')] == '-5'
    _assert_alt_delimiters_safe(csv_text)
    assert conn.committed
