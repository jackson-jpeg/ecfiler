"""Tests for filing history storage."""

from datetime import datetime
from pathlib import Path

import pytest

from ecfiler.filing.models import FilingReceipt
from ecfiler.storage.history import FilingHistory, archive_filing_pdf


@pytest.fixture
def history(tmp_path: Path) -> FilingHistory:
    return FilingHistory(db_path=tmp_path / "test_history.db")


@pytest.fixture
def sample_receipt() -> FilingReceipt:
    return FilingReceipt(
        court_id="nysd",
        case_number="1:24-cv-01234",
        docket_number="58",
        event_description="Motion to Dismiss",
        filed_at=datetime(2024, 12, 15, 10, 30, 0),
        confirmation_text="Document filed successfully",
        receipt_path="/tmp/receipt.html",
    )


class TestFilingHistory:
    def test_log_and_retrieve(
        self, history: FilingHistory, sample_receipt: FilingReceipt
    ) -> None:
        row_id = history.log_filing(sample_receipt, user_id="user_123")
        assert row_id > 0

        entries = history.get_recent(user_id="user_123")
        assert len(entries) == 1
        assert entries[0]["court_id"] == "nysd"
        assert entries[0]["case_number"] == "1:24-cv-01234"
        assert entries[0]["user_id"] == "user_123"

    def test_user_isolation(
        self, history: FilingHistory, sample_receipt: FilingReceipt
    ) -> None:
        """Filings from one user should not appear for another."""
        history.log_filing(sample_receipt, user_id="user_a")
        sample_receipt.case_number = "1:24-cv-99999"
        history.log_filing(sample_receipt, user_id="user_b")

        a_entries = history.get_recent(user_id="user_a")
        assert len(a_entries) == 1
        assert a_entries[0]["case_number"] == "1:24-cv-01234"

        b_entries = history.get_recent(user_id="user_b")
        assert len(b_entries) == 1
        assert b_entries[0]["case_number"] == "1:24-cv-99999"

    def test_multiple_filings(
        self, history: FilingHistory, sample_receipt: FilingReceipt
    ) -> None:
        history.log_filing(sample_receipt, user_id="u1")
        sample_receipt.case_number = "1:24-cv-05678"
        history.log_filing(sample_receipt, user_id="u1")

        entries = history.get_recent(user_id="u1")
        assert len(entries) == 2

    def test_search(
        self, history: FilingHistory, sample_receipt: FilingReceipt
    ) -> None:
        history.log_filing(sample_receipt, user_id="u1")

        results = history.search("01234", user_id="u1")
        assert len(results) == 1

        results = history.search("dismiss", user_id="u1")
        assert len(results) == 1

        results = history.search("nonexistent", user_id="u1")
        assert len(results) == 0

    def test_search_user_isolation(
        self, history: FilingHistory, sample_receipt: FilingReceipt
    ) -> None:
        history.log_filing(sample_receipt, user_id="u1")
        results = history.search("01234", user_id="u2")
        assert len(results) == 0

    def test_get_by_id(
        self, history: FilingHistory, sample_receipt: FilingReceipt
    ) -> None:
        row_id = history.log_filing(sample_receipt, user_id="u1")
        record = history.get_by_id(row_id, user_id="u1")
        assert record is not None
        assert record["court_id"] == "nysd"

        # Different user cannot access
        record = history.get_by_id(row_id, user_id="u2")
        assert record is None

    def test_sealed_flag(
        self, history: FilingHistory, sample_receipt: FilingReceipt
    ) -> None:
        row_id = history.log_filing(sample_receipt, user_id="u1", is_sealed=True)
        record = history.get_by_id(row_id, user_id="u1")
        assert record is not None
        assert record["is_sealed"] == 1

    def test_count(
        self, history: FilingHistory, sample_receipt: FilingReceipt
    ) -> None:
        assert history.count == 0
        history.log_filing(sample_receipt)
        assert history.count == 1

    def test_empty_history(self, history: FilingHistory) -> None:
        entries = history.get_recent()
        assert len(entries) == 0


class TestPdfArchive:
    def test_archive_normal_pdf(self, tmp_path: Path) -> None:
        """Normal PDFs should be archived."""
        import ecfiler.storage.history as hist_mod
        original_dir = hist_mod.DOCUMENTS_DIR
        hist_mod.DOCUMENTS_DIR = tmp_path / "documents"
        hist_mod.DOCUMENTS_DIR.mkdir()

        try:
            path = archive_filing_pdf(
                pdf_content=b"%PDF-1.4 fake content",
                user_id="user_123",
                court_id="nysd",
                case_number="1:24-cv-01234",
                is_sealed=False,
            )
            assert path != ""
            assert "user_123" in path
            assert (tmp_path / "documents" / path).exists()
        finally:
            hist_mod.DOCUMENTS_DIR = original_dir

    def test_sealed_pdf_never_stored(self, tmp_path: Path) -> None:
        """Sealed documents must NEVER be persisted."""
        import ecfiler.storage.history as hist_mod
        original_dir = hist_mod.DOCUMENTS_DIR
        hist_mod.DOCUMENTS_DIR = tmp_path / "documents"
        hist_mod.DOCUMENTS_DIR.mkdir()

        try:
            path = archive_filing_pdf(
                pdf_content=b"%PDF-1.4 sealed content",
                user_id="user_123",
                court_id="nysd",
                case_number="1:24-cv-01234",
                is_sealed=True,
            )
            assert path == ""
            # Verify nothing was written to disk
            user_dir = tmp_path / "documents" / "user_123"
            if user_dir.exists():
                assert len(list(user_dir.iterdir())) == 0
        finally:
            hist_mod.DOCUMENTS_DIR = original_dir

    def test_empty_user_id_skips(self) -> None:
        """No user ID means no archival."""
        path = archive_filing_pdf(
            pdf_content=b"%PDF-1.4 content",
            user_id="",
            court_id="nysd",
            case_number="1:24-cv-01234",
        )
        assert path == ""
