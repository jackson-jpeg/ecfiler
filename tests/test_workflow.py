"""Tests for filing workflow models and event codes."""

import pytest

from ecfiler.filing.events import (
    get_common_events,
    get_event_categories,
    search_events,
)
from ecfiler.filing.models import (
    CaseInfo,
    CaseOpeningData,
    CourtType,
    Document,
    DocumentValidation,
    EventCode,
    Filing,
    FilingParty,
    FilingStatus,
    PartyInfo,
)


class TestFilingModels:
    def test_document_filename(self) -> None:
        doc = Document(file_path="/path/to/motion.pdf")
        assert doc.filename == "motion.pdf"

    def test_document_validity(self) -> None:
        doc = Document(file_path="test.pdf")
        assert not doc.is_valid  # No validation yet

        doc.validation = DocumentValidation(valid=True, file_size_mb=1.0, page_count=5)
        assert doc.is_valid

    def test_filing_main_document(self) -> None:
        filing = Filing(
            court_id="nysd",
            case=CaseInfo(case_number="1:24-cv-01234"),
            event=EventCode(code="12", description="Motion to Dismiss"),
            documents=[
                Document(file_path="main.pdf", is_main=True),
                Document(file_path="exhibit_a.pdf", is_main=False),
            ],
        )
        assert filing.main_document is not None
        assert filing.main_document.filename == "main.pdf"
        assert len(filing.attachments) == 1
        assert filing.attachments[0].filename == "exhibit_a.pdf"

    def test_filing_status_default(self) -> None:
        filing = Filing(
            court_id="nysd",
            case=CaseInfo(case_number="1:24-cv-01234"),
            event=EventCode(code="12", description="Motion"),
        )
        assert filing.status == FilingStatus.INIT

    def test_court_type_enum(self) -> None:
        assert CourtType.DISTRICT.value == "district"
        assert CourtType.BANKRUPTCY.value == "bankruptcy"
        assert CourtType.APPELLATE.value == "appellate"

    def test_filing_party(self) -> None:
        fp = FilingParty(
            party_name="Smith Corp",
            party_role="defendant",
            attorney_name="Jane Doe",
            attorney_bar_number="JD5678",
        )
        assert "Smith Corp" in fp.display
        assert "defendant" in fp.display
        assert "Jane Doe" in fp.display

    def test_case_info_parties(self) -> None:
        case = CaseInfo(
            case_number="1:24-cv-01234",
            parties=[
                PartyInfo(name="Smith", role="plaintiff"),
                PartyInfo(name="Jones Corp", role="defendant"),
                PartyInfo(name="Doe", role="defendant"),
            ],
        )
        assert case.plaintiff_names == ["Smith"]
        assert len(case.defendant_names) == 2

    def test_case_opening_data(self) -> None:
        data = CaseOpeningData(
            case_type="cv",
            cause_of_action="42 USC 1983",
            jurisdiction_basis="federal_question",
            plaintiffs=[PartyInfo(name="Smith", role="plaintiff")],
            defendants=[PartyInfo(name="City of X", role="defendant")],
        )
        assert not data.is_bankruptcy
        assert len(data.all_parties) == 2

    def test_case_opening_bankruptcy(self) -> None:
        data = CaseOpeningData(
            case_type="bk",
            chapter="7",
            plaintiffs=[PartyInfo(name="Debtor", role="debtor")],
        )
        assert data.is_bankruptcy

    def test_filing_is_case_opening(self) -> None:
        filing = Filing(
            court_id="nysd",
            case=CaseInfo(case_number="NEW"),
            event=EventCode(code="400", description="Complaint"),
            case_opening=CaseOpeningData(case_type="cv"),
        )
        assert filing.is_case_opening

    def test_filing_not_case_opening(self) -> None:
        filing = Filing(
            court_id="nysd",
            case=CaseInfo(case_number="1:24-cv-01234"),
            event=EventCode(code="12", description="Motion"),
        )
        assert not filing.is_case_opening

    def test_filing_response_flag(self) -> None:
        filing = Filing(
            court_id="nysd",
            case=CaseInfo(case_number="1:24-cv-01234"),
            event=EventCode(code="301", description="Response"),
            is_response=True,
        )
        assert filing.is_response


class TestEventCodes:
    def test_get_district_events(self) -> None:
        events = get_common_events("district")
        assert len(events) > 0
        assert all(isinstance(e, EventCode) for e in events)

    def test_get_bankruptcy_events(self) -> None:
        events = get_common_events("bankruptcy")
        assert len(events) > 0

    def test_get_appellate_events(self) -> None:
        events = get_common_events("appellate")
        assert len(events) > 0

    def test_search_events(self) -> None:
        results = search_events("motion to dismiss", "district")
        assert len(results) >= 1
        assert any("dismiss" in e.description.lower() for e in results)

    def test_search_no_results(self) -> None:
        results = search_events("xyznonexistent", "district")
        assert len(results) == 0

    def test_get_categories(self) -> None:
        categories = get_event_categories("district")
        assert "Motions" in categories
        assert "Briefs and Memoranda" in categories
        assert "Notices" in categories

    def test_bankruptcy_categories(self) -> None:
        categories = get_event_categories("bankruptcy")
        assert "Petitions" in categories or "Claims" in categories

    def test_appellate_categories(self) -> None:
        categories = get_event_categories("appellate")
        assert "Briefs" in categories
