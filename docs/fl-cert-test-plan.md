# ECFiler — Florida TPV Certification Test Plan (TS001–TS009)

- **Date:** 2026-07-27
- **Maps 1:1 to:** the Third Party Vendor Test Case Checklist v1.0
  (`docs/fl/test-case-checklist.md`, source:
  https://documents.myflcourtaccess.com/uploads/2021/08/TPVTestCaseDocumentation_v1.pdf).
  Scenario names, task steps, and county lists below are taken from that checklist
  verbatim where the checklist gives them.
- **Certification scope this plan executes** (adopted in
  `docs/fl-certification-gap-analysis.md` §5): **Existing Case filing path, Circuit Civil
  (CA) and County Civil (CC) divisions, multi-document, Correction/Abandoned Queue
  included, no fee-bearing submissions.** In-scope scenarios: **TS001, TS002, TS005,
  TS006**, each run in both divisions. Out of scope for this first application: TS003,
  TS004 (fee/fee-waiver) and TS007–TS009 (New Case) — rationale under each below.
- **Caveat:** the checklist is v1.0, dated 1/21/2017. Its process details (cc to a named
  Portal staffer, county list) must be reconfirmed with the Portal team before execution
  (`docs/fl-certification-gap-analysis.md` §9.2). Steps below quote the checklist as
  captured.

---

## 0. Common material

### 0.1 ECFiler components referenced (key)

**Existing today** (federal CM/ECF product; verified on disk per
`docs/fl-certification-gap-analysis.md` §4):

| Component | Path | Role in this plan |
|---|---|---|
| PDF validator | `ecfiler/pdf/validator.py` | Structural PDF checks; to be extended with Florida's 50 MB cap and prohibited-element linting (`docs/fl/technical-specs.md` §4) |
| PDF/A converter | `ecfiler/pdf/converter.py` | ocrmypdf-based PDF/A conversion; currently CLI-only, to be wired into the submission path |
| Redaction scanner | `ecfiler/pdf/redaction_check.py` | Confidentiality screening; rule set to be re-targeted to Fla. R. Gen. Prac. & Jud. Admin. 2.420/2.425 (differentiator, not a certification requirement) |
| Exhibit model | `ecfiler/filing/exhibits.py` | Lead-document/exhibit relationships; matches the checklist's Lead Document / Exhibit definitions |
| Pre-filing checklist engine | `ecfiler/filing/checklist.py` | Pre-submission gate (format, size, filename rules) |
| Audit trail | `ecfiler/storage/history.py` | To be extended with Submission Numbers, UCNs, per-county status, NEF capture |
| Court registry pattern | `ecfiler/courts/registry.py`, `ecfiler/courts/data/` | Pattern reused for a Florida per-county code-list registry |

**To be built** (planned modules; names are the plan of record from the build order in
`docs/fl-certification-gap-analysis.md` §6 — none of this code exists yet):

| Planned component | Planned path | Build item (§6) |
|---|---|---|
| Florida domain model (UCN, division, submission, status lifecycle) | `ecfiler/fl/models.py` | #2 |
| ECF 4.01 core message construction/parsing | `ecfiler/fl/ecf401.py` | #4 |
| Florida Portal extensions + SOAP transport (Batch Interface client) | `ecfiler/fl/portal.py` | #5 |
| Status retrieval — FilingReviewCompleteResult polling loop + durable store | `ecfiler/fl/status.py` | #6 |
| Correction/Abandoned queue workflow (replace/add lead doc, resubmit, aging) | `ecfiler/fl/corrections.py` | #7 |
| Resiliency layer (idempotent submission, retry/backoff, error catalog) | `ecfiler/fl/resilience.py` | #8 |
| Florida county registry data | `ecfiler/courts/data/fl/` | #9 |

### 0.2 The eight-county CMS matrix

Per the checklist's Submission Requirements, every applicable scenario must be executed
against each of these eight county targets, and "If a submission fails to process
properly with one of the Counties, the Test Scenario must be repeated with all the
Counties" (`docs/fl/test-case-checklist.md`):

| # | County target |
|---|---|
| 1 | Alachua County |
| 2 | Brevard County |
| 3 | Duval **or** Collier County |
| 4 | Marion **or** Walton County |
| 5 | Miami-Dade County |
| 6 | Orange County |
| 7 | Polk County |
| 8 | Sarasota **or** St. Lucie County |

Per-scenario results are recorded per county: Submission #, Received Time, Completion
Time, Pass/Fail, Remarks. Where the checklist offers a choice (rows 3, 4, 8), pick one
county per pair and use it consistently; record the choice in the results table.

**Test volume under our scope:** 4 scenarios × 8 counties × 2 divisions (CA, CC) ≈ **64
submissions**, plus reruns forced by any single-county failure
(`docs/fl-certification-gap-analysis.md` §5). Test data (case numbers, UCNs, Document
Group/Type codes) comes from the Service Desk where we lack it (checklist Submission
Requirements #3); every code list received is captured into `ecfiler/courts/data/fl/`.

### 0.3 Common setup (all in-scope scenarios)

1. Application approved; QA Portal credentials in hand (issued only post-approval —
   `docs/fl/vendor-application.md`, User Credentials).
2. Emailed XML review passed for the Existing Case path in CA and CC ("The Applicant
   shall provide a sample XML of each case type and filing path" —
   `docs/fl/vendor-application.md`, XML Review).
3. Per-county test data (UCN/clerk case number, Document Group/Type codes) obtained from
   the Service Desk and loaded into `ecfiler/courts/data/fl/`.
4. Test PDFs prepared and passed through the pipeline: `ecfiler/pdf/converter.py` →
   PDF/A; `ecfiler/pdf/validator.py` → 50 MB cap, no prohibited elements (annotations,
   form fields, JavaScript, embedded attachments, encryption), filename character/length
   rules (`docs/fl/technical-specs.md` §4).
5. `ecfiler/fl/status.py` polling loop running against the QA Portal;
   `ecfiler/storage/history.py` recording every request/response.
6. Each scenario is executed first in QA, then repeated in the TEST environment for the
   end-to-end certification pass (`docs/fl/vendor-application.md`, User Credentials /
   End to End Processing).

### 0.4 Common pass criteria (all in-scope scenarios)

- Portal accepts the submission and returns a Submission Number, recorded in
  `ecfiler/storage/history.py`.
- Clerk verifies the information in the county CMS (Portal-team-confirmed).
- ECFiler retrieves status and review results via FilingReviewCompleteResult polling
  without manual intervention; NEF captured and stored.
- Portal Team returns the completed Test Results section marked **Pass** for all eight
  counties (`docs/fl/test-case-checklist.md`, Instructions).
- Support email with Submission Number sent per checklist step 2 for every submission
  (process step, executed manually; confirm current recipient list with the Portal team —
  the 2017 checklist cc's a named staffer).

---

## TS001 — Existing Case filing path with 1 lead document, no filing fee — **IN SCOPE**

**Objective.** Prove the minimal happy path: one lead document filed to an existing case
(UCN-keyed), no fee, full status roundtrip. This is the first electronic proof that
`ecfiler/fl/ecf401.py` + `ecfiler/fl/portal.py` produce XML the Portal and a county CMS
accept.

**Components under test.** To-be-built: `ecfiler/fl/models.py`, `ecfiler/fl/ecf401.py`,
`ecfiler/fl/portal.py`, `ecfiler/fl/status.py`. Existing: `ecfiler/pdf/converter.py`,
`ecfiler/pdf/validator.py`, `ecfiler/filing/checklist.py`, `ecfiler/storage/history.py`.

**Setup.** Common setup §0.3; one PDF/A lead document per county; valid existing-case
UCN/clerk case number per county (Service Desk data).

**Steps (checklist verbatim, TS001 task table):**

1. TPV Submit — existing case filing with one lead document and no filing fee
2. TPV Completes the Submission Number and sends email with the document attached to Support with a copy to Kyle Reichert *(confirm current cc with Portal team — 2017 document)*
3. Portal Team/Clerk — Review and Accept
4. Clerk — Verify information in CMS
5. TPV Retrieve Status
6. TPV Retrieve Review Results
7. Portal Team Completes Test Results Section and Return to TPV

**Pass criteria.** Common criteria §0.4; additionally, exactly one lead document appears
in the clerk's CMS against the correct case.

**County matrix.** Full 8-county matrix (§0.2), run once per division (CA, CC) = 16
submissions.

---

## TS002 — Existing Case: 1+ lead documents & 1+ exhibit documents, no filing fee — **IN SCOPE**

**Objective.** Prove multi-document submissions: multiple lead documents with exhibits
correctly associated, in one submission. This is the capability that lifts ECFiler above
the "only one document per submission" restriction tier
(`docs/fl/certified-vendor-list.md`; rationale in
`docs/fl-certification-gap-analysis.md` §5.4).

**Components under test.** Existing: `ecfiler/filing/exhibits.py` (lead/exhibit
relationships — the checklist's own Lead Document/Exhibit definitions map onto it),
plus the TS001 set. To-be-built: multi-document envelope construction in
`ecfiler/fl/ecf401.py`.

**Setup.** Common setup §0.3; per county: at least two lead documents and at least one
exhibit attached to a lead document, modeled in `ecfiler/filing/exhibits.py` and
serialized by `ecfiler/fl/ecf401.py`; combined submission size verified < 50 MB by
`ecfiler/pdf/validator.py` (`docs/fl/technical-specs.md` §4).

**Steps (checklist, TS002 task pattern):** TPV Submit; email Submission Number to Support
(cc per current Portal-team instruction); Portal Team/Clerk Review; Clerk Verify in CMS;
TPV Retrieve Review Results; TPV Retrieve Status.

**Pass criteria.** Common criteria §0.4; additionally, every lead document and exhibit
appears in the CMS with the correct lead/exhibit association and ordering.

**County matrix.** Full 8-county matrix × 2 divisions = 16 submissions.

---

## TS003 — Existing Case: 1+ lead documents & 0+ exhibits, with filing fee — **OUT OF SCOPE (first application)**

**Why out.** We are applying with a voluntary "no submission with fee" restriction,
precedented by DreamBuild and TSI Legal on the official 05/01/2025 vendor list
(`docs/fl/certified-vendor-list.md`). The machine-to-machine statutory-fee settlement
mechanism is not publicly documented (`docs/fl-certification-gap-analysis.md` §3, §9.5),
and building the payment rail is one of the two largest deferred builds. Planned for the
second application (fee-bearing + New Case) once volume justifies it
(`docs/fl-certification-gap-analysis.md` §5.6).

**If/when in scope:** would exercise a future `ecfiler/fl/payments.py` against the
Portal's settlement flow (card 3.5% / e-check $5 convenience fees —
`docs/fl/technical-specs.md` §7); steps follow the same 6-step pattern as TS002.

---

## TS004 — Existing Case: 1+ lead documents & 0+ exhibits, fee waiver — **OUT OF SCOPE (first application) — PENDING PORTAL CONFIRMATION**

**Why out.** Deferred together with TS003 under the no-fee restriction. **Open question,
to be raised at XML-review time (and in the intro email):** whether the Authority permits
deferring the fee-waiver scenario alongside the fee scenario — the vendor-list
restriction language says "No submission with fee," which does not unambiguously cover
waivers (`docs/fl-certification-gap-analysis.md` §5.5, §9.7). If the Portal team requires
TS004 for any Existing Case certification, it gets pulled into scope: a fee-waiver
request flag is interface metadata, not a payment rail, so the build cost lands in
`ecfiler/fl/ecf401.py`, not a payments module — re-estimate at that point.

*(Checklist note: the PDF's inner "Name:" field for TS004 mistakenly repeats TS003's
"filing fee" text; the section heading and description — fee waiver — control.
`docs/fl/test-case-checklist.md`.)*

---

## TS005 — Existing Case: 1+ lead documents & 0+ exhibits, no filing fee — Correction Queue — **IN SCOPE**

**Objective.** Prove deficiency handling end to end: receive a correction-queue status,
perform the two prescribed edit operations (replace first lead document; add a new lead
document), resubmit, and reach acceptance. This is the scenario that distinguishes a
dependable product from a demo (`docs/fl-certification-gap-analysis.md` §5.4).

**Components under test.** To-be-built: `ecfiler/fl/corrections.py` (deficiency
ingestion, edit operations against a prior submission, resubmission) — the heart of build
item #7; plus `ecfiler/fl/status.py` (detecting the correction-queue status) and the
TS001 set. Existing: `ecfiler/storage/history.py` (persistent submission state across the
correct-and-resubmit cycle).

**Setup.** Common setup §0.3; original submission prepared as in TS001/TS002; replacement
lead document and an additional new lead document prepared per county. The Portal
Team/Clerk deliberately routes the submission to the correction queue (their step — no
artificial defect needs to be engineered unless the Portal team asks for one).

**Steps (checklist verbatim, TS005 task table):**

1. TPV Submit — Existing Case filing with one or more lead documents and zero or more exhibit documents and no filing fee
2. TPV Completes the Submission Number and sends email with the document attached to Support with a copy to Kyle Reichert *(confirm current cc)*
3. Portal Team/Clerk — Send to correction queue
4. TPV — correction — Replace first lead document
5. TPV — correction — Add a new lead document
6. TPV — Submit corrected filing
7. Portal Team/Clerk — Review
8. Clerk — Verify information in CMS
9. TPV Retrieve Review Results
10. TPV Retrieve Status

**Pass criteria.** Common criteria §0.4; additionally: correction-queue status detected
by polling and surfaced without manual DB inspection; the corrected resubmission carries
the same submission lineage in `ecfiler/storage/history.py` (original → corrected linked);
the replaced document — not the original — and the added document both appear in the CMS;
final status is accepted.

**County matrix.** Full 8-county matrix × 2 divisions = 16 submissions (each involving a
correction roundtrip — budget clerk latency accordingly).

---

## TS006 — Existing Case: 1+ lead documents & 0+ exhibits, no filing fee — Abandoned — **IN SCOPE**

**Objective.** Prove Abandoned Filing Queue awareness: when a correction-queue submission
is deliberately left uncorrected, ECFiler correctly observes the transition to the
Abandoned Filing Queue and records the terminal status. Per the checklist's definitions,
uncorrected submissions move to the Abandoned Filing Queue after five business days
(`docs/fl/test-case-checklist.md`, Terms; `docs/fl/technical-specs.md` §5).

**Components under test.** To-be-built: abandoned-state handling in
`ecfiler/fl/corrections.py` and `ecfiler/fl/models.py` (status lifecycle: received →
review → correction → abandoned) plus `ecfiler/fl/status.py` continuing to poll a
dormant submission. Existing: `ecfiler/storage/history.py` (terminal-state record).
Mostly a state machine on top of the TS005 plumbing
(`docs/fl-certification-gap-analysis.md` §3, "Abandoned queue awareness — Small").

**Setup.** Common setup §0.3; one submission per county as in TS005. **Deliberate
inaction is the test:** after the Portal Team/Clerk sends the submission to the
correction queue, ECFiler takes no corrective action and the submission ages out. Note
in the test calendar: this scenario embeds a 5-business-day wait per pass — schedule it
early and in parallel with other scenarios (aging in the QA/TEST environments may be
accelerated by the Portal team; ask — **open question**).

**Steps (checklist verbatim, TS006 task table):**

1. TPV Submit — Existing Case filing, 1+ lead documents, 0+ exhibits, no filing fee
2. TPV Completes the Submission Number and sends email to Support (cc Kyle Reichert) *(confirm current cc)*
3. Portal Team/Clerk — Send to correction queue
4. TPV — Take no action — no corrections
5. Portal Team/Clerk — Send to Abandoned queue
6. TPV Retrieve Review Results
7. TPV Retrieve Status

**Pass criteria.** Common criteria §0.4 (as applicable — no CMS acceptance occurs in this
scenario); additionally: ECFiler's status record shows the full lifecycle
(submitted → correction queue → abandoned) with timestamps; the abandoned state is
surfaced as a terminal, user-visible outcome, not an error; no spurious resubmission is
attempted by `ecfiler/fl/corrections.py`.

**County matrix.** Full 8-county matrix × 2 divisions = 16 submissions.

---

## TS007 — New Case: 1+ lead documents & 0+ exhibits, with filing fee — **OUT OF SCOPE (first application)**

**Why out.** New Case certification is not requested in this application. All three New
Case scenarios involve a filing fee or fee waiver (`docs/fl/test-case-checklist.md`), so
New Case cannot be certified without the payment/waiver build we are deferring; it also
requires a structured multi-party initiation model (1+ plaintiffs, 1+ defendants) that
does not exist in ECFiler today (`docs/fl-certification-gap-analysis.md` §3, §5.2).
Existing-Case-only certification is precedented (Caffeine Code: "No new case initiation";
DreamBuild, TSI Legal, ProVest: Existing Case only —
`docs/fl/certified-vendor-list.md`). Planned for the second application; scope expansion
requires a new application regardless (`docs/fl/fee-schedule.md`).

---

## TS008 — New Case: 1+ documents & 0+ exhibits, using fee waiver — **OUT OF SCOPE (first application)**

**Why out.** Same rationale as TS007 (New Case path not requested; waiver flow deferred
with the fee build). *(Checklist note: the PDF's inner Name/Description fields for TS008
repeat TS007's "filing fee" text; the section heading, table of contents, and
results-summary table all say fee waiver, which controls —
`docs/fl/test-case-checklist.md`.)*

---

## TS009 — New Case: 1+ lead documents & 0+ exhibits, filing fee — Correction Queue — **OUT OF SCOPE (first application)**

**Why out.** Same rationale as TS007. Noted for the second application's plan: TS009's
correction operations are a superset of TS005's (change name of first
plaintiff/petitioner; add a defendant; replace first lead document; add a new lead
document; resubmit — `docs/fl/test-case-checklist.md`), so the party-edit operations
will extend `ecfiler/fl/corrections.py` rather than requiring a new subsystem.

---

## Results summary (to be completed during certification)

| ID | Scenario | Scope | CA result | CC result |
|---|---|---|---|---|
| TS001 | Existing Case — 1 lead document, no filing fee | IN | — | — |
| TS002 | Existing Case — 1+ lead & 1+ exhibit, no filing fee | IN | — | — |
| TS003 | Existing Case — 1+ lead & 0+ exhibits, filing fee | OUT (no-fee restriction) | n/a | n/a |
| TS004 | Existing Case — 1+ lead & 0+ exhibits, fee waiver | OUT (pending Portal confirmation) | n/a | n/a |
| TS005 | Existing Case — no fee — Correction Queue | IN | — | — |
| TS006 | Existing Case — no fee — Abandoned Filing Queue | IN | — | — |
| TS007 | New Case — filing fee | OUT (New Case not requested) | n/a | n/a |
| TS008 | New Case — fee waiver | OUT (New Case not requested) | n/a | n/a |
| TS009 | New Case — filing fee — Correction Queue | OUT (New Case not requested) | n/a | n/a |

Support contact during testing: support@myflcourtaccess.com, 850-577-4609
(`docs/fl/test-case-checklist.md`).
