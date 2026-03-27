"""ECFiler MCP Server — Model Context Protocol for AI integration.

This lets Claude Code, Cursor, or any MCP-compatible AI tool
directly interact with ECFiler:

  - Analyze a PDF for filing metadata
  - Validate a PDF against CM/ECF requirements
  - Search federal courts
  - Look up event codes
  - Generate certificates of service
  - Search nature of suit codes

Run with: python -m ecfiler.mcp_server
Or configure in Claude Code's MCP settings.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


def handle_request(request: dict) -> dict:
    """Handle a single MCP JSON-RPC request."""
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    if method == "initialize":
        return _ok(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "ecfiler", "version": "0.1.0"},
        })

    if method == "notifications/initialized":
        return None  # No response needed

    if method == "tools/list":
        return _ok(req_id, {"tools": TOOLS})

    if method == "tools/call":
        tool_name = params.get("name", "")
        args = params.get("arguments", {})
        try:
            result = call_tool(tool_name, args)
            return _ok(req_id, {"content": [{"type": "text", "text": result}]})
        except Exception as e:
            return _ok(req_id, {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True})

    return _error(req_id, -32601, f"Unknown method: {method}")


def call_tool(name: str, args: dict) -> str:
    """Execute an MCP tool and return the result as text."""

    if name == "ecfiler_search_courts":
        from ecfiler.courts.registry import CourtRegistry
        registry = CourtRegistry()
        query = args.get("query", "")
        court_type = args.get("court_type")
        if query:
            courts = registry.search(query)
        else:
            courts = registry.list_courts(court_type)
        return json.dumps(courts[:25], indent=2)

    if name == "ecfiler_court_info":
        from ecfiler.courts.registry import CourtRegistry
        registry = CourtRegistry()
        court = registry.get(args["court_id"])
        p = court.profile
        from ecfiler.filing.events import get_common_events
        events = get_common_events(p.court_type)
        return json.dumps({
            "court_id": p.court_id, "name": p.name, "type": p.court_type,
            "url": p.ecf_url, "quirks": p.quirks,
            "event_count": len(events),
            "events": [{"code": e.code, "description": e.description} for e in events[:20]],
        }, indent=2)

    if name == "ecfiler_search_events":
        from ecfiler.filing.events import search_events
        results = search_events(args["query"], args.get("court_type", "district"))
        return json.dumps([{"code": e.code, "description": e.description, "category": e.category} for e in results[:15]], indent=2)

    if name == "ecfiler_validate_pdf":
        from ecfiler.pdf.validator import validate_pdf
        result = validate_pdf(args["file_path"])
        return json.dumps({
            "valid": result.valid, "size_mb": round(result.file_size_mb, 2),
            "pages": result.page_count, "searchable": result.has_text,
            "encrypted": result.is_encrypted, "errors": result.errors, "warnings": result.warnings,
        }, indent=2)

    if name == "ecfiler_scan_redaction":
        from ecfiler.pdf.validator import extract_text
        from ecfiler.pdf.redaction_check import scan_document
        text = extract_text(args["file_path"])
        report = scan_document(text)
        return json.dumps({
            "risk_level": report.risk_level,
            "issues": [{"type": i.issue_type, "text": i.text[:60], "confidence": i.confidence, "suggestion": i.suggestion} for i in report.issues],
        }, indent=2)

    if name == "ecfiler_nature_of_suit":
        from ecfiler.filing.civil_cover_sheet import search_nature_of_suit, get_nature_of_suit_codes
        query = args.get("query", "")
        if query:
            codes = search_nature_of_suit(query)
        else:
            codes = get_nature_of_suit_codes(args.get("category"))
        return json.dumps(codes[:20], indent=2)

    if name == "ecfiler_generate_cos":
        from ecfiler.agent.certificate_of_service import ServiceRecipient, generate_certificate
        recipients = [
            ServiceRecipient(name=r.get("name", ""), role=r.get("role", ""),
                attorney_name=r.get("attorney_name", ""), method=r.get("method", "CM/ECF"))
            for r in args.get("recipients", [])
        ]
        cert = generate_certificate(recipients, args["attorney_name"], case_number=args.get("case_number", ""))
        return cert.text

    if name == "ecfiler_filing_checklist":
        from ecfiler.filing.checklist import get_checklist
        cl = get_checklist(args["event_description"])
        if not cl:
            return "No checklist for this filing type."
        lines = [cl.title]
        for item in cl.items:
            marker = "[REQUIRED]" if item.required else "[ ]"
            lines.append(f"  {marker} {item.text}")
        return "\n".join(lines)

    raise ValueError(f"Unknown tool: {name}")


TOOLS = [
    {
        "name": "ecfiler_search_courts",
        "description": "Search federal courts by name or ID. Returns court_id, name, and type (district/bankruptcy/appellate).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search by name or court ID (e.g., 'new york', 'nysd')"},
                "court_type": {"type": "string", "enum": ["district", "bankruptcy", "appellate"], "description": "Filter by court type"},
            },
        },
    },
    {
        "name": "ecfiler_court_info",
        "description": "Get detailed info about a specific federal court: name, URL, quirks, and event codes.",
        "inputSchema": {
            "type": "object",
            "properties": {"court_id": {"type": "string", "description": "PACER court ID (e.g., 'nysd', 'cacd', 'ca2')"}},
            "required": ["court_id"],
        },
    },
    {
        "name": "ecfiler_search_events",
        "description": "Search CM/ECF event codes by description. Use to find the right event code for a filing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Filing description (e.g., 'motion to dismiss', 'reply brief')"},
                "court_type": {"type": "string", "enum": ["district", "bankruptcy", "appellate"], "default": "district"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "ecfiler_validate_pdf",
        "description": "Validate a PDF file against CM/ECF filing requirements: format, size, searchable text, encryption.",
        "inputSchema": {
            "type": "object",
            "properties": {"file_path": {"type": "string", "description": "Path to the PDF file"}},
            "required": ["file_path"],
        },
    },
    {
        "name": "ecfiler_scan_redaction",
        "description": "Scan a PDF for unredacted personal identifiers per Rule 5.2 (SSNs, DOBs, financial accounts).",
        "inputSchema": {
            "type": "object",
            "properties": {"file_path": {"type": "string", "description": "Path to the PDF file"}},
            "required": ["file_path"],
        },
    },
    {
        "name": "ecfiler_nature_of_suit",
        "description": "Search JS-44 Civil Cover Sheet nature of suit codes for case opening.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search by description (e.g., 'patent', 'employment')"},
                "category": {"type": "string", "description": "Filter by category (e.g., 'Civil Rights', 'Intellectual Property')"},
            },
        },
    },
    {
        "name": "ecfiler_generate_cos",
        "description": "Generate a Certificate of Service for a federal court filing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "attorney_name": {"type": "string"},
                "case_number": {"type": "string"},
                "recipients": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"}, "role": {"type": "string"},
                            "attorney_name": {"type": "string"}, "method": {"type": "string", "default": "CM/ECF"},
                        },
                    },
                },
            },
            "required": ["attorney_name", "recipients"],
        },
    },
    {
        "name": "ecfiler_filing_checklist",
        "description": "Get a filing checklist for a specific event type (e.g., 'Motion to Dismiss', 'Complaint', 'Answer').",
        "inputSchema": {
            "type": "object",
            "properties": {"event_description": {"type": "string", "description": "The filing type"}},
            "required": ["event_description"],
        },
    },
]


def _ok(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}

def _error(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def main():
    """Run the MCP server on stdio."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            pass
        except Exception as e:
            err = _error(None, -32603, str(e))
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
