# DRAFT — Cover Letter to Accompany the Third Party Vendor Application

*One page. To be printed on `[ENTITY NAME]` letterhead and mailed with the application and
the $500 fee to Florida Courts E-Filing Authority, P.O. Box 16428, Tallahassee, FL 32317
(`docs/fl/vendor-application.md`). Items in `[BRACKETS]` are for Jackson to complete.*

---

`[DATE]`

Florida Courts E-Filing Authority
P.O. Box 16428
Tallahassee, FL 32317

**Re: Third Party Vendor Application (Batch Filing) — `[ENTITY NAME]` ("ECFiler")**

Dear Members of the Authority:

Enclosed please find the completed Third Party Vendor Application and the $500.00
non-refundable application fee. I am the author of ECFiler, an open-source
filing-preparation tool for federal CM/ECF practice, and the sole principal of
`[ENTITY NAME]`. I work in litigation docketing by profession, and I am based in
Tampa. ECFiler's document pipeline — PDF validation, PDF/A conversion,
confidential-information redaction scanning, lead-document and exhibit handling, and
a per-submission audit trail — is built and exercised by an extensive automated test
suite; I am applying now to obtain the Third Party Vendor and ECF Specification and
begin the XML review and QA testing sequence for a Florida batch-filing interface
built on ECF 4.01 and the Portal extensions.

**Scope requested.** I deliberately request a narrow first certification:

- **Filing path:** Pleading on Existing Case only (no case initiation);
- **Divisions:** Circuit Civil (CA) and County Civil (CC);
- **Capabilities:** multi-document submissions (one or more lead documents with
  exhibits), with Correction Queue and Abandoned Filing Queue handling included;
- **Restriction accepted:** no submissions with a filing fee.

**Why a restricted scope.** The Authority's certified vendor list shows that restricted
certifications of exactly this shape are an established on-ramp: DreamBuild and TSI Legal
are each certified for Existing Case in CA and CC with a "no submission with fee"
restriction; ProVest LLC is certified for Existing Case in CA under similar
restrictions; and Caffeine Code, Inc. is certified for the Existing Case path only, with
no new case initiation. I am asking to enter on that precedented tier — while, unlike
the minimum tier, supporting multi-document submissions and full Correction/Abandoned
Queue handling from day one, because a vendor that cannot correct a deficient filing
machine-to-machine does not serve filers well. I intend to seek fee-bearing and New
Case certification through a subsequent application once this scope is proven in
production.

**Readiness.** I understand certification proceeds through emailed XML review, the QA
Portal, and the TEST environment, culminating in end-to-end roundtrip testing of each
scenario against the eight designated county case maintenance systems. My test plan for
scenarios TS001, TS002, TS005, and TS006 across both requested divisions is prepared,
and I am ready to submit sample XML for review promptly upon receiving the
specification and QA credentials. I will use the FilingReviewCompleteResult polling
service for status retrieval unless the Portal team directs otherwise.

Thank you for your consideration. I can be reached at `[PHONE]` or `[EMAIL]` for any
questions about this application.

Respectfully,

`[SIGNATURE]`

Jackson Sanger
`[TITLE]`, `[ENTITY NAME]`
`[ADDRESS, TAMPA, FL]`

---

<!-- lint:notes -->

*Drafting notes (not part of the letter):*

- *Every program claim above traces to the captured documents: application mechanics and
  fee — `docs/fl/vendor-application.md`, `docs/fl/fee-schedule.md`; vendor precedents
  (DreamBuild, TSI Legal, ProVest, Caffeine Code) — `docs/fl/certified-vendor-list.md`
  (official PDF list dated 05/01/2025); QA/TEST/XML-review sequence and polling service —
  `docs/fl/vendor-application.md`, `docs/fl/technical-specs.md` §2–3; eight-county test
  matrix and TS scenario numbers — `docs/fl/test-case-checklist.md`.*
- *The letter claims only what exists: the federal-side document pipeline is real and
  test-proven (no claim of production operation or of any user); the Florida interface
  is described as the thing being applied-for to build and test, which is the sequence
  the program itself prescribes (spec provided post-approval —
  `docs/fl/technical-specs.md` §9).*
- *Voice is singular throughout — there is one person. The entity signs (`[TITLE]`,
  `[ENTITY NAME]`), but no staff, no "we", and no employer: Jackson's day-job firm is
  never named or alluded to in Authority correspondence.*
