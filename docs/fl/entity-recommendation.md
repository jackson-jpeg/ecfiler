# Entity: Unpossible Studio LLC d/b/a ECFiler (Florida Third Party Vendor application)

- **Decided 2026-11-13 (Jackson, via the lead).** Jackson is forming **Unpossible Studio LLC**, a
  single-member Florida LLC **effective 01/01/2027**, as the umbrella for all his
  projects. ECFiler operates as a **registered fictitious name of Unpossible Studio LLC**, so the
  applicant on every Florida document is **"Unpossible Studio LLC d/b/a ECFiler"**. ECFiler gets
  its own LLC once law firms use it.
- **Name corrected the same day:** the umbrella is **Unpossible Studio LLC**. An
  earlier revision of this packet said Bertlegs LLC; every ECFiler document was switched.
- **Superseded:** the 2026-07-28 recommendation to form "ECFiler LLC" now. Its reasoning
  for an entity over applying as an individual still holds and is kept below; only the
  vehicle changed.
- **Not this repo's job:** forming Unpossible Studio LLC, and the umbrella's website and analytics (a separate session).
  ECFiler's part starts once Unpossible Studio LLC is active on Sunbiz.

---

## What the decision means for the application

| Item | Answer |
|---|---|
| Applicant Name (p. 1) | Unpossible Studio LLC d/b/a ECFiler (filled) |
| Status of Company (p. 5 §II) | margin note: single-member Florida LLC, organized effective 01/01/2027 (filled) |
| Years in business (p. 5 §III.A) | "Less than one year", with the organization and fictitious-name dates (gray blank, completed at mailing) |
| [NAME OF COMPANY] / Company Name (signature blocks, pp. 4 and 5) | Unpossible Studio LLC d/b/a ECFiler, written by Jackson when he signs |
| Title | his title in Unpossible Studio LLC's Articles (e.g. "Authorized Member" or "Manager"); written when he signs |
| References, bank account, $500 check | in Unpossible Studio LLC's name (a d/b/a account lets the bank take payments made out to ECFiler) |

**Order of operations.** The application cannot be mailed before 2027-01-01. Florida
requires an LLC to be registered and **active** with the Division before it can
register a fictitious name (s. 865.09(3)(a)4., Fla. Stat.), so:

1. Unpossible Studio LLC becomes effective, 01/01/2027 (Jackson, outside this repo).
2. Advertise "ECFiler" once in a newspaper in the county of the principal place of
   business (Hillsborough, if that is Tampa), then register the fictitious name on Sunbiz,
   **$50** (s. 865.09(3)(a)5. and (12)(a)). HUMAN-QUEUE #7.
3. EIN for Unpossible Studio LLC, business account (with the d/b/a), references.
4. Mail the application with the $500 check (HUMAN-QUEUE #8). The Authority's
   vendor-fee work group meets 2026-12-08, before any of this can happen anyway.

## Why an entity, and what the umbrella changes

The case for applying as an entity rather than as Jackson personally is unchanged. The
applicant signs a broad hold-harmless of the Authority and its contractors, accepts
responsibility "under applicable law for any loss, damage, or injury" arising from use
of the Portal, and enters a license that can be revoked after three non-compliance issues
in 180 days (`docs/fl/batch-license-agreement.md` §5). A tool that moves other people's
court documents should carry that on an entity, not on Jackson's personal assets. The
entity also serves the application's three financial-stability references: a business
bank account, an EIN and vendor relationships the Authority can verify (the declaration
authorizes contacting "any surety company, bank depository … to verify the statements
made in this form").

**What the umbrella changes, plainly.** A fictitious name is not a separate entity. Any
claim arising from ECFiler is a claim against Unpossible Studio LLC, and so it can reach what
Unpossible Studio LLC holds for Jackson's other projects; the reverse is true too. A separate
ECFiler LLC would have walled that off. That is the trade Jackson chose: one entity, one
annual report and one set of books now, and a separate LLC for ECFiler once law firms use
it, which is when the filing-deadline exposure becomes real. Until then ECFiler files
nothing for anyone but Jackson's own QA account. Keep Unpossible Studio's records clean
(ECFiler's income and costs identifiable, nothing commingled with personal money) so the
later spin-out is a transfer, not an untangling.

**Florida, not Delaware.** Unchanged from July: a Florida LLC is the home-state LLC for a
Tampa operator; Delaware would add a franchise tax, a paid agent and a Florida foreign
qualification for benefits a solo, unfunded business does not need.

## The fictitious name

From s. 865.09, Fla. Stat. (read 2026-11-13 at leg.state.fl.us):

- An LLC doing business under any name other than its legal name must register that
  name first (865.09(3)(a)). Not registering bars Unpossible Studio LLC from suing in Florida
  courts on ECFiler business until it complies, and is a noncriminal violation
  (865.09(9)).
- Registering requires certifying that the name was advertised at least once in a
  newspaper (as defined in chapter 50) in the county of the principal place of business
  (865.09(3)(a)5.). Expect a small newspaper fee on top of the filing fee.
- Fee **$50** (865.09(12)(a)). Valid through December 31 of the fifth calendar year,
  counting the year of registration (865.09(5)), then renewable for 5 years.
- Registration is public notice only. It does not give Unpossible Studio LLC a presumption of
  rights in the name (865.09(8)); trademark is the route for that (see USPTO below).

**Name availability.** The November check below found no Florida entity of record named
ECFiler or ECF Filer. It covers corporations and LLCs, not fictitious-name filings, and
Florida does not refuse a fictitious name because another business registered the same
one. So it is evidence that nobody in Florida trades as "ECFiler" through an entity, not
a reservation.

### Name check: 2026-11-13 (bulk data, not the search page)

**Result: no Florida entity of record is named ECFiler, ECF Filer, or anything that
normalizes to either.** "ECFiler LLC" looks available. The Division confirms
availability only when it accepts the Articles, so this is strong evidence, not a
reservation (Florida has no name reservation for LLCs).

How, exactly:

- **search.sunbiz.org (the name search) refused automated access**: `curl` with an
  ordinary browser User-Agent got HTTP 403 and a Cloudflare "Just a moment..."
  challenge on both `/Inquiry/CorporationSearch/ByName` and a direct `SearchResults`
  URL. OpenCorporates answered with a reCAPTCHA (its API needs a paid token). Neither
  was pushed further: no CAPTCHA solving, no evasion.
- **The Division's own bulk data**, the sanctioned route: the public SFTP server
  whose host and public login are printed on
  https://dos.fl.gov/sunbiz/other-services/data-downloads/ (read 2026-11-13).
  - Quarterly corporate file `doc/Quarterly/Cor/cordata.zip` (dated 2026-10-07,
    1,793,034,019 bytes, 10 members): **12,987,601 records scanned, active and
    inactive** (it carries both: status `A` and `I` both present), every
    corporation, LLC and LP of record.
  - Daily corporate files `doc/cor/20261001c.txt` through `20261112c.txt` (40 files,
    overlapping the quarterly cut-off): **79,126 records scanned**.
  - **Zero hits.** Each name (columns 13-204 of the 1440-character record, per the
    Division's corporate-data-file definitions) was normalized the way Florida
    judges distinguishability (entity designator, punctuation, spaces, a leading
    "THE" and "&"/"and" ignored), then compared with `ECFILER` and `ECFFILER`; any
    name matching `E C F ... FIL` in any spacing was also reported. The matcher was
    shown to fire on planted records ("E.C.F. FILER, L.L.C.", "THE ECFILER COMPANY")
    before the real run. Unrelated names such as "FILER LLC" and "NEXT FILER LLC"
    exist and do not conflict.
  - Reproduce: `scripts/sunbiz_name_check.py` (its header says where the files are).
- **Not covered:** filings made on 2026-11-13 or later, and fictitious-name (d/b/a)
  registrations, which do not block an LLC name in Florida.

**UPL optics.** Unchanged: "ECFiler" reads as software for electronic court filing, and
the name must never carry "legal", "law", "paralegal" or "attorney". "Unpossible Studio LLC d/b/a
ECFiler" keeps that posture. Before relying on the name, a five-minute USPTO trademark
search and a scan of the certified-vendor list (`docs/fl/certified-vendor-list.md`) for
confusingly similar vendors are still worth doing.

## What the application form actually asks (entity requirements)

From `docs/fl/vendor-application.md` (rev. 01-01-2021):

- **Eligibility:** "individuals or entities (including law firms, etc.)" — an entity is
  *optional*, and no Florida domicile requirement appears anywhere in the form.
- **Page 5, "Status of Company":** if a Corporation — state and date of incorporation
  plus officer names; if a Partnership or Joint Venture — equivalents. The form predates
  LLC ubiquity and has no LLC subsection. The filled packet answers it with a margin
  note: "Applicant: Unpossible Studio LLC d/b/a ECFiler, a single-member Florida limited liability
  company, organized effective 01/01/2027. State of organization: Florida."
- **Corporate History:** years in business under present name (answer honestly at
  mailing: "Less than one year. Unpossible Studio LLC was organized effective January 1, 2027, and
  registered ECFiler as its fictitious name on [DATE]." The program has no longevity
  requirement); affiliates; 5-year litigation/fines; principal
  convictions; current investigations; **three financial-stability references** — all
  under penalty of perjury, with authorization to verify with banks et al.
- **No insurance or bond requirement** anywhere in the application.

Conclusion: the Authority wants *an* answerable corporate disclosure and verifiable
financial standing — any U.S. entity satisfies it; a Florida LLC satisfies it most simply.

## Cost (ECFiler's share)

| Item | Amount | Notes |
|---|---|---|
| Unpossible Studio LLC formation and annual report | not ECFiler's line | Jackson's umbrella; $125 to form and $138.75/yr in Florida |
| Fictitious name registration | **$50** | after Unpossible Studio LLC is active; 5 years |
| Newspaper notice | varies | one insertion in the county of the principal place of business |
| Florida TPV application | **$500** | non-refundable |

## Decision

Made. No open question for Jackson in this doc. The queue holds the $50 fictitious-name
filing (after the LLC exists) and the application.
