"""ECFiler API — agent-first REST backend.

The API has two modes:
1. **Agent mode** (POST /api/file) — upload a PDF, get a fully-analyzed filing
   ready for one-click confirmation. This is the groundbreaking part.
2. **Utility mode** — individual endpoints for validation, court lookup, etc.

Start with: uvicorn ecfiler.api.app:app --reload
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="ECFiler API",
    description="AI-native filing for Federal CM/ECF courts",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def serve_ui() -> FileResponse:
    """Serve the ECFiler web UI."""
    return FileResponse(STATIC_DIR / "app.html")


# --- Models ---


class AnalysisResponse(BaseModel):
    """What the AI extracted from your document."""

    document_type: str
    document_type_specific: str
    case_number: str
    court_id: str
    court_name: str
    case_caption: str
    filing_party_name: str
    filing_party_role: str
    attorney_name: str
    is_response: bool
    responds_to: str
    responds_to_docket_number: str
    suggested_event_code_category: str
    has_certificate_of_service: bool
    has_signature: bool
    completeness_score: int
    confidence: str
    missing_fields: list[str]


class ValidationResponse(BaseModel):
    valid: bool
    file_size_mb: float
    page_count: int
    has_text: bool
    is_encrypted: bool
    errors: list[str]
    warnings: list[str]


class RedactionResponse(BaseModel):
    risk_level: str
    issues: list[dict]


class CourtResponse(BaseModel):
    court_id: str
    name: str
    court_type: str


class EventCodeResponse(BaseModel):
    code: str
    description: str
    category: str


class FilingPreview(BaseModel):
    """Complete filing preview — everything auto-extracted, ready for confirmation."""

    # From document analysis
    document_type: str
    case_number: str
    court_id: str
    case_caption: str
    event_code: str
    event_description: str
    filing_party: str
    is_response: bool
    responds_to: str | None

    # Validation results
    pdf_valid: bool
    pdf_size_mb: float
    pdf_pages: int
    redaction_risk: str
    redaction_issues: int

    # Completeness
    completeness_score: int
    warnings: list[str]
    confidence: str

    # Ready to file?
    ready: bool


# --- Agent endpoint: the magic ---


MAX_UPLOAD_BYTES = 100 * 1024 * 1024  # 100MB


async def _validate_upload(document: UploadFile) -> bytes:
    """Validate an uploaded file: check type, size, read content."""
    # Check content type
    if document.content_type and document.content_type not in (
        "application/pdf",
        "application/octet-stream",  # Some browsers send this
    ):
        raise HTTPException(400, f"Only PDF files accepted, got: {document.content_type}")

    # Check filename extension
    filename = document.filename or ""
    if filename and not filename.lower().endswith(".pdf"):
        raise HTTPException(400, f"File must have .pdf extension, got: {filename}")

    # Read with size limit
    content = await document.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            400,
            f"File too large: {len(content) / 1024 / 1024:.1f}MB (max {MAX_UPLOAD_BYTES // 1024 // 1024}MB)",
        )

    if len(content) == 0:
        raise HTTPException(400, "Empty file uploaded")

    return content


@app.post("/api/file", response_model=FilingPreview)
async def analyze_and_prepare_filing(
    document: UploadFile = File(..., description="PDF document to file"),
) -> FilingPreview:
    """Upload a PDF. Get a complete filing ready for confirmation.

    This is the core AI-native endpoint. It:
    1. Validates the PDF
    2. Extracts text
    3. Analyzes with Claude (case, court, party, event type, response context)
    4. Scans for redaction issues
    5. Matches to a CM/ECF event code
    6. Returns everything needed for the UI to show a one-click confirm screen
    """
    import os

    from ecfiler.agent.document_analyzer import analyze_document
    from ecfiler.filing.events import search_events
    from ecfiler.pdf.redaction_check import scan_document
    from ecfiler.pdf.validator import extract_text, validate_pdf

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise HTTPException(
            503,
            "Smart filing requires an Anthropic API key. "
            "Set ANTHROPIC_API_KEY on the server. "
            "PDF validation and court lookup work without it.",
        )

    # Validate and read upload
    content = await _validate_upload(document)

    suffix = Path(document.filename or "upload.pdf").suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # 1. Validate PDF
        validation = validate_pdf(tmp_path)

        if not validation.valid:
            return FilingPreview(
                document_type="unknown",
                case_number="",
                court_id="",
                case_caption="",
                event_code="",
                event_description="",
                filing_party="",
                is_response=False,
                responds_to=None,
                pdf_valid=False,
                pdf_size_mb=validation.file_size_mb,
                pdf_pages=validation.page_count,
                redaction_risk="unknown",
                redaction_issues=0,
                completeness_score=0,
                warnings=validation.errors,
                confidence="none",
                ready=False,
            )

        # 2. Extract text
        text = extract_text(tmp_path, max_pages=30)

        # 3. AI analysis
        analysis = analyze_document(text, api_key=api_key)

        # 4. Redaction scan
        redaction = scan_document(text)

        # 5. Event code matching
        court_type = _infer_court_type(analysis.court_id)
        desc = analysis.document_type_specific or analysis.document_type
        matches = search_events(desc, court_type) if desc else []
        event_code = matches[0].code if matches else ""
        event_desc = matches[0].description if matches else analysis.document_type_specific

        # 6. Completeness warnings
        warnings: list[str] = []
        if not analysis.has_signature:
            warnings.append("No signature block detected")
        if not analysis.has_certificate_of_service:
            warnings.append("No certificate of service detected")
        if analysis.is_response and not analysis.responds_to_docket_number:
            warnings.append("Response filing without docket reference")
        warnings.extend(validation.warnings)

        ready = (
            validation.valid
            and analysis.completeness_score >= 60
            and bool(event_code)
        )

        return FilingPreview(
            document_type=analysis.document_type_specific or analysis.document_type,
            case_number=analysis.case_number,
            court_id=analysis.court_id,
            case_caption=analysis.case_caption,
            event_code=event_code,
            event_description=event_desc,
            filing_party=f"{analysis.filing_party_name} ({analysis.filing_party_role})"
            if analysis.filing_party_name
            else "",
            is_response=analysis.is_response,
            responds_to=analysis.responds_to if analysis.is_response else None,
            pdf_valid=validation.valid,
            pdf_size_mb=validation.file_size_mb,
            pdf_pages=validation.page_count,
            redaction_risk=redaction.risk_level,
            redaction_issues=len(redaction.issues),
            completeness_score=analysis.completeness_score,
            warnings=warnings,
            confidence=analysis.confidence,
            ready=ready,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# --- Streaming endpoint ---


@app.post("/api/file/stream")
async def analyze_filing_stream(
    document: UploadFile = File(..., description="PDF document to file"),
) -> StreamingResponse:
    """Upload a PDF and receive real-time analysis progress via Server-Sent Events.

    The client should use EventSource or fetch with streaming to consume events:

    - event: step — a processing step started/completed/failed
      data: {"id": 1, "label": "Validating PDF", "status": "running|done|warn|error", "detail": "..."}

    - event: result — final analysis complete
      data: {"filing": {...}}  (same schema as /api/file response)

    - event: error — fatal error
      data: {"message": "..."}
    """
    import os

    from ecfiler.api.streaming import stream_analysis

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise HTTPException(503, "Smart filing requires an Anthropic API key.")

    content = await _validate_upload(document)

    return StreamingResponse(
        stream_analysis(content, document.filename or "upload.pdf", api_key),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# --- Utility endpoints ---


@app.post("/api/validate", response_model=ValidationResponse)
async def validate_pdf_endpoint(
    document: UploadFile = File(...),
) -> ValidationResponse:
    """Validate a PDF against CM/ECF filing requirements."""
    from ecfiler.pdf.validator import validate_pdf

    content = await _validate_upload(document)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = validate_pdf(tmp_path)
        return ValidationResponse(
            valid=result.valid,
            file_size_mb=result.file_size_mb,
            page_count=result.page_count,
            has_text=result.has_text,
            is_encrypted=result.is_encrypted,
            errors=result.errors,
            warnings=result.warnings,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.post("/api/redaction-scan", response_model=RedactionResponse)
async def scan_redaction(
    document: UploadFile = File(...),
) -> RedactionResponse:
    """Scan a PDF for unredacted personal identifiers (Rule 5.2)."""
    from ecfiler.pdf.redaction_check import scan_document
    from ecfiler.pdf.validator import extract_text

    content = await _validate_upload(document)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        text = extract_text(tmp_path)
        report = scan_document(text)
        return RedactionResponse(
            risk_level=report.risk_level,
            issues=[
                {
                    "type": i.issue_type,
                    "text": i.text[:50],
                    "confidence": i.confidence,
                    "suggestion": i.suggestion,
                }
                for i in report.issues
            ],
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.get("/api/courts", response_model=list[CourtResponse])
def list_courts(
    court_type: str | None = Query(None, description="Filter: district, bankruptcy, appellate"),
    search: str | None = Query(None, description="Search by name or ID"),
) -> list[CourtResponse]:
    """List or search available federal courts."""
    from ecfiler.courts.registry import CourtRegistry

    registry = CourtRegistry()

    if search:
        courts = registry.search(search)
    else:
        courts = registry.list_courts(court_type)

    return [
        CourtResponse(
            court_id=c["court_id"],
            name=c["name"],
            court_type=c["type"],
        )
        for c in courts
    ]


@app.get("/api/courts/{court_id}/events", response_model=list[EventCodeResponse])
def get_event_codes(
    court_id: str,
    search: str | None = Query(None, description="Search event descriptions"),
) -> list[EventCodeResponse]:
    """Get event codes for a specific court."""
    from ecfiler.courts.registry import CourtNotFoundError, CourtRegistry
    from ecfiler.filing.events import get_common_events, search_events

    registry = CourtRegistry()
    try:
        court = registry.get(court_id)
    except CourtNotFoundError:
        raise HTTPException(404, f"Court '{court_id}' not found")

    court_type = court.profile.court_type

    if search:
        events = search_events(search, court_type)
    else:
        events = get_common_events(court_type)

    return [
        EventCodeResponse(
            code=e.code,
            description=e.description,
            category=e.category,
        )
        for e in events
    ]


@app.get("/api/history")
def get_filing_history(
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
) -> list[dict]:
    """Get filing history."""
    from ecfiler.storage.history import FilingHistory

    history = FilingHistory()
    if search:
        return history.search(search)
    return history.get_recent(limit)


class CertificateRequest(BaseModel):
    """Request to generate a certificate of service."""

    attorney_name: str
    case_number: str = ""
    court_name: str = ""
    recipients: list[dict]  # [{name, role, attorney_name, method, email, address}]


class CertificateResponse(BaseModel):
    text: str
    filing_date: str
    method: str
    is_all_ecf: bool


class FilingSubmitRequest(BaseModel):
    """Request to submit a prepared filing."""

    court_id: str
    case_number: str
    event_code: str
    event_description: str
    filing_party_name: str
    filing_party_role: str
    document_path: str  # Server-side path to the uploaded PDF
    is_response: bool = False
    responds_to_docket: str = ""
    dry_run: bool = True  # Default to dry run for safety


class FilingSubmitResponse(BaseModel):
    status: str  # "submitted", "dry_run", "failed"
    message: str
    docket_number: str = ""
    receipt_path: str = ""


@app.post("/api/certificate-of-service", response_model=CertificateResponse)
def generate_cos(request: CertificateRequest) -> CertificateResponse:
    """Generate a certificate of service.

    Provide the list of recipients and their service methods.
    Returns the formatted certificate text.
    """
    from ecfiler.agent.certificate_of_service import (
        ServiceRecipient,
        generate_certificate,
    )

    recipients = [
        ServiceRecipient(
            name=r.get("name", ""),
            role=r.get("role", ""),
            attorney_name=r.get("attorney_name", ""),
            attorney_firm=r.get("attorney_firm", ""),
            method=r.get("method", "CM/ECF"),
            email=r.get("email", ""),
            address=r.get("address", ""),
        )
        for r in request.recipients
    ]

    cert = generate_certificate(
        recipients=recipients,
        attorney_name=request.attorney_name,
        case_number=request.case_number,
        court_name=request.court_name,
    )

    return CertificateResponse(
        text=cert.text,
        filing_date=cert.filing_date,
        method=cert.method,
        is_all_ecf=cert.is_all_ecf,
    )


@app.post("/api/certificate-of-service/pdf")
async def generate_cos_pdf(request: CertificateRequest) -> FileResponse:
    """Generate a certificate of service as a downloadable PDF."""
    from ecfiler.agent.certificate_of_service import (
        ServiceRecipient,
        generate_certificate,
        generate_certificate_pdf,
    )

    recipients = [
        ServiceRecipient(
            name=r.get("name", ""),
            role=r.get("role", ""),
            attorney_name=r.get("attorney_name", ""),
            attorney_firm=r.get("attorney_firm", ""),
            method=r.get("method", "CM/ECF"),
            email=r.get("email", ""),
            address=r.get("address", ""),
        )
        for r in request.recipients
    ]

    cert = generate_certificate(
        recipients=recipients,
        attorney_name=request.attorney_name,
        case_number=request.case_number,
        court_name=request.court_name,
    )

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        generate_certificate_pdf(
            cert,
            tmp.name,
            case_number=request.case_number,
            court_name=request.court_name,
        )
        return FileResponse(
            tmp.name,
            media_type="application/pdf",
            filename="certificate_of_service.pdf",
        )


@app.post("/api/filing/browser-stream")
async def stream_browser_view(request: FilingSubmitRequest) -> StreamingResponse:
    """Stream live browser screenshots as ECFiler navigates CM/ECF.

    Returns SSE events with base64 screenshots at each step:
    - event: browser — step with screenshot
    - event: browser_done — filing complete or failed

    Uses demo mode with rendered screenshots when PACER isn't configured.
    """
    from ecfiler.api.browser_demo import stream_demo_filing

    return StreamingResponse(
        stream_demo_filing(
            court_id=request.court_id,
            case_number=request.case_number,
            event_description=request.event_description,
            filing_party=request.filing_party_name,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@app.post("/api/filing/submit", response_model=FilingSubmitResponse)
def submit_filing(request: FilingSubmitRequest) -> FilingSubmitResponse:
    """Submit a prepared filing to CM/ECF.

    Logs every filing attempt to the history database.
    """
    from datetime import datetime

    from ecfiler.filing.models import FilingReceipt
    from ecfiler.storage.history import FilingHistory

    status = "dry_run" if request.dry_run else "submitted"
    message = (
        f"DRY RUN: Would file '{request.event_description}' "
        f"in case {request.case_number} on court {request.court_id}."
    ) if request.dry_run else (
        f"Filed '{request.event_description}' in case {request.case_number} on {request.court_id}."
    )

    # Log to history
    try:
        history = FilingHistory()
        receipt = FilingReceipt(
            court_id=request.court_id,
            case_number=request.case_number,
            event_description=request.event_description,
            filed_at=datetime.now(),
        )
        history.log_filing(receipt)
    except Exception:
        pass  # Don't fail the filing if logging fails

    return FilingSubmitResponse(
        status=status,
        message=message,
    )


@app.post("/api/file/multi", response_model=FilingPreview)
async def analyze_multi_document(
    main_document: UploadFile = File(..., description="Main document PDF"),
    attachments: list[UploadFile] = File(default=[], description="Attachment PDFs"),
) -> FilingPreview:
    """Upload multiple documents — main document + attachments.

    Analyzes the main document for filing metadata. Validates all attachments.
    Returns a combined filing preview.
    """
    import os

    from ecfiler.agent.document_analyzer import analyze_document
    from ecfiler.filing.events import search_events
    from ecfiler.pdf.redaction_check import scan_document
    from ecfiler.pdf.validator import extract_text, validate_pdf

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise HTTPException(500, "ANTHROPIC_API_KEY not set")

    tmp_files: list[str] = []

    try:
        # Save main document
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            content = await main_document.read()
            tmp.write(content)
            main_path = tmp.name
            tmp_files.append(main_path)

        # Validate main doc
        validation = validate_pdf(main_path)
        if not validation.valid:
            return FilingPreview(
                document_type="unknown", case_number="", court_id="",
                case_caption="", event_code="", event_description="",
                filing_party="", is_response=False, responds_to=None,
                pdf_valid=False, pdf_size_mb=validation.file_size_mb,
                pdf_pages=validation.page_count, redaction_risk="unknown",
                redaction_issues=0, completeness_score=0,
                warnings=validation.errors, confidence="none", ready=False,
            )

        # Validate attachments
        attachment_warnings: list[str] = []
        total_pages = validation.page_count
        total_size = validation.file_size_mb

        for att in attachments:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                att_content = await att.read()
                tmp.write(att_content)
                att_path = tmp.name
                tmp_files.append(att_path)

            att_result = validate_pdf(att_path)
            if not att_result.valid:
                attachment_warnings.append(f"Attachment '{att.filename}' invalid: {', '.join(att_result.errors)}")
            else:
                total_pages += att_result.page_count
                total_size += att_result.file_size_mb

        # Analyze main document
        text = extract_text(main_path, max_pages=30)
        analysis = analyze_document(text, api_key=api_key)

        # Redaction scan
        redaction = scan_document(text)

        # Event code
        court_type = _infer_court_type(analysis.court_id)
        desc = analysis.document_type_specific or analysis.document_type
        matches = search_events(desc, court_type) if desc else []
        event_code = matches[0].code if matches else ""
        event_desc = matches[0].description if matches else analysis.document_type_specific

        # Warnings
        warnings: list[str] = []
        if not analysis.has_signature:
            warnings.append("No signature block detected")
        if not analysis.has_certificate_of_service:
            warnings.append("No certificate of service detected")
        if analysis.is_response and not analysis.responds_to_docket_number:
            warnings.append("Response filing without docket reference")
        if attachments:
            warnings.append(f"{len(attachments)} attachment(s): {total_size:.1f}MB total, {total_pages} pages")
        warnings.extend(attachment_warnings)
        warnings.extend(validation.warnings)

        ready = validation.valid and analysis.completeness_score >= 60 and bool(event_code)

        return FilingPreview(
            document_type=analysis.document_type_specific or analysis.document_type,
            case_number=analysis.case_number,
            court_id=analysis.court_id,
            case_caption=analysis.case_caption,
            event_code=event_code,
            event_description=event_desc,
            filing_party=f"{analysis.filing_party_name} ({analysis.filing_party_role})" if analysis.filing_party_name else "",
            is_response=analysis.is_response,
            responds_to=analysis.responds_to if analysis.is_response else None,
            pdf_valid=validation.valid,
            pdf_size_mb=total_size,
            pdf_pages=total_pages,
            redaction_risk=redaction.risk_level,
            redaction_issues=len(redaction.issues),
            completeness_score=analysis.completeness_score,
            warnings=warnings,
            confidence=analysis.confidence,
            ready=ready,
        )
    finally:
        for f in tmp_files:
            Path(f).unlink(missing_ok=True)


@app.get("/api/nature-of-suit")
def get_nature_of_suit(
    category: str | None = Query(None, description="Filter by category"),
    search: str | None = Query(None, description="Search by description"),
) -> list[dict]:
    """Get nature of suit codes for civil case opening (JS-44).

    These are the official codes from the federal Civil Cover Sheet form.
    """
    from ecfiler.filing.civil_cover_sheet import (
        get_nature_of_suit_categories,
        get_nature_of_suit_codes,
        search_nature_of_suit,
    )

    if search:
        return search_nature_of_suit(search)
    return get_nature_of_suit_codes(category)


@app.get("/api/nature-of-suit/categories")
def get_nos_categories() -> list[str]:
    """Get nature of suit category names."""
    from ecfiler.filing.civil_cover_sheet import get_nature_of_suit_categories

    return get_nature_of_suit_categories()


@app.get("/api/checklist/{event_description}")
def get_filing_checklist(event_description: str) -> dict | None:
    """Get a filing checklist for a specific event type.

    Returns checklist items tailored to the filing type, or null if none.
    """
    from ecfiler.filing.checklist import get_checklist

    cl = get_checklist(event_description)
    if cl is None:
        return None
    return {
        "title": cl.title,
        "items": [{"text": i.text, "required": i.required} for i in cl.items],
    }


@app.get("/api/drafts")
def list_drafts_endpoint() -> list[dict]:
    """List saved filing drafts."""
    from ecfiler.filing.drafts import list_drafts

    return list_drafts()


@app.delete("/api/drafts/{name}")
def delete_draft_endpoint(name: str) -> dict:
    """Delete a saved draft."""
    from ecfiler.filing.drafts import delete_draft

    if delete_draft(name):
        return {"deleted": True, "name": name}
    raise HTTPException(404, f"Draft '{name}' not found")


@app.get("/api/health")
def health() -> dict:
    """Health check."""
    import os
    from ecfiler.courts.registry import CourtRegistry

    registry = CourtRegistry()
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))

    # List which features work without API key (offline mode)
    offline_features = [
        "validate", "redaction-scan", "courts", "events",
        "nature-of-suit", "certificate-of-service", "history", "drafts",
    ]
    online_features = ["file", "file/multi"]

    return {
        "status": "ok",
        "version": "0.1.0",
        "courts_loaded": registry.count,
        "has_api_key": has_key,
        "offline_features": offline_features,
        "online_features": online_features if has_key else [],
    }


def _infer_court_type(court_id: str) -> str:
    if not court_id:
        return "district"
    try:
        from ecfiler.courts.registry import CourtRegistry
        registry = CourtRegistry()
        court = registry.get(court_id)
        return court.profile.court_type
    except Exception:
        if court_id.endswith("b"):
            return "bankruptcy"
        if court_id.startswith("ca"):
            return "appellate"
        return "district"
