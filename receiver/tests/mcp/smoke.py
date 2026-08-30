#!/usr/bin/env python3
"""MCP smoke suite for a running unifi-log-insight deployment.

Hits every tool the MCP server exposes via JSON-RPC 2.0 over HTTP, checks
that responses are well-formed, and prints a per-tool pass/fail report.

Usage:
    export MCP_URL="http://core-syno:8099/api/mcp"     # or duncan, or localhost
    export MCP_TOKEN="<bearer-token-from-Settings-MCP>"
    python3 receiver/tests/mcp/smoke.py
    python3 receiver/tests/mcp/smoke.py --json         # machine-readable

Exit codes:
    0 — every tool green
    1 — at least one tool failed or the endpoint is unreachable

Design notes:
    - Uses only the stdlib (urllib.request, json, argparse) so it can be
      dropped on any Linux/macOS host without a venv.
    - Each tool is one CHECK entry: (name, args, validator). The validator
      is a function that receives the JSON-RPC result and returns None on
      success or a str describing the failure. Add a tool by appending a
      row.
    - Every check is best-effort in isolation: a permission-scoped tool
      returning an auth error still records the raw response so the
      operator can see whether the token needs a scope bump.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Callable

# ── JSON-RPC transport ─────────────────────────────────────────────────

_rpc_id = 0

def _next_id() -> int:
    global _rpc_id
    _rpc_id += 1
    return _rpc_id


def rpc(url: str, token: str, method: str, params: dict | None = None,
        timeout: float = 30.0) -> dict:
    """Send one JSON-RPC 2.0 request. Returns the parsed response dict.

    Raises on transport errors (unreachable host, non-2xx HTTP, malformed
    JSON). JSON-RPC-level errors (result.error, missing result) are
    surfaced to the caller by returning the parsed body — they aren't
    exceptional at the transport layer.
    """
    payload = {
        "jsonrpc": "2.0",
        "id": _next_id(),
        "method": method,
        "params": params or {},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'MCP-Protocol-Version': '2025-06-18',
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def call_tool(url: str, token: str, name: str, args: dict | None = None) -> dict:
    """Call an MCP tool via tools/call. Returns the raw JSON-RPC response."""
    return rpc(url, token, 'tools/call', {'name': name, 'arguments': args or {}})


# ── Validators ─────────────────────────────────────────────────────────

def _extract_result(response: dict) -> tuple[Any, str | None]:
    """Return (result_dict_or_None, error_str_or_None) from a JSON-RPC response."""
    if 'error' in response:
        err = response['error']
        return None, f"JSON-RPC error {err.get('code')}: {err.get('message')}"
    if 'result' not in response:
        return None, "missing 'result' in response"
    return response['result'], None


def v_ok(response: dict) -> str | None:
    """Pass if the response has a non-error result."""
    _, err = _extract_result(response)
    return err


def v_content_nonempty(response: dict) -> str | None:
    """Pass if result.content is a non-empty list (MCP text-content shape)."""
    result, err = _extract_result(response)
    if err:
        return err
    content = result.get('content')
    if not isinstance(content, list) or not content:
        return f"expected non-empty content list, got: {type(content).__name__}"
    return None


def v_health_ok(response: dict) -> str | None:
    """get_health: body must contain status=ok and a version string."""
    err = v_content_nonempty(response)
    if err:
        return err
    body = _tool_body(response)
    if not isinstance(body, dict):
        return f"health body not a dict: {type(body).__name__}"
    if body.get('status') != 'ok':
        return f"status != 'ok' (got {body.get('status')!r})"
    if not body.get('version'):
        return "missing 'version'"
    return None


def _tool_body(response: dict) -> Any:
    """Extract the parsed JSON payload from a tools/call response.

    MCP servers wrap tool output in result.content[0].text (JSON-serialized
    string). Return the parsed structure, or the raw text on parse failure.
    """
    result = response.get('result', {})
    content = result.get('content', [])
    if not content:
        return None
    text = content[0].get('text', '')
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return text


# ── Check catalog ──────────────────────────────────────────────────────
# Each row: (tool_name, args_dict, validator, human_description)
# validator: Callable[[dict], Optional[str]] — returns None on pass, str on fail

CHECKS = [
    # Read-only, cheap
    ('get_health',              {},                       v_health_ok,          'app+DB health'),
    ('get_log_stats',           {'time_range': '24h'},    v_content_nonempty,   'DB stats snapshot'),
    ('list_interfaces',         {},                       v_content_nonempty,   'discovered network interfaces'),
    ('list_services',           {},                       v_content_nonempty,   'known service labels'),
    ('list_protocols',          {},                       v_content_nonempty,   'known protocols'),

    # UniFi-integration tools — need UniFi API credentials configured
    ('get_unifi_status',        {},                       v_ok,                 'UniFi poller status (may be "disabled")'),
    ('list_unifi_devices',      {},                       v_content_nonempty,   'UniFi devices'),
    ('list_unifi_clients',      {},                       v_content_nonempty,   'UniFi clients'),
    ('list_firewall_policies',  {},                       v_content_nonempty,   'zone-based firewall policies'),

    # Log-query tools — depend on ingested data volume
    ('search_logs',             {'limit': 5},             v_content_nonempty,   'recent logs sample'),
    ('aggregate_logs',          {'group_by': 'src_ip',
                                 'time_range': '1h',
                                 'limit': 5},             v_content_nonempty,   'top src_ip aggregation'),
    ('get_top_threat_ips',      {'limit': 5},             v_content_nonempty,   'threat scoring digest'),
    ('list_threat_ips',         {'limit': 5},             v_content_nonempty,   'threat IPs paginated'),
    ('export_logs_csv_url',     {'time_range': '1h'},     v_content_nonempty,   'CSV export URL builder'),
]

# get_log takes an id; search_logs feeds it. Not in the static catalog —
# handled specially in run() below.


# ── Runner ─────────────────────────────────────────────────────────────

def run(url: str, token: str, verbose: bool = True) -> tuple[int, int, list[dict]]:
    """Execute the check catalog. Returns (passed, total, report_rows)."""
    rows: list[dict] = []
    passed = 0
    for name, args, validator, desc in CHECKS:
        started = time.monotonic()
        row: dict[str, Any] = {'tool': name, 'desc': desc, 'args': args}
        try:
            resp = call_tool(url, token, name, args)
            err = validator(resp)
            row['elapsed_ms'] = round((time.monotonic() - started) * 1000, 1)
            if err is None:
                row['status'] = 'PASS'
                passed += 1
            else:
                row['status'] = 'FAIL'
                row['error'] = err
                row['raw_response'] = resp
        except urllib.error.HTTPError as e:
            row.update(status='FAIL', error=f'HTTP {e.code}: {e.reason}',
                       elapsed_ms=round((time.monotonic() - started) * 1000, 1))
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            row.update(status='FAIL', error=f'transport: {e}',
                       elapsed_ms=round((time.monotonic() - started) * 1000, 1))
        except (json.JSONDecodeError, ValueError) as e:
            row.update(status='FAIL', error=f'malformed response: {e}',
                       elapsed_ms=round((time.monotonic() - started) * 1000, 1))
        rows.append(row)

        if verbose:
            symbol = '✓' if row['status'] == 'PASS' else '✗'
            line = f"  {symbol} {name:26s} {row['elapsed_ms']:>6.1f} ms  — {desc}"
            if row['status'] == 'FAIL':
                line += f"\n      ↳ {row['error']}"
            print(line)

    # Chained check: search_logs → get_log with the first id we saw.
    if verbose:
        print()
        print("  Chained check: search_logs → get_log")
    try:
        first = call_tool(url, token, 'search_logs', {'limit': 1})
        body = _tool_body(first)
        # body shape: {"logs": [{"id": N, ...}], "total": ...} — adapt if
        # your app returns a different envelope.
        log_id = None
        if isinstance(body, dict):
            logs = body.get('logs') or body.get('rows') or []
            if logs:
                log_id = logs[0].get('id')
        if log_id is None:
            row = {'tool': 'get_log', 'desc': 'fetch by id from search_logs',
                   'args': {}, 'status': 'SKIP',
                   'error': 'no rows returned by search_logs — DB may be empty'}
        else:
            resp = call_tool(url, token, 'get_log', {'id': log_id})
            err = v_content_nonempty(resp)
            row = {'tool': 'get_log', 'desc': f'fetch log id={log_id}',
                   'args': {'id': log_id},
                   'status': 'PASS' if err is None else 'FAIL',
                   'error': err}
            if err is None:
                passed += 1
        rows.append(row)
        if verbose:
            print(f"    {row['status']:4s} get_log id={row['args'].get('id','-')}")
    except Exception as e:  # noqa: BLE001 — smoke, want any error surfaced
        row = {'tool': 'get_log', 'status': 'FAIL', 'error': str(e)}
        rows.append(row)
        if verbose:
            print(f"    FAIL get_log — {e}")

    total = len(CHECKS) + 1
    return passed, total, rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--url', default=os.environ.get('MCP_URL'),
                        help='MCP endpoint URL (env: MCP_URL)')
    parser.add_argument('--token', default=os.environ.get('MCP_TOKEN'),
                        help='Bearer token (env: MCP_TOKEN)')
    parser.add_argument('--json', action='store_true',
                        help='Emit machine-readable JSON report only')
    args = parser.parse_args()

    if not args.url or not args.token:
        print("error: --url / MCP_URL and --token / MCP_TOKEN are required",
              file=sys.stderr)
        return 2

    if not args.json:
        print(f"MCP smoke — endpoint: {args.url}")
        print(f"─" * 76)

    passed, total, rows = run(args.url, args.token, verbose=not args.json)

    if args.json:
        json.dump({'passed': passed, 'total': total, 'rows': rows},
                  sys.stdout, indent=2, default=str)
        sys.stdout.write('\n')
    else:
        print(f"─" * 76)
        print(f"Result: {passed}/{total} passed")

    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
