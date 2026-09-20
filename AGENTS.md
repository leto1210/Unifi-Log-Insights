# Repository Guidelines

## Project Structure & Module Organization

`receiver/` contains the Python backend, syslog receiver, parsers, enrichment jobs, API routes, and PostgreSQL access. Keep endpoints in `receiver/routes/`, database logic in `receiver/db/`, services in `receiver/service/`, and UniFi client code in `receiver/unifi/`. Backend tests live in `receiver/tests/`, with performance and MCP smoke subdirectories.

`ui/` is the React/Vite frontend. Put views in `ui/src/components/`, hooks in `ui/src/hooks/`, helpers in `ui/src/lib/`, tests in `ui/src/__tests__/`, and static files in `ui/public/`. Root files define Docker deployment and database initialization. Documentation and screenshots belong in `docs/`. `extension/` is archived; change it only for extension-specific work.

## Build, Test, and Development Commands

- `cd ui && npm ci && npm run dev` installs pinned frontend dependencies and starts Vite.
- `cd ui && npm test` runs Vitest once; `npm run test:watch` supports local iteration.
- `cd ui && npm run build` creates the production UI bundle in `ui/dist/`.
- `python3 -m venv .venv && . .venv/bin/activate` creates a local Python environment.
- `pip install -r receiver/requirements.txt -r receiver/requirements-test.txt` installs backend and test dependencies.
- `cd receiver && pytest tests/ -v --tb=short` matches backend CI.
- `docker build -t unifi-log-insights .` verifies the complete production image.

## Coding Style & Naming Conventions

Use four spaces and `snake_case` for Python functions/modules; use `PascalCase` for React components and `camelCase` for JavaScript helpers and hooks (`useTimeRange`). Follow surrounding quote and semicolon style—frontend files use two-space indentation and generally omit semicolons. Keep changes focused and preserve package boundaries. Add accurate docstrings as the first statement of Python modules, classes, and functions; modified Python files should retain at least 80% docstring coverage.

## Integration enable/disable flags

Each external integration (UniFi, Pi-hole, AdGuard Home, AbuseIPDB) has an `<integration>_enabled` flag stored in the `system_config` table and resolved with the precedence **env var > DB value > default** (e.g. `ABUSEIPDB_ENABLED` overrides the stored `abuseipdb_enabled`). This flag is the runtime kill-switch surfaced in Settings, and **every code path that touches the integration must respect it**, not just the poller:

- **Pollers / background tasks** gate their loop on the flag and re-read it on `reload_config()` (SIGUSR2).
- **On-demand outbound routes** return `409 {"detail": "integration disabled"}` when the flag is off (distinct from `400` when the integration was never configured).
- **Widgets, stats, and any read path** that surfaces integration-sourced data must gate on the same flag rather than querying the underlying table blindly. A widget that reads the data directly (as the old `_query_top_dns` did against `logs.log_type='dns'` while ignoring `adguard_enabled`/`pihole_enabled`) is a bug: it keeps showing data from an integration the user has turned off.

When adding a new integration or a new surface for an existing one, wire it to the flag on both the write path (poller/outbound calls) and the read path (widgets/stats), and add regression coverage for the disabled state. The user-facing behaviour is documented under "Enabling / disabling integrations" in the Configuration wiki.

## Performance & shared utilities

The `logs` table is large (tens of millions of rows). Treat it accordingly:

- **Response caching:** there is ONE TTL cache decorator, `ttl_cache` in `receiver/response_cache.py` (dependency-free so it stays unit-testable; re-exported by `deps` and `routes._response_cache`). Use `@ttl_cache(ttl=<seconds>)` on expensive read-only handlers — it keys on the call args and deep-copies on read. Do not add a second cache implementation.
- **No `COUNT(*)` on hot paths.** A full `SELECT COUNT(*) FROM logs …` costs ~1 s and must never sit behind a per-page-load endpoint (this is what slowed `/api/auth/status` — it called `setup_status()` for a `logs_count` it discarded). Read a config flag, use `EXISTS`, or `pg_class.reltuples` estimates instead of counting.
- **`statement_timeout`:** the pool caps queries at 30 s. For a genuinely heavy handler, raise it per-transaction with `SET LOCAL statement_timeout = '90s'` (scoped to the txn, so pooled connections revert after commit) rather than lifting the pool-wide default.
- **Self-signed integration TLS:** clients that talk to self-signed hosts (UniFi controllers, Pi-hole) suppress `InsecureRequestWarning` once, unconditionally, at module import (`urllib3.disable_warnings(...)`). Do not toggle that warning per-instance in config-reload code — global-filter flips fight the other clients' disable and leak the warning into the logs.

## Testing Guidelines

Name backend tests `test_*.py` and frontend tests `*.test.js` or `*.test.jsx`. Add regression coverage near the affected module, including failure paths for database, authentication, and external-service changes. Run both suites when an API contract affects the UI. Syntax-check every changed Python file before submission, for example: `python3 -c "import ast; ast.parse(open('receiver/parsers.py').read())"`.

## Commit & Pull Request Guidelines

Recent history follows Conventional Commits: `fix(security): ...`, `refactor(db): ...`, and `docs(wiki): ...`. Use an imperative, scoped subject and keep unrelated work separate. Pull requests should explain the problem and solution, link relevant issues, list verification performed, and include screenshots for visible UI changes. Document new environment variables in `.env.example` and the wiki. Never commit API keys, passwords, production logs, or real network identifiers.
