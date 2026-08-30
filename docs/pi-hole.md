---
original_url: https://insightsplus.dev/docs/pi-hole.html
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

- <a href="configuration.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Environment Variables</a>
- <a href="authentication.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Authentication</a>
- <a href="maxmind.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">MaxMind GeoIP</a>
- <a href="abuseipdb.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">AbuseIPDB</a>
- <a href="pi-hole.html" class="block rounded-md px-2 py-1 text-sm transition-colors bg-primary/10 font-medium text-primary">Pi-hole</a>
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

<div class="flex items-center gap-4">

<img src="../icons/pihole.png" class="h-12 w-12 shrink-0" alt="Pi-hole" />

<div>

# Pi-hole Integration

Ingest DNS query logs from Pi-hole v6 directly into Insights Plus.

</div>

</div>

<div class="inline-flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3 mt-4">

<img src="data:image/svg+xml;base64,PHN2ZyB2aWV3Ym94PSIwIDAgMTYgMTYiIGhlaWdodD0iMTYiIHdpZHRoPSIxNiIgY2xhc3M9InNocmluay0wIHRleHQtYmx1ZS01MDAiPjxwYXRoIGZpbGw9ImN1cnJlbnRDb2xvciIgZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNMS41IDEuNWg0Ljg0Yy42NyAwIDEuMy4yNiAxLjc3LjczTDEzLjg4IDggOCAxMy44OCAyLjIzIDguMWEyLjUgMi41IDAgMCAxLS43My0xLjc3ek0xNiA4bC0xLjA2LTEuMDYtNS43Ny01Ljc3QTQgNCAwIDAgMCA2LjM0IDBIMHY2LjM0YTQgNCAwIDAgMCAxLjE3IDIuODNsNS43NyA1Ljc3TDggMTZsMS4wNi0xLjA2IDUuODgtNS44OHpNNC41IDUuMjVhLjc1Ljc1IDAgMSAwIDAtMS41Ljc1Ljc1IDAgMCAwIDAgMS41IiBjbGlwLXJ1bGU9ImV2ZW5vZGQiPjwvcGF0aD48L3N2Zz4=" class="shrink-0 text-blue-500" />

<div class="flex flex-col">

<span class="text-xs text-muted-foreground">Supported Version</span><span class="text-sm font-semibold">3.6.0</span>

</div>

</div>

<div class="mt-8 space-y-8 text-[15px] leading-relaxed">

<div class="section">

## Overview

If your UniFi gateway does not forward DNS query logs (see <a href="dns-logging.html" class="text-primary underline-offset-4 hover:underline">DNS Logging</a>), Insights Plus can poll a Pi-hole instance directly over its REST API and import every query into the same log stream as the rest of your network data. Queries are mapped to the standard log schema, enriched with GeoIP and threat intelligence, and appear alongside firewall and DHCP events in the dashboard.

<div class="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/5 px-4 py-3">

Pi-hole v6 only

The integration uses the v6 REST API. Older Pi-hole releases (v5 and below) are not supported and will be rejected during connection verification.

</div>

</div>

<div class="section">

## Prerequisites

- A reachable **Pi-hole v6** instance with its web admin interface accessible from the Insights Plus container
- The Pi-hole **admin password** (used to obtain a session ID via `/api/auth`)
- Pi-hole privacy level set to **“Show everything and record everything”** (level 0) - any higher level hides domains or client IPs and makes the data unusable. Configure this under *Pi-hole Settings \> Privacy \> Query Anonymization*.

</div>

<div class="section">

## Setup via the UI

1.  Open **Settings \> Integrations \> Pi-hole** in the Insights Plus web UI.
2.  Enter your Pi-hole URL. Include the scheme and port, no trailing slash. Both IP addresses and hostnames are supported, including local domains resolved by your own network — for example `http://192.0.2.10:80`, `http://pihole.mydomain.local`, or `https://pihole.example.net`.
3.  Enter the Pi-hole admin password. It is encrypted at rest using the same key as your other API credentials.
4.  Choose a **Poll Interval**: 15s for large networks (50+ devices), 30-60s for most homes, 2-5m for light use.
5.  Choose an **Enrichment** option (None, GeoIP only, Threat only, or Both). This controls whether resolved query IPs are enriched with GeoIP and AbuseIPDB threat data.
6.  Click **Test Connection**. On success, the version is displayed and the **Enable** toggle becomes available. Save to start polling.

The status card shows **Active** once the first poll completes successfully, along with the last poll timestamp.

</div>

<div class="section">

## Setup via Environment Variables

Pi-hole can also be configured headlessly. When both `PIHOLE_HOST` and `PIHOLE_PASSWORD` are set, the integration auto-enables on first start.

<div class="mt-4 overflow-x-auto">

| Variable               | Description                                                                                                                                                 |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `PIHOLE_HOST`          | Pi-hole base URL including scheme and port. Accepts IPs or hostnames, including local domains (e.g. `http://192.0.2.10:80`, `http://pihole.mydomain.local`) |
| `PIHOLE_PASSWORD`      | Pi-hole admin password                                                                                                                                      |
| `PIHOLE_POLL_INTERVAL` | Poll interval in seconds (15-86400). Defaults to 60                                                                                                         |
| `PIHOLE_ENABLED`       | `true` / `false`. Optional - auto-enables when host and password are both set                                                                               |

</div>

</div>

<div class="section">

## How It Works

- **Authentication** - The poller posts the password to `/api/auth` to obtain a session ID, then renews it automatically before expiry.
- **Polling** - `/api/queries` is fetched every poll interval. The first poll only imports the last 5 minutes; subsequent polls track the highest query ID seen and import only newer records.
- **Mapping** - Each Pi-hole query becomes a standard DNS log entry with action `allow` or `block` based on Pi-hole's status (FORWARDED, CACHE, GRAVITY, REGEX, etc).
- **DNS Resolution**- For non-blocked A/AAAA queries, the poller resolves the answer against Pi-hole's own DNS port (53) so enrichment matches what clients actually received. Results are cached for 5 minutes.
- **Enrichment** - Resolved public IPs flow through the same GeoIP and AbuseIPDB pipeline as the rest of your logs.

</div>

<div class="section">

## Troubleshooting

- **“Pi-hole vX.X is not supported”** - Only Pi-hole v6 is supported. Upgrade your Pi-hole instance.
- **“Privacy level must be set to...”** - Set *Pi-hole Settings \> Privacy \> Query Anonymization* to the first option (level 0). Anything higher hides domains or client IPs.
- **Status shows “Offline” after enabling** - Confirm the URL is reachable from inside the Insights Plus container (try `docker exec` + curl). Check the container logs for `pihole-poller` messages.
- **Auth rate-limited (HTTP 429)** - Pi-hole limits concurrent sessions. The poller backs off automatically; avoid logging in to the Pi-hole admin UI in multiple tabs at once.
- **“Returned queries at fetch limit” warning** - Your network is generating more than 10,000 queries per poll interval. Reduce the poll interval to keep up.

</div>

</div>

<div class="mt-12 flex items-center justify-between border-t border-border/50 pt-6">

<a href="abuseipdb.html" class="group flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"><img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoZXZyb24tbGVmdCBoLTQgdy00IHRyYW5zaXRpb24tdHJhbnNmb3JtIGdyb3VwLWhvdmVyOi10cmFuc2xhdGUteC0wLjUiIGFyaWEtaGlkZGVuPSJ0cnVlIj48cGF0aCBkPSJtMTUgMTgtNi02IDYtNiI+PC9wYXRoPjwvc3ZnPg==" class="lucide lucide-chevron-left h-4 w-4 transition-transform group-hover:-translate-x-0.5" /><span>AbuseIPDB</span></a><a href="external-database.html" class="group flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"><span>External Database</span><img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoZXZyb24tcmlnaHQgaC00IHctNCB0cmFuc2l0aW9uLXRyYW5zZm9ybSBncm91cC1ob3Zlcjp0cmFuc2xhdGUteC0wLjUiIGFyaWEtaGlkZGVuPSJ0cnVlIj48cGF0aCBkPSJtOSAxOCA2LTYtNi02Ij48L3BhdGg+PC9zdmc+" class="lucide lucide-chevron-right h-4 w-4 transition-transform group-hover:translate-x-0.5" /></a>

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
