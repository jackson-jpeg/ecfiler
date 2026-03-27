"""PDF validation for CM/ECF filing requirements.

Checks:
- File is a valid PDF
- File size under court limit (default 100MB)
- Contains searchable/extractable text
- No password protection
- No fillable form fields
- Optionally checks PDF/A conformance
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import fitz  # PyMuPDF
import pikepdf


@dataclass
class ValidationResult:
    """Result of PDF validation."""

    valid: bool
    file_path: str
    file_size_mb: float
    page_count: int
    has_text: bool
    is_encrypted: bool
    has_form_fields: bool
    is_pdfa: bool | None  # None = not checked
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        status = "✓ Valid" if self.valid else "✗ Invalid"
        parts = [
            f"{status}",
            f"{self.file_size_mb:.1f}MB",
            f"{self.page_count} pages",
            "searchable" if self.has_text else "NOT searchable",
        ]
        return ", ".join(parts)


def validate_pdf(
    file_path: str | Path,
    max_size_mb: int = 100,
    check_pdfa: bool = False,
) -> ValidationResult:
    """Validate a PDF file against CM/ECF requirements.

    Args:
        file_path: Path to the PDF file
        max_size_mb: Maximum file size in megabytes
        check_pdfa: Whether to check PDF/A conformance

    Returns:
        ValidationResult with all check outcomes
    """
    path = Path(file_path)
    errors: list[str] = []
    warnings: list[str] = []

    # --- Existence & extension ---
    if not path.exists():
        return ValidationResult(
            valid=False,
            file_path=str(path),
            file_size_mb=0,
            page_count=0,
            has_text=False,
            is_encrypted=False,
            has_form_fields=False,
            is_pdfa=None,
            errors=[f"File not found: {path}"],
        )

    if path.suffix.lower() != ".pdf":
        errors.append(f"File extension is '{path.suffix}', expected '.pdf'")

    # --- File size ---
    size_bytes = path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    if size_mb > max_size_mb:
        errors.append(f"File size {size_mb:.1f}MB exceeds {max_size_mb}MB limit")

    if size_mb == 0:
        errors.append("File is empty (0 bytes)")
        return ValidationResult(
            valid=False,
            file_path=str(path),
            file_size_mb=0,
            page_count=0,
            has_text=False,
            is_encrypted=False,
            has_form_fields=False,
            is_pdfa=None,
            errors=errors,
        )

    # --- Open with pikepdf for structure checks ---
    is_encrypted = False
    has_form_fields = False
    is_pdfa: bool | None = None

    try:
        with pikepdf.open(path) as pdf:
            page_count = len(pdf.pages)

            # Check for encryption (even if opened, it may have been encrypted)
            is_encrypted = pdf.is_encrypted

            # Check for form fields (AcroForm)
            if "/AcroForm" in pdf.Root:
                acroform = pdf.Root["/AcroForm"]
                if "/Fields" in acroform and len(acroform["/Fields"]) > 0:
                    has_form_fields = True
                    warnings.append(
                        "PDF contains fillable form fields. "
                        "CM/ECF may reject it — consider flattening."
                    )

            # Check PDF/A conformance via metadata
            if check_pdfa:
                is_pdfa = _check_pdfa_metadata(pdf)
                if not is_pdfa:
                    warnings.append("Not PDF/A conformant. Some courts prefer PDF/A.")

    except pikepdf.PasswordError:
        is_encrypted = True
        errors.append("PDF is password-protected. CM/ECF does not accept encrypted PDFs.")
        return ValidationResult(
            valid=False,
            file_path=str(path),
            file_size_mb=size_mb,
            page_count=0,
            has_text=False,
            is_encrypted=True,
            has_form_fields=False,
            is_pdfa=None,
            errors=errors,
        )
    except Exception as e:
        errors.append(f"Cannot open PDF: {e}")
        return ValidationResult(
            valid=False,
            file_path=str(path),
            file_size_mb=size_mb,
            page_count=0,
            has_text=False,
            is_encrypted=False,
            has_form_fields=False,
            is_pdfa=None,
            errors=errors,
        )

    if is_encrypted:
        errors.append("PDF is encrypted. CM/ECF does not accept encrypted PDFs.")

    # --- Text extraction check with PyMuPDF ---
    has_text = False
    try:
        doc = fitz.open(str(path))
        # Check first 5 pages for text (sufficient to determine searchability)
        for i in range(min(5, len(doc))):
            page_text = doc[i].get_text().strip()
            if len(page_text) > 20:
                has_text = True
                break
        doc.close()
    except Exception:
        warnings.append("Could not extract text — PDF may not be searchable.")

    if not has_text:
        warnings.append(
            "No searchable text detected. CM/ECF requires searchable PDFs. "
            "Consider running OCR (ocrmypdf)."
        )

    is_valid = len(errors) == 0
    return ValidationResult(
        valid=is_valid,
        file_path=str(path),
        file_size_mb=size_mb,
        page_count=page_count,
        has_text=has_text,
        is_encrypted=is_encrypted,
        has_form_fields=has_form_fields,
        is_pdfa=is_pdfa,
        errors=errors,
        warnings=warnings,
    )


def extract_text(file_path: str | Path, max_pages: int = 50) -> str:
    """Extract text from a PDF for Claude analysis.

    Args:
        file_path: Path to PDF
        max_pages: Maximum pages to extract (for large documents)

    Returns:
        Extracted text content
    """
    doc = fitz.open(str(file_path))
    pages = []
    for i in range(min(max_pages, len(doc))):
        pages.append(doc[i].get_text())
    doc.close()
    return "\n\n--- PAGE BREAK ---\n\n".join(pages)


def extract_title(file_path: str | Path) -> str:
    """Try to extract the document title from PDF metadata or first page."""
    try:
        doc = fitz.open(str(file_path))
        # Try metadata title first
        metadata = doc.metadata
        if metadata and metadata.get("title"):
            title = metadata["title"].strip()
            if len(title) > 5:
                doc.close()
                return title

        # Fall back to first line of first page
        if len(doc) > 0:
            text = doc[0].get_text().strip()
            first_line = text.split("\n")[0].strip() if text else ""
            doc.close()
            return first_line[:200] if first_line else Path(file_path).stem

        doc.close()
    except Exception:
        pass

    return Path(file_path).stem


def _check_pdfa_metadata(pdf: pikepdf.Pdf) -> bool:
    """Check if PDF claims PDF/A conformance in XMP metadata."""
    try:
        with pdf.open_metadata() as meta:
            xmp = str(meta)
            return "pdfaid" in xmp.lower() or "PDF/A" in xmp
    except Exception:
        return False
