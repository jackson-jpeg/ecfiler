"""No filing may reach a court other than the one it was staged for.

Session 6's QA run staged a filing for the Az Test District Court and the
draft that came back named `azd` — the real District of Arizona — because
the runbook staged against a production court ID and then "overrode" the URL
at submit time. A pydantic error was the only thing between that draft and a
production endpoint.

Two structural fixes are pinned here:

1. `enforce_court_invariants` runs before the browser launches and aborts on
   any disagreement between the staged court, the filing's court, the
   resolved court profile, and the URL override.
2. The registry serves exactly one PACER environment. A QA court is not
   merely unlikely to resolve in production mode — it is absent from it, and
   asking for it raises `CourtEnvironmentError`.
"""

from __future__ import annotations

import pytest

from ecfiler.config import FilingEnvironment
from ecfiler.courts.base import BaseCourt, CourtProfile
from ecfiler.courts.registry import (
    CourtEnvironmentError,
    CourtNotFoundError,
    CourtRegistry,
)
from ecfiler.filing.invariants import CourtSubstitutionError, enforce_court_invariants
from ecfiler.filing.models import CaseInfo, EventCode, Filing, StagedProvenance

QA_URL = "https://ecf.tc1d.aztc.uscourts.gov"
AZD_URL = "https://ecf.azd.uscourts.gov"


def _court(court_id: str, url: str, environment: str = "production") -> BaseCourt:
    return BaseCourt(
        CourtProfile(
            court_id=court_id,
            name=court_id.upper(),
            court_type="district",
            ecf_url=url,
            environment=environment,
        )
    )


def _filing(court_id: str, staged: StagedProvenance | None = None) -> Filing:
    return Filing(
        court_id=court_id,
        case=CaseInfo(case_number="0:07-cv-00170"),
        event=EventCode(code="16", description="Motion for Extension of Time"),
        staged=staged,
    )


def _provenance(court_id: str, url: str, environment: str = "qa") -> StagedProvenance:
    return StagedProvenance(
        stage_code="TESTCODE",
        staged_at="2026-07-29T00:00:00+00:00",
        court_id=court_id,
        ecf_url=url,
        environment=environment,
    )


class TestCourtSubstitutionAborts:
    def test_the_qa_day_bug_exactly(self) -> None:
        """Staged for the QA court, resolved to the real District of Arizona.

        This is the failure Jackson caught: without the invariant, the run
        proceeds and files in `azd`.
        """
        filing = _filing("azd", staged=_provenance("azttdc", QA_URL))
        env = FilingEnvironment(use_qa=True, ecf_url_override=QA_URL)
        with pytest.raises(CourtSubstitutionError) as e:
            enforce_court_invariants(filing, _court("azd", AZD_URL), env)
        assert "azttdc" in str(e.value)

    def test_url_override_may_not_retarget_a_court(self) -> None:
        """The override confirms the target; it never substitutes one."""
        filing = _filing("azd")
        env = FilingEnvironment(ecf_url_override=QA_URL)
        with pytest.raises(CourtSubstitutionError) as e:
            enforce_court_invariants(filing, _court("azd", AZD_URL), env)
        assert "never retargets" in str(e.value)

    def test_override_equal_to_the_courts_own_url_passes(self) -> None:
        filing = _filing("azttdc", staged=_provenance("azttdc", QA_URL))
        env = FilingEnvironment(use_qa=True, ecf_url_override=QA_URL)
        enforce_court_invariants(filing, _court("azttdc", QA_URL, "qa"), env)

    def test_trailing_slash_is_not_a_mismatch(self) -> None:
        filing = _filing("azttdc", staged=_provenance("azttdc", QA_URL + "/"))
        env = FilingEnvironment(use_qa=True, ecf_url_override=QA_URL)
        enforce_court_invariants(filing, _court("azttdc", QA_URL, "qa"), env)

    def test_resolved_court_must_answer_to_the_filings_id(self) -> None:
        with pytest.raises(CourtSubstitutionError):
            enforce_court_invariants(
                _filing("nysd"), _court("azd", AZD_URL), FilingEnvironment()
            )

    def test_qa_run_refuses_a_production_court(self) -> None:
        filing = _filing("azd")
        env = FilingEnvironment(use_qa=True, ecf_url_override=AZD_URL)
        with pytest.raises(CourtSubstitutionError) as e:
            enforce_court_invariants(filing, _court("azd", AZD_URL), env)
        assert "production" in str(e.value)

    def test_production_run_refuses_a_qa_court(self) -> None:
        filing = _filing("azttdc")
        with pytest.raises(CourtSubstitutionError) as e:
            enforce_court_invariants(
                filing, _court("azttdc", QA_URL, "qa"), FilingEnvironment()
            )
        assert "qa" in str(e.value)

    def test_staged_url_drift_aborts(self) -> None:
        """Same court ID, different endpoint — still a substitution."""
        filing = _filing("azttdc", staged=_provenance("azttdc", "https://evil.example"))
        env = FilingEnvironment(use_qa=True, ecf_url_override=QA_URL)
        with pytest.raises(CourtSubstitutionError) as e:
            enforce_court_invariants(filing, _court("azttdc", QA_URL, "qa"), env)
        assert "endpoint changed after staging" in str(e.value)

    def test_court_changed_after_attestation_aborts(self) -> None:
        filing = _filing("nysd", staged=_provenance("azttdc", QA_URL))
        env = FilingEnvironment(use_qa=True, ecf_url_override=QA_URL)
        with pytest.raises(CourtSubstitutionError) as e:
            enforce_court_invariants(filing, _court("nysd", QA_URL, "qa"), env)
        assert "after the attorney attested" in str(e.value)

    def test_mock_court_url_is_allowed(self) -> None:
        """localhost reaches no real court, so the dry run may point at it."""
        filing = _filing("nysd")
        env = FilingEnvironment(ecf_url_override="http://localhost:18923")
        enforce_court_invariants(filing, _court("nysd", AZD_URL), env)

    def test_unstaged_production_filing_passes(self) -> None:
        enforce_court_invariants(
            _filing("azd"), _court("azd", AZD_URL), FilingEnvironment()
        )


class TestEnvironmentSeparation:
    """A QA package cannot reach a production court, structurally."""

    def test_production_registry_excludes_qa_courts(self) -> None:
        registry = CourtRegistry(environment="production")
        with pytest.raises(CourtEnvironmentError):
            registry.get("azttdc")
        assert not any(c["court_id"] == "azttdc" for c in registry.list_courts())
        assert registry.search("tc1d") == []

    def test_qa_registry_excludes_production_courts(self) -> None:
        registry = CourtRegistry(environment="qa")
        with pytest.raises(CourtEnvironmentError):
            registry.get("azd")
        with pytest.raises(CourtEnvironmentError):
            registry.get("nysd")

    def test_qa_registry_serves_the_qa_court(self) -> None:
        """The court-directory bug: New Filing could never find tc1d."""
        registry = CourtRegistry(environment="qa")
        court = registry.get("azttdc")
        assert court.profile.ecf_url == QA_URL
        assert court.profile.environment == "qa"
        assert [c["court_id"] for c in registry.search("tc1d")] == ["azttdc"]
        assert [c["court_id"] for c in registry.search("azttdc")] == ["azttdc"]

    def test_environment_follows_the_qa_switch(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """One switch drives both the credential realm and the directory."""
        monkeypatch.setenv("ECFILER_PACER_QA", "1")
        assert CourtRegistry().environment == "qa"
        monkeypatch.delenv("ECFILER_PACER_QA")
        assert CourtRegistry().environment == "production"

    def test_unknown_court_still_says_not_found(self) -> None:
        with pytest.raises(CourtNotFoundError) as e:
            CourtRegistry(environment="production").get("zzz")
        assert "not found" in str(e.value)

    def test_production_directory_is_unchanged_by_the_qa_file(self) -> None:
        """Adding QA courts must not move the public court counts."""
        import json
        from pathlib import Path

        data = Path("ecfiler/courts/data")
        expected = sum(
            len(json.loads((data / f"{n}_courts.json").read_text()))
            for n in ("district", "bankruptcy", "appellate")
        )
        assert CourtRegistry(environment="production").count == expected

    def test_bad_environment_name_rejected(self) -> None:
        with pytest.raises(ValueError):
            CourtRegistry(environment="staging")


class TestStagingRefusesCrossEnvironment:
    """The hosted API stages only courts in its own environment."""

    def test_production_api_refuses_to_stage_a_qa_court(
        self, tmp_path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from fastapi.testclient import TestClient

        from ecfiler.api.app import app

        monkeypatch.setenv("ECFILER_DATA_DIR", str(tmp_path))
        client = TestClient(app, headers={"X-User-Id": "env-test"})
        resp = client.post(
            "/api/filing/stage",
            json={
                "court_id": "azttdc",
                "case_number": "0:07-cv-00170",
                "event_code": "16",
                "event_description": "Motion for Extension of Time",
                "filing_party_name": "DeSohi",
                "filing_party_role": "plaintiff",
                "attestation": {
                    "attested": True,
                    "attestor_name": "Jackson Sanger",
                    "attestation_text": "QA test filing.",
                },
            },
        )
        assert resp.status_code == 422
        assert "environment" in resp.text
