# Mail-Out Checklist — Florida TPV Application Packet

One page. Companion to `docs/fl/Third_Party_Vendor_Application_FILLED.pdf` (pre-filled
overlay on the official form, rev. 01-01-2021). Everything typed in black is done;
everything in **gray brackets** on the PDF, and everything below, is yours.

**Checked 2026-11-13** against the Authority's Certified Vendors page
(https://www.myflcourtaccess.com/authority/certified-vendors): the form it links is
an ADA re-upload (2026-05-06) of the same rev. 01-01-2021, identical word for word and
position for position; the filled PDF was regenerated on it and read back
(`tests/test_fl_tpv_fill.py`). Fee still **$500**; P.O. Box unchanged. One open item:
a Board work group is reviewing TPV "processes and fees" (appointed 2026-06-22, no
report yet; next Board meeting 2026-12-08). Sources: `docs/fl/vendor-application.md`,
`docs/fl/fee-schedule.md`.

## Before you print

- [ ] **Re-check the form and the fee the week you mail** (2 min): open
      https://www.myflcourtaccess.com/authority/certified-vendors → "Batch Filing As a
      Third-Party Vendor" → "Batch Filing Application". If the link no longer ends in
      `uploads/2026/05/Third_Party_Vendor_Application_01-01-2021_ADA.pdf`, or "Vendor
      Fees" no longer ends in `uploads/2021/08/Proposed_third_party_fees.pdf`, stop and
      have the packet regenerated (the work group may have changed the form or the fee).

- [ ] **Bertlegs LLC is active** on Sunbiz (effective 01/01/2027; formed by Jackson
      outside this repo). The applicant is **Bertlegs LLC d/b/a ECFiler**
      (`docs/fl/entity-recommendation.md`). Not before 2027-01-01.
- [ ] **Register ECFiler as Bertlegs LLC's fictitious name**: one newspaper notice in the
      county of the principal place of business, then $50 on Sunbiz (s. 865.09, Fla.
      Stat.; the LLC must be active first). HUMAN-QUEUE #7.
- [ ] **Open the business bank account + EIN** — the bank is your strongest financial reference.
- [ ] **Line up three financial-stability references** and warn them the Authority may call
      (`docs/fl/drafts/reference-request-emails.md`). Type up a one-page reference sheet —
      the form's item III.F says "See attached reference sheet."

## Write in by hand (every blank left on the printed form, and why)

| Page | Blank | Why it was left for you |
|---|---|---|
| 1 | Contact Phone # — gray `[phone]` | Personal data not kept in the repo |
| 4 | [NAME OF COMPANY] | Write **Bertlegs LLC d/b/a ECFiler** (left blank because it sits in the signature block) |
| 4 | Signature of Applicant / Date of Application / Printed Name / Title | Your signature and legal assent — never pre-filled |
| 5 §I | Address — gray `[street address]` (Tampa, FL is typed) | Street address not kept in the repo |
| 5 §I | Phone — gray `[phone]` | Same |
| 5 §III.A | Gray `[to complete at mailing]` | "Years in business under present name": answer literally on the mailing date (e.g., "Less than one year. Bertlegs LLC organized effective January 1, 2027; ECFiler registered as its fictitious name on [date].") |
| 5 | Company Name (Bertlegs LLC d/b/a ECFiler) / "Dated this __ day of ____, 20__" / Signature / Title (your title in the Articles) | Signature block — yours alone |

Also confirm personally before signing (page 5 is **under penalty of perjury**):
III.B "None." (Jackson's other projects are product lines of Bertlegs LLC, not affiliated
companies; list any that has its own entity), III.C "None.", III.D "No.", III.E "No." are pre-typed from your instructions — verify each
is literally true on the mailing date. Note: III.C's "None." sits in the left margin
beside item C (the printed question runs to the right edge; there was no inline blank).

## The check

- [ ] **$500.00**, non-refundable application fee.
- [ ] Payee: **Florida Courts E-Filing Authority** (the form directs the fee to the
      Authority but does not print payee wording — call 850-577-4609 or email
      support@myflcourtaccess.com if you want it confirmed before writing the check).
- [ ] Drawn on Bertlegs LLC's business account.

## Enclose

- [ ] Signed cover letter on letterhead (`docs/fl/drafts/cover-letter.md`) — fill its
      `[BRACKETS]` (date, entity name = Bertlegs LLC d/b/a ECFiler, phone, title, address, signature).
- [ ] Completed application, all 5 pages, **both** signature blocks executed (p. 4 and p. 5).
- [ ] Reference sheet (three financial-stability references: name, org, relationship, phone, email).
- [ ] The $500 check.
- [ ] Keep a full copy of the packet.

## Mail

- [ ] Tracked mail to: **Florida Courts E-Filing Authority, P.O. Box 16428, Tallahassee, FL 32317**.
- [ ] Same week: send the intro email (`docs/fl/drafts/intro-email.md`) so the support
      desk can flag the incoming application.

## What the filled PDF already commits you to (typed answers)

Contact: Jackson Sanger / jackson@sang3r.com (pp. 1, 5; changed 2026-11-13 from the
Gmail address, since the Authority's QA credentials and notices go to this mailbox). Status retrieval:
FilingReviewCompleteResult polling; callback table marked N/A (p. 3). Scope: "X" in
**Pleading on Existing Case** for **Circuit Civil (CA)** and **County Civil (CC)** only
(p. 3). Applicant Name (p. 1): Bertlegs LLC d/b/a ECFiler. §II margin note: Bertlegs LLC
d/b/a ECFiler, single-member Florida LLC, organized effective 01/01/2027. §III: B "None.", C "None.",
D "No.", E "No.", F "See attached reference sheet."
