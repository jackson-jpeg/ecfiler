"""Mock CM/ECF server for browser automation testing.

Simulates the real NextGen CM/ECF multi-page filing workflow:
1. Login (PACER CSO style)
2. Menu selection
3. Case number entry
4. Event type selection (checkboxes)
5. Party selection (checkboxes)
6. Document upload (file input)
7. Docket text entry
8. Confirmation page
9. NEF receipt

This lets us run real Playwright tests against a local server
without PACER credentials or court access.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse

app = FastAPI(title="Mock CM/ECF")

# Track state per session
_sessions: dict[str, dict] = {}

HEADER = """
<html><head><title>Mock CM/ECF NextGen</title></head>
<body style="font-family: Arial; padding: 20px;">
<div style="background: #003366; color: white; padding: 10px; margin-bottom: 20px;">
    <b>Mock CM/ECF — Test District</b>
</div>
"""
FOOTER = "</body></html>"


@app.get("/cgi-bin/login.pl", response_class=HTMLResponse)
def login_redirect():
    """CM/ECF redirects to PACER CSO login."""
    return HTMLResponse(f"""
    {HEADER}
    <h2>PACER Central Sign-On</h2>
    <form id="loginForm" method="post" action="/csologin/login.jsf">
        <input type="hidden" name="loginForm" value="loginForm" />
        <p>Username: <input id="loginForm:loginName" name="loginForm:loginName" type="text" /></p>
        <p>Password: <input id="loginForm:password" name="loginForm:password" type="password" /></p>
        <p>Client Code: <input id="loginForm:clientCode" name="loginForm:clientCode" type="text" /></p>
        <button id="loginForm:pbtnLogin" name="loginForm:pbtnLogin" type="submit">Login</button>
    </form>
    {FOOTER}
    """)


@app.post("/csologin/login.jsf", response_class=HTMLResponse)
def do_login(request: Request):
    """Process login and redirect to ECF menu."""
    return HTMLResponse(status_code=302, headers={"Location": "/cgi-bin/showpage.pl"})


@app.get("/cgi-bin/showpage.pl", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
def ecf_menu():
    """CM/ECF main menu."""
    return HTMLResponse(f"""
    {HEADER}
    <table>
        <tr>
            <td><a href="/cgi-bin/filing.pl?civil">Civil</a></td>
            <td><a href="/cgi-bin/filing.pl?criminal">Criminal</a></td>
            <td><a href="/cgi-bin/iquery.pl">Query</a></td>
            <td><a href="/cgi-bin/reports.pl">Reports</a></td>
        </tr>
    </table>
    <h3>Civil Filing Categories</h3>
    <ul>
        <li><a href="/cgi-bin/filing.pl?type=motion">Motions and Related Filings</a></li>
        <li><a href="/cgi-bin/filing.pl?type=initial">Initial Pleadings and Service</a></li>
        <li><a href="/cgi-bin/filing.pl?type=other">Other Filings</a></li>
    </ul>
    {FOOTER}
    """)


@app.get("/cgi-bin/filing.pl", response_class=HTMLResponse)
def filing_tips():
    """ECF Filing Tips page (step 2)."""
    return HTMLResponse(f"""
    {HEADER}
    <h3>ECF Filing Tips</h3>
    <p>Ensure your document is in PDF format and under 100MB.</p>
    <form method="post" action="/cgi-bin/case_entry.pl">
        <input value="Next" type="submit" />
    </form>
    {FOOTER}
    """)


@app.post("/cgi-bin/case_entry.pl", response_class=HTMLResponse)
@app.get("/cgi-bin/case_entry.pl", response_class=HTMLResponse)
def case_entry():
    """Case number entry (step 3)."""
    return HTMLResponse(f"""
    {HEADER}
    <h3>Case Number</h3>
    <form method="post" action="/cgi-bin/case_confirm.pl">
        <p>Enter case number: <input name="case_num" type="text" /></p>
        <input value="Next" type="submit" />
    </form>
    {FOOTER}
    """)


@app.post("/cgi-bin/case_confirm.pl", response_class=HTMLResponse)
def case_confirm(case_num: str = Form("")):
    """Case confirmation (step 4)."""
    return HTMLResponse(f"""
    {HEADER}
    <h3>Case Confirmation</h3>
    <p>Case: <b>{case_num or '1:24-cv-01234'}</b></p>
    <p>Caption: <b>SMITH v. JONES CORP</b></p>
    <p>Judge: <b>Hon. Williams</b></p>
    <form method="post" action="/cgi-bin/event_select.pl">
        <input type="hidden" name="case_num" value="{case_num}" />
        <input value="Next" type="submit" />
    </form>
    {FOOTER}
    """)


@app.post("/cgi-bin/event_select.pl", response_class=HTMLResponse)
def event_select(case_num: str = Form("")):
    """Event type selection (step 5) — checkboxes."""
    return HTMLResponse(f"""
    {HEADER}
    <h3>Select Event</h3>
    <form method="post" action="/cgi-bin/party_select.pl">
        <input type="hidden" name="case_num" value="{case_num}" />
        <p><input type="checkbox" name="event" value="12" /> Motion to Dismiss</p>
        <p><input type="checkbox" name="event" value="13" /> Motion for Summary Judgment</p>
        <p><input type="checkbox" name="event" value="100" /> Memorandum of Law in Support</p>
        <p><input type="checkbox" name="event" value="301" /> Response/Opposition</p>
        <p><input type="checkbox" name="event" value="105" /> Reply Brief</p>
        <input value="Next" type="submit" />
    </form>
    {FOOTER}
    """)


@app.post("/cgi-bin/party_select.pl", response_class=HTMLResponse)
def party_select(case_num: str = Form(""), event: str = Form("")):
    """Party selection (step 6) — checkboxes."""
    return HTMLResponse(f"""
    {HEADER}
    <h3>Select Filing Party</h3>
    <form method="post" action="/cgi-bin/document_upload.pl" enctype="multipart/form-data">
        <input type="hidden" name="case_num" value="{case_num}" />
        <input type="hidden" name="event" value="{event}" />
        <p><input type="checkbox" name="party" value="1" /> Smith (Plaintiff)</p>
        <p><input type="checkbox" name="party" value="2" /> Jones Corp (Defendant)</p>
        <input value="Next" type="submit" />
    </form>
    {FOOTER}
    """)


@app.post("/cgi-bin/document_upload.pl", response_class=HTMLResponse)
async def document_upload(
    case_num: str = Form(""),
    event: str = Form(""),
    party: str = Form(""),
):
    """Document upload (step 7)."""
    return HTMLResponse(f"""
    {HEADER}
    <h3>Upload Document</h3>
    <form method="post" action="/cgi-bin/docket_text.pl" enctype="multipart/form-data">
        <input type="hidden" name="case_num" value="{case_num}" />
        <input type="hidden" name="event" value="{event}" />
        <p>Main Document: <input type="file" name="document" /></p>
        <p>Attachment: <input type="file" name="attachment" /></p>
        <input value="Next" type="submit" />
    </form>
    {FOOTER}
    """)


@app.post("/cgi-bin/docket_text.pl", response_class=HTMLResponse)
async def docket_text(
    case_num: str = Form(""),
    event: str = Form(""),
):
    """Docket text entry (step 8)."""
    return HTMLResponse(f"""
    {HEADER}
    <h3>Docket Text</h3>
    <form method="post" action="/cgi-bin/confirm.pl">
        <input type="hidden" name="case_num" value="{case_num}" />
        <input type="hidden" name="event" value="{event}" />
        <p>Modify docket text if needed:</p>
        <textarea name="docket_text" rows="3" cols="60">Motion to Dismiss</textarea>
        <br/><br/>
        <input value="Next" type="submit" />
    </form>
    {FOOTER}
    """)


@app.post("/cgi-bin/confirm.pl", response_class=HTMLResponse)
def confirm_filing(
    case_num: str = Form(""),
    event: str = Form(""),
    docket_text: str = Form(""),
):
    """Final confirmation (step 9)."""
    return HTMLResponse(f"""
    {HEADER}
    <h3>Confirm Filing</h3>
    <div id="confirmationText">
        <table class="confirmation">
            <tr><td>Case:</td><td>{case_num or '1:24-cv-01234'}</td></tr>
            <tr><td>Event:</td><td>Motion to Dismiss</td></tr>
            <tr><td>Document:</td><td>motion.pdf</td></tr>
            <tr><td>Docket Text:</td><td>{docket_text}</td></tr>
        </table>
    </div>
    <form method="post" action="/cgi-bin/submit.pl">
        <input type="hidden" name="case_num" value="{case_num}" />
        <p><b>Click Next to submit your filing.</b></p>
        <input value="Next" type="submit" />
    </form>
    {FOOTER}
    """)


@app.post("/cgi-bin/submit.pl", response_class=HTMLResponse)
@app.get("/cgi-bin/submit.pl", response_class=HTMLResponse)
def submit_filing(case_num: str = Form("")):
    """NEF receipt (step 10)."""
    return HTMLResponse(f"""
    {HEADER}
    <h3>Notice of Electronic Filing</h3>
    <p>Your document has been filed.</p>
    <table>
        <tr><td>Case:</td><td>{case_num or '1:24-cv-01234'}</td></tr>
        <tr><td>Docket #58</td><td>filed 03/27/2026 10:30:00</td></tr>
        <tr><td>Event:</td><td>Motion to Dismiss</td></tr>
    </table>
    <p>Notice sent to all counsel of record.</p>
    {FOOTER}
    """)
