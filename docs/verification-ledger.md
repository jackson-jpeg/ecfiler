# Verification ledger

**Append-only.** A session report may write "verified", "proven",
"confirmed", "deployed", "tested externally", or "green" only with a row
here behind it: the exact command with its `[VPS]`/`[MAC]` label, when it
ran, and what it returned. "Verified" means an outsider could reproduce the
check from the row alone. Anything without a row is **STAGED** (built and
committed, external effect not evidenced) or **UNPROVEN** (asserted with no
evidence). Enforced by `tests/test_verification_ledger.py`.

Why this exists: session 3 reported "production redeployed to Vercel and
verified from an external browser." Measured 2026-07-29, production was
serving `master@714c2d7` — a build predating that session's web work — with
`/courts` bouncing anonymous visitors to sign-in. The claims register
polices what the product tells the world; this ledger polices what the
session reports tell the operator.

Statuses: **VERIFIED** (reproducible from the row), **STAGED**, **UNPROVEN**.

## Rows

### L01 — 2026-07-29 — production smoke baseline (pre-pipeline)
`[VPS] bash scripts/verify-production.sh` → exit 1, **13 FAIL / 6 PASS**:
no commit meta tag; `/tools` `/events` `/fees` `/redaction` 404; `/courts`
`/certificate` `/validate` 307 → sign-in; purged claims live on production
(`3-pass; 3 safety passes; stripe billing; min saved per filing; cancel
anytime; live demo` on `/`, `last updated: march 2026` on both legal
pages). Establishes that production served the pre-audit build. VERIFIED
(as a measurement of staleness).

### L02 — 2026-07-29 — API crash-restart
`[VPS] kill -9 214352` (MainPID of ecfiler-api) at 02:11:10 → new MainPID
`214743` by 02:11:15 (≤5 s), `systemctl is-active` → `active`,
`curl http://127.0.0.1:8001/api/health` → `200`. VERIFIED.

### L03 — 2026-07-29 — unit hygiene
`[VPS] systemd-analyze verify /etc/systemd/system/ecfiler-api.service` →
clean. `[VPS] systemctl is-enabled ecfiler-api ecfiler-backup.timer
ecfiler-compress.timer ecfiler-post-reboot.service
ecfiler-epa-monitor.timer` → `enabled` ×5. VERIFIED.

### L04 — 2026-07-29 — offsite backup round-trip (one manual run)
`[VPS] ls /var/backups/ecfiler/` → `ecfiler-backup-20260728_193031.tar.gz`
(114 B — the database is empty). `[MAC] ls ~/ecfiler-backups/` → same file
present. One manual run VERIFIED. **Nightly** operation: `systemctl
list-timers ecfiler-backup.timer` shows LAST = never (first scheduled fire
2026-07-29 03:47) → STAGED until a timer-fired backup exists both ends.

### L05 — 2026-07-29 — no Railway references served by production
`[VPS] curl -s https://www.ecfiler.com/ | grep -ci railway` → 0; same grep
over the six `_next/static/chunks/*.js` files the homepage loads → 0 each.
VERIFIED (scope: homepage HTML + its six main chunks, on the *old* build).

### L06 — 2026-07-29 — test suite
`[VPS] .venv/bin/python -m pytest tests/ -q --ignore=tests/test_browser_e2e.py`
→ `592 passed, 8 skipped`. `[VPS] ECFILER_WEB_URL=http://127.0.0.1:3100
.venv/bin/python -m pytest tests/test_web_public_access.py
tests/test_browser_e2e.py -q` (against a local `next start` of the branch
build) → `16 passed`. Total **605 passed, 0 failed**. VERIFIED.

### L07 — 2026-07-29 — CI green including the anonymous web job
GitHub Actions run `30414754218` (branch `worktree-session2`, commit
`2b66b0a`) → `completed success`; includes the `web` job: `npm run build`,
`next start`, `pytest tests/test_web_public_access.py` with a cookieless
Playwright context. VERIFIED (public CI log).

### L08 — 2026-07-29 — live VPS API on session-4 code
`[VPS] git -C /opt/ecfiler pull` → fast-forward to session-4 HEAD;
`[VPS] systemctl restart ecfiler-api`; `[VPS] curl
http://127.0.0.1:8001/api/health` → `{"status":"ok",...,"courts_loaded":207,
"has_api_key":false}`. VERIFIED.

### L09 — 2026-07-29 — mock-court NEF round trip
`[VPS] make qa-day` →
`tests/test_browser_e2e.py::TestStagedToNefRoundTrip` `1 passed in 12.09s`.
VERIFIED (reproducible anywhere the venv exists).

### L10 — 2026-07-29 — activation script verification half
`[VPS] ECFILER_API_BASE=http://127.0.0.1:8901 bash
scripts/deploy/activate-api.sh --verify-only` (against a throwaway local
API instance with Clerk issuer set, dev auth off) → 6/6 PASS: health, 207
courts, 401 on `/api/file`, 401 on `/api/export`, waitlist count 0→1,
known-bad PDF `valid=False`; exit 0. VERIFIED. The DNS/certbot/key half is
STAGED until queue row "DNS + activate" runs.

### L11 — 2026-07-29 — post-reboot check writes its result
`[VPS] bash scripts/deploy/post-reboot-check.sh --record` → all `ok`,
`exit=0`, wrote `/var/log/ecfiler/post-reboot-20260729T013042.result` and
the `post-reboot-latest.result` symlink. Unit installed + enabled (L03).
The *boot-triggered* run: STAGED until the human reboot happens.

### L12 — 2026-07-29 — Mac filing-path health
`[MAC] ~/ecfiler/scripts/mac/ecfiler-mac check` → **3 failed** (was
reported "10/12" in session 2): the two known ANTHROPIC_API_KEY failures
plus `system_deps: Missing ghostscript, tesseract-ocr` — the PDF/A pipeline
grew dependencies and the old claim rotted silently. `[MAC] brew install
ghostscript tesseract` → installed; re-check with homebrew on PATH →
**2 failed** (only the key rows, which are HUMAN-QUEUE). The `ecfiler-mac`
wrapper now exports the homebrew PATH so non-interactive SSH runs see the
tools. VERIFIED (current state measured; key rows remain).

### L13 — 2026-07-29 — PR #1 merged; git-integration production deploy
`[VPS] gh api -X PUT repos/jackson-jpeg/ecfiler/pulls/1/merge -f
merge_method=merge` → `merged: true`, master = `3e004f63`. Vercel git
integration built Production for that SHA: GitHub deployment `5650666265`,
state `success` — no CLI, no hand step. VERIFIED.

### L14 — 2026-07-29 — production smoke, 18/18 PASS from outside
`[MAC] cd ~/ecfiler && bash scripts/verify-production.sh` → exit 0,
**18 PASS / 0 FAIL**: production serves master HEAD (`3e004f63a933` via the
ecfiler-commit meta tag); all eight free-tool routes answer 200 with no
auth bounce; /federal-courts court numbers sum to 207 matching
`web/lib/data/*.json`; zero purged claims on any served page; walkthrough
labeled scripted; aspirational Pro claims carry the Coming Soon label.
This closes L01's 13-FAIL baseline. VERIFIED.

### L15 — 2026-07-29 — QA PACER account live; filing target established; dry run green on the filing machine
`[MAC] ~/ecfiler/scripts/mac/ecfiler-mac session auth-test --qa --username
ecfilercom` → `✓ Authenticated. Token received (length 128, not shown)` —
after fixing two bugs the first real call exposed: the QA CSO constants
pointed at `qa-pacer.login.uscourts.gov` (NXDOMAIN; the real host is
`qa-login.uscourts.gov`, pinned by test), and a function-local `import
time` crashed `authenticate()`'s success path (regression-tested).
Target discovery: `[VPS/MAC]` `ecf-train.<court>.uscourts.gov` hosts
resolve but refuse TCP from both machines; the QA realm's roster at
`qa-pacer.uscourts.gov/file-case/court-cmecf-lookup` lists its own test
courts; `*.aocms.uscourts.gov` ones are firewalled from here;
**`https://ecf.tc1d.aztc.uscourts.gov` (Az Test District Court, AZTTDC)
answers 200 from the Mac**, serves District CM/ECF v10.8.4, and its login
page names `qa-login.uscourts.gov` — same realm the account authenticates
against. Recorded in docs/nef-roundtrip-runbook.md.
`[MAC] make qa-day` (dry, mock court, on the filing machine) → `1 passed`.
`[MAC] make qa-day MODE=live` → 9 PASS / 3 FAIL — the three reds are the
two human steps (headed `session login --qa` seeds the Chromium profile
and live session) plus the sandbox allow-rules paste. VERIFIED for
everything above; the live NEF round trip itself remains STAGED.

### L16 — 2026-07-29 — attended QA run reached the filing machine and stopped at a contract bug; no filing was made
The first live attempt at the NEF round trip. Preflight, on the Mac, with
the real QA account:
`[MAC] cd ~/ecfiler && make qa-day MODE=live STAGE=FEp-ZKwdKcg
TARGET=https://ecf.tc1d.aztc.uscourts.gov SERVER=http://100.126.58.33:8901
DEVUSER=qa-day` → **12/12 preflight PASS** (macOS, venv, keychain exists,
keychain password file, keychain unlocks, QA credential stored, QA
credential authenticates via cso-auth, Chromium profile, persisted QA
session live, sandbox allow-rules, receipts dir writable, attestation chain
verifies), then `✓ Staged package saved as draft:
/Users/jackson/.ecfiler/drafts/staged_0_07-cv-00170.json`.

Then it stopped. `[2] Resume Draft` → `Error resuming draft: 3 validation
errors for Filing` (`case` Field required, `event` Field required,
`filing_party` Input should be a valid dictionary or instance of
FilingParty). `[1] New Filing` → `207 courts available` / search `tc1d` →
`No courts found`. Jackson quit at `[6]`.

Proof state after the run, from the same terminal:
`✓ Attestation chain intact — head 0000000000000000…` (the empty-chain
head — no attestation was written), `~/.ecfiler/receipts/` empty,
`~/.ecfiler/traces/` empty.

**No filing was submitted, no browser reached the court, no NEF exists.**
The QA-day proof list (L15's STAGED item) is still STAGED. What this run
did verify: the twelve preflight gates pass against live PACER QA
infrastructure, and the hosted→local staging seam was broken in production
code the whole time. VERIFIED as a failed run — the failure state above is
the evidence, captured before any retry.

### L17 — 2026-07-29 — two real bugs found by the failed run, fixed and pinned
Both were found only because a human drove the real path; both had passing
tests over them.

1. **The hosted→local contract had never been exercised.** The API returned
   a flat display dict; `stage-pull` wrote it verbatim; the CLI parsed it as
   a `Filing` and raised. `StagedPackage` now embeds the canonical `Filing`
   the CLI resumes from, and `stage-pull` validates through that model
   before it writes anything. `[VPS] .venv/bin/python -m pytest
   tests/test_staged_contract.py -q` → **13 passed**.
2. **The draft named the wrong court.** It said `azd` — the real District of
   Arizona — for a run targeting the QA court, because the runbook staged
   against a production court ID and "overrode" the URL at submit time. A
   pydantic error was the only thing between that draft and a production
   endpoint. Fixed structurally: `StagedProvenance` pins court id, ECF URL
   and environment at staging; `enforce_court_invariants` aborts before the
   browser launches on any mismatch; `ECFILER_ECF_URL` is now a
   confirmation, never a substitution; the registry serves exactly one PACER
   environment, so a QA court is absent from production mode rather than
   merely unlikely. `[VPS] .venv/bin/python -m pytest
   tests/test_court_invariants.py -q` → **19 passed**.

A third, smaller bug the run exposed: stage codes came from
`token_urlsafe`, which can start with `-`; the CLI then answers `Error: No
such option '-c'`. Codes are now alphanumeric (`new_stage_code`), pinned by
test. Full suite `[VPS] .venv/bin/python -m pytest tests/ -q` → **643
passed, 8 skipped** (includes the browser round trip). VERIFIED.

### L18 — 2026-07-29 — what the mock round-trip test was actually proving
Audited after L17, because the mock passed while the real seam was broken.
`TestStagedToNefRoundTrip` asserted `draft["filing"]["case_number"]` — a key
that exists only in the shape the bug produced — then drove the browser from
hardcoded literals, built its court profile inline with `court_id="test"`,
and recorded an attestation for a court (`test`) that was not the court it
staged (`nysd`). It never loaded the draft through `Filing`, never called
the workflow's submit path, and never compared staged court to filed court.
It did prove: the API stages and chains; the CLI can fetch a package and
write a file; Playwright walks the mock's ten steps to a receipt; NEF text
lands in a `kind="submitted"` attestation, the chain verifies, and the
chain head anchors into the saved receipt.

The test now parses the pulled draft through `Filing`, drives every browser
step from the draft's own values, runs `enforce_court_invariants` on the
registry-resolved court, asserts the substitution case raises, and asserts
the court and case that were staged are the ones in the receipt.
`[VPS] .venv/bin/python -m pytest
tests/test_browser_e2e.py::TestStagedToNefRoundTrip -q` → **1 passed**.
VERIFIED.

### L19 — 2026-07-29 — the fixed seam re-staged and pulled clean onto the filing machine
Restaged against the QA court with the fixed code, on a QA-mode staging API:
`[VPS] ECFILER_DEV_AUTH=1 ECFILER_PACER_QA=1
ECFILER_DATA_DIR=/root/.ecfiler-qa-staging .venv/bin/python -m uvicorn
ecfiler.api.app:app --host 100.126.58.33 --port 8901` (health 200), then
`[VPS] curl -X POST …/api/filing/stage -H 'X-User-Id: qa-day' -d
'{"court_id":"azttdc",…}'` → `stage_code: 56DB64etAjX`, `court: azttdc Az
Test District Court (PACER QA)`, `filing.court_id: azttdc`, provenance
`{court_id: azttdc, ecf_url: https://ecf.tc1d.aztc.uscourts.gov,
environment: qa}`.

Pulled with the real CLI on the Mac:
`[MAC] /Users/jackson/ecfiler/scripts/mac/ecfiler-mac stage-pull 56DB64etAjX
--server http://100.126.58.33:8901 --dev-user qa-day` → `✓ Staged package
saved as draft: /Users/jackson/.ecfiler/drafts/staged_0_07-cv-00170.json` /
`Court: azttdc (qa) — https://ecf.tc1d.aztc.uscourts.gov` / `Case:
0:07-cv-00170   Event: Motion for Extension of Time`. The draft is visible
to the product: `[MAC] … ecfiler-mac drafts` lists it as `azttdc
0:07-cv-00170 Motion for Extension of Time`. In production mode the QA court
stays invisible: `[MAC] … ecfiler-mac courts --search tc1d` → `No courts
found`.

The new qa-day provenance gate was exercised in both directions with its own
script extracted from `scripts/mac/qa-day.sh`: a draft naming `azd` →
`FAIL  staged ECF URL https://ecf.azd.uscourts.gov != TARGET
https://ecf.tc1d.aztc.uscourts.gov; staged environment is 'production', not
'qa' — refusing to file.` (exit 1); the real draft → `PASS  → azttdc @
https://ecf.tc1d.aztc.uscourts.gov (qa)` (exit 0).

CI on PR #3 (`session6-qa-day`, head `7446ecf`): `test (3.11)` pass,
`test (3.12)` pass, `web` pass, Vercel preview pass. VERIFIED.

**Still STAGED:** the live NEF round trip. Everything up to the browser is
now proven on the real machines with the real account; the filing itself has
not been attempted since the fix.

---

### L20 — 2026-07-30 — the re-run reached the court's own permission wall; the closest anything has come, and still no filing
The second attended attempt, with the session-6 fixes in place:
`[MAC] cd ~/ecfiler && make qa-day MODE=live STAGE=56DB64etAjX
TARGET=https://ecf.tc1d.aztc.uscourts.gov SERVER=http://100.126.58.33:8901
DEVUSER=qa-day`.

**How far it got.** Every ECFiler-owned stage did its job: PDF validated,
redaction scan clean, attorney review rendered with the right court and
case, the court invariant from L17 passed (`Target confirmed`), PACER
authenticated against the QA realm, the browser reached
`https://ecf.tc1d.aztc.uscourts.gov/cgi-bin/iquery.pl`, and the case number
`0:07-cv-00170` was entered and accepted with no CM/ECF error. Artifacts:
`docs/qa-roundtrip/run-20260730-01-filing-page.png`,
`run-20260730-02-case-entered.png`. The Playwright trace
(`trace_0-07-cv-00170_20260730_114335.zip`, on the Mac) records the whole
walk. It is deliberately **not** committed: a trace carries network data
including session cookies, and the screenshots carry the evidence without
them.

**Where it stopped.** `Selecting event type…` → `#event_list` not found,
three attempts, then abort. `~/.ecfiler/receipts/` is empty; nothing was
filed, and no docket entry exists.

**Why.** Not a selector bug. Both screenshots show the CM/ECF menu bar this
account is served: **Query · Reports · Utilities · Help · Log Out** — and no
Civil or Criminal menu. A PACER account grants access to *read* dockets;
filing requires e-filing privileges the individual court grants separately
and must approve. With no filing menu there is no filing form, so the event
list genuinely is not on the page. The three retries were the product
mistaking a permissions answer for a transient one.

**A second defect, found in the trace and independent of the first.**
`DistrictCourt.navigate_to_filing` went to `/cgi-bin/iquery.pl` — the docket
*query* CGI. No event list exists on that page under any account, so an
approved e-filer would have failed at the same line for a different reason.
The same URL was being handed to filers as `ecf_filing_url` in every staged
package. `filing_url` now returns the court's menu page and the query CGI is
named `query_url` (`tests/test_efiling_entitlement.py`). The real route from
the Civil menu to an event list stays unbuilt rather than guessed at, and is
logged as R-014: it cannot be written or tested until an account with filing
privileges exists.

**Also observed, and treated as a defect:** `AI validation unavailable
(ConfigError) — proceeding`. The verification stage this product is named
for did not run, and the run continued on one dim line of console output.
Fixed in L21.

STAGED — the NEF round trip remains unproven, and is now blocked on a court
approval rather than on code.

---

### L21 — 2026-07-30 — the two failures the run exposed, fixed and pinned
1. **A permissions failure now says so.** `check_filing_entitlement` reads
   the CM/ECF menu bar before the event list is looked for and raises
   `NotAnEFilerError` naming the court, quoting the menu items the account
   was actually served, stating that nothing was filed and that the staged
   package is unchanged, and pointing at the privilege request. Matching is
   on exact anchor text, so a "View Civil Docket" link is not mistaken for a
   Civil menu. `retry_on_error` does not retry it. `[VPS] .venv/bin/python
   -m pytest tests/test_efiling_entitlement.py -q` → **23 passed**, and the
   failure is reproduced against a real Chromium DOM in
   `tests/test_browser_e2e.py::TestEFilingEntitlementInARealBrowser` (2
   passed) using a mock route that serves the exact menu bar from the
   screenshots above.
2. **A verification stage that cannot run no longer fails open.** An
   unavailable check (missing key, unreachable service, unparseable
   response) stops the run unless the attorney types `FILE UNVERIFIED`; the
   waiver names who gave it and why the check could not run, appears in the
   attorney-review panel above the CONFIRM gate, and is hashed into the
   submission attestation — payload `verification[]` plus a plain-English
   clause in the attestation text. A validator that *ran and objected* is
   recorded distinctly (`issues_found`) and still routed to the attorney
   review gate rather than blocking. The same audit found the redaction scan
   doing a quieter version of it: without an API key it silently degrades to
   a pattern scan and still printed "No redaction issues", and a document it
   could not read at all printed one dim line and was filed anyway. It now
   names the scan it actually performed, and an unreadable document goes
   through the same waiver gate. `[VPS] .venv/bin/python -m pytest
   tests/test_verification_gate.py -q` → **21 passed**.

Full suite `[VPS] .venv/bin/python -m pytest tests/ -q` → **685 passed, 8
skipped** (was 641 before this session's 44 new tests). VERIFIED.

---

## Retro-audit — sessions 2–4 verification claims

Each claim that used verification language in a report or doc, judged
against the evidence available on 2026-07-29. Downgrades were applied in
place (PR body, `docs/hosting-topology.md`, HUMAN-QUEUE).

| Claim (session) | Evidence today | Status |
|---|---|---|
| "Production redeployed to Vercel and verified from an external browser" (S3) | L01: production served `master@714c2d7`, predating the claim's web work; no artifact of the claimed external check exists | **UNPROVEN — false as measured** |
| "Zero references to the dead Railway host" on the live site (S3) | L05 | VERIFIED (narrow scope) |
| "Clerk login works" on production (S3) | `/sign-in` answers 200 today; the login flow itself was never evidenced | UNPROVEN → downgraded to a page-load observation |
| "Crash-restart proven, SIGKILL → auto-restart <5 s" (S3) | L02 re-run | VERIFIED |
| "First backup ran local + offsite" (S3) | L04 artifacts both ends | VERIFIED |
| "Nightly offsite backups" (S3) | L04: timer enabled, has never fired | **STAGED** |
| "Restore test passed / snapshot restore-tested, chain verifies, row counts match" (S3) | No artifact, no reproducible command recorded; not re-run | **STAGED** |
| "NEF round-trip dry-run proven end to end against the mock court" (S3) | L09, reproducible; also in CI (L07) | VERIFIED |
| "Hash-don't-store … tested"; account deletion/export (S3) | `tests/test_attestation.py`, `tests/test_account_lifecycle.py` in the green suite (L06/L07) | VERIFIED |
| "API surface closed" — auth on AI endpoints, compress removed (S3) | `tests/test_public_surface.py` (L06) + live 401s (L10) | VERIFIED |
| "Units enabled and systemd-analyze verify clean" (S3) | L03 re-run | VERIFIED |
| "Suite: 541/546 passed" (S3) | CI history on GitHub | VERIFIED |
| "ecfiler check on the Mac is 10/12" (S2, repeated in queue) | L12: it was 3-failed by dependency drift before this session's fix | **UNPROVEN as stated — superseded by L12** |
| "PACER session persistence … covered by tests" (S2) | `tests/test_pacer_session.py` in the green suite | VERIFIED |
| EPA window monitor operational (S2) | timer enabled (L03); journal shows a completed run 2026-07-28 14:59 | VERIFIED |
| "Verified as an anonymous outsider" (S4) | L06/L07 — explicitly scoped to a local build in the report itself; production explicitly flagged as unverified in the same report | VERIFIED as scoped |
| "Live VPS API updated and healthy" (S4) | L08 | VERIFIED |
| "Reboot self-documents" (S4) | L03 + L11; boot-triggered run pending | STAGED (labeled as such) |
| "Vercel's build of the exact commit is green" (S4) | GitHub deployment status `success` for the Preview of `fe094e8` | VERIFIED |

**Count: 19 claims audited — 13 VERIFIED, 3 STAGED, 3 UNPROVEN** (one of
the three outright false as measured: session 3's production deploy).
The pattern in all three UNPROVEN rows is the same: a real action happened
(a deploy, a login page, a passing check) and the report generalized it
past its evidence.
