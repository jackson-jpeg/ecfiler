"""Tests for PACER search models."""

import pytest

from ecfiler.pacer_search import CaseResult


class TestCaseResult:
    def test_is_open(self) -> None:
        case = CaseResult(
            case_number="1:24-cv-01234",
            case_title="Smith v. Jones",
            court_id="nysd",
            court_name="S.D.N.Y.",
            date_filed="2024-01-15",
            date_closed="",
            judge="Williams",
            case_type="cv",
        )
        assert case.is_open

    def test_is_closed(self) -> None:
        case = CaseResult(
            case_number="1:24-cv-01234",
            case_title="Smith v. Jones",
            court_id="nysd",
            court_name="S.D.N.Y.",
            date_filed="2024-01-15",
            date_closed="2024-12-01",
            judge="Williams",
            case_type="cv",
        )
        assert not case.is_open

    def test_display_open(self) -> None:
        case = CaseResult(
            case_number="1:24-cv-01234",
            case_title="Smith v. Jones",
            court_id="nysd",
            court_name="S.D.N.Y.",
            date_filed="2024-01-15",
            date_closed="",
            judge="Williams",
            case_type="cv",
        )
        display = case.display
        assert "Smith v. Jones" in display
        assert "Williams" in display
        assert "Open" in display

    def test_display_no_judge(self) -> None:
        case = CaseResult(
            case_number="1:24-cv-01234",
            case_title="Smith v. Jones",
            court_id="nysd",
            court_name="S.D.N.Y.",
            date_filed="2024-01-15",
            date_closed="",
            judge="",
            case_type="cv",
        )
        display = case.display
        assert "Smith v. Jones" in display
        assert "Judge" not in display
