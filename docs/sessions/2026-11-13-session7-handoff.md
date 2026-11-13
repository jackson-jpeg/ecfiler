# ECFiler session 7 handoff (2026-11-13)

## Two decisions for the lead / Jackson

1. **Restore the API now? The trigger may already have fired.** Clerk has
   10 accounts; 9 are outside signups (two on law-firm domains, 2026-08-15
   and 2026-10-23), and all 5 since 2026-08-15 signed up while the workspace
   was dead. The rule agreed today was "restore only when ECFiler has a
   real signup or paying user". If these count, say "readmit ECFiler to the
   VPS" and the operator amends `/root/CLAUDE.md` and restores per
   `docs/hosting-topology.md` (plus an `api` A record in the **Hostinger**
   zone and `BACKEND_URL` in Vercel; the site switches back on its own).
   Whoever restores should first decide what to tell those nine people.
   No message has gone to them.
2. **Install the EPA monitor on the VPS?** A3 says the call is overdue and
   worth watching to 2027-03-31. v2 is in `scripts/epa-window-monitor.sh`
   (RSS user-group items + group-page keywords, ops-page, stops itself).
   It is a retired ECFiler unit, so it needs Jackson's okay to come back.

## State

- Branch `session7`. One PR into master. Production was deployed from the
  branch at `4b1cd25` mid-session, and the merge redeploys master with the
  same site plus the docs.
- PR #3 is merged (`b1d6f64`).
- New secrets:
  - Resend send-only key in Vercel (`RESEND_API_KEY`).
  - `WAITLIST_NOTIFY_TO` in Vercel.
  - A local copy of both in `/root/.ecfiler-resend-key.env` (600).
  - Resend domain `ecfiler.com` (id 40801801-…), verified.
  - 4 DNS records in the Hostinger zone (`resend._domainkey`, `send` MX+TXT,
    `rsend`).
- The Vercel CLI token in `/root/.local/share/com.vercel.cli/auth.json` is
  expired. The token in `/root/Sanger/.env.local` works.
- The VPS working copy is `/root/ecfiler` (cloned this session) with a
  `.venv`. The Mac repo is on `session7`.

## Next operator steps

1. Watch for approval:
   `[MAC] ~/ecfiler/scripts/mac/ecfiler-mac session filing-access --qa --username ecfilercom --court <court>`.
2. If the approval is for a court other than AZTTDC, add it to
   `qa_courts.json` and re-stage on the Mac's loopback before Jackson sits
   down.
3. After the NEF, do the wrap-up in `docs/qa-roundtrip/attended-run.md`,
   then remove the four allow-rules.

## Hook and permission blocks hit this session

- **require-pipefail**, twice: pipelines inside `ssh macbook-tunnel '…'`.
  Fixed as its message says (`set -o pipefail` inside the remote command,
  or no pipe there). Agent D hit it once on `nc | head` inside `bash -c`,
  same fix.
- **Permission denied**: a live run of the EPA monitor (it could page via
  ops-page). Not retried; only the self-test (pages nothing) ran.

## Cleanup

Covered in the session's closing line in chat.
