"""Tests for batch PDF validation CLI command."""

from pathlib import Path

import fitz
import pytest
from click.testing import CliRunner

from ecfiler.__main__ import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def pdf_dir(tmp_path: Path) -> Path:
    """Create a directory with multiple test PDFs."""
    for name, text in [
        ("motion.pdf", "Motion to Dismiss pursuant to Rule 12(b)(6)."),
        ("brief.pdf", "Memorandum of Law in Support of Motion."),
        ("exhibit_a.pdf", "Exhibit A — Contract dated January 1, 2024."),
    ]:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), text)
        doc.save(str(tmp_path / name))
        doc.close()
    return tmp_path


class TestBatchValidate:
    def test_validate_multiple(self, runner: CliRunner, pdf_dir: Path) -> None:
        files = [str(pdf_dir / f) for f in ["motion.pdf", "brief.pdf", "exhibit_a.pdf"]]
        result = runner.invoke(main, ["batch-validate"] + files)
        assert result.exit_code == 0
        assert "3 passed" in result.output
        assert "0 failed" in result.output

    def test_validate_with_bad_file(self, runner: CliRunner, pdf_dir: Path, tmp_path: Path) -> None:
        bad = tmp_path / "bad.pdf"
        bad.write_bytes(b"")
        files = [str(pdf_dir / "motion.pdf"), str(bad)]
        result = runner.invoke(main, ["batch-validate"] + files)
        assert result.exit_code == 0
        assert "1 passed" in result.output
        assert "1 failed" in result.output

    def test_no_files(self, runner: CliRunner) -> None:
        result = runner.invoke(main, ["batch-validate"])
        assert result.exit_code == 0
        assert "No files" in result.output

    def test_no_redaction(self, runner: CliRunner, pdf_dir: Path) -> None:
        files = [str(pdf_dir / "motion.pdf")]
        result = runner.invoke(main, ["batch-validate", "--no-redaction"] + files)
        assert result.exit_code == 0
        assert "1 passed" in result.output

    def test_redaction_detects_ssn(self, runner: CliRunner, tmp_path: Path) -> None:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "SSN: 123-45-6789")
        pdf = tmp_path / "ssn.pdf"
        doc.save(str(pdf))
        doc.close()

        result = runner.invoke(main, ["batch-validate", str(pdf)])
        assert result.exit_code == 0
        assert "issue" in result.output.lower()
