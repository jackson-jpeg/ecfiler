"""Florida Uniform Case Number (UCN) parsing and validation.

Pre-approval work for Florida third-party-vendor certification: the UCN is the
case key for the Existing Case filing path (TS001–TS006), so nothing else in the
Florida stack can be built without it. This module needs no Portal specification
and is therefore safe to build before the application clears — unlike the ECF
4.01 message layer, which depends on XSDs the Authority only releases after
approval.

Sources — both primary, both read in full rather than summarized:

* *In Re: Uniform Case Numbering System*, Fla. Sup. Ct. Admin. Order
  (July 6, 1998, as amended Dec. 20, 1999). Supplies the six sub-fields, the
  court-type designators, and the county designator codes (Appendix).
* Uniform Case Reporting Technical Memorandum 2023-01, Attachment One,
  Office of the State Courts Administrator (Mar. 30, 2023), V2.0.0. Supplies
  the state-reporting constraints — reserved filler values, the UCN14 case
  identity rule, and the traffic-citation variation.

Structure (20 characters, no spaces; example ``012000CF000001A000XX``):

======  =========================  ===================================
pos     sub-field                  content
======  =========================  ===================================
1–2     County Designator          numeric, 01–67
3–6     Year Designator            four-digit year the clerk initiated
7–8     Court Type                 two-letter designator, e.g. ``CA``
9–14    Sequential Number          ``000001``–``999999``
15–18   Party/Defendant Identifier four-char alphanumeric
19–20   Branch/Location            two-char alphanumeric
======  =========================  ===================================

Two rules that are easy to get wrong and expensive to get wrong late:

* **UCN14 is the case.** "All UCNs with the same county, year, court type, and
  sequential number will be considered as belonging to the same case regardless
  of the content of the party/defendant identifier or branch/location
  sub-fields." Group by :attr:`UCN.ucn14`, never by the full 20 characters.
* **The 20-character UCN is static once assigned.** Correcting one requires the
  clerk to have OSCA delete the case from state systems. Treat a parsed UCN as
  immutable; this module never rewrites one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Appendix, Florida County Designator Codes (1998 order, as amended).
# "Dade" is the order's spelling; the county is now Miami-Dade.
COUNTY_CODES: dict[str, str] = {
    "01": "Alachua", "02": "Baker", "03": "Bay", "04": "Bradford",
    "05": "Brevard", "06": "Broward", "07": "Calhoun", "08": "Charlotte",
    "09": "Citrus", "10": "Clay", "11": "Collier", "12": "Columbia",
    "13": "Miami-Dade", "14": "DeSoto", "15": "Dixie", "16": "Duval",
    "17": "Escambia", "18": "Flagler", "19": "Franklin", "20": "Gadsden",
    "21": "Gilchrist", "22": "Glades", "23": "Gulf", "24": "Hamilton",
    "25": "Hardee", "26": "Hendry", "27": "Hernando", "28": "Highlands",
    "29": "Hillsborough", "30": "Holmes", "31": "Indian River", "32": "Jackson",
    "33": "Jefferson", "34": "Lafayette", "35": "Lake", "36": "Lee",
    "37": "Leon", "38": "Levy", "39": "Liberty", "40": "Madison",
    "41": "Manatee", "42": "Marion", "43": "Martin", "44": "Monroe",
    "45": "Nassau", "46": "Okaloosa", "47": "Okeechobee", "48": "Orange",
    "49": "Osceola", "50": "Palm Beach", "51": "Pasco", "52": "Pinellas",
    "53": "Polk", "54": "Putnam", "55": "St. Johns", "56": "St. Lucie",
    "57": "Santa Rosa", "58": "Sarasota", "59": "Seminole", "60": "Sumter",
    "61": "Suwannee", "62": "Taylor", "63": "Union", "64": "Volusia",
    "65": "Wakulla", "66": "Walton", "67": "Washington",
}

COUNTY_BY_NAME: dict[str, str] = {v.lower(): k for k, v in COUNTY_CODES.items()}

# Court Type Designators (1998 order, Appendix).
CIRCUIT_COURT_TYPES: dict[str, str] = {
    "CF": "Felony",
    "DR": "Domestic Relations/Family",
    "CA": "Circuit Civil",
    "CP": "Probate/Guardianship",
    "MH": "Mental Health",
    "GA": "Guardianship",
    "CJ": "Delinquency",
    "DP": "Dependency",
    "AP": "Appeal from County Court",
}

COUNTY_COURT_TYPES: dict[str, str] = {
    "MM": "Misdemeanor",
    "MO": "Municipal Ordinance",
    "CO": "County Ordinance",
    "CC": "County Civil",
    "SC": "Small Claims",
    "TR": "Traffic Infractions",
    "CT": "Criminal Traffic",
    "IN": "Non-Criminal Infraction",
}

COURT_TYPES: dict[str, str] = {**CIRCUIT_COURT_TYPES, **COUNTY_COURT_TYPES}

# Court types that may substitute a Uniform Traffic Citation number for the
# sequential number (Tech Memo 2023-01, "Sequential Number").
TRAFFIC_COURT_TYPES = frozenset({"TR", "CT"})

# The scope of ECFiler's first Florida certification (docs/fl-certification-gap-analysis.md §5).
FIRST_CERTIFICATION_COURT_TYPES = frozenset({"CA", "CC"})

# Filler values the 2023 memo forbids for state reporting. 'X' and '0' mean
# "no information" in the 1998 order, so a sub-field made only of them carries
# nothing and is rejected.
_FORBIDDEN_PARTY_IDS = frozenset({"XXXX", "0000"})
_FORBIDDEN_PARTY_IDS_V2 = frozenset({"XXX", "000"})       # 3-char traffic variation
_FORBIDDEN_PARTY_IDS_V3 = frozenset({"XX", "00"})         # pos 17-18, local-use variation
_FORBIDDEN_BRANCH = frozenset({"XX", "00"})
# Reserved by OSCA for reporting scenario #3; not for individual parties.
_RESERVED_PARTY_IDS = frozenset({"XXGE", "XGE", "GE"})

_ALNUM = re.compile(r"^[A-Z0-9]+$")


class UCNError(ValueError):
    """Raised when a string is not a well-formed Uniform Case Number."""


@dataclass(frozen=True)
class UCN:
    """A parsed, immutable Florida Uniform Case Number."""

    county_code: str
    year: str
    court_type: str
    sequential_number: str
    party_identifier: str
    branch_location: str

    def __str__(self) -> str:
        return (
            f"{self.county_code}{self.year}{self.court_type}"
            f"{self.sequential_number}{self.party_identifier}{self.branch_location}"
        )

    @property
    def ucn14(self) -> str:
        """First 14 characters — the case identity for state reporting.

        Two UCNs sharing a UCN14 are the same case even when their party and
        branch sub-fields differ. Group case activity by this, not by ``str()``.
        """
        return f"{self.county_code}{self.year}{self.court_type}{self.sequential_number}"

    @property
    def county_name(self) -> str | None:
        return COUNTY_CODES.get(self.county_code)

    @property
    def court_type_name(self) -> str | None:
        return COURT_TYPES.get(self.court_type)

    @property
    def is_circuit(self) -> bool:
        return self.court_type in CIRCUIT_COURT_TYPES

    @property
    def formatted(self) -> str:
        """Human-readable grouping, as the 2023 memo prints examples."""
        return (
            f"{self.county_code} {self.year} {self.court_type} "
            f"{self.sequential_number} {self.party_identifier} {self.branch_location}"
        )


def parse_ucn(value: str, *, strict: bool = True) -> UCN:
    """Parse a 20-character UCN.

    Args:
        value: The UCN. Spaces and hyphens are tolerated on input and stripped —
            clerks and case-management systems display UCNs both ways — but the
            canonical form has neither.
        strict: Apply the state-reporting constraints from Tech Memo 2023-01
            (no filler party/branch values, known county code, known court type,
            non-zero sequence). Set False to parse a legacy UCN assigned before
            2024, which the memo expressly does not require to be corrected.

    Raises:
        UCNError: If the value cannot be parsed, or fails a constraint under
            ``strict``.
    """
    if value is None:
        raise UCNError("UCN is required")

    cleaned = re.sub(r"[\s-]", "", str(value)).upper()
    if len(cleaned) != 20:
        raise UCNError(
            f"UCN must be 20 characters, got {len(cleaned)}: {cleaned!r}"
        )
    if not _ALNUM.match(cleaned):
        raise UCNError(f"UCN must be alphanumeric: {cleaned!r}")

    ucn = UCN(
        county_code=cleaned[0:2],
        year=cleaned[2:6],
        court_type=cleaned[6:8],
        sequential_number=cleaned[8:14],
        party_identifier=cleaned[14:18],
        branch_location=cleaned[18:20],
    )

    if not ucn.county_code.isdigit():
        raise UCNError(f"County designator must be numeric: {ucn.county_code!r}")
    if not ucn.year.isdigit():
        raise UCNError(f"Year designator must be numeric: {ucn.year!r}")

    if strict:
        _validate_strict(ucn)
    return ucn


def _validate_strict(ucn: UCN) -> None:
    """Apply Tech Memo 2023-01 state-reporting constraints."""
    if ucn.county_code not in COUNTY_CODES:
        raise UCNError(
            f"Unknown county designator {ucn.county_code!r} "
            "(valid: 01-67, per the 1998 order's Appendix)"
        )
    if ucn.court_type not in COURT_TYPES:
        raise UCNError(
            f"Unknown court type {ucn.court_type!r} "
            f"(valid: {', '.join(sorted(COURT_TYPES))})"
        )

    year = int(ucn.year)
    if not (1900 <= year <= 2200):
        raise UCNError(f"Implausible year designator: {ucn.year!r}")

    # Traffic types may carry a 7-character citation number occupying pos 9-15,
    # leaving only pos 16-18 for the party identifier. In that variation the
    # sequential sub-field is not a plain number, so the numeric check is skipped.
    traffic_variation = (
        ucn.court_type in TRAFFIC_COURT_TYPES and not ucn.sequential_number.isdigit()
    )

    if not traffic_variation:
        if not ucn.sequential_number.isdigit():
            raise UCNError(
                f"Sequential number must be six digits: {ucn.sequential_number!r}"
            )
        if int(ucn.sequential_number) == 0:
            raise UCNError("Sequential number must be between 000001 and 999999")

    if traffic_variation:
        # pos 15 belongs to the citation number; the party identifier is pos 16-18.
        party = ucn.party_identifier[1:]
        if party in _FORBIDDEN_PARTY_IDS_V2:
            raise UCNError(
                f"Party/defendant identifier {party!r} is a reserved filler value "
                "and is not allowed for state reporting"
            )
    elif ucn.party_identifier in _FORBIDDEN_PARTY_IDS:
        raise UCNError(
            f"Party/defendant identifier {ucn.party_identifier!r} is a reserved "
            "filler value and is not allowed for state reporting"
        )

    if ucn.party_identifier in _RESERVED_PARTY_IDS:
        raise UCNError(
            f"Party/defendant identifier {ucn.party_identifier!r} is reserved by OSCA "
            "for reporting scenario #3 and must not be used for an individual party"
        )

    if ucn.branch_location in _FORBIDDEN_BRANCH:
        raise UCNError(
            f"Branch/location {ucn.branch_location!r} is a reserved filler value "
            "and is not allowed for state reporting"
        )


def validate_party_identifier_variation3(party_identifier: str) -> None:
    """Apply the variation-3 constraint, which only a caller can know applies.

    Tech Memo 2023-01 defines three party/defendant identifier variations. Under
    variation 3, positions 15-16 are reserved for local use and 17-18 carry the
    actual identifier, so a trailing ``XX`` or ``00`` is filler and forbidden —
    the memo's example is ``QZXX`` invalid, ``QZAX`` valid.

    This cannot be enforced during parsing, because the variation is a local
    clerk implementation choice that leaves no trace in the string: ``AXXX`` is
    explicitly *valid* under variation 1 and would be invalid under variation 3.
    Guessing would reject conforming UCNs, so :func:`parse_ucn` checks only the
    constraints that hold across all three variations, and a caller who knows a
    county uses variation 3 calls this in addition.
    """
    if party_identifier[2:] in _FORBIDDEN_PARTY_IDS_V3:
        raise UCNError(
            f"Party/defendant identifier {party_identifier!r} ends in a reserved "
            "filler value (under variation 3, positions 17-18 may not be 'XX' or '00')"
        )


def is_valid_ucn(value: str, *, strict: bool = True) -> bool:
    """True if ``value`` parses as a UCN. Never raises."""
    try:
        parse_ucn(value, strict=strict)
        return True
    except UCNError:
        return False


def county_code_for(name: str) -> str | None:
    """Look up a county designator by county name. Case-insensitive."""
    key = name.strip().lower()
    if key in COUNTY_BY_NAME:
        return COUNTY_BY_NAME[key]
    # "Dade" is the 1998 order's spelling of Miami-Dade.
    if key == "dade":
        return "13"
    return None
