"""Florida Portal submission model and status lifecycle.

Pre-approval work (`docs/fl-certification-gap-analysis.md` item #2). The wire
format — ECF 4.01 plus Florida's proprietary Portal extensions — is not
available until the $500 application is approved, so this module deliberately
models only what the *public* program documents establish: the submission
lifecycle, the lead/exhibit structure, and the per-county test matrix. No XML,
no field names invented from guesswork. When the XSDs arrive, they attach to
this model rather than replacing it.

Sources: `docs/fl/test-case-checklist.md` (TS001–TS009 and its Terms and
Definitions), `docs/fl/technical-specs.md`, `docs/fl/vendor-application.md`.

The lifecycle, in the Portal's own vocabulary:

    submitted ─▶ received ─▶ under_review ─┬─▶ accepted (Clerk verifies in CMS)
                                           └─▶ correction_queue
                                                  │  filer has 5 business days
                                                  ├─▶ resubmitted ─▶ received …
                                                  └─▶ abandoned (aged out)

``abandoned`` and ``accepted`` are terminal. The five-business-day window is the
subject of TS006, which tests it by deliberately letting a submission age out.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum

from ecfiler.courts.florida.ucn import UCN, parse_ucn


class SubmissionStatus(str, Enum):
    """Where a submission sits in the Portal's processing pipeline."""

    DRAFT = "draft"                      # local only; never sent
    SUBMITTED = "submitted"              # handed to the Portal
    RECEIVED = "received"                # Portal assigned a Submission Number
    UNDER_REVIEW = "under_review"        # Portal team / Clerk reviewing
    ACCEPTED = "accepted"                # Clerk verified in county CMS
    CORRECTION_QUEUE = "correction_queue"  # deficiency; filer must fix
    RESUBMITTED = "resubmitted"          # corrected and sent again
    ABANDONED = "abandoned"              # uncorrected past the 5-day window

    @property
    def is_terminal(self) -> bool:
        return self in (SubmissionStatus.ACCEPTED, SubmissionStatus.ABANDONED)

    @property
    def needs_filer_action(self) -> bool:
        return self is SubmissionStatus.CORRECTION_QUEUE


# Permitted transitions. Anything absent is a bug in our state handling or an
# unmodelled Portal behaviour — either way we want it to raise, not to be
# silently absorbed, because a wrong belief about submission state is how a
# filing gets duplicated or a deadline gets missed.
_TRANSITIONS: dict[SubmissionStatus, frozenset[SubmissionStatus]] = {
    SubmissionStatus.DRAFT: frozenset({SubmissionStatus.SUBMITTED}),
    SubmissionStatus.SUBMITTED: frozenset({SubmissionStatus.RECEIVED}),
    SubmissionStatus.RECEIVED: frozenset({
        SubmissionStatus.UNDER_REVIEW,
        SubmissionStatus.ACCEPTED,
        SubmissionStatus.CORRECTION_QUEUE,
    }),
    SubmissionStatus.UNDER_REVIEW: frozenset({
        SubmissionStatus.ACCEPTED,
        SubmissionStatus.CORRECTION_QUEUE,
    }),
    SubmissionStatus.CORRECTION_QUEUE: frozenset({
        SubmissionStatus.RESUBMITTED,
        SubmissionStatus.ABANDONED,
    }),
    SubmissionStatus.RESUBMITTED: frozenset({SubmissionStatus.RECEIVED}),
    SubmissionStatus.ACCEPTED: frozenset(),
    SubmissionStatus.ABANDONED: frozenset(),
}

# "the filer has five business days to correct the deficiency"
# — test-case-checklist.md, Terms and Definitions, Abandoned Filing Queue.
CORRECTION_WINDOW_BUSINESS_DAYS = 5


class SubmissionStateError(RuntimeError):
    """Raised on an illegal submission status transition."""


class FilingPath(str, Enum):
    """The two certification paths. ECFiler seeks EXISTING_CASE first."""

    EXISTING_CASE = "existing"
    NEW_CASE = "new"


@dataclass
class Document:
    """A document in a submission.

    Florida's definitions (test-case-checklist.md, Terms): a *lead document*
    "is filed with the Clerk that is requesting an action"; an *exhibit* "is
    filed in support of a lead document".
    """

    filename: str
    is_lead: bool
    document_type: str = ""
    page_count: int | None = None

    def __post_init__(self) -> None:
        if not self.filename.strip():
            raise ValueError("Document filename is required")


@dataclass
class Submission:
    """One batch submission to the Florida Courts E-Filing Portal."""

    ucn: UCN | None
    filing_path: FilingPath
    documents: list[Document] = field(default_factory=list)
    status: SubmissionStatus = SubmissionStatus.DRAFT
    submission_number: str | None = None
    submitted_at: datetime | None = None
    correction_deadline: date | None = None
    history: list[tuple[SubmissionStatus, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.filing_path is FilingPath.EXISTING_CASE and self.ucn is None:
            raise ValueError(
                "Existing Case filings require a UCN — that is what identifies "
                "the case to file into"
            )
        if self.filing_path is FilingPath.NEW_CASE and self.ucn is not None:
            raise ValueError(
                "New Case filings must not carry a UCN — the clerk assigns it "
                "when the case is created"
            )

    @property
    def lead_documents(self) -> list[Document]:
        return [d for d in self.documents if d.is_lead]

    @property
    def exhibits(self) -> list[Document]:
        return [d for d in self.documents if not d.is_lead]

    def validate_documents(self) -> None:
        """Every submission needs at least one lead document.

        An exhibit is defined by its support of a lead document, so a submission
        of exhibits alone has nothing to support and no action to request.
        """
        if not self.documents:
            raise ValueError("Submission has no documents")
        if not self.lead_documents:
            raise ValueError(
                "Submission has no lead document — an exhibit is filed in "
                "support of a lead document and cannot stand alone"
            )

    def transition(
        self,
        new_status: SubmissionStatus,
        note: str = "",
        *,
        now: datetime | None = None,
    ) -> None:
        """Move to ``new_status``, rejecting transitions the Portal cannot make."""
        allowed = _TRANSITIONS.get(self.status, frozenset())
        if new_status not in allowed:
            raise SubmissionStateError(
                f"Cannot move from {self.status.value} to {new_status.value}. "
                f"Allowed: {sorted(s.value for s in allowed) or 'none (terminal)'}"
            )
        self.status = new_status
        self.history.append((new_status, note))

        stamp = now or datetime.now()
        if new_status is SubmissionStatus.SUBMITTED:
            self.submitted_at = stamp
        elif new_status is SubmissionStatus.CORRECTION_QUEUE:
            self.correction_deadline = add_business_days(
                stamp.date(), CORRECTION_WINDOW_BUSINESS_DAYS
            )
        elif new_status is SubmissionStatus.RESUBMITTED:
            self.correction_deadline = None

    def is_past_correction_deadline(self, today: date | None = None) -> bool:
        """True when an uncorrected submission has aged out (TS006).

        This is our own local reckoning, used to warn the filer early. The
        Portal's determination is authoritative; never mark a submission
        abandoned on the strength of this alone.
        """
        if self.status is not SubmissionStatus.CORRECTION_QUEUE:
            return False
        if self.correction_deadline is None:
            return False
        return (today or date.today()) > self.correction_deadline


def add_business_days(start: date, days: int) -> date:
    """Add ``days`` business days, skipping weekends.

    Court holidays are **not** applied: the observed-holiday list varies by
    county clerk and no authoritative machine-readable list is in the program
    documents. The effect is that this returns a deadline no later than the
    true one, so a warning fires early rather than late — the safe direction
    for a five-day correction window.
    """
    if days < 0:
        raise ValueError("days must be non-negative")
    current = start
    remaining = days
    while remaining > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current


# The eight county CMS targets every test scenario must be run against
# (test-case-checklist.md, Submission Requirements). Four slots permit either
# of two counties; the tuple records the actual choice available.
TEST_COUNTY_MATRIX: tuple[tuple[str, ...], ...] = (
    ("Alachua",),
    ("Brevard",),
    ("Duval", "Collier"),
    ("Marion", "Walton"),
    ("Miami-Dade",),
    ("Orange",),
    ("Polk",),
    ("Sarasota", "St. Lucie"),
)


def certification_submission_count(scenarios: int, divisions: int) -> int:
    """Test submissions required for certification, excluding reruns.

    Eight county CMS targets per scenario per division. Reruns are excluded
    because the checklist requires re-running a scenario against *all* eight
    counties if any single county fails, which is unbounded in advance.
    """
    if scenarios < 0 or divisions < 0:
        raise ValueError("scenarios and divisions must be non-negative")
    return scenarios * divisions * len(TEST_COUNTY_MATRIX)


def new_existing_case_submission(ucn: str, documents: list[Document]) -> Submission:
    """Build an Existing Case submission from a UCN string. TS001–TS006 shape."""
    submission = Submission(
        ucn=parse_ucn(ucn),
        filing_path=FilingPath.EXISTING_CASE,
        documents=documents,
    )
    submission.validate_documents()
    return submission
