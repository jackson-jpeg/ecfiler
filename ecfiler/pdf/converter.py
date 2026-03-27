"""PDF/A conversion and OCR for court filing compliance.

Uses ocrmypdf (optional dependency) for:
- Converting standard PDFs to PDF/A format
- Adding OCR text layer to scanned documents
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConversionResult:
    success: bool
    output_path: str
    message: str


def is_ocrmypdf_available() -> bool:
    """Check if ocrmypdf is installed."""
    return shutil.which("ocrmypdf") is not None


def convert_to_pdfa(
    input_path: str | Path,
    output_path: str | Path | None = None,
    add_ocr: bool = True,
) -> ConversionResult:
    """Convert a PDF to PDF/A format, optionally adding OCR.

    Args:
        input_path: Source PDF path
        output_path: Destination path (default: adds _pdfa suffix)
        add_ocr: Whether to add OCR text layer if missing

    Returns:
        ConversionResult with success status and output path
    """
    if not is_ocrmypdf_available():
        return ConversionResult(
            success=False,
            output_path="",
            message=(
                "ocrmypdf is not installed. Install with: "
                "pip install 'ecfiler[pdf-convert]' && apt install ghostscript tesseract-ocr"
            ),
        )

    inp = Path(input_path)
    if output_path is None:
        out = inp.with_stem(inp.stem + "_pdfa")
    else:
        out = Path(output_path)

    cmd = [
        "ocrmypdf",
        "--output-type", "pdfa-2",
        "--pdfa-image-compression", "jpeg",
    ]

    if add_ocr:
        cmd.append("--skip-text")  # Only OCR pages without text
    else:
        cmd.append("--skip-text")

    cmd.extend([str(inp), str(out)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout for large PDFs
        )

        if result.returncode == 0:
            return ConversionResult(
                success=True,
                output_path=str(out),
                message=f"Converted to PDF/A: {out}",
            )
        else:
            return ConversionResult(
                success=False,
                output_path="",
                message=f"ocrmypdf failed: {result.stderr.strip()}",
            )

    except subprocess.TimeoutExpired:
        return ConversionResult(
            success=False,
            output_path="",
            message="PDF/A conversion timed out (>5 minutes). Try a smaller file.",
        )
    except Exception as e:
        return ConversionResult(
            success=False,
            output_path="",
            message=f"Conversion error: {e}",
        )


def add_ocr_layer(
    input_path: str | Path,
    output_path: str | Path | None = None,
) -> ConversionResult:
    """Add OCR text layer to a scanned PDF without converting to PDF/A.

    Args:
        input_path: Source PDF path
        output_path: Destination path (default: adds _ocr suffix)
    """
    if not is_ocrmypdf_available():
        return ConversionResult(
            success=False,
            output_path="",
            message="ocrmypdf is not installed.",
        )

    inp = Path(input_path)
    if output_path is None:
        out = inp.with_stem(inp.stem + "_ocr")
    else:
        out = Path(output_path)

    try:
        result = subprocess.run(
            [
                "ocrmypdf",
                "--skip-text",
                "--output-type", "pdf",
                str(inp),
                str(out),
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            return ConversionResult(
                success=True, output_path=str(out), message=f"OCR added: {out}"
            )
        else:
            return ConversionResult(
                success=False,
                output_path="",
                message=f"OCR failed: {result.stderr.strip()}",
            )
    except Exception as e:
        return ConversionResult(success=False, output_path="", message=f"OCR error: {e}")
