# Federal & Florida engagement — contact tracker

One row per touch. Nothing is sent without Jackson's explicit approval of the final
text. Never send the same message to two channels.

| Date | Channel | Contact | Item | Status | Follow-up due | Notes |
|---|---|---|---|---|---|---|
| — | GovDelivery USFEDCOURTS_1821 | (list signup) | C1 subscription | **prepared** — awaiting Jackson | — | steps in c1-registration-steps.md |
| — | QA PACER | qa-pacer.psc.uscourts.gov | C1 test account | **prepared** — awaiting Jackson | +1 business day (activation) | skip credit card |
| — | developers@psc.uscourts.gov | AO developer mailbox | C2 technical questions | **draft** (c2-dev-mailbox-email.md), refreshed 2026-11-13. **The Gmail draft in Jackson's account is stale: do not send it.** Delete it and send the repo text from jackson@sang3r.com | +3 weeks if no reply, one polite nudge, then stop | 3 questions max, no pitch. Gmail draft has the old Gmail From, the "subscribed to the developer updates list" claim, and em dashes |
| — | uscourts.gov EPA Public User Group | (application form when window opens) | C3 membership application | **draft** (c3-epa-application.md) | check announcements weekly from Aug 1, 2026 | window expected ~Aug 2026; last cycle closed Sep 2, 2024 |
| — | M.D. Fla. clerk's office | web form flmd.uscourts.gov/webforms/contact-cmecf | C5 local-rule inquiry | **draft** (c5-clerk-inquiry.md, c5-submission-sheet.md), refreshed 2026-11-13 | +4 weeks if no reply; do not escalate | send only after C2 is out; different register. Form re-read 2026-11-13 (now has a CAPTCHA) |
| — | support@myflcourtaccess.com | FL E-Filing Authority support | B3 intro email | **draft** (see docs/fl/) | +2 weeks | test env access + current cert process |

## Channel discipline

- **Dev mailbox** = technical clarification only.
- **EPA user group** = requirements/feedback membership; practitioner identity.
- **Clerk's office** = local-rule interpretation; the only body that can bless
  agent-assisted filing in its district.
- **FL Authority** = vendor certification process; commercial register is acceptable
  here (it is a vendor program).

## Monitoring

- Weekly (from 2026-08-01): <https://pacer.uscourts.gov/announcements> and
  <https://www.uscourts.gov/court-records/electronic-public-access-public-user-group>
  for the EPA application window.
- GovDelivery list mail: file into a dedicated folder; spec changes get a dated note
  in this tracker.

## Dated notes

- **2026-11-13: contact address.** The ecfiler.com mailbox no longer exists. Every
  outbound item (C2, C5, the FL application and its intro email) uses
  `jackson@sang3r.com`, never a Gmail address.
- **2026-11-13: the C2 Gmail draft is stale.** HUMAN-QUEUE #7 says the Gmail draft
  to developers@psc.uscourts.gov "matches the repo text". It no longer does: the repo
  text was refreshed today (new From and signature, the developer-list subscription
  claim dropped, "lookup feeds" dropped, "still in development" added, no em
  dashes). Replace the Gmail draft with `c2-dev-mailbox-email.md` and send from
  jackson@sang3r.com. The Gmail draft itself was not touched.
- **2026-11-13: still in Gmail form elsewhere.** `c1-answer-sheet.md`,
  `c3-epa-application.md` and `c4-white-paper.md`/`.pdf` still show the Gmail
  address. C1 is account registration (the email is the account login, so it must
  match whatever address the PACER account uses); C3 and C4 were outside this
  refresh and need the same change before they go out.

