# C5 — Clerk's office inquiry (draft, held for approval)

**Target:** Clerk's Office, U.S. District Court for the Middle District of Florida
(home district — send first; S.D. Fla. optional second, only after M.D. Fla.
responds or 4 weeks pass). Address to the Clerk of Court or the ECF/attorney-services
help desk per the court's website contact page — verify the current addressee at
send time.

**Channel note:** different register from the AO items. This is a local-procedure
question from a local practitioner, not a policy inquiry. Short, concrete, no
attachments, no product name.

---

Dear [Clerk of Court / ECF Help Desk],

I write in a personal capacity. By profession I am a litigation docketing specialist
in Tampa; separately, I build an open-source tool that attorneys and their staff can
run to help prepare filings, and I would like to build it to match what this court
expects. I am not an attorney, and this inquiry is not made on behalf of any employer
or client. I have a question I could not answer from the Administrative Procedures
for Electronic Filing, and I would be grateful for the court's guidance.

The tool is still in development and has not yet completed a filing in any court.
It runs on the filer's own computer. It checks documents before filing (PDF format,
and a scan for personal identifiers that need redaction), walks the filer through a
pre-filing checklist, and fills in the CM/ECF screens for the filer to review. It is
built to submit only through the filer's own CM/ECF login, in their own browser
session, after the person at the keyboard reviews and authorizes that specific
filing. Login credentials are never transmitted to or stored by any outside service,
including mine.

My question: does the court consider this kind of attorney-supervised,
software-assisted preparation and submission to fall within the ordinary use of an
attorney's ECF account by that attorney and their authorized staff? And is there
anything the court would want filers using such tools to do, or to avoid, to stay
squarely within its expectations?

I would rather learn the court's preferences before the tool is finished than have
filers discover them the hard way. If a different office or person is the right one
for this question, I would appreciate a pointer.

Respectfully,

Jackson Sanger
Independent Developer, ECFiler Project
Tampa, Florida
jackson@sang3r.com · github.com/jackson-jpeg/ecfiler

---

<!-- lint:notes -->

### Why the draft is framed this way

- **Identity is truthful, and scoped.** Jackson is in fact a litigation docketing
  specialist in Tampa, and the letter claims that profession because it earns the
  question a serious read. What it deliberately does not do: name or describe the
  employer (a firm that has not consented must not appear in a letter the clerk's
  answer will file next to), use any organizational voice ("our filings", "our
  staff"), tie the inquiry to any employment practice, or claim ECFiler is in use by
  anyone — it has never filed for a client. The first-session draft did all of
  that; the second session over-corrected by deleting the profession entirely;
  this draft states the true profession in personal capacity, which is the stable
  place to land.
- It asks about *how the tool is actually used* (filer-operated, on the filer's
  machine, filer's own login, per-filing authorization) rather than about hypothetical
  autonomy. A "yes, that's ordinary account use" answer is achievable and citable; a
  question about "AI agents" invites a no.
- It volunteers the two facts that matter to a clerk after 2023: no credential
  sharing with any outside service, and a human authorizes each filing.
- It ends by asking what the court wants, which is the posture clerks respond to.
- M.D. Fla. note: verify at send time whether the district's Administrative
  Procedures have an "authorized agent"/staff-use provision to reference by section
  number — cite it if so, stay general if not. (Unverified at draft time.)

### Refresh 2026-11-13 (true as of this date)

- **Address:** `jackson@sang3r.com` replaces the Gmail address (the ecfiler.com
  mailbox no longer exists; no Gmail on outbound correspondence).
- **"still in development and has not yet completed a filing in any court"** added.
  The only live run stopped at the court's permission wall and no NEF exists. The
  old text ("it submits only through...") described the submission step as working;
  it now says what it is *built* to do.
- **"deadline checks" removed.** The code has a pre-filing checklist that asks the
  filer to confirm the deadline (`ecfiler/filing/checklist.py`); it does not compute
  or check deadlines. "Pre-filling filing information" became "fills in the CM/ECF
  screens for the filer to review", which is what `ecfiler/courts/` does.
- **"runs entirely on the filer's own computer" softened to "runs on".** The
  optional AI checks (`ecfiler/claude_client.py`: event-code suggestion, redaction
  scan) send document text to Anthropic under the filer's own API key when one is
  set. The credentials sentence stays, now "Login credentials", which is exactly
  true: no credential leaves the filer's machine, and ECFiler's hosted API is
  offline (the website is frontend-only).
- No em dashes in the letter body.

