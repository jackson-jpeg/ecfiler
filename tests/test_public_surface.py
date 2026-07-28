"""The hosted API's public surface is deliberate, not accidental.

Free tools stay public. Anything that spends money (Anthropic-backed
analysis), touches user state (drafts), or rewrites stored filings
(compression) must not be reachable without authentication.
"""

import pytest
from fastapi.testclient import TestClient

from ecfiler.api.app import app


@pytest.fixture
def anon_client() -> TestClient:
    """A client with no credentials at all."""
    return TestClient(app)


class TestAuthRequired:
    def test_file_requires_auth(self, anon_client: TestClient) -> None:
        res = anon_client.post(
            "/api/file",
            files={"document": ("m.pdf", b"%PDF-1.4 minimal", "application/pdf")},
        )
        assert res.status_code == 401

    def test_file_stream_requires_auth(self, anon_client: TestClient) -> None:
        res = anon_client.post(
            "/api/file/stream",
            files={"document": ("m.pdf", b"%PDF-1.4 minimal", "application/pdf")},
        )
        assert res.status_code == 401

    def test_file_multi_requires_auth(self, anon_client: TestClient) -> None:
        res = anon_client.post(
            "/api/file/multi",
            files={"main_document": ("m.pdf", b"%PDF-1.4 minimal", "application/pdf")},
        )
        assert res.status_code == 401

    def test_draft_delete_requires_auth(self, anon_client: TestClient) -> None:
        res = anon_client.delete("/api/drafts/some-draft")
        assert res.status_code == 401

    def test_compress_endpoint_removed(self, anon_client: TestClient) -> None:
        res = anon_client.post("/api/filing/compress")
        assert res.status_code in (404, 405)


class TestFreeToolsStayPublic:
    def test_courts_public(self, anon_client: TestClient) -> None:
        res = anon_client.get("/api/courts")
        assert res.status_code == 200
        assert len(res.json()) > 0

    def test_events_public(self, anon_client: TestClient) -> None:
        res = anon_client.get("/api/courts/nysd/events")
        assert res.status_code == 200

    def test_certificate_public(self, anon_client: TestClient) -> None:
        res = anon_client.post(
            "/api/certificate-of-service",
            json={
                "attorney_name": "Jane Doe",
                "case_number": "1:24-cv-00001",
                "recipients": [{"name": "John Roe", "method": "CM/ECF"}],
            },
        )
        assert res.status_code == 200

    def test_health_public(self, anon_client: TestClient) -> None:
        res = anon_client.get("/api/health")
        assert res.status_code == 200
