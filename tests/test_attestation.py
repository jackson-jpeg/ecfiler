"""Attestation log: append-only, hash-chained, verifiable, payload-deletable."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from ecfiler.storage.attestation import (
    GENESIS_HASH,
    AttestationLog,
    canonical_json,
)


@pytest.fixture
def log(tmp_path: Path) -> AttestationLog:
    return AttestationLog(db_path=tmp_path / "audit.db")


def _record(log: AttestationLog, n: int = 1, user_id: str = "") -> None:
    for i in range(n):
        log.record(
            kind="submitted",
            attestor_name="Jane Doe, Esq.",
            attestation_text="Typed CONFIRM and YES.",
            payload={"case": f"1:24-cv-{i:05d}", "event": "Motion to Dismiss"},
            nef_text=f"Notice of Electronic Filing #{i}",
            user_id=user_id,
        )


class TestChain:
    def test_first_record_chains_from_genesis(self, log: AttestationLog) -> None:
        rec = log.record(
            kind="staged",
            attestor_name="A",
            attestation_text="t",
            payload={"x": 1},
        )
        assert rec.prev_hash == GENESIS_HASH
        assert log.chain_head() == rec.record_hash

    def test_chain_links(self, log: AttestationLog) -> None:
        _record(log, 3)
        ok, problems = log.verify_chain()
        assert ok, problems

    def test_canonical_json_deterministic(self) -> None:
        assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})


class TestImmutability:
    def test_update_blocked(self, log: AttestationLog) -> None:
        _record(log)
        with sqlite3.connect(log.db_path) as conn:
            with pytest.raises(sqlite3.IntegrityError, match="append-only"):
                conn.execute("UPDATE attestations SET attestor_name = 'Mallory'")

    def test_delete_blocked(self, log: AttestationLog) -> None:
        _record(log)
        with sqlite3.connect(log.db_path) as conn:
            with pytest.raises(sqlite3.IntegrityError, match="append-only"):
                conn.execute("DELETE FROM attestations")


class TestHashDontStore:
    """Case data lives only in the deletable side table."""

    def test_chain_table_holds_no_case_data(self, log: AttestationLog) -> None:
        _record(log, user_id="user-1")
        with sqlite3.connect(log.db_path) as conn:
            columns = {r[1] for r in conn.execute("PRAGMA table_info(attestations)")}
            assert "payload_json" not in columns
            assert "nef_text" not in columns

    def test_payload_purge_leaves_chain_verifiable(self, log: AttestationLog) -> None:
        _record(log, 2, user_id="user-1")
        _record(log, 1, user_id="user-2")

        deleted = log.purge_user_payloads("user-1")
        assert deleted == 2

        ok, problems = log.verify_chain()
        assert ok, problems
        # The chain records themselves are all still present.
        with sqlite3.connect(log.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM attestations").fetchone()[0]
            remaining = conn.execute(
                "SELECT COUNT(*) FROM attestation_payloads"
            ).fetchone()[0]
        assert count == 3
        assert remaining == 1

    def test_purge_removes_salt_with_payload(self, log: AttestationLog) -> None:
        """After a purge, no salt survives, so payload hashes cannot be
        brute-forced from guessed case data."""
        _record(log, user_id="user-1")
        log.purge_user_payloads("user-1")
        with sqlite3.connect(log.db_path) as conn:
            rows = conn.execute(
                "SELECT salt FROM attestation_payloads"
            ).fetchall()
        assert rows == []

    def test_purge_empty_user_id_is_noop(self, log: AttestationLog) -> None:
        _record(log, user_id="")
        assert log.purge_user_payloads("") == 0


class TestVerification:
    def test_tampered_payload_detected(self, log: AttestationLog) -> None:
        _record(log, 2)
        with sqlite3.connect(log.db_path) as conn:
            conn.execute(
                "UPDATE attestation_payloads SET payload_json = '{\"case\":\"FORGED\"}' "
                "WHERE attestation_id = 1"
            )
            conn.commit()
        ok, problems = log.verify_chain()
        assert not ok
        assert any("payload hash mismatch" in p for p in problems)

    def test_tampered_nef_detected(self, log: AttestationLog) -> None:
        _record(log)
        with sqlite3.connect(log.db_path) as conn:
            conn.execute(
                "UPDATE attestation_payloads SET nef_text = 'FORGED NEF'"
            )
            conn.commit()
        ok, problems = log.verify_chain()
        assert not ok
        assert any("NEF hash mismatch" in p for p in problems)

    def test_tampered_chain_field_detected(self, log: AttestationLog) -> None:
        _record(log, 2)
        with sqlite3.connect(log.db_path) as conn:
            conn.execute("DROP TRIGGER attestations_no_update")
            conn.execute(
                "UPDATE attestations SET attestor_name = 'Mallory' WHERE id = 1"
            )
            conn.commit()
        ok, problems = log.verify_chain()
        assert not ok
        assert any("record hash mismatch" in p for p in problems)

    def test_rechained_forgery_detected_downstream(self, log: AttestationLog) -> None:
        """Rewriting one record breaks the link to its successor."""
        _record(log, 2)
        with sqlite3.connect(log.db_path) as conn:
            conn.execute("DROP TRIGGER attestations_no_update")
            conn.execute(
                "UPDATE attestations SET record_hash = ? WHERE id = 1", ("f" * 64,)
            )
            conn.commit()
        ok, problems = log.verify_chain()
        assert not ok


class TestLegacyQuarantine:
    """Pre-split chains hashed over inline payloads; they are preserved
    untouched under a new name, not migrated into hashes they would break."""

    LEGACY_SCHEMA = """
    CREATE TABLE attestations (
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

    def _make_legacy_db(self, path: Path) -> None:
        with sqlite3.connect(path) as conn:
            conn.execute(self.LEGACY_SCHEMA)
            conn.execute(
                """
                CREATE TRIGGER attestations_no_delete
                BEFORE DELETE ON attestations
                BEGIN SELECT RAISE(ABORT, 'attestations are append-only'); END;
                """
            )
            conn.execute(
                """
                INSERT INTO attestations
                    (kind, created_at, attestor_name, attestation_text,
                     payload_json, payload_sha256, prev_hash, record_hash)
                VALUES ('staged', '2026-07-01T00:00:00Z', 'A', 't',
                        '{"case":"old"}', 'x', ?, 'y')
                """,
                (GENESIS_HASH,),
            )
            conn.commit()

    def test_legacy_table_quarantined_and_preserved(self, tmp_path: Path) -> None:
        db = tmp_path / "audit.db"
        self._make_legacy_db(db)

        log = AttestationLog(db_path=db)
        _record(log)

        with sqlite3.connect(db) as conn:
            legacy = conn.execute(
                "SELECT payload_json FROM attestations_legacy_v1"
            ).fetchall()
            assert legacy == [('{"case":"old"}',)]
            # The legacy table keeps its append-only trigger after the rename.
            with pytest.raises(sqlite3.IntegrityError, match="append-only"):
                conn.execute("DELETE FROM attestations_legacy_v1")

        ok, problems = log.verify_chain()
        assert ok, problems

    def test_quarantine_is_idempotent(self, tmp_path: Path) -> None:
        db = tmp_path / "audit.db"
        self._make_legacy_db(db)
        AttestationLog(db_path=db)
        log = AttestationLog(db_path=db)  # second init must not rename again
        _record(log)
        ok, problems = log.verify_chain()
        assert ok, problems


class TestStagingAttestationRequired:
    def test_stage_without_attestation_422(self) -> None:
        from fastapi.testclient import TestClient

        from ecfiler.api.app import app

        client = TestClient(app, headers={"X-User-Id": "test-user"})
        response = client.post(
            "/api/filing/stage",
            json={
                "court_id": "nysd",
                "case_number": "1:24-cv-01234",
                "event_code": "12",
                "event_description": "Motion to Dismiss",
                "filing_party_name": "Smith",
                "filing_party_role": "plaintiff",
            },
        )
        assert response.status_code == 422
        assert "attestation" in response.json()["error"].lower()

    def test_stage_with_attestation_succeeds_and_records(self, tmp_path: Path) -> None:
        from fastapi.testclient import TestClient

        from ecfiler.api.app import app

        client = TestClient(app, headers={"X-User-Id": "test-user"})
        response = client.post(
            "/api/filing/stage",
            json={
                "court_id": "nysd",
                "case_number": "1:24-cv-01234",
                "event_code": "12",
                "event_description": "Motion to Dismiss",
                "filing_party_name": "Smith",
                "filing_party_role": "plaintiff",
                "attestation": {
                    "attested": True,
                    "attestor_name": "Jane Doe, Esq.",
                    "attestation_text": "I have reviewed and take responsibility.",
                    "client_timestamp": "2026-07-27T12:00:00Z",
                },
            },
        )
        assert response.status_code == 200
        ok, problems = AttestationLog().verify_chain()
        assert ok, problems
