"""Tests for FRAP appellate type-volume + compliance-cert validation."""

from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from ecfiler.filing.appellate_rules import (
    AppellateDocType,
    TYPE_VOLUME_LIMITS,
    classify_appellate_doc,
    detect_certificate_of_compliance,
    validate_appellate_document,
)
from ecfiler.pdf.validator import extract_metrics


CERT_BLOCK = (
    "CERTIFICATE OF COMPLIANCE\n"
    "I certify that this brief complies with the type-volume limitation "
    "of FRAP 32(a)(7)(B) because it contains 4,200 words, excluding the "
    "parts exempted by FRAP 32(f), and was prepared in 14-point Times New Roman."
)


def _make_pdf(tmp_path: Path, body: str, name: str = "brief.pdf") -> Path:
    doc = fitz.open()
    words = body.split(" ")
    # ~400 words per page fits comfortably in an 8.5x11 textbox at 10pt.
    per_page = 400
    chunks = [" ".join(words[i : i + per_page]) for i in range(0, len(words), per_page)] or [body]
    for chunk in chunks:
        page = doc.new_page()
        rect = fitz.Rect(72, 72, 540, 720)
        page.insert_textbox(rect, chunk, fontsize=10)
    pdf_path = tmp_path / name
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_extract_metrics_counts_words(tmp_path: Path) -> None:
    body = "one two three four five\nsix seven eight nine ten"
    pdf = _make_pdf(tmp_path, body)
    metrics = extract_metrics(pdf)
    assert metrics.word_count == 10
    assert metrics.page_count == 1
    assert metrics.line_count >= 2


def test_classify_appellate_doc() -> None:
    assert classify_appellate_doc("Reply Brief") == AppellateDocType.REPLY_BRIEF
    assert classify_appellate_doc("Appellant's Opening Brief") == AppellateDocType.PRINCIPAL_BRIEF
    assert classify_appellate_doc("Amicus Curiae Brief") == AppellateDocType.AMICUS
    assert classify_appellate_doc("Petition for Rehearing En Banc") == AppellateDocType.PETITION_REHEARING
    assert classify_appellate_doc("Notice of Appearance") == AppellateDocType.OTHER
    assert classify_appellate_doc(None) == AppellateDocType.OTHER


def test_detect_certificate_present() -> None:
    assert detect_certificate_of_compliance(CERT_BLOCK) is True


def test_detect_certificate_absent() -> None:
    assert detect_certificate_of_compliance("Just a boring motion body.") is False
    # A passing mention of "certificate" shouldn't trigger a false positive.
    assert detect_certificate_of_compliance("Certificate of Service attached.") is False


def test_principal_brief_under_limit_passes() -> None:
    result = validate_appellate_document(
        AppellateDocType.PRINCIPAL_BRIEF,
        word_count=10000,
        page_count=40,
        line_count=900,
        text=CERT_BLOCK,
    )
    assert result.passed
    assert result.has_certificate_of_compliance


def test_principal_brief_over_limit_fails() -> None:
    result = validate_appellate_document(
        AppellateDocType.PRINCIPAL_BRIEF,
        word_count=14000,
        page_count=55,
        line_count=1400,
        text=CERT_BLOCK,
    )
    assert not result.passed
    assert any("13,000" in e for e in result.errors)


def test_reply_brief_over_limit_fails() -> None:
    result = validate_appellate_document(
        AppellateDocType.REPLY_BRIEF,
        word_count=7000,
        page_count=28,
        line_count=700,
        text=CERT_BLOCK,
    )
    assert not result.passed
    assert any("6,500" in e for e in result.errors)


def test_petition_rehearing_over_limit_fails() -> None:
    result = validate_appellate_document(
        AppellateDocType.PETITION_REHEARING,
        word_count=4500,
        page_count=18,
        line_count=450,
        text=CERT_BLOCK,
    )
    assert not result.passed


def test_missing_certificate_warns_on_brief() -> None:
    result = validate_appellate_document(
        AppellateDocType.PRINCIPAL_BRIEF,
        word_count=5000,
        page_count=20,
        line_count=500,
        text="Just the body of a brief with no compliance certificate.",
    )
    assert result.passed  # type-volume ok
    assert not result.has_certificate_of_compliance
    assert any("Certificate of Compliance" in w for w in result.warnings)


def test_other_document_bypasses_limits() -> None:
    result = validate_appellate_document(
        AppellateDocType.OTHER,
        word_count=50000,
        page_count=200,
        line_count=5000,
        text="",
    )
    assert result.passed
    assert not result.errors
    assert not result.warnings


def test_type_volume_thresholds_match_frap() -> None:
    assert TYPE_VOLUME_LIMITS[AppellateDocType.PRINCIPAL_BRIEF]["words"] == 13000
    assert TYPE_VOLUME_LIMITS[AppellateDocType.REPLY_BRIEF]["words"] == 6500
    assert TYPE_VOLUME_LIMITS[AppellateDocType.PETITION_REHEARING]["words"] == 3900


def test_near_limit_warns() -> None:
    result = validate_appellate_document(
        AppellateDocType.PRINCIPAL_BRIEF,
        word_count=12600,
        page_count=50,
        line_count=1200,
        text=CERT_BLOCK,
    )
    assert result.passed
    assert any("within 5%" in w for w in result.warnings)


def test_e2e_fixture_brief_pdf_over_limit(tmp_path: Path) -> None:
    """E2E: build a synthetic over-length brief PDF; extract + validate."""
    body = (" ".join(["lorem"] * 14000)) + "\n\n" + CERT_BLOCK
    pdf = _make_pdf(tmp_path, body, "opening_brief.pdf")
    metrics = extract_metrics(pdf)
    assert metrics.word_count >= 14000

    doc_type = classify_appellate_doc("Appellant's Opening Brief", "Opening Brief")
    assert doc_type == AppellateDocType.PRINCIPAL_BRIEF

    result = validate_appellate_document(
        doc_type,
        metrics.word_count,
        metrics.page_count,
        metrics.line_count,
        metrics.text,
    )
    assert not result.passed
    assert result.has_certificate_of_compliance
    assert any("FRAP type-volume" in e for e in result.errors)


def test_e2e_fixture_brief_pdf_compliant(tmp_path: Path) -> None:
    body = (" ".join(["lorem"] * 5000)) + "\n\n" + CERT_BLOCK
    pdf = _make_pdf(tmp_path, body, "reply.pdf")
    metrics = extract_metrics(pdf)
    result = validate_appellate_document(
        AppellateDocType.REPLY_BRIEF,
        metrics.word_count,
        metrics.page_count,
        metrics.line_count,
        metrics.text,
    )
    assert result.passed
    assert result.has_certificate_of_compliance


def test_non_appellate_filings_bypass_validator() -> None:
    # classify_appellate_doc on a district-style filing maps to OTHER,
    # and OTHER is a no-op.
    result = validate_appellate_document(
        classify_appellate_doc("Motion to Dismiss", "Motion"),
        word_count=99999,
        page_count=500,
        line_count=9999,
        text="",
    )
    assert result.passed
    assert not result.errors
    assert not result.warnings
