# Human queue

*Rewritten 2026-11-13 (session 7). One list, ordered by what unblocks the
most. A row is here only for money, a signature, Jackson's identity, a
CAPTCHA that truly can't be passed, or a credential that exists nowhere.
Each row says why it is his, the exact click path, and the time.*

Session 7 removed the old rows for DNS + API activation (the API stays
retired until ECFiler has a real signup or paying user), the allow-rules
removal (the operator does it after the NEF), and the VPS reboot (its
post-reboot unit went with the retirement).

| # | What | Why it's Jackson's | Time |
|---|---|---|---|
| 1 | [Register the QA account to e-file, and send the PSC email](#1) | Identity attestation + email in his name | 15 min, then the court's wait |
| 2 | [The attended NEF run](#2) | Typing YES submits to a court under his account | 10 min, after #1 is approved |
| 3 | [Rotate the production PACER password](#3) | Credential | 2 min |
| 4 | [Send C2 and C5](#4) | His name; C5 has a CAPTCHA and needs his phone | 6 min |
| 5 | [Subscribe to GovDelivery](#5) | CAPTCHA | 30 s |
| 6 | [Form the LLC and file the Florida application](#6) | Money + signature | $625, about 45 min |
| 7 | [Counsel review of Terms and Privacy](#7) | Money (a lawyer) | two questions |
| 8 | [Put `ANTHROPIC_API_KEY` on the Mac](#8) | Credential that exists nowhere | 1 min |

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

## 3. Rotate the production PACER password {#3}

<https://pacer.uscourts.gov/my-account-billing/manage-my-account-login> → log in
as jmsanger → Settings → Change Password. Then store it on the Mac:

```
[MAC] printf '%s' 'NEW-PASSWORD' | bash ~/ecfiler/scripts/mac/keychain-setup.sh jmsanger
```

## 4. Send C2 and C5 {#4}

**C2** (2 min): in Gmail, delete the old draft to developers@psc.uscourts.gov
(it is stale). New email from **jackson@sang3r.com** to
developers@psc.uscourts.gov, pasting `docs/outreach/c2-dev-mailbox-email.md`.

**C5** (4 min): <https://www.flmd.uscourts.gov/webforms/contact-cmecf>. The form
now has a CAPTCHA. Answers are in `docs/outreach/c5-submission-sheet.md`; add
your phone number, solve the CAPTCHA, submit.

## 5. Subscribe to GovDelivery {#5}

<https://public.govdelivery.com/accounts/USFEDCOURTS/subscriber/new?topic_id=USFEDCOURTS_1821>
→ email jackson@sang3r.com → solve the MTCaptcha → submit → click the
confirmation link. Do it before C2, so nothing in C2 needs to change.

## 6. Form the LLC and file the Florida application {#6}

No Sunbiz entity named "ECFiler" or "ECF Filer" exists (checked against the
Division's own bulk data, `scripts/sunbiz_name_check.py`; not a reservation).
Entity reasoning: `docs/fl/entity-recommendation.md`.

1. **LLC, $125, 15 min:** <https://search.sunbiz.org/Inquiry/CorporationSearch/ByName>
   → Entity Name "ECFiler" to confirm, then <https://efile.sunbiz.org/llc_file.html>
   → ECFiler LLC, registered agent yourself, principal address your Tampa address.
2. **References, 5 min:** send the three emails in
   `docs/fl/drafts/reference-request-emails.md`.
3. **Application, $500, 30 min once references are in:** print
   `docs/fl/Third_Party_Vendor_Application_FILLED.pdf` (form rev. 01-01-2021,
   still current), add the LLC name, sign pages 4 and 5, check to the payee
   confirmed with the Authority (support@myflcourtaccess.com / 850-577-4609),
   mail to P.O. Box 16428. Checklist: `docs/fl/application-packet-checklist.md`.
   The Authority's board has a work group reviewing vendor "processes and
   fees"; its next meeting is 2026-12-08, so mailing after it costs nothing.

## 7. Counsel review of Terms and Privacy {#7}

`docs/legal/counsel-review-brief.md`, Q1 (UPL) and Q2 (liability stack). Both
pages still carry the "LEGAL REVIEW REQUIRED" note. Session 7 changed Privacy
§7/§8 (no server holds data while the workspace is closed; Resend carries
waitlist emails) and the contact address on both pages (the ecfiler.com
mailboxes no longer exist).

## 8. Put `ANTHROPIC_API_KEY` on the Mac {#8}

Not needed for the NEF (the run takes the pattern-scan path with its waiver
gate). Needed for the AI analysis on the Mac.

```
[MAC] printf 'export ANTHROPIC_API_KEY=%s\n' 'sk-ant-...' > ~/.ecfiler/env.sh && chmod 600 ~/.ecfiler/env.sh
```
