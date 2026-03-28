"""Server-Sent Events for real-time filing progress.

Instead of the client waiting for one big JSON response while showing
a fake spinner, we stream each step as it happens:

  event: step
  data: {"id": 1, "label": "Validating PDF", "status": "running"}

  event: step
  data: {"id": 1, "label": "Validating PDF", "status": "done", "detail": "2.3MB, 15 pages, searchable"}

  event: step
  data: {"id": 2, "label": "Reading document", "status": "running"}

  ...

  event: result
  data: {"filing": {...}}
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from typing import AsyncGenerator

from ecfiler.logging import get_logger

logger = get_logger(__name__)


async def stream_analysis(file_content: bytes, filename: str, api_key: str) -> AsyncGenerator[str, None]:
    """Stream document analysis progress as SSE events.

    Yields SSE-formatted strings that the client consumes via EventSource.
    """
    step_id = 0

    def emit_step(label: str, status: str, detail: str = "") -> str:
        nonlocal step_id
        if status == "running":
            step_id += 1
        data = {"id": step_id, "label": label, "status": status}
        if detail:
            data["detail"] = detail
        return f"event: step\ndata: {json.dumps(data)}\n\n"

    def emit_result(filing: dict) -> str:
        return f"event: result\ndata: {json.dumps(filing)}\n\n"

    def emit_error(message: str) -> str:
        return f"event: error\ndata: {json.dumps({'message': message})}\n\n"

    # Save to temp file
    suffix = Path(filename).suffix or ".pdf"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name

    try:
        # Step 1: Validate PDF
        yield emit_step("Validating PDF", "running")
        await asyncio.sleep(0.1)  # Let the event flush

        from ecfiler.pdf.validator import validate_pdf
        validation = validate_pdf(tmp_path, check_pdfa=True)

        if not validation.valid:
            yield emit_step("Validating PDF", "error", "; ".join(validation.errors))
            yield emit_error("PDF validation failed: " + "; ".join(validation.errors))
            return

        detail = f"{validation.file_size_mb:.1f}MB, {validation.page_count} pages"
        if validation.has_text:
            detail += ", searchable"
        else:
            detail += ", NOT searchable"
        if validation.is_pdfa:
            detail += ", PDF/A"
        yield emit_step("Validating PDF", "done", detail)

        # Step 2: Extract text
        yield emit_step("Reading document", "running")
        await asyncio.sleep(0.1)

        from ecfiler.pdf.validator import extract_text
        text = extract_text(tmp_path, max_pages=30)
        yield emit_step("Reading document", "done", f"{len(text):,} characters extracted")

        # Step 3: AI analysis
        yield emit_step("AI analyzing document", "running")
        await asyncio.sleep(0.1)

        from ecfiler.agent.document_analyzer import analyze_document
        analysis = analyze_document(text, api_key=api_key)

        ai_detail = []
        if analysis.case_number:
            ai_detail.append(f"Case {analysis.case_number}")
        if analysis.court_id:
            ai_detail.append(analysis.court_id)
        if analysis.filing_party_name:
            ai_detail.append(analysis.filing_party_name)
        yield emit_step("AI analyzing document", "done", " — ".join(ai_detail) or "Analysis complete")

        # Step 4: Redaction scan
        yield emit_step("Scanning for redaction issues", "running")
        await asyncio.sleep(0.1)

        from ecfiler.pdf.redaction_check import scan_document
        redaction = scan_document(text)

        if redaction.has_issues:
            yield emit_step("Scanning for redaction issues", "warn", f"{len(redaction.issues)} potential issue(s)")
        else:
            yield emit_step("Scanning for redaction issues", "done", "No issues found")

        # Step 5: Event code matching
        yield emit_step("Matching event code", "running")
        await asyncio.sleep(0.1)

        from ecfiler.filing.events import search_events

        court_type = _infer_court_type(analysis.court_id)
        desc = analysis.document_type_specific or analysis.document_type
        matches = search_events(desc, court_type) if desc else []
        event_code = matches[0].code if matches else ""
        event_desc = matches[0].description if matches else desc

        if event_code:
            yield emit_step("Matching event code", "done", f"{event_desc} ({event_code})")
        else:
            yield emit_step("Matching event code", "warn", "No exact match — manual selection needed")

        # Step 6: Generate docket text
        yield emit_step("Generating docket text", "running")
        await asyncio.sleep(0.1)

        # Build smart docket text from analysis
        docket_text = _build_docket_text(analysis, event_desc)
        yield emit_step("Generating docket text", "done", docket_text[:80] + ("..." if len(docket_text) > 80 else ""))

        # Check filing fee
        from ecfiler.filing.fees import get_fee, format_fee
        fee = get_fee(event_desc or analysis.document_type, court_type)
        fee_amount = fee.amount if fee else 0
        fee_text = format_fee(fee) if fee else "Unknown"

        # Build warnings
        warnings: list[str] = []
        if not analysis.has_signature:
            warnings.append("No signature block detected")
        if not analysis.has_certificate_of_service:
            warnings.append("No certificate of service detected")
        if analysis.is_response and not analysis.responds_to_docket_number:
            warnings.append("Response filing without docket reference")
        if fee and fee.amount > 0:
            warnings.append(f"Filing fee: {fee_text}")
        warnings.extend(validation.warnings)

        ready = validation.valid and analysis.completeness_score >= 60 and bool(event_code)

        # Emit final result
        filing = {
            "document_type": analysis.document_type_specific or analysis.document_type,
            "case_number": analysis.case_number,
            "court_id": analysis.court_id,
            "case_caption": analysis.case_caption,
            "event_code": event_code,
            "event_description": docket_text or event_desc,
            "filing_party": f"{analysis.filing_party_name} ({analysis.filing_party_role})" if analysis.filing_party_name else "",
            "is_response": analysis.is_response,
            "responds_to": analysis.responds_to if analysis.is_response else None,
            "pdf_valid": validation.valid,
            "pdf_size_mb": validation.file_size_mb,
            "pdf_pages": validation.page_count,
            "pdf_is_pdfa": validation.is_pdfa or False,
            "redaction_risk": redaction.risk_level,
            "redaction_issues": len(redaction.issues),
            "completeness_score": analysis.completeness_score,
            "warnings": warnings,
            "confidence": analysis.confidence,
            "ready": ready,
            "filing_fee": fee_amount,
            "filing_fee_text": fee_text,
        }

        yield emit_result(filing)

    except Exception as e:
        logger.error("Streaming analysis failed: %s", e)
        yield emit_error(str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def _build_docket_text(analysis, event_desc: str) -> str:
    """Build a suggested docket text from the analysis results.

    The docket text is what appears on the court docket. It should be
    descriptive but concise, matching CM/ECF conventions.
    """
    doc_type = analysis.document_type_specific or analysis.document_type or event_desc

    # Start with the document type
    text = doc_type

    # Add response context if applicable
    if analysis.is_response and analysis.responds_to_docket_number:
        text += f" re: Dkt. #{analysis.responds_to_docket_number}"
    elif analysis.is_response and analysis.responds_to:
        text += f" re: {analysis.responds_to}"

    return text


def _infer_court_type(court_id: str) -> str:
    if not court_id:
        return "district"
    try:
        from ecfiler.courts.registry import CourtRegistry
        return CourtRegistry().get(court_id).profile.court_type
    except Exception:
        if court_id.endswith("b"):
            return "bankruptcy"
        if court_id.startswith("ca"):
            return "appellate"
        return "district"
