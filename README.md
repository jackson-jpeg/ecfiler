# ECFiler

Automated document filing for Federal CM/ECF court systems, powered by Claude API.

ECFiler is the first open-source tool for filing documents on CM/ECF. It uses Playwright browser automation (CM/ECF has no filing API) with Claude AI for intelligent event code selection, redaction scanning, and filing validation. Every filing requires explicit attorney confirmation before submission.

## Features

- **Smart Filing** — drop a PDF, AI extracts case, court, party, event type. Zero form-filling.
- **150 federal courts** — 94 district, 43 bankruptcy, 13 appellate
- **7 safety gates** — PDF validation, redaction scan, event code verification, completeness check, attorney CONFIRM, final submit watchdog, receipt capture
- **Web UI + CLI + API** — three interfaces, same engine
- **Claude AI** — document analysis, event code matching, redaction scanning, filing validation
- **Certificate of Service** — auto-generated with PDF export
- **Pre-flight checks** — catches errors before the browser even starts
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

### Option C: Full CLI

```bash
ecfiler                              # Interactive TUI menu
ecfiler smart motion.pdf             # AI-powered filing (zero forms)
ecfiler smart motion.pdf --dry-run   # Test without submitting
ecfiler validate brief.pdf           # Check PDF meets CM/ECF requirements
ecfiler convert scanned.pdf          # Convert to PDF/A with OCR
ecfiler courts --search california   # Find courts
ecfiler courts --type appellate      # List appellate courts
ecfiler setup                        # Store PACER credentials
ecfiler check                        # Verify setup (API key, browser, etc.)
ecfiler history                      # View past filings
ecfiler history --search "01234"     # Search filing history
ecfiler save-template mtd --court nysd --event-code 12 --event-desc "Motion to Dismiss"
ecfiler quick mtd 1:24-cv-01234 brief.pdf   # Quick file from template
ecfiler demo                         # Demo walkthrough (no account needed)
ecfiler serve                        # Start web UI + API server
ecfiler serve --port 8080            # Custom port
```

## Setup

### 1. Verify installation

```bash
ecfiler check
```

This runs diagnostics on your setup: config file, API key, PACER credentials, Playwright/Chromium, PDF tools, court data.

### 2. PACER Credentials

```bash
ecfiler setup
```

Stores your PACER password in the system keyring (never in plaintext).

### 3. Configuration

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

### 4. Optional: PDF/A Conversion

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
5. **Pre-flight checks** — catches errors before browser starts
6. **Review** — full summary, type CONFIRM to proceed
7. **File** — Playwright submits to CM/ECF, captures receipt

## Safety

ECFiler never auto-submits. The attorney must:
- Type `CONFIRM` at the review screen
- Type `YES` at the final CM/ECF confirmation
- Both gates must pass for any filing to be submitted

Additional protections:
- Pre-flight checks block filings with missing/invalid data
- PDF validation blocks invalid documents
- Claude scans for unredacted personal identifiers (Rule 5.2)
- Claude validates event code matches document content
- Sealed/restricted document warnings
- Browser retry with error recovery for transient failures
- All filings logged to SQLite audit trail
- Screenshots captured at every step

## API

Start the server with `ecfiler serve`, then visit http://localhost:8000/docs for interactive API documentation.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/api/file` | POST | Smart filing — upload PDF, get filing preview |
| `/api/file/multi` | POST | Multi-document smart filing |
| `/api/filing/submit` | POST | Submit to CM/ECF |
| `/api/validate` | POST | PDF validation |
| `/api/redaction-scan` | POST | Rule 5.2 scanning |
| `/api/certificate-of-service` | POST | Generate certificate of service |
| `/api/certificate-of-service/pdf` | POST | Download CoS as PDF |
| `/api/courts` | GET | List/search courts |
| `/api/courts/{id}/events` | GET | Event codes per court |
| `/api/nature-of-suit` | GET | JS-44 nature of suit codes |
| `/api/nature-of-suit/categories` | GET | NOS categories |
| `/api/history` | GET | Filing history |
| `/api/health` | GET | Health check |

## Supported Courts

| Type | Count | Examples |
|------|-------|---------|
| District | 94 | S.D.N.Y. (`nysd`), C.D. Cal. (`cacd`), N.D. Ill. (`ilnd`) |
| Bankruptcy | 43 | S.D.N.Y. (`nysb`), C.D. Cal. (`cacb`), D. Del. (`deb`) |
| Appellate | 13 | 2nd Cir. (`ca2`), 9th Cir. (`ca9`), D.C. Cir. (`cadc`) |

## Development

```bash
python -m pytest tests/ -v     # Run all 206 tests
ecfiler check                  # Verify dev setup
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT
