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

## Testing Guidelines

Name backend tests `test_*.py` and frontend tests `*.test.js` or `*.test.jsx`. Add regression coverage near the affected module, including failure paths for database, authentication, and external-service changes. Run both suites when an API contract affects the UI. Syntax-check every changed Python file before submission, for example: `python3 -c "import ast; ast.parse(open('receiver/parsers.py').read())"`.

## Commit & Pull Request Guidelines

Recent history follows Conventional Commits: `fix(security): ...`, `refactor(db): ...`, and `docs(wiki): ...`. Use an imperative, scoped subject and keep unrelated work separate. Pull requests should explain the problem and solution, link relevant issues, list verification performed, and include screenshots for visible UI changes. Document new environment variables in `.env.example` and the wiki. Never commit API keys, passwords, production logs, or real network identifiers.
