"""Append-only, hash-chained attestation records — hash-don't-store.

Every filing action carries a durable answer to "who signed this, and what did
they see?": the attestor's identity, the exact attestation language, a salted
hash of the payload, and (for real submissions) a salted hash of the NEF text —
each record chained to its predecessor by hash, with UPDATE and DELETE blocked
by SQLite triggers.

The raw payload and NEF text live in a separate, deletable table
(attestation_payloads) keyed to the chain record. This is what lets the Privacy
Policy's deletion promise coexist with an append-only chain: deleting an account
removes the case data, while the chain still proves what was attested and when.
The per-record salt is stored only beside the payload, so once a payload row is
deleted its hash cannot be brute-forced from guessed case data, and the
remaining record is unlinkable to any case.

Chains written before this split stored the payload inline and hashed over it,
so their records cannot be migrated without breaking their own hashes. A legacy
table found at init is renamed to attestations_legacy_v1 — its append-only
triggers follow the rename — and a fresh v2 chain starts.

Tamper model, stated honestly: the triggers and chain make edits *evident*, not
impossible — an actor with raw file access can rewrite the whole chain. The
cheap anchor is that the current chain-head hash is embedded in every saved
receipt, which leaves the operator's machine with the filer; rewriting history
would have to explain receipts that no longer match.
"""

from __future__ import annotations

import hashlib
import json
import secrets
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
    payload_sha256 TEXT NOT NULL,
    context_sha256 TEXT NOT NULL DEFAULT '',
    nef_sha256 TEXT NOT NULL DEFAULT '',
    trace_path TEXT NOT NULL DEFAULT '',
    prev_hash TEXT NOT NULL,
    record_hash TEXT NOT NULL
);
"""

_PAYLOAD_SCHEMA = """
CREATE TABLE IF NOT EXISTS attestation_payloads (
    attestation_id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL DEFAULT '',
    salt TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    nef_text TEXT NOT NULL DEFAULT ''
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

# attestation_payloads deliberately has no triggers: deletable by design.


def canonical_json(payload: dict) -> str:
    """Deterministic serialization — same dict, same bytes, same hash."""
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str
    )


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _salted_sha256(salt: str, text: str) -> str:
    return _sha256(salt + text)


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
            self._quarantine_legacy_table(conn)
            conn.execute(_SCHEMA)
            conn.execute(_PAYLOAD_SCHEMA)
            for trigger in _TRIGGERS:
                conn.execute(trigger)
            conn.commit()

    @staticmethod
    def _quarantine_legacy_table(conn: sqlite3.Connection) -> None:
        """Rename a pre-split attestations table out of the way.

        Legacy records hashed over the inline payload_json, so they can only
        verify under the old rules; they are preserved untouched (the
        append-only triggers follow the rename) rather than migrated.
        """
        columns = {
            row[1] for row in conn.execute("PRAGMA table_info(attestations)")
        }
        if "payload_json" in columns:
            conn.execute(
                "ALTER TABLE attestations RENAME TO attestations_legacy_v1"
            )
            logger.warning(
                "Legacy attestation table quarantined as attestations_legacy_v1; "
                "starting a fresh hash-don't-store chain"
            )

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
        salt = secrets.token_hex(16)

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
                "payload_sha256": _salted_sha256(salt, payload_json),
                "context_sha256": _sha256(context_text) if context_text else "",
                "nef_sha256": _salted_sha256(salt, nef_text) if nef_text else "",
                "trace_path": trace_path,
            }
            record_hash = _record_hash(prev_hash, fields)

            cursor = conn.execute(
                """
                INSERT INTO attestations
                    (user_id, filing_id, kind, created_at, attestor_name,
                     attestation_text, payload_sha256, context_sha256,
                     nef_sha256, trace_path, prev_hash, record_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fields["user_id"],
                    fields["filing_id"],
                    fields["kind"],
                    fields["created_at"],
                    fields["attestor_name"],
                    fields["attestation_text"],
                    fields["payload_sha256"],
                    fields["context_sha256"],
                    fields["nef_sha256"],
                    fields["trace_path"],
                    prev_hash,
                    record_hash,
                ),
            )
            row_id = cursor.lastrowid or 0
            conn.execute(
                """
                INSERT INTO attestation_payloads
                    (attestation_id, user_id, salt, payload_json, nef_text)
                VALUES (?, ?, ?, ?, ?)
                """,
                (row_id, user_id, salt, payload_json, nef_text),
            )
            conn.commit()

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

    def purge_user_payloads(self, user_id: str) -> int:
        """Delete the stored payloads (and salts) for one user's records.

        The chain records themselves are untouched — they keep proving that an
        attestation happened; they just no longer contain or point to case data.
        Returns the number of payload rows deleted.
        """
        if not user_id:
            return 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM attestation_payloads WHERE user_id = ?", (user_id,)
            )
            conn.commit()
        deleted = cursor.rowcount
        if deleted:
            logger.info(
                "Purged %d attestation payload(s) for user %s", deleted, user_id
            )
        return deleted

    def export_for_user(self, user_id: str) -> list[dict]:
        """Machine-readable export of one user's attestation records.

        Includes the raw payload and NEF text while they still exist; after a
        purge only the chain metadata remains.
        """
        if not user_id:
            return []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT a.id, a.kind, a.created_at, a.attestor_name,
                       a.attestation_text, a.payload_sha256, a.context_sha256,
                       a.nef_sha256, a.prev_hash, a.record_hash,
                       p.payload_json, p.nef_text
                FROM attestations a
                LEFT JOIN attestation_payloads p ON p.attestation_id = a.id
                WHERE a.user_id = ?
                ORDER BY a.id
                """,
                (user_id,),
            ).fetchall()
        records = []
        for row in rows:
            rec = dict(row)
            if rec["payload_json"] is not None:
                rec["payload"] = json.loads(rec.pop("payload_json"))
            else:
                rec.pop("payload_json")
                rec["payload"] = None
            records.append(rec)
        return records

    def verify_chain(self) -> tuple[bool, list[str]]:
        """Recompute every hash. Returns (ok, list of problems).

        Records whose payload row was deleted still verify: the chain hashes
        cover only the stored fields. When a payload row is present, its salted
        hash is cross-checked against the chain record.
        """
        problems: list[str] = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT a.*, p.salt AS p_salt, p.payload_json AS p_payload_json,
                       p.nef_text AS p_nef_text
                FROM attestations a
                LEFT JOIN attestation_payloads p ON p.attestation_id = a.id
                ORDER BY a.id
                """
            ).fetchall()

        expected_prev = GENESIS_HASH
        for row in rows:
            if row["prev_hash"] != expected_prev:
                problems.append(
                    f"record {row['id']}: prev_hash broken "
                    f"(expected {expected_prev[:12]}, found {row['prev_hash'][:12]})"
                )
            if row["p_salt"] is not None:
                if row["payload_sha256"] != _salted_sha256(
                    row["p_salt"], row["p_payload_json"]
                ):
                    problems.append(f"record {row['id']}: payload hash mismatch")
                if row["nef_sha256"] and row["nef_sha256"] != _salted_sha256(
                    row["p_salt"], row["p_nef_text"]
                ):
                    problems.append(f"record {row['id']}: NEF hash mismatch")
            fields = {
                "user_id": row["user_id"],
                "filing_id": row["filing_id"],
                "kind": row["kind"],
                "created_at": row["created_at"],
                "attestor_name": row["attestor_name"],
                "attestation_text": row["attestation_text"],
                "payload_sha256": row["payload_sha256"],
                "context_sha256": row["context_sha256"],
                "nef_sha256": row["nef_sha256"],
                "trace_path": row["trace_path"],
            }
            if row["record_hash"] != _record_hash(row["prev_hash"], fields):
                problems.append(f"record {row['id']}: record hash mismatch")
            expected_prev = row["record_hash"]

        return (not problems, problems)
