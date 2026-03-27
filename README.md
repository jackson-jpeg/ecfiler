# ECFiler

Automated document filing for Federal CM/ECF court systems, powered by Claude API.

ECFiler is the first open-source tool for filing documents on CM/ECF. It uses Playwright browser automation (CM/ECF has no filing API) with Claude AI for intelligent event code selection, redaction scanning, and filing validation. Every filing requires explicit attorney confirmation before submission.

## Features

- **Smart Filing** — drop a PDF, AI extracts case, court, party, event type. Zero form-filling.
- **150 federal courts** — 94 district, 43 bankruptcy, 13 appellate
- **7 safety gates** — PDF validation, redaction scan, event code verification, completeness check, attorney CONFIRM, final submit watchdog, receipt capture
- **Web UI + CLI + API** — three interfaces, same engine
- **Claude AI** — document analysis, event code matching, redaction scanning, filing validation
- **Filing history** — SQLite audit log of all filings

## Quick Start

### Option A: Web UI (recommended)

```bash
git clone <repo-url> && cd ecfiler
export ANTHROPIC_API_KEY=sk-ant-...

# With Docker
docker compose up

# Or without Docker
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[web,dev]"
ecfiler serve
```

Open http://localhost:8000 — drop a PDF and go.

### Option B: Smart CLI

```bash
# One command — AI reads the document, you just confirm
ecfiler smart ./motion_to_dismiss.pdf
```

### Option C: Interactive TUI

```bash
ecfiler                              # Interactive menu
ecfiler --dry-run                    # Test without filing
ecfiler courts --search california   # Find courts
ecfiler validate brief.pdf           # Check a PDF
ecfiler demo                         # Demo walkthrough
```

## Setup

### 1. PACER Credentials

ECFiler stores your PACER password in your system keyring (never in plaintext):

```
$ python -m ecfiler
> [4] Setup Credentials
> PACER username: your@email.com
> PACER password: ********
```

### 2. Configuration

Edit `~/.ecfiler/config.toml` (created on first run):

```toml
[general]
default_court = "nysd"
claude_model = "claude-sonnet-4-20250514"
dry_run = false

[pacer]
username = "your@email.com"

[attorney]
name = "Jane Smith"
bar_number = "JS1234"

[pdf]
redaction_check = true
```

### 3. Optional: PDF/A Conversion

For PDF/A conversion and OCR support:

```bash
pip install 'ecfiler[pdf-convert]'
apt install ghostscript tesseract-ocr  # Linux
brew install ghostscript tesseract     # macOS
```

## How It Works

1. **Select court** — choose from 150 federal courts
2. **Enter case number** — looked up on PACER
3. **Describe your filing** — Claude suggests the right event code
4. **Select documents** — PDF validation + redaction scanning
5. **Review** — full summary, type CONFIRM to proceed
6. **File** — Playwright submits to CM/ECF, captures receipt

## Safety

ECFiler never auto-submits. The attorney must:
- Type `CONFIRM` at the review screen
- Type `YES` at the final CM/ECF confirmation
- Both gates must pass for any filing to be submitted

Additional protections:
- PDF validation blocks invalid documents
- Claude scans for unredacted personal identifiers (Rule 5.2)
- Claude validates event code matches document content
- All filings logged to SQLite audit trail
- Screenshots captured at every step
- Playwright traces saved for debugging

## Supported Courts

| Type | Count | Examples |
|------|-------|---------|
| District | 94 | S.D.N.Y. (`nysd`), C.D. Cal. (`cacd`), N.D. Ill. (`ilnd`) |
| Bankruptcy | 43 | S.D.N.Y. (`nysb`), C.D. Cal. (`cacb`), D. Del. (`deb`) |
| Appellate | 13 | 2nd Cir. (`ca2`), 9th Cir. (`ca9`), D.C. Cir. (`cadc`) |

## Development

```bash
# Run tests
python -m pytest tests/ -v

# Run a specific test
python -m pytest tests/test_pdf_validator.py -v
```

## License

MIT
