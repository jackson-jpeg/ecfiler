"""SQLite-based filing history and audit log.

Append-only log of all filing attempts for accountability and review.
User-isolated: every record is tied to a user_id for multi-tenant safety.
PDFs are archived per-user, compressed after 30 days, sealed docs are never kept.
"""

from __future__ import annotations

import gzip
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from rich.console import Console
from rich.table import Table

from ecfiler.config import DB_PATH, DOCUMENTS_DIR
from ecfiler.filing.models import FilingReceipt

CREATE_TABLE = """\
CREATE TABLE IF NOT EXISTS filing_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT '',
    court_id TEXT NOT NULL,
    case_number TEXT NOT NULL,
    docket_number TEXT DEFAULT '',
    event_description TEXT DEFAULT '',
    status TEXT DEFAULT 'submitted',
    filed_at TEXT NOT NULL,
    confirmation_text TEXT DEFAULT '',
    receipt_path TEXT DEFAULT '',
    screenshot_path TEXT DEFAULT '',
    pdf_path TEXT DEFAULT '',
    pdf_compressed INTEGER DEFAULT 0,
    is_sealed INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

MIGRATE_STATEMENTS = [
    "ALTER TABLE filing_history ADD COLUMN user_id TEXT NOT NULL DEFAULT ''",
    "ALTER TABLE filing_history ADD COLUMN pdf_path TEXT DEFAULT ''",
    "ALTER TABLE filing_history ADD COLUMN pdf_compressed INTEGER DEFAULT 0",
    "ALTER TABLE filing_history ADD COLUMN is_sealed INTEGER DEFAULT 0",
]


class FilingHistory:
    """Manages the filing history database with user isolation."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(CREATE_TABLE)
            # Run migrations for existing databases
            for stmt in MIGRATE_STATEMENTS:
                try:
                    conn.execute(stmt)
                except sqlite3.OperationalError:
                    pass  # Column already exists
            conn.commit()

    def log_filing(
        self,
        receipt: FilingReceipt,
        user_id: str = "",
        is_sealed: bool = False,
    ) -> int:
        """Log a filing to the history database.

        Returns the row ID of the new record.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """\
                INSERT INTO filing_history
                    (user_id, court_id, case_number, docket_number, event_description,
                     status, filed_at, confirmation_text, receipt_path, screenshot_path,
                     pdf_path, is_sealed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    receipt.court_id,
                    receipt.case_number,
                    receipt.docket_number,
                    receipt.event_description,
                    "submitted",
                    receipt.filed_at.isoformat(),
                    receipt.confirmation_text[:5000],
                    receipt.receipt_path,
                    receipt.screenshot_path,
                    receipt.pdf_path,
                    1 if is_sealed else 0,
                ),
            )
            conn.commit()
            return cursor.lastrowid or 0

    def get_recent(self, limit: int = 20, user_id: str = "") -> list[dict]:
        """Get recent filing history entries for a specific user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if user_id:
                rows = conn.execute(
                    "SELECT * FROM filing_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                    (user_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM filing_history ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return [dict(row) for row in rows]

    def get_by_id(self, filing_id: int, user_id: str = "") -> dict | None:
        """Get a single filing by ID, optionally scoped to user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if user_id:
                row = conn.execute(
                    "SELECT * FROM filing_history WHERE id = ? AND user_id = ?",
                    (filing_id, user_id),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM filing_history WHERE id = ?",
                    (filing_id,),
                ).fetchone()
            return dict(row) if row else None

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

    def search(self, query: str, user_id: str = "") -> list[dict]:
        """Search filing history by case number or event description."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if user_id:
                rows = conn.execute(
                    """\
                    SELECT * FROM filing_history
                    WHERE user_id = ? AND (case_number LIKE ? OR event_description LIKE ? OR court_id LIKE ?)
                    ORDER BY created_at DESC LIMIT 50
                    """,
                    (user_id, f"%{query}%", f"%{query}%", f"%{query}%"),
                ).fetchall()
            else:
                rows = conn.execute(
                    """\
                    SELECT * FROM filing_history
                    WHERE case_number LIKE ? OR event_description LIKE ? OR court_id LIKE ?
                    ORDER BY created_at DESC LIMIT 50
                    """,
                    (f"%{query}%", f"%{query}%", f"%{query}%"),
                ).fetchall()
            return [dict(row) for row in rows]

    @property
    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT COUNT(*) FROM filing_history").fetchone()
            return row[0] if row else 0


# ── PDF Document Archive ────────────────────────────────────────────


def user_documents_dir(user_id: str) -> Path:
    """Get or create the documents directory for a specific user."""
    user_dir = DOCUMENTS_DIR / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def archive_filing_pdf(
    pdf_content: bytes,
    user_id: str,
    court_id: str,
    case_number: str,
    is_sealed: bool = False,
) -> str:
    """Archive a filed PDF to the user's document store.

    Sealed documents are NEVER stored — returns empty string.
    Returns the path to the archived PDF (relative to DOCUMENTS_DIR).
    """
    if is_sealed:
        return ""  # Legal requirement: never persist sealed documents

    if not user_id or not pdf_content:
        return ""

    user_dir = user_documents_dir(user_id)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_case = case_number.replace(":", "_").replace("/", "_").replace(" ", "_")
    filename = f"{timestamp}_{court_id}_{safe_case}.pdf"
    pdf_path = user_dir / filename
    pdf_path.write_bytes(pdf_content)

    return str(pdf_path.relative_to(DOCUMENTS_DIR))


def get_archived_pdf_path(relative_path: str) -> Path | None:
    """Resolve a relative PDF path to an absolute path. Returns None if not found."""
    if not relative_path:
        return None
    full_path = DOCUMENTS_DIR / relative_path
    # Also check for compressed version
    gz_path = Path(str(full_path) + ".gz")
    if gz_path.exists():
        return gz_path
    if full_path.exists():
        return full_path
    return None


def decompress_pdf(gz_path: Path) -> bytes:
    """Decompress a gzipped PDF and return the raw bytes."""
    with gzip.open(gz_path, "rb") as f:
        return f.read()


def compress_old_pdfs(days_old: int = 30) -> int:
    """Compress PDFs older than N days to save storage.

    Returns count of files compressed.
    """
    cutoff = datetime.now() - timedelta(days=days_old)
    compressed = 0

    for pdf_file in DOCUMENTS_DIR.rglob("*.pdf"):
        if pdf_file.stat().st_mtime < cutoff.timestamp():
            gz_path = Path(str(pdf_file) + ".gz")
            if gz_path.exists():
                continue  # Already compressed
            with open(pdf_file, "rb") as f_in:
                with gzip.open(gz_path, "wb", compresslevel=6) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            pdf_file.unlink()  # Remove the uncompressed original
            compressed += 1

    # Update database records
    if compressed:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "UPDATE filing_history SET pdf_compressed = 1 WHERE pdf_path != '' AND pdf_compressed = 0"
                    " AND created_at < ?",
                    (cutoff.isoformat(),),
                )
                conn.commit()
        except Exception:
            pass

    return compressed
