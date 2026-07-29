"""OASIS ECF 4.01 core message layer — Florida gap item #4 (pre-approval).

Builds ReviewFiling request XML and parses the two response shapes the
Portal program documents name (MessageReceipt at submission time;
FilingReviewComplete when review finishes), against the *public* OASIS
Electronic Court Filing 4.01 specification.

Honesty about provenance (docs/fl/technical-specs.md §1, §9):

- ECF 4.01 is an approved-errata release of ECF 4.0; the schema namespaces
  keep the ``-4.0`` suffix. The namespace URIs below are the public ECF 4.0
  schema set's, with NIEM 2.0 for core/justice content, as required by the
  spec's "XML schemas are the only normative representations" rule.
- Florida's Portal extensions and its own XSD/WSDL set are released only
  after TPV application approval. Everything Florida-specific is therefore
  isolated in ``FL_EXTENSION_NS`` and the ``build_*`` element layout, and
  the whole module is expected to need adjustment against the real XSDs —
  that rework risk is priced into the gap analysis (§6, item #5).

What is *not* at risk of rework: the invariants. Illegal states raise here
and will keep raising whatever the final wire shape is — no lead document,
invalid UCN, new-case or fee-bearing paths (outside the §5 certification
scope), filename-rule violations, and submissions over the 50 MB cap.
"""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass, field
from xml.etree import ElementTree as ET

from ecfiler.courts.florida.document_rules import (
    TRIAL_SUBMISSION_LIMIT_MB,
    validate_filename,
)
from ecfiler.courts.florida.submission import SubmissionStatus
from ecfiler.courts.florida.ucn import UCN, parse_ucn

# --- Namespaces -------------------------------------------------------------
# Public ECF 4.0/4.01 schema set (OASIS) and the NIEM 2.0 releases it builds
# on. ECF 4.01 §2 (Message Structures) and the schema set's xsd files are the
# normative source; these URIs are from that public set.
NS = {
    "core": "urn:oasis:names:tc:legalxml-courtfiling:schema:xsd:CoreFilingMessage-4.0",
    "ecf": "urn:oasis:names:tc:legalxml-courtfiling:schema:xsd:CommonTypes-4.0",
    "receipt": "urn:oasis:names:tc:legalxml-courtfiling:schema:xsd:MessageReceiptMessage-4.0",
    "review": "urn:oasis:names:tc:legalxml-courtfiling:schema:xsd:FilingReviewCompleteNotificationMessage-4.0",
    "nc": "http://niem.gov/niem/niem-core/2.0",
    "j": "http://niem.gov/niem/domains/jxdm/4.0",
}

# Placeholder for Florida's gated Portal-extension namespace: the real URI
# ships with the post-approval XSD package. Nothing outside this constant
# may hard-code a Florida wire detail.
FL_EXTENSION_NS = "urn:ecfiler:placeholder:florida-portal-extension"

for prefix, uri in {**NS, "flext": FL_EXTENSION_NS}.items():
    ET.register_namespace(prefix, uri)


def _q(prefix: str, local: str) -> str:
    ns = FL_EXTENSION_NS if prefix == "flext" else NS[prefix]
    return f"{{{ns}}}{local}"


class ECF401Error(ValueError):
    """An illegal message state. Raised, never warned."""


# --- Request model ----------------------------------------------------------


@dataclass
class Attachment:
    """One document rendition attached to the filing."""

    filename: str
    content: bytes
    document_type: str = ""

    def __post_init__(self) -> None:
        problems = validate_filename(self.filename)
        if problems:
            raise ECF401Error(
                f"filename {self.filename!r} violates Portal rules: "
                + "; ".join(problems)
            )
        if not self.content:
            raise ECF401Error(f"attachment {self.filename!r} is empty")


@dataclass
class ReviewFilingRequest:
    """An Existing Case, no-fee ReviewFiling — the §5 certification scope.

    New Case initiation and fee-bearing submissions are deliberately
    unrepresentable: they need structured party data and the undocumented
    fee-settlement mechanism (gap analysis §5 points 2 and 5).
    """

    ucn: str
    lead_document: Attachment
    connected_documents: list[Attachment] = field(default_factory=list)
    filing_code: str = ""
    filing_description: str = ""
    submitter_name: str = ""
    fee_amount: float = 0.0

    parsed_ucn: UCN = field(init=False)

    def __post_init__(self) -> None:
        # parse_ucn raises UCNError on garbage; strict mode enforces the
        # 20-character uniform layout including the county code table.
        try:
            self.parsed_ucn = parse_ucn(self.ucn)
        except Exception as exc:
            raise ECF401Error(f"invalid UCN {self.ucn!r}: {exc}") from exc
        if self.fee_amount:
            raise ECF401Error(
                "fee-bearing submissions are outside the certification scope "
                "(no-fee Existing Case only — gap analysis §5)"
            )
        if not self.submitter_name.strip():
            raise ECF401Error("submitter_name is required")
        total_bytes = len(self.lead_document.content) + sum(
            len(d.content) for d in self.connected_documents
        )
        limit = TRIAL_SUBMISSION_LIMIT_MB * 1024 * 1024
        if total_bytes > limit:
            raise ECF401Error(
                f"submission is {total_bytes / (1024 * 1024):.1f} MB; the "
                f"Portal caps a single submission at {TRIAL_SUBMISSION_LIMIT_MB} MB "
                "(Technology Standards §2.1.2)"
            )


# --- Request construction ---------------------------------------------------


def build_review_filing(request: ReviewFilingRequest) -> bytes:
    """Serialize a ReviewFiling CoreFilingMessage.

    Layout follows the public ECF 4.01 CoreFilingMessage structure: case
    identification, submitter, then one FilingLeadDocument and zero or more
    FilingConnectedDocument entries, each carrying a base64 rendition.
    Element placement inside the Florida extension points will move once the
    gated XSDs arrive; the content set is what the public documents require.
    """
    root = ET.Element(_q("core", "CoreFilingMessage"))

    case = ET.SubElement(root, _q("core", "Case"))
    tracking = ET.SubElement(case, _q("nc", "CaseTrackingID"))
    tracking.text = str(request.parsed_ucn)
    county = ET.SubElement(case, _q("flext", "CountyCode"))
    county.text = request.parsed_ucn.county_code

    submitter = ET.SubElement(root, _q("ecf", "FilingParty"))
    name = ET.SubElement(submitter, _q("nc", "PersonName"))
    full = ET.SubElement(name, _q("nc", "PersonFullName"))
    full.text = request.submitter_name

    if request.filing_code or request.filing_description:
        filing_event = ET.SubElement(root, _q("flext", "FilingCode"))
        filing_event.set("code", request.filing_code)
        filing_event.text = request.filing_description

    def attach(element_name: str, doc: Attachment, sequence: int) -> None:
        el = ET.SubElement(root, _q("core", element_name))
        meta = ET.SubElement(el, _q("nc", "DocumentFileControlID"))
        meta.text = doc.filename
        if doc.document_type:
            dtype = ET.SubElement(el, _q("nc", "DocumentCategoryText"))
            dtype.text = doc.document_type
        seq = ET.SubElement(el, _q("ecf", "DocumentSequenceID"))
        seq.text = str(sequence)
        rendition = ET.SubElement(el, _q("ecf", "DocumentRendition"))
        binary = ET.SubElement(rendition, _q("nc", "BinaryBase64Object"))
        binary.text = base64.b64encode(doc.content).decode("ascii")

    attach("FilingLeadDocument", request.lead_document, 0)
    for i, doc in enumerate(request.connected_documents, start=1):
        attach("FilingConnectedDocument", doc, i)

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


# --- Response parsing -------------------------------------------------------


@dataclass
class MessageReceipt:
    """ECF MessageReceiptMessage: did the Portal take the submission?"""

    accepted: bool
    submission_id: str
    errors: list[tuple[str, str]]  # (code, text); code "0" means no error


def parse_message_receipt(xml_bytes: bytes) -> MessageReceipt:
    root = _parse(xml_bytes)
    _require_tag(root, "MessageReceiptMessage")

    errors: list[tuple[str, str]] = []
    for err in root.iter(_q("ecf", "Error")):
        code = _text(err.find(_q("ecf", "ErrorCode")))
        text = _text(err.find(_q("ecf", "ErrorText")))
        errors.append((code, text))

    real_errors = [(c, t) for c, t in errors if c not in ("", "0")]
    submission_id = _text(root.find(f".//{_q('nc', 'DocumentIdentification')}/{_q('nc', 'IdentificationID')}"))
    return MessageReceipt(
        accepted=not real_errors,
        submission_id=submission_id,
        errors=real_errors,
    )


# Portal review outcomes → the submission lifecycle from submission.py.
# Left side: status vocabulary the program documents use for review results
# (Test Case Checklist TS001–TS006; Application "statuses are returned as
# submissions are processed"). Case-insensitive.
_REVIEW_STATUS_MAP = {
    "accepted": SubmissionStatus.ACCEPTED,
    "filed": SubmissionStatus.ACCEPTED,
    "docketed": SubmissionStatus.ACCEPTED,
    "correction": SubmissionStatus.CORRECTION_QUEUE,
    "correction queue": SubmissionStatus.CORRECTION_QUEUE,
    "pending correction": SubmissionStatus.CORRECTION_QUEUE,
    "abandoned": SubmissionStatus.ABANDONED,
    "under review": SubmissionStatus.UNDER_REVIEW,
    "received": SubmissionStatus.RECEIVED,
}


@dataclass
class ReviewResult:
    """FilingReviewComplete: what the clerk decided."""

    status: SubmissionStatus
    raw_status: str
    submission_id: str
    reviewer_comment: str


def parse_review_complete(xml_bytes: bytes) -> ReviewResult:
    root = _parse(xml_bytes)
    _require_tag(root, "FilingReviewCompleteNotificationMessage")

    raw = _text(root.find(f".//{_q('ecf', 'FilingStatus')}"))
    if not raw:
        raise ECF401Error("review-complete message carries no FilingStatus")
    status = _REVIEW_STATUS_MAP.get(raw.strip().lower())
    if status is None:
        raise ECF401Error(
            f"unknown review status {raw!r} — do not guess an outcome; "
            f"known statuses: {sorted(_REVIEW_STATUS_MAP)}"
        )
    return ReviewResult(
        status=status,
        raw_status=raw,
        submission_id=_text(
            root.find(f".//{_q('nc', 'DocumentIdentification')}/{_q('nc', 'IdentificationID')}")
        ),
        reviewer_comment=_text(root.find(f".//{_q('ecf', 'FilingReviewCommentsText')}")),
    )


# --- helpers ----------------------------------------------------------------

_TAG_RE = re.compile(r"^\{(?P<ns>[^}]+)\}(?P<local>.+)$")


def _parse(xml_bytes: bytes) -> ET.Element:
    try:
        return ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ECF401Error(f"not well-formed XML: {exc}") from exc


def _require_tag(root: ET.Element, local: str) -> None:
    m = _TAG_RE.match(root.tag)
    if not m or m.group("local") != local:
        raise ECF401Error(f"expected {local}, got {root.tag}")


def _text(el: ET.Element | None) -> str:
    return (el.text or "").strip() if el is not None else ""
