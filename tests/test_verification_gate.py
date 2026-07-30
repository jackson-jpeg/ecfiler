"""A check that could not run is not a check that passed.

Session 7's live QA run printed

    AI validation unavailable (ConfigError) — proceeding

as one dim grey line and carried on to the review gate. ECFiler's whole
claim is that it verifies a filing before it goes out; the failure mode
that matters most is the product implying a check happened when it did not
(ledger L20).

The rule these tests pin: an unavailable verification stage stops the run
unless the attorney explicitly waives it, and a waiver is carried into the
attorney-review panel and hashed into the attestation, so the permanent
record shows the filing went out unverified.
"""

from __future__ import annotations

import pytest

from ecfiler.config import AppConfig, ConfigError
from ecfiler.filing.models import (
    CaseInfo,
    Document,
    EventCode,
    Filing,
    VerificationRecord,
    VerificationStatus,
)
from ecfiler.filing.workflow import (
    AI_VALIDATION,
    WAIVER_PHRASE,
    FilingWorkflow,
)


@pytest.fixture
def workflow(tmp_path) -> FilingWorkflow:
    config = AppConfig()
    config.attorney.name = "Jackson Sanger"
    wf = FilingWorkflow(config)
    pdf = tmp_path / "motion.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    wf.filing = Filing(
        court_id="azttdc",
        case=CaseInfo(case_number="0:07-cv-00170"),
        event=EventCode(code="16", description="Motion for Extension of Time"),
        documents=[Document(file_path=str(pdf), filename="motion.pdf", is_main=True)],
    )
    return wf


def _answer(monkeypatch, reply: str) -> None:
    """Stand in for the human at the waiver prompt."""
    monkeypatch.setattr(
        "ecfiler.filing.workflow.Prompt.ask", lambda *a, **k: reply
    )


def _validator_raises(monkeypatch, exc: Exception) -> None:
    monkeypatch.setattr(
        FilingWorkflow, "_get_claude", lambda self: (_ for _ in ()).throw(exc)
    )


def _pdf_is_readable(monkeypatch) -> None:
    """The fixture PDF is a stub; let the text extraction succeed."""
    monkeypatch.setattr(
        "ecfiler.pdf.validator.extract_title", lambda *a, **k: "Motion"
    )
    monkeypatch.setattr(
        "ecfiler.pdf.validator.extract_text", lambda *a, **k: "Motion text"
    )


class TestUnavailableStops:
    def test_the_qa_day_line_no_longer_proceeds_silently(
        self, workflow, monkeypatch
    ) -> None:
        """ConfigError used to print one line and continue."""
        _validator_raises(monkeypatch, ConfigError("ANTHROPIC_API_KEY not set"))
        _answer(monkeypatch, "")
        with pytest.raises(KeyboardInterrupt) as e:
            workflow._step_ai_validation()
        assert "AI validation did not run" in str(e.value)

    def test_a_declined_waiver_stops(self, workflow, monkeypatch) -> None:
        _validator_raises(monkeypatch, RuntimeError("service unreachable"))
        _answer(monkeypatch, "no")
        with pytest.raises(KeyboardInterrupt):
            workflow._step_ai_validation()

    def test_near_misses_do_not_waive(self, workflow, monkeypatch) -> None:
        _validator_raises(monkeypatch, RuntimeError("service unreachable"))
        for reply in ["file", "unverified", "yes", "y", "FILE  UNVERIFIED"]:
            _answer(monkeypatch, reply)
            with pytest.raises(KeyboardInterrupt):
                workflow._step_ai_validation()

    def test_the_stop_is_recorded_too(self, workflow, monkeypatch) -> None:
        """A cancelled run's draft should still say why it stopped."""
        _validator_raises(monkeypatch, ConfigError("ANTHROPIC_API_KEY not set"))
        _answer(monkeypatch, "")
        with pytest.raises(KeyboardInterrupt):
            workflow._step_ai_validation()
        record = workflow.filing.verification[0]
        assert record.status == VerificationStatus.UNAVAILABLE
        assert record.waived_by == ""
        assert "ANTHROPIC_API_KEY" in record.detail

    def test_an_unparseable_response_is_not_a_pass(
        self, workflow, monkeypatch
    ) -> None:
        class Claude:
            def validate_filing_package(self, **kwargs):
                return {"parse_error": True}

        _pdf_is_readable(monkeypatch)
        monkeypatch.setattr(FilingWorkflow, "_get_claude", lambda self: Claude())
        _answer(monkeypatch, "")
        with pytest.raises(KeyboardInterrupt):
            workflow._step_ai_validation()
        assert workflow.filing.unverified_stages


class TestExplicitWaiver:
    def test_the_exact_phrase_proceeds(self, workflow, monkeypatch) -> None:
        _validator_raises(monkeypatch, ConfigError("ANTHROPIC_API_KEY not set"))
        _answer(monkeypatch, WAIVER_PHRASE)
        workflow._step_ai_validation()  # does not raise

    def test_lowercase_is_accepted(self, workflow, monkeypatch) -> None:
        _validator_raises(monkeypatch, ConfigError("nope"))
        _answer(monkeypatch, "file unverified")
        workflow._step_ai_validation()

    def test_the_waiver_names_who_waived_it(self, workflow, monkeypatch) -> None:
        _validator_raises(monkeypatch, ConfigError("ANTHROPIC_API_KEY not set"))
        _answer(monkeypatch, WAIVER_PHRASE)
        workflow._step_ai_validation()
        record = workflow.filing.verification[0]
        assert record.stage == AI_VALIDATION
        assert record.status == VerificationStatus.UNAVAILABLE
        assert record.waived_by == "Jackson Sanger"
        assert record.waived_at
        assert record.is_waived

    def test_the_waiver_records_why_the_check_could_not_run(
        self, workflow, monkeypatch
    ) -> None:
        _validator_raises(monkeypatch, RuntimeError("connection timed out"))
        _answer(monkeypatch, WAIVER_PHRASE)
        workflow._step_ai_validation()
        assert "connection timed out" in workflow.filing.verification[0].detail


class TestTheAttestationShowsIt:
    def test_the_attestation_text_says_the_filing_was_unverified(
        self, workflow, monkeypatch
    ) -> None:
        _validator_raises(monkeypatch, ConfigError("ANTHROPIC_API_KEY not set"))
        _answer(monkeypatch, WAIVER_PHRASE)
        workflow._step_ai_validation()
        sentence = workflow._waiver_sentence()
        assert "WITHOUT verification" in sentence
        assert "AI validation" in sentence
        assert "Jackson Sanger" in sentence

    def test_a_verified_filing_gets_no_waiver_clause(
        self, workflow, monkeypatch
    ) -> None:
        """An ordinary filing's attestation reads exactly as it always has."""
        _passing_validator(monkeypatch)
        workflow._step_ai_validation()
        assert workflow._waiver_sentence() == ""

    def test_the_record_survives_a_round_trip(self, workflow, monkeypatch) -> None:
        """It has to reach the attestation payload as JSON."""
        _validator_raises(monkeypatch, ConfigError("nope"))
        _answer(monkeypatch, WAIVER_PHRASE)
        workflow._step_ai_validation()
        dumped = workflow.filing.model_dump(mode="json")
        reloaded = Filing.model_validate(dumped)
        assert reloaded.verification[0].waived_by == "Jackson Sanger"
        assert reloaded.unverified_stages


def _passing_validator(monkeypatch) -> None:
    class Claude:
        def validate_filing_package(self, **kwargs):
            return {"valid": True, "warnings": [], "errors": []}

    _pdf_is_readable(monkeypatch)
    monkeypatch.setattr(FilingWorkflow, "_get_claude", lambda self: Claude())


class TestStagesThatDidRun:
    def test_passing_is_recorded(self, workflow, monkeypatch) -> None:
        _passing_validator(monkeypatch)
        workflow._step_ai_validation()
        assert workflow.filing.verification[0].status == VerificationStatus.PASSED
        assert not workflow.filing.unverified_stages

    def test_the_validator_objecting_is_not_the_same_as_not_running(
        self, workflow, monkeypatch
    ) -> None:
        """It ran and said no. That belongs in the record, and it does not
        stop the run — the attorney-review gate is where that call is made."""

        class Claude:
            def validate_filing_package(self, **kwargs):
                return {
                    "valid": False,
                    "errors": ["Document title does not match event code"],
                    "warnings": [],
                }

        _pdf_is_readable(monkeypatch)
        monkeypatch.setattr(FilingWorkflow, "_get_claude", lambda self: Claude())
        workflow._step_ai_validation()
        record = workflow.filing.verification[0]
        assert record.status == VerificationStatus.ISSUES_FOUND
        assert "does not match" in record.detail
        assert not workflow.filing.unverified_stages
        assert workflow._waiver_sentence() == ""

    def test_one_record_per_stage(self, workflow, monkeypatch) -> None:
        _passing_validator(monkeypatch)
        workflow._step_ai_validation()
        workflow._step_ai_validation()
        assert len(workflow.filing.verification) == 1


class TestTheReviewPanelShowsIt:
    """The attestation is only honest if the attorney saw this at CONFIRM."""

    def _panel_text(self, workflow, monkeypatch) -> str:
        import io

        from rich.console import Console

        buffer = io.StringIO()
        monkeypatch.setattr(
            "ecfiler.filing.workflow.console", Console(file=buffer, width=200)
        )
        monkeypatch.setattr(
            "ecfiler.filing.workflow.Prompt.ask", lambda *a, **k: "cancel"
        )
        workflow._step_attorney_review()
        return buffer.getvalue()

    def test_a_waived_stage_is_on_the_review_panel(
        self, workflow, monkeypatch
    ) -> None:
        workflow.filing.verification = [
            VerificationRecord(
                stage=AI_VALIDATION,
                status=VerificationStatus.UNAVAILABLE,
                detail="ANTHROPIC_API_KEY not set",
                waived_by="Jackson Sanger",
                waived_at="2026-07-30T00:00:00+00:00",
            )
        ]
        text = self._panel_text(workflow, monkeypatch)
        assert "DID NOT RUN" in text
        assert "unverified" in text.lower()

    def test_a_passed_stage_shows_as_passed(self, workflow, monkeypatch) -> None:
        workflow.filing.verification = [
            VerificationRecord(
                stage=AI_VALIDATION, status=VerificationStatus.PASSED
            )
        ]
        assert "passed" in self._panel_text(workflow, monkeypatch)
