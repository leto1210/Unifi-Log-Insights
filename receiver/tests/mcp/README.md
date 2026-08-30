# MCP smoke suite

End-to-end validation of every tool exposed by the `unifi-log-insight` MCP
server. Not run by pytest — this is an operator-executed check to run
against a live deployment (RC / prod).

## Run against a deployment

```bash
export MCP_URL="http://core-syno:8099/api/mcp"          # or duncan
export MCP_TOKEN="<bearer token from Settings > MCP > Tokens>"

python3 receiver/tests/mcp/smoke.py                       # human-readable
python3 receiver/tests/mcp/smoke.py --json > report.json  # for automation
```

Exit code: `0` on all-green, `1` on any failure, `2` on missing flags.

## What it checks (14 tools + 1 chained)

| Tool                   | What it validates                                   |
| ---------------------- | --------------------------------------------------- |
| `get_health`           | `status == "ok"` and `version` present              |
| `get_log_stats`        | non-empty result                                    |
| `list_interfaces`      | non-empty result                                    |
| `list_services`        | non-empty result                                    |
| `list_protocols`       | non-empty result                                    |
| `get_unifi_status`     | responds (may report disabled — that's still pass)  |
| `list_unifi_devices`   | non-empty result (needs UniFi API creds)            |
| `list_unifi_clients`   | non-empty result                                    |
| `list_firewall_policies` | non-empty (needs zone-based firewall)             |
| `search_logs`          | returns a recent-logs sample                        |
| `aggregate_logs`       | groups by src_ip on a 1h window                     |
| `get_top_threat_ips`   | threat digest (may be empty on quiet networks)      |
| `list_threat_ips`      | paginated threat list                               |
| `export_logs_csv_url`  | CSV URL builder                                     |
| `get_log` (chained)    | fetches the id returned by search_logs              |

`set_firewall_syslog` is intentionally **not** included — it mutates
UniFi state. Test it manually with a controlled input if you need to.

## Cross-validation with the direct UDM API

The count returned by `list_unifi_devices` / `list_unifi_clients` /
`list_firewall_policies` should match what the UniFi controller reports
directly. Ad-hoc check via the `unifi` MCP (available in this session):

```
mcp__unifi__list_devices_by_type      # vs. mcp__unifi-log-insight__list_unifi_devices
mcp__unifi__list_active_clients       # vs. list_unifi_clients (count may differ — active vs known)
mcp__unifi__list_firewall_policies    # vs. list_firewall_policies
```

Rule of thumb: device count should be exactly equal; client count from
ULI can be **greater** than "active" since ULI keeps historically-seen
clients until the retention window expires.

## Adding a new tool

Append a row to `CHECKS` in `smoke.py`:

```python
CHECKS = [
    ...
    ('new_tool_name', {'arg': 'value'}, v_content_nonempty, 'human description'),
]
```

For richer assertions, write a dedicated validator that returns `None`
on pass or an error string on fail, and use it instead of the generic
`v_content_nonempty`.
