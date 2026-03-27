# Contributing to ECFiler

ECFiler is focused on one thing: filing documents on Federal CM/ECF. Contributions that improve the core filing experience are welcome.

## Scope

**In scope:** Anything that makes CM/ECF filing more reliable, faster, or easier.

**Out of scope:** Case management, deadline tracking, docket monitoring, billing, or anything not directly related to the act of filing a document on CM/ECF.

## Development Setup

```bash
git clone <repo-url> && cd ecfiler
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,web]"
playwright install chromium
export ANTHROPIC_API_KEY=sk-ant-...

# Verify setup
ecfiler check

# Run tests
python -m pytest tests/ -v
```

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific module
python -m pytest tests/test_pdf_validator.py -v

# Quick summary
python -m pytest tests/ -q
```

Tests don't require PACER credentials or a Claude API key — they use local fixtures and mock data.

## Project Structure

```
ecfiler/
├── agent/           # AI document analysis + smart filing
├── api/             # FastAPI backend + web UI
├── browser/         # Playwright CM/ECF automation + recovery
├── courts/          # Court profiles, selectors, registry, JSON data
├── filing/          # Models, events, workflow, preflight, civil cover sheet
├── pdf/             # Validation, conversion, redaction scanning
├── storage/         # SQLite history, filing templates
├── ui/              # Rich TUI menus and display
├── config.py        # TOML config loading
├── claude_client.py # Anthropic SDK wrapper
├── diagnostics.py   # Setup verification
├── logging.py       # Centralized logging
├── pacer_auth.py    # PACER authentication
└── pacer_search.py  # PACER case search
```

## Adding a New Court Profile

Most courts work with the default `BaseCourt` selectors. If a court needs overrides:

1. Add court-specific selectors to the court's JSON entry in `ecfiler/courts/data/`
2. If selectors aren't enough, add a Python override in the appropriate court type file (`district.py`, `bankruptcy.py`, `appellate.py`)
3. Test with `ecfiler check` and `ecfiler --dry-run`

## Adding Event Codes

Event codes are in `ecfiler/filing/events.py` (common codes) and `ecfiler/courts/data/event_codes/` (court-specific). To add:

1. Find the real CM/ECF event codes for the court (visible in the CM/ECF event dropdown)
2. Add to the appropriate JSON file or Python list
3. Include: code, description, category

## Code Style

- Python 3.11+, type hints everywhere
- No docstrings on obvious methods
- Tests for everything that can break
- `ecfiler.logging.get_logger(__name__)` for logging
- `ECFFormError` for CM/ECF form interaction failures
- Pydantic models for all data structures

## Before Submitting a PR

1. `python -m pytest tests/ -q` — all tests pass
2. `ecfiler check` — setup diagnostics pass
3. No scope creep — keep it about filing
