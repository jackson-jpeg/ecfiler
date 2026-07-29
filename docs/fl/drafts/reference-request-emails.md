# DRAFT — Financial-Reference Request Emails (Florida TPV Application)

*Three sendable emails lining up the three financial-stability references required by
the Third Party Vendor application. Items in `[BRACKETS]` are for Jackson to complete.*

## What the application actually requires

From `docs/fl/vendor-application.md`, page 5, item III.F:

> F. List three (3) references regarding the financial stability of the Firm.

The form asks only for a **list** — name, organization, relationship, phone, email for
each reference. References do not write letters or sign anything. However, the
declaration Jackson signs authorizes the Authority to contact them:

> The undersigned hereby authorize(s) and request(s) any surety company, bank
> depository, contractor, person, firm or corporation to furnish any pertinent
> information requested by the Florida Courts E-Filing Authority ("Authority") deemed
> necessary to verify the statements made in this form or regarding the standing and
> general reputation of the applicant.

So each email below does three things: (1) asks consent to be listed, (2) warns that
the Florida Courts E-Filing Authority may contact them, and (3) confirms they can
speak to the Firm's financial standing if asked. Collect from each: **contact name,
title, organization, phone, email** — that is what goes on the form.

**Sequencing:** send these only after ECFiler LLC exists and the accounts below are in
(or moved into) the LLC's name — see `docs/fl/entity-recommendation.md`. The form's
wording is "financial stability of **the Firm**," so references tied to the entity are
stronger than references tied to Jackson personally.

**Better substitutes, if available:** a CPA/accountant or an established paying client
outranks a SaaS vendor as a financial reference. No CPA relationship is documented in
this repo — if Jackson has one, swap them in for Email 3.

---

## Email 1 — Bank (strongest reference; the declaration names "bank depository" explicitly)

**To:** `[Business banker or branch manager at the bank holding the ECFiler LLC
account. If the account was opened online with no named banker, call or secure-message
the bank first and ask who handles business-account verification requests; address this
email to that person. A named human beats a department inbox on the form.]`

**Subject:** Reference request — ECFiler LLC vendor application, Florida Courts E-Filing Authority

Hello `[NAME]`,

I hold the business account for ECFiler LLC (account ending `[XXXX]`) at your
`[BRANCH/institution]`. I'm applying to the Florida Courts E-Filing Authority — the
public body that operates Florida's court e-filing portal — to become a certified
third-party filing vendor. The application asks me to list three references regarding
the financial stability of the company, and I'd like to list the bank as one of them.

May I list you (name, title, phone, and email) as that reference? Nothing is required
of you up front — the Authority may contact you to verify that the account is in good
standing and that the company's banking relationship is sound, and my application
authorizes the bank to answer such an inquiry. If a different person or department
should be listed for verification requests like this, please point me to them.

Happy to provide anything you need, and thank you.

Best regards,

Jackson Sanger
Managing Member, ECFiler LLC
`[PHONE]` · `[EMAIL]`

> **What this reference needs to be able to state if contacted:** that ECFiler LLC
> holds an account in good standing; how long the relationship has existed; that the
> account has no adverse history (overdrafts/charge-offs); general reputation of the
> accountholder.

---

## Email 2 — Payment processor (Stripe)

**To:** `[Stripe support via the Dashboard (Support → Contact), or the dedicated
account manager if the account has one — most solo accounts do not. Realistically,
Stripe will not take reference phone calls; the useful ask is a written
account-standing confirmation you can attach or cite, plus the correct contact point
to list on the form. If Stripe can't provide either, replace this reference with a
CPA or an established client — see note above.]`

**Subject:** Request: account-standing confirmation for a government vendor application — ECFiler LLC

Hello,

I operate the Stripe account for ECFiler LLC (account `[acct_XXXX / registered
email]`), open since `[MONTH YEAR]`. I'm applying to the Florida Courts E-Filing
Authority, a Florida public body, to be certified as a third-party e-filing vendor.
The application requires three references regarding the financial stability of the
company, and its declaration authorizes the Authority to verify my statements with
firms I do business with.

Two questions:

1. Can Stripe provide a brief written confirmation that the account is in good
   standing — active since `[MONTH YEAR]`, no unresolved disputes, reserves, or
   adverse actions?
2. If the Authority contacts Stripe to verify the account's standing, what contact
   (name or department, phone, email) should I list on the application for that
   inquiry?

Thank you — glad to verify account ownership through whatever process you need.

Best regards,

Jackson Sanger
Managing Member, ECFiler LLC
`[PHONE]` · `[STRIPE ACCOUNT EMAIL]`

> **What this reference needs to be able to state if contacted:** that the ECFiler LLC
> Stripe account is active and in good standing; how long it has processed payments;
> no unresolved disputes, holds, reserves, or adverse actions on the account.

---

## Email 3 — Paid infrastructure vendor (Hostinger)

*An earlier draft used Railway here. That is no longer truthful: the Railway
relationship was a free trial that has expired, and ECFiler's backend now runs on the
Hostinger VPS (`docs/hosting-topology.md`). Hostinger is a real, ongoing **paid**
hosting relationship — currently in Jackson's name, so per the sequencing note above
it belongs on the form only if the account (or a successor account) is in the LLC's
name, or listed transparently as the principal's account hosting the company's
infrastructure. A CPA or established client remains the stronger substitute.*

**To:** `[Hostinger support/billing — ask who can serve as the verification contact
for a government vendor application; a billing/accounts person is ideal. Any
infrastructure vendor with a comparable paid history works the same way.]`

**Subject:** Vendor reference request — ECFiler LLC application to the Florida Courts E-Filing Authority

Hello,

I'm a paying Hostinger customer — the VPS hosting ECFiler's backend has been on
Hostinger since `[MONTH YEAR]` under the account `[ACCOUNT EMAIL]`. I'm applying to
the Florida Courts E-Filing Authority (the public body operating Florida's court
e-filing portal) for certification as a third-party filing vendor, and the
application asks for three references on the financial stability of the company.

May I list Hostinger as a vendor reference? Concretely, that means: the Authority may
contact you to confirm a customer relationship in good standing with a timely payment
history, and my application authorizes you to answer that inquiry. Could you let me
know the right contact (name or department, phone, email) to put on the form for such
a verification request?

Thank you.

Best regards,

Jackson Sanger
Managing Member, ECFiler LLC
`[PHONE]` · `[EMAIL]`

> **What this reference needs to be able to state if contacted:** customer in good
> standing; duration of the relationship; invoices paid on time; no collections or
> payment disputes. **Fill `[MONTH YEAR]` from the actual Hostinger billing history,
> and reconcile the account-name question before listing.**

---

## Checklist before the form is filled in

- [ ] Three confirmed references, each with name, title, organization, phone, email
- [ ] Each reference warned the Florida Courts E-Filing Authority may contact them
      (blocking item #1 in `docs/fl/drafts/application-draft.md`)
- [ ] All referenced accounts are in ECFiler LLC's name (not Jackson's personal name)
- [ ] Written confirmations (e.g., Stripe letter) saved with the retained application copy
