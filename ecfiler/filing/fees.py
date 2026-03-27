"""Federal court filing fee schedule.

CM/ECF collects fees as part of the filing process. Some filings
require payment before the court will process the document. Others
are free. Some filers qualify for fee waivers (IFP — in forma pauperis).

Fee schedule based on 28 U.S.C. § 1914 and the Judicial Conference
fee schedule effective December 2024.

Reference: https://www.uscourts.gov/services-forms/fees
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FilingFee:
    """Fee information for a filing type."""

    amount: float  # In USD, 0 = no fee
    description: str
    waivable: bool = True  # Can IFP waive this fee?
    notes: str = ""


# District court fees
DISTRICT_FEES: dict[str, FilingFee] = {
    "complaint": FilingFee(405.00, "Civil action filing fee", notes="Includes $350 filing fee + $55 admin fee"),
    "removal": FilingFee(405.00, "Notice of removal filing fee"),
    "appeal": FilingFee(605.00, "Notice of appeal", notes="$505 appeal fee + $100 district court fee"),
    "motion_reopen": FilingFee(405.00, "Motion to reopen"),
    "misc_action": FilingFee(52.00, "Miscellaneous case/action"),
    "motion": FilingFee(0, "Standard motion (no fee)"),
    "brief": FilingFee(0, "Brief or memorandum (no fee)"),
    "notice": FilingFee(0, "Notice (no fee)"),
    "answer": FilingFee(0, "Answer (no fee)"),
    "response": FilingFee(0, "Response/opposition (no fee)"),
    "reply": FilingFee(0, "Reply (no fee)"),
    "stipulation": FilingFee(0, "Stipulation (no fee)"),
}

# Bankruptcy court fees
BANKRUPTCY_FEES: dict[str, FilingFee] = {
    "chapter7": FilingFee(338.00, "Chapter 7 petition", notes="Can be paid in installments"),
    "chapter11": FilingFee(1738.00, "Chapter 11 petition", notes="Individuals: $1,738. Corps: same"),
    "chapter11_sub5": FilingFee(1738.00, "Chapter 11 Subchapter V (small business)"),
    "chapter12": FilingFee(278.00, "Chapter 12 petition"),
    "chapter13": FilingFee(313.00, "Chapter 13 petition"),
    "adversary": FilingFee(350.00, "Adversary proceeding"),
    "appeal": FilingFee(298.00, "Appeal to district court or BAP"),
    "motion_reopen": FilingFee(260.00, "Motion to reopen bankruptcy case"),
    "motion": FilingFee(0, "Standard motion (no fee)"),
    "proof_of_claim": FilingFee(0, "Proof of claim (no fee)"),
}

# Appellate court fees
APPELLATE_FEES: dict[str, FilingFee] = {
    "appeal": FilingFee(505.00, "Docketing fee for appeal"),
    "petition_review": FilingFee(505.00, "Petition for review from agency"),
    "petition_permission": FilingFee(505.00, "Petition for permission to appeal"),
    "petition_rehearing": FilingFee(0, "Petition for rehearing (no fee)"),
    "motion": FilingFee(0, "Standard motion (no fee)"),
    "brief": FilingFee(0, "Brief (no fee)"),
    "amicus": FilingFee(0, "Amicus brief (no fee)"),
}


def get_fee(event_description: str, court_type: str) -> FilingFee | None:
    """Look up the filing fee for an event type.

    Args:
        event_description: The event/filing description
        court_type: "district", "bankruptcy", or "appellate"

    Returns:
        FilingFee if found, None if unknown
    """
    desc_lower = event_description.lower()

    if court_type == "bankruptcy":
        fees = BANKRUPTCY_FEES
        # Check petition chapters
        if "chapter 7" in desc_lower or "voluntary petition" in desc_lower:
            return fees.get("chapter7")
        if "chapter 11" in desc_lower:
            if "subchapter v" in desc_lower or "sub v" in desc_lower:
                return fees.get("chapter11_sub5")
            return fees.get("chapter11")
        if "chapter 12" in desc_lower:
            return fees.get("chapter12")
        if "chapter 13" in desc_lower:
            return fees.get("chapter13")
        if "adversary" in desc_lower:
            return fees.get("adversary")
    elif court_type == "appellate":
        fees = APPELLATE_FEES
        if "petition for review" in desc_lower:
            return fees.get("petition_review")
        if "petition" in desc_lower and "permission" in desc_lower:
            return fees.get("petition_permission")
        if "rehearing" in desc_lower:
            return fees.get("petition_rehearing")
    else:
        fees = DISTRICT_FEES

    # Common lookups
    if "complaint" in desc_lower or "petition" in desc_lower and court_type == "district":
        return fees.get("complaint", DISTRICT_FEES["complaint"])
    if "removal" in desc_lower:
        return fees.get("removal", DISTRICT_FEES["removal"])
    if "appeal" in desc_lower:
        return fees.get("appeal")
    if "reopen" in desc_lower:
        return fees.get("motion_reopen")
    if "motion" in desc_lower:
        return fees.get("motion", FilingFee(0, "No fee"))
    if "brief" in desc_lower or "memorandum" in desc_lower:
        return fees.get("brief", FilingFee(0, "No fee"))
    if "answer" in desc_lower:
        return fees.get("answer", FilingFee(0, "No fee"))
    if "response" in desc_lower or "opposition" in desc_lower:
        return fees.get("response", FilingFee(0, "No fee"))
    if "notice" in desc_lower:
        return fees.get("notice", FilingFee(0, "No fee"))

    return None


def format_fee(fee: FilingFee) -> str:
    """Format a fee for display."""
    if fee.amount == 0:
        return "No filing fee"
    text = f"${fee.amount:.2f} — {fee.description}"
    if fee.notes:
        text += f" ({fee.notes})"
    if fee.waivable:
        text += " [IFP waiver available]"
    return text
