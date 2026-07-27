"""Attestation log: append-only, hash-chained, verifiable."""

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


def _record(log: AttestationLog, n: int = 1) -> None:
    for i in range(n):
        log.record(
            kind="submitted",
            attestor_name="Jane Doe, Esq.",
            attestation_text="Typed CONFIRM and YES.",
            payload={"case": f"1:24-cv-{i:05d}", "event": "Motion to Dismiss"},
            nef_text=f"Notice of Electronic Filing #{i}",
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


class TestVerification:
    def test_tampered_payload_detected(self, log: AttestationLog) -> None:
        _record(log, 2)
        with sqlite3.connect(log.db_path) as conn:
            conn.execute("DROP TRIGGER attestations_no_update")
            conn.execute(
                "UPDATE attestations SET payload_json = '{\"case\":\"FORGED\"}' WHERE id = 1"
            )
            conn.commit()
        ok, problems = log.verify_chain()
        assert not ok
        assert any("payload hash mismatch" in p for p in problems)

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
