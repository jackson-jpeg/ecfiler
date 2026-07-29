# ECFiler task entry points.
#
# qa-day — the NEF round-trip, collapsed to one command
#   [MAC] make qa-day                       # dry run: mock court, end to end
#   [MAC] make qa-day MODE=live             # preflight gate only (no STAGE)
#   [MAC] make qa-day MODE=live STAGE=CODE  # preflight, pull, attended filing
#
# Live mode refuses to start unless every precondition is green — see
# scripts/mac/qa-day.sh and docs/nef-roundtrip-runbook.md.

MODE ?= dry
STAGE ?=

.PHONY: qa-day test web-verify

qa-day:
	bash scripts/mac/qa-day.sh $(MODE) $(STAGE)

test:
	.venv/bin/python -m pytest tests/ -q --ignore=tests/test_browser_e2e.py

web-verify:
	bash scripts/deploy/verify-web-anon.sh
