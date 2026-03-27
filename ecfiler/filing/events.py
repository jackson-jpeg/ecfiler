"""Event code lookup and management.

Event codes are the CM/ECF identifiers for types of filings
(e.g., "Motion to Dismiss", "Reply Brief", "Notice of Appearance").
"""

from __future__ import annotations

from ecfiler.filing.models import EventCode

# Common event codes shared across most district courts.
# Individual courts may have additional or differently-named codes.
COMMON_DISTRICT_EVENTS: list[dict[str, str]] = [
    # Motions
    {"code": "12", "description": "Motion to Dismiss", "category": "Motions"},
    {"code": "13", "description": "Motion for Summary Judgment", "category": "Motions"},
    {"code": "14", "description": "Motion to Compel", "category": "Motions"},
    {"code": "15", "description": "Motion in Limine", "category": "Motions"},
    {"code": "16", "description": "Motion for Extension of Time", "category": "Motions"},
    {"code": "17", "description": "Motion to Seal", "category": "Motions"},
    {"code": "18", "description": "Motion for Leave to File", "category": "Motions"},
    {"code": "19", "description": "Motion for Reconsideration", "category": "Motions"},
    {"code": "20", "description": "Motion for Default Judgment", "category": "Motions"},
    {"code": "21", "description": "Motion to Remand", "category": "Motions"},
    {"code": "22", "description": "Motion to Stay", "category": "Motions"},
    {"code": "23", "description": "Motion for Preliminary Injunction", "category": "Motions"},
    {"code": "24", "description": "Motion for Temporary Restraining Order", "category": "Motions"},
    {"code": "25", "description": "Motion to Withdraw", "category": "Motions"},
    # Briefs & Memoranda
    {"code": "100", "description": "Memorandum of Law in Support", "category": "Briefs"},
    {"code": "101", "description": "Memorandum of Law in Opposition", "category": "Briefs"},
    {"code": "102", "description": "Reply Memorandum of Law", "category": "Briefs"},
    {"code": "103", "description": "Brief in Support", "category": "Briefs"},
    {"code": "104", "description": "Brief in Opposition", "category": "Briefs"},
    {"code": "105", "description": "Reply Brief", "category": "Briefs"},
    {"code": "106", "description": "Amicus Brief", "category": "Briefs"},
    {"code": "107", "description": "Sur-Reply", "category": "Briefs"},
    # Notices
    {"code": "200", "description": "Notice of Appearance", "category": "Notices"},
    {"code": "201", "description": "Notice of Motion", "category": "Notices"},
    {"code": "202", "description": "Notice of Appeal", "category": "Notices"},
    {"code": "203", "description": "Notice of Removal", "category": "Notices"},
    {"code": "204", "description": "Notice of Settlement", "category": "Notices"},
    {"code": "205", "description": "Notice of Voluntary Dismissal", "category": "Notices"},
    # Responses
    {"code": "300", "description": "Answer", "category": "Responses"},
    {"code": "301", "description": "Response/Opposition to Motion", "category": "Responses"},
    {"code": "302", "description": "Reply to Response", "category": "Responses"},
    {"code": "303", "description": "Objection", "category": "Responses"},
    # Initiating Documents
    {"code": "400", "description": "Complaint", "category": "Initiating"},
    {"code": "401", "description": "Amended Complaint", "category": "Initiating"},
    {"code": "402", "description": "Petition", "category": "Initiating"},
    {"code": "403", "description": "Counterclaim", "category": "Initiating"},
    {"code": "404", "description": "Cross-Claim", "category": "Initiating"},
    {"code": "405", "description": "Third-Party Complaint", "category": "Initiating"},
    # Other
    {"code": "500", "description": "Stipulation", "category": "Other"},
    {"code": "501", "description": "Proposed Order", "category": "Other"},
    {"code": "502", "description": "Affidavit/Declaration", "category": "Other"},
    {"code": "503", "description": "Certificate of Service", "category": "Other"},
    {"code": "504", "description": "Consent Motion", "category": "Other"},
    {"code": "505", "description": "Status Report", "category": "Other"},
    {"code": "506", "description": "Discovery Material", "category": "Other"},
    {"code": "507", "description": "Exhibit", "category": "Other"},
    {"code": "508", "description": "Letter/Correspondence", "category": "Other"},
]

COMMON_BANKRUPTCY_EVENTS: list[dict[str, str]] = [
    {"code": "B1", "description": "Voluntary Petition", "category": "Petitions"},
    {"code": "B2", "description": "Involuntary Petition", "category": "Petitions"},
    {"code": "B3", "description": "Schedules", "category": "Schedules"},
    {"code": "B4", "description": "Statement of Financial Affairs", "category": "Schedules"},
    {"code": "B5", "description": "Means Test", "category": "Schedules"},
    {"code": "B6", "description": "Creditor Matrix", "category": "Creditors"},
    {"code": "B7", "description": "Proof of Claim", "category": "Claims"},
    {"code": "B8", "description": "Motion for Relief from Stay", "category": "Motions"},
    {"code": "B9", "description": "Plan of Reorganization", "category": "Plans"},
    {"code": "B10", "description": "Disclosure Statement", "category": "Plans"},
    {"code": "B11", "description": "Objection to Claim", "category": "Claims"},
    {"code": "B12", "description": "Motion to Dismiss", "category": "Motions"},
    {"code": "B13", "description": "Motion to Convert", "category": "Motions"},
    {"code": "B14", "description": "Reaffirmation Agreement", "category": "Other"},
    {"code": "B15", "description": "Motion for Hardship Discharge", "category": "Motions"},
    # Additional bankruptcy events
    {"code": "B16", "description": "Amended Schedules", "category": "Schedules"},
    {"code": "B17", "description": "Motion to Avoid Lien", "category": "Motions"},
    {"code": "B18", "description": "Motion to Value Collateral", "category": "Motions"},
    {"code": "B19", "description": "Motion to Approve Sale", "category": "Motions"},
    {"code": "B20", "description": "Adversary Proceeding Complaint", "category": "Adversary"},
    {"code": "B21", "description": "Answer to Adversary Complaint", "category": "Adversary"},
    {"code": "B22", "description": "Motion for Summary Judgment", "category": "Motions"},
    {"code": "B23", "description": "Notice of Appearance", "category": "Notices"},
    {"code": "B24", "description": "Notice of Hearing", "category": "Notices"},
    {"code": "B25", "description": "Motion to Extend Time", "category": "Motions"},
    {"code": "B26", "description": "Motion to Approve Compromise", "category": "Motions"},
    {"code": "B27", "description": "Monthly Operating Report", "category": "Reports"},
    {"code": "B28", "description": "Ballot/Vote on Plan", "category": "Plans"},
    {"code": "B29", "description": "Objection to Confirmation", "category": "Plans"},
    {"code": "B30", "description": "Motion for Adequate Protection", "category": "Motions"},
    {"code": "B31", "description": "Motion to Employ Professional", "category": "Motions"},
    {"code": "B32", "description": "Application for Compensation", "category": "Motions"},
    {"code": "B33", "description": "Certificate of Service", "category": "Other"},
    {"code": "B34", "description": "Stipulation", "category": "Other"},
    {"code": "B35", "description": "Declaration/Affidavit", "category": "Other"},
]

COMMON_APPELLATE_EVENTS: list[dict[str, str]] = [
    {"code": "A1", "description": "Opening Brief", "category": "Briefs"},
    {"code": "A2", "description": "Answering Brief", "category": "Briefs"},
    {"code": "A3", "description": "Reply Brief", "category": "Briefs"},
    {"code": "A4", "description": "Petition for Review", "category": "Petitions"},
    {"code": "A5", "description": "Petition for Rehearing", "category": "Petitions"},
    {"code": "A6", "description": "Petition for Rehearing En Banc", "category": "Petitions"},
    {"code": "A7", "description": "Motion for Extension of Time", "category": "Motions"},
    {"code": "A8", "description": "Motion to Dismiss Appeal", "category": "Motions"},
    {"code": "A9", "description": "Motion for Stay Pending Appeal", "category": "Motions"},
    {"code": "A10", "description": "Joint Appendix", "category": "Appendices"},
    {"code": "A11", "description": "Supplemental Appendix", "category": "Appendices"},
    {"code": "A12", "description": "Amicus Curiae Brief", "category": "Briefs"},
    {"code": "A13", "description": "Certificate of Compliance", "category": "Other"},
    {"code": "A14", "description": "Corporate Disclosure Statement", "category": "Other"},
    {"code": "A15", "description": "Motion for Oral Argument", "category": "Motions"},
    # Additional appellate events
    {"code": "A16", "description": "Notice of Appeal", "category": "Notices"},
    {"code": "A17", "description": "Designation of Record", "category": "Other"},
    {"code": "A18", "description": "Statement of Issues", "category": "Other"},
    {"code": "A19", "description": "Motion for Appointment of Counsel", "category": "Motions"},
    {"code": "A20", "description": "Motion for Leave to File", "category": "Motions"},
    {"code": "A21", "description": "Motion to Consolidate", "category": "Motions"},
    {"code": "A22", "description": "Motion for Summary Disposition", "category": "Motions"},
    {"code": "A23", "description": "Emergency Motion", "category": "Motions"},
    {"code": "A24", "description": "Supplemental Brief", "category": "Briefs"},
    {"code": "A25", "description": "Response to Motion", "category": "Responses"},
    {"code": "A26", "description": "Reply to Response", "category": "Responses"},
    {"code": "A27", "description": "Certificate of Service", "category": "Other"},
    {"code": "A28", "description": "Notice of Supplemental Authority", "category": "Notices"},
    {"code": "A29", "description": "Motion to Seal", "category": "Motions"},
    {"code": "A30", "description": "Stipulation for Dismissal", "category": "Other"},
]


def get_common_events(court_type: str) -> list[EventCode]:
    """Get common event codes for a court type."""
    if court_type == "bankruptcy":
        raw = COMMON_BANKRUPTCY_EVENTS
    elif court_type == "appellate":
        raw = COMMON_APPELLATE_EVENTS
    else:
        raw = COMMON_DISTRICT_EVENTS

    return [
        EventCode(
            code=e["code"],
            description=e["description"],
            category=e.get("category", ""),
        )
        for e in raw
    ]


def search_events(query: str, court_type: str) -> list[EventCode]:
    """Search event codes by description.

    Uses bidirectional matching: finds events where either the query
    contains the event description or the description contains the query.
    Results sorted by relevance (exact > contains > partial word overlap).
    """
    query_lower = query.lower()
    query_words = set(query_lower.split())
    events = get_common_events(court_type)

    scored: list[tuple[float, EventCode]] = []
    for e in events:
        desc_lower = e.description.lower()
        desc_words = set(desc_lower.split())

        if query_lower == desc_lower:
            scored.append((1000, e))
        elif desc_lower in query_lower:
            # Event description is inside the query — score by length
            # Bonus if query starts with the event description (strongest signal)
            bonus = 50 if query_lower.startswith(desc_lower) else 0
            scored.append((100 + len(desc_lower) + bonus, e))
        elif query_lower in desc_lower:
            scored.append((90, e))
        else:
            # Word overlap — score by % of event words matched
            overlap = len(query_words & desc_words)
            if overlap >= 2:
                pct = overlap / len(desc_words) if desc_words else 0
                scored.append((overlap * 10 + pct * 5, e))

    scored.sort(key=lambda x: -x[0])
    return [e for _, e in scored]


def get_event_categories(court_type: str) -> list[str]:
    """Get unique event categories for a court type."""
    events = get_common_events(court_type)
    categories = sorted(set(e.category for e in events if e.category))
    return categories
