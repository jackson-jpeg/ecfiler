"""Setup diagnostics — verify ECFiler is correctly configured before filing.

Run with: ecfiler check
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field

from ecfiler.config import CONFIG_FILE, DB_PATH, AppConfig, load_config
from ecfiler.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    fix: str = ""


@dataclass
class DiagnosticReport:
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def required_passed(self) -> bool:
        """At minimum, API key and config must work."""
        return all(
            c.passed for c in self.checks if c.name in ("config", "anthropic_key")
        )

    @property
    def pass_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)

    @property
    def fail_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed)


def run_diagnostics(config_path: str | None = None) -> DiagnosticReport:
    """Run all diagnostic checks."""
    report = DiagnosticReport()

    report.checks.append(_check_config(config_path))
    report.checks.append(_check_anthropic_key())
    report.checks.append(_check_anthropic_connectivity())
    report.checks.append(_check_pacer_credentials(config_path))
    report.checks.append(_check_playwright())
    report.checks.append(_check_pdf_tools())
    report.checks.append(_check_ocrmypdf())
    report.checks.append(_check_system_deps())
    report.checks.append(_check_courts_data())
    report.checks.append(_check_event_codes())
    report.checks.append(_check_history_db())
    report.checks.append(_check_disk_space())
    report.checks.append(_check_encryption_key())

    return report


def _check_config(config_path: str | None) -> CheckResult:
    """Check that config file exists and is valid."""
    try:
        cfg = load_config(config_path)
        has_court = bool(cfg.general.default_court)
        has_attorney = bool(cfg.attorney.name)
        details = []
        if has_court:
            details.append(f"court={cfg.general.default_court}")
        if has_attorney:
            details.append(f"attorney={cfg.attorney.name}")
        msg = f"Config loaded ({', '.join(details)})" if details else "Config loaded (defaults)"
        return CheckResult("config", True, msg)
    except Exception as e:
        return CheckResult(
            "config",
            False,
            f"Config error: {e}",
            fix=f"Edit {CONFIG_FILE}",
        )


def _check_anthropic_key() -> CheckResult:
    """Check that ANTHROPIC_API_KEY is set."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        masked = key[:10] + "..." + key[-4:]
        return CheckResult("anthropic_key", True, f"API key set ({masked})")
    return CheckResult(
        "anthropic_key",
        False,
        "ANTHROPIC_API_KEY not set",
        fix="export ANTHROPIC_API_KEY=sk-ant-...",
    )


def _check_pacer_credentials(config_path: str | None) -> CheckResult:
    """Check that PACER credentials are stored."""
    try:
        cfg = load_config(config_path)
        if not cfg.pacer.username:
            return CheckResult(
                "pacer",
                False,
                "No PACER username configured",
                fix="Run: ecfiler setup",
            )

        import keyring

        password = keyring.get_password("ecfiler-pacer", cfg.pacer.username)
        if password:
            return CheckResult("pacer", True, f"PACER credentials stored for {cfg.pacer.username}")
        else:
            return CheckResult(
                "pacer",
                False,
                f"Username set ({cfg.pacer.username}) but no password in keyring",
                fix="Run: ecfiler setup",
            )
    except Exception as e:
        return CheckResult("pacer", False, f"Keyring error: {e}", fix="Run: ecfiler setup")


def _check_playwright() -> CheckResult:
    """Check that Playwright and Chromium are installed."""
    try:
        from playwright.sync_api import sync_playwright

        pw = sync_playwright().start()
        try:
            browser = pw.chromium.launch(headless=True, timeout=10_000)
            version = browser.version
            browser.close()
            pw.stop()
            return CheckResult("playwright", True, f"Chromium {version} ready")
        except Exception as e:
            pw.stop()
            return CheckResult(
                "playwright",
                False,
                f"Chromium not available: {e}",
                fix="Run: playwright install chromium",
            )
    except ImportError:
        return CheckResult(
            "playwright",
            False,
            "Playwright not installed",
            fix="pip install playwright && playwright install chromium",
        )


def _check_pdf_tools() -> CheckResult:
    """Check PDF processing libraries."""
    issues = []
    try:
        import pikepdf  # noqa: F401
    except ImportError:
        issues.append("pikepdf")
    try:
        import fitz  # noqa: F401
    except ImportError:
        issues.append("PyMuPDF")

    if issues:
        return CheckResult(
            "pdf_tools",
            False,
            f"Missing: {', '.join(issues)}",
            fix=f"pip install {' '.join(issues)}",
        )
    return CheckResult("pdf_tools", True, "pikepdf + PyMuPDF installed")


def _check_ocrmypdf() -> CheckResult:
    """Check optional OCR/PDF-A conversion."""
    if shutil.which("ocrmypdf"):
        return CheckResult("ocrmypdf", True, "ocrmypdf available (PDF/A conversion ready)")
    return CheckResult(
        "ocrmypdf",
        False,
        "ocrmypdf not installed (optional — needed for PDF/A conversion)",
        fix="pip install 'ecfiler[pdf-convert]' && apt install ghostscript tesseract-ocr",
    )


def _check_anthropic_connectivity() -> CheckResult:
    """Check that the Claude API is reachable (quick model list call)."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return CheckResult("anthropic_api", False, "Skipped — no API key", fix="Set ANTHROPIC_API_KEY first")
    try:
        import httpx

        resp = httpx.get(
            "https://api.anthropic.com/v1/models",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
            timeout=10,
        )
        if resp.status_code == 200:
            return CheckResult("anthropic_api", True, "Claude API reachable")
        return CheckResult(
            "anthropic_api", False, f"API returned {resp.status_code}",
            fix="Check your ANTHROPIC_API_KEY is valid",
        )
    except Exception as e:
        return CheckResult("anthropic_api", False, f"Cannot reach API: {e}", fix="Check network connectivity")


def _check_system_deps() -> CheckResult:
    """Check required system-level dependencies."""
    missing = []
    if not shutil.which("ghostscript") and not shutil.which("gs"):
        missing.append("ghostscript")
    if not shutil.which("tesseract"):
        missing.append("tesseract-ocr")
    if missing:
        return CheckResult(
            "system_deps", False, f"Missing: {', '.join(missing)}",
            fix=f"apt install {' '.join(missing)}",
        )
    return CheckResult("system_deps", True, "ghostscript + tesseract installed")


def _check_courts_data() -> CheckResult:
    """Check court registry loads."""
    try:
        from ecfiler.courts.registry import CourtRegistry

        registry = CourtRegistry()
        return CheckResult("courts", True, f"{registry.count} courts loaded")
    except Exception as e:
        return CheckResult("courts", False, f"Court data error: {e}")


def _check_event_codes() -> CheckResult:
    """Check that event code JSON files are valid and loaded."""
    import json
    from pathlib import Path

    codes_dir = Path(__file__).parent / "courts" / "data" / "event_codes"
    total = 0
    errors = []
    for name in ["common_district.json", "common_bankruptcy.json", "common_appellate.json"]:
        path = codes_dir / name
        if not path.exists():
            errors.append(f"{name}: missing")
            continue
        try:
            with open(path) as f:
                data = json.load(f)
            count = sum(len(codes) for codes in data.get("categories", {}).values())
            total += count
        except Exception as e:
            errors.append(f"{name}: {e}")

    if errors:
        return CheckResult("event_codes", False, "; ".join(errors))
    return CheckResult("event_codes", True, f"{total} event codes across 3 court types")


def _check_history_db() -> CheckResult:
    """Check filing history database."""
    try:
        from ecfiler.storage.history import FilingHistory

        history = FilingHistory()
        return CheckResult("history_db", True, f"History DB ready ({history.count} filings)")
    except Exception as e:
        return CheckResult("history_db", False, f"Database error: {e}")


def _check_disk_space() -> CheckResult:
    """Check available disk space for temp files and PDF storage."""
    try:
        stat = os.statvfs(os.path.expanduser("~"))
        free_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
        if free_mb < 100:
            return CheckResult(
                "disk_space", False, f"Low disk space: {free_mb:.0f}MB free",
                fix="Free up disk space — filing requires temp files for PDF processing",
            )
        return CheckResult("disk_space", True, f"{free_mb:.0f}MB free")
    except Exception as e:
        return CheckResult("disk_space", False, f"Cannot check disk space: {e}")


def _check_encryption_key() -> CheckResult:
    """Check that the encryption key is configured for credential storage."""
    key = os.environ.get("ECFILER_ENCRYPTION_KEY", "")
    if key:
        return CheckResult("encryption_key", True, "Encryption key set (PACER credential storage ready)")
    return CheckResult(
        "encryption_key", False, "ECFILER_ENCRYPTION_KEY not set",
        fix="export ECFILER_ENCRYPTION_KEY=$(python -c \"import secrets; print(secrets.token_urlsafe(32))\")",
    )
