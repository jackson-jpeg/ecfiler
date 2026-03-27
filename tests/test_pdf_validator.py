"""Tests for PDF validation."""

import tempfile
from pathlib import Path

import pytest

from ecfiler.pdf.validator import ValidationResult, extract_title, validate_pdf


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a minimal valid PDF for testing."""
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Sample filing document for testing purposes.")
    page.insert_text((72, 100), "This is a test document with searchable text.")
    pdf_path = tmp_path / "sample.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def empty_pdf(tmp_path: Path) -> Path:
    """Create a PDF with no text (scanned-like)."""
    import fitz

    doc = fitz.open()
    doc.new_page()  # Empty page
    pdf_path = tmp_path / "empty.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def large_file(tmp_path: Path) -> Path:
    """Create a file that's too large."""
    path = tmp_path / "large.pdf"
    # Write minimal PDF header + padding to exceed limit
    path.write_bytes(b"%PDF-1.4\n" + b"0" * (2 * 1024 * 1024))  # 2MB
    return path


class TestValidatePdf:
    def test_valid_pdf(self, sample_pdf: Path) -> None:
        result = validate_pdf(sample_pdf)
        assert result.valid
        assert result.has_text
        assert not result.is_encrypted
        assert result.page_count == 1
        assert result.file_size_mb > 0
        assert len(result.errors) == 0

    def test_nonexistent_file(self) -> None:
        result = validate_pdf("/nonexistent/file.pdf")
        assert not result.valid
        assert "not found" in result.errors[0].lower()

    def test_wrong_extension(self, tmp_path: Path) -> None:
        path = tmp_path / "document.doc"
        path.write_text("not a pdf")
        result = validate_pdf(path)
        assert not result.valid

    def test_empty_file(self, tmp_path: Path) -> None:
        path = tmp_path / "empty.pdf"
        path.write_bytes(b"")
        result = validate_pdf(path)
        assert not result.valid
        assert any("empty" in e.lower() for e in result.errors)

    def test_no_text_warning(self, empty_pdf: Path) -> None:
        result = validate_pdf(empty_pdf)
        # Should be valid (it's a real PDF) but with a warning about text
        assert result.valid  # No text is a warning, not an error
        assert any("searchable" in w.lower() or "text" in w.lower() for w in result.warnings)

    def test_size_limit(self, sample_pdf: Path) -> None:
        # Test with a very small limit
        result = validate_pdf(sample_pdf, max_size_mb=0)
        assert not result.valid
        assert any("size" in e.lower() for e in result.errors)

    def test_validation_result_summary(self, sample_pdf: Path) -> None:
        result = validate_pdf(sample_pdf)
        summary = result.summary
        assert "Valid" in summary or "Invalid" in summary


class TestExtractTitle:
    def test_extract_from_text(self, sample_pdf: Path) -> None:
        title = extract_title(sample_pdf)
        assert isinstance(title, str)
        assert len(title) > 0

    def test_fallback_to_filename(self, tmp_path: Path) -> None:
        import fitz

        doc = fitz.open()
        doc.new_page()
        path = tmp_path / "my_motion.pdf"
        doc.save(str(path))
        doc.close()
        title = extract_title(path)
        # Should fall back to stem if no text
        assert isinstance(title, str)
