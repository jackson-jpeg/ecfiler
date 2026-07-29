# Human queue

Everything here failed one of the blocking tests: money, identity/signature,
a credential that exists nowhere on either machine, an irreversible action on
production data, a lawyer's judgment, or the sandbox's permission layer.
Nothing is here because it was tedious.

Ordered by what unblocks the most downstream work. Session 4 collapsed three
rows (DNS, certbot, API key) into one command and turned the reboot row into
"just reboot" — the proof now writes itself.

| # | What | Why blocked | Time |
|---|---|---|---|
| 1 | [Deploy the truth-audited site to production](#0) | Sandbox (`vercel` over SSH blocked) | 90 s |
| 2 | [DNS records, then one activation command](#1) | Sandbox (DNS write blocked) | 3 min |
| 3 | [Paste the sandbox allow-rules block](#2) | Sandbox | 1 min |
| 4 | [Register the QA PACER account](#3) | Identity + CAPTCHA | 60 s |
| 5 | [Rotate the PACER password](#4) | Credential | 90 s |
| 6 | [Put `ANTHROPIC_API_KEY` on the Mac](#5) | Credential + sandbox | 60 s |
| 7 | [Subscribe to GovDelivery](#6) | CAPTCHA | 30 s |
| 8 | [Send the two outreach messages](#7) | Identity | 4 min |
| 9 | [Decide the entity question](#8) | Identity/legal | 5 min read |
| 10 | [Form the LLC + file the FL application](#9) | Money + signature | $625 |
| 11 | [Counsel review of Terms/Privacy](#10) | Lawyer | two questions |
| 12 | [Reboot the VPS](#11) | Kills live sessions incl. mine | 2 min |

---

## 1. Deploy the truth-audited site to production {#0}

**www.ecfiler.com is still serving the old build** — measured 2026-07-29:
the homepage says "3-Pass" and "Live Demo", `/courts` bounces anonymous
visitors to `/sign-in`, and `/tools` 404s. Every fix is on the branch,
Vercel's build of the exact commit already succeeded (the Preview
deployment is green — it's just behind Vercel SSO, so it can't stand in
for production), and a deploy-ready clone is staged on the Mac at
`~/ecfiler-s4-deploy`. The sandbox now blocks all `vercel` CLI use over
SSH, so the deploy is yours:

```
[MAC] cd ~/ecfiler-s4-deploy && vercel link --yes --project ecfiler && vercel --prod
```

Then confirm as an outsider (no login): `/courts` search works, `/tools`
lists six tools, the homepage says "Scripted demo" instead of "Live".
The repo check is `[MAC] cd ~/ecfiler-s4-deploy && bash scripts/deploy/verify-web-anon.sh`
pointed at a local build, or just click around in a private window.

---

## 2. DNS records, then one activation command {#1}

The API is live and healthy on the VPS; only the name is missing. Add the
records (the sandbox blocked this write twice), then the new script does
everything else — waits for propagation, runs certbot, drops the key,
restarts, and verifies from outside with a pass/fail table:

```
[MAC] vercel dns add ecfiler.com api A 187.77.218.14
[MAC] vercel dns add ecfiler.com api AAAA 2a02:4780:4:1c0b::1
[VPS] ANTHROPIC_API_KEY=sk-ant-... bash /opt/ecfiler/scripts/deploy/activate-api.sh
```

(A dedicated key from console.anthropic.com beats reusing the sanger-monitor
key — separate billing visibility — but either works. Omit the variable to
activate without AI endpoints; they answer 503 until a key lands.)

Until this runs, the site's `/api/*` calls answer 502 — the waitlist widget,
`/validate`, and signed-in backend features. Every other free tool is
client-side and already works. The verification half of the script was
proven against a local API instance — all six checks pass (ledger L10).

## 3. Paste the sandbox allow-rules block {#2}

Queue row 1 of sessions 2–3, now reduced to a paste: the exact JSON block
lives in `docs/nef-roundtrip-runbook.md` ("Sandbox allow-rules — paste this
first"). Merge it into `.claude/settings.json`. Without it, the live QA run
stalls at `session login` again — and `make qa-day MODE=live` now checks for
it and refuses to start, so the failure is at least loud and immediate.

## 4. Register the QA PACER account {#3}

**Still the gating item for proving ECFiler actually files.** The whole
staged→pull→file→NEF→attestation path round-trips against the mock CM/ECF
(`make qa-day` runs it in one command — ledger L09), and QA
day itself is now `make qa-day MODE=live STAGE=<code>` behind a six-point
preflight. Only this account is missing.

<https://qa-pacer.psc.uscourts.gov/pscof/registration.jsf>

Every field is pre-answered in `docs/outreach/c1-answer-sheet.md` — copy,
paste, solve the reCAPTCHA, submit. **Skip the credit-card section**; set
User Type to **Individual**. Blocked because it is an account registration
under your identity with terms assent, behind reCAPTCHA.

Once it activates overnight:

```
[MAC] printf '%s' 'QA-PASSWORD' | bash ~/ecfiler/scripts/mac/keychain-setup.sh 'QA-USERNAME'
[MAC] ~/ecfiler/scripts/mac/ecfiler-mac session login --qa
[MAC] cd ~/ecfiler && make qa-day MODE=live
```

## 5. Rotate the PACER password {#4}

The production PACER password was exposed in a prior session transcript.
Treat it as compromised (R-002).

<https://pacer.uscourts.gov/my-account-billing/manage-my-account-login> →
Settings → Change Password. Then update it on the Mac (piped, never in
shell history):

```
[MAC] printf '%s' 'NEW-PASSWORD' | bash ~/ecfiler/scripts/mac/keychain-setup.sh jmsanger
```

## 6. Put `ANTHROPIC_API_KEY` on the Mac {#5}

`ecfiler check` on the Mac is 10/12; the two failures clear with one file:

```
[MAC] printf 'export ANTHROPIC_API_KEY=%s\n' 'sk-ant-...' > ~/.ecfiler/env.sh
[MAC] chmod 600 ~/.ecfiler/env.sh
[MAC] ~/ecfiler/scripts/mac/ecfiler-mac check
```

## 7. Subscribe to GovDelivery {#6}

<https://public.govdelivery.com/accounts/USFEDCOURTS/subscriber/new?topic_id=USFEDCOURTS_1821>

Email `realjacksons@gmail.com`, solve the MTCaptcha, submit, click the
confirmation link. Blocked only by the CAPTCHA.

## 8. Send the two outreach messages {#7}

**C2 — AO developer mailbox.** The Gmail draft in your account
(`developers@psc.uscourts.gov`) is final — it matches the repo text (checked in session 3), untouched since. Read it and hit send, ideally after item 6 so
"I'm subscribed to the developer updates list" is true.

**C5 — M.D. Fla. clerk.** Web form, not email:
<https://www.flmd.uscourts.gov/webforms/contact-cmecf> — paste-ready answers
in `docs/outreach/c5-submission-sheet.md`. Needs your phone number, which is
nowhere in the repo.

The identity rules are settled and lint-enforced (session 3): true
profession in personal capacity, employer never named or implied, singular
voice, no ECFiler-in-use claims. Skim `tests/test_copy_lint.py`'s header
before sending if you want the reasoning.

## 9. Decide the entity question {#8}

`docs/fl/entity-recommendation.md` — the recommendation is **ECFiler LLC, a
single-member Florida LLC, formed now**, defended against Delaware and
against waiting. Read it and say yes or overrule it. Everything in item 10
waits on the name.

Sunbiz sits behind Cloudflare bot protection and refused both machines, so
the name-availability check is yours:
<https://search.sunbiz.org/Inquiry/CorporationSearch/ByName>.

## 10. Form the LLC and file the Florida application {#9}

Money and your signature. Roughly **$625** total. The packet is
signature-ready: the filled PDF reproduces from
`scripts/fill_fl_tpv_application.py` (fill script re-run this session), and
`docs/fl/application-packet-checklist.md` lists every remaining blank — all
of them are entity name, signatures, dates, phone, or street address.

- **LLC** (~$125): <https://efile.sunbiz.org/llc_file.html>. Registered
  agent = yourself, principal address = your Tampa address.
- **Application** ($500): confirm the check payee with the Authority
  (support@myflcourtaccess.com / 850-577-4609) before writing it.
- **References**: three request emails in
  `docs/fl/drafts/reference-request-emails.md` (third is Hostinger — note
  the account-name caveat in that file). Send these *before* mailing.
- Engineering is ahead of the paperwork: gap items #2 (domain model), #3
  (PDF/A enforcement), and #4 (ECF 4.01 message layer, this session) are
  built and tested; the next build items need the post-approval XSDs.

## 11. Counsel review of Terms and Privacy {#10}

`docs/legal/counsel-review-brief.md`. Q1 (UPL) and Q2 (liability stack)
remain the genuine lawyer questions; Q3/Q4 collapsed to "here is what we
did" in session 3. Both pages still carry the `LEGAL REVIEW REQUIRED before
deploy` banner. Session 4 note for counsel: Terms §5 no longer claims a
"3-pass" verification system (nothing implemented it) — it now describes
the real AI analysis + five-point readiness check; §10 states expressly
that Pro is not yet purchasable.

## 12. Reboot the VPS {#11}

Now genuinely one step: `ecfiler-post-reboot.service` is installed and
enabled, so the boot runs the check itself and writes a timestamped result.

```
[VPS] reboot
# ...after it returns, read the proof:
[VPS] cat /var/log/ecfiler/post-reboot-latest.result
```

The reboot kills every live Claude session on the box — including the one
doing the work — so it is yours, whenever convenient.

---

## Done in session 4 (check the work)

Full detail in the PR. **Suite: 605 passed, 0 failed** (was 546).

- **The marketing site stopped lying.** Free tools actually public (the
  (app) auth gate was redirecting /courts to /sign-in), plus new public
  /tools, /events, /fees, /redaction pages — the last two are client-side
  ports with data-parity tests. Checked as an anonymous outsider with
  Playwright; that check now runs in CI.
- **Claims deleted rather than softened**: 3-pass verification, Stripe
  billing, hosted CM/ECF filing, timing stats, sealed-filing-in-one-click,
  competitor pricing. `docs/claims-register.md` maps every surviving claim
  to code + test, and `tests/test_claims_register.py` enforces it.
- **Every court number derives from the registry data**; the 207
  decomposes explicitly (90+4 districts, 94 bankruptcy, 13 courts of
  appeals, 3 BAPs, 3 national courts).
- **activate-api.sh**, **make qa-day**, **ECF 4.01 message layer**,
  **self-documenting reboot** — rows 1, 2, 3, 11 above got shorter.

**Still not done, plainly: no filing has round-tripped to an NEF on a real
court system.** Item 4 (QA account) remains the only thing between the dry
run and the real one.
