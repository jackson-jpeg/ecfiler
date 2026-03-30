"""Event code lookup and management.

Event codes are the CM/ECF identifiers for types of filings
(e.g., "Motion to Dismiss", "Reply Brief", "Notice of Appearance").

Data is loaded from JSON files in courts/data/event_codes/.
Hardcoded fallbacks kept for cases where JSON loading fails.
"""

from __future__ import annotations

import json
from pathlib import Path

from ecfiler.filing.models import EventCode

_EVENT_CODES_DIR = Path(__file__).parent.parent / "courts" / "data" / "event_codes"
_CACHE: dict[str, list[dict[str, str]]] = {}


def _load_from_json(court_type: str) -> list[dict[str, str]]:
    """Load event codes from JSON file, flattening categories."""
    if court_type in _CACHE:
        return _CACHE[court_type]

    filename_map = {
        "district": "common_district.json",
        "bankruptcy": "common_bankruptcy.json",
        "appellate": "common_appellate.json",
    }
    filename = filename_map.get(court_type, "common_district.json")
    path = _EVENT_CODES_DIR / filename

    if path.exists():
        try:
            with open(path) as f:
                data = json.load(f)
            events = []
            for category, codes in data.get("categories", {}).items():
                for code in codes:
                    events.append({
                        "code": code["code"],
                        "description": code["description"],
                        "category": category,
                    })
            _CACHE[court_type] = events
            return events
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to load event codes from %s", path)

    # Fallback to hardcoded
    if court_type == "bankruptcy":
        return COMMON_BANKRUPTCY_EVENTS
    elif court_type == "appellate":
        return COMMON_APPELLATE_EVENTS
    return COMMON_DISTRICT_EVENTS


# Hardcoded fallbacks — representative subsets used when JSON loading fails.
# These cover the most commonly filed document types across federal courts.
COMMON_DISTRICT_EVENTS: list[dict[str, str]] = [
    # Motions (most frequently filed)
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
    {"code": "26", "description": "Motion for Protective Order", "category": "Motions"},
    {"code": "27", "description": "Motion to Strike", "category": "Motions"},
    {"code": "28", "description": "Motion to Intervene", "category": "Motions"},
    {"code": "29", "description": "Motion for Sanctions", "category": "Motions"},
    {"code": "30", "description": "Motion for Attorney Fees", "category": "Motions"},
    {"code": "31", "description": "Motion for Class Certification", "category": "Motions"},
    {"code": "32", "description": "Motion to Amend/Correct", "category": "Motions"},
    {"code": "33", "description": "Motion for Judgment on the Pleadings", "category": "Motions"},
    {"code": "34", "description": "Motion to Transfer Venue", "category": "Motions"},
    {"code": "35", "description": "Motion to Continue/Postpone", "category": "Motions"},
    {"code": "36", "description": "Motion to Quash", "category": "Motions"},
    {"code": "37", "description": "Motion to Appear Pro Hac Vice", "category": "Motions"},
    {"code": "38", "description": "Motion for Contempt", "category": "Motions"},
    {"code": "39", "description": "Motion to Vacate", "category": "Motions"},
    {"code": "40", "description": "Motion to Reopen Case", "category": "Motions"},
    {"code": "41", "description": "Motion to Substitute Party", "category": "Motions"},
    {"code": "42", "description": "Motion for Permanent Injunction", "category": "Motions"},
    {"code": "43", "description": "Emergency Motion", "category": "Motions"},
    {"code": "44", "description": "Motion for Judgment as a Matter of Law", "category": "Motions"},
    {"code": "45", "description": "Motion for New Trial", "category": "Motions"},
    {"code": "46", "description": "Consent Motion", "category": "Motions"},
    # Briefs & Memoranda
    {"code": "100", "description": "Memorandum of Law in Support", "category": "Briefs"},
    {"code": "101", "description": "Memorandum of Law in Opposition", "category": "Briefs"},
    {"code": "102", "description": "Reply Memorandum of Law", "category": "Briefs"},
    {"code": "103", "description": "Brief in Support", "category": "Briefs"},
    {"code": "104", "description": "Brief in Opposition", "category": "Briefs"},
    {"code": "105", "description": "Reply Brief", "category": "Briefs"},
    {"code": "106", "description": "Amicus Brief", "category": "Briefs"},
    {"code": "107", "description": "Sur-Reply", "category": "Briefs"},
    {"code": "108", "description": "Post-Trial Brief", "category": "Briefs"},
    {"code": "109", "description": "Trial Brief", "category": "Briefs"},
    {"code": "110", "description": "Pretrial Memorandum", "category": "Briefs"},
    # Notices
    {"code": "200", "description": "Notice of Appearance", "category": "Notices"},
    {"code": "201", "description": "Notice of Motion", "category": "Notices"},
    {"code": "202", "description": "Notice of Appeal", "category": "Notices"},
    {"code": "203", "description": "Notice of Removal", "category": "Notices"},
    {"code": "204", "description": "Notice of Settlement", "category": "Notices"},
    {"code": "205", "description": "Notice of Voluntary Dismissal", "category": "Notices"},
    {"code": "206", "description": "Notice of Supplemental Authority", "category": "Notices"},
    {"code": "207", "description": "Notice of Change of Address", "category": "Notices"},
    {"code": "208", "description": "Notice of Substitution of Counsel", "category": "Notices"},
    {"code": "209", "description": "Notice of Deposition", "category": "Notices"},
    {"code": "210", "description": "Notice of Lis Pendens", "category": "Notices"},
    {"code": "211", "description": "Notice of Intent to Request Redaction", "category": "Notices"},
    # Responses and Answers
    {"code": "300", "description": "Answer", "category": "Responses"},
    {"code": "301", "description": "Response/Opposition to Motion", "category": "Responses"},
    {"code": "302", "description": "Reply to Response", "category": "Responses"},
    {"code": "303", "description": "Objection", "category": "Responses"},
    {"code": "304", "description": "Answer to Amended Complaint", "category": "Responses"},
    {"code": "305", "description": "Answer to Counterclaim", "category": "Responses"},
    {"code": "306", "description": "Answer to Crossclaim", "category": "Responses"},
    {"code": "307", "description": "Answer to Third-Party Complaint", "category": "Responses"},
    # Initiating Documents
    {"code": "400", "description": "Complaint", "category": "Initiating Documents"},
    {"code": "401", "description": "Amended Complaint", "category": "Initiating Documents"},
    {"code": "402", "description": "Petition", "category": "Initiating Documents"},
    {"code": "403", "description": "Counterclaim", "category": "Initiating Documents"},
    {"code": "404", "description": "Cross-Claim", "category": "Initiating Documents"},
    {"code": "405", "description": "Third-Party Complaint", "category": "Initiating Documents"},
    {"code": "406", "description": "Notice of Removal", "category": "Initiating Documents"},
    {"code": "407", "description": "Intervenor Complaint", "category": "Initiating Documents"},
    {"code": "408", "description": "Petition for Writ of Habeas Corpus", "category": "Initiating Documents"},
    {"code": "409", "description": "Registration of Foreign Judgment", "category": "Initiating Documents"},
    # Discovery
    {"code": "500", "description": "Rule 26 Initial Disclosures", "category": "Discovery"},
    {"code": "501", "description": "Interrogatories", "category": "Discovery"},
    {"code": "502", "description": "Request for Production of Documents", "category": "Discovery"},
    {"code": "503", "description": "Request for Admissions", "category": "Discovery"},
    {"code": "504", "description": "Deposition", "category": "Discovery"},
    {"code": "505", "description": "Subpoena", "category": "Discovery"},
    {"code": "506", "description": "Notice to Take Deposition", "category": "Discovery"},
    {"code": "507", "description": "Rule 26(f) Discovery Plan Report", "category": "Discovery"},
    # Stipulations
    {"code": "600", "description": "Stipulation", "category": "Stipulations"},
    {"code": "601", "description": "Stipulation of Dismissal", "category": "Stipulations"},
    {"code": "602", "description": "Stipulation to Extend Time", "category": "Stipulations"},
    {"code": "603", "description": "Stipulation of Facts", "category": "Stipulations"},
    # Supporting Documents
    {"code": "700", "description": "Proposed Order", "category": "Supporting Documents"},
    {"code": "701", "description": "Affidavit/Declaration", "category": "Supporting Documents"},
    {"code": "702", "description": "Certificate of Service", "category": "Supporting Documents"},
    {"code": "703", "description": "Exhibit", "category": "Supporting Documents"},
    {"code": "704", "description": "Corporate Disclosure Statement", "category": "Supporting Documents"},
    {"code": "705", "description": "Civil Cover Sheet (JS-44)", "category": "Supporting Documents"},
    {"code": "706", "description": "Sealed Document", "category": "Supporting Documents"},
    {"code": "707", "description": "Errata", "category": "Supporting Documents"},
    {"code": "708", "description": "Redacted Document", "category": "Supporting Documents"},
    # Reports and Filings
    {"code": "800", "description": "Status Report", "category": "Reports"},
    {"code": "801", "description": "Letter/Correspondence", "category": "Reports"},
    {"code": "802", "description": "Settlement Agreement", "category": "Reports"},
    {"code": "803", "description": "Bill of Costs", "category": "Reports"},
    {"code": "804", "description": "Satisfaction of Judgment", "category": "Reports"},
    {"code": "805", "description": "Suggestion of Bankruptcy", "category": "Reports"},
    {"code": "806", "description": "Suggestion of Death", "category": "Reports"},
    # Service of Process
    {"code": "900", "description": "Summons Returned Executed", "category": "Service of Process"},
    {"code": "901", "description": "Summons Returned Unexecuted", "category": "Service of Process"},
    {"code": "902", "description": "Waiver of Service Executed", "category": "Service of Process"},
    {"code": "903", "description": "Affidavit of Service", "category": "Service of Process"},
    # Trial Documents
    {"code": "1000", "description": "Witness List", "category": "Trial Documents"},
    {"code": "1001", "description": "Exhibit List", "category": "Trial Documents"},
    {"code": "1002", "description": "Proposed Jury Instructions", "category": "Trial Documents"},
    {"code": "1003", "description": "Proposed Findings of Fact", "category": "Trial Documents"},
    {"code": "1004", "description": "Pretrial Statement", "category": "Trial Documents"},
]

COMMON_BANKRUPTCY_EVENTS: list[dict[str, str]] = [
    # Petitions
    {"code": "BK7", "description": "Chapter 7 Voluntary Petition", "category": "Petitions"},
    {"code": "BK11", "description": "Chapter 11 Voluntary Petition", "category": "Petitions"},
    {"code": "BK12", "description": "Chapter 12 Voluntary Petition", "category": "Petitions"},
    {"code": "BK13", "description": "Chapter 13 Voluntary Petition", "category": "Petitions"},
    {"code": "BKV", "description": "Involuntary Petition", "category": "Petitions"},
    {"code": "BKI", "description": "Involuntary Petition Against", "category": "Petitions"},
    {"code": "BKCONV", "description": "Conversion of Case", "category": "Petitions"},
    {"code": "BK15", "description": "Chapter 15 Petition", "category": "Petitions"},
    {"code": "BKAMD", "description": "Amended Petition", "category": "Petitions"},
    # Motions
    {"code": "BM1", "description": "Motion for Relief from Stay", "category": "Motions"},
    {"code": "BM2", "description": "Motion to Dismiss Case", "category": "Motions"},
    {"code": "BM3", "description": "Motion to Convert Case", "category": "Motions"},
    {"code": "BM4", "description": "Motion for Hardship Discharge", "category": "Motions"},
    {"code": "BM5", "description": "Motion to Avoid Lien", "category": "Motions"},
    {"code": "BM6", "description": "Motion to Value Collateral", "category": "Motions"},
    {"code": "BM7", "description": "Motion to Approve Sale of Property", "category": "Motions"},
    {"code": "BM8", "description": "Motion for Summary Judgment", "category": "Motions"},
    {"code": "BM9", "description": "Motion to Extend Time", "category": "Motions"},
    {"code": "BM10", "description": "Motion to Approve Compromise", "category": "Motions"},
    {"code": "BM11", "description": "Motion for Adequate Protection", "category": "Motions"},
    {"code": "BM12", "description": "Motion to Employ Professional", "category": "Motions"},
    {"code": "BM13", "description": "Application for Compensation", "category": "Motions"},
    {"code": "BM14", "description": "Motion to Use Cash Collateral", "category": "Motions"},
    {"code": "BM15", "description": "Motion to Assume/Reject Lease or Executory Contract", "category": "Motions"},
    {"code": "BM16", "description": "Motion to Reopen Case", "category": "Motions"},
    {"code": "BM17", "description": "Motion for Contempt", "category": "Motions"},
    {"code": "BM18", "description": "Motion for Protective Order", "category": "Motions"},
    {"code": "BM19", "description": "Motion for Sanctions", "category": "Motions"},
    {"code": "BM20", "description": "Motion to Modify Plan", "category": "Motions"},
    {"code": "BM21", "description": "Motion to Obtain Credit", "category": "Motions"},
    {"code": "BM22", "description": "Motion to Incur Debt", "category": "Motions"},
    {"code": "BM23", "description": "Motion to Seal", "category": "Motions"},
    {"code": "BM24", "description": "Motion for Joint Administration", "category": "Motions"},
    {"code": "BM25", "description": "Motion to Appoint Trustee", "category": "Motions"},
    {"code": "BM26", "description": "Motion to Appoint Examiner", "category": "Motions"},
    {"code": "BM27", "description": "Motion for Default Judgment", "category": "Motions"},
    {"code": "BM28", "description": "Motion to Reconsider", "category": "Motions"},
    {"code": "BM29", "description": "Motion to Substitute Attorney", "category": "Motions"},
    {"code": "BM30", "description": "Motion for Turnover of Property", "category": "Motions"},
    {"code": "BM31", "description": "Motion for Sale Free and Clear", "category": "Motions"},
    {"code": "BM32", "description": "Motion to Extend Automatic Stay", "category": "Motions"},
    # Schedules and Statements
    {"code": "BS1", "description": "Schedule A/B - Property", "category": "Schedules"},
    {"code": "BS2", "description": "Schedule C - Exempt Property", "category": "Schedules"},
    {"code": "BS3", "description": "Schedule D - Secured Claims", "category": "Schedules"},
    {"code": "BS4", "description": "Schedule E/F - Unsecured Claims", "category": "Schedules"},
    {"code": "BS5", "description": "Schedule G - Executory Contracts and Leases", "category": "Schedules"},
    {"code": "BS6", "description": "Schedule H - Codebtors", "category": "Schedules"},
    {"code": "BS7", "description": "Schedule I - Income", "category": "Schedules"},
    {"code": "BS8", "description": "Schedule J - Expenses", "category": "Schedules"},
    {"code": "BS9", "description": "Summary of Schedules", "category": "Schedules"},
    {"code": "BS10", "description": "Statement of Financial Affairs", "category": "Schedules"},
    {"code": "BS11", "description": "Means Test / Chapter 7 Statement", "category": "Schedules"},
    {"code": "BS12", "description": "Amended Schedules", "category": "Schedules"},
    {"code": "BS13", "description": "Creditor Matrix/Mailing List", "category": "Schedules"},
    # Claims
    {"code": "BC1", "description": "Proof of Claim", "category": "Claims"},
    {"code": "BC2", "description": "Amended Proof of Claim", "category": "Claims"},
    {"code": "BC3", "description": "Objection to Claim", "category": "Claims"},
    {"code": "BC4", "description": "Withdrawal of Claim", "category": "Claims"},
    {"code": "BC5", "description": "Transfer of Claim", "category": "Claims"},
    {"code": "BC6", "description": "Administrative Expense Claim", "category": "Claims"},
    {"code": "BC7", "description": "Objection to Exemptions", "category": "Claims"},
    # Plans and Disclosure
    {"code": "BP1", "description": "Chapter 11 Plan of Reorganization", "category": "Plans"},
    {"code": "BP2", "description": "Chapter 13 Plan", "category": "Plans"},
    {"code": "BP3", "description": "Disclosure Statement", "category": "Plans"},
    {"code": "BP4", "description": "Amended Plan", "category": "Plans"},
    {"code": "BP5", "description": "Modified Plan", "category": "Plans"},
    {"code": "BP6", "description": "Plan Supplement", "category": "Plans"},
    {"code": "BP7", "description": "Objection to Confirmation", "category": "Plans"},
    {"code": "BP8", "description": "Ballot/Vote on Plan", "category": "Plans"},
    # Adversary Proceedings
    {"code": "BA1", "description": "Adversary Proceeding Complaint", "category": "Adversary Proceedings"},
    {"code": "BA2", "description": "Answer to Adversary Complaint", "category": "Adversary Proceedings"},
    {"code": "BA3", "description": "Counterclaim in Adversary", "category": "Adversary Proceedings"},
    {"code": "BA4", "description": "Crossclaim in Adversary", "category": "Adversary Proceedings"},
    # Notices
    {"code": "BN1", "description": "Notice of Appearance", "category": "Notices"},
    {"code": "BN2", "description": "Notice of Hearing", "category": "Notices"},
    {"code": "BN3", "description": "Notice of Motion", "category": "Notices"},
    {"code": "BN4", "description": "Notice of Appeal", "category": "Notices"},
    {"code": "BN5", "description": "Notice of Change of Address", "category": "Notices"},
    {"code": "BN6", "description": "Notice of Voluntary Conversion", "category": "Notices"},
    {"code": "BN7", "description": "Notice of Voluntary Dismissal", "category": "Notices"},
    # Supporting Documents
    {"code": "BD1", "description": "Affidavit/Declaration", "category": "Supporting Documents"},
    {"code": "BD2", "description": "Certificate of Service", "category": "Supporting Documents"},
    {"code": "BD3", "description": "Proposed Order", "category": "Supporting Documents"},
    {"code": "BD4", "description": "Exhibit", "category": "Supporting Documents"},
    {"code": "BD5", "description": "Memorandum of Law", "category": "Supporting Documents"},
    {"code": "BD6", "description": "Response/Opposition to Motion", "category": "Supporting Documents"},
    {"code": "BD7", "description": "Reply to Response", "category": "Supporting Documents"},
    {"code": "BD8", "description": "Stipulation", "category": "Supporting Documents"},
    # Other
    {"code": "BO1", "description": "Reaffirmation Agreement", "category": "Other"},
    {"code": "BO2", "description": "Monthly Operating Report", "category": "Other"},
    {"code": "BO3", "description": "Status Report", "category": "Other"},
    {"code": "BO4", "description": "Fee Application", "category": "Other"},
]

COMMON_APPELLATE_EVENTS: list[dict[str, str]] = [
    # Briefs
    {"code": "AB1", "description": "Opening Brief", "category": "Briefs"},
    {"code": "AB2", "description": "Answering Brief", "category": "Briefs"},
    {"code": "AB3", "description": "Reply Brief", "category": "Briefs"},
    {"code": "AB4", "description": "Amicus Curiae Brief", "category": "Briefs"},
    {"code": "AB5", "description": "Supplemental Brief", "category": "Briefs"},
    {"code": "AB6", "description": "Cross-Appellant Opening Brief", "category": "Briefs"},
    {"code": "AB7", "description": "Cross-Appellee Answering Brief", "category": "Briefs"},
    {"code": "AB8", "description": "Intervenor Brief", "category": "Briefs"},
    {"code": "AB9", "description": "Corrected Brief", "category": "Briefs"},
    {"code": "AB10", "description": "Anders Brief", "category": "Briefs"},
    {"code": "AB11", "description": "FRAP 28(j) Letter (Supplemental Authority)", "category": "Briefs"},
    # Motions
    {"code": "AM1", "description": "Motion for Extension of Time", "category": "Motions"},
    {"code": "AM2", "description": "Motion to Dismiss Appeal", "category": "Motions"},
    {"code": "AM3", "description": "Motion for Stay Pending Appeal", "category": "Motions"},
    {"code": "AM4", "description": "Motion for Oral Argument", "category": "Motions"},
    {"code": "AM5", "description": "Motion for Appointment of Counsel", "category": "Motions"},
    {"code": "AM6", "description": "Motion for Leave to File", "category": "Motions"},
    {"code": "AM7", "description": "Motion to Consolidate Appeals", "category": "Motions"},
    {"code": "AM8", "description": "Motion for Expedited Briefing", "category": "Motions"},
    {"code": "AM9", "description": "Motion for Summary Disposition", "category": "Motions"},
    {"code": "AM10", "description": "Emergency Motion", "category": "Motions"},
    {"code": "AM11", "description": "Motion to Seal", "category": "Motions"},
    {"code": "AM12", "description": "Motion for Leave to Proceed In Forma Pauperis", "category": "Motions"},
    {"code": "AM13", "description": "Motion to Withdraw as Counsel", "category": "Motions"},
    {"code": "AM14", "description": "Motion for Attorney Fees", "category": "Motions"},
    {"code": "AM15", "description": "Motion for Clarification", "category": "Motions"},
    {"code": "AM16", "description": "Motion to Stay Mandate", "category": "Motions"},
    {"code": "AM17", "description": "Motion to Recall Mandate", "category": "Motions"},
    {"code": "AM18", "description": "Motion for Sanctions", "category": "Motions"},
    {"code": "AM19", "description": "Motion to Strike", "category": "Motions"},
    {"code": "AM20", "description": "Motion to Substitute Party", "category": "Motions"},
    {"code": "AM21", "description": "Motion to Correct/Supplement Record", "category": "Motions"},
    {"code": "AM22", "description": "Motion for Limited Remand", "category": "Motions"},
    {"code": "AM23", "description": "Motion to Reconsider", "category": "Motions"},
    {"code": "AM24", "description": "Motion to Vacate", "category": "Motions"},
    {"code": "AM25", "description": "Motion for Temporary Injunction Pending Appeal", "category": "Motions"},
    {"code": "AM26", "description": "Motion to Reopen Case", "category": "Motions"},
    {"code": "AM27", "description": "Motion to Waive Oral Argument", "category": "Motions"},
    {"code": "AM28", "description": "Motion to Deconsolidate Appeals", "category": "Motions"},
    # Notices and Filings
    {"code": "AN1", "description": "Notice of Appeal", "category": "Notices"},
    {"code": "AN2", "description": "Amended Notice of Appeal", "category": "Notices"},
    {"code": "AN3", "description": "Notice of Cross-Appeal", "category": "Notices"},
    {"code": "AN4", "description": "Notice of Supplemental Authority", "category": "Notices"},
    {"code": "AN5", "description": "Entry of Appearance", "category": "Notices"},
    {"code": "AN6", "description": "Notice of Related Case", "category": "Notices"},
    {"code": "AN7", "description": "Notice of Change of Address", "category": "Notices"},
    {"code": "AN8", "description": "Certificate of Service", "category": "Notices"},
    {"code": "AN9", "description": "FRAP 26.1 Corporate Disclosure Statement", "category": "Notices"},
    {"code": "AN10", "description": "Certificate of Compliance", "category": "Notices"},
    {"code": "AN11", "description": "Designation/Cross Designation of Record", "category": "Notices"},
    {"code": "AN12", "description": "Status Report", "category": "Notices"},
    {"code": "AN13", "description": "Civil Appeals Docketing Statement", "category": "Notices"},
    # Appendices and Records
    {"code": "AA1", "description": "Joint Appendix", "category": "Appendices"},
    {"code": "AA2", "description": "Supplemental Appendix", "category": "Appendices"},
    {"code": "AA3", "description": "Deferred Appendix", "category": "Appendices"},
    {"code": "AA4", "description": "Corrected Appendix", "category": "Appendices"},
    {"code": "AA5", "description": "Sealed/Confidential Appendix", "category": "Appendices"},
    {"code": "AA6", "description": "Bill of Costs", "category": "Appendices"},
    # Responses
    {"code": "AR1", "description": "Response to Motion", "category": "Responses"},
    {"code": "AR2", "description": "Reply to Response", "category": "Responses"},
    {"code": "AR3", "description": "Petition for Rehearing", "category": "Responses"},
    {"code": "AR4", "description": "Petition for Rehearing En Banc", "category": "Responses"},
    {"code": "AR5", "description": "Opposition to Motion", "category": "Responses"},
    {"code": "AR6", "description": "Response to Court Order", "category": "Responses"},
    {"code": "AR7", "description": "Response to Show Cause", "category": "Responses"},
    # Stipulations
    {"code": "AS1", "description": "Stipulation for Voluntary Dismissal", "category": "Stipulations"},
    {"code": "AS2", "description": "Non-Dispositive Stipulation", "category": "Stipulations"},
]


def get_common_events(court_type: str) -> list[EventCode]:
    """Get common event codes for a court type.

    Loads from JSON files first, falls back to hardcoded data.
    """
    raw = _load_from_json(court_type)

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
