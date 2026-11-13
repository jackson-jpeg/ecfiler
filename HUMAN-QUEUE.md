# Human queue

Everything here failed one of the blocking tests: money, identity/signature,
a credential that exists nowhere on either machine, an irreversible action on
production data, a lawyer's judgment, or the sandbox's permission layer.
Nothing is here because it was tedious.

Ordered by what unblocks the most downstream work. Session 4 collapsed three
rows (DNS, certbot, API key) into one command and turned the reboot row into
"just reboot". Session 5 **deleted the "deploy the site" row permanently**:
PR #1 merged to master, production deploys from every master push via the
Vercel git integration (ledger L13), and the outside-in smoke passed 18/18
(ledger L14) — deploying the site is now `git push`, not a queue item.
Session 6 closed the QA-account row (it exists and authenticates) and the
allow-rules paste row (pasted, scoped); both were replaced by what came
after them — re-running the filing, and taking the SSH rules back out.

| # | What | Why blocked | Time |
|---|---|---|---|
| 1 | [DNS records, then one activation command](#1) | Sandbox (DNS write blocked) | 3 min |
| 2 | [Remove the scoped SSH allow-rules after QA day](#2) | Your laptop, your call | 1 min |
| 3 | [Request e-filing privileges for AZTTDC, then re-run the filing](#3) | Web form + a court's approval | 10 min, then days |
| 4 | [Rotate the PACER password](#4) | Credential | 90 s |
| 5 | [Put `ANTHROPIC_API_KEY` on the Mac](#5) | Credential + sandbox | 60 s |
| 6 | [Subscribe to GovDelivery](#6) | CAPTCHA | 30 s |
| 7 | [Send the two outreach messages](#7) | Identity | 4 min |
| 8 | [Decide the entity question](#8) | Identity/legal | 5 min read |
| 9 | [Form the LLC + file the FL application](#9) | Money + signature | $625 |
| 10 | [Counsel review of Terms/Privacy](#10) | Lawyer | two questions |
| 11 | [Reboot the VPS](#11) | Kills live sessions incl. mine | 2 min |

---

## 1. DNS records, then one activation command {#1}

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

## 2. Remove the four scoped SSH allow-rules when QA day is over {#2}

**This replaces the old "paste the allow-rules" row — the rules are in
place.** You allowed them for an attended run and asked for a row to take
them back out. Four prefixes, in two files:

```json
"Bash(ssh macbook-tunnel /Users/jackson/ecfiler/scripts/mac/ecfiler-mac:*)"
"Bash(ssh macbook-tunnel git -C /Users/jackson/ecfiler:*)"
"Bash(ssh macbook-tunnel ls:*)"
"Bash(ssh macbook /Users/jackson/ecfiler/scripts/mac/ecfiler-mac:*)"
```

- `[VPS]` `/root/.claude/settings.json` — the global file on this machine, so
  I can edit it myself when you say the word.
- repo `.claude/settings.json` — committed; removing it is a normal commit.

They are deliberately not `Bash(ssh macbook:*)`, which would be arbitrary
command execution on your laptop. `make qa-day MODE=live` checks that *some*
`Bash(ssh macbook` rule exists and refuses to start otherwise, so pulling
them ends VPS-driven QA runs until they go back — which is the point.

## 3. Request e-filing privileges for AZTTDC, then re-run the filing {#3}

**Start the request today — the wait is the long pole.** The 2026-07-30 run
(ledger L20) got further than anything has: PDF validated, redaction scan
clean, review gate rendered with the right court and case, court invariant
passed, PACER authenticated, case number entered and accepted. It stopped at
the court's own permission wall. The QA account can *read* the Az Test
District Court and cannot file in it — CM/ECF served Query, Reports,
Utilities, Help, Log Out and no Civil or Criminal menu. Filing is a separate
privilege each court grants and must approve, on a multi-day turnaround
(R-015).

Numbered steps are in `docs/nef-roundtrip-runbook.md` → "Requesting e-filing
privileges". It starts here, and steps 2–5 are a web form, which is why this
is your row:

```
[MAC] open https://qa-pacer.psc.uscourts.gov/pscof/manage/maint.jsf
```

Check for approval without attempting a filing:

```
[MAC] ~/ecfiler/scripts/mac/ecfiler-mac session filing-access --qa --court azttdc
```

Once it answers `✓ This account may file in azttdc`, the re-run command is
at the top of the runbook. The proof list when it finishes: NEF text and
docket number in the receipt, a `kind="submitted"` attestation carrying that
NEF text, both chains verifying, and the chain head anchored in the saved
receipt.

Expect the approved run to find more. Everything past the case lookup has
only ever run against the mock, and the route from the Civil menu to an
event list is deliberately unbuilt until someone can see that screen
(R-014). The earlier bugs from 2026-07-29 (R-012 wrong court, R-013 unusable
staged package) are fixed and pinned. Nothing has been filed; the chain on
the filing machine is still empty.

**Rotate the QA credential when you're done with it** (your own plan — it
was shared in chat, so treat it as exposed):

```
[MAC] printf '%s' 'NEW-QA-PASSWORD' | bash ~/ecfiler/scripts/mac/keychain-setup.sh 'ecfilercom'
```

## 4. Rotate the PACER password {#4}

The production PACER password was exposed in a prior session transcript.
Treat it as compromised (R-002).

<https://pacer.uscourts.gov/my-account-billing/manage-my-account-login> →
Settings → Change Password. Then update it on the Mac (piped, never in
shell history):

```
[MAC] printf '%s' 'NEW-PASSWORD' | bash ~/ecfiler/scripts/mac/keychain-setup.sh jmsanger
```

## 5. Put `ANTHROPIC_API_KEY` on the Mac {#5}

`ecfiler check` on the Mac is 10/12; the two failures clear with one file:

```
[MAC] printf 'export ANTHROPIC_API_KEY=%s\n' 'sk-ant-...' > ~/.ecfiler/env.sh
[MAC] chmod 600 ~/.ecfiler/env.sh
[MAC] ~/ecfiler/scripts/mac/ecfiler-mac check
```

## 6. Subscribe to GovDelivery {#6}

<https://public.govdelivery.com/accounts/USFEDCOURTS/subscriber/new?topic_id=USFEDCOURTS_1821>

Email `realjacksons@gmail.com`, solve the MTCaptcha, submit, click the
confirmation link. Blocked only by the CAPTCHA.

## 7. Send the two outreach messages {#7}

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

## 8. Decide the entity question {#8}

`docs/fl/entity-recommendation.md` — the recommendation is **ECFiler LLC, a
single-member Florida LLC, formed now**, defended against Delaware and
against waiting. Read it and say yes or overrule it. Everything in item 9
waits on the name.

Sunbiz sits behind Cloudflare bot protection and refused both machines, so
the name-availability check is yours:
<https://search.sunbiz.org/Inquiry/CorporationSearch/ByName>.

## 9. Form the LLC and file the Florida application {#9}

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

## 10. Counsel review of Terms and Privacy {#10}

`docs/legal/counsel-review-brief.md`. Q1 (UPL) and Q2 (liability stack)
remain the genuine lawyer questions; Q3/Q4 collapsed to "here is what we
did" in session 3. Both pages still carry the `LEGAL REVIEW REQUIRED before
deploy` banner. Session 4 note for counsel: Terms §5 no longer claims a
"3-pass" verification system (nothing implemented it) — it now describes
the real AI analysis + five-point readiness check; §10 states expressly
that Pro is not yet purchasable.

## 11. Reboot the VPS {#11}

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
court system.** Item 3 is what stands between the dry run and the real one —
and as of 2026-07-30 it is no longer a code problem. Two attended runs have
now reached a real court; the second one ran out of road at a permission a
court has to grant (R-015).
