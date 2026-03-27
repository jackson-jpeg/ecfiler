"""Tests for the MCP server."""

import json

import pytest

from ecfiler.mcp_server import TOOLS, call_tool, handle_request


class TestMCPProtocol:
    def test_initialize(self) -> None:
        resp = handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        assert resp["result"]["serverInfo"]["name"] == "ecfiler"
        assert resp["result"]["capabilities"]["tools"] == {}

    def test_tools_list(self) -> None:
        resp = handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools = resp["result"]["tools"]
        assert len(tools) == 8
        names = {t["name"] for t in tools}
        assert "ecfiler_search_courts" in names
        assert "ecfiler_validate_pdf" in names
        assert "ecfiler_filing_checklist" in names

    def test_unknown_method(self) -> None:
        resp = handle_request({"jsonrpc": "2.0", "id": 3, "method": "foo/bar", "params": {}})
        assert "error" in resp


class TestMCPTools:
    def test_search_courts(self) -> None:
        result = call_tool("ecfiler_search_courts", {"query": "new york"})
        data = json.loads(result)
        assert len(data) >= 2
        assert any("new york" in c["name"].lower() for c in data)

    def test_court_info(self) -> None:
        result = call_tool("ecfiler_court_info", {"court_id": "nysd"})
        data = json.loads(result)
        assert data["court_id"] == "nysd"
        assert data["event_count"] > 0

    def test_search_events(self) -> None:
        result = call_tool("ecfiler_search_events", {"query": "motion to dismiss"})
        data = json.loads(result)
        assert any("Dismiss" in e["description"] for e in data)

    def test_validate_pdf(self, tmp_path) -> None:
        import fitz
        doc = fitz.open()
        doc.new_page().insert_text((72, 72), "Test")
        pdf = tmp_path / "test.pdf"
        doc.save(str(pdf))
        doc.close()

        result = call_tool("ecfiler_validate_pdf", {"file_path": str(pdf)})
        data = json.loads(result)
        assert data["valid"] is True

    def test_scan_redaction_clean(self, tmp_path) -> None:
        import fitz
        doc = fitz.open()
        doc.new_page().insert_text((72, 72), "Clean document text")
        pdf = tmp_path / "clean.pdf"
        doc.save(str(pdf))
        doc.close()

        result = call_tool("ecfiler_scan_redaction", {"file_path": str(pdf)})
        data = json.loads(result)
        assert data["risk_level"] == "none"

    def test_nature_of_suit(self) -> None:
        result = call_tool("ecfiler_nature_of_suit", {"query": "patent"})
        data = json.loads(result)
        assert any("Patent" in c["description"] for c in data)

    def test_generate_cos(self) -> None:
        result = call_tool("ecfiler_generate_cos", {
            "attorney_name": "Jane Smith",
            "recipients": [{"name": "Jones Corp", "method": "CM/ECF"}],
        })
        assert "Jane Smith" in result
        assert "CM/ECF" in result

    def test_filing_checklist(self) -> None:
        result = call_tool("ecfiler_filing_checklist", {"event_description": "Motion to Dismiss"})
        assert "REQUIRED" in result
        assert "12(b)" in result

    def test_unknown_tool(self) -> None:
        with pytest.raises(ValueError, match="Unknown tool"):
            call_tool("nonexistent_tool", {})
