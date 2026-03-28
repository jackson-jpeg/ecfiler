"""Demo browser view — generates simulated CM/ECF screenshots.

When the mock server isn't running and real PACER isn't configured,
this generates realistic-looking CM/ECF page screenshots using PyMuPDF
to render HTML-like pages. The user sees what the filing process
looks like step by step.
"""

from __future__ import annotations

import asyncio
import base64
import json
from typing import AsyncGenerator

import fitz

from ecfiler.logging import get_logger

logger = get_logger(__name__)


def _render_page(title: str, lines: list[str], highlight: str = "") -> bytes:
    """Render a simple CM/ECF-style page as a PNG image."""
    doc = fitz.open()
    page = doc.new_page(width=800, height=500)

    # Header bar
    page.draw_rect(fitz.Rect(0, 0, 800, 40), color=None, fill=fitz.pdfcolor["navy"])
    page.insert_text((20, 26), "CM/ECF — U.S. District Court", fontsize=13, color=fitz.pdfcolor["white"])

    # Menu bar
    page.draw_rect(fitz.Rect(0, 40, 800, 62), color=None, fill=fitz.pdfcolor["lightgray"])
    for i, item in enumerate(["Civil", "Criminal", "Query", "Reports", "Utilities", "Logout"]):
        page.insert_text((20 + i * 100, 55), item, fontsize=10, color=fitz.pdfcolor["navy"])

    # Title
    page.insert_text((30, 90), title, fontsize=14, color=fitz.pdfcolor["black"])
    page.draw_rect(fitz.Rect(30, 95, 770, 96), color=None, fill=fitz.pdfcolor["navy"])

    # Content lines
    y = 120
    for line in lines:
        if line.startswith("---"):
            page.draw_rect(fitz.Rect(30, y, 770, y + 1), color=None, fill=fitz.pdfcolor["lightgray"])
            y += 10
        elif line.startswith("[X]") or line.startswith("[x]"):
            page.draw_rect(fitz.Rect(30, y - 8, 42, y + 4), color=fitz.pdfcolor["navy"])
            page.insert_text((32, y), "X", fontsize=9, color=fitz.pdfcolor["white"])
            page.insert_text((50, y), line[3:].strip(), fontsize=11, color=fitz.pdfcolor["black"])
            y += 18
        elif line.startswith("[ ]"):
            page.draw_rect(fitz.Rect(30, y - 8, 42, y + 4), color=fitz.pdfcolor["gray"])
            page.insert_text((50, y), line[3:].strip(), fontsize=11, color=fitz.pdfcolor["black"])
            y += 18
        elif line.startswith(">>"):
            # Input field
            page.draw_rect(fitz.Rect(30, y - 10, 400, y + 6), color=fitz.pdfcolor["gray"])
            page.insert_text((35, y), line[2:].strip(), fontsize=11, color=fitz.pdfcolor["navy"])
            y += 20
        elif line.startswith("**"):
            page.insert_text((30, y), line.strip("*"), fontsize=11, color=fitz.pdfcolor["navy"])
            y += 18
        else:
            color = fitz.pdfcolor["red"] if "error" in line.lower() else fitz.pdfcolor["black"]
            page.insert_text((30, y), line, fontsize=11, color=color)
            y += 16

    if highlight:
        page.draw_rect(fitz.Rect(30, y + 5, 200, y + 30), color=None, fill=fitz.pdfcolor["navy"])
        page.insert_text((40, y + 22), highlight, fontsize=11, color=fitz.pdfcolor["white"])

    # Render to PNG
    pix = page.get_pixmap(dpi=150)
    png_bytes = pix.tobytes("png")
    doc.close()
    return png_bytes


async def stream_demo_filing(
    court_id: str,
    case_number: str,
    event_description: str,
    filing_party: str,
    is_sealed: bool = False,
    is_redacted: bool = False,
    exhibits: list[dict] | None = None,
) -> AsyncGenerator[str, None]:
    """Stream simulated CM/ECF screenshots as SSE events."""

    court_name = court_id.upper() if court_id else "NYSD"
    exhibit_list = exhibits or []

    steps = [
        ("Login", "Authenticating with PACER",
         "PACER Central Sign-On", [
             f"Court: {court_name}", "---",
             "Username: ********", "Password: ********",
             "Client Code: ecfiler", "---",
             "Authenticating..."
         ], "Login"),

        ("Authenticated", "Logged into CM/ECF",
         f"CM/ECF — {court_name}", [
             "Welcome to the Electronic Filing System", "---",
             f"User: Filing Attorney", f"Court: {court_name}", "---",
             "Select a category below to begin filing:",
             "", "  Civil    Criminal    Query    Reports"
         ], ""),

        ("Filing Category", "Selected Civil > Motions",
         "Select Filing Category", [
             "[X] Motions and Related Filings",
             "[ ] Initial Pleadings and Service",
             "[ ] Other Filings", "[ ] Notices",
         ], "Next"),

        ("Case Entry", f"Entering case {case_number}",
         "Enter Case Number", [
             f">> {case_number}", "---",
             "Searching case..."
         ], "Find"),

        ("Case Confirmed", "Case details verified",
         "Case Information", [
             f"**Case: {case_number}",
             f"**Court: {court_name}",
             "**Caption: SMITH v. JONES CORP",
             "**Judge: Hon. Williams",
             "**Status: Open", "---",
             "Confirm this is the correct case."
         ], "Next"),

        ("Event Selected", f"Selected: {event_description}",
         "Select Event Type", [
             f"[X] {event_description}",
             "[ ] Motion for Summary Judgment",
             "[ ] Motion to Compel",
             "[ ] Motion for Extension of Time",
         ], "Next"),

        ("Party Selected", f"Filing for: {filing_party}",
         "Select Filing Party", [
             "Select the party filing this document:", "---",
             f"[X] {filing_party}",
             "[ ] Smith (Plaintiff)",
         ], "Next"),

        ("Document Uploaded", f"PDF uploaded{f' + {len(exhibit_list)} exhibit(s)' if exhibit_list else ''}",
         "Upload Document", [
             "Main Document:", f">> document.pdf",
             "---", "File uploaded successfully.",
             "Size: 2.3 MB", "Pages: 15",
             *(
                 [f"---", f"Attachments ({len(exhibit_list)}):"]
                 + [f"  {e.get('label', f'Exhibit {i+1}')}: {e.get('description', 'Document')}" for i, e in enumerate(exhibit_list)]
                 if exhibit_list else []
             ),
         ], "Next"),

        ("Docket Text", "Docket text confirmed",
         "Modify Docket Text", [
             "Docket text (modify if needed):", "---",
             f">> {event_description}", "---",
             *(["[X] FILE UNDER SEAL"] if is_sealed else []),
             *(["[X] REDACTED FILING"] if is_redacted else []),
             "This text will appear on the docket."
         ], "Next"),

        ("Final Confirmation", "Review and submit",
         "FINAL CONFIRMATION", [
             f"**Case: {case_number}",
             f"**Event: {event_description}",
             f"**Filed by: {filing_party}",
             f"**Document: document.pdf (2.3 MB)",
             *(exhibit_list and [f"**Attachments: {len(exhibit_list)}"] or []),
             *(["**SEALED FILING"] if is_sealed else []),
             *(["**REDACTED VERSION"] if is_redacted else []),
             "---",
             "WARNING: Clicking Submit will file this document.",
             "This action cannot be undone."
         ], "Submit"),
    ]

    for step_name, description, title, lines, button in steps:
        # Emit running
        yield f"event: browser\ndata: {json.dumps({'step': step_name, 'status': 'running', 'description': description})}\n\n"
        await asyncio.sleep(0.8)

        # Render screenshot
        png = _render_page(title, lines, button)
        b64 = base64.b64encode(png).decode()

        # Emit done with screenshot
        yield f"event: browser\ndata: {json.dumps({'step': step_name, 'status': 'done', 'description': description, 'screenshot': b64})}\n\n"
        await asyncio.sleep(0.3)

    # Log to filing history
    try:
        from datetime import datetime
        from ecfiler.filing.models import FilingReceipt
        from ecfiler.storage.history import FilingHistory
        history = FilingHistory()
        receipt = FilingReceipt(
            court_id=court_id,
            case_number=case_number,
            event_description=event_description,
            docket_number="58",
            filed_at=datetime.now(),
        )
        history.log_filing(receipt)
    except Exception:
        pass

    yield f"event: browser_done\ndata: {json.dumps({'success': True, 'message': 'Filing complete. Document filed as Docket #58.'})}\n\n"
