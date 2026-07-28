"""Account data lifecycle: the Privacy Policy's promises, as executable checks.

Self-serve deletion and machine-readable export exist as endpoints, deletion
is immediate and complete, and the attestation chain survives it.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from ecfiler.api.app import app
from ecfiler.storage.attestation import AttestationLog


def _client(user_id: str) -> TestClient:
    return TestClient(app, headers={"X-User-Id": user_id})


def _stage_filing(client: TestClient) -> None:
    response = client.post(
        "/api/filing/stage",
        json={
            "court_id": "nysd",
            "case_number": "1:24-cv-09999",
            "event_code": "12",
            "event_description": "Motion to Dismiss",
            "filing_party_name": "Smith",
            "filing_party_role": "plaintiff",
            "attestation": {
                "attested": True,
                "attestor_name": "Jane Doe, Esq.",
                "attestation_text": "I have reviewed and take responsibility.",
            },
        },
    )
    assert response.status_code == 200, response.text


@pytest.fixture
def user_id() -> str:
    return f"lifecycle-{uuid.uuid4().hex[:12]}"


class TestExport:
    def test_export_requires_auth(self) -> None:
        res = TestClient(app).get("/api/export")
        assert res.status_code == 401

    def test_export_contains_staged_data(self, user_id: str) -> None:
        client = _client(user_id)
        _stage_filing(client)

        res = client.get("/api/export")
        assert res.status_code == 200
        data = res.json()
        assert data["user_id"] == user_id
        assert len(data["filing_history"]) == 1
        assert data["filing_history"][0]["case_number"] == "1:24-cv-09999"
        assert len(data["staged_packages"]) == 1
        assert len(data["attestations"]) == 1
        # While the account exists, the export includes the raw payload.
        assert data["attestations"][0]["payload"]["case_number"] == "1:24-cv-09999"


class TestDeletion:
    def test_delete_requires_auth(self) -> None:
        res = TestClient(app).delete("/api/account")
        assert res.status_code == 401

    def test_delete_purges_everything_and_chain_survives(self, user_id: str) -> None:
        client = _client(user_id)
        _stage_filing(client)

        res = client.delete("/api/account")
        assert res.status_code == 200
        counts = res.json()
        assert counts["deleted"] is True
        assert counts["filing_history_rows"] == 1
        assert counts["staged_packages"] == 1
        assert counts["attestation_payloads"] == 1

        # Everything user-visible is gone.
        after = client.get("/api/export").json()
        assert after["filing_history"] == []
        assert after["staged_packages"] == []
        # The chain record remains, but carries no case data.
        assert len(after["attestations"]) == 1
        assert after["attestations"][0]["payload"] is None
        assert after["attestations"][0]["nef_text"] is None

        # And the chain still verifies end to end.
        ok, problems = AttestationLog().verify_chain()
        assert ok, problems

    def test_delete_is_scoped_to_the_user(self, user_id: str) -> None:
        other = f"lifecycle-other-{uuid.uuid4().hex[:8]}"
        _stage_filing(_client(other))
        _stage_filing(_client(user_id))

        _client(user_id).delete("/api/account")

        other_export = _client(other).get("/api/export").json()
        assert len(other_export["filing_history"]) == 1
        assert other_export["attestations"][0]["payload"] is not None

        # Clean up the second user too.
        _client(other).delete("/api/account")

    def test_delete_twice_is_safe(self, user_id: str) -> None:
        client = _client(user_id)
        _stage_filing(client)
        client.delete("/api/account")
        res = client.delete("/api/account")
        assert res.status_code == 200
        assert res.json()["filing_history_rows"] == 0
