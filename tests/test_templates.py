"""Tests for filing templates storage."""

from pathlib import Path

import pytest

from ecfiler.storage import templates


@pytest.fixture(autouse=True)
def use_tmp_templates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Override templates directory to use tmp_path."""
    monkeypatch.setattr(templates, "TEMPLATES_DIR", tmp_path / "templates")


class TestTemplates:
    def test_save_and_load(self) -> None:
        data = {"court_id": "nysd", "event_code": "12"}
        templates.save_template("motion-dismiss", data)

        loaded = templates.load_template("motion-dismiss")
        assert loaded == data

    def test_load_nonexistent(self) -> None:
        result = templates.load_template("nonexistent")
        assert result is None

    def test_list_templates(self) -> None:
        templates.save_template("template-a", {"a": 1})
        templates.save_template("template-b", {"b": 2})

        names = templates.list_templates()
        assert "template-a" in names
        assert "template-b" in names

    def test_list_empty(self) -> None:
        names = templates.list_templates()
        assert names == []

    def test_delete_template(self) -> None:
        templates.save_template("to-delete", {"x": 1})
        assert templates.delete_template("to-delete") is True
        assert templates.load_template("to-delete") is None

    def test_delete_nonexistent(self) -> None:
        assert templates.delete_template("ghost") is False

    def test_sanitizes_name(self) -> None:
        templates.save_template("bad/name with spaces!", {"ok": True})
        # Should still be loadable with the same input
        loaded = templates.load_template("bad/name with spaces!")
        assert loaded == {"ok": True}
