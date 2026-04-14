"""Appellate-specific validation: FRAP type-volume limits + compliance cert.

Word counts are approximate (whitespace-split from PDF text extraction) and
will not perfectly match Microsoft Word's counter — callers should surface
that caveat to the attorney via the warnings list.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class AppellateDocType(str, Enum):
    PRINCIPAL_BRIEF = "principal_brief"
    REPLY_BRIEF = "reply_brief"
    PETITION_REHEARING = "petition_rehearing"
    AMICUS = "amicus"
    OTHER = "other"


# FRAP 32(a)(7) / 29(a)(5) / 35(b)(2) / 40(b) type-volume limits.
TYPE_VOLUME_LIMITS: dict[AppellateDocType, dict[str, int]] = {
    AppellateDocType.PRINCIPAL_BRIEF: {"words": 13000, "lines": 1300},
    AppellateDocType.REPLY_BRIEF: {"words": 6500, "lines": 650},
    AppellateDocType.PETITION_REHEARING: {"words": 3900, "lines": 390},
    AppellateDocType.AMICUS: {"words": 6500, "lines": 650},
}

BRIEF_TYPES = {
    AppellateDocType.PRINCIPAL_BRIEF,
    AppellateDocType.REPLY_BRIEF,
    AppellateDocType.AMICUS,
}


@dataclass
class AppellateValidation:
    doc_type: AppellateDocType
    word_count: int
    page_count: int
    line_count: int
    has_certificate_of_compliance: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors


_CERT_PATTERNS = [
    re.compile(r"certificate\s+of\s+compliance", re.IGNORECASE),
    re.compile(r"certify\s+that\s+this\s+(?:brief|document|petition)\s+complies", re.IGNORECASE),
    re.compile(r"type[-\s]?volume\s+limitation", re.IGNORECASE),
    re.compile(r"frap\s+32\s*\(\s*[ag]\s*\)", re.IGNORECASE),
    re.compile(r"contains?\s+\d[\d,]*\s+words", re.IGNORECASE),
]


def detect_certificate_of_compliance(text: str) -> bool:
    """Best-effort scan for a Certificate of Compliance (FRAP 32(g)).

    Favors false negatives — requires at least two independent phrase hits
    so a stray "certificate" reference in the body doesn't count.
    """
    if not text:
        return False
    hits = sum(1 for p in _CERT_PATTERNS if p.search(text))
    return hits >= 2


def classify_appellate_doc(
    document_type: str | None,
    event_description: str | None = None,
) -> AppellateDocType:
    """Map free-form descriptions to an AppellateDocType."""
    blob = " ".join(s for s in (document_type, event_description) if s).lower()
    if not blob:
        return AppellateDocType.OTHER
    if "reply" in blob and "brief" in blob:
        return AppellateDocType.REPLY_BRIEF
    if "rehearing" in blob or "en banc" in blob:
        return AppellateDocType.PETITION_REHEARING
    if "amicus" in blob:
        return AppellateDocType.AMICUS
    if "brief" in blob:
        return AppellateDocType.PRINCIPAL_BRIEF
    return AppellateDocType.OTHER


def validate_appellate_document(
    doc_type: AppellateDocType,
    word_count: int,
    page_count: int,
    line_count: int,
    text: str,
) -> AppellateValidation:
    """Run FRAP type-volume + compliance-cert checks."""
    has_cert = detect_certificate_of_compliance(text)
    result = AppellateValidation(
        doc_type=doc_type,
        word_count=word_count,
        page_count=page_count,
        line_count=line_count,
        has_certificate_of_compliance=has_cert,
    )

    if doc_type == AppellateDocType.OTHER:
        return result

    limits = TYPE_VOLUME_LIMITS.get(doc_type)
    if limits:
        word_cap = limits["words"]
        line_cap = limits["lines"]
        if word_count > word_cap:
            result.errors.append(
                f"FRAP type-volume: {word_count:,} words exceeds the "
                f"{word_cap:,}-word limit for {doc_type.value} "
                f"(approximate count from PDF text — verify in Word)"
            )
        elif word_count > int(word_cap * 0.95):
            result.warnings.append(
                f"Word count {word_count:,} is within 5% of the {word_cap:,}-word "
                f"FRAP limit — verify with Word's counter before filing"
            )
        if line_count > line_cap * 1.5 and word_count > word_cap:
            result.warnings.append(
                f"Line count {line_count:,} also exceeds the {line_cap:,}-line "
                f"monospaced limit"
            )

    if doc_type in BRIEF_TYPES or doc_type == AppellateDocType.PETITION_REHEARING:
        if not has_cert:
            result.warnings.append(
                "Could not detect a Certificate of Compliance (FRAP 32(g)). "
                "Appellate briefs using type-volume rules must include one "
                "stating word count, typeface, and type size."
            )

    return result
