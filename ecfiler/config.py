"""Configuration loading and management for ECFiler."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# Use ECFILER_DATA_DIR env var if set (for persistent storage on Railway/Docker)
# Falls back to ~/.ecfiler for local development
CONFIG_DIR = Path(os.environ.get("ECFILER_DATA_DIR", str(Path.home() / ".ecfiler")))
CONFIG_FILE = CONFIG_DIR / "config.toml"
RECEIPTS_DIR = CONFIG_DIR / "receipts"
DOCUMENTS_DIR = CONFIG_DIR / "documents"
DB_PATH = CONFIG_DIR / "history.db"

DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-20250514"


@dataclass
class PacerConfig:
    username: str = ""
    # Password stored in keyring, not config file

    @property
    def has_credentials(self) -> bool:
        return bool(self.username)


@dataclass
class AttorneyConfig:
    name: str = ""
    bar_number: str = ""
    firm: str = ""
    email: str = ""


@dataclass
class PdfConfig:
    auto_convert_pdfa: bool = False
    max_file_size_mb: int = 100
    redaction_check: bool = True


@dataclass
class GeneralConfig:
    default_court: str = ""
    claude_model: str = DEFAULT_CLAUDE_MODEL
    dry_run: bool = False
    screenshot_on_every_step: bool = True


@dataclass
class AppConfig:
    general: GeneralConfig = field(default_factory=GeneralConfig)
    pacer: PacerConfig = field(default_factory=PacerConfig)
    attorney: AttorneyConfig = field(default_factory=AttorneyConfig)
    pdf: PdfConfig = field(default_factory=PdfConfig)

    @property
    def claude_api_key(self) -> str:
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            raise ConfigError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Export it or add it to your shell profile."
            )
        return key


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""


def ensure_dirs() -> None:
    """Create ECFiler directories if they don't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


def load_config(config_path: str | None = None) -> AppConfig:
    """Load configuration from TOML file.

    Falls back to defaults if no config file exists.
    Creates a template config on first run.
    """
    ensure_dirs()

    path = Path(config_path) if config_path else CONFIG_FILE

    if not path.exists():
        _create_default_config(path)
        return AppConfig()

    with open(path, "rb") as f:
        raw = tomllib.load(f)

    cfg = _parse_config(raw)
    _validate_config(cfg)
    return cfg


def _validate_config(cfg: AppConfig) -> None:
    """Validate configuration values. Warns on issues, raises on critical errors."""
    import sys

    if cfg.pdf.max_file_size_mb <= 0:
        print("Warning: max_file_size_mb must be positive, using default 100", file=sys.stderr)
        cfg.pdf.max_file_size_mb = 100

    if cfg.pdf.max_file_size_mb > 100:
        print(
            f"Warning: max_file_size_mb={cfg.pdf.max_file_size_mb} exceeds CM/ECF 100MB limit",
            file=sys.stderr,
        )

    valid_model_prefixes = ("claude-", "claude-")
    if cfg.general.claude_model and not cfg.general.claude_model.startswith("claude"):
        print(
            f"Warning: claude_model '{cfg.general.claude_model}' doesn't look like a Claude model ID",
            file=sys.stderr,
        )


def _parse_config(raw: dict) -> AppConfig:
    """Parse raw TOML dict into AppConfig."""
    cfg = AppConfig()

    if g := raw.get("general"):
        cfg.general = GeneralConfig(
            default_court=g.get("default_court", ""),
            claude_model=g.get("claude_model", DEFAULT_CLAUDE_MODEL),
            dry_run=g.get("dry_run", False),
            screenshot_on_every_step=g.get("screenshot_on_every_step", True),
        )

    if p := raw.get("pacer"):
        cfg.pacer = PacerConfig(username=p.get("username", ""))

    if a := raw.get("attorney"):
        cfg.attorney = AttorneyConfig(
            name=a.get("name", ""),
            bar_number=a.get("bar_number", ""),
            firm=a.get("firm", ""),
            email=a.get("email", ""),
        )

    if pdf := raw.get("pdf"):
        cfg.pdf = PdfConfig(
            auto_convert_pdfa=pdf.get("auto_convert_pdfa", False),
            max_file_size_mb=pdf.get("max_file_size_mb", 100),
            redaction_check=pdf.get("redaction_check", True),
        )

    return cfg


def _create_default_config(path: Path) -> None:
    """Write a template config file for first-time setup."""
    template = """\
# ECFiler Configuration
# See: https://github.com/ecfiler/ecfiler for documentation

[general]
# default_court = "nysd"          # Court ID (e.g., nysd, cacd, txsd)
# claude_model = "claude-sonnet-4-20250514"
# dry_run = false                  # true = stop before final submit
# screenshot_on_every_step = true

[pacer]
# username = "your@email.com"
# Password is stored in your system keyring. Run: ecfiler setup-credentials

[attorney]
# name = "Jane Smith"
# bar_number = "JS1234"
# firm = "Smith & Associates"
# email = "jane@smithlaw.com"

[pdf]
# auto_convert_pdfa = false
# max_file_size_mb = 100
# redaction_check = true
"""
    path.write_text(template)
