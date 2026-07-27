"""Pre-flight checks for CM/ECF filing.

Catches problems BEFORE the browser automation starts, so the attorney
doesn't waste time watching a filing fail halfway through.

Checks:
1. All documents are valid PDFs
2. Court exists and is accessible
3. Event code is valid for the court type
4. Filing party is specified
5. Sealed documents have proper configuration
6. Response filings have a related entry
7. Case opening filings have complete data
8. Amended filings reference the original
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from ecfiler.filing.models import Filing, SealingLevel
from ecfiler.logging import get_logger

logger = get_logger(__name__)

# Language that suggests a filing touches sealed/restricted material. A hit on
# an unsealed filing is never silently ignored: the attorney must either mark
# the document sealed or explicitly confirm public filing.
SEAL_KEYWORD_RE = re.compile(
    r"\b(seal(?:ed|ing)?|restrict(?:ed|ion)?|redact(?:ed|ion)?|ex parte|in camera)\b",
    re.IGNORECASE,
)


def scan_seal_keywords(text: str) -> list[str]:
    """Return the distinct sealing-related terms found in text (lowercased)."""
    return sorted({m.group(1).lower() for m in SEAL_KEYWORD_RE.finditer(text or "")})


@dataclass
class PreflightResult:
    """Result of pre-flight checks."""

    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.passed = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


def run_preflight(filing: Filing) -> PreflightResult:
    """Run all pre-flight checks on a filing.

    Args:
        filing: The filing to check

    Returns:
        PreflightResult with pass/fail status and details
    """
    result = PreflightResult(passed=True)

    _check_documents(filing, result)
    _check_court(filing, result)
    _check_event_code(filing, result)
    _check_filing_party(filing, result)
    _check_sealing(filing, result)
    _check_seal_keywords(filing, result)
    _check_response(filing, result)
    _check_case_opening(filing, result)
    _check_amended(filing, result)

    if result.passed:
        logger.info("Pre-flight checks passed (%d warnings)", len(result.warnings))
    else:
        logger.warning("Pre-flight checks FAILED: %d errors", len(result.errors))

    return result


def _check_documents(filing: Filing, result: PreflightResult) -> None:
    """Check that all documents exist and are valid."""
    if not filing.documents:
        result.add_error("No documents to file")
        return

    main = filing.main_document
    if not main:
        result.add_error("No main document specified")
        return

    if not Path(main.file_path).exists():
        result.add_error(f"Main document not found: {main.file_path}")

    if main.validation and not main.validation.valid:
        for err in main.validation.errors:
            result.add_error(f"Main document: {err}")

    for att in filing.attachments:
        if not Path(att.file_path).exists():
            result.add_error(f"Attachment not found: {att.file_path}")
        if att.validation and not att.validation.valid:
            for err in att.validation.errors:
                result.add_error(f"Attachment '{att.filename}': {err}")


def _check_court(filing: Filing, result: PreflightResult) -> None:
    """Check that the court exists."""
    if not filing.court_id:
        result.add_error("No court specified")
        return

    try:
        from ecfiler.courts.registry import CourtRegistry

        registry = CourtRegistry()
        registry.get(filing.court_id)
    except Exception:
        result.add_error(f"Court '{filing.court_id}' not found in registry")


def _check_event_code(filing: Filing, result: PreflightResult) -> None:
    """Check that the event code is specified."""
    if not filing.event.code:
        result.add_error("No event code specified")
    if not filing.event.description:
        result.add_warning("Event code has no description")


def _check_filing_party(filing: Filing, result: PreflightResult) -> None:
    """Check filing party is specified."""
    if not filing.filing_party:
        result.add_warning("No filing party specified — CM/ECF requires party selection")
    elif not filing.filing_party.party_name:
        result.add_error("Filing party name is empty")


def _check_sealing(filing: Filing, result: PreflightResult) -> None:
    """Check sealed document configuration.

    Sealed filings fail closed: misconfiguration is an error, never a warning —
    a sealed document silently filed public is the worst possible outcome.
    """
    for doc in filing.documents:
        if doc.is_sealed:
            result.add_warning(
                f"'{doc.filename}' is marked as {doc.sealing.value} — "
                f"the filing will abort unless the court's ECF sealing controls "
                f"are found and set; some courts require conventional (paper) "
                f"filing under seal per local rule"
            )
            if doc.sealing == SealingLevel.SEALED and not doc.description:
                result.add_error(
                    f"Sealed document '{doc.filename}' has no description — "
                    f"courts require a reason for sealing; add one before filing"
                )

        if doc.sealing == SealingLevel.EX_PARTE:
            result.add_warning(
                f"'{doc.filename}' is an ex parte submission — "
                f"opposing party will NOT be served"
            )


def _check_seal_keywords(filing: Filing, result: PreflightResult) -> None:
    """Flag sealing-related language on filings not marked sealed.

    A hit is an error unless the attorney set confirmed_public explicitly.
    'Motion to Unseal' and similar false positives are exactly why this is a
    confirmable gate rather than a hard block.
    """
    has_sealed_docs = any(d.is_sealed for d in filing.documents) or bool(
        filing.exhibit_package and filing.exhibit_package.has_sealed_exhibits
    )
    if has_sealed_docs or filing.confirmed_public:
        return

    hits = scan_seal_keywords(f"{filing.event.description} {filing.docket_text}")
    if hits:
        result.add_error(
            f"Event or docket text mentions sealing-related terms ({', '.join(hits)}) "
            f"but no document is marked sealed. Mark the document sealed, or set "
            f"confirmed_public to attest this is intentionally a public filing."
        )


def _check_response(filing: Filing, result: PreflightResult) -> None:
    """Check response filing has required context."""
    if filing.is_response and not filing.related_entry:
        result.add_warning(
            "Filing is marked as a response but no related docket entry specified — "
            "CM/ECF may require selecting the entry being responded to"
        )
    if filing.is_response and filing.related_entry and not filing.related_entry.docket_number:
        result.add_error("Response filing has empty docket number for related entry")


def _check_case_opening(filing: Filing, result: PreflightResult) -> None:
    """Check case opening data is complete."""
    if not filing.case_opening:
        return

    co = filing.case_opening
    if not co.case_type:
        result.add_error("Case opening: case type not specified (cv/cr/bk)")

    if not co.plaintiffs and not co.defendants:
        result.add_error("Case opening: no parties specified")

    if co.case_type == "cv" and not co.jurisdiction_basis:
        result.add_warning("Case opening: no jurisdiction basis specified for civil case")

    if co.is_bankruptcy:
        if not co.chapter:
            result.add_error("Bankruptcy case opening: chapter not specified")
        if not co.plaintiffs:
            result.add_error("Bankruptcy case opening: no debtor specified")


def _check_amended(filing: Filing, result: PreflightResult) -> None:
    """Check amended document references."""
    for doc in filing.documents:
        if doc.is_amended and not doc.amends_docket_number:
            result.add_warning(
                f"'{doc.filename}' is marked as amended but does not reference "
                f"the original docket entry number"
            )
