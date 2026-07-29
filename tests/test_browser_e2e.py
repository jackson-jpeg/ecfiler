"""End-to-end browser automation tests against mock CM/ECF server.

Runs real Playwright browser against a local mock CM/ECF server.
Each test executes Playwright in a subprocess to avoid async loop
conflicts with pytest-asyncio.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import fitz
import pytest

pytest.importorskip(
    "uvicorn",
    reason="E2E browser tests require `uvicorn` to start the mock CM/ECF server. "
    "Install project deps: `pip install -r requirements.txt`.",
)


@pytest.fixture(scope="module")
def mock_server():
    """Start the mock CM/ECF server as a subprocess."""
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "tests.mock_ecf.server:app",
         "--host", "127.0.0.1", "--port", "18923", "--log-level", "error"],
        cwd=str(Path(__file__).parent.parent),
    )
    time.sleep(2)
    yield "http://127.0.0.1:18923"
    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Test motion document for e-filing.")
    pdf_path = tmp_path / "motion.pdf"
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def _run_browser_script(script: str, timeout: int = 30) -> dict:
    """Run a Playwright script in a subprocess and return the result.

    This avoids the async event loop conflict between pytest-asyncio
    and Playwright's sync API.
    """
    # Dedent the script first, then build the wrapper
    clean_script = textwrap.dedent(script).strip()
    # Indent the user script to fit inside the try block
    indented = "\n".join("    " + line for line in clean_script.split("\n"))

    full_script = (
        f"import json, sys, os\n"
        f"sys.path.insert(0, '{Path(__file__).parent.parent}')\n"
        f"os.chdir('{Path(__file__).parent.parent}')\n"
        f"try:\n"
        f"{indented}\n"
        f"    print(json.dumps({{'ok': True, 'result': result}}))\n"
        f"except Exception as e:\n"
        f"    print(json.dumps({{'ok': False, 'error': str(e)}}))\n"
    )

    proc = subprocess.run(
        [sys.executable, "-c", full_script],
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if proc.returncode != 0 and not proc.stdout.strip():
        return {"ok": False, "error": proc.stderr[:500]}

    try:
        return json.loads(proc.stdout.strip().split("\n")[-1])
    except (json.JSONDecodeError, IndexError):
        return {"ok": False, "error": proc.stdout[:300] + proc.stderr[:300]}


class TestLoginFlow:
    def test_login_page_has_cso_fields(self, mock_server: str) -> None:
        result = _run_browser_script(f"""
from ecfiler.browser.session import BrowserSession
with BrowserSession(headless=True, slow_mo=0) as browser:
    page = browser.page
    page.goto("{mock_server}/cgi-bin/login.pl")
    page.wait_for_load_state("networkidle")
    has_username = page.query_selector("#loginForm\\\\:loginName") is not None
    has_password = page.query_selector("#loginForm\\\\:password") is not None
    has_submit = page.query_selector("#loginForm\\\\:pbtnLogin") is not None
    result = {{"username": has_username, "password": has_password, "submit": has_submit}}
        """)
        assert result["ok"], result.get("error")
        assert result["result"]["username"]
        assert result["result"]["password"]
        assert result["result"]["submit"]

    def test_login_redirects_to_menu(self, mock_server: str) -> None:
        result = _run_browser_script(f"""
from ecfiler.browser.session import BrowserSession
with BrowserSession(headless=True, slow_mo=0) as browser:
    ok = browser.login_via_form("{mock_server}/cgi-bin/login.pl", "testuser", "testpass")
    result = {{"logged_in": ok, "url": browser.page.url}}
        """)
        assert result["ok"], result.get("error")
        assert result["result"]["logged_in"]


class TestFullFilingFlow:
    def test_ten_step_flow(self, mock_server: str, sample_pdf: Path) -> None:
        """Walk through the entire CM/ECF filing flow."""
        result = _run_browser_script(f"""
from ecfiler.browser.session import BrowserSession
with BrowserSession(headless=True, slow_mo=0) as browser:
    page = browser.page

    # Step 1-2: Filing tips
    page.goto("{mock_server}/cgi-bin/filing.pl?type=motion")
    page.wait_for_load_state("networkidle")
    has_tips = "Filing Tips" in page.inner_text("body")

    # Click Next to case entry
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")
    has_case_input = page.query_selector("input[name='case_num']") is not None

    # Step 3: Enter case number
    page.fill("input[name='case_num']", "1:24-cv-01234")
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")

    # Step 4: Case confirmation
    has_caption = "SMITH v. JONES" in page.inner_text("body")
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")

    # Step 5: Event checkboxes
    events = page.query_selector_all("input[type='checkbox'][name='event']")
    event_count = len(events)
    events[0].check()
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")

    # Step 6: Party checkboxes
    parties = page.query_selector_all("input[type='checkbox'][name='party']")
    party_count = len(parties)
    parties[1].check()
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")

    # Step 7: Document upload
    file_input = page.query_selector("input[type='file'][name='document']")
    has_upload = file_input is not None
    file_input.set_input_files("{sample_pdf}")
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")

    # Step 8: Docket text
    has_textarea = page.query_selector("textarea[name='docket_text']") is not None
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")

    # Step 9: Confirmation
    has_confirm = "Confirm" in page.inner_text("body")
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")

    # Step 10: Receipt
    body = page.inner_text("body")
    has_nef = "Notice of Electronic Filing" in body
    has_docket = "Docket #58" in body

    result = {{
        "has_tips": has_tips,
        "has_case_input": has_case_input,
        "has_caption": has_caption,
        "event_count": event_count,
        "party_count": party_count,
        "has_upload": has_upload,
        "has_textarea": has_textarea,
        "has_confirm": has_confirm,
        "has_nef": has_nef,
        "has_docket": has_docket,
    }}
        """)
        assert result["ok"], result.get("error")
        r = result["result"]
        assert r["has_tips"], "Filing tips page not found"
        assert r["has_case_input"], "Case number input not found"
        assert r["has_caption"], "Case caption not shown"
        assert r["event_count"] >= 3, f"Expected 3+ events, got {r['event_count']}"
        assert r["party_count"] >= 2, f"Expected 2+ parties, got {r['party_count']}"
        assert r["has_upload"], "File upload not found"
        assert r["has_textarea"], "Docket text textarea not found"
        assert r["has_confirm"], "Confirmation page not shown"
        assert r["has_nef"], "NEF receipt not shown"
        assert r["has_docket"], "Docket number not in receipt"


class TestReceiptExtraction:
    def test_extract_docket_from_receipt(self, mock_server: str) -> None:
        """Test receipt parsing by posting directly to the submit endpoint."""
        result = _run_browser_script(f"""
from ecfiler.browser.session import BrowserSession
from ecfiler.courts.base import BaseCourt, CourtProfile
with BrowserSession(headless=True, slow_mo=0) as browser:
    page = browser.page
    # Go directly to the NEF receipt page via POST
    page.goto("{mock_server}/cgi-bin/submit.pl")
    page.wait_for_load_state("networkidle")

    court = BaseCourt(CourtProfile(court_id="test", name="Test", court_type="district", ecf_url="{mock_server}"))
    receipt = court.get_receipt_info(page)
    result = {{"docket_number": receipt.get("docket_number", ""), "has_text": len(receipt.get("page_text", "")) > 0}}
        """)
        assert result["ok"], result.get("error")
        assert result["result"]["docket_number"] == "58"
        assert result["result"]["has_text"]


@pytest.fixture(scope="module")
def api_server(tmp_path_factory):
    """The hosted staging API, as a real HTTP server in dev-auth mode."""
    data_dir = tmp_path_factory.mktemp("api-data")
    import os

    env = dict(os.environ)
    env["ECFILER_DEV_AUTH"] = "1"
    env["ECFILER_DATA_DIR"] = str(data_dir)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "ecfiler.api.app:app",
         "--host", "127.0.0.1", "--port", "18924", "--log-level", "error"],
        cwd=str(Path(__file__).parent.parent),
        env=env,
    )
    # Poll for readiness instead of guessing at a sleep: a fixed wait that is
    # a little too short reports as "connection refused" from the first test,
    # which reads like a product bug and is not one.
    import httpx

    url = "http://127.0.0.1:18924"
    for _ in range(100):
        if proc.poll() is not None:
            raise RuntimeError(f"staging API exited early (rc={proc.returncode})")
        try:
            httpx.get(f"{url}/api/health", timeout=1)
            break
        except httpx.RequestError:
            time.sleep(0.2)
    else:
        proc.terminate()
        raise RuntimeError("staging API did not become ready within 20s")
    yield url, data_dir
    proc.terminate()
    proc.wait(timeout=5)


class TestStagedToNefRoundTrip:
    """The full staging→CLI→NEF path, end to end, minus a real court.

    This is the QA-day sequence with the mock CM/ECF standing in for the QA
    PACER environment: stage on the hosted API (with attestation), pull the
    package down with the real `ecfiler stage-pull` CLI, drive the browser
    through the full filing flow to a NEF, and record the submission
    attestation with the NEF text — then prove both chains verify.
    """

    def test_stage_pull_file_nef_attest(
        self, api_server, mock_server: str, sample_pdf: Path, tmp_path: Path
    ) -> None:
        import os
        import sqlite3

        import httpx

        from ecfiler.storage.attestation import AttestationLog

        api_url, api_data_dir = api_server
        filer_dir = tmp_path / "filer-machine"
        filer_dir.mkdir()

        # 1. Stage on the hosted API, attested.
        resp = httpx.post(
            f"{api_url}/api/filing/stage",
            headers={"X-User-Id": "qa-dryrun"},
            json={
                "court_id": "nysd",
                "case_number": "1:24-cv-01234",
                "event_code": "12",
                "event_description": "Motion to Dismiss",
                "filing_party_name": "Smith",
                "filing_party_role": "plaintiff",
                "attestation": {
                    "attested": True,
                    "attestor_name": "Jane Doe, Esq.",
                    "attestation_text": "I reviewed this package and take responsibility.",
                },
            },
            timeout=15,
        )
        assert resp.status_code == 200, resp.text
        stage_code = resp.json()["stage_code"]

        # The staged attestation exists server-side and verifies.
        server_log = AttestationLog(db_path=api_data_dir / "history.db")
        ok, problems = server_log.verify_chain()
        assert ok, problems

        # 2. Pull it down with the real CLI, as the filing machine would.
        env = dict(os.environ)
        env["ECFILER_DATA_DIR"] = str(filer_dir)
        env["ECFILER_SERVER"] = api_url
        env["ECFILER_DEV_USER"] = "qa-dryrun"
        pull = subprocess.run(
            [sys.executable, "-m", "ecfiler", "stage-pull", stage_code],
            capture_output=True, text=True, timeout=30, env=env,
            cwd=str(Path(__file__).parent.parent),
        )
        assert pull.returncode == 0, pull.stderr + pull.stdout
        drafts = list((filer_dir / "drafts").glob("staged_*.json"))
        assert len(drafts) == 1, "stage-pull did not save a draft"
        draft = json.loads(drafts[0].read_text())

        # The draft must load as the product loads it — through the Filing
        # model, the same call Resume Draft makes. Asserting on raw dict keys
        # is what let the hosted→local seam ship broken: the old assertion
        # matched the shape the code happened to write, not the shape the
        # CLI can read.
        from ecfiler.filing.models import Filing

        filing = Filing.model_validate(draft["filing"])
        assert filing.case.case_number == "1:24-cv-01234"
        assert filing.event.code == "12"
        assert filing.filing_party is not None

        # The court survives the seam intact, with its provenance pinned.
        assert filing.court_id == "nysd"
        assert filing.staged is not None
        assert filing.staged.court_id == "nysd"
        assert filing.staged.ecf_url == "https://ecf.nysd.uscourts.gov"

        # And the submit-time invariant accepts this filing only for the
        # court it was staged for.
        from ecfiler.config import FilingEnvironment
        from ecfiler.courts.registry import CourtRegistry
        from ecfiler.filing.invariants import (
            CourtSubstitutionError,
            enforce_court_invariants,
        )

        court = CourtRegistry(environment="production").get(filing.court_id)
        enforce_court_invariants(filing, court, FilingEnvironment())
        with pytest.raises(CourtSubstitutionError):
            enforce_court_invariants(
                filing,
                CourtRegistry(environment="production").get("azd"),
                FilingEnvironment(),
            )

        case_number = filing.case.case_number
        draft_path = drafts[0]

        # 3. File it against the mock court, capture the NEF, attest — the
        #    exact calls FilingWorkflow._step_submit_filing makes.
        result = _run_browser_script(f"""
import os
os.environ["ECFILER_DATA_DIR"] = r"{filer_dir}"
import json as _json

from ecfiler.browser.session import BrowserSession
from ecfiler.config import FilingEnvironment
from ecfiler.courts.registry import CourtRegistry
from ecfiler.filing.invariants import enforce_court_invariants
from ecfiler.filing.models import Filing
from ecfiler.storage.attestation import AttestationLog

# Everything below is driven by the draft the CLI actually wrote — no
# literals. If stage-pull writes something the workflow cannot read, this
# script fails before the browser opens.
filing = Filing.model_validate(_json.loads(open(r"{draft_path}").read())["filing"])
case_number = filing.case.case_number

# The submit-step sequence: resolve from the registry, enforce the court
# invariants, then apply the (localhost) URL override.
court = CourtRegistry(environment="production").get(filing.court_id)
env = FilingEnvironment(ecf_url_override="{mock_server}")
enforce_court_invariants(filing, court, env)
court.profile.ecf_url = env.ecf_url_override

with BrowserSession(headless=True, slow_mo=0) as browser:
    page = browser.page
    page.goto("{mock_server}/cgi-bin/filing.pl?type=motion")
    page.wait_for_load_state("networkidle")
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")
    page.fill("input[name='case_num']", case_number)
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")
    page.query_selector_all("input[type='checkbox'][name='event']")[0].check()
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")
    page.query_selector_all("input[type='checkbox'][name='party']")[1].check()
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")
    page.query_selector("input[type='file'][name='document']").set_input_files(r"{sample_pdf}")
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")
    page.click("input[value='Next']")
    page.wait_for_load_state("networkidle")

    receipt_info = court.get_receipt_info(page)
    receipt_path = browser.save_receipt(case_number, receipt_info.get("docket_number") or "unknown")

    log = AttestationLog()
    rec = log.record(
        kind="submitted",
        attestor_name="Jane Doe, Esq.",
        attestation_text="Typed CONFIRM at attorney review and YES at the CM/ECF final confirmation screen.",
        payload={{
            "court_id": filing.court_id,
            "staged_court_id": filing.staged.court_id,
            "case_number": case_number,
            "event_code": filing.event.code,
        }},
        nef_text=receipt_info.get("page_text", ""),
        trace_path="trace_dryrun",
    )
    with open(receipt_path, "a") as rf:
        rf.write(f"\\n<!-- ECFiler attestation chain head: {{log.chain_head()}} -->\\n")

    ok, problems = log.verify_chain()
    result = {{
        "docket_number": receipt_info.get("docket_number", ""),
        "nef_captured": "Notice of Electronic Filing" in receipt_info.get("page_text", ""),
        "chain_ok": ok,
        "problems": problems,
        "receipt_path": str(receipt_path),
        "record_hash": rec.record_hash,
        "court_id": filing.court_id,
        "case_number": case_number,
    }}
        """, timeout=60)
        assert result["ok"], result.get("error")
        r = result["result"]
        assert r["docket_number"] == "58"
        assert r["nef_captured"], "NEF text was not captured into the attestation"
        assert r["chain_ok"], r["problems"]
        # The court and case that were staged are the ones that got filed.
        assert r["court_id"] == "nysd"
        assert r["case_number"] == "1:24-cv-01234"

        # 4. The receipt the filer keeps carries the chain-head anchor, and
        #    the stored NEF text round-trips through the payload store.
        receipt_text = Path(r["receipt_path"]).read_text()
        assert "ECFiler attestation chain head:" in receipt_text
        assert r["record_hash"] in receipt_text

        with sqlite3.connect(filer_dir / "history.db") as conn:
            nef_text = conn.execute(
                "SELECT nef_text FROM attestation_payloads ORDER BY attestation_id DESC LIMIT 1"
            ).fetchone()[0]
        assert "Notice of Electronic Filing" in nef_text
        assert "Docket #58" in nef_text
