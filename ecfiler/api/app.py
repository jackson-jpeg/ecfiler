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
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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
        raise HTTPException(500, "ANTHROPIC_API_KEY not set")

    # Save upload to temp file
    suffix = Path(document.filename or "upload.pdf").suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await document.read()
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


# --- Utility endpoints ---


@app.post("/api/validate", response_model=ValidationResponse)
async def validate_pdf_endpoint(
    document: UploadFile = File(...),
) -> ValidationResponse:
    """Validate a PDF against CM/ECF filing requirements."""
    from ecfiler.pdf.validator import validate_pdf

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        content = await document.read()
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

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        content = await document.read()
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


@app.get("/api/health")
def health() -> dict:
    """Health check."""
    import os
    from ecfiler.courts.registry import CourtRegistry

    registry = CourtRegistry()
    return {
        "status": "ok",
        "courts_loaded": registry.count,
        "has_api_key": bool(os.environ.get("ANTHROPIC_API_KEY")),
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
