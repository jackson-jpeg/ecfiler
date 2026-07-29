"""The hosted→local seam: one contract, enforced in both directions.

Session 6's live QA run found this seam had never been exercised with a real
staged package. The hosted API returned a flat display dict; `stage-pull`
wrote it to disk verbatim; the CLI then tried to parse it as a `Filing` and
raised three validation errors. The mock round-trip test passed anyway
because it asserted on the flat dict it had just written — it was shaped to
match the code rather than the contract.

These tests round-trip an *actual staging-API response* through the `Filing`
model, in the same order the product does: stage → fetch → parse → save
draft → load draft → parse again. Nothing here constructs a package by hand.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ecfiler.api.app import app
from ecfiler.filing.models import Filing

STAGE_PAYLOAD = {
    "court_id": "nysd",
    "case_number": "1:24-cv-01234",
    "event_code": "12",
    "event_description": "Motion to Dismiss",
    "filing_party_name": "Smith",
    "filing_party_role": "plaintiff",
    "attestation": {
        "attested": True,
        "attestor_name": "Jane Doe, Esq.",
        "attestation_text": "I have reviewed and take responsibility.",
    },
}


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("ECFILER_DATA_DIR", str(tmp_path / "server"))
    return TestClient(app, headers={"X-User-Id": "contract-test"})


@pytest.fixture
def filer_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A filing machine with its own ~/.ecfiler.

    `CONFIG_DIR` is bound at import time, so pointing the CLI at a temp
    directory means reloading the two modules that capture it — and putting
    them back afterwards so later tests see the real paths.
    """
    import importlib

    import ecfiler.config
    import ecfiler.filing.drafts

    root = tmp_path / "filer"
    monkeypatch.setenv("ECFILER_DATA_DIR", str(root))
    importlib.reload(ecfiler.config)
    importlib.reload(ecfiler.filing.drafts)
    yield root
    monkeypatch.undo()
    importlib.reload(ecfiler.config)
    importlib.reload(ecfiler.filing.drafts)


def _stage(client: TestClient, **overrides) -> dict:
    resp = client.post("/api/filing/stage", json={**STAGE_PAYLOAD, **overrides})
    assert resp.status_code == 200, resp.text
    return resp.json()


class TestStagedPackageParsesAsFiling:
    """The seam that broke on QA day, pinned from both ends."""

    def test_stage_response_carries_canonical_filing(self, client: TestClient) -> None:
        pkg = _stage(client)
        assert "filing" in pkg, (
            "StagedPackage has no canonical filing record — the CLI cannot "
            "resume a package it cannot parse"
        )
        filing = Filing.model_validate(pkg["filing"])
        assert filing.court_id == "nysd"
        assert filing.case.case_number == "1:24-cv-01234"
        assert filing.event.code == "12"
        assert filing.event.description == "Motion to Dismiss"
        assert filing.filing_party is not None
        assert filing.filing_party.party_name == "Smith"
        assert filing.filing_party.party_role == "plaintiff"

    def test_fetched_package_parses_too(self, client: TestClient) -> None:
        """GET must return what POST promised — the CLI reads the GET."""
        code = _stage(client)["stage_code"]
        fetched = client.get(f"/api/filing/stage/{code}")
        assert fetched.status_code == 200, fetched.text
        Filing.model_validate(fetched.json()["filing"])

    def test_draft_written_from_a_real_package_reloads_as_filing(
        self, client: TestClient, filer_dir: Path
    ) -> None:
        """stage → draft → resume, the exact sequence Resume Draft runs.

        Fails without the contract fix: the flat package is saved verbatim
        and `Filing.model_validate` raises on the missing case/event fields.
        """
        from ecfiler.filing.drafts import list_drafts, load_draft, save_draft

        pkg = client.get(f"/api/filing/stage/{_stage(client)['stage_code']}").json()
        filing = Filing.model_validate(pkg["filing"])
        save_draft(f"staged_{filing.case.case_number}", filing.model_dump(mode="json"))

        listed = list_drafts()
        assert len(listed) == 1
        assert listed[0]["court"] == "nysd"
        assert listed[0]["case"] == "1:24-cv-01234"
        assert listed[0]["event"] == "Motion to Dismiss"

        reloaded = Filing.model_validate(load_draft(listed[0]["file"]))
        assert reloaded.court_id == filing.court_id
        assert reloaded.case.case_number == filing.case.case_number
        assert reloaded.event.code == filing.event.code

    def test_flat_package_shape_is_rejected(self) -> None:
        """A regression guard on the bug itself.

        This is the shape the API used to return. If it ever parses as a
        Filing again, the model has grown loose enough to hide the bug.
        """
        from pydantic import ValidationError

        legacy = {
            "stage_code": "abc",
            "court_id": "nysd",
            "case_number": "1:24-cv-01234",
            "event_code": "12",
            "event_description": "Motion to Dismiss",
            "filing_party": "Smith (plaintiff)",
        }
        with pytest.raises(ValidationError):
            Filing.model_validate(legacy)


class TestStageCodeIsCliSafe:
    """A stage code the filer cannot paste is a broken product.

    `token_urlsafe` emits "-" and "_"; a leading "-" makes the CLI answer
    `Error: No such option '-c'`. Found by the QA-day round trip.
    """

    def test_generated_codes_are_alphanumeric(self) -> None:
        from ecfiler.api.app import new_stage_code

        for _ in range(500):
            code = new_stage_code()
            assert code.isalnum(), code
            assert not code.startswith("-"), code
            assert len(code) == 11

    def test_staged_code_survives_a_cli_argument(self, client: TestClient) -> None:
        from click.testing import CliRunner

        from ecfiler.__main__ import main

        code = _stage(client)["stage_code"]
        # No option-parsing surprises: the code reaches the command intact,
        # which we observe by the pull failing on the network, not on argv.
        result = CliRunner().invoke(
            main, ["stage-pull", code, "--server", "http://127.0.0.1:9"]
        )
        assert "No such option" not in result.output


class TestStagedProvenance:
    """The court is pinned at staging and travels with the package."""

    def test_provenance_pins_court_and_url(self, client: TestClient) -> None:
        filing = Filing.model_validate(_stage(client)["filing"])
        assert filing.staged is not None
        assert filing.staged.court_id == "nysd"
        assert filing.staged.ecf_url == "https://ecf.nysd.uscourts.gov"
        assert filing.staged.environment == "production"

    def test_provenance_survives_the_draft_round_trip(
        self, client: TestClient
    ) -> None:
        filing = Filing.model_validate(_stage(client)["filing"])
        revived = Filing.model_validate(json.loads(filing.model_dump_json()))
        assert revived.staged is not None
        assert revived.staged.court_id == filing.staged.court_id
        assert revived.staged.ecf_url == filing.staged.ecf_url

    def test_interactive_filings_have_no_provenance(self) -> None:
        """Only staged packages carry provenance; the field stays optional."""
        from ecfiler.filing.models import CaseInfo, EventCode

        filing = Filing(
            court_id="nysd",
            case=CaseInfo(case_number="1:24-cv-00001"),
            event=EventCode(code="12", description="Motion"),
        )
        assert filing.staged is None


class TestStagePullRejectsBadContracts:
    """`stage-pull` fails loudly rather than writing an unusable draft."""

    def _run_pull(self, monkeypatch: pytest.MonkeyPatch, payload):
        import httpx
        from click.testing import CliRunner

        from ecfiler.__main__ import main

        class _Resp:
            status_code = 200

            def raise_for_status(self) -> None:
                pass

            def json(self):
                return payload

        monkeypatch.setattr(httpx, "get", lambda *a, **k: _Resp())
        return CliRunner().invoke(
            main, ["stage-pull", "CODE", "--server", "http://localhost:1"]
        )

    def test_package_without_filing_record_aborts(
        self, monkeypatch: pytest.MonkeyPatch, filer_dir: Path
    ) -> None:
        result = self._run_pull(
            monkeypatch, {"stage_code": "CODE", "case_number": "1:24-cv-1"}
        )
        assert result.exit_code != 0
        assert "canonical filing record" in result.output
        assert not list(filer_dir.glob("drafts/*.json")), (
            "an unparseable package must not leave a draft behind"
        )

    def test_malformed_filing_record_aborts(
        self, monkeypatch: pytest.MonkeyPatch, filer_dir: Path
    ) -> None:
        result = self._run_pull(
            monkeypatch,
            {"stage_code": "CODE", "filing": {"court_id": "nysd"}},  # no case/event
        )
        assert result.exit_code != 0
        assert "does not parse as a Filing" in result.output
        assert not list(filer_dir.glob("drafts/*.json"))

    def test_good_package_writes_a_resumable_draft(
        self, monkeypatch: pytest.MonkeyPatch, filer_dir: Path, client: TestClient
    ) -> None:
        pkg = _stage(client)
        result = self._run_pull(monkeypatch, pkg)
        assert result.exit_code == 0, result.output
        drafts = list((filer_dir / "drafts").glob("staged_*.json"))
        assert len(drafts) == 1
        envelope = json.loads(drafts[0].read_text())
        Filing.model_validate(envelope["filing"])


class TestResumeStagedDraft:
    """Resuming a staged package attaches documents before review.

    A staged package names no local file — the document lives on the filing
    machine. Before this, Resume Draft walked a staged filing into preflight
    with an empty document list.
    """

    def test_resume_collects_documents_when_the_draft_has_none(
        self, client: TestClient, filer_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import ecfiler.app as app_module
        from ecfiler.filing.drafts import save_draft
        from ecfiler.filing.models import Document, DocumentValidation

        filing = Filing.model_validate(_stage(client)["filing"])
        assert filing.documents == []
        save_draft(f"staged_{filing.case.case_number}", filing.model_dump(mode="json"))

        doc = Document(
            file_path="/tmp/motion.pdf",
            validation=DocumentValidation(valid=True, page_count=3, has_text=True),
        )
        calls: list[str] = []

        def _select(self):
            calls.append("select")
            return [doc]

        def _validate(self, documents):
            calls.append("validate")
            return documents

        monkeypatch.setattr(
            "ecfiler.filing.workflow.FilingWorkflow._step_select_documents", _select
        )
        monkeypatch.setattr(
            "ecfiler.filing.workflow.FilingWorkflow._step_validate_documents", _validate
        )
        # Pick draft 1, then decline to continue — we are testing what happens
        # before the review gate, not the filing itself.
        answers = iter(["1", "n"])
        monkeypatch.setattr(
            app_module.Prompt, "ask", staticmethod(lambda *a, **k: next(answers))
        )

        from ecfiler.config import AppConfig

        app_module._resume_draft(AppConfig())

        assert calls == ["select", "validate"], (
            "a staged draft with no documents must collect them before review"
        )
