"""Tests for the FastAPI backend."""

import tempfile
from pathlib import Path

import fitz
import pytest
from fastapi.testclient import TestClient

from ecfiler.api.app import app


@pytest.fixture
def client() -> TestClient:
    # Dev-auth mode (see conftest.py): user-scoped endpoints need X-User-Id.
    return TestClient(app, headers={"X-User-Id": "test-user"})


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "UNITED STATES DISTRICT COURT")
    page.insert_text((72, 90), "SOUTHERN DISTRICT OF NEW YORK")
    page.insert_text((72, 120), "SMITH, Plaintiff,")
    page.insert_text((72, 140), "v.")
    page.insert_text((72, 160), "JONES CORP, Defendant.")
    page.insert_text((72, 180), "Case No. 1:24-cv-01234-ABC")
    page.insert_text((72, 220), "MOTION TO DISMISS")
    page.insert_text((72, 260), "Respectfully submitted,")
    page.insert_text((72, 280), "/s/ Jane Doe")
    page.insert_text((72, 300), "Jane Doe, Esq. (Bar #JD5678)")
    page.insert_text((72, 320), "Smith & Associates LLP")
    pdf_path = tmp_path / "motion.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


class TestUIServing:
    def test_root_serves_ui(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.status_code == 200
        assert "ECFiler" in response.text

    def test_ui_has_drop_zone(self, client: TestClient) -> None:
        response = client.get("/")
        assert "Drop" in response.text and "PDF" in response.text

    def test_ui_has_alpine(self, client: TestClient) -> None:
        response = client.get("/")
        assert "alpinejs" in response.text


class TestHealthEndpoint:
    def test_health(self, client: TestClient) -> None:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["courts_loaded"] >= 150


class TestCourtsEndpoint:
    def test_list_all(self, client: TestClient) -> None:
        response = client.get("/api/courts")
        assert response.status_code == 200
        courts = response.json()
        assert len(courts) >= 150

    def test_filter_by_type(self, client: TestClient) -> None:
        response = client.get("/api/courts?court_type=appellate")
        assert response.status_code == 200
        courts = response.json()
        assert all(c["court_type"] == "appellate" for c in courts)
        assert len(courts) >= 13

    def test_search(self, client: TestClient) -> None:
        response = client.get("/api/courts?search=california")
        assert response.status_code == 200
        courts = response.json()
        assert len(courts) >= 1


class TestEventCodesEndpoint:
    def test_get_events(self, client: TestClient) -> None:
        response = client.get("/api/courts/nysd/events")
        assert response.status_code == 200
        events = response.json()
        assert len(events) > 0
        assert all("code" in e and "description" in e for e in events)

    def test_search_events(self, client: TestClient) -> None:
        response = client.get("/api/courts/nysd/events?search=motion")
        assert response.status_code == 200
        events = response.json()
        assert len(events) >= 1
        assert any("motion" in e["description"].lower() for e in events)

    def test_court_not_found(self, client: TestClient) -> None:
        response = client.get("/api/courts/zzz/events")
        assert response.status_code == 404


class TestValidateEndpoint:
    def test_valid_pdf(self, client: TestClient, sample_pdf: Path) -> None:
        with open(sample_pdf, "rb") as f:
            response = client.post(
                "/api/validate",
                files={"document": ("motion.pdf", f, "application/pdf")},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["page_count"] == 1
        assert data["has_text"] is True

    def test_empty_pdf(self, client: TestClient, tmp_path: Path) -> None:
        empty = tmp_path / "empty.pdf"
        empty.write_bytes(b"")
        with open(empty, "rb") as f:
            response = client.post(
                "/api/validate",
                files={"document": ("empty.pdf", f, "application/pdf")},
            )
        # Empty files are now rejected at upload validation
        assert response.status_code == 400
        assert "Empty" in response.json()["error"]


class TestRedactionEndpoint:
    def test_clean_document(self, client: TestClient, sample_pdf: Path) -> None:
        with open(sample_pdf, "rb") as f:
            response = client.post(
                "/api/redaction-scan",
                files={"document": ("motion.pdf", f, "application/pdf")},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] in ("none", "low", "high")

    def test_document_with_ssn(self, client: TestClient, tmp_path: Path) -> None:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Plaintiff SSN: 123-45-6789")
        pdf = tmp_path / "ssn.pdf"
        doc.save(str(pdf))
        doc.close()

        with open(pdf, "rb") as f:
            response = client.post(
                "/api/redaction-scan",
                files={"document": ("ssn.pdf", f, "application/pdf")},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] == "high"
        assert len(data["issues"]) >= 1


class TestCertificateEndpoint:
    def test_generate_cos_all_ecf(self, client: TestClient) -> None:
        response = client.post(
            "/api/certificate-of-service",
            json={
                "attorney_name": "Jane Smith",
                "case_number": "1:24-cv-01234",
                "recipients": [
                    {"name": "Jones Corp", "role": "defendant", "attorney_name": "John Adams", "method": "CM/ECF"},
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_all_ecf"] is True
        assert "Jane Smith" in data["text"]
        assert "CM/ECF" in data["text"]

    def test_generate_cos_mixed(self, client: TestClient) -> None:
        response = client.post(
            "/api/certificate-of-service",
            json={
                "attorney_name": "Jane Smith",
                "recipients": [
                    {"name": "ECF Party", "role": "defendant", "method": "CM/ECF"},
                    {"name": "Mail Party", "role": "defendant", "method": "mail", "address": "123 Main St"},
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_all_ecf"] is False
        assert data["method"] == "mixed"

    def test_generate_cos_pdf(self, client: TestClient) -> None:
        response = client.post(
            "/api/certificate-of-service/pdf",
            json={
                "attorney_name": "Jane Smith",
                "case_number": "1:24-cv-01234",
                "court_name": "S.D.N.Y.",
                "recipients": [
                    {"name": "Jones", "role": "defendant", "attorney_name": "Adams", "method": "CM/ECF"},
                ],
            },
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 100


_STAGE_PAYLOAD = {
    "court_id": "nysd",
    "case_number": "1:24-cv-01234",
    "event_code": "12",
    "event_description": "Motion to Dismiss",
    "filing_party_name": "Smith",
    "filing_party_role": "plaintiff",
    "document_path": "/tmp/test.pdf",
    "attestation": {
        "attested": True,
        "attestor_name": "Jane Doe, Esq.",
        "attestation_text": "I have reviewed and take responsibility.",
    },
}


class TestFilingStageEndpoint:
    def test_stage_returns_package(self, client: TestClient) -> None:
        response = client.post("/api/filing/stage", json=_STAGE_PAYLOAD)
        assert response.status_code == 200
        pkg = response.json()
        assert pkg["stage_code"]
        assert pkg["court_id"] == "nysd"
        assert pkg["ecf_login_url"].startswith("https://")
        assert len(pkg["instructions"]) >= 5
        assert any("your own credentials" in i for i in pkg["instructions"])

    def test_stage_roundtrip_fetch(self, client: TestClient) -> None:
        pkg = client.post("/api/filing/stage", json=_STAGE_PAYLOAD).json()
        fetched = client.get(f"/api/filing/stage/{pkg['stage_code']}")
        assert fetched.status_code == 200
        assert fetched.json()["case_number"] == "1:24-cv-01234"

    def test_stage_unknown_code_404(self, client: TestClient) -> None:
        assert client.get("/api/filing/stage/nonexistent").status_code == 404

    def test_stage_unknown_court_404(self, client: TestClient) -> None:
        response = client.post(
            "/api/filing/stage", json={**_STAGE_PAYLOAD, "court_id": "zzz"}
        )
        assert response.status_code == 404

    def test_submit_alias_answers_staged(self, client: TestClient) -> None:
        """Deprecated /submit endpoint delegates to staging and says so —
        the old 'submitted'/'dry_run' pretense is gone."""
        response = client.post("/api/filing/submit", json=_STAGE_PAYLOAD)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "staged"
        assert "does not submit" in data["message"]

    def test_browser_stream_endpoint_gone(self, client: TestClient) -> None:
        response = client.post("/api/filing/browser-stream", json=_STAGE_PAYLOAD)
        assert response.status_code in (404, 405)


class TestHistoryEndpoint:
    def test_empty_history(self, client: TestClient) -> None:
        response = client.get("/api/history")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)


class TestCORSConfiguration:
    def test_cors_rejects_unlisted_origin(self, client: TestClient) -> None:
        """Requests from origins not in ECFILER_ALLOWED_ORIGINS should lack CORS headers."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "https://evil.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        # Should NOT include the evil origin in the response
        allow_origin = response.headers.get("access-control-allow-origin", "")
        assert allow_origin != "https://evil.example.com"
        assert allow_origin != "*"

    def test_cors_allows_configured_origin(self, client: TestClient) -> None:
        """The default allowed origin (localhost:3000) should get CORS headers."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        allow_origin = response.headers.get("access-control-allow-origin", "")
        assert allow_origin == "http://localhost:3000"


class TestStandardizedErrorResponses:
    def test_404_returns_json_with_error_field(self, client: TestClient) -> None:
        response = client.get("/api/courts/zzz/events")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "code" in data
        assert data["code"] == 404

    def test_400_returns_json_with_error_field(self, client: TestClient, tmp_path: Path) -> None:
        empty = tmp_path / "empty.pdf"
        empty.write_bytes(b"")
        with open(empty, "rb") as f:
            response = client.post(
                "/api/validate",
                files={"document": ("empty.pdf", f, "application/pdf")},
            )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["code"] == 400


class TestCacheHeaders:
    def test_courts_has_cache_control(self, client: TestClient) -> None:
        response = client.get("/api/courts")
        assert response.status_code == 200
        assert "max-age=3600" in response.headers.get("cache-control", "")

    def test_events_has_cache_control(self, client: TestClient) -> None:
        response = client.get("/api/courts/nysd/events")
        assert response.status_code == 200
        assert "max-age=3600" in response.headers.get("cache-control", "")


class TestFilingFeeInPreview:
    def test_complaint_surface_fee(
        self,
        client: TestClient,
        sample_pdf: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """analyze_and_prepare_filing should return filing_fee / filing_fee_text."""
        from ecfiler.agent.document_analyzer import DocumentAnalysis

        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        def fake_analyze(text: str, api_key: str = "") -> DocumentAnalysis:
            return DocumentAnalysis(
                document_type="Complaint",
                document_type_specific="Complaint",
                case_number="1:24-cv-01234",
                court_id="nysd",
                case_caption="Smith v. Jones",
                filing_party_name="Smith",
                filing_party_role="Plaintiff",
                is_response=False,
                has_signature=True,
                has_certificate_of_service=True,
                attorney_name="Jane Doe",
                suggested_event_code_category="complaint",
                confidence="high",
            )

        monkeypatch.setattr(
            "ecfiler.agent.document_analyzer.analyze_document", fake_analyze
        )

        with open(sample_pdf, "rb") as f:
            response = client.post(
                "/api/file",
                files={"document": ("complaint.pdf", f, "application/pdf")},
            )

        assert response.status_code == 200, response.text
        data = response.json()
        assert "filing_fee" in data
        assert "filing_fee_text" in data
        assert data["filing_fee"] == 405.00
        assert "$405.00" in data["filing_fee_text"]
