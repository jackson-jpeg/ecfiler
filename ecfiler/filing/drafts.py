"""Draft filing persistence — save incomplete filings and resume later.

Attorneys often prepare filings in stages: validate PDFs one day,
select the event code later, then file when ready. Drafts let them
save progress at any point and resume without re-entering data.

Stored as JSON files at ~/.ecfiler/drafts/.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ecfiler.config import CONFIG_DIR
from ecfiler.logging import get_logger

logger = get_logger(__name__)

DRAFTS_DIR = CONFIG_DIR / "drafts"


def _ensure_dir() -> None:
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)


def save_draft(name: str, filing_data: dict, overwrite: bool = False) -> Path:
    """Save a filing draft.

    Args:
        name: Draft name (used as filename)
        filing_data: Serialized filing data (from Filing.model_dump())
        overwrite: Whether to overwrite an existing draft

    Returns:
        Path to the saved draft file
    """
    _ensure_dir()
    safe_name = _sanitize(name)
    path = DRAFTS_DIR / f"{safe_name}.json"

    if path.exists() and not overwrite:
        # Append timestamp to avoid overwriting
        ts = datetime.now().strftime("%H%M%S")
        path = DRAFTS_DIR / f"{safe_name}_{ts}.json"

    envelope = {
        "name": name,
        "saved_at": datetime.now().isoformat(),
        "filing": filing_data,
    }

    path.write_text(json.dumps(envelope, indent=2, default=str))
    logger.info("Draft saved: %s → %s", name, path)
    return path


def load_draft(name: str) -> dict | None:
    """Load a draft by name.

    Returns the filing data dict, or None if not found.
    """
    _ensure_dir()
    safe_name = _sanitize(name)
    path = DRAFTS_DIR / f"{safe_name}.json"

    if not path.exists():
        return None

    try:
        envelope = json.loads(path.read_text())
        return envelope.get("filing")
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("Failed to load draft %s: %s", name, e)
        return None


def list_drafts() -> list[dict[str, str]]:
    """List all saved drafts.

    Returns list of {"name": ..., "saved_at": ..., "court": ..., "case": ...}
    """
    _ensure_dir()
    drafts = []
    for path in sorted(DRAFTS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            envelope = json.loads(path.read_text())
            filing = envelope.get("filing", {})
            drafts.append({
                "name": envelope.get("name", path.stem),
                "file": path.stem,
                "saved_at": envelope.get("saved_at", ""),
                "court": filing.get("court_id", ""),
                "case": filing.get("case", {}).get("case_number", "") if isinstance(filing.get("case"), dict) else "",
                "event": filing.get("event", {}).get("description", "") if isinstance(filing.get("event"), dict) else "",
            })
        except Exception:
            continue
    return drafts


def delete_draft(name: str) -> bool:
    """Delete a draft. Returns True if it existed."""
    safe_name = _sanitize(name)
    path = DRAFTS_DIR / f"{safe_name}.json"
    if path.exists():
        path.unlink()
        logger.info("Draft deleted: %s", name)
        return True
    return False


def _sanitize(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
