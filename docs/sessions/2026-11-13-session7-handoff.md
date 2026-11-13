# ECFiler session 7 handoff (2026-11-13, updated after Jackson's answers)

> **PARKED (Jackson, 2026-11-13).** Nothing moves until the court approves the
> QA e-filing registration (HUMAN-QUEUE #1). No installs or caches on the Mac
> until the NEF run. The run's prep reinstalls Playwright Chromium first
> (`docs/qa-roundtrip/attended-run.md`). The Mac disk filled today; this
> session removed its own 539 MB browser cache. The EPA monitor keeps running
> on the VPS, which is not the Mac.

## Decisions made (no longer open)

1. **API stays retired until the first NEF lands** (Jackson). Then restore per
   `docs/hosting-topology.md` (plus an `api` A record in the **Hostinger** zone
   and `BACKEND_URL` in Vercel; the site switches back on its own), and amend
   `/root/CLAUDE.md` to readmit it.
2. **Note to the 9 signups:** drafted, not sent, waiting on Jackson
   (HUMAN-QUEUE #3, `docs/outreach/c7-signup-prelaunch-note.md`). On his "send
   C7": re-read the outside accounts from Clerk, repeat the Hinshaw check
   (`hinshawlaw.com`; today neither law-firm domain is Hinshaw), send one message
   per person through Resend from `hello@ecfiler.com` with reply-to
   jackson@sang3r.com, no tracking, and log the ids in the ledger.
3. **EPA monitor installed** (approved exception, recorded in `/root/CLAUDE.md`).
   `ecfiler-epa-monitor.timer`, daily about 15:10 UTC; state
   `/var/lib/ecfiler-epa-monitor` (the September v1 files there are ignored by
   v2 and were left alone). After changing the script, re-run the `install`
   line in `deploy/systemd/README-epa-monitor.md`. It ends itself after
   2027-03-31 with one page; then remove the units.
4. **Entity: Unpossible Studio LLC d/b/a ECFiler.** Unpossible Studio LLC (single-member Florida,
   effective 01/01/2027) is Jackson's and outside this repo, as are the umbrella's website
   and its analytics. ECFiler's steps start once the LLC is active: fictitious
   name ($50, after a newspaper notice; queue #7), then the application ($500;
   queue #8).

## State

- master `494da2a` (PR #4) plus this session's follow-up commit; production
  serves master, outside check 30/30 (L28).
- PR #3 is merged (`b1d6f64`).
- Secrets added this session:
  - Resend send-only key in Vercel (`RESEND_API_KEY`).
  - `WAITLIST_NOTIFY_TO` in Vercel.
  - A local copy of both in `/root/.ecfiler-resend-key.env` (600).
  - Resend domain `ecfiler.com` (id 40801801-…), verified.
  - 4 DNS records in the Hostinger zone (`resend._domainkey`, `send` MX+TXT,
    `rsend`).
- The Vercel CLI token in `/root/.local/share/com.vercel.cli/auth.json` is
  expired. The token in `/root/Sanger/.env.local` works.
- The VPS working copy is `/root/ecfiler` with a `.venv`. The Mac repo is at
  `~/ecfiler`.

## Next operator steps

1. Watch for the QA e-filing approval:
   `[MAC] ~/ecfiler/scripts/mac/ecfiler-mac session filing-access --qa --username ecfilercom --court <court>`.
2. If the approval is for a court other than AZTTDC, add it to
   `qa_courts.json` and re-stage on the Mac's loopback before Jackson sits
   down.
3. After the NEF: the wrap-up in `docs/qa-roundtrip/attended-run.md`, remove
   the four allow-rules, then restore the API (decision 1).

## Hook and permission blocks hit this session

- **require-pipefail**, twice: pipelines inside `ssh macbook-tunnel '…'`.
  Fixed as its message says (`set -o pipefail` inside the remote command,
  or no pipe there). Agent D hit it once on `nc | head` inside `bash -c`,
  same fix.
- **Permission denied**, none retried by another route:
  - a live EPA monitor run before approval (only the self-test ran; the
    install came after Jackson's okay);
  - merging PR #4 (merged after his okay);
  - the cleanup deletions (done after his okay);
  - a background loop polling Vercel's deployments API with the Sanger token
    for the master deploy. Instead, `verify-production.sh` read the deployed
    commit from the public site.

## Cleanup

Covered in the session's closing line in chat.
