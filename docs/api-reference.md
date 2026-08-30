---
original_url: https://insightsplus.dev/docs/api-reference.html
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
- <a href="api-reference.html" class="block rounded-md px-2 py-1 text-sm transition-colors bg-primary/10 font-medium text-primary">API Reference</a>

</div>

<div>

#### Deployment

- <a href="unraid.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Unraid Setup</a>
- <a href="database-maintenance.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Database Maintenance</a>
- <a href="troubleshooting.html" class="block rounded-md px-2 py-1 text-sm transition-colors text-muted-foreground hover:bg-muted hover:text-foreground">Troubleshooting</a>

</div>

<div class="min-w-0 flex-1 pt-10 pb-20">

# API Reference

All REST API endpoints served on port 8090.

<div class="mt-4 flex items-center gap-3">

<div class="inline-flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3">

<img src="data:image/svg+xml;base64,PHN2ZyB2aWV3Ym94PSIwIDAgMTYgMTYiIGhlaWdodD0iMTYiIHdpZHRoPSIxNiIgY2xhc3M9InNocmluay0wIHRleHQtYmx1ZS01MDAiPjxwYXRoIGZpbGw9ImN1cnJlbnRDb2xvciIgZmlsbC1ydWxlPSJldmVub2RkIiBkPSJNMS41IDEuNWg0Ljg0Yy42NyAwIDEuMy4yNiAxLjc3LjczTDEzLjg4IDggOCAxMy44OCAyLjIzIDguMWEyLjUgMi41IDAgMCAxLS43My0xLjc3ek0xNiA4bC0xLjA2LTEuMDYtNS43Ny01Ljc3QTQgNCAwIDAgMCA2LjM0IDBIMHY2LjM0YTQgNCAwIDAgMCAxLjE3IDIuODNsNS43NyA1Ljc3TDggMTZsMS4wNi0xLjA2IDUuODgtNS44OHpNNC41IDUuMjVhLjc1Ljc1IDAgMSAwIDAtMS41Ljc1Ljc1IDAgMCAwIDAgMS41IiBjbGlwLXJ1bGU9ImV2ZW5vZGQiPjwvcGF0aD48L3N2Zz4=" class="shrink-0 text-blue-500" />

<div class="flex flex-col">

<span class="text-xs text-muted-foreground">Supported Version</span><span class="text-sm font-semibold">3.3.0</span>

</div>

</div>

<a href="../openapi.html" class="inline-flex items-center gap-1.5 rounded-md border border-border/60 bg-muted/50 px-2.5 py-1 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground">OpenAPI Spec<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMiIgaGVpZ2h0PSIxMiIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xOCAxM3Y2YTIgMiAwIDAgMS0yIDJINWEyIDIgMCAwIDEtMi0yVjhhMiAyIDAgMCAxIDItMmg2Ij48L3BhdGg+PHBvbHlsaW5lIHBvaW50cz0iMTUgMyAyMSAzIDIxIDkiPjwvcG9seWxpbmU+PGxpbmUgeDE9IjEwIiB5MT0iMTQiIHgyPSIyMSIgeTI9IjMiPjwvbGluZT48L3N2Zz4=" /></a>

</div>

<div class="mt-4 rounded-lg border border-amber-500/30 bg-amber-500/5 px-4 py-3">

Breaking Change

Authentication was introduced in version **3.3.0**. If you are upgrading from an earlier version, any existing API integrations must be updated to include a bearer token.

</div>

<div class="mt-8 space-y-10 text-[15px] leading-relaxed">

<div class="section">

## Authentication

When <a href="authentication.html" class="text-primary underline">authentication</a> is enabled, most API endpoints require a valid session cookie or a bearer token in the `Authorization` header. Tokens are created in **Settings → API**.

Endpoints marked <span class="rounded-full bg-black px-2 py-0.5 text-[10px] font-semibold text-white dark:bg-white dark:text-black">PUBLIC</span> in the table below do not require authentication. These include the health check, authentication flow, and initial setup endpoints.

### Example: Authenticated Request

<div class="group relative mt-3">

<div class="overflow-hidden rounded-xl border border-border/60 bg-white dark:bg-[#0a0c10]">

<div class="flex items-center gap-1 border-b border-border/40 px-4 py-2.5">

cURL

JavaScript

</div>

<div class="flex items-center justify-between border-b border-border/40 px-4 py-2">

<div class="flex items-center gap-2 text-muted-foreground">

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLXRlcm1pbmFsIGgtMy41IHctMy41IiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHBhdGggZD0iTTEyIDE5aDgiPjwvcGF0aD48cGF0aCBkPSJtNCAxNyA2LTYtNi02Ij48L3BhdGg+PC9zdmc+" class="lucide lucide-terminal h-3.5 w-3.5" /><span class="text-xs">Terminal</span>

</div>

<img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNvcHkgaC0zLjUgdy0zLjUgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIiBhcmlhLWhpZGRlbj0idHJ1ZSI+PHJlY3Qgd2lkdGg9IjE0IiBoZWlnaHQ9IjE0IiB4PSI4IiB5PSI4IiByeD0iMiIgcnk9IjIiPjwvcmVjdD48cGF0aCBkPSJNNCAxNmMtMS4xIDAtMi0uOS0yLTJWNGMwLTEuMS45LTIgMi0yaDEwYzEuMSAwIDIgLjkgMiAyIj48L3BhdGg+PC9zdmc+" class="lucide lucide-copy h-3.5 w-3.5 text-muted-foreground" />

</div>

<div class="shiki-wrapper overflow-x-auto text-sm [&_pre]:!bg-[#fafafa] [&_pre]:!p-4 dark:[&_pre]:!bg-[#0a0c10] [&_code]:font-mono">

``` shiki
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
  https://your-host:8090/api/logs
```

</div>

</div>

</div>

</div>

<div class="section">

## Endpoints

<div class="mt-4 space-y-2">

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/logs`

</div>

Paginated log list with all filters (prefix any filter with ! to negate)

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/logs/aggregate`

</div>

Aggregate logs by dimension with CIDR grouping and HAVING thresholds

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/logs/{id}`

</div>

Single log detail with threat data

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/stats`

</div>

Dashboard aggregations (pass ?time_range=24h)

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/export`

</div>

CSV export with current filters (up to 100K rows)

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/health`<span class="rounded-full bg-black px-2 py-0.5 text-[10px] font-semibold text-white dark:bg-white dark:text-black">PUBLIC</span>

</div>

Health check with total count and latest timestamp

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/auth/status`<span class="rounded-full bg-black px-2 py-0.5 text-[10px] font-semibold text-white dark:bg-white dark:text-black">PUBLIC</span>

</div>

Current authentication state (logged in, auth enabled, setup complete)

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/auth/login`<span class="rounded-full bg-black px-2 py-0.5 text-[10px] font-semibold text-white dark:bg-white dark:text-black">PUBLIC</span>

</div>

Authenticate with username and password

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/auth/logout`<span class="rounded-full bg-black px-2 py-0.5 text-[10px] font-semibold text-white dark:bg-white dark:text-black">PUBLIC</span>

</div>

End the current session

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/auth/setup`<span class="rounded-full bg-black px-2 py-0.5 text-[10px] font-semibold text-white dark:bg-white dark:text-black">PUBLIC</span>

</div>

Create the first admin account (one-time)

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/setup/status`<span class="rounded-full bg-black px-2 py-0.5 text-[10px] font-semibold text-white dark:bg-white dark:text-black">PUBLIC</span>

</div>

Whether initial setup has been completed

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/services`

</div>

Distinct service names for filter dropdown

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/protocols`

</div>

Distinct protocols seen in logs

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/interfaces`

</div>

Distinct interfaces seen in logs

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/config`

</div>

Current system configuration (WAN, labels, setup status)

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/setup/complete`

</div>

Save wizard configuration

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/setup/wan-candidates`

</div>

Auto-detected WAN interface candidates

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/setup/network-segments`

</div>

Discovered network segments with suggested labels

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/enrich/{ip}`

</div>

Force fresh AbuseIPDB lookup for an IP

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/settings/unifi`

</div>

Current UniFi API settings

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-yellow-500/15 text-yellow-600 dark:text-yellow-400">PUT</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/settings/unifi`

</div>

Update UniFi API settings

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/settings/unifi/test`

</div>

Test UniFi connection and save on success

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/settings/ui`

</div>

Current UI display preferences

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-yellow-500/15 text-yellow-600 dark:text-yellow-400">PUT</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/settings/ui`

</div>

Update UI display preferences

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/firewall/policies`

</div>

All firewall policies with zone data

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-orange-500/15 text-orange-600 dark:text-orange-400">PATCH</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/firewall/policies/{id}`

</div>

Toggle syslog on a firewall policy

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/firewall/policies/bulk-logging`

</div>

Bulk-toggle syslog on multiple policies

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/unifi/clients`

</div>

Cached UniFi client list

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/unifi/devices`

</div>

Cached UniFi infrastructure devices

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/unifi/status`

</div>

UniFi polling status

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/config/export`

</div>

Export all settings as JSON

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/config/import`

</div>

Import settings from JSON backup

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/config/vpn-networks`

</div>

Save VPN network configuration

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/config/retention`

</div>

Current retention configuration

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/config/retention`

</div>

Update retention settings

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/config/retention/cleanup`

</div>

Run retention cleanup immediately

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/threats`

</div>

Threat intelligence cache with IP/date filters

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/threats/geo`

</div>

Geo-aggregated threat data for Threat Map (GeoJSON)

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/logs/batch`

</div>

Fetch multiple logs by ID (max 50)

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/mcp`

</div>

MCP JSON-RPC endpoint (bearer token required)

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/mcp`

</div>

MCP SSE streaming endpoint (bearer token required)

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/settings/mcp`

</div>

MCP server settings

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-yellow-500/15 text-yellow-600 dark:text-yellow-400">PUT</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/settings/mcp`

</div>

Update MCP settings

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/tokens`

</div>

List API tokens (filter by client_type: mcp, extension, api)

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-blue-500/15 text-blue-600 dark:text-blue-400">POST</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/tokens`

</div>

Create a new API token

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-red-500/15 text-red-600 dark:text-red-400">DELETE</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/tokens/{id}`

</div>

Revoke an API token

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/settings/mcp/scopes`

</div>

List available permission scopes

</div>

</div>

<div class="flex items-start gap-3 rounded-lg border border-border/40 px-3 py-2.5">

<span class="mt-0.5 shrink-0 rounded px-1.5 py-0.5 font-mono text-[10px] font-bold bg-green-500/15 text-green-600 dark:text-green-400">GET</span>

<div class="min-w-0 flex-1">

<div class="flex items-center gap-2">

`/api/settings/mcp/audit`

</div>

MCP audit trail with pagination

</div>

</div>

</div>

</div>

</div>

<div class="mt-12 flex items-center justify-between border-t border-border/50 pt-6">

<a href="dns-logging.html" class="group flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"><img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoZXZyb24tbGVmdCBoLTQgdy00IHRyYW5zaXRpb24tdHJhbnNmb3JtIGdyb3VwLWhvdmVyOi10cmFuc2xhdGUteC0wLjUiIGFyaWEtaGlkZGVuPSJ0cnVlIj48cGF0aCBkPSJtMTUgMTgtNi02IDYtNiI+PC9wYXRoPjwvc3ZnPg==" class="lucide lucide-chevron-left h-4 w-4 transition-transform group-hover:-translate-x-0.5" /><span>DNS Logging</span></a><a href="unraid.html" class="group flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"><span>Unraid Setup</span><img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld2JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWNoZXZyb24tcmlnaHQgaC00IHctNCB0cmFuc2l0aW9uLXRyYW5zZm9ybSBncm91cC1ob3Zlcjp0cmFuc2xhdGUteC0wLjUiIGFyaWEtaGlkZGVuPSJ0cnVlIj48cGF0aCBkPSJtOSAxOCA2LTYtNi02Ij48L3BhdGg+PC9zdmc+" class="lucide lucide-chevron-right h-4 w-4 transition-transform group-hover:translate-x-0.5" /></a>

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
