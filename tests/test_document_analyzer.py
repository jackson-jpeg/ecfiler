"""Tests for document analysis models."""

import pytest

from ecfiler.agent.document_analyzer import DocumentAnalysis


class TestDocumentAnalysis:
    def test_complete_analysis(self) -> None:
        analysis = DocumentAnalysis(
            document_type="motion",
            document_type_specific="Motion to Dismiss",
            case_number="1:24-cv-01234",
            court_id="nysd",
            filing_party_name="Smith",
        )
        assert analysis.is_complete
        assert analysis.completeness_score > 50
        assert len(analysis.missing_fields) == 0

    def test_incomplete_analysis(self) -> None:
        analysis = DocumentAnalysis(
            document_type="motion",
        )
        assert not analysis.is_complete
        assert "case_number" in analysis.missing_fields
        assert "filing_party" in analysis.missing_fields

    def test_completeness_score(self) -> None:
        # All fields filled
        full = DocumentAnalysis(
            document_type="brief",
            case_number="1:24-cv-01234",
            court_id="nysd",
            filing_party_name="Jones",
            filing_party_role="defendant",
            attorney_name="Jane Doe",
            suggested_event_code_category="Briefs",
        )
        assert full.completeness_score == 100

        # No fields filled
        empty = DocumentAnalysis()
        assert empty.completeness_score == 0

    def test_missing_fields(self) -> None:
        analysis = DocumentAnalysis(
            document_type="motion",
            case_number="1:24-cv-01234",
            # Missing court and filing_party
        )
        missing = analysis.missing_fields
        assert "court" in missing
        assert "filing_party" in missing
        assert "case_number" not in missing
        assert "document_type" not in missing

    def test_response_fields(self) -> None:
        analysis = DocumentAnalysis(
            is_response=True,
            responds_to="Motion to Dismiss (Dkt. #45)",
            responds_to_docket_number="45",
        )
        assert analysis.is_response
        assert "45" in analysis.responds_to_docket_number

    def test_completeness_checks(self) -> None:
        analysis = DocumentAnalysis(
            has_certificate_of_service=True,
            has_signature=True,
            has_proposed_order=False,
        )
        assert analysis.has_certificate_of_service
        assert analysis.has_signature
        assert not analysis.has_proposed_order
