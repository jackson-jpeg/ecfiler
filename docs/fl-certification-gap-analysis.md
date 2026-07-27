# Florida Certified-Vendor (TPV / Batch Filing) Gap Analysis for ECFiler

- **Date:** 2026-07-27
- **Scope of this document:** what it would take to get ECFiler certified as a Third Party Vendor (TPV) for machine-to-machine ("batch") filing through the Florida Courts E-Filing Portal, measured against the current codebase.
- **Sources:** captured extracts of the official program documents in `docs/fl/` (each file carries its source URL): `INDEX.md`, `vendor-application.md`, `batch-license-agreement.md`, `test-case-checklist.md`, `fee-schedule.md`, `batch-filer-faq.md`, `technical-specs.md`, `certified-vendor-list.md`. Claims not traceable to those files are marked **unverified** or **assumption**. Effort and duration numbers are **estimates** unless cited.

---

## 1. Executive summary

**What certification requires.** Florida's program is active (23–24 certified vendors as of the 05/01/2025 list; the license agreement was re-uploaded in March 2026 — `docs/fl/INDEX.md`, `docs/fl/certified-vendor-list.md`). A vendor must: (1) file a Third Party Vendor Application with a non-refundable $500 fee, including corporate disclosure and three financial-stability references under penalty of perjury (`docs/fl/vendor-application.md`); (2) build an OASIS **ECF 4.01 + proprietary Portal extensions** SOAP/XML interface against Florida's XSDs/WSDLs — which are **only provided after application approval** (`docs/fl/vendor-application.md`, `docs/fl/technical-specs.md` §9, `docs/fl/INDEX.md`); (3) pass a staged test sequence — emailed XML review → QA Portal → TEST environment → end-to-end roundtrip through eight distinct county CMS targets, using the TS001–TS009 test scenarios (`docs/fl/vendor-application.md`, `docs/fl/test-case-checklist.md`); (4) execute a license agreement carrying a 60-day forced-adaptation clause for spec changes, 20-day cure windows, and a $125–$250/month tiered license fee (`docs/fl/batch-license-agreement.md`).

**What ECFiler has.** ECFiler today is a federal CM/ECF product. There is **zero** Florida, state-court, OASIS/NIEM, or EFSP code, and no XML/SOAP anywhere in the codebase. What transfers is the document-quality and agent layer: PDF validation (`ecfiler/pdf/validator.py`), a PDF/A converter that exists but is not wired into any pipeline (`ecfiler/pdf/converter.py`), redaction checking (`ecfiler/pdf/redaction_check.py`), exhibit handling (`ecfiler/filing/exhibits.py`), Claude document analysis (`ecfiler/agent/document_analyzer.py`), pre-filing checklists (`ecfiler/filing/checklist.py`), and a SQLite audit trail (`ecfiler/storage/history.py`). The entire transport, envelope, status, correction-queue, and payment layer must be built from nothing.

**Headline numbers (estimates, solo developer with AI assistance):** roughly **14–19 engineer-weeks** of build plus certification-testing labor; cash cost **$500** application fee plus **$125/month** license fee at entry volume; realistic calendar duration **6–9 months** end to end, dominated by Authority review latency, which is **unknown** — no published SLA exists in any program document.

**Recommendation (detail in §5 and §8):** Apply **Florida-first** — do not build a generic OASIS ECF layer speculatively — and request a deliberately narrow first certification: **Existing Case filing path only, Circuit Civil (CA) and County Civil (CC) divisions, multi-document submissions, no fee-bearing submissions, with Correction/Abandoned Queue handling included.** Restricted certifications of exactly this shape are normal and precedented on the official vendor list (`docs/fl/certified-vendor-list.md`). Expand to fee-bearing and New Case via a second application once revenue justifies the payment-settlement build.

---

## 2. Program requirements digest

### 2.1 Application

- **$500.00 non-refundable application fee**, mailed with the application to the Authority's P.O. box in Tallahassee (`docs/fl/vendor-application.md`, `docs/fl/fee-schedule.md`, `docs/fl/batch-filer-faq.md`).
- Eligibility is broad: "individuals or entities (including law firms, etc.)"; several law firms (Morgan & Morgan, Kahane, RAS, Landau) are certified vendors (`docs/fl/vendor-application.md`, `docs/fl/certified-vendor-list.md`).
- **Corporate disclosure** (page 5 of the application): state/date of incorporation and officer names (or partnership/JV equivalents); years in business; subsidiaries/affiliates; regulatory fines, proceedings, or litigation in the past 5 years; whether any principal has a first-degree-misdemeanor or felony conviction; whether currently under investigation; and **three references regarding the financial stability of the firm** — all declared **under penalty of perjury**, with authorization for the Authority to verify with banks/sureties/etc. (`docs/fl/vendor-application.md`).
- **No insurance or bond requirement** appears anywhere in the application (`docs/fl/vendor-application.md`, `docs/fl/INDEX.md`).
- The application itself contains the case-type selection grid (see §2.3) — scope is declared **up front**.
- Applicant acknowledgments include a no-reverse-engineering / no-derivative-works clause and a broad hold-harmless of the Authority and its contractors (`docs/fl/vendor-application.md`).

### 2.2 License terms that bind engineering

From the License Agreement for Third-Party Batch Filing (`docs/fl/batch-license-agreement.md`):

- **§2.f — 60-day forced adaptation.** System Technical Requirements may change over time; the licensee gets **60 days' prior notice** and bears sole responsibility to "adapt, test, and certify its software" to the changes. Failure to conform by the effective date "may result in the immediate revocation" of certification. This is a permanent engineering-capacity commitment, not a one-time build.
- **§3 — monthly license fee tiers** by documents processed per month: 1–500 → **$125**; 501–1,000 → $150; 1,001–10,000 → $175; 10,001–25,000 → $200; over 25,000 → $250. Authority may revise fees on 30 days' notice. Invoices due in 30 days ($25 late charge + interest thereafter); unpaid at 60 days → revocation and termination on 10 days' notice, plus collections (`docs/fl/batch-license-agreement.md`, `docs/fl/fee-schedule.md`).
- **§5 — cure windows and revocation triggers.** Non-compliance in production requires a **root-cause analysis and remediation within 20 calendar days** of notice. Revocation triggers: failure to cure in time; **three or more non-compliance issues within a 180-day period**; failure to pay after final notice. After revocation the vendor must **re-apply through the full application and testing process**. Either party may also terminate without cause on 30 days' notice.
- **§6–7 — no warranty, tight liability cap.** Batch filing is "AS IS"; the Authority's direct-damages liability is capped at "the transaction fees paid for the relevant transactions"; the licensee acknowledges batch filing is "a convenience service" and that **attorneys remain ultimately responsible for timely filing** — product messaging and terms of service must reflect this.
- **No per-filing transaction fee and no revenue share** anywhere in the program documents; the only vendor-side program charges are the $500 application fee and the tiered monthly fee (`docs/fl/fee-schedule.md`).

### 2.3 Certification scope mechanics

- Certification is granted **per filing path (New Case / Existing Case) per division** — the checklist's stated purpose is certification "in a filing path [New Case or Existing Case] and a Division [Circuit Civil, County Civil, Probate, Domestic Relations/Family, Juvenile Dependency, Juvenile Delinquency, Circuit Criminal, Criminal Traffic]" (`docs/fl/test-case-checklist.md`).
- The application's case-type grid lists **16 ECF-case-type / CCIS-court-type combinations** (Citation/TR, Citation/CT, Civil/CA, Civil/CC, Civil/SC, Civil/CP, Civil/GA, Civil/MH, Criminal/CF, Criminal/CO, Criminal/MM, Criminal/MO, Criminal/IN, Domestic/DR, Juvenile/CJ, Juvenile/DP), with columns for **Pleading on Existing Case / Case Initiation / Proposed Orders**; case initiation is "Not Supported" for TR and CF (`docs/fl/vendor-application.md`).
- **Capabilities are certified (and restricted) separately.** The official vendor list shows restriction tiers such as "No submission with fee," "only one document per submission," "No Correction Queue," "No Abandoned Filing Queue" (ProVest carries all four; DreamBuild and TSI Legal carry the first two) — i.e., fee-bearing submissions, multi-document submissions, and queue handling are separately certified capabilities (`docs/fl/certified-vendor-list.md`, `docs/fl/INDEX.md`).
- **Scope expansion requires a new application:** "To obtain certification in an additional filing path or division, a new Application would be required" (per the Request for Certification form, quoted in `docs/fl/fee-schedule.md`; see also `docs/fl/vendor-application.md` notes). Whether a second $500 fee is charged is **presumed but unverified** (`docs/fl/fee-schedule.md` says "presumably").
- **Certification pipeline sequence:** application approved → QA Portal credentials issued → **XML samples emailed** for human review per case type and filing path → approval → electronic submission to the **QA Portal** → **TEST environment** credentials → **end-to-end test** (accepted by Portal, County CMS, and status returned) on **all** requested case types and filing paths → execute license agreement → certification (`docs/fl/vendor-application.md`, `docs/fl/technical-specs.md` §3).
- Certification testing runs each applicable scenario against **eight distinct county CMS targets**: Alachua; Brevard; Duval or Collier; Marion or Walton; Miami-Dade; Orange; Polk; Sarasota or St. Lucie. A failure with any single county requires **re-running that scenario against all counties** (`docs/fl/test-case-checklist.md`).

---

## 3. Gap table

Requirements are drawn from the TPV Test Case Checklist (TS001–TS009) and the technical-interface synthesis (`docs/fl/test-case-checklist.md`, `docs/fl/technical-specs.md`, `docs/fl/vendor-application.md`). "What ECFiler has" reflects the current codebase (federal CM/ECF only; no XML/SOAP anywhere).

| Requirement | What ECFiler has | Gap | Notes |
|---|---|---|---|
| **ECF 4.01 envelope + Portal extensions (SOAP/XML)** — implement/consume web services per the "Third Party Vendor and ECF Specification" and Florida's XSDs (`vendor-application.md`, `technical-specs.md` §1–2) | Nothing. No SOAP, no XML serialization, no ECF code. | **Large** | The single biggest build. Actual XSDs/WSDLs are gated post-approval; only the OASIS 4.01 base spec is public. HTTPS/TLS with CA-issued certs ≥2048-bit required (`technical-specs.md` §1). |
| **TPV Batch Interface consumption** — consume the batch-submission service URL; provide callback URL and IP address (`vendor-application.md`) | Nothing. | **Large** | Requires stable public infrastructure (static IP, FQDN) — an operational requirement, not just code. |
| **Existing Case filing path** (TS001–TS006) — file to an existing UCN/clerk case number | Federal-only case handling; `ecfiler/filing/workflow.py` and `ecfiler/filing/models.py` model CM/ECF filings, not UCN-keyed state cases | **Large** | Concepts (lead document, case number, filing event) map loosely; the data model and transport do not. UCN is a 20-character number (`test-case-checklist.md`). |
| **New Case filing path** (TS007–TS009) — case initiation with 1+ plaintiffs, 1+ defendants, filing fee | `ecfiler/filing/civil_cover_sheet.py` handles federal case-opening paperwork; no party-structured initiation model | **Large** | Requires structured party data (plaintiffs/defendants), fee calculation, and fee-waiver flow. Recommend deferring (§5). |
| **16 case-type grid / division targeting** — court-specific values, Document Group/Type codes per county (`vendor-application.md`, `test-case-checklist.md`) | `ecfiler/courts/registry.py` + `ecfiler/courts/data/*.json` — a federal court registry with per-court metadata; pattern transfers, data does not | **Medium** | Court-specific code lists are not public; the Service Desk provides sample data during testing (`test-case-checklist.md` Submission Requirements #3). Registry architecture is reusable. |
| **Multi-document submissions** — 1+ lead documents plus 0+ exhibits (TS002, TS003, …) | `ecfiler/filing/exhibits.py` models lead-document/exhibit relationships for CM/ECF | **Medium** | Semantics match Florida's lead/exhibit definitions (`test-case-checklist.md` Terms). Needs re-mapping into the ECF message structure, not a rebuild. |
| **Fee-bearing submissions + settlement** (TS003, TS007) — statutory fee settled through the Portal at submission; incorrect fee is a correction-queue trigger (`technical-specs.md` §7) | `ecfiler/filing/fees.py` covers federal fee logic (e.g., pay.gov context); no state fee schedule, no payment rail | **Large** | How a TPV funds statutory fees machine-to-machine (payment account/escrow?) is **not stated in public docs — unverified**. Convenience fees: 3.5% credit card / $5 e-check (`technical-specs.md` §7). Recommend deferring (§5). |
| **Fee waiver flow** (TS004, TS008) | Nothing state-specific | **Medium** | First-class in the interface — dedicated scenarios. If fee-bearing is deferred, whether waiver flow can also be deferred is a scoping question for the Portal team — **open question**. |
| **Correction queue handling** (TS005, TS009) — receive deficiency status; replace first lead doc; add lead doc; change first plaintiff name; add defendant; resubmit | Nothing. No resubmission/amendment semantics anywhere. | **Large** | This is a genuine workflow subsystem: persistent submission state, edit operations against a prior submission, resubmit. Some vendors are certified without it ("No Correction Queue" — `certified-vendor-list.md`), but that tier is weak in practice (deficient filings would strand). |
| **Abandoned queue awareness** (TS006) — uncorrected submissions age out after 5 business days; vendor must retrieve final status | Nothing. | **Small** (given queue plumbing) | Mostly a state machine + status retrieval on top of the correction-queue build; the test deliberately lets a submission age out (`test-case-checklist.md`, `technical-specs.md` §5). |
| **Status retrieval: FilingReviewCompleteResult (polling) and/or NotifyFilingReviewComplete (callback)** — exercised in every scenario (`vendor-application.md`, `technical-specs.md` §2) | `ecfiler/storage/history.py` tracks filing history locally; no polling/callback service | **Large** | Callback option requires hosting an inbound web service (IP, FQDN, URL, HTTP/HTTPS declared to the Portal). Polling-only is simpler for v1 — **assumption:** polling alone satisfies certification, since the application presents the two as alternatives ("The other option would be…"). |
| **PDF/A conformance** — preferred format; permitted elements (bookmarks, e-signatures, internal links, embedded images…) vs prohibited (embedded attachments, comments/annotations, form fields, JavaScript, thumbnails, non-display data, encryption); ≤50 MB per submission; 8.5×11, black-and-white, searchable, 300 DPI OCR minimum; filename character/length rules (`technical-specs.md` §4) | `ecfiler/pdf/validator.py` (pikepdf + PyMuPDF, 100 MB limit); `ecfiler/pdf/converter.py` (PDF/A via ocrmypdf — **CLI-only, not wired into any pipeline**) | **Medium** | Best transfer story in the codebase. Needs: converter wired into the submission path; limit dropped 100→50 MB; a prohibited-element scrubber/linter (annotations, form fields, JS, embedded files) — pikepdf can detect and strip these. Non-conforming docs go to the correction queue (`technical-specs.md` §4). |
| **Rule 2.516 e-service** — Portal performs e-service and issues the NEF (`technical-specs.md` §6, `test-case-checklist.md` Terms) | `ecfiler/agent/certificate_of_service.py` generates prose CoS only — not a machine-readable service list | **Small** | Favorable: unlike CM/ECF prose practice, **the Portal maintains e-service lists and performs service** (AOSC13-49). ECFiler mainly needs to consume/record the NEF. No TPV-specific 2.516 guidance is published — residual **open question**. |
| **8 county CMS targets** — every scenario submitted to all eight; single-county failure → rerun all (`test-case-checklist.md`) | N/A (test-execution requirement, not code) | **Medium** (labor) | Up to 72 test submissions per filing-path/division combination; each submission also emailed to Support (cc'd to a named Portal staffer) with manual clerk verification — expect calendar drag. |
| **QA → TEST → end-to-end sequence** — emailed XML review, QA credentials, TEST credentials, full roundtrip on all requested case types/paths (`vendor-application.md`) | Nothing (no state-side environments concept); `ecfiler/diagnostics.py` exists for the federal stack | **Medium** (labor) | Process gate as much as engineering. QA credentials only issued post-approval, so no integration work can start before the $500 application clears. |
| **Resiliency / error handling** — handle scheduled/unscheduled outages and the provided error test cases; validation logic for preventable and non-preventable failures (`vendor-application.md`) | Retry/recovery exists for browser flows (`ecfiler/browser/recovery.py`) but is CM/ECF-specific | **Medium** | Error-case catalog is not public (`technical-specs.md` §9). Design for idempotent submission + durable queue from the start. |

---

## 4. What transfers from the existing codebase

Verified present on disk; per the baseline these are the transferable assets.

- **`/root/ecfiler/ecfiler/pdf/validator.py`** — pikepdf + PyMuPDF structural validation with a size cap. Transfers directly; change the cap from 100 MB to Florida's 50 MB per submission and add checks for the prohibited PDF/A elements list (annotations, form fields, JavaScript, embedded attachments, encryption) from `docs/fl/technical-specs.md` §4.
- **`/root/ecfiler/ecfiler/pdf/converter.py`** — PDF/A conversion via ocrmypdf. Exists but is CLI-only and not wired into any pipeline; Florida makes PDF/A the preferred format and rasterizes non-searchable PDFs, so wiring this into the submission path is high-value and cheap.
- **`/root/ecfiler/ecfiler/pdf/redaction_check.py`** — regex + Claude confidentiality screening built for federal Rule 5.2. The engine transfers; the rule set must be re-targeted to Fla. R. Gen. Prac. & Jud. Admin. 2.420/2.425, under which **the filer is responsible for confidentiality** (`docs/fl/technical-specs.md` §4). This is a differentiator, not a certification requirement.
- **`/root/ecfiler/ecfiler/filing/exhibits.py`** — lead-document/exhibit modeling; maps onto Florida's lead/exhibit definitions (`docs/fl/test-case-checklist.md`) and supports the multi-document scenarios (TS002 et seq.).
- **`/root/ecfiler/ecfiler/agent/document_analyzer.py`** — Claude-based document extraction; reusable for populating Florida case/party/document metadata from the PDFs themselves.
- **`/root/ecfiler/ecfiler/filing/checklist.py`** — pre-filing checklist engine; reusable as the pre-submission gate (format rules, size, filename constraints, confidentiality notice).
- **`/root/ecfiler/ecfiler/storage/history.py`** — SQLite audit trail; extend to store Submission Numbers, UCNs, per-county status, and NEFs. The license's production-compliance and cure obligations (`docs/fl/batch-license-agreement.md` §5) make a strong audit trail operationally necessary.
- **`/root/ecfiler/ecfiler/courts/registry.py`** and **`/root/ecfiler/ecfiler/courts/data/`** — the registry *pattern* (per-court metadata, code lists, overrides) transfers; the federal data does not. A parallel Florida registry would hold per-county code lists obtained during testing.
- **`/root/ecfiler/ecfiler/agent/certificate_of_service.py`** — partial transfer only; it produces prose CoS, not a machine-readable Rule 2.516 service list. Since the Portal performs e-service and issues the NEF (`docs/fl/technical-specs.md` §6), its role in Florida shrinks to document-text conventions.

**What does not transfer at all:** the browser-automation layer (`ecfiler/browser/*` — CM/ECF is screen-driven; Florida TPV is machine-to-machine SOAP), federal fee logic (`ecfiler/filing/fees.py`), PACER auth/search, and the federal event-code catalogs. There is no SOAP/ECF envelope layer, no e-service list handling, no payment rail, no correction-queue handling, no batch semantics, and no state-court registry — all confirmed absent.

---

## 5. Recommended certification scope for the first application

**Request: Existing Case filing path, Circuit Civil (CA) and County Civil (CC) divisions, multi-document submissions, Correction Queue and Abandoned Filing Queue handling included, no fee-bearing submissions.**

Reasoning, anchored in the vendor-list precedent (`docs/fl/certified-vendor-list.md`):

1. **Restricted certifications are normal.** Of 24 vendors on the 05/01/2025 official list, most are certified only in civil divisions; DreamBuild and TSI Legal are certified Existing Case CA/CC with "No submission with fee, only one document per submission"; ProVest is Existing Case CA with those restrictions plus "No Correction Queue, No Abandoned Filing Queue." A narrow first certification is the established on-ramp, and the Authority plainly grants them.
2. **Existing Case avoids the two hardest builds.** New Case requires structured multi-party initiation data plus fee settlement (TS007–TS009 all involve a filing fee or waiver — `docs/fl/test-case-checklist.md`), and the machine-to-machine statutory-fee funding mechanism is not publicly documented (**unverified**, §3). Existing Case no-fee scenarios (TS001, TS002, TS005, TS006) need neither.
3. **CA + CC is where the market is.** Nearly every vendor holds CA/CC; it covers general civil practice in both circuit and county court. Adding Small Claims (SC) is a plausible cheap third division (several vendors hold CA/CC/SC) but adds test volume; take it only if the Portal team confirms it rides on the same message shapes — **open question**.
4. **Include multi-doc and queue handling, unlike the minimum tier.** `ecfiler/filing/exhibits.py` makes multi-document support cheap, and "one document per submission" is crippling for real filings (motion + exhibits). Correction-queue handling (TS005) is the difference between a demo and a dependable product — a deficient filing a vendor cannot correct machine-to-machine strands the client. Abandoned-queue support (TS006) is nearly free once correction handling exists. This positions ECFiler above the DreamBuild/TSI/ProVest restriction tier on day one while still deferring the two expensive capabilities.
5. **Defer fee-bearing and fee-waiver paths (TS003, TS004) if the Authority permits** — the DreamBuild/TSI "No submission with fee" precedent shows it does. Whether TS004 (fee waiver) can be skipped alongside TS003 is an **open question** to raise with the Portal team at XML-review time.
6. **Expansion is a known, bounded cost:** a new application per added filing path/division (`docs/fl/fee-schedule.md`), presumably with a new $500 fee (**unverified**). Fee-bearing + New Case CA/CC is the natural second application once there is filing volume to justify the payment build.

Certification test volume under this scope (**estimate**): 4 scenarios (TS001, TS002, TS005, TS006) × 8 counties × 2 divisions ≈ **64 test submissions**, plus reruns — the checklist requires re-running a scenario against all eight counties if any one county fails (`docs/fl/test-case-checklist.md`).

---

## 6. Build plan

Assumptions: solo developer with AI assistance; Python stack continuous with the existing codebase; polling (FilingReviewCompleteResult) chosen over the callback service for v1; scope as in §5. All effort figures are **estimates** in engineer-weeks (ew); calendar time will be longer because certification steps serialize on Authority/clerk responses.

| # | Component | Depends on | Effort (ew) |
|---|---|---|---|
| 1 | **Application package** — corporate disclosure, references, case-type grid, $500 fee, mail it (`docs/fl/vendor-application.md`) | — | 0.5 |
| 2 | **Florida domain model** — UCN/clerk case number, division, submission, lead/exhibit structure, status lifecycle (received → review → accepted / correction → abandoned); extend `storage/history.py` for Submission Numbers and per-county state | — (pre-approval work) | 2 |
| 3 | **PDF/A enforcement pipeline** — wire `pdf/converter.py` into the submission path; 50 MB cap; prohibited-element scrub/lint in `pdf/validator.py`; filename rules (`docs/fl/technical-specs.md` §4) | — (pre-approval work) | 1.5 |
| 4 | **ECF 4.01 core message layer** — study the public OASIS 4.01 spec; build ReviewFiling-style request construction and response parsing skeleton against the public schemas | — (pre-approval work, at risk of rework) | 3 |
| 5 | **Florida Portal extensions + SOAP transport** — adapt #4 to the actual "Third Party Vendor and ECF Specification," Florida XSDs/WSDLs, TLS client config; consume the Batch Interface URL | Application approved (spec is gated — `docs/fl/technical-specs.md` §9) | 3 |
| 6 | **Status retrieval** — FilingReviewCompleteResult polling loop, durable status store, NEF capture, notification surface | 5 | 1.5 |
| 7 | **Correction/Abandoned queue workflow** — deficiency ingestion, replace/add lead document operations, resubmission, 5-business-day aging awareness (TS005/TS006 semantics) | 5, 6 | 2 |
| 8 | **Resiliency layer** — idempotent submission, retry/backoff for outages, the Portal's provided error test cases, validation that blocks preventable failures (`docs/fl/vendor-application.md`) | 5 | 1.5 |
| 9 | **Certification execution** — emailed XML samples per case type/path; QA Portal submissions; TEST end-to-end; TS001/TS002/TS005/TS006 × 8 counties × 2 divisions with per-submission support emails; county code-list capture into a Florida registry | 5–8 | 3 (labor, latency-dominated) |
| 10 | **Production hardening** — monitoring for the license's compliance/cure obligations (20-day RCA window, 3-strikes/180-days — `docs/fl/batch-license-agreement.md` §5), invoice/volume tracking against fee tiers | 9 | 1 |

**Total: ~19 engineer-weeks** of scheduled work, of which roughly 6.5 ew (#2–#4) can proceed before application approval. The ECF-core work in #4 carries rework risk since Florida's extensions are unseen — budget the 3 ew there as partially speculative.

---

## 7. Timeline and cost

**Cash costs (from the program documents):**

- Application fee: **$500**, non-refundable (`docs/fl/fee-schedule.md`).
- Monthly license fee once certified: expect the bottom tier, **$125/month** (1–500 documents/month), stepping to $150–$250 with volume (`docs/fl/batch-license-agreement.md` §3). No per-filing transaction fee, no revenue share, no stated renewal fee (`docs/fl/fee-schedule.md`).
- Statutory court filing fees pass through per case and are settled through the Portal — irrelevant at first under a no-fee-submission scope.
- **Estimated first-year program cash: ≈ $1,250–$2,000** ($500 + $125 × months certified) — **estimate**.

**Engineering time:** ~19 ew (**estimate**, §6). At solo-developer pace with other commitments, that is 5–7 calendar months of build effort even before external latency.

**Calendar duration:** realistically **6–9 months** application-to-certification (**estimate**), decomposed as:

- Application mail-in and Authority review: **unknown** — no published SLA or review timeline exists in any captured document; the 2016 FAQ's dates are historical (`docs/fl/batch-filer-faq.md`). Mark this explicitly as the largest unmodeled variable.
- Pre-approval build (#2–#4): can overlap the review window.
- Post-spec build (#5–#8): ~8 ew.
- Certification execution: emailed XML review is a human turnaround per case type/path; each of ~64 QA/TEST submissions involves a support email and manual Portal-team/clerk review and CMS verification (`docs/fl/test-case-checklist.md`); single-county failures force full 8-county reruns. Budget 6–10 weeks calendar (**estimate**).
- License execution and Authority approval of certification: board-action cadence **unknown**.

---

## 8. §3.6 decision: generic OASIS ECF vs Florida-first

**The question.** OASIS ECF underlies e-filing in multiple states (CA/FL/IL/IN/MD/NY/TX/UT per the general ECF-adoption landscape — **assumption**; state list not verified in the captured sources). Should ECFiler build a generic ECF layer now, or a Florida-specific integration?

**Recommendation: Florida-first.** Build the Florida integration with one clean internal seam — keep ECF-4.01-shaped message construction (core case/party/document structures) in a module separate from the Florida-extension and transport code — but do not invest in a state-agnostic abstraction now.

Reasoning:

1. **The Florida wire spec is not generic ECF.** The binding requirement is "the ECF 4.01 Specification **and Portal extensions**," conformance is judged against "**Florida's** associated XSD document," and that spec plus the XSDs/WSDLs are only provided post-application-approval (`docs/fl/vendor-application.md`, `docs/fl/technical-specs.md` §1, §9; `docs/fl/INDEX.md`). A generic layer built today would be built against zero observable targets and then bent to fit the first real one — the classic premature abstraction.
2. **Other states would not reuse it anyway.** Tyler-based states use different profiles and vendor-specific EFM APIs (**assumption** — stated in the task baseline, not verified in the captured sources), so "generic ECF 4.01" buys less cross-state leverage than the standard's name suggests.
3. **Certification, not message construction, is the moat and the cost.** Most of the Florida spend is scope-specific: 8-county testing, queue workflows, county code lists, license obligations. None of that is portable, so the portable fraction of a generic build is small.
4. **The 60-day adaptation clause punishes abstraction overhead.** When Florida changes its spec, ECFiler must adapt within 60 days (`docs/fl/batch-license-agreement.md` §2.f); a thick generic layer between the product and Florida's XSDs makes those forced changes slower, not faster.

**Evidence that would change the answer:** (a) obtaining Florida's actual extension spec and a second state's spec (e.g., a Tyler EFM API doc) and finding substantial structural overlap in case/party/document messages — then promote the internal seam into a real abstraction; (b) a concrete business decision to enter a second ECF state within ~12 months; (c) discovery of a maintained open-source ECF 4.x library worth adopting instead of writing message code (**none evaluated here**).

---

## 9. Risks and open questions

1. **The wire spec is gated behind approval.** The "Third Party Vendor and ECF Specification," Florida XSDs, WSDLs, QA/TEST endpoints, county code lists, and the error-case catalog are all provided only after the $500 application is approved (`docs/fl/technical-specs.md` §9, `docs/fl/INDEX.md`). Effort estimates for #5–#8 in §6 cannot be firmed up until then; the $500 is partly a fee to see the spec.
2. **Dated program documents vs current standards.** The test checklist is v1.0 from 1/21/2017, the FAQ from 7/25/2016, the fee sheet from 02/27/2017 — while the governing technology standards are v4.0, May 2025 (`docs/fl/test-case-checklist.md`, `docs/fl/batch-filer-faq.md`, `docs/fl/fee-schedule.md`, `docs/fl/technical-specs.md`). The 2017 process (named staff cc's, emailed submission numbers) may differ in practice today; the county list and scenario set could have drifted. Confirm the current checklist version with the Portal team early. Mitigating signal: the license agreement was ADA-re-uploaded in March 2026 and the vendor list is actively maintained (`docs/fl/INDEX.md`).
3. **Per-scope recertification.** Every filing-path/division expansion is a new application and test cycle (`docs/fl/fee-schedule.md`), and any spec change triggers the 60-day adapt-test-recertify obligation (`docs/fl/batch-license-agreement.md` §2.f). Florida is a permanent maintenance commitment; a solo operation must budget standing capacity for it, and the 3-strikes/180-day revocation rule (§5.c) makes production incidents existential rather than merely embarrassing.
4. **UPL posture in state court.** The batch-filing license is transport-only; the agreement itself recites that "the timely filing of motions, briefs, and other documents … requires the professional judgment of an attorney" (`docs/fl/batch-license-agreement.md` §7.c). ECFiler's agentic drafting/analysis features sit closer to the unauthorized-practice-of-law line in Florida state court than in the federal pro-se context, and vendor-list precedent shows pure-transport vendors (process servers, filing services) as the norm. How ECFiler's AI features are presented in the application and product is a legal-positioning question outside this document — flag for counsel. **Unverified/assumption** beyond the quoted clause.
5. **Statutory-fee settlement mechanics for TPVs are undocumented publicly.** Payment is "settled at the time the filing is submitted" with card/e-check convenience fees (`docs/fl/technical-specs.md` §7), but how a machine-to-machine vendor funds fees (stored payment account? per-submission tender in the XML?) is unknown until the spec arrives. This supports deferring fee-bearing scope (§5).
6. **Authority review latency is unknown.** No SLA anywhere in the captured documents; the calendar estimate in §7 has wide error bars for this reason.
7. **Open questions to raise with the Portal team** (support@myflcourtaccess.com, 850-577-4609 — `docs/fl/test-case-checklist.md`): current checklist version and county list; whether TS004 (fee waiver) can be deferred with TS003 under a no-fee restriction; whether polling-only (no callback service) is acceptable for certification; whether Small Claims (SC) shares CA/CC message shapes; whether scope-expansion applications incur a second $500 fee; status of conformed-copy return through the interface (discussed in 2022, implementation status not stated — `docs/fl/technical-specs.md` §8).

---

## Bottom line

Apply Florida-first with a narrow Existing Case CA/CC, multi-document, no-fee scope including correction-queue handling; spend $500 and roughly 19 estimated engineer-weeks; expect 6–9 months to certification with the Authority's review latency as the dominant unknown; defer fee-bearing and New Case to a second application; and do not build a generic OASIS ECF layer until a second state is a funded commitment.
