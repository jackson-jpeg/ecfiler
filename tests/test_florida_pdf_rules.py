"""Florida Portal document rules: prohibited elements, size, filenames.

Every fixture is generated in-test (no binary fixtures), and every rule
asserts the behavior the Florida Courts Technology Standards v4.0 §2 requires
(as captured in docs/fl/technical-specs.md §4). Illegal states raise —
the Portal's remedy is the Correction Queue, so ECFiler refuses up front.
"""

from __future__ import annotations

from pathlib import Path

import fitz
import pikepdf
import pytest

from ecfiler.courts.florida import (
    FloridaDocumentError,
    Document,
    FilingPath,
    Submission,
    parse_ucn,
    prepare_document_for_portal,
    scan_prohibited_elements,
    scrub_prohibited_elements,
    validate_filename,
    validate_submission_files,
)


def _basic_pdf(path: Path, pages: int = 1) -> Path:
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page()
        page.insert_text((72, 72), f"Motion text, page {i + 1}.")
    doc.save(str(path))
    doc.close()
    return path


def _elements(scan) -> set[str]:
    return {f.element for f in scan.findings}


class TestFilenameRules:
    def test_clean_name_passes(self) -> None:
        assert validate_filename("Motion_to_Dismiss.pdf") == []

    @pytest.mark.parametrize("ch", list('"#%&*:<>'))
    def test_each_forbidden_character_rejected(self, ch: str) -> None:
        errors = validate_filename(f"motion{ch}.pdf")
        assert errors and "forbidden character" in errors[0]

    def test_150_byte_cap_is_bytes_not_chars(self) -> None:
        # 149 two-byte characters = 298 bytes: over the cap at only 153 chars.
        name = "é" * 149 + ".pdf"
        errors = validate_filename(name)
        assert errors and "bytes" in errors[0]

    def test_150_bytes_exactly_passes(self) -> None:
        name = "a" * 146 + ".pdf"
        assert len(name.encode()) == 150
        assert validate_filename(name) == []


class TestProhibitedElementScan:
    def test_clean_pdf_is_clean(self, tmp_path: Path) -> None:
        scan = scan_prohibited_elements(_basic_pdf(tmp_path / "clean.pdf"))
        assert scan.clean, [f.detail for f in scan.findings]

    def test_text_annotation_detected(self, tmp_path: Path) -> None:
        doc = fitz.open()
        page = doc.new_page()
        page.add_text_annot((72, 72), "a sticky note comment")
        p = tmp_path / "annot.pdf"
        doc.save(str(p))
        doc.close()
        assert "annotations" in _elements(scan_prohibited_elements(p))

    def test_link_annotation_permitted(self, tmp_path: Path) -> None:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "see the docket")
        page.insert_link(
            {"kind": fitz.LINK_URI, "from": fitz.Rect(72, 60, 200, 80),
             "uri": "https://www.flcourts.gov/"}
        )
        p = tmp_path / "link.pdf"
        doc.save(str(p))
        doc.close()
        scan = scan_prohibited_elements(p)
        assert scan.clean, [f.detail for f in scan.findings]

    def test_form_fields_detected(self, tmp_path: Path) -> None:
        doc = fitz.open()
        page = doc.new_page()
        w = fitz.Widget()
        w.field_name = "signature"
        w.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        w.rect = fitz.Rect(72, 72, 200, 100)
        page.add_widget(w)
        p = tmp_path / "form.pdf"
        doc.save(str(p))
        doc.close()
        found = _elements(scan_prohibited_elements(p))
        assert "form-fields" in found or "annotations" in found

    def test_javascript_detected(self, tmp_path: Path) -> None:
        p = _basic_pdf(tmp_path / "js.pdf")
        with pikepdf.open(p, allow_overwriting_input=True) as pdf:
            js_action = pdf.make_indirect(
                pikepdf.Dictionary(S=pikepdf.Name.JavaScript, JS="app.alert('hi');")
            )
            pdf.Root.Names = pdf.make_indirect(
                pikepdf.Dictionary(
                    JavaScript=pikepdf.Dictionary(
                        Names=pikepdf.Array(["boom", js_action])
                    )
                )
            )
            pdf.save(p)
        assert "javascript" in _elements(scan_prohibited_elements(p))

    def test_embedded_attachment_detected(self, tmp_path: Path) -> None:
        p = _basic_pdf(tmp_path / "attach.pdf")
        with pikepdf.open(p, allow_overwriting_input=True) as pdf:
            pdf.attachments["exhibit.txt"] = b"smuggled attachment"
            pdf.save(tmp_path / "attach2.pdf")
        assert "embedded-attachments" in _elements(
            scan_prohibited_elements(tmp_path / "attach2.pdf")
        )

    def test_open_action_detected(self, tmp_path: Path) -> None:
        p = _basic_pdf(tmp_path / "oa.pdf")
        with pikepdf.open(p, allow_overwriting_input=True) as pdf:
            pdf.Root.OpenAction = pdf.make_indirect(
                pikepdf.Dictionary(S=pikepdf.Name.JavaScript, JS="this.print();")
            )
            pdf.save(p)
        assert "actions" in _elements(scan_prohibited_elements(p))

    def test_encrypted_pdf_detected_and_unscrubbable(self, tmp_path: Path) -> None:
        p = _basic_pdf(tmp_path / "plain.pdf")
        locked = tmp_path / "locked.pdf"
        with pikepdf.open(p) as pdf:
            pdf.save(
                locked,
                encryption=pikepdf.Encryption(owner="owner-secret", user="user-secret"),
            )
        scan = scan_prohibited_elements(locked)
        assert _elements(scan) == {"encryption"}
        assert not scan.findings[0].scrubbable
        with pytest.raises(FloridaDocumentError, match="cannot scrub"):
            scrub_prohibited_elements(locked, tmp_path / "out.pdf")


class TestScrub:
    def _dirty_pdf(self, tmp_path: Path) -> Path:
        """A PDF with an annotation, form field, JS, attachment, and OpenAction."""
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "The underlying motion text.")
        page.add_text_annot((72, 120), "reviewer comment")
        w = fitz.Widget()
        w.field_name = "f1"
        w.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        w.rect = fitz.Rect(72, 150, 200, 170)
        page.add_widget(w)
        p = tmp_path / "dirty.pdf"
        doc.save(str(p))
        doc.close()
        with pikepdf.open(p, allow_overwriting_input=True) as pdf:
            pdf.Root.OpenAction = pdf.make_indirect(
                pikepdf.Dictionary(S=pikepdf.Name.JavaScript, JS="this.print();")
            )
            pdf.attachments["x.txt"] = b"data"
            pdf.save(p)
        return p

    def test_scrub_removes_everything_and_preserves_content(
        self, tmp_path: Path
    ) -> None:
        dirty = self._dirty_pdf(tmp_path)
        assert not scan_prohibited_elements(dirty).clean

        out = tmp_path / "scrubbed.pdf"
        result = scrub_prohibited_elements(dirty, out)
        assert result.clean

        with fitz.open(str(out)) as doc:
            assert doc.page_count == 1
            assert "The underlying motion text." in doc[0].get_text()

    def test_scrub_keeps_permitted_links(self, tmp_path: Path) -> None:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "text")
        page.insert_link(
            {"kind": fitz.LINK_URI, "from": fitz.Rect(72, 60, 200, 80),
             "uri": "https://www.flcourts.gov/"}
        )
        page.add_text_annot((72, 120), "comment to remove")
        p = tmp_path / "mixed.pdf"
        doc.save(str(p))
        doc.close()

        out = tmp_path / "mixed-clean.pdf"
        scrub_prohibited_elements(p, out)
        with fitz.open(str(out)) as cleaned:
            links = cleaned[0].get_links()
            annots = list(cleaned[0].annots())
        assert len(links) == 1
        assert annots == []


class TestSubmissionValidation:
    def _submission(self) -> Submission:
        return Submission(
            ucn=parse_ucn("502026CA001234XXXXMB", strict=False),
            filing_path=FilingPath.EXISTING_CASE,
            documents=[
                Document(filename="motion.pdf", is_lead=True),
                Document(filename="exhibit_a.pdf", is_lead=False),
            ],
        )

    def test_valid_submission_passes(self, tmp_path: Path) -> None:
        files = {
            "motion.pdf": _basic_pdf(tmp_path / "motion.pdf"),
            "exhibit_a.pdf": _basic_pdf(tmp_path / "exhibit_a.pdf"),
        }
        validate_submission_files(self._submission(), files)

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        files = {"motion.pdf": _basic_pdf(tmp_path / "motion.pdf")}
        with pytest.raises(FloridaDocumentError, match="no file provided"):
            validate_submission_files(self._submission(), files)

    def test_prohibited_element_raises(self, tmp_path: Path) -> None:
        doc = fitz.open()
        page = doc.new_page()
        page.add_text_annot((72, 72), "note")
        annotated = tmp_path / "motion.pdf"
        doc.save(str(annotated))
        doc.close()
        files = {
            "motion.pdf": annotated,
            "exhibit_a.pdf": _basic_pdf(tmp_path / "exhibit_a.pdf"),
        }
        with pytest.raises(FloridaDocumentError, match="annotation"):
            validate_submission_files(self._submission(), files)

    def test_size_cap_is_per_submission_not_per_document(self, tmp_path: Path) -> None:
        """Two documents under the cap individually must still fail together."""
        a = _basic_pdf(tmp_path / "motion.pdf")
        b = _basic_pdf(tmp_path / "exhibit_a.pdf")
        # Pad each to ~0.6 MB, then apply a 1 MB cap: each fits, the pair doesn't.
        for f in (a, b):
            f.write_bytes(f.read_bytes() + b" " * 600_000)
        files = {"motion.pdf": a, "exhibit_a.pdf": b}
        with pytest.raises(FloridaDocumentError, match="caps a single submission"):
            validate_submission_files(self._submission(), files, limit_mb=1)
        validate_submission_files(self._submission(), files, limit_mb=2)

    def test_forbidden_filename_raises(self, tmp_path: Path) -> None:
        sub = Submission(
            ucn=parse_ucn("502026CA001234XXXXMB", strict=False),
            filing_path=FilingPath.EXISTING_CASE,
            documents=[Document(filename="motion:final.pdf", is_lead=True)],
        )
        files = {"motion:final.pdf": _basic_pdf(tmp_path / "m.pdf")}
        with pytest.raises(FloridaDocumentError, match="forbidden character"):
            validate_submission_files(sub, files)


class TestPreparePipeline:
    def test_prepare_without_pdfa_returns_scrubbed(self, tmp_path: Path) -> None:
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "content")
        page.add_text_annot((72, 100), "note")
        src = tmp_path / "src.pdf"
        doc.save(str(src))
        doc.close()

        out = prepare_document_for_portal(
            src, tmp_path / "ready.pdf", convert_pdfa=False
        )
        assert scan_prohibited_elements(out).clean

    def test_prepare_with_pdfa_requires_ocrmypdf_or_raises(
        self, tmp_path: Path
    ) -> None:
        from ecfiler.pdf.converter import is_ocrmypdf_available

        src = _basic_pdf(tmp_path / "src.pdf")
        if is_ocrmypdf_available():
            out = prepare_document_for_portal(src, tmp_path / "ready.pdf")
            assert Path(out).exists()
            with pikepdf.open(out) as pdf:
                meta = pdf.open_metadata()
                assert meta.pdfa_status != ""
        else:
            with pytest.raises(FloridaDocumentError, match="ocrmypdf"):
                prepare_document_for_portal(src, tmp_path / "ready.pdf")
