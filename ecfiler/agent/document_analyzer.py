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
Your job is to extract structured metadata from a legal document so it \
can be filed on CM/ECF. Be precise — this data drives automated filing.

Return ONLY a JSON object with these keys (null for fields you cannot determine):

{
  "document_type": "motion | brief | notice | complaint | answer | response | reply | stipulation | petition | order | other",
  "document_type_specific": "the exact filing title, e.g., 'Motion to Dismiss for Failure to State a Claim'",
  "case_number": "exact case number from the caption, e.g., '1:24-cv-01234-ABC' or '24-12345'",
  "court_name": "full court name, e.g., 'United States District Court for the Southern District of New York'",
  "court_id": "PACER court ID — use state abbreviation + district: nysd, nyed, cacd, cand, txsd, ilnd, flsd, dcd, etc. For bankruptcy add 'b': nysb, cacb. For appellate: ca2, ca9, cadc.",
  "case_caption": "full caption, e.g., 'SMITH v. JONES CORPORATION'",
  "filing_party_name": "the party on whose behalf this is filed — look for 'Respectfully submitted' or 'Dated:' sections",
  "filing_party_role": "plaintiff | defendant | petitioner | respondent | debtor | creditor | movant | appellant | appellee | other",
  "attorney_name": "from the /s/ signature block or 'Submitted by' line",
  "attorney_bar_number": "bar number, bar ID, or attorney ID if present near signature",
  "attorney_firm": "law firm name if present",
  "is_response": "true if this is an opposition, response, reply, answer, objection, or sur-reply to another filing. false otherwise.",
  "responds_to": "if is_response, describe what it responds to, e.g., 'Defendant's Motion to Dismiss (Dkt. 45)'",
  "responds_to_docket_number": "just the docket number, e.g., '45'. Look for 'Dkt.', 'Docket', 'ECF No.', 'Doc.', 'D.E.'",
  "suggested_event_code_category": "Motions | Briefs | Notices | Responses | Initiating | Other",
  "references_docket_entries": ["list of docket numbers referenced anywhere in the document"],
  "has_certificate_of_service": "true if the document contains a Certificate of Service section",
  "has_proposed_order": "true if a proposed order is embedded or referenced as attached",
  "has_signature": "true if there is a /s/ signature line or wet signature",
  "page_count_stated": "number if the document states its own page count (e.g., in a certificate of compliance), else null",
  "word_count_stated": "number if stated, else null",
  "confidence": "high | medium | low — based on how much you could extract"
}

EXTRACTION TIPS:
- The case number is usually on the first page in the caption. Federal format: \
[division]:[year]-[type]-[number]-[judge initials], e.g., 1:24-cv-01234-ABC.
- Court name is in the header/caption: "UNITED STATES DISTRICT COURT FOR THE ..."
- Court ID mapping: Southern District of New York = nysd, Central District of California = cacd, \
Northern District of Illinois = ilnd, District of Delaware = ded, Eastern District of Virginia = vaed.
- The filing party is whoever submitted the document — look at the end, \
not the caption (caption lists all parties, signature block shows who filed).
- For is_response: oppositions ("in opposition to"), replies ("in reply to"), \
answers to complaints, objections, and sur-replies are all responses.
- Docket references appear as: "Dkt. 45", "ECF No. 45", "Doc. 45", "D.E. 45", "[Dkt. 45]".
- Certificate of service is usually the last section. Look for "CERTIFICATE OF SERVICE" \
or "I hereby certify".
- The /s/ signature pattern: /s/ [Name] or /s/[Name].
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
