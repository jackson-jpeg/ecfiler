"""Filing templates — save and reuse common filing configurations."""

from __future__ import annotations

import json
from pathlib import Path

from ecfiler.config import CONFIG_DIR

TEMPLATES_DIR = CONFIG_DIR / "templates"


def ensure_templates_dir() -> None:
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


def save_template(name: str, data: dict) -> Path:
    """Save a filing template.

    Args:
        name: Template name (used as filename)
        data: Filing configuration to save

    Returns:
        Path to the saved template file
    """
    ensure_templates_dir()
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    path = TEMPLATES_DIR / f"{safe_name}.json"
    path.write_text(json.dumps(data, indent=2))
    return path


def load_template(name: str) -> dict | None:
    """Load a filing template by name."""
    ensure_templates_dir()
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    path = TEMPLATES_DIR / f"{safe_name}.json"
    if path.exists():
        return json.loads(path.read_text())
    return None


def list_templates() -> list[str]:
    """List all available template names."""
    ensure_templates_dir()
    return [p.stem for p in TEMPLATES_DIR.glob("*.json")]


def delete_template(name: str) -> bool:
    """Delete a template. Returns True if it existed."""
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    path = TEMPLATES_DIR / f"{safe_name}.json"
    if path.exists():
        path.unlink()
        return True
    return False
