# ECFiler task entry points.
#
# qa-day — the NEF round-trip, collapsed to one command
#   [MAC] make qa-day                                 # dry run: mock court
#   [MAC] make qa-day MODE=live                       # preflight gates only
#   [MAC] make qa-day MODE=live STAGE=CODE TARGET=https://...
#                                                     # preflight, pull, attended filing
#
# TARGET is the QA/training CM/ECF base URL (recorded in
# docs/nef-roundtrip-runbook.md once established). Live mode refuses to
# start unless every precondition is green — see scripts/mac/qa-day.sh.

MODE ?= dry
STAGE ?=
TARGET ?=
SERVER ?=
DEVUSER ?=

.PHONY: qa-day test web-verify

qa-day:
	QA_STAGE=$(STAGE) QA_TARGET=$(TARGET) QA_SERVER=$(SERVER) QA_DEV_USER=$(DEVUSER) bash scripts/mac/qa-day.sh $(MODE)

test:
	.venv/bin/python -m pytest tests/ -q --ignore=tests/test_browser_e2e.py

web-verify:
	bash scripts/deploy/verify-web-anon.sh
