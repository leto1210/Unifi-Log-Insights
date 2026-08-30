---
original_url: https://insightsplus.dev/docs/configuration.html
original_source: insightsplus.dev
attribution: "Copied from https://insightsplus.dev/docs — original author credited"
---

<div hidden="">

</div>

<div class="relative flex min-h-screen flex-col">

<div class="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-lg">

<div class="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">

<a href="../index.html" class="flex items-center gap-2.5"><img src="data:image/svg+xml;base64,PHN2ZyB2aWV3Ym94PSIwIDAgMTAwIDExNiIgY2xhc3M9InctNiBoLTciIGZpbGw9Im5vbmUiIHJvbGU9ImltZyIgYXJpYS1sYWJlbD0iSW5zaWdodHMgUGx1cyI+PHBhdGggZD0iTSAyOSA2OCBDIDIyIDYyLCAxNiA1MywgMTYgNDEgQSAzNCAzNCAwIDEgMSA4NCA0MSBDIDg0IDUzLCA3OCA2MiwgNzEgNjggWiIgY2xhc3M9ImZpbGwtWyMxNEI4QTZdLzEyIGRhcms6ZmlsbC1bIzE0YjhhNl0vMTIiPjwvcGF0aD48cGF0aCBkPSJNIDI5IDY4IEMgMjIgNjIsIDE2IDUzLCAxNiA0MSBBIDM0IDM0IDAgMSAxIDg0IDQxIEMgODQgNTMsIDc4IDYyLCA3MSA2OCIgY2xhc3M9InN0cm9rZS1bIzE0QjhBNl0gZGFyazpzdHJva2UtWyMxNGI4YTZdIiBzdHJva2Utd2lkdGg9IjUuMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBmaWxsPSJub25lIj48L3BhdGg+PHBhdGggZD0iTSAyOCAzNCBBIDE4IDE4IDAgMCAxIDQ0IDIyIiBjbGFzcz0ic3Ryb2tlLVsjMTRCOEE2XSBkYXJrOnN0cm9rZS1bIzE0YjhhNl0iIHN0cm9rZS13aWR0aD0iNC44IiBzdHJva2UtbGluZWNhcD0icm91bmQiIGZpbGw9Im5vbmUiIG9wYWNpdHk9IjAuNyI+PC9wYXRoPjxsaW5lIHgxPSIyOCIgeTE9Ijc1IiB4Mj0iNzIiIHkyPSI3NSIgY2xhc3M9InN0cm9rZS1bIzE0QjhBNl0gZGFyazpzdHJva2UtWyMxNGI4YTZdIiBzdHJva2Utd2lkdGg9IjUuMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L2xpbmU+PGxpbmUgeDE9IjM2IiB5MT0iODQiIHgyPSI2NCIgeTI9Ijg0IiBjbGFzcz0ic3Ryb2tlLVsjMTRCOEE2XSBkYXJrOnN0cm9rZS1bIzE0YjhhNl0iIHN0cm9rZS13aWR0aD0iNS4yIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvbGluZT48dGV4dCB4PSI1MCIgeT0iMTEwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iLWFwcGxlLXN5c3RlbSxCbGlua01hY1N5c3RlbUZvbnQsJiMzOTtTRiBQcm8gRGlzcGxheSYjMzk7LHNhbnMtc2VyaWYiIGZvbnQtd2VpZ2h0PSI4MDAiIGZvbnQtc2l6ZT0iMTkiIGxldHRlci1zcGFjaW5nPSIwLjE2ZW0iIGNsYXNzPSJmaWxsLVsjMEQ5NDg4XSBkYXJrOmZpbGwtWyMwZDk0ODhdIj5QTFVTPC90ZXh0Pjwvc3ZnPg==" class="w-6 h-7" /><span class="text-lg font-bold tracking-tight">Insights Plus</span></a>

<a href="../index.html#features" class="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground">Features</a><a href="../index.html#extension" class="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground">Extension</a><a href="../roadmap.html" class="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground">Roadmap</a><a href="../docs.html" class="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground">Docs</a>

<div class="flex items-center gap-2">

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXNlYXJjaCBoLTMuNSB3LTMuNSIgYXJpYS1oaWRkZW49InRydWUiPjxwYXRoIGQ9Im0yMSAyMS00LjM0LTQuMzQiPjwvcGF0aD48Y2lyY2xlIGN4PSIxMSIgY3k9IjExIiByPSI4Ij48L2NpcmNsZT48L3N2Zz4=" class="lucide lucide-search h-3.5 w-3.5" />Search docs...<span class="kbd ml-2 rounded border border-border/60 bg-background px-1.5 py-0.5 font-mono text-[10px]"><span class="text-xs">⌘</span>K</span>

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXNlYXJjaCBoLTQgdy00IHRleHQtbXV0ZWQtZm9yZWdyb3VuZCIgYXJpYS1oaWRkZW49InRydWUiPjxwYXRoIGQ9Im0yMSAyMS00LjM0LTQuMzQiPjwvcGF0aD48Y2lyY2xlIGN4PSIxMSIgY3k9IjExIiByPSI4Ij48L2NpcmNsZT48L3N2Zz4=" class="lucide lucide-search h-4 w-4 text-muted-foreground" />

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWdpdGh1YiBoLTQgdy00IiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHBhdGggZD0iTTE1IDIydi00YTQuOCA0LjggMCAwIDAtMS0zLjVjMyAwIDYtMiA2LTUuNS4wOC0xLjI1LS4yNy0yLjQ4LTEtMy41LjI4LTEuMTUuMjgtMi4zNSAwLTMuNSAwIDAtMSAwLTMgMS41LTIuNjQtLjUtNS4zNi0uNS04IDBDNiAyIDUgMiA1IDJjLS4zIDEuMTUtLjMgMi4zNSAwIDMuNUE1LjQwMyA1LjQwMyAwIDAgMCA0IDljMCAzLjUgMyA1LjUgNiA1LjUtLjM5LjQ5LS42OCAxLjA1LS44NSAxLjY1LS4xNy42LS4yMiAxLjIzLS4xNSAxLjg1djQiPjwvcGF0aD48cGF0aCBkPSJNOSAxOGMtNC41MSAyLTUtMi03LTIiPjwvcGF0aD48L3N2Zz4=" class="lucide lucide-github h-4 w-4" /><span class="sr-only">GitHub</span>

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXN1biBoLTQgdy00IHJvdGF0ZS0wIHNjYWxlLTEwMCB0cmFuc2l0aW9uLXRyYW5zZm9ybSBkYXJrOi1yb3RhdGUtOTAgZGFyazpzY2FsZS0wIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iNCI+PC9jaXJjbGU+PHBhdGggZD0iTTEyIDJ2MiI+PC9wYXRoPjxwYXRoIGQ9Ik0xMiAyMHYyIj48L3BhdGg+PHBhdGggZD0ibTQuOTMgNC45MyAxLjQxIDEuNDEiPjwvcGF0aD48cGF0aCBkPSJtMTcuNjYgMTcuNjYgMS40MSAxLjQxIj48L3BhdGg+PHBhdGggZD0iTTIgMTJoMiI+PC9wYXRoPjxwYXRoIGQ9Ik0yMCAxMmgyIj48L3BhdGg+PHBhdGggZD0ibTYuMzQgMTcuNjYtMS40MSAxLjQxIj48L3BhdGg+PHBhdGggZD0ibTE5LjA3IDQuOTMtMS40MSAxLjQxIj48L3BhdGg+PC9zdmc+" class="lucide lucide-sun h-4 w-4 rotate-0 scale-100 transition-transform dark:-rotate-90 dark:scale-0" /><img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLW1vb24gYWJzb2x1dGUgaC00IHctNCByb3RhdGUtOTAgc2NhbGUtMCB0cmFuc2l0aW9uLXRyYW5zZm9ybSBkYXJrOnJvdGF0ZS0wIGRhcms6c2NhbGUtMTAwIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHBhdGggZD0iTTIwLjk4NSAxMi40ODZhOSA5IDAgMSAxLTkuNDczLTkuNDcyYy40MDUtLjAyMi42MTcuNDYuNDAyLjgwM2E2IDYgMCAwIDAgOC4yNjggOC4yNjhjLjM0NC0uMjE1LjgyNS0uMDA0LjgwMy40MDEiPjwvcGF0aD48L3N2Zz4=" class="lucide lucide-moon absolute h-4 w-4 rotate-90 scale-0 transition-transform dark:rotate-0 dark:scale-100" /><span class="sr-only">Toggle theme</span>

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLW1lbnUgaC00IHctNCIgYXJpYS1oaWRkZW49InRydWUiPjxwYXRoIGQ9Ik00IDVoMTYiPjwvcGF0aD48cGF0aCBkPSJNNCAxMmgxNiI+PC9wYXRoPjxwYXRoIGQ9Ik00IDE5aDE2Ij48L3BhdGg+PC9zdmc+" class="lucide lucide-menu h-4 w-4" />

</div>

</div>

</div>

<div class="flex-1" role="main">

<div class="mx-auto max-w-7xl px-4 sm:px-6">

<div class="lg:grid lg:min-h-[calc(100vh-var(--navbar-h))] lg:grid-cols-[11rem_minmax(0,1fr)] lg:gap-8">

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLW1lbnUgaC00IHctNCIgYXJpYS1oaWRkZW49InRydWUiPjxwYXRoIGQ9Ik00IDVoMTYiPjwvcGF0aD48cGF0aCBkPSJNNCAxMmgxNiI+PC9wYXRoPjxwYXRoIGQ9Ik00IDE5aDE2Ij48L3BhdGg+PC9zdmc+" class="lucide lucide-menu h-4 w-4" />

<div>

#### Getting Started

- <a href="../docs.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Introduction</a>
- <a href="getting-started.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Prerequisites</a>
- <a href="installation.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Installation</a>

</div>

<div>

#### Configuration

- <a href="configuration.html" class="block rounded-md px-2 py-1 text-sm transition-colors bg-primary/10 font-medium text-primary">Environment Variables</a>
- <a href="authentication.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Authentication</a>
- <a href="maxmind.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">MaxMind GeoIP</a>
- <a href="abuseipdb.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">AbuseIPDB</a>
- <a href="pi-hole.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Pi-hole</a>
- <a href="external-database.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">External Database</a>

</div>

<div>

#### Features

- <a href="ui-guide.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">UI Guide</a>
- <a href="mcp.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">AI Agent (MCP)</a>
- <a href="browser-extension.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Browser Extension</a>
- <a href="dns-logging.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">DNS Logging</a>
- <a href="api-reference.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">API Reference</a>

</div>

<div>

#### Deployment

- <a href="unraid.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Unraid Setup</a>
- <a href="database-maintenance.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Database Maintenance</a>
- <a href="troubleshooting.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Troubleshooting</a>

</div>

<div class="min-w-0 flex-1 pt-10 pb-20">

# Environment Variables

All configuration options for Insights Plus.

<div class="mt-8 space-y-8 text-[15px] leading-relaxed">

<div class="section">

## Environment Variables

<div class="mt-4 overflow-x-auto">

| Variable               | Description                                                                                                                                                     |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `SECRET_KEY`           | Encryption key for stored API keys, UniFi credentials, and session tokens. Recommended but optional — falls back to POSTGRES_PASSWORD or DB_PASSWORD if not set |
| `AUTH_ENABLED`         | Set to true to enable built-in authentication. Requires HTTPS. Default: false                                                                                   |
| `POSTGRES_PASSWORD`    | PostgreSQL password for the embedded database user. Not required when using an external database with SECRET_KEY set                                            |
| `ABUSEIPDB_API_KEY`    | Enables threat scoring on blocked inbound IPs. Free tier: 1,000 check lookups/day + 5 blacklist pulls/day                                                       |
| `MAXMIND_ACCOUNT_ID`   | Enables GeoIP auto-update. Without it, manually place .mmdb files                                                                                               |
| `MAXMIND_LICENSE_KEY`  | Paired with account ID for auto-update                                                                                                                          |
| `TZ`                   | Timezone for cron schedules. Defaults to UTC. Examples: Europe/London, Asia/Amman, America/New_York                                                             |
| `LOG_LEVEL`            | Logging verbosity: DEBUG, INFO, WARNING, ERROR, CRITICAL. Defaults to INFO                                                                                      |
| `UNIFI_HOST`           | UniFi Controller URL (e.g., https://192.168.1.1). Can also be set via Settings UI                                                                               |
| `UNIFI_API_KEY`        | UniFi API key (Local Admin). For UniFi OS controllers only. Can also be set via Settings UI                                                                     |
| `UNIFI_USERNAME`       | Local username for self-hosted UniFi controllers. Use instead of UNIFI_API_KEY. Can also be set via Settings UI                                                 |
| `UNIFI_PASSWORD`       | Local password for self-hosted UniFi controllers. Paired with UNIFI_USERNAME. Can also be set via Settings UI                                                   |
| `UNIFI_SITE`           | UniFi site name. Defaults to 'default'                                                                                                                          |
| `UNIFI_VERIFY_SSL`     | Set to false for self-signed certificates. Defaults to true                                                                                                     |
| `UNIFI_POLL_INTERVAL`  | Device polling interval in seconds. Defaults to 300 (5 minutes)                                                                                                 |
| `UNIFI_ENABLED`        | Master toggle for UniFi integration. Auto-enables when both UNIFI_HOST and UNIFI_API_KEY are set                                                                |
| `PIHOLE_HOST`          | Pi-hole v6 base URL (e.g., http://10.10.10.229:60080). See Pi-hole docs page                                                                                    |
| `PIHOLE_PASSWORD`      | Pi-hole admin password. Setting both PIHOLE_HOST and PIHOLE_PASSWORD auto-enables the integration                                                               |
| `PIHOLE_POLL_INTERVAL` | Pi-hole poll interval in seconds (15-86400). Defaults to 60                                                                                                     |
| `PIHOLE_ENABLED`       | Master toggle for the Pi-hole integration. Defaults to auto-enable when host + password are set                                                                 |
| `RETENTION_DAYS`       | Log retention in days for firewall/DHCP/Wi-Fi/system. Defaults to 60                                                                                            |
| `DNS_RETENTION_DAYS`   | DNS log retention in days. Defaults to 10                                                                                                                       |
| `DB_HOST`              | External PostgreSQL host. When set to a non-localhost address, embedded PG is disabled                                                                          |
| `DB_PORT`              | External PostgreSQL port (default: 5432)                                                                                                                        |
| `DB_NAME`              | Database name (default: unifi_logs)                                                                                                                             |
| `DB_USER`              | Database user (default: unifi)                                                                                                                                  |
| `DB_PASSWORD`          | Database password (falls back to POSTGRES_PASSWORD)                                                                                                             |
| `DB_SSLMODE`           | SSL mode: require, verify-ca, verify-full                                                                                                                       |
| `DB_SSLROOTCERT`       | Path to CA certificate file                                                                                                                                     |
| `DB_SSLCERT`           | Path to client certificate (mTLS)                                                                                                                               |
| `DB_SSLKEY`            | Path to client key (mTLS)                                                                                                                                       |

</div>

</div>

<div class="section">

## Ports

<div class="mt-4 overflow-x-auto">

| Port | Protocol | Purpose                                    |
|------|----------|--------------------------------------------|
| 514  | UDP      | Syslog receiver (incoming logs from UniFi) |
| 8090 | TCP      | Web UI and REST API                        |

</div>

</div>

<div class="section">

## Retention Policy

<div class="mt-4 overflow-x-auto">

| Log Type                      | Default | Range       |
|-------------------------------|---------|-------------|
| Firewall, DHCP, Wi-Fi, System | 60 days | 1-3650 days |
| DNS (when enabled)            | 10 days | 1-3650 days |

</div>

Configurable via **Settings \> Data & Backups** slider, or via environment variables. Cleanup runs daily at 03:00.

</div>

</div>

<div class="mt-12 flex items-center justify-between border-t border-border/50 pt-6">

<a href="installation.html" class="group flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"><img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoZXZyb24tbGVmdCBoLTQgdy00IHRyYW5zaXRpb24tdHJhbnNmb3JtIGdyb3VwLWhvdmVyOi10cmFuc2xhdGUteC0wLjUiIGFyaWEtaGlkZGVuPSJ0cnVlIj48cGF0aCBkPSJtMTUgMTgtNi02IDYtNiI+PC9wYXRoPjwvc3ZnPg==" class="lucide lucide-chevron-left h-4 w-4 transition-transform group-hover:-translate-x-0.5" /><span>Installation</span></a><a href="authentication.html" class="group flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"><span>Authentication</span><img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoZXZyb24tcmlnaHQgaC00IHctNCB0cmFuc2l0aW9uLXRyYW5zZm9ybSBncm91cC1ob3Zlcjp0cmFuc2xhdGUteC0wLjUiIGFyaWEtaGlkZGVuPSJ0cnVlIj48cGF0aCBkPSJtOSAxOCA2LTYtNi02Ij48L3BhdGg+PC9zdmc+" class="lucide lucide-chevron-right h-4 w-4 transition-transform group-hover:translate-x-0.5" /></a>

</div>

</div>

</div>

</div>

</div>

<div class="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 py-8 sm:flex-row sm:px-6">

<div class="flex items-center gap-2 text-sm text-muted-foreground">

<img src="data:image/svg+xml;base64,PHN2ZyB2aWV3Ym94PSIwIDAgMTAwIDExNiIgY2xhc3M9InctNCBoLTUiIGZpbGw9Im5vbmUiIHJvbGU9ImltZyIgYXJpYS1sYWJlbD0iSW5zaWdodHMgUGx1cyI+PHBhdGggZD0iTSAyOSA2OCBDIDIyIDYyLCAxNiA1MywgMTYgNDEgQSAzNCAzNCAwIDEgMSA4NCA0MSBDIDg0IDUzLCA3OCA2MiwgNzEgNjggWiIgY2xhc3M9ImZpbGwtWyMxNEI4QTZdLzEyIGRhcms6ZmlsbC1bIzE0YjhhNl0vMTIiPjwvcGF0aD48cGF0aCBkPSJNIDI5IDY4IEMgMjIgNjIsIDE2IDUzLCAxNiA0MSBBIDM0IDM0IDAgMSAxIDg0IDQxIEMgODQgNTMsIDc4IDYyLCA3MSA2OCIgY2xhc3M9InN0cm9rZS1bIzE0QjhBNl0gZGFyazpzdHJva2UtWyMxNGI4YTZdIiBzdHJva2Utd2lkdGg9IjUuMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBmaWxsPSJub25lIj48L3BhdGg+PHBhdGggZD0iTSAyOCAzNCBBIDE4IDE4IDAgMCAxIDQ0IDIyIiBjbGFzcz0ic3Ryb2tlLVsjMTRCOEE2XSBkYXJrOnN0cm9rZS1bIzE0YjhhNl0iIHN0cm9rZS13aWR0aD0iNC44IiBzdHJva2UtbGluZWNhcD0icm91bmQiIGZpbGw9Im5vbmUiIG9wYWNpdHk9IjAuNyI+PC9wYXRoPjxsaW5lIHgxPSIyOCIgeTE9Ijc1IiB4Mj0iNzIiIHkyPSI3NSIgY2xhc3M9InN0cm9rZS1bIzE0QjhBNl0gZGFyazpzdHJva2UtWyMxNGI4YTZdIiBzdHJva2Utd2lkdGg9IjUuMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIj48L2xpbmU+PGxpbmUgeDE9IjM2IiB5MT0iODQiIHgyPSI2NCIgeTI9Ijg0IiBjbGFzcz0ic3Ryb2tlLVsjMTRCOEE2XSBkYXJrOnN0cm9rZS1bIzE0YjhhNl0iIHN0cm9rZS13aWR0aD0iNS4yIiBzdHJva2UtbGluZWNhcD0icm91bmQiPjwvbGluZT48dGV4dCB4PSI1MCIgeT0iMTEwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LWZhbWlseT0iLWFwcGxlLXN5c3RlbSxCbGlua01hY1N5c3RlbUZvbnQsJiMzOTtTRiBQcm8gRGlzcGxheSYjMzk7LHNhbnMtc2VyaWYiIGZvbnQtd2VpZ2h0PSI4MDAiIGZvbnQtc2l6ZT0iMTkiIGxldHRlci1zcGFjaW5nPSIwLjE2ZW0iIGNsYXNzPSJmaWxsLVsjMEQ5NDg4XSBkYXJrOmZpbGwtWyMwZDk0ODhdIj5QTFVTPC90ZXh0Pjwvc3ZnPg==" class="w-4 h-5" />Built by <a href="https://github.com/jmasarweh" class="font-medium text-foreground underline-offset-4 hover:underline" target="_blank" rel="noopener noreferrer">jmasarweh</a>

</div>

<a href="../privacy.html" class="hover:text-foreground transition-colors">Privacy</a><a href="../docs.html" class="hover:text-foreground transition-colors">Docs</a><a href="https://github.com/jmasarweh/unifi-log-insight" class="hover:text-foreground transition-colors" target="_blank" rel="noopener noreferrer">GitHub</a>

</div>

</div>
