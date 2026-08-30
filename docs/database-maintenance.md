---
original_url: https://insightsplus.dev/docs/database-maintenance.html
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
- <a href="database-maintenance.html" class="block rounded-md px-2 py-1 text-sm transition-colors bg-primary/10 font-medium text-primary">Database Maintenance</a>
- <a href="troubleshooting.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Troubleshooting</a>

</div>

<div class="min-w-0 flex-1 pt-10 pb-20">

# Database Maintenance

Reclaim disk space and keep PostgreSQL running efficiently.

<div class="mt-8 space-y-8 text-[15px] leading-relaxed">

<div class="section">

## Why Disk Space Doesn't Shrink

PostgreSQL's `DELETE` command marks rows as dead but does not return the space to the operating system. The daily retention cleanup removes old logs on schedule, but the on-disk database files stay the same size until you explicitly reclaim the space.

</div>

<div class="section">

## Step 1: Run Retention Cleanup

The easiest way to trigger an immediate cleanup is from **Settings → Data & Backups** in the UI, or via the API:

``` mt-3
POST /api/config/retention/cleanup
```

Alternatively, if you want to run the retention query manually before the daily 03:00 cron, you can delete rows directly. This deletes rows older than your configured retention period:

<div class="group relative mt-3">

<div class="overflow-hidden rounded-xl border border-border/60 bg-white dark:bg-[#0a0c10]">

<div class="flex items-center gap-4 border-b border-border/40 px-4 py-2.5">

<div class="flex gap-1.5">

<div class="h-2 w-2 rounded-full bg-border dark:bg-[#2a2d32]">

</div>

<div class="h-2 w-2 rounded-full bg-border dark:bg-[#2a2d32]">

</div>

<div class="h-2 w-2 rounded-full bg-border dark:bg-[#2a2d32]">

</div>

</div>

</div>

<div class="flex items-center gap-3 px-4 py-3">

<span class="select-none font-mono text-sm text-muted-foreground">\$</span>

``` flex-1
docker exec unifi-log-insight psql -U unifi -d unifi_logs -c "
  DELETE FROM logs
  WHERE timestamp < NOW() - INTERVAL '60 days';
"
```

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

</div>

</div>

Adjust `60 days` to match your `RETENTION_DAYS` setting.

</div>

<div class="section">

## Step 2: VACUUM ANALYZE (Safe)

A standard `VACUUM ANALYZE` reclaims dead-row space for reuse by future inserts and updates query planner statistics. It runs **without locking** the table, so the application keeps working normally:

<div class="group relative mt-3">

<div class="overflow-hidden rounded-xl border border-border/60 bg-white dark:bg-[#0a0c10]">

<div class="flex items-center gap-4 border-b border-border/40 px-4 py-2.5">

<div class="flex gap-1.5">

<div class="h-2 w-2 rounded-full bg-border dark:bg-[#2a2d32]">

</div>

<div class="h-2 w-2 rounded-full bg-border dark:bg-[#2a2d32]">

</div>

<div class="h-2 w-2 rounded-full bg-border dark:bg-[#2a2d32]">

</div>

</div>

</div>

<div class="flex items-center gap-3 px-4 py-3">

<span class="select-none font-mono text-sm text-muted-foreground">\$</span>

``` flex-1
docker exec unifi-log-insight psql -U unifi -d unifi_logs -c "
  VACUUM ANALYZE logs;
"
```

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

</div>

</div>

This makes the freed space available for new rows but does not reduce the on-disk file size.

</div>

<div class="section">

## Step 3: VACUUM FULL ANALYZE (Shrinks Disk)

To actually shrink the database files on disk, run `VACUUM FULL ANALYZE`. This rewrites the entire table and returns space to the OS. **Warning:** it takes an **exclusive lock** on the table - reads and writes will block until it finishes.

<div class="group relative mt-3">

<div class="overflow-hidden rounded-xl border border-border/60 bg-white dark:bg-[#0a0c10]">

<div class="flex items-center gap-4 border-b border-border/40 px-4 py-2.5">

<div class="flex gap-1.5">

<div class="h-2 w-2 rounded-full bg-border dark:bg-[#2a2d32]">

</div>

<div class="h-2 w-2 rounded-full bg-border dark:bg-[#2a2d32]">

</div>

<div class="h-2 w-2 rounded-full bg-border dark:bg-[#2a2d32]">

</div>

</div>

</div>

<div class="flex items-center gap-3 px-4 py-3">

<span class="select-none font-mono text-sm text-muted-foreground">\$</span>

``` flex-1
docker exec unifi-log-insight psql -U unifi -d unifi_logs -c "
  VACUUM FULL ANALYZE logs;
"
```

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

</div>

</div>

For large databases this can take several minutes. Run it during a maintenance window when brief downtime is acceptable.

</div>

<div class="section">

## Additional Checks

If disk usage is still higher than expected after vacuuming, check the Docker container logs and the WAL directory:

<div class="group relative mt-3">

<div class="overflow-hidden rounded-xl border border-border/60">

<div class="shiki-wrapper overflow-x-auto text-sm [&_pre]:!bg-[#fafafa] [&_pre]:!p-4 dark:[&_pre]:!bg-[#0a0c10] [&_code]:font-mono">

``` shiki
# Check container logs for errors
docker logs unifi-log-insight --tail 50

# Check WAL directory size
docker exec unifi-log-insight du -sh /var/lib/postgresql/data/pg_wal
```

</div>

</div>

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

A large `pg_wal` directory can indicate replication slots or checkpoint issues. Restarting the container typically resolves temporary WAL buildup.

</div>

<div class="section">

## Docker Container Log Rotation

Docker's default `json-file` logging driver captures all container stdout/stderr output. Without rotation, this log file can grow to tens of gigabytes over time.

The default `docker-compose.yml` ships with log rotation enabled (10 MB per file, 5 files max = ~50 MB cap). If you use a custom compose file, add a `logging:` section to your service:

<div class="group relative mt-3">

<div class="overflow-hidden rounded-xl border border-border/60">

<div class="shiki-wrapper overflow-x-auto text-sm [&_pre]:!bg-[#fafafa] [&_pre]:!p-4 dark:[&_pre]:!bg-[#0a0c10] [&_code]:font-mono">

``` shiki
services:
  unifi-log-insight:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
```

</div>

</div>

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

Adjust `max-size` and `max-file` to suit your needs. You can also set rotation globally via `/etc/docker/daemon.json`.

To check the current Docker log file size (Linux only, requires privileged access):

<div class="group relative mt-3">

<div class="overflow-hidden rounded-xl border border-border/60 bg-white dark:bg-[#0a0c10]">

<div class="flex items-center gap-4 border-b border-border/40 px-4 py-2.5">

<div class="flex gap-1.5">

<div class="h-2 w-2 rounded-full bg-border dark:bg-[#2a2d32]">

</div>

<div class="h-2 w-2 rounded-full bg-border dark:bg-[#2a2d32]">

</div>

<div class="h-2 w-2 rounded-full bg-border dark:bg-[#2a2d32]">

</div>

</div>

</div>

<div class="flex items-center gap-3 px-4 py-3">

<span class="select-none font-mono text-sm text-muted-foreground">\$</span>

``` flex-1
docker run --rm --privileged --pid=host alpine nsenter -t 1 -m -- sh -c "ls -lh $(docker inspect unifi-log-insight --format='{{.LogPath}}')"
```

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

</div>

</div>

</div>

</div>

<div class="mt-12 flex items-center justify-between border-t border-border/50 pt-6">

<a href="unraid.html" class="group flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"><img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoZXZyb24tbGVmdCBoLTQgdy00IHRyYW5zaXRpb24tdHJhbnNmb3JtIGdyb3VwLWhvdmVyOi10cmFuc2xhdGUteC0wLjUiIGFyaWEtaGlkZGVuPSJ0cnVlIj48cGF0aCBkPSJtMTUgMTgtNi02IDYtNiI+PC9wYXRoPjwvc3ZnPg==" class="lucide lucide-chevron-left h-4 w-4 transition-transform group-hover:-translate-x-0.5" /><span>Unraid Setup</span></a><a href="troubleshooting.html" class="group flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"><span>Troubleshooting</span><img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoZXZyb24tcmlnaHQgaC00IHctNCB0cmFuc2l0aW9uLXRyYW5zZm9ybSBncm91cC1ob3Zlcjp0cmFuc2xhdGUteC0wLjUiIGFyaWEtaGlkZGVuPSJ0cnVlIj48cGF0aCBkPSJtOSAxOCA2LTYtNi02Ij48L3BhdGg+PC9zdmc+" class="lucide lucide-chevron-right h-4 w-4 transition-transform group-hover:translate-x-0.5" /></a>

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
