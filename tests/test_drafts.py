"""Tests for filing drafts persistence."""

from pathlib import Path

import pytest

from ecfiler.filing import drafts


@pytest.fixture(autouse=True)
def use_tmp_drafts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Override drafts directory."""
    monkeypatch.setattr(drafts, "DRAFTS_DIR", tmp_path / "drafts")


class TestDrafts:
    def test_save_and_load(self) -> None:
        data = {"court_id": "nysd", "case": {"case_number": "1:24-cv-01234"}}
        drafts.save_draft("my-motion", data)

        loaded = drafts.load_draft("my-motion")
        assert loaded == data

    def test_load_nonexistent(self) -> None:
        assert drafts.load_draft("ghost") is None

    def test_list_drafts(self) -> None:
        drafts.save_draft("draft-a", {"court_id": "nysd"})
        drafts.save_draft("draft-b", {"court_id": "cacd"})

        result = drafts.list_drafts()
        assert len(result) == 2
        names = {d["name"] for d in result}
        assert "draft-a" in names
        assert "draft-b" in names

    def test_list_empty(self) -> None:
        assert drafts.list_drafts() == []

    def test_delete_draft(self) -> None:
        drafts.save_draft("to-delete", {"x": 1})
        assert drafts.delete_draft("to-delete") is True
        assert drafts.load_draft("to-delete") is None

    def test_delete_nonexistent(self) -> None:
        assert drafts.delete_draft("nope") is False

    def test_overwrite_false_appends_timestamp(self) -> None:
        drafts.save_draft("dup", {"v": 1}, overwrite=False)
        drafts.save_draft("dup", {"v": 2}, overwrite=False)
        # Should have 2 files (second gets timestamp suffix)
        result = drafts.list_drafts()
        assert len(result) == 2

    def test_overwrite_true_replaces(self) -> None:
        drafts.save_draft("dup", {"v": 1}, overwrite=True)
        drafts.save_draft("dup", {"v": 2}, overwrite=True)
        result = drafts.list_drafts()
        assert len(result) == 1
        loaded = drafts.load_draft("dup")
        assert loaded["v"] == 2

    def test_draft_metadata(self) -> None:
        drafts.save_draft("meta-test", {
            "court_id": "txsd",
            "case": {"case_number": "4:24-cv-999"},
            "event": {"description": "Motion to Compel"},
        })
        result = drafts.list_drafts()
        assert len(result) == 1
        d = result[0]
        assert d["court"] == "txsd"
        assert "999" in d["case"]
        assert "Compel" in d["event"]


class TestDraftsAPI:
    def test_list_empty(self) -> None:
        from fastapi.testclient import TestClient
        from ecfiler.api.app import app

        client = TestClient(app)
        res = client.get("/api/drafts")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_delete_nonexistent(self) -> None:
        from fastapi.testclient import TestClient
        from ecfiler.api.app import app

        client = TestClient(app)
        res = client.delete("/api/drafts/nonexistent")
        assert res.status_code == 404
