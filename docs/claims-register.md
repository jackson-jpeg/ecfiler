# Public claims register

*Built 2026-07-28 (session 4). Enforced by `tests/test_claims_register.py`.*

Every outward-facing factual claim about ECFiler, mapped to the code that
implements it and the test that proves it. The enforcement test:

- fails if a quoted claim no longer appears in its surface file (rows can't rot);
- fails if a cited proving test doesn't exist;
- fails on any **FALSE** verdict (a FALSE row is a release blocker — fix the
  code or delete the claim before merging);
- sweeps every public surface for claim signatures (court counts, dollar
  amounts, "N-point", "safety gates", custody language, "append-only",
  "Rule 5.2", "PDF/A", "Stripe") and fails if a signature line has no
  covering row — so new claims can't ship unregistered;
- pins the numeric literals (court counts, fee amounts, retention days,
  safety-gate count) to their Python sources.

**Verdicts** — `TRUE`: implemented, tested, reachable. `TRUE-BUT-UNREACHABLE`:
implemented and tested, but a deployment step still pending in HUMAN-QUEUE.md
keeps a visitor from exercising it. `ASPIRATIONAL`: describes a planned
offering and is explicitly labeled as such on the surface. `FALSE`: not
implemented — must not exist at HEAD.

**Scope note.** Statements about the world rather than about ECFiler
(CM/ECF history, court fee amounts, Rule 5.2's requirements) carry a source
in the Implementation column instead of a code path. Rhetorical framing with
no factual content ("Stop wrestling with CM/ECF forms") is not registered;
anything measurable is.

## Landing page — `web/app/page.tsx`

| Claim | Surface | Implementation | Proving test | Verdict |
|---|---|---|---|---|
| `federal courts supported` (count from `COURT_COUNT`) | web/app/page.tsx | web/lib/facts.ts + web/lib/data/*.json ← ecfiler/courts/data | tests/test_web_data_parity.py::test_facts_constants_match_data | TRUE |
| `5-point readiness check` | web/app/page.tsx | ecfiler/api/streaming.py::readiness_checks | tests/test_readiness_checks.py::TestReadinessChecks::test_exactly_five_checks | TRUE |
| `Credentials never touch our servers` | web/app/page.tsx | no credential intake anywhere in ecfiler/api/app.py; legacy endpoints answer 410 | tests/test_security.py; tests/test_api.py | TRUE |
| `Free tools, no credit card` | web/app/page.tsx | web/app/(tools)/* public routes, no auth gate | tests/test_web_public_access.py::test_free_tools_reachable_anonymously | TRUE |
| `AI reads the document, extracts case number, court, event code, and filing party` | web/app/page.tsx | ecfiler/claude_client.py document analysis | tests/test_claude_client.py; tests/test_document_analyzer.py | TRUE |
| `AI detects unredacted SSNs, DOBs, financial accounts, and minor names` | web/app/page.tsx | ecfiler/pdf/redaction_check.py (regex) + claude_client redaction prompt (minor names) | tests/test_redaction.py | TRUE |
| `Validates size, searchable text, encryption, and PDF/A compliance` | web/app/page.tsx | ecfiler/pdf/validator.py | tests/test_pdf_validator.py | TRUE |
| `The hosted service refuses sealed or restricted documents outright` | web/app/page.tsx | ecfiler/api/app.py sealed 403s | tests/test_sealed_hardfail.py::test_submit_with_sealed_flag_403 | TRUE |
| `PDF validated, PDF/A compliance checked` | web/app/page.tsx | ecfiler/pdf/validator.py `check_pdfa` | tests/test_pdf_validator.py | TRUE |
| `Filing fee displayed before you submit` | web/app/page.tsx | ecfiler/filing/fees.py wired into ecfiler/api/streaming.py | tests/test_fees.py | TRUE |
| `Docket text AI-generated and editable` | web/app/page.tsx | claude_client docket generation; editable textarea in web/app/(app)/file/page.tsx | tests/test_claude_client.py | TRUE |
| `Event code matched by AI` | web/app/page.tsx | claude_client + ecfiler/filing/events.py | tests/test_claude_client.py; tests/test_event_crawler.py | TRUE |
| `Attorney attestation required before staging` | web/app/page.tsx | POST /api/filing/stage rejects without attestation | tests/test_attestation.py::test_stage_without_attestation_422 | TRUE |
| `Automatic redaction scanning` | web/app/page.tsx | ecfiler/pdf/redaction_check.py in the streaming pipeline | tests/test_redaction.py | TRUE |
| `Manually check Rule 5.2 compliance` (the "without ECFiler" pain list) | web/app/page.tsx | statement about filing without ECFiler — Fed. R. Civ. P. 5.2 | — (external; rule cited) | TRUE |
| `Court Passwords Held` = `0` | web/app/page.tsx | same custody row as above | tests/test_security.py | TRUE |
| `$0` `To Start` | web/app/page.tsx | free tier has no payment surface at all (no billing code exists) | tests/test_claims_register.py::test_no_stripe_claims_without_stripe_code | TRUE |
| `Not available yet — join the waitlist for launch.` (Pro card) | web/app/page.tsx | waitlist POST /api/waitlist; no purchase path exists | tests/test_api.py | TRUE |
| Pro feature list under a `Coming Soon` badge (incl. `Team management`, `Priority support`) | web/app/page.tsx | planned offering, labeled Coming Soon; history/staging/AI parts exist | — (labeled planned) | ASPIRATIONAL |
| `A scripted walkthrough with sample data` (the walkthrough section is labeled, not passed off as live) | web/app/page.tsx | web/components/demo.tsx is a scripted animation and now says so | tests/test_copy_lint.py::test_demo_is_labeled_scripted | TRUE |
| `Built with` `Claude AI` / `Playwright (local CLI)` / `Next.js` | web/app/page.tsx | pyproject.toml, web/package.json | — (dependency manifests) | TRUE |
| `Not affiliated with the U.S. Courts.` | web/app/page.tsx | disclaimer, accurate | — | TRUE |

## Walkthrough component — `web/components/demo.tsx`

| Claim | Surface | Implementation | Proving test | Verdict |
|---|---|---|---|---|
| `Scripted demo` chrome label; sample case data (`motion_to_dismiss.pdf`, `1:24-cv-01234`) | web/components/demo.tsx | fictional sample data inside a labeled scripted walkthrough | tests/test_copy_lint.py::test_demo_is_labeled_scripted | TRUE |
| `5-Point` `Readiness Check` stat | web/components/demo.tsx | ecfiler/api/streaming.py::readiness_checks | tests/test_readiness_checks.py | TRUE |
| `Court Passwords` = `0` `Never on our servers` | web/components/demo.tsx | custody architecture | tests/test_security.py | TRUE |
| `Rule 5.2` scan step labels | web/components/demo.tsx | mirrors the real pipeline steps in ecfiler/api/streaming.py | tests/test_redaction.py | TRUE |
| `PDF/A` step detail | web/components/demo.tsx | mirrors validator output shape | tests/test_pdf_validator.py | TRUE |

## Facts module — `web/lib/facts.ts`

| Claim | Surface | Implementation | Proving test | Verdict |
|---|---|---|---|---|
| `COURT_COUNT = 207` and `COURT_BREAKDOWN` | web/lib/facts.ts | ecfiler/courts/data/*.json | tests/test_web_data_parity.py::test_facts_constants_match_data | TRUE |
| `RETENTION_DAYS = 30` | web/lib/facts.ts | ecfiler/storage/history.py compress_old_pdfs default | tests/test_claims_register.py::test_retention_days_pinned_to_storage | TRUE |
| Free tier: `PDF validation & PDF/A checks` | web/lib/facts.ts | POST /api/validate (public) + web/app/(tools)/validate | tests/test_public_surface.py; tests/test_pdf_validator.py | TRUE-BUT-UNREACHABLE |
| Free tier: `Rule 5.2 redaction scanning` | web/lib/facts.ts | web/lib/redaction.ts (client-side regex pass) + web/app/(tools)/redaction | tests/test_web_data_parity.py::test_redaction_patterns_json_matches_python_source; tests/test_web_public_access.py | TRUE |
| Free tier: `federal courts directory` | web/lib/facts.ts | web/lib/courts-data.ts + /courts | tests/test_web_data_parity.py; tests/test_web_public_access.py | TRUE |
| Free tier: `Filing fee lookup` | web/lib/facts.ts | web/lib/fees.ts (client-side) + /fees | tests/test_web_data_parity.py::test_fees_json_matches_python_source; tests/test_web_public_access.py | TRUE |
| Free tier: `Certificate of service generator` | web/lib/facts.ts | web/lib/certificate.ts + /certificate | tests/test_certificate.py; tests/test_web_public_access.py | TRUE |
| Free tier: `Event code browser` | web/lib/facts.ts | web/lib/courts-data.ts::getEvents + /events | tests/test_web_data_parity.py; tests/test_web_public_access.py | TRUE |
| Pro tier feature list (`5-point readiness check`, staging, history, `Team management`, `Priority support`) | web/lib/facts.ts | AI/staging/history exist behind auth; team/support are planned; Pro is labeled Coming Soon everywhere it renders | tests/test_readiness_checks.py; tests/test_account_lifecycle.py | ASPIRATIONAL |
| `PRO_PRICE = 99` | web/lib/facts.ts | planned price, labeled `planned` / `Coming Soon` on every rendering surface | — (labeled planned) | ASPIRATIONAL |

## Court directory — `web/app/(marketing)/federal-courts/page.tsx`

| Claim | Surface | Implementation | Proving test | Verdict |
|---|---|---|---|---|
| Every count and the explicit decomposition (district + bankruptcy + courts of appeals + BAPs + national courts) | web/app/(marketing)/federal-courts/page.tsx | computed at build from web/lib/courts-data.ts; zero hand-typed numbers | tests/test_web_data_parity.py; tests/test_claims_register.py::test_no_hand_typed_court_counts | TRUE |
| Per-court CM/ECF links | web/app/(marketing)/federal-courts/page.tsx | `ecf_url` field shipped in ecfiler/courts/data/*.json (not synthesized) | tests/test_web_data_parity.py::test_web_copy_matches_python_source | TRUE |

## What is CM/ECF — `web/app/(marketing)/what-is-cmecf/page.tsx`

| Claim | Surface | Implementation | Proving test | Verdict |
|---|---|---|---|---|
| `Complaints ($405), appeals ($605), bankruptcy ($338-$1,738)` | web/app/(marketing)/what-is-cmecf/page.tsx | ecfiler/filing/fees.py (Judicial Conference schedule, Dec 2024) | tests/test_claims_register.py::test_cmecf_page_fee_literals_match_schedule | TRUE |
| `PDFs must be searchable and under 100MB` | web/app/(marketing)/what-is-cmecf/page.tsx | ecfiler/pdf/validator.py max_size_mb=100 default | tests/test_pdf_validator.py | TRUE |
| `some courts require PDF/A` / `Rule 5.2 redaction` obligations / CM/ECF history and NextGen migration | web/app/(marketing)/what-is-cmecf/page.tsx | statements about CM/ECF itself — uscourts.gov | — (external; source cited) | TRUE |
| `ECFiler prepares all of this for you` + staging description | web/app/(marketing)/what-is-cmecf/page.tsx | staging pipeline | tests/test_attestation.py::test_stage_with_attestation_succeeds_and_records | TRUE |

## Free tools — `web/app/(tools)/*`

| Claim | Surface | Implementation | Proving test | Verdict |
|---|---|---|---|---|
| `No account, no credit card.` and per-tool descriptions (`Rule 5.2 Redaction Scan`, `PDF/A compliance` checks) | web/app/(tools)/tools/page.tsx | public routes; client-side libs | tests/test_web_public_access.py::test_free_tools_reachable_anonymously | TRUE |
| `Runs in your browser` / `your documents never leave your machine` (marked tools) | web/app/(tools)/tools/page.tsx | courts/events/fees/certificate/redaction are static-data client code; only /validate posts to the server | tests/test_web_public_access.py | TRUE |
| `Rule 5.2 redaction scan` `Runs entirely in your browser — the document is never uploaded.` | web/app/(tools)/redaction/page.tsx | web/lib/redaction.ts + pdfjs-dist text extraction, no network call | tests/test_web_data_parity.py::test_redaction_patterns_json_matches_python_source | TRUE |
| `This is the pattern pass only.` (AI-pass scoping) | web/app/(tools)/redaction/page.tsx | honest scoping of the regex pass vs the server AI pass | — (self-limiting statement) | TRUE |
| Fee schedule content (amounts incl. `$0` no-fee rows) and `28 U.S.C. § 1914` sourcing | web/app/(tools)/fees/page.tsx | web/lib/data/fees.json ← ecfiler/filing/fees.py | tests/test_web_data_parity.py::test_fees_json_matches_python_source | TRUE |
| Event codes shown per court type | web/app/(tools)/events/page.tsx | web/lib/data/event_codes/*.json ← ecfiler/courts/data | tests/test_web_data_parity.py::test_web_copy_matches_python_source | TRUE |
| PDF validation results (`/validate`) | web/app/(tools)/validate/page.tsx | POST /api/validate (public, server-side pikepdf/qpdf) | tests/test_public_surface.py; tests/test_pdf_validator.py | TRUE-BUT-UNREACHABLE |

## Legal pages — `web/app/privacy/page.tsx`, `web/app/terms/page.tsx`

The full clause-by-clause audit of both documents lives in
`docs/legal/counsel-review-brief.md` (session 3). Rows here cover the
machine-checkable architecture claims; the brief covers the rest.

| Claim | Surface | Implementation | Proving test | Verdict |
|---|---|---|---|---|
| `Court credentials never reach our servers.` (and §1/§2/§7/§11 custody language) | web/app/privacy/page.tsx | no credential intake in ecfiler/api/app.py; 410 tombstones | tests/test_security.py; tests/test_api.py | TRUE |
| `append-only, hash-chained` attestation records with disclosed retained remainder | web/app/privacy/page.tsx | ecfiler/storage/attestation.py | tests/test_attestation.py::test_update_blocked; tests/test_attestation.py::test_delete_blocked; tests/test_attestation.py::test_chain_table_holds_no_case_data | TRUE |
| Self-serve deletion and export (§3/§9/§11) | web/app/privacy/page.tsx | DELETE /api/account, GET /api/export, settings page wiring | tests/test_account_lifecycle.py::test_delete_purges_everything_and_chain_survives | TRUE-BUT-UNREACHABLE |
| `{RETENTION_DAYS} days` retention statements | web/app/privacy/page.tsx | ecfiler/storage/history.py | tests/test_claims_register.py::test_retention_days_pinned_to_storage | TRUE |
| Sealed documents `never` accepted by the hosted service | web/app/privacy/page.tsx | sealed 403s | tests/test_sealed_hardfail.py | TRUE |
| `Last updated: {LEGAL_LAST_UPDATED}` | web/app/privacy/page.tsx | web/lib/facts.ts constant | tests/test_copy_lint.py::test_no_forbidden_copy (bans the stale date) | TRUE |
| §5 `five-point readiness check` description | web/app/terms/page.tsx | ecfiler/api/streaming.py::readiness_checks | tests/test_readiness_checks.py | TRUE |
| §6 credentials `never held by ECFiler` / `never leave your device` | web/app/terms/page.tsx | custody architecture | tests/test_security.py | TRUE |
| §10 Free tier list (`PDF validation and PDF/A checks`, redaction scanning, courts, fees, certificate, events) | web/app/terms/page.tsx | mirrors web/lib/facts.ts TIERS | tests/test_public_surface.py | TRUE |
| §10 Pro tier `not yet available for purchase` + planned feature list | web/app/terms/page.tsx | explicit availability statement | — (labeled planned) | ASPIRATIONAL |
| §8 liability cap `DOLLARS ($100)` | web/app/terms/page.tsx | contractual term, counsel question Q2 | — (contract term, not a code claim) | TRUE |
| `Rule 5.2` obligations references (§3, §4, §5) | web/app/terms/page.tsx | Fed. R. Civ. P. 5.2 | — (external; rule cited) | TRUE |

## Signed-in app — `web/app/(app)/*`

| Claim | Surface | Implementation | Proving test | Verdict |
|---|---|---|---|---|
| `5-point readiness check` header + per-check display + `Readiness checks passed` | web/app/(app)/file/page.tsx | renders real FilingPreview fields from the streaming pipeline | tests/test_readiness_checks.py | TRUE |
| `PDF/A` requirement banners and per-court gating | web/app/(app)/file/page.tsx | ecfiler/pdf/validator.py + court quirks data | tests/test_pdf_validator.py | TRUE |
| `Rule 5.2` scan results and redacted-version flag | web/app/(app)/file/page.tsx | redaction_check + stage flags | tests/test_redaction.py | TRUE |
| Fee display incl. `$0 (fee waiver requested)` IFP path | web/app/(app)/file/page.tsx | fees.py + fee_status in stage payload | tests/test_fees.py | TRUE |
| `Connected`/`Offline` backend chip | web/app/(app)/file/page.tsx | live health check against /api/health | tests/test_api.py | TRUE |
| Settings: `5-point readiness check` feature row; court count via `COURT_COUNT` | web/app/(app)/settings/page.tsx | facts.ts | tests/test_readiness_checks.py; tests/test_web_data_parity.py | TRUE |
| Settings: profile fields `never leave your device` / PACER password `never reaches ECFiler's servers` | web/app/(app)/settings/page.tsx | localStorage-only profile; no password field exists anywhere in the web app | tests/test_security.py | TRUE |
| Settings: Pro preview card `Coming Soon` + `Pro is not available yet.` | web/app/(app)/settings/page.tsx | truthful availability; links to the waitlist | — (labeled planned) | ASPIRATIONAL |

## Auth pages — `web/app/sign-up/`, `web/app/sign-in/`

| Claim | Surface | Implementation | Proving test | Verdict |
|---|---|---|---|---|
| `federal courts supported`, `Rule 5.2 redaction scanning`, `Free to use. No credit card required.` | web/app/sign-up/[[...sign-up]]/page.tsx | facts.ts + redaction + no-billing | tests/test_web_data_parity.py; tests/test_redaction.py | TRUE |

## Root metadata — `web/app/layout.tsx`, OG image, README, BRANDING

| Claim | Surface | Implementation | Proving test | Verdict |
|---|---|---|---|---|
| Meta/OG/JSON-LD descriptions (court count from `COURT_COUNT`; `Rule 5.2 redaction scanning` in featureList; `filing preparation` framing) | web/app/layout.tsx | facts.ts; stage-don't-submit architecture | tests/test_web_data_parity.py; tests/test_copy_lint.py | TRUE |
| `Drop a PDF. AI extracts everything. You review and file.` | web/app/opengraph-image.tsx | analysis pipeline + stage-don't-submit | tests/test_claude_client.py | TRUE |
| `207 federal courts` — `97 district, 94 bankruptcy, 16 appellate` | README.md | ecfiler/courts/data | tests/test_claims_register.py::test_readme_court_counts_match_data | TRUE |
| `7 safety gates` list (validation, redaction, event code, completeness, CONFIRM, typed YES, receipt) | README.md | ecfiler/filing/workflow.py Safety Gates 1–7 | tests/test_claims_register.py::test_seven_safety_gates_pinned_to_workflow | TRUE |
| `no server ever sees a court password` / keyring custody | README.md | keychain/keyring modules; zero API intake | tests/test_security.py; tests/test_keychain_macos.py | TRUE |
| `append-only hash-chained attestation records` + `ecfiler audit verify` | README.md | ecfiler/storage/attestation.py + CLI | tests/test_attestation.py; tests/test_cli.py | TRUE |
| API endpoint table (incl. `/api/redaction-scan` `Rule 5.2 scanning`) | README.md | ecfiler/api/app.py routes | tests/test_api.py | TRUE |
| `Convert to PDF/A with OCR` (`ecfiler convert`) | README.md | ecfiler/pdf/converter.py | tests/test_pdf_validator.py | TRUE |
| Elevator pitch, key messages (incl. `append-only, hash-chained attestation log`, credentials `never leave the attorney's machine`), self-only differentiation table | BRANDING.md | rows above; competitor comparisons deleted 2026-07-28 for lack of captured evidence | tests/test_attestation.py; tests/test_copy_lint.py | TRUE |
| `All 207 federal courts` / `207 federal courts` in BRANDING | BRANDING.md | ecfiler/courts/data | tests/test_claims_register.py::test_readme_court_counts_match_data | TRUE |
| `Rule 5.2 redaction scanning` row in the BRANDING differentiation table | BRANDING.md | ecfiler/pdf/redaction_check.py | tests/test_redaction.py | TRUE |

## Deleted rather than fixed (session 4)

Claims removed from public surfaces because nothing in the repo could back
them:

- **"3-pass AI verification" / "3 safety passes"** (landing page ×4, demo,
  file page ×3, settings, Terms §5/§10, facts.ts) — no three-pass structure
  exists anywhere in the code. Replaced with the real, tested 5-point
  readiness check.
- **"~15 min per filing" / "<1 min per filing" / "10+ min saved per filing" /
  "<1min to prepare"** — no timing measurement exists.
- **"Cancel anytime. Stripe billing." / "Secure checkout via Stripe." /
  "Upgrade to Pro" button** — no billing code of any kind exists in the repo.
- **"Hosted CM/ECF filing"** (settings Pro card) — the product never submits
  to CM/ECF, by architecture; the claim contradicted the Terms.
- **"File under seal … One checkbox."** (features grid) — the hosted service
  *refuses* sealed content (403); claim inverted to the truth.
- **"final submit watchdog"** (README gate list) — no watchdog exists; the
  real Gate 6 is the typed YES at the CM/ECF confirmation screen.
- **PacerPro/ECFX comparison table and "$500/month" competitor pricing**
  (BRANDING.md) — claims about third parties with no captured evidence.
- **"Last updated: March 2026"** on both legal pages over July content —
  replaced with the `LEGAL_LAST_UPDATED` constant.
