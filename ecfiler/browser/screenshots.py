"""Screenshot management for filing review and debugging."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console


def display_screenshot_path(console: Console, path: Path, label: str = "") -> None:
    """Display a screenshot path to the user for review.

    In a TUI environment, we show the path so the user can open it.
    """
    prefix = f"[{label}] " if label else ""
    console.print(f"  {prefix}Screenshot saved: [link=file://{path}]{path}[/link]")


def cleanup_screenshots(directory: Path, keep_latest: int = 50) -> None:
    """Remove old screenshots, keeping the most recent ones."""
    screenshots = sorted(directory.glob("*.png"), key=lambda p: p.stat().st_mtime)
    to_remove = screenshots[:-keep_latest] if len(screenshots) > keep_latest else []
    for path in to_remove:
        path.unlink(missing_ok=True)
