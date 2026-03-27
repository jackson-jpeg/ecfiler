"""Tests for setup diagnostics."""

import pytest

from ecfiler.diagnostics import DiagnosticReport, CheckResult, run_diagnostics


class TestCheckResult:
    def test_passed(self) -> None:
        r = CheckResult("test", True, "OK")
        assert r.passed
        assert r.fix == ""

    def test_failed_with_fix(self) -> None:
        r = CheckResult("test", False, "Bad", fix="do this")
        assert not r.passed
        assert r.fix == "do this"


class TestDiagnosticReport:
    def test_all_passed(self) -> None:
        report = DiagnosticReport(checks=[
            CheckResult("a", True, "ok"),
            CheckResult("b", True, "ok"),
        ])
        assert report.all_passed
        assert report.pass_count == 2
        assert report.fail_count == 0

    def test_some_failed(self) -> None:
        report = DiagnosticReport(checks=[
            CheckResult("a", True, "ok"),
            CheckResult("b", False, "bad"),
        ])
        assert not report.all_passed
        assert report.pass_count == 1
        assert report.fail_count == 1

    def test_required_checks(self) -> None:
        report = DiagnosticReport(checks=[
            CheckResult("config", True, "ok"),
            CheckResult("anthropic_key", True, "ok"),
            CheckResult("playwright", False, "missing"),
        ])
        assert report.required_passed  # config + API key are enough
        assert not report.all_passed


class TestRunDiagnostics:
    def test_returns_report(self) -> None:
        report = run_diagnostics()
        assert isinstance(report, DiagnosticReport)
        assert len(report.checks) >= 6

    def test_has_expected_checks(self) -> None:
        report = run_diagnostics()
        check_names = {c.name for c in report.checks}
        assert "config" in check_names
        assert "anthropic_key" in check_names
        assert "pdf_tools" in check_names
        assert "courts" in check_names
        assert "history_db" in check_names

    def test_pdf_tools_pass(self) -> None:
        """pikepdf and PyMuPDF should be installed in dev environment."""
        report = run_diagnostics()
        pdf_check = next(c for c in report.checks if c.name == "pdf_tools")
        assert pdf_check.passed

    def test_courts_pass(self) -> None:
        report = run_diagnostics()
        courts_check = next(c for c in report.checks if c.name == "courts")
        assert courts_check.passed
        assert "150" in courts_check.message or "courts" in courts_check.message.lower()
