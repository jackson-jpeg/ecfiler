"""The filled Florida TPV application says exactly what the packet checklist says it does.

Reads the overlay back out of the PDF: every word the fill script added, on
which page, inside which cell. A stray answer on a signature line, a missing
"X" in the scope grid, or a personal Gmail address on a form mailed to the
Authority all fail here. Both the freshly generated PDF and the committed
`docs/fl/Third_Party_Vendor_Application_FILLED.pdf` are checked, so the
committed packet cannot drift from the script.
"""

from __future__ import annotations

import collections
import hashlib
import subprocess
import sys
from pathlib import Path

import fitz
import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "fill_fl_tpv_application.py"
SOURCE = REPO / "docs/fl/sources/Third_Party_Vendor_Application_01-01-2021_ADA.pdf"
COMMITTED = REPO / "docs/fl/Third_Party_Vendor_Application_FILLED.pdf"

# The form the Certified Vendors page links (ADA re-upload, 2026-05-06).
# If the Authority replaces it, this pin fails and the overlay geometry has to
# be re-measured against the new form before anything is printed.
SOURCE_SHA256 = "a42528fc84238c6999d3db742b4b3f8a117b559632511dc9c74e833e481f6b87"

EMAIL = "jackson@sang3r.com"

# Every word the overlay adds, page by page, in reading order.
EXPECTED_ADDED = {
    1: f"Unpossible Studio LLC d/b/a ECFiler {EMAIL} Jackson Sanger [phone]",
    3: "N/A N/A N/A N/A Not applicable: Applicant will use the "
    "FilingReviewCompleteResult polling service for status retrieval "
    "(see cover letter). X X",
    5: f"Jackson Sanger [street address] Tampa, FL [phone] {EMAIL} "
    "Applicant: Unpossible Studio LLC d/b/a ECFiler, a single-member Florida limited liability "
    "company, organized effective 01/01/2027. State of organization: Florida. "
    "[to complete at mailing] None. None. No. No. See attached reference sheet.",
}

# Text that must sit inside a given cell (page, x0, y0, x1, y1), measured on the form.
PLACEMENTS = [
    (1, (120, 180, 304, 195), "Unpossible Studio LLC d/b/a ECFiler"),  # Applicant Name value cell
    (1, (391, 180, 570, 195), EMAIL),  # Contact Email value cell
    (1, (120, 199, 304, 214), "Jackson Sanger"),  # Contact Name value cell
    (1, (391, 199, 570, 214), "[phone]"),  # Contact Phone value cell
    (5, (120, 150, 400, 165), EMAIL),  # Section I E-mail line
]


def _added_words(src: fitz.Document, out: fitz.Document) -> dict[int, list[tuple]]:
    added: dict[int, list[tuple]] = {}
    for i, (a, b) in enumerate(zip(src, out), start=1):
        base = collections.Counter((round(w[0], 1), round(w[1], 1), w[4]) for w in a.get_text("words"))
        for w in b.get_text("words"):
            key = (round(w[0], 1), round(w[1], 1), w[4])
            if base[key]:
                base[key] -= 1
            else:
                added.setdefault(i, []).append(w)
    return added


@pytest.fixture(scope="module")
def generated(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("fl") / "filled.pdf"
    subprocess.run([sys.executable, str(SCRIPT), str(out)], cwd=REPO, check=True, capture_output=True)
    return out


def test_source_is_the_currently_linked_form() -> None:
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256


@pytest.mark.parametrize("which", ["generated", "committed"])
def test_overlay_reads_back_exactly(which: str, generated: Path) -> None:
    path = generated if which == "generated" else COMMITTED
    src, out = fitz.open(SOURCE), fitz.open(path)
    assert len(out) == len(src) == 5
    added = _added_words(src, out)
    got = {p: " ".join(w[4] for w in sorted(ws, key=lambda w: (round(w[3]), w[0]))) for p, ws in added.items()}
    assert got == EXPECTED_ADDED

    for page, rect, text in PLACEMENTS:
        inside = " ".join(w[4] for w in sorted(added[page], key=lambda w: w[0]) if fitz.Rect(w[:4]) in fitz.Rect(rect))
        assert inside == text, f"p{page} {rect}: {inside!r}"


    # The two scope marks: "Pleading on Existing Case" column, CA and CC rows only.
    xs = [w for w in added[3] if w[4] == "X"]
    assert len(xs) == 2
    for w, (top, bottom) in zip(sorted(xs, key=lambda w: w[1]), [(491.7, 506.9), (507.7, 522.9)]):
        r = fitz.Rect(w[:4])
        assert 288.4 <= r.x0 and r.x1 <= 410.9 and top - 1.5 <= r.y0 and r.y1 <= bottom
    # Nothing below the Section III answers on p5: both signature blocks blank.
    assert max(w[3] for w in added[5]) < 540


@pytest.mark.parametrize("which", ["generated", "committed"])
def test_placeholders_gray_answers_black(which: str, generated: Path) -> None:
    path = generated if which == "generated" else COMMITTED
    src, out = fitz.open(SOURCE), fitz.open(path)
    added = _added_words(src, out)
    for page, words in added.items():
        spans = [s for b in out[page - 1].get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]]
        for w in words:
            r = fitz.Rect(w[:4])
            owners = [s for s in spans if fitz.Rect(s["bbox"]).intersects(r) and w[4] in s["text"]]
            assert owners, f"p{page} {w[4]!r}: no span"
            span = owners[0]
            # A bracketed span is a blank left for Jackson: gray. Everything else is an answer: black.
            if span["text"].strip().startswith("["):
                assert span["color"] != 0, f"p{page} placeholder {span['text']!r} should be gray"
            else:
                assert span["color"] == 0, f"p{page} answer {span['text']!r} should be black"


@pytest.mark.parametrize("which", ["generated", "committed"])
def test_no_personal_gmail(which: str, generated: Path) -> None:
    path = generated if which == "generated" else COMMITTED
    text = "".join(p.get_text() for p in fitz.open(path)).lower()
    assert "gmail" not in text
    assert "ecfiler.com" not in text  # that mailbox no longer exists
    assert "@gmail." not in SCRIPT.read_text().lower()
