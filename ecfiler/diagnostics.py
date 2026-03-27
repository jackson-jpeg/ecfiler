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
    report.checks.append(_check_pacer_credentials(config_path))
    report.checks.append(_check_playwright())
    report.checks.append(_check_pdf_tools())
    report.checks.append(_check_ocrmypdf())
    report.checks.append(_check_courts_data())
    report.checks.append(_check_history_db())

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


def _check_courts_data() -> CheckResult:
    """Check court registry loads."""
    try:
        from ecfiler.courts.registry import CourtRegistry

        registry = CourtRegistry()
        return CheckResult("courts", True, f"{registry.count} courts loaded")
    except Exception as e:
        return CheckResult("courts", False, f"Court data error: {e}")


def _check_history_db() -> CheckResult:
    """Check filing history database."""
    try:
        from ecfiler.storage.history import FilingHistory

        history = FilingHistory()
        return CheckResult("history_db", True, f"History DB ready ({history.count} filings)")
    except Exception as e:
        return CheckResult("history_db", False, f"Database error: {e}")
