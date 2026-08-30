---
original_url: https://insightsplus.dev/docs/troubleshooting.html
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
- <a href="database-maintenance.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Database Maintenance</a>
- <a href="troubleshooting.html" class="block rounded-md px-2 py-1 text-sm transition-colors bg-primary/10 font-medium text-primary">Troubleshooting</a>

</div>

<div class="min-w-0 flex-1 pt-10 pb-20">

# Troubleshooting

Common issues and how to fix them.

<div class="mt-8 space-y-8 text-[15px] leading-relaxed">

<div class="section">

## UniFi API Auth Errors

### UniFi OS (API Key)

- Use the **local controller URL** (e.g. `https://192.168.1.1`), not the Ubiquiti cloud URL.
- The **site ID** must be the internal name (usually `default`), not the display name shown in the UniFi UI.
- Use a **Local Admin**API key, not a cloud admin key. Create one in UniFi OS under Settings → Admins → Local Admin.
- If you changed `SECRET_KEY` or `POSTGRES_PASSWORD` after initial setup, stored API keys become unrecoverable. Re-enter the UniFi API key in Settings.

### Self-Hosted Controller (Username/Password)

- Use a **local account** on the controller, not a Ubiquiti SSO account.
- The controller URL should point to the local address and port (e.g. `https://192.168.1.10:8443`).
- If the controller uses a self-signed certificate, set `UNIFI_VERIFY_SSL=false` or configure it in Settings.
- Firewall rule management is **not available** on self-hosted controllers. Use the UniFi controller UI to toggle syslog on individual firewall rules.

</div>

<div class="section">

## No Logs Appearing

- Confirm your UniFi gateway's syslog is pointed at the Insights Plus host on **UDP port 514**.
- Syslog must be enabled **per firewall rule**in the UniFi controller. Use the Settings → Firewall zone matrix to bulk-toggle syslog.
- Check container logs for receiver errors:

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
docker logs unifi-log-insight --tail 100
```

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

</div>

</div>

Verify that **UDP 514** is not blocked by a host firewall or already in use by another process.

</div>

<div class="section">

## GeoIP Not Working

- Verify the `.mmdb` files exist in the MaxMind volume:

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
docker exec unifi-log-insight ls -la /app/maxmind/
```

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

</div>

</div>

- Check the health endpoint for GeoIP status:

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
curl http://localhost:8090/api/health
```

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

</div>

</div>

- If auto-update is configured, check the update log:

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
docker exec unifi-log-insight cat /var/log/geoip-update.log
```

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

</div>

</div>

- To trigger a manual update:

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
docker exec unifi-log-insight /app/geoip-update.sh
```

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

</div>

</div>

</div>

<div class="section">

## Container Won't Start

- Check the container logs for startup errors:

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
docker logs unifi-log-insight
```

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

</div>

</div>

- Verify your `.env` file exists and contains `POSTGRES_PASSWORD`.
- If the database is corrupted, reset with a full wipe (this destroys all data):

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
docker compose down -v
```

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

</div>

</div>

Then start fresh with `docker compose up -d`.

</div>

<div class="section">

## External Database Issues

<div class="mt-4 overflow-x-auto">

| Symptom                        | Fix                                                                                                                                                           |
|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Connection refused             | Verify DB_HOST, DB_PORT, and that the PostgreSQL server allows remote connections (check pg_hba.conf and listen_addresses)                                    |
| Password authentication failed | Confirm DB_PASSWORD matches the database user's password. If using POSTGRES_PASSWORD as fallback, ensure DB_PASSWORD is set explicitly for external databases |
| Permission denied              | The DB_USER must own or have full privileges on DB_NAME. Run GRANT ALL ON DATABASE ... TO ... as superuser                                                    |
| SSL required                   | Set DB_SSLMODE=require (or verify-ca / verify-full). Provide DB_SSLROOTCERT if the server uses a private CA                                                   |
| Health check shows unhealthy   | Check container logs with docker logs. Verify the external database is reachable from the container network and credentials are correct                       |

</div>

</div>

</div>

<div class="mt-12 flex items-center justify-between border-t border-border/50 pt-6">

<a href="database-maintenance.html" class="group flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"><img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoZXZyb24tbGVmdCBoLTQgdy00IHRyYW5zaXRpb24tdHJhbnNmb3JtIGdyb3VwLWhvdmVyOi10cmFuc2xhdGUteC0wLjUiIGFyaWEtaGlkZGVuPSJ0cnVlIj48cGF0aCBkPSJtMTUgMTgtNi02IDYtNiI+PC9wYXRoPjwvc3ZnPg==" class="lucide lucide-chevron-left h-4 w-4 transition-transform group-hover:-translate-x-0.5" /><span>Database Maintenance</span></a>

<div>

</div>

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
