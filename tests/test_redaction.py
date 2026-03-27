"""Tests for redaction scanning."""

import pytest

from ecfiler.pdf.redaction_check import RedactionReport, regex_scan, scan_document


class TestRegexScan:
    def test_detects_ssn(self) -> None:
        text = "Plaintiff's SSN is 123-45-6789."
        issues = regex_scan(text)
        assert len(issues) >= 1
        assert any(i.issue_type == "ssn" for i in issues)
        assert any("123-45-6789" in i.text for i in issues)

    def test_detects_ssn_with_spaces(self) -> None:
        text = "Social Security Number: 123 45 6789"
        issues = regex_scan(text)
        assert any(i.issue_type == "ssn" for i in issues)

    def test_detects_dob(self) -> None:
        text = "Date of Birth: 03/15/1985"
        issues = regex_scan(text)
        assert any(i.issue_type == "dob" for i in issues)

    def test_detects_account_number(self) -> None:
        text = "Account #: 1234567890"
        issues = regex_scan(text)
        assert any(i.issue_type == "account_number" for i in issues)

    def test_detects_credit_card(self) -> None:
        text = "Card number 4111-2222-3333-4444 was used."
        issues = regex_scan(text)
        assert any(i.issue_type == "account_number" for i in issues)

    def test_detects_ein_in_context(self) -> None:
        text = "Employer Identification Number: 12-3456789"
        issues = regex_scan(text)
        assert any(i.issue_type == "ssn" for i in issues)  # EINs flagged as tax IDs

    def test_no_false_positive_on_clean_text(self) -> None:
        text = (
            "This is a motion to dismiss the complaint filed by plaintiff "
            "against defendant corporation. The court should grant the motion "
            "for the following reasons."
        )
        issues = regex_scan(text)
        assert len(issues) == 0

    def test_no_false_positive_on_case_number(self) -> None:
        text = "Case No. 1:24-cv-01234-ABC"
        issues = regex_scan(text)
        # Case numbers should not trigger SSN detection
        assert not any(i.issue_type == "ssn" and i.confidence == "high" for i in issues)


class TestScanDocument:
    def test_clean_document(self) -> None:
        text = "This is a clean legal document with no personal identifiers."
        report = scan_document(text)
        assert report.risk_level == "none"
        assert not report.has_issues

    def test_document_with_ssn(self) -> None:
        text = "The debtor's SSN is 123-45-6789 and their DOB is 01/01/1980."
        report = scan_document(text)
        assert report.risk_level == "high"
        assert report.has_issues
        assert report.high_risk_count >= 1
