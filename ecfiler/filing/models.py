"""Pydantic data models for filing workflow."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class CourtType(str, Enum):
    DISTRICT = "district"
    BANKRUPTCY = "bankruptcy"
    APPELLATE = "appellate"


class FilingStatus(str, Enum):
    INIT = "init"
    COURT_SELECTED = "court_selected"
    CASE_FOUND = "case_found"
    EVENT_SELECTED = "event_selected"
    DOCUMENTS_VALIDATED = "documents_validated"
    FORM_FILLED = "form_filled"
    AWAITING_REVIEW = "awaiting_review"
    CONFIRMED = "confirmed"
    SUBMITTED = "submitted"
    RECEIPT_SAVED = "receipt_saved"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DocumentValidation(BaseModel):
    """Validation results for a single document."""

    valid: bool = False
    file_size_mb: float = 0
    page_count: int = 0
    has_text: bool = False
    is_encrypted: bool = False
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class SealingLevel(str, Enum):
    """Document sealing/restriction level for CM/ECF."""

    PUBLIC = "public"  # Normal public filing
    SEALED = "sealed"  # Filed under seal — not publicly accessible
    RESTRICTED = "restricted"  # Restricted access (e.g., Social Security cases)
    EX_PARTE = "ex_parte"  # Ex parte submission — opposing party not served


class Document(BaseModel):
    """A document to be filed."""

    file_path: str
    description: str = ""
    is_main: bool = True  # Main document vs attachment
    validation: DocumentValidation | None = None
    sealing: SealingLevel = SealingLevel.PUBLIC
    is_amended: bool = False  # True if this amends a prior filing
    amends_docket_number: str = ""  # Docket # of the document being amended

    @property
    def filename(self) -> str:
        return Path(self.file_path).name

    @property
    def is_valid(self) -> bool:
        return self.validation is not None and self.validation.valid

    @property
    def is_sealed(self) -> bool:
        return self.sealing in (SealingLevel.SEALED, SealingLevel.RESTRICTED)

    @property
    def requires_leave(self) -> bool:
        """Whether filing this document requires leave of court."""
        return self.sealing == SealingLevel.SEALED


class CaseInfo(BaseModel):
    """Information about the case being filed in."""

    case_number: str
    title: str = ""
    judge: str = ""
    status: str = ""  # open, closed
    case_type: str = ""  # cv, cr, bk, ap
    date_filed: str = ""
    parties: list["PartyInfo"] = Field(default_factory=list)

    @property
    def plaintiff_names(self) -> list[str]:
        return [p.name for p in self.parties if p.role in ("plaintiff", "petitioner", "debtor")]

    @property
    def defendant_names(self) -> list[str]:
        return [p.name for p in self.parties if p.role in ("defendant", "respondent")]


class PartyInfo(BaseModel):
    """A party in a case."""

    name: str
    role: str  # plaintiff, defendant, petitioner, respondent, debtor, creditor, etc.
    attorney: str = ""  # Representing attorney name
    is_pro_se: bool = False


class FilingParty(BaseModel):
    """Which party the filer is acting on behalf of."""

    party_name: str
    party_role: str  # plaintiff, defendant, etc.
    attorney_name: str = ""
    attorney_bar_number: str = ""

    @property
    def display(self) -> str:
        parts = [f"{self.party_name} ({self.party_role})"]
        if self.attorney_name:
            parts.append(f"by {self.attorney_name}")
        return " ".join(parts)


class EventCode(BaseModel):
    """A CM/ECF event code."""

    code: str
    description: str
    category: str = ""


class RelatedEntry(BaseModel):
    """A related docket entry."""

    docket_number: str
    description: str = ""
    date: str = ""


class DocketEntry(BaseModel):
    """A docket entry from the case (for selecting related filings)."""

    number: str
    date: str = ""
    description: str = ""
    filed_by: str = ""

    @property
    def display(self) -> str:
        parts = [f"#{self.number}"]
        if self.date:
            parts.append(self.date)
        parts.append(self.description[:80])
        return " — ".join(parts)


class CaseOpeningData(BaseModel):
    """Data required for opening a new case (complaint/petition filing).

    This requires extra validation since incorrect info creates a permanent
    court record.
    """

    case_type: str  # cv (civil), cr (criminal), bk (bankruptcy)
    cause_of_action: str = ""  # Statute or cause
    jurisdiction_basis: str = ""  # federal question, diversity, etc.
    demand_amount: str = ""  # Dollar amount for diversity cases
    jury_demand: str = ""  # plaintiff, defendant, both, none

    # Plaintiff/Petitioner info
    plaintiffs: list[PartyInfo] = Field(default_factory=list)
    # Defendant/Respondent info
    defendants: list[PartyInfo] = Field(default_factory=list)

    # Bankruptcy-specific
    chapter: str = ""  # 7, 11, 12, 13
    asset_case: bool = False
    estimated_creditors: str = ""  # Range: 1-49, 50-99, etc.
    estimated_assets: str = ""
    estimated_liabilities: str = ""

    @property
    def is_bankruptcy(self) -> bool:
        return self.case_type == "bk"

    @property
    def all_parties(self) -> list[PartyInfo]:
        return self.plaintiffs + self.defendants


class RedactionFinding(BaseModel):
    """A potential redaction issue."""

    issue_type: str
    text: str
    confidence: str
    suggestion: str


class ExhibitEntry(BaseModel):
    """A single exhibit with label + description (UI-ordered)."""

    file_path: str = ""
    label: str = ""
    description: str = ""
    sealed: bool = False


class ExhibitPackageModel(BaseModel):
    """Filing-time exhibit package: ordered exhibits with auto-labels."""

    exhibits: list[ExhibitEntry] = Field(default_factory=list)
    has_sealed_exhibits: bool = False


class Filing(BaseModel):
    """Complete filing record."""

    court_id: str
    court_type: CourtType = CourtType.DISTRICT
    case: CaseInfo
    event: EventCode
    documents: list[Document] = Field(default_factory=list)
    related_entry: RelatedEntry | None = None
    filing_party: FilingParty | None = None
    parties: list[str] = Field(default_factory=list)
    docket_text: str = ""
    status: FilingStatus = FilingStatus.INIT
    redaction_issues: list[RedactionFinding] = Field(default_factory=list)
    case_opening: CaseOpeningData | None = None  # Set when filing initiates a case
    is_response: bool = False  # True if this is a response to another filing
    exhibit_package: ExhibitPackageModel | None = None

    @property
    def main_document(self) -> Document | None:
        for doc in self.documents:
            if doc.is_main:
                return doc
        return None

    @property
    def attachments(self) -> list[Document]:
        return [d for d in self.documents if not d.is_main]

    @property
    def all_valid(self) -> bool:
        return all(d.is_valid for d in self.documents)

    @property
    def is_case_opening(self) -> bool:
        """Whether this filing opens a new case (complaint, petition, etc.)."""
        return self.case_opening is not None


class FilingReceipt(BaseModel):
    """Confirmation of a successful filing."""

    filing_id: str = ""
    court_id: str
    case_number: str
    docket_number: str = ""
    event_description: str = ""
    filed_at: datetime = Field(default_factory=datetime.now)
    confirmation_text: str = ""
    receipt_path: str = ""
    screenshot_path: str = ""
    pdf_path: str = ""
