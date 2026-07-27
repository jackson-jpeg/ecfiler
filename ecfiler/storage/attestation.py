"""Append-only, hash-chained attestation records.

Every filing action carries a durable answer to "who signed this, and what did
they see?": the attestor's identity, the exact attestation language, a canonical
copy of the payload, and (for real submissions) the NEF text — each record
chained to its predecessor by hash, with UPDATE and DELETE blocked by SQLite
triggers.

Tamper model, stated honestly: the triggers and chain make edits *evident*, not
impossible — an actor with raw file access can rewrite the whole chain. The
cheap anchor is that the current chain-head hash is embedded in every saved
receipt, which leaves the operator's machine with the filer; rewriting history
would have to explain receipts that no longer match.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ecfiler.config import DB_PATH
from ecfiler.logging import get_logger

logger = get_logger(__name__)

GENESIS_HASH = "0" * 64

_SCHEMA = """
CREATE TABLE IF NOT EXISTS attestations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT '',
    filing_id INTEGER,
    kind TEXT NOT NULL CHECK (kind IN ('staged', 'submitted')),
    created_at TEXT NOT NULL,
    attestor_name TEXT NOT NULL,
    attestation_text TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    payload_sha256 TEXT NOT NULL,
    context_sha256 TEXT NOT NULL DEFAULT '',
    nef_text TEXT NOT NULL DEFAULT '',
    nef_sha256 TEXT NOT NULL DEFAULT '',
    trace_path TEXT NOT NULL DEFAULT '',
    prev_hash TEXT NOT NULL,
    record_hash TEXT NOT NULL
);
"""

_TRIGGERS = [
    """
    CREATE TRIGGER IF NOT EXISTS attestations_no_update
    BEFORE UPDATE ON attestations
    BEGIN SELECT RAISE(ABORT, 'attestations are append-only'); END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS attestations_no_delete
    BEFORE DELETE ON attestations
    BEGIN SELECT RAISE(ABORT, 'attestations are append-only'); END;
    """,
]


def canonical_json(payload: dict) -> str:
    """Deterministic serialization — same dict, same bytes, same hash."""
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str
    )


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class AttestationRecord:
    id: int
    kind: str
    created_at: str
    attestor_name: str
    payload_sha256: str
    prev_hash: str
    record_hash: str


def _record_hash(prev_hash: str, fields: dict) -> str:
    return _sha256(prev_hash + canonical_json(fields))


class AttestationLog:
    """The append-only log. Shares the history database file."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(_SCHEMA)
            for trigger in _TRIGGERS:
                conn.execute(trigger)
            conn.commit()

    def chain_head(self) -> str:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT record_hash FROM attestations ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return row[0] if row else GENESIS_HASH

    def record(
        self,
        *,
        kind: str,
        attestor_name: str,
        attestation_text: str,
        payload: dict,
        user_id: str = "",
        filing_id: int | None = None,
        context_text: str = "",
        nef_text: str = "",
        trace_path: str = "",
    ) -> AttestationRecord:
        """Append one attestation. Returns the stored record with its hash."""
        payload_json = canonical_json(payload)
        created_at = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # Serialize writers so prev_hash cannot race.
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT record_hash FROM attestations ORDER BY id DESC LIMIT 1"
            ).fetchone()
            prev_hash = row[0] if row else GENESIS_HASH

            fields = {
                "user_id": user_id,
                "filing_id": filing_id,
                "kind": kind,
                "created_at": created_at,
                "attestor_name": attestor_name,
                "attestation_text": attestation_text,
                "payload_json": payload_json,
                "payload_sha256": _sha256(payload_json),
                "context_sha256": _sha256(context_text) if context_text else "",
                "nef_text": nef_text,
                "nef_sha256": _sha256(nef_text) if nef_text else "",
                "trace_path": trace_path,
            }
            record_hash = _record_hash(prev_hash, fields)

            cursor = conn.execute(
                """
                INSERT INTO attestations
                    (user_id, filing_id, kind, created_at, attestor_name,
                     attestation_text, payload_json, payload_sha256,
                     context_sha256, nef_text, nef_sha256, trace_path,
                     prev_hash, record_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fields["user_id"],
                    fields["filing_id"],
                    fields["kind"],
                    fields["created_at"],
                    fields["attestor_name"],
                    fields["attestation_text"],
                    fields["payload_json"],
                    fields["payload_sha256"],
                    fields["context_sha256"],
                    fields["nef_text"],
                    fields["nef_sha256"],
                    fields["trace_path"],
                    prev_hash,
                    record_hash,
                ),
            )
            conn.commit()
            row_id = cursor.lastrowid or 0

        logger.info(
            "Attestation recorded: id=%d kind=%s head=%s", row_id, kind, record_hash[:12]
        )
        return AttestationRecord(
            id=row_id,
            kind=kind,
            created_at=created_at,
            attestor_name=attestor_name,
            payload_sha256=fields["payload_sha256"],
            prev_hash=prev_hash,
            record_hash=record_hash,
        )

    def verify_chain(self) -> tuple[bool, list[str]]:
        """Recompute every hash. Returns (ok, list of problems)."""
        problems: list[str] = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM attestations ORDER BY id").fetchall()

        expected_prev = GENESIS_HASH
        for row in rows:
            if row["prev_hash"] != expected_prev:
                problems.append(
                    f"record {row['id']}: prev_hash broken "
                    f"(expected {expected_prev[:12]}, found {row['prev_hash'][:12]})"
                )
            if row["payload_sha256"] != _sha256(row["payload_json"]):
                problems.append(f"record {row['id']}: payload hash mismatch")
            fields = {
                "user_id": row["user_id"],
                "filing_id": row["filing_id"],
                "kind": row["kind"],
                "created_at": row["created_at"],
                "attestor_name": row["attestor_name"],
                "attestation_text": row["attestation_text"],
                "payload_json": row["payload_json"],
                "payload_sha256": row["payload_sha256"],
                "context_sha256": row["context_sha256"],
                "nef_text": row["nef_text"],
                "nef_sha256": row["nef_sha256"],
                "trace_path": row["trace_path"],
            }
            if row["record_hash"] != _record_hash(row["prev_hash"], fields):
                problems.append(f"record {row['id']}: record hash mismatch")
            expected_prev = row["record_hash"]

        return (not problems, problems)
