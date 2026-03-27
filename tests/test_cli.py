"""Tests for CLI subcommands."""

import pytest
from click.testing import CliRunner

from ecfiler.__main__ import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


class TestCli:
    def test_version(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_help(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "ECFiler" in result.output
        assert "courts" in result.output
        assert "validate" in result.output
        assert "setup" in result.output

    def test_courts_list(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["courts"])
        assert result.exit_code == 0
        assert "nysd" in result.output.lower() or "Southern District" in result.output

    def test_courts_filter_appellate(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["courts", "--type", "appellate"])
        assert result.exit_code == 0
        # Should only show appellate courts
        assert "appellate" in result.output.lower()

    def test_courts_search(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["courts", "--search", "california"])
        assert result.exit_code == 0
        assert "California" in result.output or "cacd" in result.output.lower()

    def test_courts_search_no_results(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["courts", "--search", "zzzznotacourt"])
        assert result.exit_code == 0
        assert "No courts found" in result.output

    def test_validate_nonexistent_file(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["validate", "/nonexistent/file.pdf"])
        # Click should catch the missing file before our code
        assert result.exit_code != 0

    def test_validate_real_pdf(self, runner: CliRunner, tmp_path) -> None:
        import fitz

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Test filing document.")
        pdf_path = tmp_path / "test.pdf"
        doc.save(str(pdf_path))
        doc.close()

        result = runner.invoke(main, ["validate", str(pdf_path)])
        assert result.exit_code == 0
        assert "VALID" in result.output

    def test_validate_with_no_redaction(self, runner: CliRunner, tmp_path) -> None:
        import fitz

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Clean document.")
        pdf_path = tmp_path / "clean.pdf"
        doc.save(str(pdf_path))
        doc.close()

        result = runner.invoke(main, ["validate", "--no-redaction", str(pdf_path)])
        assert result.exit_code == 0
        assert "VALID" in result.output

    def test_history_empty(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["history"])
        assert result.exit_code == 0

    def test_convert_help(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["convert", "--help"])
        assert result.exit_code == 0
        assert "PDF/A" in result.output or "pdf" in result.output.lower()

    def test_setup_help(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["setup", "--help"])
        assert result.exit_code == 0
        assert "PACER" in result.output or "credential" in result.output.lower()
