"""Sealed/restricted hard-fail behavior.

The invariant: a sealed document can never silently become a public filing,
and the hosted service never handles sealed content at all.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from ecfiler.api.app import app
from ecfiler.browser.filing import FilingAutomation
from ecfiler.courts.base import BaseCourt, CourtProfile, SealingUnavailableError
from ecfiler.filing.models import (
    CaseInfo,
    Document,
    EventCode,
    ExhibitEntry,
    ExhibitPackageModel,
    Filing,
    SealingLevel,
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, headers={"X-User-Id": "test-user"})


def _court() -> BaseCourt:
    return BaseCourt(
        CourtProfile(
            court_id="nysd",
            name="SDNY",
            court_type="district",
            ecf_url="https://nysd.uscourts.gov",
        )
    )


class TestSelectSealingLevelFailsClosed:
    def test_no_control_found_raises(self) -> None:
        page = MagicMock()
        page.query_selector.return_value = None
        with pytest.raises(SealingUnavailableError, match="NOT submitted"):
            _court().select_sealing_level(page, "sealed")

    def test_public_is_noop(self) -> None:
        page = MagicMock()
        _court().select_sealing_level(page, "public")
        page.query_selector.assert_not_called()

    def test_checkbox_control_is_checked(self) -> None:
        page = MagicMock()
        el = MagicMock()
        el.evaluate.return_value = "INPUT"
        page.query_selector.return_value = el
        _court().select_sealing_level(page, "sealed")
        el.check.assert_called_once()


class TestSealedExhibitPropagation:
    def test_sealed_exhibit_without_control_aborts(self) -> None:
        court = _court()
        court.upload_attachment = MagicMock()  # type: ignore[method-assign]
        browser = MagicMock()
        browser.page.query_selector.return_value = None

        filing = Filing(
            court_id="nysd",
            case=CaseInfo(case_number="1:24-cv-01234"),
            event=EventCode(code="12", description="Motion"),
            documents=[
                Document(file_path="/tmp/main.pdf", is_main=True),
                Document(file_path="/tmp/a.pdf", is_main=False),
            ],
            exhibit_package=ExhibitPackageModel(
                exhibits=[
                    ExhibitEntry(file_path="/tmp/a.pdf", label="Exhibit A", sealed=True)
                ],
                has_sealed_exhibits=True,
            ),
        )
        automation = FilingAutomation(court=court, browser=browser, filing=filing)
        with pytest.raises(SealingUnavailableError):
            automation._upload_attachments()

    def test_sealed_main_document_without_control_aborts(self) -> None:
        court = _court()
        court.upload_document = MagicMock()  # type: ignore[method-assign]
        browser = MagicMock()
        browser.page.query_selector.return_value = None

        filing = Filing(
            court_id="nysd",
            case=CaseInfo(case_number="1:24-cv-01234"),
            event=EventCode(code="12", description="Motion"),
            documents=[
                Document(
                    file_path="/tmp/main.pdf",
                    is_main=True,
                    sealing=SealingLevel.SEALED,
                    description="Sealed per protective order",
                )
            ],
        )
        automation = FilingAutomation(court=court, browser=browser, filing=filing)
        with pytest.raises(SealingUnavailableError):
            automation._upload_main()


class TestHostedServiceRefusesSealed:
    def test_submit_with_sealed_flag_403(self, client: TestClient) -> None:
        response = client.post(
            "/api/filing/submit",
            json={
                "court_id": "nysd",
                "case_number": "1:24-cv-01234",
                "event_code": "12",
                "event_description": "Motion to Dismiss",
                "filing_party_name": "Smith",
                "filing_party_role": "plaintiff",
                "document_path": "/tmp/test.pdf",
                "is_sealed": True,
            },
        )
        assert response.status_code == 403
        assert "sealed" in response.json()["error"].lower()

    def test_unsealed_submit_still_works(self, client: TestClient) -> None:
        response = client.post(
            "/api/filing/submit",
            json={
                "court_id": "nysd",
                "case_number": "1:24-cv-01234",
                "event_code": "12",
                "event_description": "Motion to Dismiss",
                "filing_party_name": "Smith",
                "filing_party_role": "plaintiff",
                "document_path": "/tmp/test.pdf",
            },
        )
        assert response.status_code == 200

    def test_analyze_with_sealed_exhibit_403(self, client: TestClient) -> None:
        response = client.post(
            "/api/file",
            files={"document": ("m.pdf", b"%PDF-1.4 minimal", "application/pdf")},
            data={"exhibits": '[{"name": "x.pdf", "sealed": true}]'},
        )
        assert response.status_code == 403
        assert "sealed" in response.json()["error"].lower()
