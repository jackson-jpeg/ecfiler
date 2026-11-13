# Human queue

*Rewritten 2026-11-13 (session 7); updated the same day after Jackson's answers
(PR #4 merged, the EPA monitor installed, Bertlegs LLC d/b/a ECFiler). One list, ordered by what unblocks the
most. A row is here only for money, a signature, Jackson's identity, a
CAPTCHA that truly can't be passed, or a credential that exists nowhere.
Each row says why it is his, the exact click path, and the time.*

Session 7 removed the old rows for DNS + API activation (the API stays
retired until **the first NEF lands**; Jackson, 2026-11-13), the allow-rules
removal (the operator does it after the NEF), and the VPS reboot (its
post-reboot unit went with the retirement).

| # | What | Why it's Jackson's | Time |
|---|---|---|---|
| 1 | [Register the QA account to e-file, and send the PSC email](#1) | Identity attestation + email in his name | 15 min, then the court's wait |
| 2 | [The attended NEF run](#2) | Typing YES submits to a court under his account | 10 min, after #1 is approved |
| 3 | [Okay the note to the 9 people who signed up](#3) | It goes out in his name | 2 min to read |
| 4 | [Rotate the production PACER password](#4) | Credential | 2 min |
| 5 | [Send C2 and C5](#5) | His name; C5 has a CAPTCHA and needs his phone | 6 min |
| 6 | [Subscribe to GovDelivery](#6) | CAPTCHA | 30 s |
| 7 | [Register ECFiler as Bertlegs LLC's fictitious name](#7) | Money + his certification | $50 + a newspaper notice, 20 min; **after Bertlegs LLC is active (01/01/2027)** |
| 8 | [File the Florida vendor application](#8) | Money + signature | $500, about 35 min; after #7 |
| 9 | [Counsel review of Terms and Privacy](#9) | Money (a lawyer) | two questions |
| 10 | [Put `ANTHROPIC_API_KEY` on the Mac](#10) | Credential that exists nowhere | 1 min |
---

## 1. Register the QA account to e-file, and send the PSC email {#1}

The only thing between ECFiler and its first NEF (ledger L20, re-checked
L27: the account can read the Az Test District Court and cannot file). Filing
is a privilege a court grants to a named person, and the form ends with that
person acknowledging the filer terms. Use the **non-attorney** path: the
runbook used to name the attorney path, which claims a bar admission.
Full research: `docs/qa-efile-registration.md`.

1. `[MAC]` open <https://qa-pacer.psc.uscourts.gov/pscof/manage/maint.jsf> and
   log in as **ecfilercom** (password in the ecfiler keychain).
2. **Maintenance** tab → **Non-Attorney E-File Registration**.
3. Court Type **U.S. District Courts** → Court **Az Test District Court**.
   Role: the most accurate non-attorney role (Party / Pro Se / Interested Party).
   If AZTTDC is not listed: Court Type **U.S. Bankruptcy Courts** → **Az Tc1b
   Bankruptcy Court** (AZTTBK), Role **Creditor**. If no QA court is listed
   under either: submit nothing and go to step 6.
4. Tick that you are the individual registering; name, address, email
   **jackson@sang3r.com**; email notices **on** (the NEF needs them). Next.
   Payment: leave blank (QA is not billable). Next.
5. Read the Non-Attorney E-Filing Terms, acknowledge, **Submit**. Screenshot
   the confirmation. Tell the operator the court and role you picked (or
   that nothing was listed).
6. Send the email in `docs/qa-efile-registration.md` → "Draft request" to
   `pacer@psc.uscourts.gov` from jackson@sang3r.com, filling in the date,
   court and role (or its "nothing listed" sentence).

The operator checks for approval from then on (`session filing-access --qa
--username ecfilercom`). No published turnaround exists; plan on 1 to 2
weeks. Note: PACER now requires a password change every 180 days (since
2026-08-17), and the QA account was registered 2026-07-28.

## 2. The attended NEF run {#2}

After #1 is approved. The sheet is `docs/qa-roundtrip/attended-run.md`. Jackson's
part is one paste in a Mac terminal, defaults at the prompts, **CONFIRM** at the
review table and **YES** at CM/ECF's confirmation screen. The operator does
everything before and after. No server is involved (the July package is on
the Mac and `STAGE=resume` files it).

```
[MAC] cd ~/ecfiler && make qa-day MODE=live STAGE=resume TARGET=https://ecf.tc1d.aztc.uscourts.gov
```

## 3. Okay the note to the 9 people who signed up {#3}

Clerk holds 9 outside ECFiler accounts, all made while the workspace was
closed, and none has been told anything. The note is in
`docs/outreach/c7-signup-prelaunch-note.md`: ECFiler is not open yet, their
account could not do anything, they hear first when filing opens, the free
tools work now, and they can ask for deletion. **Nothing has been sent.**

Hinshaw check: the two law-firm addresses are on `njlawflorida.com` and
`ofjlaw.com`; neither is a Hinshaw domain, so nobody is left out.

Say "send C7" (or send back edits). The operator then sends one message per
person through Resend from `hello@ecfiler.com`, reply-to jackson@sang3r.com, and
logs the ids. Replies come to you.

## 4. Rotate the production PACER password {#4}

<https://pacer.uscourts.gov/my-account-billing/manage-my-account-login> → log in
as jmsanger → Settings → Change Password. Then store it on the Mac:

```
[MAC] printf '%s' 'NEW-PASSWORD' | bash ~/ecfiler/scripts/mac/keychain-setup.sh jmsanger
```

## 5. Send C2 and C5 {#5}

**C2** (2 min): in Gmail, delete the old draft to developers@psc.uscourts.gov
(it is stale). New email from **jackson@sang3r.com** to
developers@psc.uscourts.gov, pasting `docs/outreach/c2-dev-mailbox-email.md`.

**C5** (4 min): <https://www.flmd.uscourts.gov/webforms/contact-cmecf>. The form
now has a CAPTCHA. Answers are in `docs/outreach/c5-submission-sheet.md`; add
your phone number, solve the CAPTCHA, submit.

## 6. Subscribe to GovDelivery {#6}

<https://public.govdelivery.com/accounts/USFEDCOURTS/subscriber/new?topic_id=USFEDCOURTS_1821>
→ email jackson@sang3r.com → solve the MTCaptcha → submit → click the
confirmation link. Do it before C2, so nothing in C2 needs to change.

## 7. Register ECFiler as Bertlegs LLC's fictitious name {#7}

ECFiler operates as a d/b/a of **Bertlegs LLC** (single-member Florida LLC,
effective 01/01/2027; forming it is yours and outside this repo). Florida
requires the LLC to be **active** on Sunbiz first, and the name to be advertised
once in a newspaper in the county of the principal place of business (s. 865.09,
Fla. Stat.). Reasoning: `docs/fl/entity-recommendation.md`.

1. **Newspaper notice:** one insertion of the name "ECFiler" and Bertlegs LLC
   as owner, in a newspaper in your county (Hillsborough, if the business address
   is Tampa). Most papers have a fictitious-name notice form.
2. **Register, $50, 10 min:** Sunbiz → Fictitious Name → File or Renew →
   Fictitious name "ECFiler", owner Bertlegs LLC (its document number), certify the
   notice ran. Valid 5 years.
3. Open the Bertlegs LLC business account with the d/b/a (the bank will ask for
   the registration), then send the three emails in
   `docs/fl/drafts/reference-request-emails.md`.

## 8. File the Florida vendor application {#8}

After #7. **$500, 30 min once the references are in:** print
`docs/fl/Third_Party_Vendor_Application_FILLED.pdf` (form rev. 01-01-2021, still
current; it already reads **Bertlegs LLC d/b/a ECFiler**). Write the company name and
your title in both signature blocks, complete §III.A ("less than one year", with the
dates), sign pages 4 and 5, check drawn on Bertlegs LLC's account to the payee
confirmed with the Authority (support@myflcourtaccess.com / 850-577-4609), mail to
P.O. Box 16428. Checklist: `docs/fl/application-packet-checklist.md`. The
Authority's board has a work group reviewing vendor "processes and fees"; it meets
2026-12-08, before this can be mailed anyway.

## 9. Counsel review of Terms and Privacy {#9}

`docs/legal/counsel-review-brief.md`, Q1 (UPL) and Q2 (liability stack). Both
pages still carry the "LEGAL REVIEW REQUIRED" note. Session 7 changed Privacy
§7/§8 (no server holds data while the workspace is closed; Resend carries
waitlist emails) and the contact address on both pages (the ecfiler.com
mailboxes no longer exist).

## 10. Put `ANTHROPIC_API_KEY` on the Mac {#10}

Not needed for the NEF (the run takes the pattern-scan path with its waiver
gate). Needed for the AI analysis on the Mac.

```
[MAC] printf 'export ANTHROPIC_API_KEY=%s\n' 'sk-ant-...' > ~/.ecfiler/env.sh && chmod 600 ~/.ecfiler/env.sh
```
