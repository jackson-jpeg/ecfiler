# Entity Recommendation — Florida Third Party Vendor Application

- **Date:** 2026-07-28
- **Question:** what entity, if any, should Jackson form before mailing the Florida
  Courts E-Filing Authority Third Party Vendor application ($500,
  `docs/fl/vendor-application.md`)?
- **Options considered:** single-member Florida LLC · home-state LLC (same thing if
  Jackson is Tampa-based, as the repo consistently states) · Delaware LLC foreign-
  qualified in Florida · wait / apply as an individual.
- **Recommendation: form a single-member Florida LLC — "ECFiler LLC" — now, before
  mailing the application.**

---

## The recommendation, defended

Form **ECFiler LLC**, a single-member Florida LLC, and make it the applicant. The
Authority does not require it — the application form says eligibility runs to
"individuals or entities (including law firms, etc.)" and its page-5 "Status of
Company" section asks only for *a* state and date of incorporation/organization, not a
Florida one (`docs/fl/vendor-application.md`) — but everything about the paperwork reads
better against an entity than against a person. The applicant signs a broad hold-harmless
of the Authority and its contractors, accepts responsibility "under applicable law for
any loss, damage, or injury" arising from use of the Portal, and enters a license whose
terms include revocation after three non-compliance issues in 180 days
(`docs/fl/batch-license-agreement.md` §5). A filing-transport tool that moves other
people's court documents is exactly the kind of product where a $125 liability wrapper is
cheap insurance: if a submission failure ever strands a filer's deadline, the claim should
land on the LLC, not on Jackson's personal assets. The entity also directly serves the
application's hardest gathering requirement — the three financial-stability references —
because it gives Jackson a business bank account, an EIN, and vendor relationships *in the
Firm's name* for the Authority to verify (the declaration explicitly authorizes contacting
"any surety company, bank depository … to verify the statements made in this form").

Florida, not Delaware, and now, not later. Jackson operates from Tampa (every document in
this repo places him and the business there), so a Florida LLC *is* the home-state LLC:
one filing (~$125), one annual report ($138.75), no registered-agent bill if he serves as
his own agent at a Florida street address, and no second state to maintain. A Delaware LLC
would add Delaware's formation fee, a ~$300/year franchise tax, a paid registered agent,
*and* still require Florida foreign qualification (~$125) plus the same Florida annual
report — double the cost and paperwork for benefits (investor familiarity, Chancery
courts) that a solo, unfunded filing tool does not need and can get later by conversion if
a financing ever demands it. Waiting and applying as an individual saves the $125 but
costs more than it saves: Jackson would personally carry the hold-harmless and the
penalty-of-perjury corporate disclosure, the "Status of Company" section would be answered
awkwardly ("individual"), and the bank/processor references would attest to a person, not
a Firm. Against a $500 non-refundable fee and a ~19-engineer-week build
(`docs/fl-certification-gap-analysis.md`), the LLC is the smallest line item in the
project — there is no scenario where skipping it is the right trade.

---

## Name: three candidates

All three must be checked for availability on Sunbiz
(<https://search.sunbiz.org/Inquiry/CorporationSearch/ByName>) before filing — Florida
requires the name to be distinguishable from existing registered entities. In preference
order:

1. **ECFiler LLC** — primary recommendation. Matches the product, the GitHub org, the
   domains, and every public surface; the application's signature block asks for
   "[NAME OF COMPANY]" and the certified-vendor list is published publicly, so the
   entity name *is* the brand on that list.
2. **ECFiler Software LLC** — fallback if "ECFiler LLC" is taken or too close to an
   existing registration; "Software" also does useful UPL work (see below).
3. **ECFiler Technologies LLC** — second fallback, same reasoning.

**UPL optics.** "ECFiler" reads as what it is — software for electronic court filing —
and that is the right side of the line. Florida polices names that imply legal services
by non-lawyers, so under no circumstances should the name contain "legal," "law,"
"paralegal," or "attorney" (a name like "ECFiler Legal Services LLC" would invite exactly
the scrutiny the batch-filing program's own license disclaims — the agreement recites
that timely filing "requires the professional judgment of an attorney,"
`docs/fl/batch-license-agreement.md` §7.c). The certified-vendor list norm is
pure-transport vendors (process servers, filing services), and "ECFiler LLC" sits
comfortably among them. If Sunbiz forces a fallback, "Software"/"Technologies" suffixes
strengthen, not weaken, that posture.

Also worth a five-minute check before committing: a USPTO TESS search and a scan of the
certified-vendor list (`docs/fl/certified-vendor-list.md`) for confusingly similar vendor
names.

## What the application form actually asks (entity requirements)

From `docs/fl/vendor-application.md` (rev. 01-01-2021):

- **Eligibility:** "individuals or entities (including law firms, etc.)" — an entity is
  *optional*, and no Florida domicile requirement appears anywhere in the form.
- **Page 5, "Status of Company":** if a Corporation — state and date of incorporation
  plus officer names; if a Partnership or Joint Venture — equivalents. The form predates
  LLC ubiquity and has no LLC subsection; per the application draft's Note A, an LLC most
  naturally completes the Corporation subsection as "Limited Liability Company, State of
  Florida, organized [DATE]; Managing Member: Jackson Sanger."
- **Corporate History:** years in business under present name (answer honestly:
  "less than one year; newly organized [MONTH YEAR] to hold the ECFiler product" — the
  program has no longevity requirement); affiliates; 5-year litigation/fines; principal
  convictions; current investigations; **three financial-stability references** — all
  under penalty of perjury, with authorization to verify with banks et al.
- **No insurance or bond requirement** anywhere in the application.

Conclusion: the Authority wants *an* answerable corporate disclosure and verifiable
financial standing — any U.S. entity satisfies it; a Florida LLC satisfies it most simply.

## Cost

| Item | Amount | Notes |
|---|---|---|
| FL Articles of Organization (Sunbiz e-file) | **$125** | $100 filing + $25 registered-agent designation |
| Registered agent | $0 | Jackson serves as his own agent (requires a FL street address; it becomes public record — use the business address he is willing to publish) |
| EIN (IRS) | $0 | Online, same-day |
| FL annual report | **$138.75/yr** | Due Jan 1 – May 1 each year; **$400 late fee** if missed — calendar it |
| Optional: certificate of status | $5 | Banks occasionally ask for it |
| *Delaware alternative, for contrast* | ~$110 formation + $300/yr franchise tax + ~$100/yr agent + $125 FL foreign qualification + $138.75/yr FL report | Strictly dominated for this business |

Florida has no state income tax on a single-member LLC's pass-through income. Ongoing
compliance is one annual report and ordinary separateness hygiene.

## Liability isolation — what the LLC does and does not do

**Does:** interposes the entity between Jackson's personal assets and (a) the license's
hold-harmless and "AS IS" allocation, (b) any claim by a customer whose filing is
delayed, deficient, or mis-served through the tool, (c) contract liabilities to the
Authority (monthly fees, cure obligations). For a product whose failure mode is "someone
missed a court deadline," this is the whole point.

**Does not:** shield Jackson from his own perjury exposure on the page-5 declaration —
he signs that personally and it must be literally true regardless of entity form. Nor
does it help if the veil is pierceable: sign everything as "Jackson Sanger, Managing
Member, ECFiler LLC," run all program payments (the $500 fee, the $125/month license
invoices) through the LLC's bank account, and never commingle. A single-member LLC's
veil is only as good as its bookkeeping.

## Banking and references implications

The reference-gathering plan (`docs/fl/drafts/reference-request-emails.md`) depends on
the entity existing *first*:

1. Form ECFiler LLC → obtain EIN → **open the business bank account immediately** — the
   bank reference needs an account to reference, and an account with even a few weeks of
   history beats one opened the day before mailing.
2. Move the Stripe account (and Railway/hosting billing) onto the LLC's name and EIN, so
   the processor and vendor references attest to *the Firm's* standing, matching the
   form's wording ("financial stability of the Firm").
3. Pay the $500 application fee from the LLC account.

## Timeline

| When | Step |
|---|---|
| Day 0 | Sunbiz name check; e-file Articles of Organization ($125) |
| Day 1–5 | Sunbiz processing (typically 2–5 business days for e-filings) |
| Same week | EIN online (same day once the LLC exists) |
| Week 1–2 | Open business bank account; move Stripe/Railway billing to the LLC |
| Week 2–4 | Send reference-request emails; let the bank account age while confirmations come in |
| Week 3–4+ | Complete the application (`docs/fl/drafts/application-draft.md`), mail with the $500 check drawn on the LLC account |

Net: the entity adds roughly **two to three weeks** before the application can be mailed
with references in place — which overlaps work Jackson is doing anyway (the application
package itself) and costs the certification calendar nothing, since the pre-approval
build (`docs/fl-cert-timeline-cost.md` M0–M2) is not gated on mailing date.

---

**Decision needed from Jackson: yes/no on forming "ECFiler LLC" as a single-member
Florida LLC now (~$125 filing, $138.75/yr annual report, Jackson as registered agent),
as the applicant entity for the Florida Third Party Vendor application.**
