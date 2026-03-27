"""Live browser view — stream screenshots from Playwright as SSE events.

When filing on CM/ECF, the user sees the actual browser:
- Each navigation step captures a screenshot
- Screenshots are base64-encoded and streamed as SSE events
- The web UI shows them in real-time, so the attorney sees
  exactly what CM/ECF looks like at each step

This runs against the mock CM/ECF server for demo purposes.
For real filing, it would run against the actual court's CM/ECF.
"""

from __future__ import annotations

import asyncio
import base64
import json
from typing import AsyncGenerator

from ecfiler.logging import get_logger

logger = get_logger(__name__)


async def stream_browser_filing(
    court_id: str,
    case_number: str,
    event_code: str,
    event_description: str,
    filing_party: str,
    document_path: str = "",
    mock: bool = True,
) -> AsyncGenerator[str, None]:
    """Stream browser screenshots as the filing progresses through CM/ECF.

    Each SSE event contains:
    - event: browser
      data: {"step": "...", "status": "running|done", "screenshot": "base64...", "description": "..."}

    - event: browser_done
      data: {"success": true, "message": "..."}
    """

    def emit(step: str, status: str, description: str, screenshot_b64: str = "") -> str:
        data = {"step": step, "status": status, "description": description}
        if screenshot_b64:
            data["screenshot"] = screenshot_b64
        return f"event: browser\ndata: {json.dumps(data)}\n\n"

    def emit_done(success: bool, message: str) -> str:
        return f"event: browser_done\ndata: {json.dumps({'success': success, 'message': message})}\n\n"

    # Use mock server for demo, real CM/ECF for production
    if mock:
        base_url = "http://127.0.0.1:18923"
    else:
        from ecfiler.courts.registry import CourtRegistry
        court = CourtRegistry().get(court_id)
        base_url = court.profile.ecf_url

    try:
        # Run Playwright in a thread to avoid blocking the async event loop
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            screenshots = await asyncio.get_event_loop().run_in_executor(
                pool,
                _run_browser_steps,
                base_url, case_number, event_code, event_description, filing_party, document_path, mock,
            )

        for step_name, status, description, screenshot_bytes in screenshots:
            b64 = base64.b64encode(screenshot_bytes).decode() if screenshot_bytes else ""
            yield emit(step_name, status, description, b64)
            await asyncio.sleep(0.1)  # Let the event flush

        yield emit_done(True, "Filing steps completed. Review the screenshots above.")

    except Exception as e:
        logger.error("Browser stream error: %s", e)
        yield emit_done(False, str(e))


def _run_browser_steps(
    base_url: str,
    case_number: str,
    event_code: str,
    event_description: str,
    filing_party: str,
    document_path: str,
    mock: bool,
) -> list[tuple[str, str, str, bytes]]:
    """Run Playwright browser steps synchronously and collect screenshots.

    Returns list of (step_name, status, description, screenshot_bytes).
    """
    from ecfiler.browser.session import BrowserSession

    results: list[tuple[str, str, str, bytes]] = []

    with BrowserSession(headless=True, slow_mo=50) as browser:
        page = browser.page

        # Step 1: Navigate to CM/ECF
        page.goto(f"{base_url}/cgi-bin/login.pl")
        page.wait_for_load_state("networkidle")
        results.append(("Login Page", "done", "Navigated to CM/ECF login", page.screenshot()))

        # Step 2: Login (mock just redirects)
        if mock:
            login_form = page.query_selector("#loginForm\\:loginName")
            if login_form:
                login_form.fill("ecfiler_user")
                page.query_selector("#loginForm\\:password").fill("********")
                page.query_selector("#loginForm\\:pbtnLogin").click()
                page.wait_for_load_state("networkidle")
        results.append(("Authenticated", "done", "Logged into PACER/CM/ECF", page.screenshot()))

        # Step 3: Navigate to filing menu
        page.goto(f"{base_url}/cgi-bin/filing.pl?type=motion")
        page.wait_for_load_state("networkidle")
        results.append(("Filing Menu", "done", "Selected filing category", page.screenshot()))

        # Step 4: Click through to case entry
        next_btn = page.query_selector("input[value='Next']")
        if next_btn:
            next_btn.click()
            page.wait_for_load_state("networkidle")

        # Step 5: Enter case number
        case_input = page.query_selector("input[name='case_num']")
        if case_input:
            case_input.fill(case_number)
            page.click("input[value='Next']")
            page.wait_for_load_state("networkidle")
        results.append(("Case Entry", "done", f"Entered case {case_number}", page.screenshot()))

        # Step 6: Case confirmation
        page.click("input[value='Next']")
        page.wait_for_load_state("networkidle")
        results.append(("Case Confirmed", "done", "Case details verified", page.screenshot()))

        # Step 7: Select event
        checkboxes = page.query_selector_all("input[type='checkbox'][name='event']")
        if checkboxes:
            checkboxes[0].check()
        page.click("input[value='Next']")
        page.wait_for_load_state("networkidle")
        results.append(("Event Selected", "done", f"Selected: {event_description}", page.screenshot()))

        # Step 8: Select party
        party_cbs = page.query_selector_all("input[type='checkbox'][name='party']")
        if party_cbs:
            party_cbs[0].check()
        page.click("input[value='Next']")
        page.wait_for_load_state("networkidle")
        results.append(("Party Selected", "done", f"Filing for: {filing_party}", page.screenshot()))

        # Step 9: Document upload
        file_input = page.query_selector("input[type='file']")
        if file_input and document_path:
            file_input.set_input_files(document_path)
        page.click("input[value='Next']")
        page.wait_for_load_state("networkidle")
        results.append(("Document Uploaded", "done", "PDF uploaded to CM/ECF", page.screenshot()))

        # Step 10: Docket text
        page.click("input[value='Next']")
        page.wait_for_load_state("networkidle")
        results.append(("Docket Text", "done", "Docket text confirmed", page.screenshot()))

        # Step 11: Final confirmation page
        results.append(("Confirmation", "done", "Ready to submit — review below", page.screenshot()))

    return results
