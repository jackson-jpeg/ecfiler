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
