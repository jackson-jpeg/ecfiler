"""Browser automation smoke test: upload_attachment called per exhibit with label."""

from __future__ import annotations

from unittest.mock import MagicMock

from ecfiler.browser.filing import FilingAutomation
from ecfiler.courts.base import BaseCourt, CourtProfile
from ecfiler.filing.models import (
    CaseInfo,
    Document,
    EventCode,
    ExhibitEntry,
    ExhibitPackageModel,
    Filing,
)


def test_upload_attachments_iterates_package_with_labels() -> None:
    court = BaseCourt(CourtProfile(
        court_id="nysd", name="SDNY", court_type="district",
        ecf_url="https://nysd.uscourts.gov",
    ))
    court.upload_attachment = MagicMock()  # type: ignore[method-assign]

    filing = Filing(
        court_id="nysd",
        case=CaseInfo(case_number="1:24-cv-01234"),
        event=EventCode(code="12", description="Motion"),
        documents=[
            Document(file_path="/tmp/main.pdf", is_main=True),
            Document(file_path="/tmp/a.pdf", is_main=False, description="Contract"),
            Document(file_path="/tmp/b.pdf", is_main=False, description="Emails"),
        ],
        exhibit_package=ExhibitPackageModel(
            exhibits=[
                ExhibitEntry(file_path="/tmp/a.pdf", label="Exhibit A", description="Contract"),
                ExhibitEntry(file_path="/tmp/b.pdf", label="Exhibit B", description="Emails"),
            ],
        ),
    )

    browser = MagicMock()
    browser.page = MagicMock()

    automation = FilingAutomation(court=court, browser=browser, filing=filing)
    automation._upload_attachments()

    assert court.upload_attachment.call_count == 2
    call_a = court.upload_attachment.call_args_list[0]
    call_b = court.upload_attachment.call_args_list[1]

    assert call_a.args[1] == "/tmp/a.pdf"
    assert call_a.kwargs["label"] == "Exhibit A"
    assert call_a.kwargs["description"] == "Contract"

    assert call_b.args[1] == "/tmp/b.pdf"
    assert call_b.kwargs["label"] == "Exhibit B"
    assert call_b.kwargs["description"] == "Emails"


def test_upload_attachments_falls_back_without_package() -> None:
    court = BaseCourt(CourtProfile(
        court_id="nysd", name="SDNY", court_type="district",
        ecf_url="https://nysd.uscourts.gov",
    ))
    court.upload_attachment = MagicMock()  # type: ignore[method-assign]

    filing = Filing(
        court_id="nysd",
        case=CaseInfo(case_number="1:24-cv-01234"),
        event=EventCode(code="12", description="Motion"),
        documents=[
            Document(file_path="/tmp/main.pdf", is_main=True),
            Document(file_path="/tmp/a.pdf", is_main=False, description="Contract"),
        ],
    )

    browser = MagicMock()
    browser.page = MagicMock()

    automation = FilingAutomation(court=court, browser=browser, filing=filing)
    automation._upload_attachments()

    assert court.upload_attachment.call_count == 1
    # Legacy 2-arg call (no label kwarg)
    assert court.upload_attachment.call_args.args[1] == "/tmp/a.pdf"
