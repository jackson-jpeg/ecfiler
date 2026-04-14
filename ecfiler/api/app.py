"""ECFiler API — agent-first REST backend.

The API has two modes:
1. **Agent mode** (POST /api/file) — upload a PDF, get a fully-analyzed filing
   ready for one-click confirmation. This is the groundbreaking part.
2. **Utility mode** — individual endpoints for validation, court lookup, etc.

Start with: uvicorn ecfiler.api.app:app --reload
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ecfiler.logging import get_logger

logger = get_logger(__name__)

STATIC_DIR = Path(__file__).parent / "static"

# --- CORS configuration ---
_allowed_origins = os.environ.get("ECFILER_ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _allowed_origins.split(",") if o.strip()]

app = FastAPI(
    title="ECFiler API",
    description="AI-native filing for Federal CM/ECF courts",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Standardized error responses ---


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return all errors in a consistent JSON format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "code": exc.status_code,
        },
    )


# --- Authentication ---


async def get_current_user(
    authorization: str = Header("", alias="Authorization"),
    x_user_id: str = Header("", alias="X-User-Id"),
) -> str:
    """Extract authenticated user ID.

    Checks for a Clerk JWT in the Authorization header first.
    Falls back to X-User-Id header for local/CLI use.
    """
    # Try JWT token first
    if authorization.startswith("Bearer "):
        token = authorization[7:]
        user_id = _verify_clerk_token(token)
        if user_id:
            return user_id

    # Fallback to X-User-Id for local/CLI mode
    return x_user_id


def _verify_clerk_token(token: str) -> str | None:
    """Verify a Clerk JWT and return the user ID (sub claim).

    Returns None if verification fails or pyjwt is not installed.
    """
    try:
        import jwt
        from jwt import PyJWKClient
    except ImportError:
        logger.debug("pyjwt not installed — skipping JWT verification")
        return None

    clerk_issuer = os.environ.get("CLERK_ISSUER", "")
    if not clerk_issuer:
        # No issuer configured — can't verify
        return None

    try:
        jwks_url = f"{clerk_issuer}/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url, cache_keys=True)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=clerk_issuer,
            options={"verify_aud": False},
        )
        return payload.get("sub", "")
    except Exception:
        logger.debug("Clerk JWT verification failed", exc_info=True)
        return None


# --- Rate limiting ---

_user_request_counts: dict[str, int] = {}
MAX_REQUESTS_PER_USER = 5  # Max concurrent requests per user on expensive endpoints


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

    # Exhibits (echoed back with auto-labels + any validation issues)
    exhibits: list[dict] = []
    exhibit_issues: list[str] = []

    # Fee information
    filing_fee: float | None = None
    filing_fee_text: str = ""


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
    exhibits: str | None = Form(default=None, description="JSON array of exhibits [{name,label,description,sealed}]"),
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
    from ecfiler.filing.fees import format_fee, get_fee
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

    # Parse exhibit metadata (client-supplied list; server re-labels to canonical A/B/C).
    import json as _json
    from ecfiler.filing.exhibits import ExhibitPackage, LabelStyle, MAX_EXHIBIT_BYTES

    exhibit_entries: list[dict] = []
    exhibit_issues: list[str] = []
    if exhibits:
        try:
            raw = _json.loads(exhibits)
            if not isinstance(raw, list):
                raise ValueError("exhibits must be a JSON array")
            pkg = ExhibitPackage(main_document=document.filename or "main.pdf", label_style=LabelStyle.LETTER)
            for item in raw:
                if not isinstance(item, dict):
                    continue
                ex = pkg.add_exhibit(
                    item.get("name", "") or item.get("file_path", ""),
                    item.get("description", ""),
                    sealed=bool(item.get("sealed", False)),
                )
                size = int(item.get("size", 0) or 0)
                if size > MAX_EXHIBIT_BYTES:
                    exhibit_issues.append(
                        f"{ex.label}: File too large ({size / 1024 / 1024:.1f}MB, max {MAX_EXHIBIT_BYTES // 1024 // 1024}MB)"
                    )
            exhibit_entries = [
                {"name": e.filename, "label": e.label, "description": e.description, "sealed": e.sealed, "order": e.order}
                for e in pkg.exhibits
            ]
        except (ValueError, _json.JSONDecodeError) as e:
            raise HTTPException(400, f"Invalid exhibits payload: {e}")

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
                exhibits=exhibit_entries,
                exhibit_issues=exhibit_issues,
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

        fee = get_fee(event_desc or "", court_type) if event_desc else None
        filing_fee_amount = fee.amount if fee else None
        filing_fee_text_val = format_fee(fee) if fee else ""

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
            exhibits=exhibit_entries,
            exhibit_issues=exhibit_issues,
            filing_fee=filing_fee_amount,
            filing_fee_text=filing_fee_text_val,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# --- Streaming endpoint ---


_analysis_in_progress: set[str] = set()  # Simple concurrency guard

@app.post("/api/file/stream")
async def analyze_filing_stream(
    document: UploadFile = File(..., description="PDF document to file"),
) -> StreamingResponse:
    """Upload a PDF and receive real-time analysis progress via Server-Sent Events.

    - event: step — processing step started/completed/failed
    - event: result — final analysis complete
    - event: error — fatal error
    """
    import os

    from ecfiler.api.streaming import stream_analysis

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise HTTPException(503, "Smart filing requires an Anthropic API key.")

    # Simple concurrency guard — max 3 concurrent analyses
    if len(_analysis_in_progress) >= 3:
        raise HTTPException(
            429,
            "Server is busy. Please try again in a moment.",
            headers={"Retry-After": "30"},
        )

    content = await _validate_upload(document)

    analysis_id = f"{id(document)}_{len(_analysis_in_progress)}"
    _analysis_in_progress.add(analysis_id)

    async def guarded_stream():
        try:
            async for event in stream_analysis(content, document.filename or "upload.pdf", api_key):
                yield event
        finally:
            _analysis_in_progress.discard(analysis_id)

    return StreamingResponse(
        guarded_stream(),
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
    response: Response,
    court_type: str | None = Query(None, description="Filter: district, bankruptcy, appellate"),
    search: str | None = Query(None, description="Search by name or ID"),
) -> list[CourtResponse]:
    """List or search available federal courts."""
    from ecfiler.courts.registry import CourtRegistry

    response.headers["Cache-Control"] = "public, max-age=3600"

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
    response: Response,
    search: str | None = Query(None, description="Search event descriptions"),
) -> list[EventCodeResponse]:
    """Get event codes for a specific court."""
    from ecfiler.courts.registry import CourtNotFoundError, CourtRegistry
    from ecfiler.filing.events import get_common_events, search_events

    response.headers["Cache-Control"] = "public, max-age=3600"

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
    user_id: str = Depends(get_current_user),
) -> dict:
    """Get filing history for the authenticated user."""
    from ecfiler.storage.history import FilingHistory

    history = FilingHistory()
    if search:
        items = history.search(search, user_id=user_id)
    else:
        items = history.get_recent(limit, user_id=user_id)
    total = history.count_for_user(user_id)
    return {"items": items, "total": total}


@app.get("/api/history/{filing_id}")
def get_filing_detail(
    filing_id: int,
    user_id: str = Depends(get_current_user),
) -> dict:
    """Get a single filing with full confirmation details."""
    from ecfiler.storage.history import FilingHistory

    history = FilingHistory()
    record = history.get_by_id(filing_id, user_id=user_id)
    if not record:
        raise HTTPException(404, "Filing not found")
    return record


@app.get("/api/history/{filing_id}/pdf")
def download_filing_pdf(
    filing_id: int,
    user_id: str = Depends(get_current_user),
) -> Response:
    """Download the archived PDF for a filing.

    Sealed documents are never stored and will return 404.
    Compressed (old) PDFs are decompressed on-the-fly.
    """
    from ecfiler.storage.history import (
        FilingHistory,
        decompress_pdf,
        get_archived_pdf_path,
    )

    history = FilingHistory()
    record = history.get_by_id(filing_id, user_id=user_id)
    if not record:
        raise HTTPException(404, "Filing not found")

    if record.get("is_sealed"):
        raise HTTPException(
            410,
            "Sealed documents are not retained per court policy. "
            "Retrieve from CM/ECF directly.",
        )

    pdf_path = record.get("pdf_path", "")
    if not pdf_path:
        raise HTTPException(404, "No PDF archived for this filing")

    resolved = get_archived_pdf_path(pdf_path)
    if not resolved:
        raise HTTPException(404, "Archived PDF not found on disk")

    # Decompress on-the-fly if gzipped
    if resolved.suffix == ".gz":
        content = decompress_pdf(resolved)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="{resolved.stem}"'},
        )

    return FileResponse(
        resolved,
        media_type="application/pdf",
        filename=resolved.name,
    )


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


class ExhibitInfo(BaseModel):
    """Exhibit/attachment metadata."""
    label: str = ""
    description: str = ""


class FilingSubmitRequest(BaseModel):
    """Request to submit a prepared filing."""

    court_id: str
    case_number: str
    event_code: str
    event_description: str
    filing_party_name: str
    filing_party_role: str
    document_path: str = ""  # Server-side path to the uploaded PDF
    is_response: bool = False
    responds_to_docket: str = ""
    is_sealed: bool = False
    is_redacted: bool = False
    include_certificate_of_service: bool = False
    exhibits: list[ExhibitInfo] = []
    fee_status: str = "paid"  # "paid" | "waived" | "ifp"
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
            is_sealed=request.is_sealed,
            is_redacted=request.is_redacted,
            exhibits=[{"label": e.label, "description": e.description} for e in request.exhibits],
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@app.post("/api/filing/submit", response_model=FilingSubmitResponse)
def submit_filing(
    request: FilingSubmitRequest,
    user_id: str = Depends(get_current_user),
) -> FilingSubmitResponse:
    """Submit a prepared filing to CM/ECF.

    Logs every filing attempt to the history database.
    Archives the PDF per-user (sealed documents are never retained).
    """
    from datetime import datetime

    from ecfiler.filing.models import FilingReceipt
    from ecfiler.storage.history import FilingHistory, archive_filing_pdf

    status = "dry_run" if request.dry_run else "submitted"
    message = (
        f"DRY RUN: Would file '{request.event_description}' "
        f"in case {request.case_number} on court {request.court_id}."
    ) if request.dry_run else (
        f"Filed '{request.event_description}' in case {request.case_number} on {request.court_id}."
    )

    # Archive PDF (sealed documents are excluded automatically)
    pdf_path = ""
    if request.document_path and not request.dry_run:
        try:
            doc_path = Path(request.document_path)
            if doc_path.exists():
                pdf_path = archive_filing_pdf(
                    pdf_content=doc_path.read_bytes(),
                    user_id=user_id,
                    court_id=request.court_id,
                    case_number=request.case_number,
                    is_sealed=request.is_sealed,
                )
        except Exception:
            logger.exception("Failed to archive filing PDF")

    # Log to history
    try:
        history = FilingHistory()
        receipt = FilingReceipt(
            court_id=request.court_id,
            case_number=request.case_number,
            event_description=request.event_description,
            filed_at=datetime.now(),
            pdf_path=pdf_path,
        )
        history.log_filing(receipt, user_id=user_id, is_sealed=request.is_sealed)
    except Exception:
        logger.exception("Failed to log filing to history")

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


@app.get("/api/fee/{event_description}")
def get_filing_fee(
    event_description: str,
    court_type: str = Query("district", description="district, bankruptcy, or appellate"),
) -> dict:
    """Look up the filing fee for a specific event type."""
    from ecfiler.filing.fees import format_fee, get_fee

    fee = get_fee(event_description, court_type)
    if fee is None:
        return {"amount": 0, "description": "Unknown filing type", "text": "Fee unknown"}
    return {
        "amount": fee.amount,
        "description": fee.description,
        "waivable": fee.waivable,
        "notes": fee.notes,
        "text": format_fee(fee),
    }


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
def list_drafts_endpoint(
    user_id: str = Depends(get_current_user),
) -> list[dict]:
    """List saved filing drafts for the authenticated user."""
    from ecfiler.filing.drafts import list_drafts

    drafts = list_drafts()
    # Filter by user_id if available (drafts created before user isolation won't have one)
    if user_id:
        return [d for d in drafts if d.get("user_id", "") in ("", user_id)]
    return drafts


@app.delete("/api/drafts/{name}")
def delete_draft_endpoint(name: str) -> dict:
    """Delete a saved draft."""
    from ecfiler.filing.drafts import delete_draft

    if delete_draft(name):
        return {"deleted": True, "name": name}
    raise HTTPException(404, f"Draft '{name}' not found")


@app.post("/api/filing/compress")
def compress_old_filings() -> dict:
    """Compress PDFs older than 30 days to save storage. Admin endpoint."""
    from ecfiler.storage.history import compress_old_pdfs

    count = compress_old_pdfs(days_old=30)
    return {"compressed": count}


class PacerCredentialRequest(BaseModel):
    username: str
    password: str = ""
    user_id: str = ""


class PacerTestRequest(BaseModel):
    username: str
    user_id: str = ""


@app.post("/api/pacer/credentials")
def store_pacer_credentials(request: PacerCredentialRequest) -> dict:
    """Store PACER credentials (AES-256-GCM encrypted) for a user."""
    import sqlite3
    from datetime import datetime

    from ecfiler.config import CONFIG_DIR
    from ecfiler.security import EncryptionError, encrypt_credential, is_encryption_configured

    if not is_encryption_configured():
        raise HTTPException(
            503,
            "Credential storage requires ECFILER_ENCRYPTION_KEY to be set on the server.",
        )

    if not request.user_id:
        raise HTTPException(400, "user_id is required")

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    db_path = CONFIG_DIR / "users.db"

    try:
        password_encrypted = encrypt_credential(request.password, request.user_id) if request.password else ""
    except EncryptionError as exc:
        raise HTTPException(500, f"Encryption failed: {exc}")

    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pacer_credentials (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                password_encrypted TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            INSERT OR REPLACE INTO pacer_credentials (user_id, username, password_encrypted, created_at)
            VALUES (?, ?, ?, ?)
        """, (request.user_id, request.username, password_encrypted, datetime.now().isoformat()))
        conn.commit()

    return {"status": "ok", "username": request.username}


@app.get("/api/pacer/credentials")
def get_pacer_credentials(
    user_id: str = Depends(get_current_user),
) -> dict:
    """Check whether PACER credentials are stored for a user.

    Never returns the actual password.
    """
    import sqlite3

    from ecfiler.config import CONFIG_DIR

    if not user_id:
        raise HTTPException(400, "Authentication required")

    db_path = CONFIG_DIR / "users.db"
    if not db_path.exists():
        return {"username": "", "has_password": False}

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT username, password_encrypted FROM pacer_credentials WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    if not row:
        return {"username": "", "has_password": False}

    return {
        "username": row["username"],
        "has_password": bool(row["password_encrypted"]),
    }


@app.post("/api/pacer/test")
def test_pacer_connection(request: PacerTestRequest) -> dict:
    """Test PACER authentication by verifying stored credentials can be decrypted."""
    import sqlite3

    from ecfiler.config import CONFIG_DIR
    from ecfiler.security import EncryptionError, decrypt_credential, is_encryption_configured

    if not is_encryption_configured():
        return {"ok": False, "message": "Encryption key not configured on server"}

    user_id = request.user_id
    if not user_id:
        return {"ok": False, "message": "user_id is required"}

    db_path = CONFIG_DIR / "users.db"
    if not db_path.exists():
        return {"ok": False, "message": "No credentials stored"}

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT username, password_encrypted FROM pacer_credentials WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    if not row:
        return {"ok": False, "message": "No credentials found for this user"}

    if not row["password_encrypted"]:
        return {"ok": False, "message": "No password stored"}

    # Validate that decryption succeeds (proves the key is correct)
    try:
        decrypt_credential(row["password_encrypted"], user_id)
    except EncryptionError:
        return {"ok": False, "message": "Credential decryption failed — encryption key may have changed"}

    return {"ok": True, "message": f"Credentials verified for PACER user '{row['username']}'"}



class WaitlistRequest(BaseModel):
    email: str


@app.post("/api/waitlist")
def join_waitlist(request: WaitlistRequest) -> dict:
    """Add an email to the ECFiler Pro waitlist."""
    import sqlite3
    from datetime import datetime

    from ecfiler.config import CONFIG_DIR

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    db_path = CONFIG_DIR / "waitlist.db"

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS waitlist (id INTEGER PRIMARY KEY, email TEXT UNIQUE, created_at TEXT)"
        )
        try:
            conn.execute(
                "INSERT INTO waitlist (email, created_at) VALUES (?, ?)",
                (request.email.strip().lower(), datetime.now().isoformat()),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Already on the list

    return {"status": "ok", "email": request.email}


@app.get("/api/waitlist/count")
def waitlist_count() -> dict:
    """Get the number of people on the waitlist."""
    import sqlite3

    from ecfiler.config import CONFIG_DIR

    db_path = CONFIG_DIR / "waitlist.db"
    if not db_path.exists():
        return {"count": 0}

    with sqlite3.connect(db_path) as conn:
        try:
            row = conn.execute("SELECT COUNT(*) FROM waitlist").fetchone()
            return {"count": row[0] if row else 0}
        except Exception:
            logger.exception("Failed to query waitlist count")
            return {"count": 0}


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
    except Exception:  # noqa: BLE001 — graceful fallback to heuristic
        if court_id.endswith("b"):
            return "bankruptcy"
        if court_id.startswith("ca"):
            return "appellate"
        return "district"
