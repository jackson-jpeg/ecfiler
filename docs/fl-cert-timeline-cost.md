# ECFiler — Florida TPV Certification Timeline and Cost

- **Date:** 2026-07-27
- **Scope assumed:** the adopted first-application scope — Existing Case path, Circuit
  Civil (CA) + County Civil (CC), multi-document, Correction/Abandoned Queue handling,
  no fee-bearing submissions (`docs/fl-certification-gap-analysis.md` §5).
- **Basis:** build order and effort figures from `docs/fl-certification-gap-analysis.md`
  §6–§7; program mechanics from the captured documents in `docs/fl/` (cited inline).
  Every duration and dollar figure below is either **[program]** (stated in a program
  document) or **[estimate]** (ours). Calendar months are counted from the month the
  application is mailed ("M0"). The single largest unknown — Authority review latency —
  sits between M0 and the start of integration work and can stretch everything after it.

---

## 1. Month-by-month plan

### M0 — Application submission

- Form the entity, gather the three financial references, complete and mail the
  application with the $500 fee (build item #1, 0.5 ew **[estimate]**;
  `docs/fl/drafts/application-draft.md`). Send the process-confirmation email to
  support@myflcourtaccess.com (`docs/fl/drafts/intro-email.md`).
- Cash out: **$500** non-refundable **[program]** (`docs/fl/fee-schedule.md`), plus
  entity formation costs **[Jackson's numbers — Florida LLC filing fee and registered
  agent if used]**.

### M0–M2 — Pre-approval build (overlaps the Authority's review window)

Work that does not require the gated spec (build items #2–#4, ~6.5 ew total
**[estimate]**, `docs/fl-certification-gap-analysis.md` §6):

- **#2 Florida domain model** (`ecfiler/fl/models.py`; extend
  `ecfiler/storage/history.py`) — UCN/clerk case number, division, submission, status
  lifecycle. ~2 ew **[estimate]**.
- **#3 PDF/A enforcement pipeline** — wire `ecfiler/pdf/converter.py` into the
  submission path; 50 MB cap and prohibited-element linting in
  `ecfiler/pdf/validator.py`; filename rules (`docs/fl/technical-specs.md` §4).
  ~1.5 ew **[estimate]**.
- **#4 ECF 4.01 core message layer** (`ecfiler/fl/ecf401.py`) — built against the public
  OASIS 4.01 spec only. ~3 ew **[estimate]**, flagged as partially speculative: Florida's
  extensions are unseen until approval, so some rework here is expected
  (`docs/fl-certification-gap-analysis.md` §6, §9.1).

Meanwhile: **Authority review of the application runs on its own clock. No published SLA
or review timeline exists in any captured program document**
(`docs/fl-certification-gap-analysis.md` §7, §9.6). We show approval landing around M2
below **[estimate — could be faster; could be several months slower; applications are
processed in order received per the 2016 FAQ, `docs/fl/batch-filer-faq.md`]**. Everything
after this point shifts with the actual approval date.

### M2–M4 — Spec in hand; post-approval build

On approval the Authority issues QA Portal credentials and the Portal team provides the
Third Party Vendor and ECF Specification, Florida XSDs/WSDLs, and endpoints — none of
which are public beforehand (`docs/fl/vendor-application.md`, User Credentials;
`docs/fl/technical-specs.md` §9). Build items #5–#8, ~8 ew **[estimate]**:

- **#5 Florida Portal extensions + SOAP transport** (`ecfiler/fl/portal.py`) — adapt the
  ECF core to the actual spec, TLS client config, consume the Batch Interface URL.
  ~3 ew. This is where spec surprises land; the 3 ew assumes the extensions are of
  ordinary complexity **[estimate with wide error bars until the spec is read]**.
- **#6 Status retrieval** (`ecfiler/fl/status.py`) — FilingReviewCompleteResult polling
  loop, durable status store, NEF capture. ~1.5 ew.
- **#7 Correction/Abandoned queue workflow** (`ecfiler/fl/corrections.py`) — deficiency
  ingestion, replace/add lead document, resubmission, 5-business-day aging. ~2 ew.
- **#8 Resiliency layer** (`ecfiler/fl/resilience.py`) — idempotent submission,
  retry/backoff, the Portal's provided error test cases. ~1.5 ew. The error-case catalog
  is also gated, so this item cannot start until the Portal team provides it
  (`docs/fl/technical-specs.md` §9).

### M4 — XML review (emailed)

Before any electronic submission, sample XML for each requested case type and filing path
(Existing Case, CA and CC) is **emailed** to the Authority for human review; electronic
QA testing may begin only after written approval of the samples
(`docs/fl/vendor-application.md`, XML Review / XML Submission). Turnaround is human and
unpublished **[unknown]**; budget 2–4 weeks **[estimate]**.

### M4–M6 — QA Portal execution (the certification matrix, round 1)

Execute the in-scope scenarios per `docs/fl-cert-test-plan.md`: **TS001, TS002, TS005,
TS006 × 8 county CMS targets × 2 divisions ≈ 64 submissions** **[estimate of count;
the scenario/county requirements are program — `docs/fl/test-case-checklist.md`]**.
Realities that set the pace (all **[program]** unless noted):

- Every submission requires a support email with the Submission Number, then Portal
  team/clerk review and county CMS verification before results come back
  (`docs/fl/test-case-checklist.md`, Instructions) — human turnaround per submission.
- **A failure with any single county forces re-running that scenario against all eight
  counties** (`docs/fl/test-case-checklist.md`) — one bad county code list can cost a
  week.
- TS006 embeds a 5-business-day aging wait per pass unless the Portal team accelerates it
  in QA **[open question]** — start TS006 submissions early and let them age in parallel.
- County-specific code lists (Document Group/Type) are collected from the Service Desk as
  we go and captured into `ecfiler/courts/data/fl/` (checklist Submission Requirements
  #3).

Budget for QA execution: 4–8 weeks **[estimate]**, latency-dominated (build item #9,
~3 ew of labor spread across it).

### M6–M7 — TEST environment: end-to-end certification pass

After QA completes, the Authority issues TEST environment credentials; the final
end-to-end test — XML accepted by the Portal and County CMS with status returned to
ECFiler, on **all** requested case types and filing paths — precedes final certification
(`docs/fl/vendor-application.md`, User Credentials / End to End Processing). Assume a
compressed re-run of the matrix (or the subset the Portal team directs) plus fixes:
2–4 weeks **[estimate]**.

### M7–M8 — License execution and certification

- Execute the License Agreement for Authority approval; once approved, certification to
  batch file issues (`docs/fl/vendor-application.md`, Overview of Process). The
  Authority's approval cadence (board action) is unpublished **[unknown]**; budget
  2–6 weeks **[estimate]**.
- Concurrently, build item **#10 production hardening** (~1 ew **[estimate]**):
  monitoring sized to the license's compliance machinery — 20-calendar-day
  root-cause-and-remediate window on any non-compliance notice, revocation at three
  non-compliance issues in 180 days, 60-day forced adaptation to spec changes
  (`docs/fl/batch-license-agreement.md` §2.f, §5) — plus document-volume tracking against
  the monthly fee tiers (§3).

### Net calendar

**Realistic end-to-end: 6–9 months [estimate]** (`docs/fl-certification-gap-analysis.md`
§7), with the composition above. The two accordion joints are the Authority's application
review (M0→M2 shown; genuinely unknown) and QA/TEST human turnaround. The plan degrades
gracefully: nothing in M0–M2 is wasted if approval is slow, because the pre-approval
build fills the wait.

---

## 2. Cash

| Item | Amount | When | Source |
|---|---|---|---|
| Application fee | **$500**, non-refundable | M0 | **[program]** `docs/fl/fee-schedule.md`, `docs/fl/vendor-application.md` |
| Entity formation (if LLC) | `[Jackson — FL filing ~$125–$160 + any registered-agent cost]` | M0 | **[estimate — verify current FL Division of Corporations fees]** |
| Monthly license fee, bottom tier (1–500 documents/month) | **$125/month**, from certification onward | ~M7+ | **[program]** `docs/fl/batch-license-agreement.md` §3, `docs/fl/fee-schedule.md` |
| Higher tiers if volume grows | $150 / $175 / $200 / $250 per month at 501–1,000 / 1,001–10,000 / 10,001–25,000 / >25,000 docs | later | **[program]** `docs/fl/batch-license-agreement.md` §3 |
| Per-filing transaction fee / revenue share | **None exists** | — | **[program]** `docs/fl/fee-schedule.md` |
| Statutory court filing fees | Not applicable under the no-fee-submission scope | — | `docs/fl-certification-gap-analysis.md` §7 |
| Infrastructure (static IP/FQDN host, TLS cert) | `[minor; existing hosting likely absorbs it]` | M0+ | **[estimate]** |

**First-year program cash: ≈ $1,250–$2,000 [estimate]** ($500 + $125 × months certified
within the year — `docs/fl-certification-gap-analysis.md` §7). Invoices are due in 30
days; 60 days unpaid is a revocation trigger (`docs/fl/batch-license-agreement.md` §3) —
put the invoice on autopay-grade process from month one.

Second-application costs (fee-bearing + New Case, later): a new application is required
per added filing path/division (`docs/fl/fee-schedule.md`); whether a second $500 fee is
charged is **presumed but unverified** (`docs/fl/fee-schedule.md`).

---

## 3. Engineering effort

**~19 engineer-weeks total [estimate]**, per the build order in
`docs/fl-certification-gap-analysis.md` §6:

| Phase | Items | Effort (ew) | Gated on |
|---|---|---|---|
| Application package | #1 | 0.5 | — |
| Pre-approval build | #2 domain model, #3 PDF/A pipeline, #4 ECF 4.01 core | 6.5 | — (#4 carries rework risk) |
| Post-approval build | #5 Portal extensions/SOAP, #6 status, #7 queues, #8 resiliency | 8 | Application approval (spec is gated) |
| Certification execution | #9 | 3 (labor, latency-dominated) | QA credentials, XML-review approval |
| Production hardening | #10 | 1 | Certification imminent |

At solo pace with other commitments, ~19 ew is 5–7 calendar months of build effort
before external latency (`docs/fl-certification-gap-analysis.md` §7) — consistent with
the 6–9-month calendar above because build and waiting overlap.

Ongoing, post-certification: the license's 60-day adaptation clause
(`docs/fl/batch-license-agreement.md` §2.f) makes Florida a **standing** engineering
commitment — spec changes must be adapted, tested, and re-certified within 60 days of
notice or certification may be revoked. Budget permanent capacity for it; this is not a
ship-and-forget integration (`docs/fl-certification-gap-analysis.md` §9.3).

---

## 4. Explicit unknowns (things this plan cannot price)

1. **Authority review latency (the big one).** No SLA or review timeline is published
   anywhere in the captured documents; the 2016 FAQ's dates are historical
   (`docs/fl/batch-filer-faq.md`; `docs/fl-certification-gap-analysis.md` §9.6). The
   M2 approval shown above is a placeholder, not a prediction.
2. **Spec surprises.** The Third Party Vendor and ECF Specification, Florida XSDs,
   WSDLs, and the error-case catalog are all gated behind approval
   (`docs/fl/technical-specs.md` §9). The #5 and #8 estimates cannot be firmed until the
   spec is read; the $500 is partly a fee to see it
   (`docs/fl-certification-gap-analysis.md` §9.1).
3. **Checklist currency.** The test checklist is v1.0 (2017); the county list, cc
   recipients, and scenario set may have drifted. Confirm with the Portal team before
   execution (`docs/fl-certification-gap-analysis.md` §9.2).
4. **TS004 deferral.** Whether the fee-waiver scenario can be deferred with the fee
   scenario under a no-fee restriction is unconfirmed; if required, it adds interface
   work and 16 more matrix submissions (`docs/fl-cert-test-plan.md`, TS004).
5. **Polling-only acceptability.** We assume FilingReviewCompleteResult polling alone
   satisfies certification, since the application presents polling and callback as
   alternatives — **assumption**, to be confirmed
   (`docs/fl-certification-gap-analysis.md` §3).
6. **QA/TEST human turnaround.** Every one of the ~64 submissions involves a support
   email, Portal-team/clerk review, and county CMS verification
   (`docs/fl/test-case-checklist.md`); per-submission turnaround is unpublished, and one
   single-county failure re-runs a scenario across all eight counties.
7. **License-execution cadence.** Authority approval of the executed license agreement
   (board action) has no published schedule.
