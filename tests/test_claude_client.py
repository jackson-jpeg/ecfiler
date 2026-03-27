"""Tests for Claude client JSON extraction."""

import pytest

from ecfiler.claude_client import _extract_json


class TestExtractJson:
    def test_plain_json(self) -> None:
        text = '{"key": "value", "number": 42}'
        result = _extract_json(text)
        assert result == {"key": "value", "number": 42}

    def test_json_in_code_block(self) -> None:
        text = 'Here is the result:\n```json\n{"key": "value"}\n```\nDone.'
        result = _extract_json(text)
        assert result == {"key": "value"}

    def test_json_in_generic_code_block(self) -> None:
        text = '```\n{"key": "value"}\n```'
        result = _extract_json(text)
        assert result == {"key": "value"}

    def test_json_with_surrounding_text(self) -> None:
        text = 'The answer is {"recommended_code": "12", "confidence": "high"} based on my analysis.'
        result = _extract_json(text)
        assert result["recommended_code"] == "12"
        assert result["confidence"] == "high"

    def test_invalid_json_returns_raw(self) -> None:
        text = "This is not JSON at all"
        result = _extract_json(text)
        assert result["parse_error"] is True
        assert "raw_response" in result

    def test_nested_json(self) -> None:
        text = '{"issues": [{"type": "ssn", "text": "123-45-6789"}], "risk_level": "high"}'
        result = _extract_json(text)
        assert result["risk_level"] == "high"
        assert len(result["issues"]) == 1
        assert result["issues"][0]["type"] == "ssn"

    def test_empty_json_object(self) -> None:
        text = "{}"
        result = _extract_json(text)
        assert result == {}

    def test_json_with_boolean_and_null(self) -> None:
        text = '{"valid": true, "errors": [], "extra": null}'
        result = _extract_json(text)
        assert result["valid"] is True
        assert result["errors"] == []
        assert result["extra"] is None
