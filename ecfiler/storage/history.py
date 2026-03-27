"""SQLite-based filing history and audit log.

Append-only log of all filing attempts for accountability and review.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ecfiler.config import DB_PATH
from ecfiler.filing.models import FilingReceipt

CREATE_TABLE = """\
CREATE TABLE IF NOT EXISTS filing_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    court_id TEXT NOT NULL,
    case_number TEXT NOT NULL,
    docket_number TEXT DEFAULT '',
    event_description TEXT DEFAULT '',
    status TEXT DEFAULT 'submitted',
    filed_at TEXT NOT NULL,
    confirmation_text TEXT DEFAULT '',
    receipt_path TEXT DEFAULT '',
    screenshot_path TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


class FilingHistory:
    """Manages the filing history database."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(CREATE_TABLE)
            conn.commit()

    def log_filing(self, receipt: FilingReceipt) -> int:
        """Log a filing to the history database.

        Returns the row ID of the new record.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """\
                INSERT INTO filing_history
                    (court_id, case_number, docket_number, event_description,
                     status, filed_at, confirmation_text, receipt_path, screenshot_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    receipt.court_id,
                    receipt.case_number,
                    receipt.docket_number,
                    receipt.event_description,
                    "submitted",
                    receipt.filed_at.isoformat(),
                    receipt.confirmation_text[:5000],
                    receipt.receipt_path,
                    receipt.screenshot_path,
                ),
            )
            conn.commit()
            return cursor.lastrowid or 0

    def get_recent(self, limit: int = 20) -> list[dict]:
        """Get recent filing history entries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """\
                SELECT * FROM filing_history
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]

    def show_recent(self, console: Console, limit: int = 20) -> None:
        """Display recent filing history in a Rich table."""
        entries = self.get_recent(limit)

        if not entries:
            console.print("\n  [dim]No filing history yet.[/dim]")
            return

        table = Table(title="Recent Filings", border_style="dim")
        table.add_column("#", style="bold", width=4)
        table.add_column("Date", width=12)
        table.add_column("Court", width=8)
        table.add_column("Case", width=16)
        table.add_column("Event")
        table.add_column("Status", width=10)

        for i, entry in enumerate(entries, 1):
            filed_at = entry.get("filed_at", "")
            if filed_at:
                try:
                    dt = datetime.fromisoformat(filed_at)
                    filed_at = dt.strftime("%Y-%m-%d")
                except ValueError:
                    pass

            status = entry.get("status", "unknown")
            status_style = "green" if status == "submitted" else "yellow"

            table.add_row(
                str(i),
                filed_at,
                entry.get("court_id", ""),
                entry.get("case_number", ""),
                entry.get("event_description", "")[:40],
                f"[{status_style}]{status}[/{status_style}]",
            )

        console.print(table)

    def search(self, query: str) -> list[dict]:
        """Search filing history by case number or event description."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """\
                SELECT * FROM filing_history
                WHERE case_number LIKE ? OR event_description LIKE ?
                ORDER BY created_at DESC
                LIMIT 50
                """,
                (f"%{query}%", f"%{query}%"),
            ).fetchall()
            return [dict(row) for row in rows]

    @property
    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT COUNT(*) FROM filing_history").fetchone()
            return row[0] if row else 0
