"""The C4 white-paper PDF must track its markdown source.

The PDF is the artifact that actually gets attached to AO correspondence.
Before this test existed, the render was an ad-hoc browser print with no
committed build path, so any markdown edit silently desynchronized the
attachable file. Regenerate with scripts/render_white_paper.py.
"""

from __future__ import annotations

import re
from pathlib import Path

import fitz
import pytest

REPO = Path(__file__).resolve().parent.parent
MD_PATH = REPO / "docs" / "outreach" / "c4-white-paper.md"
PDF_PATH = REPO / "docs" / "outreach" / "c4-white-paper.pdf"


@pytest.fixture(scope="module")
def pdf_text() -> str:
    assert PDF_PATH.exists(), "c4-white-paper.pdf missing — run scripts/render_white_paper.py"
    doc = fitz.open(PDF_PATH)
    text = "".join(page.get_text() for page in doc)
    doc.close()
    # PDF extraction breaks lines unpredictably; compare on collapsed whitespace.
    return re.sub(r"\s+", " ", text)


def _normalize(s: str) -> str:
    # Match the smartypants transformations the renderer applies.
    s = s.replace("---", "—").replace("--", "–")
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = re.sub(r"`(.+?)`", r"\1", s)
    s = re.sub(r"\[\^?\d+\]", "", s)  # footnote refs
    s = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", s)  # links → text
    return re.sub(r"\s+", " ", s).strip()


def test_every_heading_appears_in_pdf(pdf_text: str) -> None:
    headings = re.findall(r"^#{1,3} (.+)$", MD_PATH.read_text(), re.M)
    assert headings, "no headings found in markdown?"
    missing = [h for h in headings if _normalize(h) not in pdf_text]
    assert missing == [], f"headings missing from PDF (stale render?): {missing}"


def test_identity_paragraph_appears_in_pdf(pdf_text: str) -> None:
    """The load-bearing identity sentences must be the *current* ones."""
    for fragment in [
        "I write in a personal capacity",
        "By profession I am a litigation docketing specialist",
        "No employer is named or represented in this paper",
        "ECFiler has never filed on behalf of a client",
    ]:
        assert _normalize(fragment) in pdf_text, f"missing from PDF: {fragment!r}"


def test_retired_framing_absent_from_pdf(pdf_text: str) -> None:
    lowered = pdf_text.lower()
    for phrase in ["national law firm", "our staff", "[firm name]"]:
        assert phrase not in lowered, f"retired phrase in PDF: {phrase!r}"


def test_footer_tagline_present(pdf_text: str) -> None:
    assert "File with confidence. File with code you can read." in pdf_text
