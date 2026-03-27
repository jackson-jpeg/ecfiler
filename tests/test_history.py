"""Tests for filing history storage."""

from datetime import datetime
from pathlib import Path

import pytest

from ecfiler.filing.models import FilingReceipt
from ecfiler.storage.history import FilingHistory


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
        row_id = history.log_filing(sample_receipt)
        assert row_id > 0

        entries = history.get_recent()
        assert len(entries) == 1
        assert entries[0]["court_id"] == "nysd"
        assert entries[0]["case_number"] == "1:24-cv-01234"

    def test_multiple_filings(
        self, history: FilingHistory, sample_receipt: FilingReceipt
    ) -> None:
        history.log_filing(sample_receipt)
        sample_receipt.case_number = "1:24-cv-05678"
        history.log_filing(sample_receipt)

        entries = history.get_recent()
        assert len(entries) == 2

    def test_search(
        self, history: FilingHistory, sample_receipt: FilingReceipt
    ) -> None:
        history.log_filing(sample_receipt)

        results = history.search("01234")
        assert len(results) == 1

        results = history.search("dismiss")
        assert len(results) == 1

        results = history.search("nonexistent")
        assert len(results) == 0

    def test_count(
        self, history: FilingHistory, sample_receipt: FilingReceipt
    ) -> None:
        assert history.count == 0
        history.log_filing(sample_receipt)
        assert history.count == 1

    def test_empty_history(self, history: FilingHistory) -> None:
        entries = history.get_recent()
        assert len(entries) == 0
