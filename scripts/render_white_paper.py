#!/usr/bin/env python3
"""Render docs/outreach/c4-white-paper.md to its distributable PDF.

The PDF is what actually gets attached to AO correspondence, so it must never
drift from the markdown. This script is the single build path (the original
render was an ad-hoc headless-Chrome print with no committed wrapper), and
tests/test_white_paper_parity.py fails when the two fall out of sync.

Usage:  .venv/bin/python scripts/render_white_paper.py
"""

from __future__ import annotations

import re
from pathlib import Path

import markdown

REPO = Path(__file__).resolve().parent.parent
MD_PATH = REPO / "docs" / "outreach" / "c4-white-paper.md"
PDF_PATH = REPO / "docs" / "outreach" / "c4-white-paper.pdf"

# The page footer carries the project tagline (BRANDING.md) plus page numbers,
# matching the original render.
TAGLINE = "ECFiler — File with confidence. File with code you can read."

CSS = """
@page { size: Letter; }
body {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 11pt; line-height: 1.5; color: #1a1a1a;
  max-width: 6.5in; margin: 0 auto;
}
h1 { font-size: 17pt; line-height: 1.25; margin-bottom: 4pt; }
h2 { font-size: 13pt; margin-top: 18pt; border-bottom: 1px solid #ccc; padding-bottom: 3pt; }
h3 { font-size: 11.5pt; }
code { font-family: Menlo, monospace; font-size: 9.5pt; background: #f4f3f0; padding: 0 2px; }
blockquote { border-left: 3px solid #ccc; margin-left: 0; padding-left: 12px; color: #444; }
a { color: #1e3a5f; }
hr { border: none; border-top: 1px solid #ccc; margin: 14pt 0; }
sup { font-size: 8pt; }
"""


def render() -> Path:
    md_text = MD_PATH.read_text(encoding="utf-8")
    body = markdown.markdown(
        md_text, extensions=["footnotes", "tables", "smarty"]
    )
    html = f"<!doctype html><meta charset='utf-8'><style>{CSS}</style><body>{body}</body>"

    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        page.pdf(
            path=str(PDF_PATH),
            format="Letter",
            margin={"top": "0.9in", "bottom": "0.9in", "left": "1in", "right": "1in"},
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=(
                "<div style='font-size:8px; font-family:Georgia,serif; color:#666;"
                " width:100%; display:flex; justify-content:space-between;"
                " padding:0 0.6in;'>"
                f"<span>{TAGLINE}</span>"
                "<span><span class='pageNumber'></span> of "
                "<span class='totalPages'></span></span></div>"
            ),
        )
        browser.close()
    return PDF_PATH


if __name__ == "__main__":
    out = render()
    size = out.stat().st_size
    print(f"rendered {out.relative_to(REPO)} ({size:,} bytes)")
    # Quick sanity: the markdown's own footnote-stripped text should be present.
    first_heading = re.search(r"^# (.+)$", MD_PATH.read_text(), re.M)
    if first_heading:
        print(f"title: {first_heading.group(1)}")
