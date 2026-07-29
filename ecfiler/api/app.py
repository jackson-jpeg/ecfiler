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

import jwt
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from jwt import PyJWKClient
from pydantic import BaseModel

from ecfiler.filing.models import Filing
from ecfiler.logging import get_logger

logger = get_logger(__name__)

STATIC_DIR = Path(__file__).parent / "static"

# The hosted service refuses sealed/restricted content outright: a hosted
# server is the wrong place for material a court has ordered protected. See
# docs/sealed-document-policy.md.
SEALED_REFUSED = (
    "ECFiler's hosted service does not accept sealed or restricted documents. "
    "File sealed documents through the local CLI on your own machine, or "
    "conventionally under seal per the court's local rule. "
    "See docs/sealed-document-policy.md."
)

# --- CORS configuration ---
_allowed_origins = os.environ.get("ECFILER_ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _allowed_origins.split(",") if o.strip()]


def validate_auth_config(env: dict[str, str] | None = None) -> None:
    """Fail fast on a misconfigured server rather than degrading to weaker auth.

    Either CLERK_ISSUER must be set (production: verified Clerk JWTs) or
    ECFILER_DEV_AUTH=1 must be set explicitly (local development: trusts the
    X-User-Id header). Missing config must never silently mean "unauthenticated".
    """
    env = os.environ if env is None else env
    if env.get("CLERK_ISSUER", "").strip():
        return
    if env.get("ECFILER_DEV_AUTH", "") == "1":
        return
    raise RuntimeError(
        "ECFiler API auth is not configured. Set CLERK_ISSUER to your Clerk issuer "
        "URL, or set ECFILER_DEV_AUTH=1 to explicitly opt into unauthenticated "
        "local development mode."
    )


validate_auth_config()

app = FastAPI(
    title="ECFiler API",
    description="AI-native filing for Federal CM/ECF courts",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-User-Id"],
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
    """Extract the authenticated user ID, or fail with 401.

    Production: a verified Clerk JWT in the Authorization header is the only
    accepted credential. The X-User-Id header is honored solely when
    ECFILER_DEV_AUTH=1 was set explicitly — it is a dev convenience, never a
    fallback for missing or invalid tokens.
    """
    if authorization.startswith("Bearer "):
        user_id = _verify_clerk_token(authorization[7:])
        if user_id:
            return user_id

    if os.environ.get("ECFILER_DEV_AUTH", "") == "1" and x_user_id:
        return x_user_id

    raise HTTPException(401, "Authentication required")


def _verify_clerk_token(token: str) -> str | None:
    """Verify a Clerk JWT and return the user ID (sub claim).

    Returns None if verification fails.
    """
    clerk_issuer = os.environ.get("CLERK_ISSUER", "")
    if not clerk_issuer:
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
    user_id: str = Depends(get_current_user),
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

    # Refuse sealed content before anything else — the hosted service never
    # handles it, regardless of server configuration.
    if exhibits:
        import json as _json_precheck

        try:
            _raw_precheck = _json_precheck.loads(exhibits)
        except _json_precheck.JSONDecodeError:
            _raw_precheck = []
        if isinstance(_raw_precheck, list) and any(
            isinstance(item, dict) and item.get("sealed") for item in _raw_precheck
        ):
            raise HTTPException(403, SEALED_REFUSED)

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
            if any(isinstance(item, dict) and item.get("sealed") for item in raw):
                raise HTTPException(403, SEALED_REFUSED)
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

        if court_type == "appellate":
            from ecfiler.filing.appellate_rules import (
                classify_appellate_doc,
                validate_appellate_document,
            )
            from ecfiler.pdf.validator import extract_metrics

            metrics = extract_metrics(tmp_path)
            appellate_type = classify_appellate_doc(
                analysis.document_type_specific or analysis.document_type,
                event_desc,
            )
            appellate_result = validate_appellate_document(
                appellate_type,
                metrics.word_count,
                metrics.page_count,
                metrics.line_count,
                metrics.text,
            )
            warnings.extend(appellate_result.errors)
            warnings.extend(appellate_result.warnings)

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
    user_id: str = Depends(get_current_user),
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


class AttestationInfo(BaseModel):
    """The human act behind a staging request — recorded, never inferred."""

    attested: bool = False
    attestor_name: str = ""
    attestation_text: str = ""
    client_timestamp: str = ""


class FilingSubmitRequest(BaseModel):
    """Request to stage a prepared filing."""

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
    dry_run: bool = True  # Deprecated: ignored — the hosted service only stages
    attestation: AttestationInfo | None = None


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


# --- Staging: the hosted product prepares; the human files -------------------
#
# There is no server-side submission to CM/ECF, and there never was: the
# previous /api/filing/browser-stream endpoint rendered a synthetic animation
# of a filing that did not happen. It has been deleted rather than relabeled.
# What the hosted product actually does — validate, analyze, and assemble a
# ready-to-file package — is now what it says it does.


class StagedPackage(BaseModel):
    """Everything the filer needs to submit the filing themselves.

    `filing` is the canonical record: the exact ecfiler.filing.models.Filing
    the CLI resumes from, built here so the hosted API and the local CLI can
    never disagree about the package shape (the flat fields alongside it are
    display projections for the web UI). Its `staged` provenance pins the
    court; the CLI refuses to file in any other.
    """

    stage_code: str
    staged_at: str
    court_id: str
    court_name: str
    ecf_login_url: str
    ecf_filing_url: str
    case_number: str
    event_code: str
    event_description: str
    docket_text: str
    filing_party: str
    fee_text: str
    fee_status: str
    filing: Filing
    exhibits: list[ExhibitInfo] = []
    checklist: list[dict] = []
    instructions: list[str] = []


STAGE_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"


def new_stage_code(length: int = 11) -> str:
    """A stage code the filer can paste into a shell without quoting.

    `token_urlsafe` can produce a leading "-", which the CLI reads as an
    option (`Error: No such option '-c'`) — caught by the QA-day round trip.
    Letters and digits only, ambiguous glyphs (0/O, 1/l/I) dropped; 11 chars
    of this 57-symbol alphabet is ~64 bits, the same as token_urlsafe(8).
    """
    from secrets import choice

    return "".join(choice(STAGE_CODE_ALPHABET) for _ in range(length))


def _build_staged_package(request: FilingSubmitRequest) -> StagedPackage:
    from datetime import datetime, timezone

    from ecfiler.courts.registry import CourtEnvironmentError, CourtRegistry
    from ecfiler.filing.checklist import get_checklist
    from ecfiler.filing.fees import format_fee, get_fee
    from ecfiler.filing.models import (
        CaseInfo,
        CourtType,
        EventCode,
        FilingParty,
        FilingStatus,
        RelatedEntry,
        StagedProvenance,
    )

    try:
        court = CourtRegistry().get(request.court_id)
        profile = court.profile
    except CourtEnvironmentError as e:
        raise HTTPException(422, str(e))
    except Exception:
        raise HTTPException(404, f"Court '{request.court_id}' not found")

    fee = get_fee(request.event_description, profile.court_type)
    checklist = get_checklist(request.event_description)
    docket_text = request.event_description

    stage_code = new_stage_code()
    staged_at = datetime.now(timezone.utc).isoformat()

    # The canonical filing record — the exact object the CLI resumes from.
    # Documents are attached on the filing machine, so the list starts empty.
    canonical = Filing(
        court_id=profile.court_id,
        court_type=CourtType(profile.court_type),
        case=CaseInfo(case_number=request.case_number),
        event=EventCode(code=request.event_code, description=request.event_description),
        filing_party=FilingParty(
            party_name=request.filing_party_name,
            party_role=request.filing_party_role,
        ),
        parties=[request.filing_party_name],
        docket_text=docket_text,
        is_response=request.is_response,
        related_entry=(
            RelatedEntry(docket_number=request.responds_to_docket)
            if request.responds_to_docket
            else None
        ),
        status=FilingStatus.EVENT_SELECTED,
        staged=StagedProvenance(
            stage_code=stage_code,
            staged_at=staged_at,
            court_id=profile.court_id,
            ecf_url=profile.ecf_url,
            environment=profile.environment,
        ),
    )

    instructions = [
        f"Log into CM/ECF for {profile.name} with your own credentials: {profile.login_url}",
        "Select the filing menu for your case type and enter the case number "
        f"{request.case_number}.",
        f"Select the event: {request.event_description}.",
        f"Select the filing party: {request.filing_party_name} "
        f"({request.filing_party_role}).",
        "Upload your main document PDF (the validated file from this session)."
        + (
            f" Upload {len(request.exhibits)} attachment(s) with the labels and "
            "descriptions listed in this package."
            if request.exhibits
            else ""
        ),
        f"Confirm the docket text matches: \"{docket_text}\"",
        f"Set fee status to '{request.fee_status}'"
        + (f" — expected fee {format_fee(fee)}." if fee else "."),
        "Review the court's confirmation screen carefully, then submit. "
        "Save the NEF for your records.",
    ]

    return StagedPackage(
        stage_code=stage_code,
        staged_at=staged_at,
        court_id=profile.court_id,
        court_name=profile.name,
        ecf_login_url=profile.login_url,
        ecf_filing_url=profile.filing_url,
        case_number=request.case_number,
        event_code=request.event_code,
        event_description=request.event_description,
        docket_text=docket_text,
        filing_party=f"{request.filing_party_name} ({request.filing_party_role})",
        fee_text=format_fee(fee) if fee else "",
        fee_status=request.fee_status,
        filing=canonical,
        exhibits=request.exhibits,
        checklist=(
            [{"text": i.text, "required": i.required} for i in checklist.items]
            if checklist
            else []
        ),
        instructions=instructions,
    )


def _staged_dir(user_id: str) -> Path:
    from ecfiler.config import CONFIG_DIR

    safe_user = "".join(c for c in user_id if c.isalnum() or c in "._-") or "anon"
    path = CONFIG_DIR / "staged" / safe_user
    path.mkdir(parents=True, exist_ok=True)
    return path


@app.post("/api/filing/stage", response_model=StagedPackage)
def stage_filing(
    request: FilingSubmitRequest,
    user_id: str = Depends(get_current_user),
) -> StagedPackage:
    """Assemble a validated, ready-to-file package. The human files it.

    Sealed filings are refused (docs/sealed-document-policy.md). The stage
    code can be pulled into the local CLI with `ecfiler stage-pull <code>`.
    """
    from datetime import datetime

    from ecfiler.filing.models import FilingReceipt
    from ecfiler.storage.attestation import AttestationLog
    from ecfiler.storage.history import FilingHistory

    if request.is_sealed:
        raise HTTPException(403, SEALED_REFUSED)

    if request.attestation is None or not request.attestation.attested:
        raise HTTPException(
            422,
            "Staging requires attorney attestation: set attestation.attested with "
            "the attestor's name and the attestation text shown to them.",
        )

    package = _build_staged_package(request)

    (_staged_dir(user_id) / f"{package.stage_code}.json").write_text(
        package.model_dump_json(indent=2)
    )

    filing_id: int | None = None
    try:
        history = FilingHistory()
        receipt = FilingReceipt(
            court_id=request.court_id,
            case_number=request.case_number,
            event_description=request.event_description,
            filed_at=datetime.now(),
        )
        filing_id = history.log_filing(receipt, user_id=user_id, status="staged")
    except Exception:
        logger.exception("Failed to log staged filing to history")

    try:
        AttestationLog().record(
            kind="staged",
            attestor_name=request.attestation.attestor_name or "unnamed",
            attestation_text=request.attestation.attestation_text,
            payload=request.model_dump(exclude={"attestation"}),
            user_id=user_id,
            filing_id=filing_id,
            context_text=package.model_dump_json(),
        )
    except Exception:
        logger.exception("Failed to record staging attestation")

    return package


@app.get("/api/filing/stage/{stage_code}", response_model=StagedPackage)
def get_staged_package(
    stage_code: str,
    user_id: str = Depends(get_current_user),
) -> StagedPackage:
    """Fetch a previously staged package (e.g. from the CLI)."""
    import json as _json

    safe_code = "".join(c for c in stage_code if c.isalnum() or c in "._-")
    path = _staged_dir(user_id) / f"{safe_code}.json"
    if not path.exists():
        raise HTTPException(404, "Staged package not found")
    try:
        return StagedPackage(**_json.loads(path.read_text()))
    except Exception:
        raise HTTPException(
            409,
            "This staged package predates the current package format "
            "(no canonical filing record) — stage the filing again.",
        )


@app.post("/api/filing/submit", response_model=FilingSubmitResponse)
def submit_filing(
    request: FilingSubmitRequest,
    user_id: str = Depends(get_current_user),
) -> FilingSubmitResponse:
    """DEPRECATED alias for /api/filing/stage — kept one release.

    This endpoint never submitted anything to CM/ECF; its "submitted" and
    "dry_run" statuses were a pretense over what was always staging. It now
    delegates to the stage handler and answers honestly.
    """
    package = stage_filing(request, user_id)
    return FilingSubmitResponse(
        status="staged",
        message=(
            f"Staged '{request.event_description}' for case {request.case_number} "
            f"({request.court_id}). ECFiler does not submit from the hosted "
            f"service — follow the package instructions to file it yourself, or "
            f"pull it into the CLI with stage code {package.stage_code}."
        ),
    )


@app.post("/api/file/multi", response_model=FilingPreview)
async def analyze_multi_document(
    main_document: UploadFile = File(..., description="Main document PDF"),
    attachments: list[UploadFile] = File(default=[], description="Attachment PDFs"),
    user_id: str = Depends(get_current_user),
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

        if court_type == "appellate":
            from ecfiler.filing.appellate_rules import (
                classify_appellate_doc,
                validate_appellate_document,
            )
            from ecfiler.pdf.validator import extract_metrics

            metrics = extract_metrics(main_path)
            appellate_type = classify_appellate_doc(
                analysis.document_type_specific or analysis.document_type,
                event_desc,
            )
            appellate_result = validate_appellate_document(
                appellate_type,
                metrics.word_count,
                metrics.page_count,
                metrics.line_count,
                metrics.text,
            )
            warnings.extend(appellate_result.errors)
            warnings.extend(appellate_result.warnings)

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
def delete_draft_endpoint(name: str, user_id: str = Depends(get_current_user)) -> dict:
    """Delete a saved draft owned by the authenticated user."""
    from ecfiler.filing.drafts import delete_draft, list_drafts

    owned = {
        d["name"]
        for d in list_drafts()
        if d.get("user_id", "") in ("", user_id)
    }
    if name in owned and delete_draft(name):
        return {"deleted": True, "name": name}
    raise HTTPException(404, f"Draft '{name}' not found")


# PDF compression (storage.history.compress_old_pdfs) is deliberately not an
# HTTP endpoint: it is maintenance, and an unauthenticated route that rewrites
# archived filings is an attack surface. Run it from the host instead:
#   python -c "from ecfiler.storage.history import compress_old_pdfs; compress_old_pdfs(days_old=30)"
# (the deployment runbook schedules this as a systemd timer).


@app.get("/api/export")
def export_account_data(user_id: str = Depends(get_current_user)) -> dict:
    """Machine-readable export of everything the server holds for this user.

    This is the Privacy Policy's export promise. Attestation records include
    their payloads while those exist; after account deletion only chain
    metadata would remain (and the account would be gone with it).
    """
    import json
    from datetime import datetime, timezone

    from ecfiler.storage.attestation import AttestationLog
    from ecfiler.storage.history import FilingHistory

    staged = []
    for path in sorted(_staged_dir(user_id).glob("*.json")):
        try:
            staged.append(json.loads(path.read_text()))
        except (OSError, json.JSONDecodeError):
            continue

    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "filing_history": FilingHistory().get_all_for_user(user_id),
        "staged_packages": staged,
        "attestations": AttestationLog().export_for_user(user_id),
    }


@app.delete("/api/account")
def delete_account_data(user_id: str = Depends(get_current_user)) -> dict:
    """Delete all server-side data for the authenticated user, immediately.

    Removes filing history, archived documents, staged packages, and the case
    data behind this user's attestation records. The attestation chain records
    themselves are retained: they hold only salted hashes and metadata, prove
    that attestations occurred, and — with their salts deleted here — cannot be
    linked back to any case. Account removal itself (the Clerk identity) is a
    separate step in the account portal.
    """
    import shutil

    from ecfiler.storage.attestation import AttestationLog
    from ecfiler.storage.history import FilingHistory, delete_user_documents

    history_rows = FilingHistory().delete_for_user(user_id)
    documents = delete_user_documents(user_id)

    staged_dir = _staged_dir(user_id)
    staged = len(list(staged_dir.glob("*.json")))
    shutil.rmtree(staged_dir, ignore_errors=True)

    attestation_payloads = AttestationLog().purge_user_payloads(user_id)

    logger.info(
        "Account data deleted for %s: %d history rows, %d documents, "
        "%d staged packages, %d attestation payloads",
        user_id, history_rows, documents, staged, attestation_payloads,
    )
    return {
        "deleted": True,
        "filing_history_rows": history_rows,
        "archived_documents": documents,
        "staged_packages": staged,
        "attestation_payloads": attestation_payloads,
    }


# --- Server-side PACER credential storage: removed 2026-07 ---
#
# ECFiler no longer accepts, stores, or handles CM/ECF or PACER credentials on
# any server, consistent with the AO's July 10, 2023 guidance on sharing filer
# credentials with third-party services. Credentials belong in the OS keyring on
# the attorney's own machine (see docs/credential-architecture.md). The stub
# below answers 410 for one release so stale clients fail loudly, and the
# startup purge removes anything stored under the old model — including the
# SQLite free pages that would otherwise retain ciphertext after a DROP.


def purge_stored_pacer_credentials(db_path: Path | None = None) -> int:
    """Drop the legacy pacer_credentials table and scrub the database file.

    Idempotent; returns the number of purged rows. VACUUM is load-bearing:
    without it, dropped rows survive in SQLite free pages on disk.
    """
    import sqlite3
    from datetime import datetime, timezone

    from ecfiler.config import CONFIG_DIR

    db_path = db_path or (CONFIG_DIR / "users.db")
    if not db_path.exists():
        return 0

    conn = sqlite3.connect(db_path)
    try:
        (table_exists,) = conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='pacer_credentials'"
        ).fetchone()
        if not table_exists:
            return 0
        (count,) = conn.execute("SELECT count(*) FROM pacer_credentials").fetchone()
        conn.execute("DROP TABLE pacer_credentials")
        conn.commit()
        conn.isolation_level = None  # VACUUM cannot run inside a transaction
        conn.execute("VACUUM")
    finally:
        conn.close()

    logger.warning(
        "purged pacer_credentials: %d row(s) at %s",
        count,
        datetime.now(timezone.utc).isoformat(),
    )
    return count


@app.on_event("startup")
def _purge_legacy_credentials_on_startup() -> None:
    purge_stored_pacer_credentials()


_CREDENTIALS_GONE = (
    "ECFiler no longer stores PACER or CM/ECF credentials server-side. "
    "Run 'ecfiler setup' to keep credentials in your own machine's OS keyring. "
    "See docs/credential-architecture.md."
)


@app.post("/api/pacer/credentials")
@app.get("/api/pacer/credentials")
@app.post("/api/pacer/test")
def pacer_credentials_gone() -> None:
    raise HTTPException(410, _CREDENTIALS_GONE)



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
