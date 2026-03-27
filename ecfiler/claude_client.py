"""Claude API integration for ECFiler.

Provides intelligent assistance for:
- Event code selection from natural language descriptions
- PDF redaction scanning (Rule 5.2 personal identifiers)
- Filing validation and completeness checks
- CM/ECF error interpretation
"""

from __future__ import annotations

from typing import Any

import anthropic

# Tool definitions that Claude can use during filing assistance
TOOLS: list[dict[str, Any]] = [
    {
        "name": "lookup_event_codes",
        "description": (
            "Search for CM/ECF event codes matching a filing description. "
            "Returns the best matching event codes for the given court and filing type."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "court_id": {
                    "type": "string",
                    "description": "Court identifier (e.g., 'nysd', 'cacd')",
                },
                "filing_description": {
                    "type": "string",
                    "description": "Natural language description of what is being filed",
                },
                "filing_category": {
                    "type": "string",
                    "enum": [
                        "motion",
                        "brief",
                        "notice",
                        "response",
                        "reply",
                        "stipulation",
                        "petition",
                        "complaint",
                        "answer",
                        "order",
                        "other",
                    ],
                    "description": "General category of the filing",
                },
            },
            "required": ["court_id", "filing_description"],
        },
    },
    {
        "name": "check_redaction",
        "description": (
            "Scan document text for unredacted personal identifiers per Rule 5.2: "
            "SSNs, tax IDs, dates of birth, minor names, financial account numbers."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "document_text": {
                    "type": "string",
                    "description": "Extracted text from the PDF document to scan",
                },
            },
            "required": ["document_text"],
        },
    },
    {
        "name": "validate_filing",
        "description": (
            "Validate that a filing package is complete and consistent. "
            "Checks document title vs event code, required attachments, etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "court_id": {"type": "string"},
                "court_type": {
                    "type": "string",
                    "enum": ["district", "bankruptcy", "appellate"],
                },
                "event_code": {"type": "string"},
                "event_description": {"type": "string"},
                "document_title": {"type": "string"},
                "document_first_page_text": {"type": "string"},
                "attachments": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of attachment filenames",
                },
            },
            "required": ["court_id", "event_code", "event_description", "document_title"],
        },
    },
    {
        "name": "interpret_ecf_error",
        "description": (
            "Interpret a CM/ECF error message and suggest corrective action. "
            "CM/ECF errors are often cryptic HTML snippets."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "error_html": {
                    "type": "string",
                    "description": "The error message or HTML from CM/ECF",
                },
                "filing_context": {
                    "type": "string",
                    "description": "What was being done when the error occurred",
                },
            },
            "required": ["error_html"],
        },
    },
]

SYSTEM_PROMPT = """\
You are ECFiler's legal filing assistant. You help attorneys file documents \
correctly on Federal CM/ECF (Case Management/Electronic Case Filing) systems.

Your role is strictly mechanical and procedural — you help with:
- Matching filing descriptions to the correct CM/ECF event codes
- Scanning documents for unredacted personal identifiers (Rule 5.2)
- Validating filing packages for completeness and consistency
- Interpreting CM/ECF system errors

You do NOT provide legal advice. You do NOT make filing decisions. \
The attorney is always responsible for the substance of their filings. \
You only assist with the procedural mechanics of electronic filing.

When recommending event codes, be specific about which code you recommend \
and explain why. If uncertain between multiple codes, present the top options \
and let the attorney choose.

When scanning for redaction issues, flag any patterns that MIGHT be personal \
identifiers — false positives are acceptable, false negatives are not. \
Personal identifiers under Rule 5.2 include:
- Social Security numbers / taxpayer IDs
- Dates of birth (for non-parties)
- Names of minor children
- Financial account numbers
- Home addresses in criminal cases
"""


class ClaudeClient:
    """Wrapper around the Anthropic SDK for ECFiler's AI features."""

    def __init__(self, api_key: str, model: str) -> None:
        self.model = model
        self._client = anthropic.Anthropic(api_key=api_key)

    def suggest_event_code(
        self,
        court_id: str,
        court_type: str,
        filing_description: str,
        available_codes: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Ask Claude to match a filing description to an event code.

        Args:
            court_id: Court identifier
            court_type: "district", "bankruptcy", or "appellate"
            filing_description: What the attorney wants to file
            available_codes: List of {"code": "...", "description": "..."} dicts

        Returns:
            Dict with "recommended_code", "recommended_description", "confidence",
            "alternatives", and "reasoning".
        """
        codes_text = "\n".join(
            f"  {c['code']}: {c['description']}" for c in available_codes
        )

        response = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Court: {court_id} ({court_type})\n"
                        f"Attorney wants to file: {filing_description}\n\n"
                        f"Available event codes:\n{codes_text}\n\n"
                        "Which event code best matches this filing? "
                        "Return your answer as JSON with keys: "
                        "recommended_code, recommended_description, confidence "
                        "(high/medium/low), alternatives (list of codes), reasoning."
                    ),
                }
            ],
        )

        return _extract_json(response.content[0].text)

    def scan_for_redaction_issues(self, document_text: str) -> dict[str, Any]:
        """Scan document text for unredacted personal identifiers.

        Returns:
            Dict with "issues" (list of findings), "risk_level" (none/low/high),
            and "summary".
        """
        response = self._client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Scan the following document text for unredacted personal "
                        "identifiers per Federal Rule of Civil Procedure 5.2. "
                        "Flag any SSNs, tax IDs, dates of birth, minor names, "
                        "financial account numbers, or criminal-case home addresses.\n\n"
                        "Return JSON with keys: issues (list of {type, text, location, "
                        "suggestion}), risk_level (none/low/high), summary.\n\n"
                        f"Document text:\n{document_text[:50000]}"
                    ),
                }
            ],
        )

        return _extract_json(response.content[0].text)

    def validate_filing_package(
        self,
        court_id: str,
        court_type: str,
        event_code: str,
        event_description: str,
        document_title: str,
        first_page_text: str,
        attachment_names: list[str],
    ) -> dict[str, Any]:
        """Validate a filing package for completeness and consistency.

        Returns:
            Dict with "valid" (bool), "warnings" (list), "errors" (list),
            and "suggestions" (list).
        """
        response = self._client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Validate this filing package:\n"
                        f"Court: {court_id} ({court_type})\n"
                        f"Event: {event_code} - {event_description}\n"
                        f"Document title: {document_title}\n"
                        f"First page text: {first_page_text[:2000]}\n"
                        f"Attachments: {attachment_names}\n\n"
                        "Check: Does the document match the event code? "
                        "Are common required attachments missing "
                        "(proposed order, certificate of service, etc.)?\n\n"
                        "Return JSON with keys: valid (bool), warnings (list of strings), "
                        "errors (list of strings), suggestions (list of strings)."
                    ),
                }
            ],
        )

        return _extract_json(response.content[0].text)

    def interpret_error(self, error_html: str, context: str = "") -> str:
        """Interpret a CM/ECF error and suggest a fix.

        Returns plain-text explanation and suggested action.
        """
        response = self._client.messages.create(
            model=self.model,
            max_tokens=512,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "CM/ECF returned this error:\n"
                        f"{error_html[:3000]}\n\n"
                        f"Context: {context}\n\n"
                        "What does this error mean and how should the attorney fix it? "
                        "Be concise and actionable."
                    ),
                }
            ],
        )

        return response.content[0].text

    def close(self) -> None:
        """Clean up the client."""
        self._client.close()


def _extract_json(text: str) -> dict[str, Any]:
    """Extract JSON from Claude's response, handling markdown code blocks."""
    import json

    # Try to find JSON in code block
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start)
        text = text[start:end].strip()
    elif "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        text = text[start:end].strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Find first { and last }
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1:
            try:
                return json.loads(text[first_brace : last_brace + 1])
            except json.JSONDecodeError:
                pass

    # Fallback: return raw text in a dict
    return {"raw_response": text, "parse_error": True}
