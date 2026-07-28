# Hosting topology

*Decided and deployed 2026-07-28 (session 3). Recurring cost: $0/month.*

## The decision

| Component | Where | Cost | Why |
|---|---|---|---|
| Frontend (Next.js) | **Vercel** (existing project `ecfiler`, `www.ecfiler.com`) | $0 (hobby) | Already there, already free, already fast. Nothing to migrate. |
| Free tools (courts, event codes, fees/NOS/checklist, cert-of-service) | **In the frontend** — static JSON + TypeScript, no server | $0 | They were always stateless and DB-free; four of the six had no non-stdlib dependency at all. The signed-in free tier now works even if the backend is down. |
| API (AI analysis, staging, history, validate, waitlist) | **Hostinger VPS** — `ecfiler-api.service`, uvicorn behind nginx | $0 marginal (VPS already runs 24/7 for other work) | Self-hosting over SaaS is the standing preference; the box already has nginx+TLS, Python 3.12, systemd conventions, and 53 GB free. |
| Database | **SQLite on VPS disk** (`/var/lib/ecfiler`) | $0 | See below — this was the decisive argument. |
| Offsite backup | **MacBook** over the existing SSH tunnel, nightly | $0 | `scripts/deploy/ecfiler-backup.sh`, 14-day retention both ends. |

## Why SQLite stays (Neon and Postgres rejected)

The repo has **zero Postgres code** — no `DATABASE_URL`, no driver, no
migrations. The datastore is three SQLite files, and the append-only
attestation guarantee is implemented as SQLite `BEFORE UPDATE/DELETE` triggers
plus `BEGIN IMMEDIATE` write serialization, with a test suite that proves it
(`tests/test_attestation.py`).

- **Neon (proposed)** solves half the problem — it is Postgres, not an
  application host — and forces a port of the attestation guarantee to a
  different mechanism. Its free tier (verified 2026-07: 100 CU-hours/month and
  0.5 GB per project, no card) adds a hard storage cap, a short
  point-in-time-recovery window on the free plan, scale-to-zero cold starts,
  and a network dependency between the API and its own data. Its one real
  advantage — surviving loss of the VPS — is covered by the nightly offsite
  backup for a database that is currently empty.
- **Postgres on the VPS** (a cluster already runs here for another project)
  buys nothing over SQLite at this scale and costs the same porting work.
- **Railway (status quo)** is dead: the trial expired, which is why the API
   404s. Reviving it costs money for a project that may never leave the garage.

**If ECFiler ever outgrows SQLite:** the append-only guarantee does *not* port
for free. In Postgres, the stronger construction is `REVOKE UPDATE, DELETE ON
attestations FROM app_role` at the role level, with a `BEFORE UPDATE OR
DELETE` trigger raising an exception as belt-and-braces — a trigger can be
disabled by the table owner; a revoked grant cannot be exercised by the
application role at all. The Postgres analogue of SQLite's free-page concern
also applies: deleted tuples persist until `VACUUM`, so a purge there needs
`VACUUM (FULL)` or `pg_repack` to be real. Carry the guarantee across with
ported tests, not a comment.

## What runs where

```
Visitor ──▶ www.ecfiler.com (Vercel)
              ├─ marketing pages, privacy, terms ── static
              ├─ courts / events / fees / cert-of-service ── client-side
              │    (web/lib/courts-data.ts, web/lib/certificate.ts,
              │     data parity enforced by tests/test_web_data_parity.py)
              └─ /api/* ──(Next rewrite, server-side proxy)──▶
                     https://api.ecfiler.com  ──▶ VPS nginx ──▶ 127.0.0.1:8001
                                                    ecfiler-api.service
                                                    /var/lib/ecfiler (SQLite)
```

- The browser makes only **relative** `/api/*` calls (`NEXT_PUBLIC_API_URL`
  is empty); the Next.js rewrite proxies server-side to `BACKEND_URL`
  (default `https://api.ecfiler.com`). One transport, no CORS surface.
- The API is **fail-closed**: it refuses to boot without `CLERK_ISSUER`.
  Anthropic-backed endpoints answer 503 until `ANTHROPIC_API_KEY` is present.
- Public API surface is deliberate (enforced by
  `tests/test_public_surface.py`): free tools public; AI analysis, drafts,
  history, staging, account deletion/export all Clerk-authenticated;
  the old unauthenticated compress endpoint is gone.

## Runbook (VPS)

All canonical files live in `scripts/deploy/`.

| Piece | Live location |
|---|---|
| Code | `/opt/ecfiler` (git clone, branch `worktree-session2` until the PR merges, then `master`) |
| venv | `/opt/ecfiler/.venv` (`pip install ".[web]"` — no Docker, no Playwright/Chromium) |
| Service | `/etc/systemd/system/ecfiler-api.service` (user `ecfiler`, `Restart=always`, hardened: `ProtectSystem=full`, `ProtectHome`, `NoNewPrivileges`) |
| Env | `/etc/ecfiler/api.env` (chmod 600: `CLERK_ISSUER`, `ECFILER_ALLOWED_ORIGINS`, `ECFILER_DATA_DIR=/var/lib/ecfiler`; add `ANTHROPIC_API_KEY=` to enable AI endpoints) |
| Data | `/var/lib/ecfiler` (owner `ecfiler:ecfiler`, 750) |
| nginx | `/etc/nginx/sites-available/ecfiler-api` → api.ecfiler.com (port 80 until certbot) |
| Timers | `ecfiler-backup.timer` (03:47 nightly), `ecfiler-compress.timer` (Sun 04:30) |
| Logs | journald (`journalctl -u ecfiler-api`) |

**Deploy an update:** `cd /opt/ecfiler && git pull && systemctl restart ecfiler-api`
**Health:** `curl http://127.0.0.1:8001/api/health`
**Backup now:** `bash /opt/ecfiler/scripts/deploy/ecfiler-backup.sh`
**Restore:** untar the newest `/var/backups/ecfiler/ecfiler-backup-*.tar.gz`
(or the Mac copy in `~/ecfiler-backups/`), copy the `.db` files into
`ECFILER_DATA_DIR`, untar `staged/documents/receipts`, restart. The snapshot
mechanism (sqlite3 `.backup` of a live, mid-write chain) was restore-tested
on 2026-07-28: restored chain verifies, row counts match.
**After any reboot:** `bash /opt/ecfiler/scripts/deploy/post-reboot-check.sh`

## Verified / remaining

Verified 2026-07-28: service healthy on localhost; auth fail-closed;
crash-restart proven (SIGKILL → auto-restart in <5 s); units enabled and
`systemd-analyze verify` clean; first backup ran local + offsite; restore
test passed; production frontend deployed and confirmed from an external
browser (zero references to the dead Railway host; Clerk login works).

Remaining, each a HUMAN-QUEUE row:

1. **DNS**: `api.ecfiler.com` A `187.77.218.14` / AAAA `2a02:4780:4:1c0b::1`
   on the ecfiler.com zone (Vercel DNS), then `certbot --nginx -d
   api.ecfiler.com` on the VPS. Until then, `/api/*` from the site answers
   502 (the waitlist widget and signed-in backend features; everything else
   works). Attempting this DNS write from the session was blocked by the
   sandbox's permission layer, twice — it is 90 seconds by hand.
2. **`ANTHROPIC_API_KEY`** into `/etc/ecfiler/api.env` (the sandbox also
   blocks credential copying, correctly). Until then `/api/file*` answers 503.
3. **Reboot verification**: everything short of the reboot is proven, but the
   session runs *on this VPS* — rebooting it kills the operator mid-job and
   every other live Claude session on the box. Reboot when convenient and run
   `post-reboot-check.sh`.

## Rejected alternatives, one line each

- **Railway paid**: recurring cost for a garage project; firm no.
- **Neon free**: replaces the wrong half, forces a guarantee port, caps at
  0.5 GB; its VPS-loss story is covered by backups.
- **Fly.io/Render free tiers**: same class of problem as Railway (trial-ish
  free tiers, cold starts, volume semantics), new platform to learn.
- **Everything serverless (kill the API)**: the AI endpoints need a
  server-side Anthropic key and the staging/history features need Clerk +
  SQLite + a filesystem. `/api/validate` stays server-side deliberately —
  a browser-side approximation would false-pass structural checks that
  pikepdf/qpdf catch, and a validity claim that can false-pass is worse than
  a network dependency. The *rest* of the free tools did move client-side.
- **Fee/NOS/checklist/redaction as client-side ports too**: nothing in the
  web UI calls those endpoints today (verified by grep — no consumer);
  porting them would be dead code. They stay API-side until a UI exists.
