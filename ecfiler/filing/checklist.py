"""Filing checklists — tailored per filing type.

Before the attorney confirms, we show a checklist of common requirements
for their specific filing type. This catches mistakes that preflight
checks can't detect (things only the attorney would know).

Example: "Motion to Dismiss" checklist:
  [ ] Brief/memorandum of law attached?
  [ ] Proposed order attached?
  [ ] Certificate of service included?
  [ ] Meet and confer statement (if required by local rule)?
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ChecklistItem:
    text: str
    required: bool = False  # True = must check, False = advisory


@dataclass
class FilingChecklist:
    title: str
    items: list[ChecklistItem] = field(default_factory=list)


# Checklists keyed by event description keywords
_CHECKLISTS: dict[str, list[ChecklistItem]] = {
    "motion": [
        ChecklistItem("Memorandum/brief in support attached or filed separately?", required=True),
        ChecklistItem("Proposed order attached?"),
        ChecklistItem("Certificate of service included or separate?"),
        ChecklistItem("Meet and confer statement (if required by local rule)?"),
        ChecklistItem("Declaration/affidavit in support attached?"),
        ChecklistItem("Filing fee paid or waiver attached?"),
    ],
    "motion to dismiss": [
        ChecklistItem("Memorandum of law in support attached?", required=True),
        ChecklistItem("Rule 12(b) basis specified in motion?", required=True),
        ChecklistItem("Proposed order attached?"),
        ChecklistItem("Certificate of service?"),
    ],
    "motion for summary judgment": [
        ChecklistItem("Memorandum of law in support attached?", required=True),
        ChecklistItem("Statement of undisputed material facts?", required=True),
        ChecklistItem("Supporting declarations/affidavits attached?"),
        ChecklistItem("Exhibits properly labeled and attached?"),
        ChecklistItem("Proposed order attached?"),
    ],
    "complaint": [
        ChecklistItem("Civil cover sheet (JS-44) attached?", required=True),
        ChecklistItem("Summons prepared for issuance?", required=True),
        ChecklistItem("Filing fee paid or IFP application attached?", required=True),
        ChecklistItem("All parties properly named?", required=True),
        ChecklistItem("Jurisdiction and venue alleged?", required=True),
        ChecklistItem("Corporate disclosure statement (if applicable)?"),
    ],
    "answer": [
        ChecklistItem("All claims in complaint addressed?", required=True),
        ChecklistItem("Affirmative defenses included?"),
        ChecklistItem("Counterclaims included (if any)?"),
        ChecklistItem("Jury demand included (if desired)?"),
        ChecklistItem("Certificate of service?"),
    ],
    "response": [
        ChecklistItem("Filed within deadline?", required=True),
        ChecklistItem("Related to correct docket entry?", required=True),
        ChecklistItem("Memorandum of law in opposition attached?"),
        ChecklistItem("Counter-statement of facts (if applicable)?"),
        ChecklistItem("Supporting declarations attached?"),
        ChecklistItem("Certificate of service?"),
    ],
    "reply": [
        ChecklistItem("Filed within reply deadline?", required=True),
        ChecklistItem("Addresses only arguments raised in opposition?"),
        ChecklistItem("Within page/word limits?"),
        ChecklistItem("Certificate of service?"),
    ],
    "notice of appearance": [
        ChecklistItem("Attorney bar number included?", required=True),
        ChecklistItem("Contact information complete?", required=True),
    ],
    "stipulation": [
        ChecklistItem("Signed by all parties/counsel?", required=True),
        ChecklistItem("Proposed order attached?"),
    ],
    "brief": [
        ChecklistItem("Within page/word count limits?", required=True),
        ChecklistItem("Table of contents included?"),
        ChecklistItem("Table of authorities included?"),
        ChecklistItem("Certificate of compliance (word count)?"),
        ChecklistItem("Certificate of service?"),
    ],
    "petition": [
        ChecklistItem("All required schedules attached?", required=True),
        ChecklistItem("Statement of financial affairs?", required=True),
        ChecklistItem("Creditor matrix attached?", required=True),
        ChecklistItem("Filing fee paid or installment application?", required=True),
        ChecklistItem("Credit counseling certificate attached?", required=True),
    ],
    "appeal": [
        ChecklistItem("Notice of appeal filed within deadline?", required=True),
        ChecklistItem("Filing fee paid?", required=True),
        ChecklistItem("Designation of record on appeal?"),
        ChecklistItem("Statement of issues?"),
    ],
}


def get_checklist(event_description: str) -> FilingChecklist | None:
    """Get the appropriate checklist for a filing type.

    Matches against the event description using keyword matching.
    Returns the most specific match, or a generic motion checklist.
    """
    desc_lower = event_description.lower()

    # Try specific matches first (longer keys = more specific)
    for key in sorted(_CHECKLISTS.keys(), key=len, reverse=True):
        if key in desc_lower:
            return FilingChecklist(
                title=f"Checklist: {event_description}",
                items=_CHECKLISTS[key],
            )

    return None


def get_all_checklist_types() -> list[str]:
    """List all available checklist types."""
    return sorted(_CHECKLISTS.keys())
