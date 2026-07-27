"""Centralized logging configuration for ECFiler.

All modules should use:
    from ecfiler.logging import get_logger
    logger = get_logger(__name__)

Logs go to both stderr (for TUI) and a rotating file at ~/.ecfiler/ecfiler.log.
"""

from __future__ import annotations

import logging
import re
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from ecfiler.config import CONFIG_DIR

LOG_FILE = CONFIG_DIR / "ecfiler.log"
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 3

_initialized = False


class TokenRedactionFilter(logging.Filter):
    """Redact PACER CSO tokens from every log record.

    Applied to all handlers so a partially-logged token (the bug this
    replaces) cannot recur anywhere in the codebase.
    """

    TOKEN_RE = re.compile(
        r"((?:csession=|nextGenCSO[=:\s\"']*|NextGenCSO[=:\s\"']*))"
        r"[A-Za-z0-9+/=_\-]{16,}"
    )

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        redacted = self.TOKEN_RE.sub(r"\1[REDACTED]", message)
        if redacted != message:
            record.msg = redacted
            record.args = None
        return True


def _init_logging(level: int = logging.INFO) -> None:
    """Initialize logging on first call."""
    global _initialized
    if _initialized:
        return
    _initialized = True

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("ecfiler")
    root.setLevel(level)

    # Handler-level filters catch records from every ecfiler.* child logger
    # (logger-level filters would only see records logged on the root itself).
    redaction = TokenRedactionFilter()

    # File handler — detailed logs for debugging
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    file_handler.addFilter(redaction)
    root.addHandler(file_handler)

    # Stderr handler — only warnings and errors (TUI uses Rich for normal output)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    stderr_handler.addFilter(redaction)
    root.addHandler(stderr_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the given module name.

    Args:
        name: Module name, typically __name__

    Returns:
        Configured logger
    """
    _init_logging()
    return logging.getLogger(name)
