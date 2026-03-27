"""Integration tests — verify CLI commands work end-to-end."""

from pathlib import Path

import fitz
import pytest
from click.testing import CliRunner

from ecfiler.__main__ import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def sample_motion(tmp_path: Path) -> Path:
    """Create a realistic-looking motion PDF."""
    doc = fitz.open()
    page = doc.new_page()
    y = 72
    for line in [
        "UNITED STATES DISTRICT COURT",
        "SOUTHERN DISTRICT OF NEW YORK",
        "",
        "JOHN SMITH,",
        "              Plaintiff,",
        "         v.                            Case No. 1:24-cv-01234-ABC",
        "JONES CORPORATION,",
        "              Defendant.",
        "",
        "MOTION TO DISMISS FOR FAILURE TO STATE A CLAIM",
        "",
        "Defendant Jones Corporation, by and through undersigned counsel,",
        "respectfully moves this Court for an order dismissing the Complaint",
        "pursuant to Federal Rule of Civil Procedure 12(b)(6).",
        "",
        "ARGUMENT",
        "",
        "Plaintiff's complaint fails to state a claim upon which relief can",
        "be granted. The allegations are conclusory and lack factual support.",
        "",
        "CONCLUSION",
        "",
        "For the foregoing reasons, Defendant respectfully requests that",
        "this Court dismiss the Complaint in its entirety.",
        "",
        "Respectfully submitted,",
        "",
        "/s/ Jane Doe",
        "Jane Doe, Esq. (Bar No. JD5678)",
        "Smith & Associates LLP",
        "123 Broadway, Suite 100",
        "New York, NY 10004",
        "(212) 555-0123",
        "jane.doe@smithlaw.com",
        "",
        "CERTIFICATE OF SERVICE",
        "",
        "I hereby certify that on this date, I electronically filed the",
        "foregoing document with the Clerk of Court using the CM/ECF system,",
        "which will send a Notice of Electronic Filing to all counsel of record.",
        "",
        "/s/ Jane Doe",
    ]:
        page.insert_text((72, y), line, fontsize=11)
        y += 15
        if y > 720:
            page = doc.new_page()
            y = 72

    pdf_path = tmp_path / "motion_to_dismiss.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


class TestCLIIntegration:
    """Test that CLI commands actually work end-to-end."""

    def test_check_command(self, runner: CliRunner) -> None:
        """ecfiler check should run all diagnostics."""
        result = runner.invoke(main, ["check"])
        assert result.exit_code == 0
        assert "config" in result.output.lower()
        assert "PASS" in result.output or "FAIL" in result.output

    def test_validate_full_motion(self, runner: CliRunner, sample_motion: Path) -> None:
        """ecfiler validate should fully check a realistic PDF."""
        result = runner.invoke(main, ["validate", str(sample_motion)])
        assert result.exit_code == 0
        assert "VALID" in result.output
        assert "redaction" in result.output.lower()

    def test_validate_catches_redaction(self, runner: CliRunner, tmp_path: Path) -> None:
        """ecfiler validate should flag SSNs in a document."""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Plaintiff's SSN: 123-45-6789")
        pdf = tmp_path / "redaction_test.pdf"
        doc.save(str(pdf))
        doc.close()

        result = runner.invoke(main, ["validate", str(pdf)])
        assert result.exit_code == 0
        assert "redaction" in result.output.lower()

    def test_courts_pipeline(self, runner: CliRunner) -> None:
        """Courts search → filter → verify specific court."""
        # List all
        result = runner.invoke(main, ["courts"])
        assert result.exit_code == 0
        assert "nysd" in result.output.lower() or "Southern District" in result.output

        # Filter
        result = runner.invoke(main, ["courts", "--type", "bankruptcy"])
        assert result.exit_code == 0

        # Search
        result = runner.invoke(main, ["courts", "--search", "delaware"])
        assert result.exit_code == 0

    def test_template_workflow(self, runner: CliRunner, sample_motion: Path) -> None:
        """Save template → list → quick file with it."""
        # Save
        result = runner.invoke(main, [
            "save-template", "test-mtd",
            "--court", "nysd",
            "--event-code", "12",
            "--event-desc", "Motion to Dismiss",
        ])
        assert result.exit_code == 0
        assert "saved" in result.output.lower()

        # Quick file (will find the template)
        result = runner.invoke(main, [
            "quick", "test-mtd", "1:24-cv-01234", str(sample_motion), "--dry-run",
        ])
        assert result.exit_code == 0
        assert "nysd" in result.output.lower() or "motion" in result.output.lower()

    def test_demo_full_walkthrough(self, runner: CliRunner) -> None:
        """ecfiler demo should complete without errors."""
        result = runner.invoke(main, ["demo"])
        assert result.exit_code == 0
        assert "CONFIRM" in result.output
        assert "Demo complete" in result.output

    def test_version_and_help(self, runner: CliRunner) -> None:
        """Basic CLI structure works."""
        result = runner.invoke(main, ["--version"])
        assert "0.1.0" in result.output

        result = runner.invoke(main, ["--help"])
        assert "smart" in result.output
        assert "serve" in result.output
        assert "check" in result.output
        assert "courts" in result.output


class TestAPIIntegration:
    """Test API endpoints work together."""

    def test_full_validation_pipeline(self, sample_motion: Path) -> None:
        """Upload → validate → redaction scan."""
        from fastapi.testclient import TestClient
        from ecfiler.api.app import app

        client = TestClient(app)

        # Validate
        with open(sample_motion, "rb") as f:
            res = client.post("/api/validate", files={"document": ("motion.pdf", f)})
        assert res.status_code == 200
        assert res.json()["valid"] is True

        # Redaction scan
        with open(sample_motion, "rb") as f:
            res = client.post("/api/redaction-scan", files={"document": ("motion.pdf", f)})
        assert res.status_code == 200
        assert res.json()["risk_level"] in ("none", "low", "high")

    def test_court_to_events_pipeline(self) -> None:
        """List courts → pick one → get its events."""
        from fastapi.testclient import TestClient
        from ecfiler.api.app import app

        client = TestClient(app)

        # List courts
        res = client.get("/api/courts?search=new york")
        assert res.status_code == 200
        courts = res.json()
        assert len(courts) >= 1
        court_id = courts[0]["court_id"]

        # Get events for that court
        res = client.get(f"/api/courts/{court_id}/events")
        assert res.status_code == 200
        events = res.json()
        assert len(events) > 0

    def test_cos_generate_and_download(self) -> None:
        """Generate certificate of service text → download PDF."""
        from fastapi.testclient import TestClient
        from ecfiler.api.app import app

        client = TestClient(app)

        payload = {
            "attorney_name": "Jane Smith",
            "case_number": "1:24-cv-01234",
            "recipients": [
                {"name": "Jones Corp", "role": "defendant", "attorney_name": "Adams", "method": "CM/ECF"},
            ],
        }

        # Text
        res = client.post("/api/certificate-of-service", json=payload)
        assert res.status_code == 200
        assert "Jane Smith" in res.json()["text"]

        # PDF
        res = client.post("/api/certificate-of-service/pdf", json=payload)
        assert res.status_code == 200
        assert len(res.content) > 100

    def test_health_reflects_state(self) -> None:
        """Health endpoint returns meaningful data."""
        from fastapi.testclient import TestClient
        from ecfiler.api.app import app

        client = TestClient(app)
        res = client.get("/api/health")
        data = res.json()
        assert data["status"] == "ok"
        assert data["courts_loaded"] >= 150
        assert "version" in data
