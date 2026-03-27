"""Civil Cover Sheet (JS-44) data for new case filings.

When opening a new civil case in federal district court, CM/ECF requires
the information from the JS-44 Civil Cover Sheet. This module provides
the nature of suit codes and other required data.

Reference: https://www.uscourts.gov/forms/civil-forms/civil-cover-sheet
"""

from __future__ import annotations

from dataclasses import dataclass

# Nature of Suit codes — these are the REAL codes used on the JS-44 form
# and in CM/ECF for case opening.
NATURE_OF_SUIT: dict[str, list[dict[str, str]]] = {
    "Contract": [
        {"code": "110", "description": "Insurance"},
        {"code": "120", "description": "Marine"},
        {"code": "130", "description": "Miller Act"},
        {"code": "140", "description": "Negotiable Instrument"},
        {"code": "150", "description": "Recovery of Overpayment"},
        {"code": "151", "description": "Medicare Act"},
        {"code": "152", "description": "Recovery of Student Loans"},
        {"code": "153", "description": "Recovery of Veteran's Benefits"},
        {"code": "160", "description": "Stockholders' Suits"},
        {"code": "190", "description": "Other Contract"},
        {"code": "195", "description": "Contract Product Liability"},
        {"code": "196", "description": "Franchise"},
    ],
    "Real Property": [
        {"code": "210", "description": "Land Condemnation"},
        {"code": "220", "description": "Foreclosure"},
        {"code": "230", "description": "Rent Lease & Ejectment"},
        {"code": "240", "description": "Torts to Land"},
        {"code": "245", "description": "Tort Product Liability"},
        {"code": "290", "description": "All Other Real Property"},
    ],
    "Torts - Personal Injury": [
        {"code": "310", "description": "Airplane"},
        {"code": "315", "description": "Airplane Product Liability"},
        {"code": "320", "description": "Assault, Libel & Slander"},
        {"code": "330", "description": "Federal Employers' Liability"},
        {"code": "340", "description": "Marine"},
        {"code": "345", "description": "Marine Product Liability"},
        {"code": "350", "description": "Motor Vehicle"},
        {"code": "355", "description": "Motor Vehicle Product Liability"},
        {"code": "360", "description": "Other Personal Injury"},
        {"code": "362", "description": "Personal Injury - Medical Malpractice"},
        {"code": "365", "description": "Personal Injury - Product Liability"},
        {"code": "367", "description": "Health Care/Pharmaceutical Personal Injury"},
        {"code": "368", "description": "Asbestos Personal Injury"},
    ],
    "Torts - Personal Property": [
        {"code": "370", "description": "Other Fraud"},
        {"code": "371", "description": "Truth in Lending"},
        {"code": "380", "description": "Other Personal Property Damage"},
        {"code": "385", "description": "Property Damage Product Liability"},
    ],
    "Civil Rights": [
        {"code": "440", "description": "Other Civil Rights"},
        {"code": "441", "description": "Voting"},
        {"code": "442", "description": "Employment"},
        {"code": "443", "description": "Housing/Accommodations"},
        {"code": "445", "description": "Americans with Disabilities - Employment"},
        {"code": "446", "description": "Americans with Disabilities - Other"},
        {"code": "448", "description": "Education"},
    ],
    "Prisoner Petitions": [
        {"code": "510", "description": "Motions to Vacate Sentence"},
        {"code": "530", "description": "General (Habeas Corpus)"},
        {"code": "535", "description": "Death Penalty (Habeas Corpus)"},
        {"code": "540", "description": "Mandamus & Other"},
        {"code": "550", "description": "Civil Rights"},
        {"code": "555", "description": "Prison Condition"},
        {"code": "560", "description": "Civil Detainee"},
    ],
    "Labor": [
        {"code": "710", "description": "Fair Labor Standards Act"},
        {"code": "720", "description": "Labor/Management Relations"},
        {"code": "740", "description": "Railway Labor Act"},
        {"code": "751", "description": "Family and Medical Leave Act"},
        {"code": "790", "description": "Other Labor Litigation"},
        {"code": "791", "description": "Employee Retirement Income Security Act"},
    ],
    "Immigration": [
        {"code": "462", "description": "Naturalization Application"},
        {"code": "465", "description": "Other Immigration Actions"},
    ],
    "Federal Tax Suits": [
        {"code": "870", "description": "Taxes (U.S. Plaintiff or Defendant)"},
        {"code": "871", "description": "IRS - Third Party 26 USC 7609"},
    ],
    "Intellectual Property": [
        {"code": "820", "description": "Copyrights"},
        {"code": "830", "description": "Patent"},
        {"code": "835", "description": "Patent - Abbreviated New Drug Application"},
        {"code": "840", "description": "Trademark"},
        {"code": "880", "description": "Defend Trade Secrets Act"},
    ],
    "Social Security": [
        {"code": "861", "description": "HIA (1395ff)"},
        {"code": "862", "description": "Black Lung (923)"},
        {"code": "863", "description": "DIWC/DIWW (405(g))"},
        {"code": "864", "description": "SSID Title XVI"},
        {"code": "865", "description": "RSI (405(g))"},
    ],
    "Other Statutes": [
        {"code": "375", "description": "False Claims Act"},
        {"code": "376", "description": "Qui Tam (31 USC 3729(a))"},
        {"code": "400", "description": "State Reapportionment"},
        {"code": "410", "description": "Antitrust"},
        {"code": "422", "description": "Appeal 28 USC 158"},
        {"code": "423", "description": "Withdrawal 28 USC 157"},
        {"code": "430", "description": "Banks and Banking"},
        {"code": "450", "description": "Commerce"},
        {"code": "460", "description": "Deportation"},
        {"code": "470", "description": "Racketeer Influenced and Corrupt Organizations"},
        {"code": "480", "description": "Consumer Credit"},
        {"code": "485", "description": "Telephone Consumer Protection Act"},
        {"code": "490", "description": "Cable/Satellite TV"},
        {"code": "850", "description": "Securities/Commodities/Exchange"},
        {"code": "890", "description": "Other Statutory Actions"},
        {"code": "891", "description": "Agricultural Acts"},
        {"code": "893", "description": "Environmental Matters"},
        {"code": "895", "description": "Freedom of Information Act"},
        {"code": "896", "description": "Arbitration"},
        {"code": "899", "description": "Administrative Procedure Act/Review of Agency Decision"},
        {"code": "950", "description": "Constitutionality of State Statutes"},
    ],
}

JURISDICTION_BASIS = [
    {"code": "1", "description": "U.S. Government Plaintiff"},
    {"code": "2", "description": "U.S. Government Defendant"},
    {"code": "3", "description": "Federal Question"},
    {"code": "4", "description": "Diversity"},
]

ORIGIN_CODES = [
    {"code": "1", "description": "Original Proceeding"},
    {"code": "2", "description": "Removed from State Court"},
    {"code": "3", "description": "Remanded from Appellate Court"},
    {"code": "4", "description": "Reinstated or Reopened"},
    {"code": "5", "description": "Transferred from Another District"},
    {"code": "6", "description": "Multidistrict Litigation"},
    {"code": "8", "description": "Multidistrict Litigation - Direct File"},
]


@dataclass
class CivilCoverSheet:
    """Data for the JS-44 Civil Cover Sheet."""

    nature_of_suit_code: str = ""
    nature_of_suit_description: str = ""
    jurisdiction_basis: str = ""  # Code from JURISDICTION_BASIS
    origin: str = ""  # Code from ORIGIN_CODES
    cause_of_action_statute: str = ""  # e.g., "42 USC 1983"
    cause_of_action_brief: str = ""  # Brief description
    demand_amount: str = ""
    jury_demand: str = ""  # "plaintiff", "defendant", "both", "none"
    class_action: bool = False
    related_case_judge: str = ""
    related_case_docket: str = ""


def get_nature_of_suit_categories() -> list[str]:
    """Get all nature of suit categories."""
    return list(NATURE_OF_SUIT.keys())


def get_nature_of_suit_codes(category: str | None = None) -> list[dict[str, str]]:
    """Get nature of suit codes, optionally filtered by category."""
    if category:
        return NATURE_OF_SUIT.get(category, [])
    # Return all codes flat
    all_codes = []
    for cat, codes in NATURE_OF_SUIT.items():
        for code in codes:
            all_codes.append({**code, "category": cat})
    return all_codes


def search_nature_of_suit(query: str) -> list[dict[str, str]]:
    """Search nature of suit codes by description."""
    query_lower = query.lower()
    results = []
    for cat, codes in NATURE_OF_SUIT.items():
        for code in codes:
            if query_lower in code["description"].lower() or query_lower in cat.lower():
                results.append({**code, "category": cat})
    return results
