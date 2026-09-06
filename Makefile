# Convenience targets for local development.
# These wrap on-demand tooling; nothing here runs in CI.

.PHONY: security-scan

## security-scan: Run OpenAI Codex Security locally against the repo (needs OPENAI_API_KEY).
## Usage: make security-scan [ARGS="receiver --provider openrouter --model ..."]
security-scan:
	@./scripts/security-scan.sh $(ARGS)
