# MCP Server

UniFi Log Insight ships a [Model Context Protocol](https://modelcontextprotocol.io) server so LLM-based clients (Claude Desktop, Claude Code, Gemini CLI, Cursor, or any HTTP MCP client) can query your network data through natural conversation instead of the UI or the raw REST API.

## Enable

1. In the app: **Settings > MCP > Enable MCP server**
2. Create a bearer token: **Settings > MCP > Tokens > New**
   - Pick the scopes you need (see below). Read scopes only for LLMs you're not fully trusting.
   - Copy the token immediately — it's shown once.
3. Endpoint: `http://<host>:8090/api/mcp` (JSON-RPC 2.0 over HTTP POST)

Requires `AUTH_ENABLED=true` in the container env.

## Tools exposed

| Tool | Scope | What it does |
| --- | --- | --- |
| `get_health` | read | App + DB health snapshot (version, log count, storage) |
| `get_log_stats` | read | Aggregated stats over a time range (`24h`, `7d`, …) |
| `search_logs` | read | Query logs with filters (ip, service, time, action) |
| `get_log` | read | Fetch a single log entry by id |
| `aggregate_logs` | read | Group-by (src_ip, dst_ip, service, country, …) with counts |
| `get_top_threat_ips` | read | Top-N threat-scored IPs |
| `list_threat_ips` | read | Paginated threat IP list |
| `export_logs_csv_url` | read | Returns a URL to download filtered logs as CSV |
| `list_services` | read | Known service labels |
| `list_protocols` | read | Known protocols |
| `list_interfaces` | read | Configured WAN/VLAN/VPN interfaces |
| `list_unifi_devices` | read | UniFi devices discovered via the API |
| `list_unifi_clients` | read | UniFi clients (may be large — filter client-side) |
| `list_firewall_policies` | read | Zone-based firewall policies |
| `get_unifi_status` | read | UniFi poller status (connected, last poll, counts) |
| `set_firewall_syslog` | **write** | Toggle `loggingEnabled` on one firewall policy |

Read-only tools require the `read` scope. `set_firewall_syslog` requires `write` — only grant to clients you trust to mutate UniFi state.

## Configure Claude Code

`~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "unifi-log-insight": {
      "type": "http",
      "url": "http://<host>:8090/api/mcp",
      "headers": {
        "Authorization": "Bearer <token>"
      }
    }
  }
}
```

Then in a session, tools appear as `mcp__unifi-log-insight__<tool_name>`.

## Configure Claude Desktop

`claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "unifi-log-insight": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://<host>:8090/api/mcp",
               "--header", "Authorization:${AUTH_HEADER}"],
      "env": {
        "AUTH_HEADER": "Bearer <token>"
      }
    }
  }
}
```

Restart Claude Desktop after saving.

## Audit

If you enable **Settings > MCP > Audit logging**, every tool invocation is written to the `audit_log` table with token id, tool name, sanitised params (secrets masked), and timestamp. Retention is configurable (default 10 days).

Audit table cleanup runs daily at 03:30 alongside auth cleanup.

## Validate a deployment

Ship-in-repo smoke test (stdlib only, no venv needed):

```bash
export MCP_URL="http://<host>:8090/api/mcp"
export MCP_TOKEN="<bearer>"
python3 receiver/tests/mcp/smoke.py            # human-readable
python3 receiver/tests/mcp/smoke.py --json     # machine-readable
```

Exits `0` on all-green, `1` on failure. Covers every tool + a chained `search_logs → get_log`. Use it after any RC deploy to confirm the MCP surface didn't regress.

## CORS / cross-origin

The MCP server validates the `Origin` header against **Settings > MCP > Allowed origins**. Add your Claude web-app or any browser client's origin there if you hit CORS errors.

## Security notes

- Every request must present a bearer token — no anonymous access even for read
- Tokens are stored hashed; the plaintext is shown only at creation
- Rate-limited per-token to prevent runaway loops
- `set_firewall_syslog` is the only write tool; audit rows keep a record even for it
- MCP endpoint respects the same `AUTH_ENABLED` gate as the rest of the API
