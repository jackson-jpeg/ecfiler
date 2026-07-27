# DRAFT — Florida Courts E-Filing Portal Third Party Vendor Application (Batch Filing)

- **Mirrors:** the actual application form, rev. 01-01-2021, field for field and in order
  (`docs/fl/vendor-application.md`, source PDF:
  https://documents.myflcourtaccess.com/uploads/2021/08/Third_Party_Vendor_Application_01-01-2021.pdf).
- **Status:** DRAFT for Jackson's review. Items in `[BRACKETS]` are facts only Jackson can
  supply; each carries a guidance note. Nothing here is submitted anywhere.
- **Submission mechanics:** the completed application plus a **$500.00 non-refundable
  application fee** must be **mailed** (not emailed) to: Florida Courts E-Filing Authority,
  P.O. Box 16428, Tallahassee, FL 32317 (`docs/fl/vendor-application.md`,
  `docs/fl/fee-schedule.md`).
- **Scope requested (adopted per `docs/fl-certification-gap-analysis.md` §5):** Existing
  Case filing path only; Circuit Civil (CA) and County Civil (CC) divisions;
  multi-document submissions; Correction Queue and Abandoned Filing Queue handling
  included; **no fee-bearing submissions** in this first application.

---

## Page 1 — Applicant Contact Information

| Form field | Draft answer |
|---|---|
| Applicant Name | `[ENTITY NAME — see note A]` |
| Contact Name | Jackson Sanger |
| Contact Email | `[BUSINESS EMAIL — see note B]` |
| Contact Phone # | `[PHONE NUMBER]` |

> **Note A — entity.** The application accepts "individuals or entities (including law
> firms, etc.)" (`docs/fl/vendor-application.md`), so Jackson *could* apply as an
> individual. However, page 5's Status of Company section, the license agreement's
> hold-harmless/liability structure (`docs/fl/batch-license-agreement.md` §2, §7), and the
> penalty-of-perjury corporate disclosure all read much more cleanly against an entity.
> **Recommendation: form a Florida LLC (e.g., "ECFiler LLC") before mailing the
> application**, so the entity — not Jackson personally — carries the license obligations
> and the hold-harmless. If the LLC is newly formed, answer the "years in business"
> question honestly (see Corporate History A below) — new entities appear on the certified
> list (the program does not require longevity; no such requirement appears in
> `docs/fl/vendor-application.md`).
>
> **Note B — email.** Use a monitored business address; Portal/Authority notices and QA
> credentials flow through it. The license agreement designates email as a notice channel
> (`docs/fl/batch-license-agreement.md` §8).

---

## Pages 1–2 — Overview of Process, Certification Focus Areas, Business Rules/Requirements, Functional Requirements

These sections of the form are informational (the Authority's text, not applicant
fill-ins) — see `docs/fl/vendor-application.md` for the verbatim text. The applicant's
obligations that flow from them, which this application accepts by signing:

- Use the **ECF 4.01 Specification and Portal extensions**; adhere to Florida's XSDs
  (provided post-approval — `docs/fl/technical-specs.md` §9).
- Consume the Third Party Vendor Batch Interface service URL; **provide a callback URL and
  IP address**; perform an end-to-end test (`docs/fl/vendor-application.md`, Business
  Requirements).
- Complete the staged testing sequence: emailed XML review → QA Portal → TEST environment
  → end-to-end roundtrip (`docs/fl/vendor-application.md`).

**Applicant technical declarations to have ready when the Portal team asks** (these appear
in the form's Filing Status Retrieval section — `docs/fl/vendor-application.md`):

| Item | Draft answer |
|---|---|
| Status retrieval method | **FilingReviewCompleteResult (polling)** — chosen for v1 per `docs/fl-certification-gap-analysis.md` §6; the application presents polling and callback as alternatives. If the Portal team indicates the callback service (NotifyFilingReviewComplete) is required, the four callback fields below apply. |
| IP Address (if callback) | `[STATIC IP of the ECFiler service host — see note C]` |
| Fully Qualified Domain Name (if callback) | `[e.g., portal.ecfiler.com — see note C]` |
| Web Service URL (if callback) | `[HTTPS callback endpoint URL]` |
| HTTP or HTTPS | HTTPS (TLS with CA-issued certificate, ≥2048-bit key, per Florida Courts Technology Standards — `docs/fl/technical-specs.md` §1) |

> **Note C — infrastructure.** Even under polling, the Business Requirements ask for the
> applicant's IP address (`docs/fl/vendor-application.md`). Decide before submission which
> host will originate Portal traffic and pin its static IP/FQDN. This is an operational
> commitment, not just a form field (`docs/fl-certification-gap-analysis.md` §3).

---

## Page 3 — Filing Paths: Case Type Selection Grid

Filled per the adopted scope. Columns as on the form: **Pleading on Existing Case /
Case Initiation / Proposed Orders**. Only the two rows marked REQUESTED are sought;
every other cell is left unrequested.

| ECF Case Type | CCIS Court Type | Pleading on Existing Case | Case Initiation | Proposed Orders |
|---|---|---|---|---|
| Citation | Traffic Infractions (TR) | — | (Not Supported per form) | — |
| Citation | Criminal Traffic (CT) | — | — | — |
| **Civil** | **Circuit Civil (CA)** | **☑ REQUESTED** | ☐ | ☐ |
| **Civil** | **County Civil (CC)** | **☑ REQUESTED** | ☐ | ☐ |
| Civil | Small Claims (SC) | — (see note D) | — | — |
| Civil | Probate (CP) | — | — | — |
| Civil | Guardianship (GA) | — | — | — |
| Civil | Mental Health (MH) | — | — | — |
| Criminal | Felony (CF) | — | (Not Supported per form) | — |
| Criminal | County Ordinance (CO) | — | — | — |
| Criminal | Misdemeanor (MM) | — | — | — |
| Criminal | Municipal Ordinance (MO) | — | — | — |
| Criminal | Non-Criminal Infraction (IN) | — | — | — |
| Domestic | Domestic Relations/Family (DR) | — | — | — |
| Juvenile | Delinquency (CJ) | — | — | — |
| Juvenile | Dependency (DP) | — | — | — |

Requested capability profile (to state in the cover letter and confirm with the Portal
team at XML-review time):

- **Multi-document submissions** (one or more lead documents plus exhibits) — requested,
  supported by ECFiler's existing lead/exhibit handling.
- **Correction Queue and Abandoned Filing Queue handling** — requested (TS005/TS006).
- **No fee-bearing submissions** — restriction voluntarily accepted, matching the
  DreamBuild / TSI Legal precedent on the official vendor list
  (`docs/fl/certified-vendor-list.md`).
- Fee-waiver path (TS004): open question whether it may be deferred alongside fee-bearing
  scope — raise with the Portal team (`docs/fl-certification-gap-analysis.md` §9.7).

> **Note D — Small Claims.** Several vendors hold CA/CC/SC. SC is a plausible cheap third
> division *if* the Portal team confirms it shares CA/CC message shapes, but it adds an
> eight-county test pass per scenario. Default: do not request it now; expansion requires
> a new application either way (`docs/fl/fee-schedule.md`,
> `docs/fl-certification-gap-analysis.md` §5.3).

---

## Page 4 — Acknowledgments and Agreements

The form's acknowledgment text (verbatim in `docs/fl/vendor-application.md`) is accepted
as written. Consequences to understand before signing:

- No copying/scraping/reverse-engineering of Portal components; no product that replicates
  Portal functionality.
- Applicant bears responsibility under applicable law for loss/damage/injury arising from
  authorized use, including unauthorized disclosure of confidential information.
- Broad hold-harmless of the Authority and its Contractors.
- "…there is no guarantee that I will be certified to batch file."

**Signature block (page 4):**

| Field | Draft answer |
|---|---|
| [NAME OF COMPANY] | `[ENTITY NAME — same as page 1]` |
| Signature of Applicant | `[Jackson signs]` |
| Date of Application | `[date mailed]` |
| Printed Name of Applicant | Jackson Sanger |
| Title | `[e.g., "Managing Member" if FL LLC; "Owner" if sole proprietor — must match the entity form chosen in note A]` |

---

## Page 5 — Eligibility / Company Disclosure

> **Everything on this page is declared UNDER PENALTY OF PERJURY**, and the declaration
> authorizes the Authority to verify statements with "any surety company, bank depository,
> contractor, person, firm or corporation" (`docs/fl/vendor-application.md`). Every answer
> must be literally true on the mailing date. No insurance or bond is required anywhere in
> the application (`docs/fl/vendor-application.md`, Notes).

### I. Contact Information

| Field | Draft answer |
|---|---|
| Name | `[ENTITY NAME]` |
| Address | `[BUSINESS ADDRESS — Jackson's Tampa business address; a physical street address is preferable to a P.O. box for a verification-oriented form]` |
| Phone | `[PHONE]` |
| E-mail | `[BUSINESS EMAIL]` |

### II. Status of Company

Complete **one** subsection matching the entity form chosen in note A:

- **If a Corporation:** state and date of incorporation; President's, Vice President's,
  Secretary's, Treasurer's names. `[Only if Jackson incorporates rather than forming an
  LLC. Note: the form predates LLC ubiquity and offers Corporation / Partnership / Joint
  Venture. An LLC most naturally completes the Corporation subsection with
  "Limited Liability Company, State of Florida, organized [DATE]; Managing Member: Jackson
  Sanger" — or ask the Portal team how they want an LLC recorded. Do not leave blank.]`
- **If a Partnership:** state/date of organization; type; partners. `[N/A expected]`
- **If a Joint Venture:** state/date; partners' names/addresses/form. `[N/A expected]`

### III. Corporate History

| Item | Draft answer |
|---|---|
| A. Number of years in business under present name? | `[If newly formed LLC: "Less than one year; newly organized [MONTH YEAR] to hold the ECFiler product. The ECFiler product and its principal's court-filing practice predate the entity." Answer literally; do not inflate.]` |
| B. List all Subsidiary or Affiliated Companies. | `[Presumably "None." Confirm — list any other Jackson entities that would count as affiliates under common ownership.]` |
| C. List any regulatory fine, proceeding, or litigation filed against the Firm in the past five (5) years. | `[Presumably "None." Confirm with Jackson — covers the entity AND, prudently read, its principal's business conduct. If the LLC is new, note the entity has existed only since [DATE] and answer for that period truthfully.]` |
| D. Any principals of the Firm ever been convicted of a first-degree misdemeanor or felony? | `[Presumably "No." Jackson must confirm personally — this is a lifetime question ("ever"), penalty of perjury.]` |
| E. Currently under investigation by any public or private, state or federal law enforcement or regulatory body? | `[Presumably "No." Jackson must confirm as of the mailing date.]` |
| F. List three (3) references regarding the financial stability of the Firm. | `[THREE REFERENCES REQUIRED — see gathering list below.]` |

**What must be gathered before mailing (blocking items):**

1. **Three financial-stability references** — name, organization, relationship, phone,
   email for each. Candidates to line up, in rough order of persuasiveness for a small
   firm: (a) the business's **bank** (branch/relationship manager at the account-holding
   institution — the declaration explicitly contemplates bank verification); (b) the
   firm's **accountant/CPA**; (c) a **commercial landlord, established client, or
   long-standing commercial counterparty** who can speak to payment history. Warn each
   reference that the Florida Courts E-Filing Authority may contact them.
2. **Entity formation papers** (if forming the LLC): Florida Division of Corporations
   filing, EIN, business bank account opened — the bank reference needs an account to
   reference.
3. Jackson's personal confirmations on items C, D, E above.

### Declaration and second signature block

Declaration text is accepted as written (verbatim in `docs/fl/vendor-application.md`).

| Field | Draft answer |
|---|---|
| Company Name | `[ENTITY NAME]` |
| Dated this __ day of ____, 20__ | `[date signed]` |
| Signature | `[Jackson signs]` |
| Title | `[same title as page 4]` |

---

## Mailing checklist

- [ ] Completed application (all five pages), both signature blocks executed
- [ ] $500.00 check `[payable per the form's instruction — confirm payee wording on the
      actual PDF before writing the check; "Florida Courts E-Filing Authority" expected]`
- [ ] Three financial references confirmed and warned
- [ ] Entity formed, EIN + bank account in place (if going the LLC route)
- [ ] Copy of the full package retained
- [ ] Mail (tracked) to: Florida Courts E-Filing Authority, P.O. Box 16428,
      Tallahassee, FL 32317
- [ ] Same-week: send the intro email (`docs/fl/drafts/intro-email.md`) if not already
      sent, so the support desk can flag the incoming application
