# ECFiler session 7 report: resurrection (2026-11-13)

## Outcome against "done means"

| Done means | State | Evidence |
|---|---|---|
| A real NEF with a ledger row, **or** the one remaining blocker with every prep step finished and Jackson's part cut to one queue row | **The blocker, prepped.** The QA account still cannot file in AZTTDC (court permission). Everything up to the registration form's attestation is done; the run after approval needs no server and about 10 minutes of Jackson | L20, L27; HUMAN-QUEUE #1 and #2; `docs/qa-roundtrip/attended-run.md` |
| www.ecfiler.com green from outside | **Done.** After the PR #4 merge, production serves master `494da2a` and all 30 outside checks pass (before the merge, 29 of 30; this row first said "30 of 31", a miscount) | L25, L28 |
| PR #3 merged | Merged after a clean re-verify (692 passed, 0 failed) | L22, master `b1d6f64` |
| CI manual only | `.github/workflows/ci.yml` is `workflow_dispatch` only; Vercel PR comments are off (`github.silent`); no Dependabot config, and GitHub's automated security fixes are disabled | commit `4b1cd25` |

## A. Recon

1. **Why ECFiler left the VPS (9/24):** `api.ecfiler.com` never had an A record
   and got 0 requests in 14 days, so the API had never served the public
   site. The reason still applied, and the VPS scope rule forbids
   reinstating it, so I asked one question. Answer: option 3 (no backend
   now; restore when there is a real signup or paying user). After the
   session, Jackson moved the trigger to **when the first NEF lands**.
2. **E-filing rights for a non-attorney QA account:** Non-Attorney E-File
   Registration in the QA Manage My Account (not the attorney path the
   runbook named), AZTTDC first, AZTTBK as a creditor if AZTTDC is not
   offered, plus an email to the PACER Service Center. No published
   turnaround; plan on 1 to 2 weeks. `docs/qa-efile-registration.md`.
3. **Since July:** the CM/ECF replacement has dates (first component before
   the end of 2026, new district cases by end of 2027); the EPA user-group
   call never went out (overdue, not missed; terms end 2026-12-31); PACER
   passwords now expire every 180 days; per-page fees go to $0.12 on
   2027-01-01; a proposed Rule 5.2 change would drop last-four SSNs.
   `docs/pacer-engagement-plan.md` → "Changes since July".
4. **Dependencies:**
   - Vercel project is fine. Its production env held a dead Railway
     `NEXT_PUBLIC_API_URL`, now removed.
   - The Vercel CLI token on the box is expired. The Sanger env's token
     works and was used.
   - Clerk works, with **10 users, 9 of them outside signups** (see below).
   - Mac keychain, QA credential, persisted session and attestation chain
     are all fine (preflight 12/12).
   - The Mac's Playwright browsers had been deleted, so I reinstalled them.
   - The Mac venv is Python 3.13 with Playwright 1.61, which is fine.
   - `~/.ecfiler/env.sh` is still absent (queue #10, not needed for the NEF).

## B. Production

- No 502s. `/api/*` is proxied only when `BACKEND_URL` is set; `/api/health`
  answers for the frontend; unknown API paths are 404.
- **The waitlist had been losing every signup since July:** the form showed
  "You're on the list" on a 502. It now posts to a Vercel route handler
  that mails the signup through Resend (ecfiler.com verified via the
  Hostinger zone, a send-only key) to ECFILER@sang3r.com and answers 200
  only after Resend accepts. One real signup through the live form landed
  in the inbox (L26).
- `/validate` runs in the browser (a port of the Python validator, PDF/A
  check on). The signed-in workspace and `/sign-up` say plainly that the
  workspace is closed. Homepage CTAs point at the tools and the waitlist.
- Removed: four unmeasured timing claims (now lint-banned) and three dead
  `@ecfiler.com` contact addresses (no MX). Privacy §7/§8 now match reality.
  Em dashes went from every touched screen, held by a test.

## C. The NEF path

- PR #3 merged after re-verification. A bug fixed on the way:
  `filing-access --qa` used the production username in the QA realm, so the
  documented approval check could never succeed.
- Registration: done as far as it goes without Jackson. The read-only recon
  script (`scripts/mac/qa-efile-recon.py`) stopped at the PSC login, which
  does not share the CM/ECF session; the form ends in his attestation anyway.
- Attended run: gates stay at the keyboard (reasoning in the sheet); no
  server; `STAGE=resume` files the July draft.
- Allow-rules: still in place, because the NEF has not landed and
  `qa-day` requires them. They come out in the wrap-up after the NEF.

## D. Florida and outreach

- The FL requirements are unchanged (form rev. 01-01-2021, $500). The board
  has a vendor-fee work group, which meets next on 2026-12-08.
- The fill script re-ran on the current form, with a read-back test.
- No Sunbiz entity named ECFiler or ECF Filer appears in the state's bulk data.
- **Entity (Jackson, after the session):** the applicant is **Bertlegs LLC d/b/a
  ECFiler**, not ECFiler LLC. The entity doc, the filled PDF, its test and every
  draft were reworked to it (see "After Jackson's answers").
- C2 and C5 are refreshed and lint-clean. C3 and C4 no longer show the
  gmail address.
- Nothing was sent.

## Tests

Full suite at the session 7 head: 708 passed, 0 failed, 14 skipped (the
skips are the live web tests, run separately: 24 passed, L24).

## After Jackson's answers (same day)

| Answer | Done | Evidence |
|---|---|---|
| Merge PR #4, confirm the outside check | Merged (`494da2a`). Production serves master; **30 of 30** checks pass. The "31" in the brief was my miscount in L25 (29 passed, 1 failed, of 30), corrected in place | L28 |
| Don't restore the API; trigger is the first NEF; draft a note to the 9 | Trigger recorded in `docs/hosting-topology.md` and the queue. Note drafted (`docs/outreach/c7-signup-prelaunch-note.md`), lint-clean, no em dashes, **not sent**; HUMAN-QUEUE #3. Neither law-firm domain is Hinshaw (`njlawflorida.com`, `ofjlaw.com`), so nobody is left out | — |
| Install the EPA monitor, quiet | Alerts rewritten so each kind fires once (one page per run for feed items, once ever for the page keyword, once for 7 days of failed fetches, once at the end); default priority, ops-page only. Self-test passes, and fails 7 ways against a copy with the once-only rule removed. Installed as `ecfiler-epa-monitor.timer` (daily ~15:10 UTC, Nice 19, idle IO, 10% CPU). First run: 10 feed items recorded, no keyword, no page. Recorded in `/root/CLAUDE.md` as an approved exception, and in `/root/retired/RESTORE.md` | `deploy/systemd/` |
| Approved deletions | `/root/ecfiler/web/.next` (241 MB), the session scratch files, `~/.ecfiler/qa-efile-recon` on the Mac: all gone | — |
| Bertlegs LLC d/b/a ECFiler | `docs/fl/entity-recommendation.md` rewritten (decision, order of operations, the umbrella's trade-off stated plainly, s. 865.09 read from the statute); the filled PDF now names the applicant on p. 1 and in the §II note; fill test updated (7 passed); draft, checklist, cover letter, intro email, reference emails and C3 switched. Queue: #7 the $50 fictitious name after the LLC is active, #8 the application | — |
