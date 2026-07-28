# Human queue

Everything here failed one of the five blocking tests: money, identity/signature,
a credential that exists nowhere on either machine, an irreversible action on
production data, or a lawyer's judgment — plus, this session, a sixth in
practice: the sandbox's permission layer, which blocked a handful of specific
actions (each noted inline). Nothing is here because it was tedious.

Ordered by what unblocks the most downstream work.

| # | What | Why blocked | Time |
|---|---|---|---|
| 1 | [Sandbox permissions for the Mac filing path](#1) | Sandbox | 2 min |
| 2 | [DNS for api.ecfiler.com + certbot](#2) | Sandbox (DNS write blocked) | 90 s |
| 3 | [`ANTHROPIC_API_KEY` into the VPS API env](#3) | Sandbox (credential copy blocked) | 60 s |
| 4 | [Rotate the PACER password](#4) | Credential | 90 s |
| 5 | [Register the QA PACER account](#5) | Identity + CAPTCHA | 60 s |
| 6 | [Subscribe to GovDelivery](#6) | CAPTCHA | 30 s |
| 7 | [Send the two outreach messages](#7) | Identity | 4 min |
| 8 | [Put `ANTHROPIC_API_KEY` on the Mac](#8) | Credential + sandbox | 60 s |
| 9 | [Decide the entity question](#9) | Identity/legal | 5 min read |
| 10 | [Form the LLC + file the FL application](#10) | Money + signature | $625 |
| 11 | [Counsel review of Terms/Privacy](#11) | Lawyer | shrunk — see below |
| 12 | [Reboot the VPS, verify boot path](#12) | Kills live sessions incl. mine | 3 min |

---

## 1. Sandbox permissions for the Mac filing path {#1}

Two Mac commands were sandbox-blocked in session 2 and will block again the
moment the QA round-trip starts: launching the headed browser at the PACER login
page over the tunnel, and writing the key file in item 8. Add to
`/root/.claude/settings.json` (or the project's `.claude/settings.json`):

```json
{
  "permissions": {
    "allow": [
      "Bash(ssh macbook-tunnel:*)",
      "Bash(ssh macbook:*)"
    ]
  }
}
```

Scoped tighter, if you prefer the minimum:

```json
      "Bash(ssh macbook-tunnel ~/ecfiler/scripts/mac/ecfiler-mac:*)",
      "Bash(ssh macbook bash ~/ecfiler/scripts/mac/keychain-setup.sh:*)"
```

Without this, the NEF round-trip (item 5's payoff) stalls at `session login`
again. Everything downstream of it is built and dry-run-proven —
`docs/nef-roundtrip-runbook.md`.

## 2. DNS for api.ecfiler.com + certbot {#2}

The API is live and healthy on the VPS (`ecfiler-api.service`, nginx vhost
staged), and www.ecfiler.com is deployed and pointing at it — but
`api.ecfiler.com` does not resolve yet. The sandbox blocked the DNS write
twice, so:

```
[mac] vercel dns add ecfiler.com api A 187.77.218.14
[mac] vercel dns add ecfiler.com api AAAA 2a02:4780:4:1c0b::1
[vps] certbot --nginx -d api.ecfiler.com
```

(Vercel CLI on the Mac is already authenticated as jackson-jpeg.) Until this
runs, the site's `/api/*` calls answer 502 — the waitlist widget and signed-in
backend features; the free tools and marketing pages work regardless, because
they no longer touch the API at all. This is the last step of R-005/R-009.

## 3. `ANTHROPIC_API_KEY` into the VPS API env {#3}

The API runs without it; `/api/file*` (AI analysis) answers 503 until it lands.
The sandbox blocked copying the existing key between env files (reasonably), so:

```
[vps] echo 'ANTHROPIC_API_KEY=sk-ant-...' >> /etc/ecfiler/api.env
[vps] systemctl restart ecfiler-api
[vps] curl -s http://127.0.0.1:8001/api/health   # "has_api_key": true
```

A dedicated key (console.anthropic.com) beats reusing the sanger-monitor key —
separate billing visibility — but either works.

## 4. Rotate the PACER password {#4}

The production PACER password was exposed in a prior session transcript. Treat it
as compromised. Everything touching production PACER inherits this.

<https://pacer.uscourts.gov/my-account-billing/manage-my-account-login> → Settings
→ Change Password. Then update it on the Mac (piped, never in shell history):

```
[mac] printf '%s' 'NEW-PASSWORD' | bash ~/ecfiler/scripts/mac/keychain-setup.sh jmsanger
```

Logged as R-002.

## 5. Register the QA PACER account {#5}

**Still the gating item for proving ECFiler actually files** — but the gap has
narrowed to exactly this account: the entire staging→pull→file→NEF→attestation
path now round-trips against the mock CM/ECF in the test suite
(`tests/test_browser_e2e.py::TestStagedToNefRoundTrip`), and
`docs/nef-roundtrip-runbook.md` holds the exact QA-day command sequence.
Activation day is execution, not building.

<https://qa-pacer.psc.uscourts.gov/pscof/registration.jsf>

Every field is pre-answered in `docs/outreach/c1-answer-sheet.md` — copy, paste,
solve the reCAPTCHA, submit. **Skip the credit-card section**; set User Type to
**Individual**. Blocked because it is an account registration under your
identity with terms assent, and reCAPTCHA-gated (anti-bot controls on federal
systems are a hard stop).

Once it activates overnight:

```
[mac] printf '%s' 'QA-PASSWORD' | bash ~/ecfiler/scripts/mac/keychain-setup.sh 'QA-USERNAME'
[mac] ~/ecfiler/scripts/mac/ecfiler-mac session login --qa
```

## 6. Subscribe to GovDelivery {#6}

<https://public.govdelivery.com/accounts/USFEDCOURTS/subscriber/new?topic_id=USFEDCOURTS_1821>

Email `realjacksons@gmail.com`, solve the MTCaptcha, submit, then click the
confirmation link. Blocked only by the CAPTCHA.

## 7. Send the two outreach messages {#7}

**C2 — AO developer mailbox.** The Gmail draft in your account
(`developers@psc.uscourts.gov`) is final and unchanged this session — verified
against the repo text. Read it and hit send, ideally after item 6 so "I'm
subscribed to the developer updates list" is true.

**C5 — M.D. Fla. clerk.** Web form, not email:
<https://www.flmd.uscourts.gov/webforms/contact-cmecf> — paste-ready answers in
`docs/outreach/c5-submission-sheet.md`. Needs your phone number, which is
nowhere in the repo.

> **Read before sending — the identity framing changed again, deliberately.**
> Session 1 borrowed a firm practice that ECFiler doesn't have; session 2
> over-corrected by erasing your profession entirely. Session 3 settled it: the
> letters now claim what is true — you are a litigation docketing specialist in
> Tampa, writing in personal capacity — and never name or allude to your
> employer, never use "we", and never claim ECFiler is in use anywhere. C5 and
> the C3/C4 documents changed; C2 did not. The lint
> (`tests/test_copy_lint.py`) now enforces those three rules rather than
> banning the (true) job title. Worth a skim: it changes how C5 reads.

## 8. Put `ANTHROPIC_API_KEY` on the Mac {#8}

`ecfiler check` on the Mac is **10/12**; the two failures clear with one file.
The sandbox blocked writing it remotely, so:

```
[mac] printf 'export ANTHROPIC_API_KEY=%s\n' 'sk-ant-...' > ~/.ecfiler/env.sh
[mac] chmod 600 ~/.ecfiler/env.sh
[mac] ~/ecfiler/scripts/mac/ecfiler-mac check     # expect 12/12
```

## 9. Decide the entity question {#9}

`docs/fl/entity-recommendation.md` — the recommendation is **ECFiler LLC, a
single-member Florida LLC, formed now**, defended against Delaware and against
waiting. Read it and say yes or overrule it. Everything in item 10 waits on the
name.

Sunbiz sits behind Cloudflare bot protection and refused both machines, so the
name-availability check is yours:
<https://search.sunbiz.org/Inquiry/CorporationSearch/ByName>.

## 10. Form the LLC and file the Florida application {#10}

Money and your signature. Roughly **$625** total.

- **LLC** (~$125): <https://efile.sunbiz.org/llc_file.html>. Registered agent =
  yourself, principal address = your Tampa address.
- **Application** ($500): `docs/fl/Third_Party_Vendor_Application_FILLED.pdf` is
  filled except entity name, both signature blocks, dates, phone, and street
  address. `docs/fl/application-packet-checklist.md` lists every blank. Confirm
  the check payee with the Authority (support@myflcourtaccess.com /
  850-577-4609) before writing it.
- **References**: three request emails in
  `docs/fl/drafts/reference-request-emails.md` — **the third changed this
  session**: the Railway reference died with the trial, and the truthful
  replacement is Hostinger (the VPS that actually hosts the backend now). Note
  the account-name caveat in that file. Send these *before* mailing, so the
  references are warned.
- The cover letter was rewritten to singular voice with truthful status claims
  (`docs/fl/drafts/cover-letter.md`) — re-read before printing.

## 11. Counsel review of Terms and Privacy {#11}

`docs/legal/counsel-review-brief.md`. **This shrank: two of the four questions
collapsed into "here is what we did" this session.** Q3 (deletion vs.
append-only attestation) is resolved in engineering — hash-don't-store, tested;
counsel now only confirms the §11 disclosure language. Q4 (facts published
ahead of reality) is resolved — the purge record is complete, the policy claims
only what is true, and the deletion/export endpoints exist. Q1 (UPL) and Q2
(liability stack) remain the genuine lawyer questions. Both pages still carry
the `LEGAL REVIEW REQUIRED before deploy` banner.

## 12. Reboot the VPS, run the boot check {#12}

Reboot survival is configured and everything short of the reboot is proven
(units enabled, crash-restart verified). The reboot itself would kill every
live Claude session on the box — including the one doing the work — so it is
yours, whenever convenient:

```
[vps] reboot
# ...after it returns:
[vps] bash /opt/ecfiler/scripts/deploy/post-reboot-check.sh   # expect all "ok"
```

---

## No longer needed

- **`railway login`** (old item 2): the purpose died with the trial. The API
  now lives on the VPS at $0/month (`docs/hosting-topology.md`); Railway
  destroys trial volumes 30 days after credit expiry, which disposes of the
  legacy environment, its env vars, and any pre-purge data without any action —
  recorded in `docs/credential-architecture.md` §4.

## Not blocked — done this session (session 3), so you can check the work

Full detail in the PR. **Suite: 541 passed, 0 failed** (was 481).

- **www.ecfiler.com works for a visitor again** — free tools (court directory,
  event codes, certificate generator) moved fully client-side and the site was
  redeployed; verified from an external browser. Item 2 above lights up the
  rest.
- **Hosting decided, deployed, documented**: API on the VPS (systemd, nginx,
  fail-closed auth, hardened unit), SQLite stays (attestation triggers ported
  unchanged), nightly offsite backups to the Mac with a passed restore test,
  Neon and paid options rejected with reasons — `docs/hosting-topology.md`.
- **Attestation store restructured (hash-don't-store)** + `DELETE /api/account`
  + `GET /api/export`, settings page wired, Privacy Policy now tells the truth,
  purge record completed honestly, counsel brief halved.
- **API surface closed**: auth on the AI endpoints (they were anonymous and
  spend money), drafts deletion scoped, the unauthenticated compress endpoint
  removed.
- **NEF round-trip dry-run proven end to end against the mock court**, runbook
  written; two real bugs fixed on the way (receipts dir creation; stage-pull
  QA auth).
- **Identity rewrite** per the settled rules, lint enforcing them, C4 PDF given
  a committed build path + parity test.
- **Florida gap item #3**: PDF/A enforcement pipeline (prohibited-element
  scan/scrub, 50 MB per-submission cap, filename rules), 28 tests from
  primary sources.

**Still not done, plainly: no filing has round-tripped to an NEF on a real
court system.** Item 5 (QA account) remains the only thing between the dry run
and the real one.
