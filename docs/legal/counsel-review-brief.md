# Counsel Review Brief — ECFiler Terms of Service & Privacy Policy

*Prepared 2026-07-28 for outside counsel. Purpose: compress review of
`web/app/terms/page.tsx` and `web/app/privacy/page.tsx` (both flagged
"LEGAL REVIEW REQUIRED before deploy", rewritten 2026-07-27 in commit
`163e280`) from a full read to a targeted one. Sections 1–2 are context,
Section 3 is what we are actually paying you to think about, Section 4 is
what you can skim.*

---

## 1. The product model, as it bears on the legal documents

ECFiler has two delivery modes with categorically different risk profiles.
Both documents were rewritten to describe them accurately; the prior
versions described a third mode that no longer exists.

**Hosted web app (ecfiler.com — stage, don't submit).** The hosted product
prepares, validates, and stages filings for the federal CM/ECF system:
PDF/PDF-A validation, Rule 5.2 redaction scanning, AI document analysis,
event-code suggestion, docket-text drafting, fee lookup, and assembly of a
"validated filing package" with guided handoff instructions. **It never
submits anything to a court and never asks for a court password.** The
attorney takes the package and files it on CM/ECF themselves.

**Local CLI (attorney's own machine — the filing happens here).** The
open-source CLI automates the mechanical CM/ECF filing steps via a local
Playwright browser session. PACER/CM-ECF credentials live in the attorney's
OS keyring (service `ecfiler-pacer`) and never leave the device. Submission
requires two typed attorney confirmations, and every filing action is
recorded in an append-only, hash-chained attestation log
(`ecfiler/storage/attestation.py`) with the chain-head hash printed on each
receipt.

**Why the architecture is shaped this way** (full statement:
`docs/credential-architecture.md`): the AO of the U.S. Courts' July 10,
2023 memorandum warned filers against sharing CM/ECF or PACER credentials
with third-party providers. A prior version of ECFiler offered optional
server-side AES-256 credential storage; it was removed and purged in July
2026. **Zero server-side credential custody is now an architectural claim
made in both public legal documents**, so any drift between the documents
and the code is a misrepresentation, not a style issue. Companion policy:
`docs/sealed-document-policy.md` — the hosted service refuses sealed or
restricted content outright (HTTP 403 at upload; enforced in
`ecfiler/api/app.py`), and the CLI hard-fails rather than file sealed
content publicly.

Corporate posture assumed in the documents: Delaware governing law, AAA
arbitration in Wilmington, class-action waiver, $99/attorney/month Pro
tier, 30-day document retention before compressed archival (constants
sourced from `web/lib/facts.ts`).

---

## 2. Redline summary — commit 163e280 (2026-07-27)

Every change moves the documents from the abandoned
"we hold credentials and submit for you" model to the shipped
"zero custody, stage-don't-submit" model. Nothing else of legal substance
changed.

### Terms of Service (`web/app/terms/page.tsx`)

| Section | Old claim | New claim | Reason |
|---|---|---|---|
| Page metadata | "AI-powered federal court **e-filing** platform" | "AI-powered federal court **filing preparation** platform" | Hosted product does not e-file. |
| §2 Nature of the Service | Helps attorneys "prepare **and submit** filings"; ECFiler "**automates** portions of the CM/ECF filing workflow" | "prepare, validate, and **stage** filings … **the attorney reviews and submits every filing**"; ECFiler "assists with portions … and produces a validated filing package **for you to submit**" | Submission is the attorney's act, always. Also narrows UPL surface. |
| §3 Attorney Responsibility | "solely responsible for all filings **made through ECFiler using your PACER credentials**" | "solely responsible for **every filing you submit to CM/ECF** — whether prepared with ECFiler's hosted tools or filed locally through the ECFiler CLI" | Old text implied filings pass through ECFiler; new text covers both real modes. |
| §3 (security bullet) | "responsible for the security of your PACER credentials **and ECFiler account**" | "…your court credentials, **which remain on your own machine and are never held by ECFiler**" | States the custody fact inside the responsibility allocation. |
| §5 3-Pass AI Verification | Analyzes filings "before **submission**" | "before **it is staged for you to submit**" | Verification gates staging, not a submission ECFiler performs. |
| §6 PACER Credentials | "To use the filing features … **you must provide your PACER credentials**" | "The Service **does not collect, store, or transmit** your PACER or CM/ECF credentials" — filing is done by you, directly or via the local CLI with keyring-held credentials | Core rewrite. Old clause described the removed server-side credential store. |
| §7 CM/ECF Availability | "A successful **submission through ECFiler** does not constitute confirmation of filing … until you receive a NEF" | "**A staged filing package is not a filing**; your filing is complete only when you submit it on CM/ECF and receive a NEF" | Eliminates the implication that ECFiler submits; sharpens the completion test. |
| §10 Service Tiers | Free: "limited number of filings per month," basic AI, 90-day history. Pro ($99): "unlimited filings" | Free: validation tools only (PDF checks, redaction scan, 207-court directory, fee lookup, CoS generator, event browser). Pro (`PRO_PRICE`): AI features, staging, guided handoff, history, teams | Old tiers sold filings ECFiler doesn't perform; new lists are the canonical `web/lib/facts.ts` tiers, so Terms and pricing page can't diverge. |
| §11 Acceptable Use | Ban on "automated scripts, bots, or other tools … that exceeds reasonable use" | Ban limited to **abusive/excessive** automation, with an express carve-out: ECFiler's own court-facing automation uses a disclosed user agent, honors court guidance and rate limits, "and ordinary use of the ECFiler CLI is not prohibited by this clause" | The blanket bot ban contradicted the product's own CLI. |

### Privacy Policy (`web/app/privacy/page.tsx`)

| Section | Old claim | New claim | Reason |
|---|---|---|---|
| Page metadata | Covers "PACER credentials, filing documents, and usage information" | "Court credentials **never reach our servers**" | No credential collection to disclose. |
| §1 Information We Collect | "**PACER username and password** — provided by you … encrypted at rest" | "**None.** We do not collect your PACER or CM/ECF username or password" — credentials stay in the OS keyring on the user's machine | The collected-data inventory must not list data we don't collect. |
| §2 (retitled "PACER Credential Storage" → "Court Credentials") | AES-256 at rest; "decrypted only at the moment of filing"; separate key storage; TLS to CM/ECF | "We do not collect, store, transmit, or have access to" credentials — "an architectural guarantee, not just a policy" — plus a **Legacy note**: server-stored credentials from the old model "were permanently purged in July 2026" | The entire old section described the removed store. Legacy note added for honesty toward pre-purge users. **See Q4 below.** |
| §3 Filing Document Retention | "filed within the last 30 days" | "uploaded within the last {RETENTION_DAYS} days"; new bullet: "**Sealed or restricted documents are never accepted** by the hosted Service and therefore are never stored in any form" | "Filed" → "uploaded" (hosted product doesn't file); retention constant now sourced from `facts.ts`. |
| §4 Sealed Documents | Sealed PDFs "held in memory only for the duration of the filing transaction," purged after submission | "The hosted Service **does not accept sealed or restricted documents at all**" — refused at upload before any content is stored; CLI hard-fails rather than file sealed content publicly | Old text described a sealed-handling mode that would itself violate the AO guidance; new text matches `docs/sealed-document-policy.md` and the 403 enforcement in `ecfiler/api/app.py`. |
| §6 Analytics | Tools don't collect "…case data, **or PACER credentials**" | Same sentence minus the credential mention | No credentials exist anywhere to disclaim. |
| §7 Infrastructure | TLS "between ECFiler and CM/ECF"; "data at rest is encrypted using AES-256 (see Section 2 …)" | "ECFiler's **servers do not communicate with CM/ECF** and never hold court credentials"; at-rest claim softened to "industry-standard encryption" | Servers have no CM/ECF connection; the AES-256 pointer targeted the deleted credential section. |
| §8 Third-Party Data Sharing | First recipient listed: "**CM/ECF** — your PACER credentials and filing documents are transmitted to the federal court's CM/ECF system when you submit a filing" | Bullet deleted; recipients are Clerk, Vercel/Railway (as processors), and legal compliance | The hosted service transmits nothing to courts. |
| §11 Account & Data Deletion | "Your PACER credentials are immediately and permanently deleted" | "**No court credentials need to be deleted — we never had them**" | Consistency with §2. |

---

## 3. Questions that actually need a lawyer

### Q1 — UPL exposure: non-lawyer-owned tool that suggests event codes and drafts docket text

**The question.** Do the AI features (event-code suggestion, docket-text
generation, deficiency scoring, certificate-of-service drafting) as
described in Terms §§2, 4, 5 stay on the "scrivener/software tool" side of
the unauthorized-practice line, given that ECFiler is not attorney-owned,
and is the Terms §2 disclaimer ("ECFiler is not a law firm, does not
practice law, and does not provide legal advice … No attorney-client
relationship is created") adequate for that purpose?

**Why it needs counsel.** UPL is state-by-state and fact-driven; software
that *selects* a docketing event (which fixes deadlines and fees) is closer
to judgment than form-filling. This is professional-judgment territory, not
drafting.

**Our current position.** Every judgment-adjacent output has a mandatory
human checkpoint, inventoried in `docs/credential-architecture.md` §6: the
software always presents multiple candidate events and never auto-picks;
docket text is editable and approved verbatim at the attestation gate; fee
status is never inferred; the product is marketed exclusively to licensed
attorneys (Privacy intro; Terms §2). Our theory is Rule 5.3-style
supervision: the attorney operates the tool.

**What turns on the answer.** Whether any feature must be disabled,
re-labeled, or moved behind additional confirmation; whether the Terms need
state-specific UPL language; whether "assists your professional judgment,
not a replacement for it" (Terms §2) is sufficient or needs strengthening
before the Florida certification effort (see `docs/fl/`) invites regulator
attention.

### Q2 — Disclaimer sufficiency and liability allocation for stage-don't-submit failures

**The question.** When a court rejects a filing that ECFiler staged and
"passed" through 3-pass verification — or an attorney relying on a staged
package misses a deadline — does the stack of Terms §5 ("a 'passed'
verification does not constitute legal advice or a representation that the
filing complies with all applicable rules"), §7 ("A staged filing package
is not a filing"), and §8 (damages exclusion naming "REJECTED FILINGS …
MISSED DEADLINES, COURT SANCTIONS, MALPRACTICE CLAIMS"; cap at greater of
12-month fees or $100) actually hold? Is a $100 floor defensible for a $99/
month product whose failure mode is a malpractice event?

**Why it needs counsel.** Enforceability of consequential-damage waivers
and low caps against gross-negligence or failure-of-essential-purpose
arguments is jurisdiction-sensitive judgment; so is whether the disclaimers
are conspicuous enough (they are amber callout boxes, not all-caps, except
§8).

**Our current position.** Ship the current language; the architecture backs
it (the attorney performs the Rule 11 act, twice-confirmed, attested).

**What turns on the answer.** Whether §8 needs a carve-out structure or a
higher cap; whether the §5 verification disclaimers should also appear
in-product at the moment a "passed" result is displayed, not only in the
Terms; insurance requirements.

### Q3 — RESOLVED in engineering (2026-07-28): hash-don't-store. Confirm the disclosure language only.

**What the question was.** Privacy §11's deletion promise conflicted with an
append-only attestation store that held `user_id`, `attestor_name`, full
filing payloads (case numbers, parties, docket text), and NEF text —
undeletable by design.

**What we did.** Restructured the store
(`ecfiler/storage/attestation.py`): case payloads and NEF text now live in a
separate, deletable table (`attestation_payloads`) beside the chain, keyed by
record and salted per record. The chain records themselves keep only salted
hashes plus attestor name, attestation language, timestamps, and the internal
account identifier. `DELETE /api/account` (implemented, tested —
`tests/test_account_lifecycle.py`) deletes filing history, documents, staged
packages, and the attestation payloads *including their salts*, so the
remaining hashes cannot be brute-forced back to case data. The chain still
verifies end to end after deletion (`tests/test_attestation.py::TestHashDontStore`).
Privacy §11 now discloses the narrow remainder expressly (attestor name,
attestation text, timestamps, account identifier, content-free hashes,
retained indefinitely as integrity records).

**What still needs counsel (reduced scope).** Only whether the §11
disclosure of the retained attestation-record remainder is adequate under
CCPA — i.e., whether retaining attestor name + account identifier
indefinitely as an integrity record fits a CCPA exception or needs consent
language. The case-data conflict is gone.

### Q4 — RESOLVED in engineering (2026-07-28): the copy now describes what exists.

**What the question was.** The policy asserted (a) a completed July-2026
credential purge whose record was blank, and (b) self-serve deletion and
machine-readable export that had no endpoints.

**What we did.** (a) The purge record in
`docs/credential-architecture.md` §4 is now complete — the honest version:
the purge-bearing build was never deployed; the legacy Railway environment
is dead (edge 404, observed 2026-07-27/28); the trial expired and Railway
destroys trial volumes 30 days after credit expiry; the encryption key dies
with the workspace. Privacy §2's legacy note was rewritten to claim only
what is true: the capability was **removed** and the environment
**decommissioned** — no "permanently purged" claim. (b) `GET /api/export`
and `DELETE /api/account` exist, are wired to the settings page (export
download + two-step delete), and are tested. §3/§9/§11 were redrafted to
match: deletion is immediate, per-document deletion is not promised
(whole-history deletion is what exists), and login-account removal is
correctly attributed to the auth provider's account portal.

**What still needs counsel (reduced scope).** Confirm the rewritten §2
legacy note before the review banner comes off. Terms §13 was re-checked
2026-07-28: its 30-day post-termination export window is an operator-conduct
commitment (we refrain from deleting for 30 days after *we* terminate an
account) and the export endpoint it presumes now exists, so it stands as
written.

---

## 4. Boilerplate — skim only

Standard clauses needing no meaningful attention beyond confirming they
exist and read normally:

**Terms of Service**

- **§1 Acceptance of Terms** — standard 18+/authority-to-bind recital.
- **§4 AI-Generated Content** — conventional AI-assist disclaimer (outputs may err; human must review); consistent with §5 and the UPL posture in Q1 but not independently novel.
- **§9 Indemnification** — standard user-indemnifies-provider list (use, filings, violations, third-party disputes); one-way, market-typical for a B2B tool.
- **§12 Intellectual Property** — user keeps uploaded content, provider keeps platform, limited license grant; entirely standard.
- **§13 Account Termination** — mutual termination with notice, 30-day export window; standard SaaS (the export *mechanism* is a Q4 item, the clause itself is boilerplate).
- **§14 Dispute Resolution** — 30-day informal-resolution period, AAA Commercial Rules, single arbitrator in Wilmington, class-action waiver; the standard post-*Concepcion* stack.
- **§15 Governing Law** — Delaware law, Wilmington forum; standard and consistent with §14.
- **§16 Changes to These Terms** — 14-day advance notice for material changes with examples; standard change-of-terms clause.
- **§17 Contact** — legal@ecfiler.com.

**Privacy Policy**

- **§5 Authentication** — accurate description of Clerk as auth processor with links to Clerk's policy; standard delegated-auth disclosure.
- **§6 Analytics & Performance** — Vercel Analytics/Speed Insights, cookieless, no ad trackers; accurate and standard.
- **§7 Infrastructure & Data Storage** — Vercel + Railway, U.S. data centers, TLS ≥1.2; standard hosting disclosure (the "industry-standard encryption" at-rest phrasing was deliberately softened in 163e280 and matches what we can verify).
- **§8 Third-Party Data Sharing** — no sale/rent/trade; processors under DPAs; legal-compliance disclosure with notice-where-permitted; standard.
- **§10 CCPA** — right-to-know/delete/non-discrimination, no-sale statement, 45-day response; standard California section (deletion mechanics are Q3/Q4, the clause text is boilerplate).
- **§12 Children's Privacy** — under-18 exclusion; standard, and low-risk given the attorney-only audience.
- **§13 Changes to This Policy** — 14-day notice for material changes; standard.
- **§14 Contact** — privacy@ecfiler.com.
