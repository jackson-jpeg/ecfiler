"""Tests for pre-flight filing checks."""

from pathlib import Path

import pytest

from ecfiler.filing.models import (
    CaseInfo,
    CaseOpeningData,
    CourtType,
    Document,
    DocumentValidation,
    EventCode,
    Filing,
    FilingParty,
    PartyInfo,
    RelatedEntry,
    SealingLevel,
)
from ecfiler.filing.preflight import PreflightResult, run_preflight


def _make_filing(**kwargs) -> Filing:
    """Helper to create a Filing with sensible defaults."""
    defaults = dict(
        court_id="nysd",
        case=CaseInfo(case_number="1:24-cv-01234"),
        event=EventCode(code="12", description="Motion to Dismiss"),
        documents=[
            Document(
                file_path=__file__,  # Use this test file as a stand-in
                is_main=True,
                validation=DocumentValidation(valid=True, file_size_mb=1.0, page_count=5),
            )
        ],
        filing_party=FilingParty(
            party_name="Smith", party_role="plaintiff", attorney_name="Doe"
        ),
    )
    defaults.update(kwargs)
    return Filing(**defaults)


class TestPreflightBasic:
    def test_valid_filing_passes(self) -> None:
        result = run_preflight(_make_filing())
        assert result.passed
        assert len(result.errors) == 0

    def test_no_documents_fails(self) -> None:
        result = run_preflight(_make_filing(documents=[]))
        assert not result.passed
        assert any("No documents" in e for e in result.errors)

    def test_missing_main_document_file_fails(self) -> None:
        filing = _make_filing(
            documents=[
                Document(
                    file_path="/nonexistent/file.pdf",
                    is_main=True,
                    validation=DocumentValidation(valid=True),
                )
            ]
        )
        result = run_preflight(filing)
        assert not result.passed
        assert any("not found" in e for e in result.errors)

    def test_invalid_document_fails(self) -> None:
        filing = _make_filing(
            documents=[
                Document(
                    file_path=__file__,
                    is_main=True,
                    validation=DocumentValidation(valid=False, errors=["Too large"]),
                )
            ]
        )
        result = run_preflight(filing)
        assert not result.passed

    def test_no_court_fails(self) -> None:
        result = run_preflight(_make_filing(court_id=""))
        assert not result.passed

    def test_invalid_court_fails(self) -> None:
        result = run_preflight(_make_filing(court_id="zzz_nonexistent"))
        assert not result.passed

    def test_no_event_code_fails(self) -> None:
        result = run_preflight(
            _make_filing(event=EventCode(code="", description=""))
        )
        assert not result.passed


class TestPreflightParty:
    def test_no_filing_party_warns(self) -> None:
        result = run_preflight(_make_filing(filing_party=None))
        assert result.passed  # Warning, not error
        assert any("filing party" in w.lower() for w in result.warnings)

    def test_empty_party_name_fails(self) -> None:
        result = run_preflight(
            _make_filing(
                filing_party=FilingParty(party_name="", party_role="plaintiff")
            )
        )
        assert not result.passed


class TestPreflightSealing:
    def test_sealed_document_warns(self) -> None:
        filing = _make_filing(
            documents=[
                Document(
                    file_path=__file__,
                    is_main=True,
                    validation=DocumentValidation(valid=True),
                    sealing=SealingLevel.SEALED,
                    description="Confidential settlement exhibit",
                )
            ]
        )
        result = run_preflight(filing)
        assert any("sealed" in w.lower() for w in result.warnings)

    def test_sealed_without_description_is_error(self) -> None:
        filing = _make_filing(
            documents=[
                Document(
                    file_path=__file__,
                    is_main=True,
                    validation=DocumentValidation(valid=True),
                    sealing=SealingLevel.SEALED,
                )
            ]
        )
        result = run_preflight(filing)
        assert not result.passed
        assert any("no description" in e.lower() for e in result.errors)

    def test_ex_parte_warns(self) -> None:
        filing = _make_filing(
            documents=[
                Document(
                    file_path=__file__,
                    is_main=True,
                    validation=DocumentValidation(valid=True),
                    sealing=SealingLevel.EX_PARTE,
                )
            ]
        )
        result = run_preflight(filing)
        assert any("ex parte" in w.lower() for w in result.warnings)


class TestPreflightResponse:
    def test_response_without_related_entry_warns(self) -> None:
        result = run_preflight(_make_filing(is_response=True, related_entry=None))
        assert any("response" in w.lower() for w in result.warnings)

    def test_response_with_empty_docket_fails(self) -> None:
        result = run_preflight(
            _make_filing(
                is_response=True,
                related_entry=RelatedEntry(docket_number=""),
            )
        )
        assert not result.passed

    def test_response_with_docket_passes(self) -> None:
        result = run_preflight(
            _make_filing(
                is_response=True,
                related_entry=RelatedEntry(docket_number="45", description="Motion"),
            )
        )
        assert result.passed


class TestPreflightCaseOpening:
    def test_case_opening_no_type_fails(self) -> None:
        result = run_preflight(
            _make_filing(case_opening=CaseOpeningData(case_type=""))
        )
        assert not result.passed

    def test_case_opening_no_parties_fails(self) -> None:
        result = run_preflight(
            _make_filing(case_opening=CaseOpeningData(case_type="cv"))
        )
        assert not result.passed

    def test_bankruptcy_no_chapter_fails(self) -> None:
        result = run_preflight(
            _make_filing(
                case_opening=CaseOpeningData(
                    case_type="bk",
                    chapter="",
                    plaintiffs=[PartyInfo(name="Debtor", role="debtor")],
                )
            )
        )
        assert not result.passed

    def test_civil_no_jurisdiction_warns(self) -> None:
        result = run_preflight(
            _make_filing(
                case_opening=CaseOpeningData(
                    case_type="cv",
                    plaintiffs=[PartyInfo(name="P", role="plaintiff")],
                    defendants=[PartyInfo(name="D", role="defendant")],
                )
            )
        )
        assert any("jurisdiction" in w.lower() for w in result.warnings)


class TestPreflightAmended:
    def test_amended_without_reference_warns(self) -> None:
        filing = _make_filing(
            documents=[
                Document(
                    file_path=__file__,
                    is_main=True,
                    validation=DocumentValidation(valid=True),
                    is_amended=True,
                    amends_docket_number="",
                )
            ]
        )
        result = run_preflight(filing)
        assert any("amended" in w.lower() for w in result.warnings)

    def test_amended_with_reference_passes(self) -> None:
        filing = _make_filing(
            documents=[
                Document(
                    file_path=__file__,
                    is_main=True,
                    validation=DocumentValidation(valid=True),
                    is_amended=True,
                    amends_docket_number="23",
                )
            ]
        )
        result = run_preflight(filing)
        assert result.passed


class TestPreflightSealKeywords:
    def test_seal_keyword_without_sealed_flag_is_error(self) -> None:
        result = run_preflight(
            _make_filing(event=EventCode(code="99", description="Motion to Seal Document"))
        )
        assert not result.passed
        assert any("sealing-related" in e.lower() for e in result.errors)

    def test_seal_keyword_in_docket_text_is_error(self) -> None:
        result = run_preflight(
            _make_filing(docket_text="Exhibit A filed under seal per protective order")
        )
        assert not result.passed

    def test_confirmed_public_passes_keyword_gate(self) -> None:
        result = run_preflight(
            _make_filing(
                event=EventCode(code="99", description="Response to Motion to Seal"),
                confirmed_public=True,
            )
        )
        assert result.passed

    def test_sealed_filing_skips_keyword_gate(self) -> None:
        from ecfiler.filing.models import Document, DocumentValidation, SealingLevel

        result = run_preflight(
            _make_filing(
                event=EventCode(code="99", description="Sealed Motion"),
                documents=[
                    Document(
                        file_path=__file__,
                        is_main=True,
                        validation=DocumentValidation(valid=True),
                        sealing=SealingLevel.SEALED,
                        description="Sealed per protective order",
                    )
                ],
            )
        )
        # No keyword error; the sealing checks themselves handle sealed docs
        assert not any("sealing-related" in e.lower() for e in result.errors)

    def test_no_keywords_passes(self) -> None:
        result = run_preflight(_make_filing())
        assert result.passed

    def test_ex_parte_keyword_detected(self) -> None:
        from ecfiler.filing.preflight import scan_seal_keywords

        assert scan_seal_keywords("Ex Parte Motion for TRO") == ["ex parte"]
        assert scan_seal_keywords("Motion for Extension") == []
