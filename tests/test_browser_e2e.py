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
