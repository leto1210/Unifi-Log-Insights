#!/usr/bin/env bash
#
# security-scan.sh — Run OpenAI Codex Security locally against this repository.
#
# Uses openai/codex-security (https://github.com/openai/codex-security) to find,
# validate, and (optionally) fix security vulnerabilities. This is a LOCAL,
# on-demand tool: it is not wired into CI and never runs automatically.
#
# Requirements:
#   - Node.js >= 22.13 (codex-security requirement; run `node -v` to check)
#   - Python  >= 3.10  (already required by the receiver)
#   - An OpenAI API key in OPENAI_API_KEY (paid OpenAI service).
#     Loaded from the environment, or from a local .env file if present.
#
# Usage:
#   ./scripts/security-scan.sh                 # scan the whole repo
#   ./scripts/security-scan.sh receiver        # scan a subdirectory
#   ./scripts/security-scan.sh receiver ui     # scan several targets
#
# Extra flags are forwarded to `codex-security scan`, e.g.:
#   ./scripts/security-scan.sh . --provider openrouter --model anthropic/claude-sonnet-4.5
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Load OPENAI_API_KEY (and friends) from .env if present, without clobbering
# variables already set in the environment.
if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source ./.env
  set +a
fi

# Auth is optional here: codex-security can either use a key from the
# environment (best for CI) OR an interactive sign-in session created with
# `npx @openai/codex-security login` — which authenticates with your ChatGPT /
# OpenAI account and needs no API key. If neither is present we still proceed
# and let the CLI prompt/report, but we print a hint first.
if [[ -z "${OPENAI_API_KEY:-}" && -z "${CODEX_SECURITY_PROVIDER_KEY:-}" ]]; then
  echo "note: no OPENAI_API_KEY set — relying on an existing 'codex-security login' session." >&2
  echo "      If you are not signed in yet, run:  npx @openai/codex-security login" >&2
  echo "      (For CI, set OPENAI_API_KEY instead. Other providers: pass --provider/--model.)" >&2
  echo >&2
fi

# Targets: everything after the script name that is not a flag becomes a scan
# target; flags (starting with '-') are forwarded verbatim. Default target: '.'.
TARGETS=()
FORWARD=()
for arg in "$@"; do
  if [[ "$arg" == -* ]]; then
    FORWARD+=("$arg")
  else
    TARGETS+=("$arg")
  fi
done
if [[ ${#TARGETS[@]} -eq 0 ]]; then
  TARGETS=(".")
fi

OUT_DIR="$REPO_ROOT/.security-scan"
mkdir -p "$OUT_DIR"

echo "==> Codex Security scan"
echo "    repo:    $REPO_ROOT"
echo "    targets: ${TARGETS[*]}"
echo "    output:  $OUT_DIR/"
echo

# npx --yes fetches the published CLI on demand: no dependency is added to the
# repo, and nothing is committed under node_modules.
# Note: guard empty-array expansion for bash 3.2 (macOS default), where
# "${arr[@]}" on an empty array trips `set -u` ("unbound variable").
npx --yes @openai/codex-security@latest scan \
  "${TARGETS[@]}" \
  ${FORWARD[@]+"${FORWARD[@]}"}

echo
echo "==> Scan complete. Findings/report written by codex-security (see output above)."
echo "    Any local artifacts under .security-scan/ are git-ignored."
