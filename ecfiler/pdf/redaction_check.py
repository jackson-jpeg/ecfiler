"""Redaction checking for Rule 5.2 personal identifiers.

Two-pass approach:
1. Fast regex pass for obvious patterns (SSNs, account numbers)
2. Claude AI pass for contextual detection (minor names, DOBs in context)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class RedactionIssue:
    """A potential unredacted personal identifier."""

    issue_type: str  # ssn, dob, minor_name, account_number, address
    text: str  # The flagged text
    page: int | None  # Page number if known
    confidence: str  # high, medium, low
    suggestion: str  # What to do about it


@dataclass
class RedactionReport:
    """Complete redaction scan results."""

    issues: list[RedactionIssue] = field(default_factory=list)
    risk_level: str = "none"  # none, low, high
    scanned_pages: int = 0

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def high_risk_count(self) -> int:
        return sum(1 for i in self.issues if i.confidence == "high")


# --- Regex patterns for obvious identifiers ---

SSN_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # 123-45-6789
    re.compile(r"\b\d{3}\s\d{2}\s\d{4}\b"),  # 123 45 6789
    re.compile(r"\b\d{9}\b"),  # 123456789 (only in context)
]

ACCOUNT_PATTERNS = [
    re.compile(r"\baccount\s*#?\s*:?\s*\d{6,}\b", re.IGNORECASE),
    re.compile(r"\bacct\s*\.?\s*#?\s*:?\s*\d{6,}\b", re.IGNORECASE),
    re.compile(r"\b\d{4}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}\b"),  # Credit card
]

DOB_PATTERNS = [
    re.compile(
        r"\b(?:date\s+of\s+birth|DOB|born|born\s+on|d\.o\.b\.?)\s*:?\s*"
        r"\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b",
        re.IGNORECASE,
    ),
]

EIN_PATTERNS = [
    re.compile(r"\b\d{2}-\d{7}\b"),  # EIN format: 12-3456789
]


def regex_scan(text: str) -> list[RedactionIssue]:
    """Fast regex scan for obvious personal identifier patterns."""
    issues: list[RedactionIssue] = []

    for pattern in SSN_PATTERNS:
        for match in pattern.finditer(text):
            matched = match.group()
            # Skip 9-digit pattern unless near SSN context words
            if len(matched) == 9 and not matched.count("-"):
                context_start = max(0, match.start() - 50)
                context = text[context_start : match.start()].lower()
                if not any(w in context for w in ["ssn", "social", "taxpayer", "tin"]):
                    continue

            issues.append(
                RedactionIssue(
                    issue_type="ssn",
                    text=matched,
                    page=None,
                    confidence="high",
                    suggestion=f"Redact to XXX-XX-{matched[-4:]}",
                )
            )

    for pattern in ACCOUNT_PATTERNS:
        for match in pattern.finditer(text):
            issues.append(
                RedactionIssue(
                    issue_type="account_number",
                    text=match.group(),
                    page=None,
                    confidence="high",
                    suggestion="Redact to last 4 digits only",
                )
            )

    for pattern in DOB_PATTERNS:
        for match in pattern.finditer(text):
            issues.append(
                RedactionIssue(
                    issue_type="dob",
                    text=match.group(),
                    page=None,
                    confidence="high",
                    suggestion="Redact to year only",
                )
            )

    for pattern in EIN_PATTERNS:
        for match in pattern.finditer(text):
            context_start = max(0, match.start() - 80)
            context = text[context_start : match.start()].lower()
            if any(w in context for w in ["ein", "tax", "employer", "identification"]):
                issues.append(
                    RedactionIssue(
                        issue_type="ssn",
                        text=match.group(),
                        page=None,
                        confidence="medium",
                        suggestion="Redact EIN/Tax ID to last 4 digits",
                    )
                )

    return issues


def scan_document(
    text: str,
    claude_client: object | None = None,
    page_count: int = 0,
) -> RedactionReport:
    """Full redaction scan: regex first, then optionally Claude.

    Args:
        text: Extracted document text
        claude_client: Optional ClaudeClient for AI-powered scan
        page_count: Number of pages scanned

    Returns:
        RedactionReport with all findings
    """
    # Pass 1: Regex
    issues = regex_scan(text)

    # Pass 2: Claude (if available)
    if claude_client is not None:
        try:
            from ecfiler.claude_client import ClaudeClient

            if isinstance(claude_client, ClaudeClient):
                ai_result = claude_client.scan_for_redaction_issues(text)
                if not ai_result.get("parse_error"):
                    for ai_issue in ai_result.get("issues", []):
                        issues.append(
                            RedactionIssue(
                                issue_type=ai_issue.get("type", "unknown"),
                                text=ai_issue.get("text", ""),
                                page=None,
                                confidence="medium",
                                suggestion=ai_issue.get("suggestion", "Review and redact"),
                            )
                        )
        except Exception:
            pass  # AI scan is best-effort; regex results are still valid

    # Determine risk level
    if any(i.confidence == "high" for i in issues):
        risk_level = "high"
    elif issues:
        risk_level = "low"
    else:
        risk_level = "none"

    return RedactionReport(
        issues=issues,
        risk_level=risk_level,
        scanned_pages=page_count,
    )
