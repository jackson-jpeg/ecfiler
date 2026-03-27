"""Document Intelligence — the core of ECFiler's AI-native approach.

Instead of asking the attorney to fill out forms, we read the document
and figure out everything:

1. What type of filing is this? (motion, brief, notice, complaint...)
2. Which case does it belong to? (extract case number from caption)
3. Which court? (extract from caption or header)
4. Who is filing it? (extract attorney info from signature block)
5. Is it responding to something? (extract references to prior filings)
6. Is it complete? (check for missing attachments, signatures, etc.)

The attorney just reviews and confirms. Zero form-filling.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import anthropic

from ecfiler.logging import get_logger

logger = get_logger(__name__)

ANALYSIS_PROMPT = """\
You are a legal document analyst for a federal court e-filing system. \
Analyze the following document and extract structured filing metadata.

Extract ALL of the following from the document text. If a field cannot \
be determined, set it to null. Be precise — this data will be used to \
file the document on CM/ECF.

Return a JSON object with these exact keys:

{
  "document_type": "motion | brief | notice | complaint | answer | response | reply | stipulation | petition | order | other",
  "document_type_specific": "e.g., 'Motion to Dismiss', 'Reply Brief in Support of Motion for Summary Judgment'",
  "case_number": "extracted case number, e.g., '1:24-cv-01234-ABC'",
  "court_name": "full court name if mentioned, e.g., 'United States District Court for the Southern District of New York'",
  "court_id": "PACER court ID if determinable, e.g., 'nysd'",
  "case_caption": "full case caption, e.g., 'SMITH v. JONES CORP'",
  "filing_party_name": "who is filing this (from signature block or 'Respectfully submitted' section)",
  "filing_party_role": "plaintiff | defendant | petitioner | respondent | debtor | movant | other",
  "attorney_name": "attorney name from signature block",
  "attorney_bar_number": "bar number if present",
  "attorney_firm": "firm name if present",
  "is_response": true/false,
  "responds_to": "description of what this responds to, e.g., 'Defendant's Motion to Dismiss (Dkt. #45)'",
  "responds_to_docket_number": "docket number being responded to, if mentioned",
  "suggested_event_code_category": "Motions | Briefs | Notices | Responses | Initiating | Other",
  "references_docket_entries": ["list of docket numbers referenced in the document"],
  "has_certificate_of_service": true/false,
  "has_proposed_order": true/false,
  "has_signature": true/false,
  "page_count_stated": null or number (if document states its own page/word count),
  "word_count_stated": null or number,
  "confidence": "high | medium | low"
}

IMPORTANT:
- Extract the case number exactly as written (including judge initials)
- For court_id, use the PACER convention: nysd, cacd, txsd, etc.
- is_response should be true for oppositions, replies, answers, objections, responses
- Check the last pages carefully for certificate of service and signature blocks
"""


@dataclass
class DocumentAnalysis:
    """Complete analysis of a document for filing."""

    # Document identification
    document_type: str = ""
    document_type_specific: str = ""

    # Case identification
    case_number: str = ""
    court_name: str = ""
    court_id: str = ""
    case_caption: str = ""

    # Filing party
    filing_party_name: str = ""
    filing_party_role: str = ""
    attorney_name: str = ""
    attorney_bar_number: str = ""
    attorney_firm: str = ""

    # Response context
    is_response: bool = False
    responds_to: str = ""
    responds_to_docket_number: str = ""

    # Event code suggestion
    suggested_event_code_category: str = ""

    # Document completeness
    references_docket_entries: list[str] = field(default_factory=list)
    has_certificate_of_service: bool = False
    has_proposed_order: bool = False
    has_signature: bool = False
    page_count_stated: int | None = None
    word_count_stated: int | None = None

    # Analysis quality
    confidence: str = "low"
    raw_response: dict | None = None

    @property
    def is_complete(self) -> bool:
        """Whether we have enough info to auto-populate a filing."""
        return bool(
            self.document_type
            and self.case_number
            and self.filing_party_name
        )

    @property
    def completeness_score(self) -> int:
        """0-100 score of how much we auto-extracted."""
        fields = [
            self.document_type,
            self.case_number,
            self.court_id,
            self.filing_party_name,
            self.filing_party_role,
            self.attorney_name,
            self.suggested_event_code_category,
        ]
        filled = sum(1 for f in fields if f)
        return int(filled / len(fields) * 100)

    @property
    def missing_fields(self) -> list[str]:
        """Fields we couldn't extract that need manual entry."""
        missing = []
        if not self.case_number:
            missing.append("case_number")
        if not self.court_id:
            missing.append("court")
        if not self.document_type:
            missing.append("document_type")
        if not self.filing_party_name:
            missing.append("filing_party")
        return missing


def analyze_document(
    document_text: str,
    api_key: str,
    model: str = "claude-sonnet-4-20250514",
) -> DocumentAnalysis:
    """Analyze a document and extract all filing metadata.

    This is the core intelligence that makes ECFiler AI-native.
    Drop a PDF, get a fully-populated filing form.

    Args:
        document_text: Extracted text from the PDF
        api_key: Anthropic API key
        model: Claude model to use

    Returns:
        DocumentAnalysis with all extracted fields
    """
    logger.info("Analyzing document (%d chars)", len(document_text))

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=ANALYSIS_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Analyze this document for federal court e-filing:\n\n"
                    f"{document_text[:80000]}"
                ),
            }
        ],
    )

    from ecfiler.claude_client import _extract_json

    raw = _extract_json(response.content[0].text)

    if raw.get("parse_error"):
        logger.warning("Failed to parse document analysis response")
        return DocumentAnalysis(raw_response=raw)

    analysis = DocumentAnalysis(
        document_type=raw.get("document_type", ""),
        document_type_specific=raw.get("document_type_specific", ""),
        case_number=raw.get("case_number", ""),
        court_name=raw.get("court_name", ""),
        court_id=raw.get("court_id", ""),
        case_caption=raw.get("case_caption", ""),
        filing_party_name=raw.get("filing_party_name", ""),
        filing_party_role=raw.get("filing_party_role", ""),
        attorney_name=raw.get("attorney_name", ""),
        attorney_bar_number=raw.get("attorney_bar_number", ""),
        attorney_firm=raw.get("attorney_firm", ""),
        is_response=raw.get("is_response", False),
        responds_to=raw.get("responds_to", ""),
        responds_to_docket_number=str(raw.get("responds_to_docket_number", "") or ""),
        suggested_event_code_category=raw.get("suggested_event_code_category", ""),
        references_docket_entries=raw.get("references_docket_entries", []),
        has_certificate_of_service=raw.get("has_certificate_of_service", False),
        has_proposed_order=raw.get("has_proposed_order", False),
        has_signature=raw.get("has_signature", False),
        page_count_stated=raw.get("page_count_stated"),
        word_count_stated=raw.get("word_count_stated"),
        confidence=raw.get("confidence", "low"),
        raw_response=raw,
    )

    logger.info(
        "Analysis complete: type=%s case=%s confidence=%s completeness=%d%%",
        analysis.document_type,
        analysis.case_number,
        analysis.confidence,
        analysis.completeness_score,
    )

    return analysis
