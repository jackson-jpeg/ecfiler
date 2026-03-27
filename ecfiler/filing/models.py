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


class Document(BaseModel):
    """A document to be filed."""

    file_path: str
    description: str = ""
    is_main: bool = True  # Main document vs attachment
    validation: DocumentValidation | None = None

    @property
    def filename(self) -> str:
        return Path(self.file_path).name

    @property
    def is_valid(self) -> bool:
        return self.validation is not None and self.validation.valid


class CaseInfo(BaseModel):
    """Information about the case being filed in."""

    case_number: str
    title: str = ""
    judge: str = ""
    status: str = ""


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


class RedactionFinding(BaseModel):
    """A potential redaction issue."""

    issue_type: str
    text: str
    confidence: str
    suggestion: str


class Filing(BaseModel):
    """Complete filing record."""

    court_id: str
    court_type: CourtType = CourtType.DISTRICT
    case: CaseInfo
    event: EventCode
    documents: list[Document] = Field(default_factory=list)
    related_entry: RelatedEntry | None = None
    parties: list[str] = Field(default_factory=list)
    docket_text: str = ""
    status: FilingStatus = FilingStatus.INIT
    redaction_issues: list[RedactionFinding] = Field(default_factory=list)

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
