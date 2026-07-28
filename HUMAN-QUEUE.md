# Human queue

Everything here failed one of the five blocking tests: money, identity/signature,
a credential that exists nowhere on either machine, an irreversible action on
production data, or a lawyer's judgment. Nothing is here because it was tedious.

Ordered by what unblocks the most downstream work. **Total under 15 minutes of
typing**, plus the money and the lawyer.

| # | What | Why blocked | Time |
|---|---|---|---|
| 1 | [Rotate the PACER password](#1) | Credential | 90 s |
| 2 | [`railway login`](#2) | Credential | 30 s |
| 3 | [Register the QA PACER account](#3) | Identity + CAPTCHA | 60 s |
| 4 | [Subscribe to GovDelivery](#4) | CAPTCHA | 30 s |
| 5 | [Send the two outreach messages](#5) | Identity | 4 min |
| 6 | [Put `ANTHROPIC_API_KEY` on the Mac](#6) | Credential | 60 s |
| 7 | [Decide the entity question](#7) | Identity/legal | 5 min read |
| 8 | [Form the LLC + file the FL application](#8) | Money + signature | $625 |
| 9 | [Counsel review of Terms/Privacy](#9) | Lawyer | 20 min of theirs |

---

## 1. Rotate the PACER password {#1}

The production PACER password was exposed in a prior session transcript. Treat it
as compromised. This is first because everything else touching PACER inherits it.

<https://pacer.uscourts.gov/my-account-billing/manage-my-account-login> → Settings
→ Change Password.

Then update it on the Mac (piped, never in shell history or argv):

```
[mac] printf '%s' 'NEW-PASSWORD' | bash ~/ecfiler/scripts/mac/keychain-setup.sh jmsanger
```

The VPS copy in `~/.ecfiler` is stale after rotation and can be left to rot or
deleted; the VPS never files. Logged as R-002.

## 2. `railway login` {#2}

**The hosted API is not deployed.** Every path on
`ecfiler-production.up.railway.app` returns Railway's edge 404 with
`x-railway-fallback: true` — no service is running. The frontend at
`www.ecfiler.com` is live and still points at that dead host (R-009).

The stored token in `~/.railway/config.json` returns `Unauthorized`, and
`railway login` opens a browser, so I could not authenticate, deploy, inspect
variables, or see whether volume snapshots still exist.

```
[mac] ~/.railway/bin/railway login
```

Then tell me and I will do the rest unattended: link the project, set
`CLERK_ISSUER=https://clerk.ecfiler.com` (JWKS verified reachable, HTTP 200),
deploy, confirm the API boots and rejects unauthenticated requests, and only then
remove `ECFILER_ENCRYPTION_KEY` and delete the pre-purge snapshots after
verifying a current backup. Snapshot deletion is irreversible, so it happens
last and only after a healthy deploy.

## 3. Register the QA PACER account {#3}

**This is the gating item for proving ECFiler actually files.** No QA filing can
round-trip to an NEF until this account exists and activates overnight.

<https://qa-pacer.psc.uscourts.gov/pscof/registration.jsf>

Every field is pre-answered in `docs/outreach/c1-answer-sheet.md` — copy, paste,
solve the reCAPTCHA, submit. **Skip the credit-card section**; QA searches are
free. Set User Type to **Individual**, not an attorney type.

Blocked because it is an account registration under your identity with terms
assent, and because the form is reCAPTCHA-gated. I do not defeat anti-bot
controls on federal systems.

Once it activates:

```
[mac] printf '%s' 'QA-PASSWORD' | bash ~/ecfiler/scripts/mac/keychain-setup.sh 'QA-USERNAME'
[mac] ~/ecfiler/scripts/mac/ecfiler-mac session login --qa
```

## 4. Subscribe to GovDelivery {#4}

<https://public.govdelivery.com/accounts/USFEDCOURTS/subscriber/new?topic_id=USFEDCOURTS_1821>

Email `realjacksons@gmail.com`, solve the MTCaptcha, submit, then click the
confirmation link it sends. Blocked only by the CAPTCHA. The topic ID is carried
by the URL, so there is nothing to pick.

## 5. Send the two outreach messages {#5}

**C2 — AO developer mailbox.** A Gmail draft is already in your account,
addressed to `developers@psc.uscourts.gov`, subject and body final. Read it and
hit send. Ideally after item 4, so "I'm subscribed to the developer updates list"
is true.

**C5 — M.D. Fla. clerk.** *There is no email draft, deliberately:* the district
does not publish a CM/ECF email address, it publishes a web form. A draft to a
guessed address would have gone nowhere.

<https://www.flmd.uscourts.gov/webforms/contact-cmecf> — answers in
`docs/outreach/c5-submission-sheet.md`. Needs your phone number, which the form
requires and which is nowhere in the repo.

> **Read before sending.** Both letters previously described you as "a docketing
> specialist at a national law firm," and C5 went further, asserting a filing
> practice with staff that does not exist. None of that was true. I rewrote all
> of it — plus the white paper and the Florida cover letter — to the honest
> independent-developer framing, and added a lint (`tests/test_copy_lint.py`)
> that fails the build if it returns. Worth a look, since it changes how these
> read.

## 6. Put `ANTHROPIC_API_KEY` on the Mac {#6}

`ecfiler check` on the Mac is **10/12**. The two failures are `anthropic_key` and
`anthropic_api`; both clear with this one file. Everything else passes, including
`pacer` against the real Keychain.

Writing the key to the Mac was blocked by the sandbox, so:

```
[mac] printf 'export ANTHROPIC_API_KEY=%s\n' 'sk-ant-...' > ~/.ecfiler/env.sh
[mac] chmod 600 ~/.ecfiler/env.sh
[mac] ~/ecfiler/scripts/mac/ecfiler-mac check     # expect 12/12
```

## 7. Decide the entity question {#7}

`docs/fl/entity-recommendation.md` — the recommendation is **ECFiler LLC, a
single-member Florida LLC, formed now**, defended against Delaware and against
waiting. Read it and say yes or overrule me. Everything in item 8 waits on the
name.

Sunbiz sits behind Cloudflare bot protection and refused both machines, so the
name-availability check is yours: <https://search.sunbiz.org/Inquiry/CorporationSearch/ByName>.

## 8. Form the LLC and file the Florida application {#8}

Money and your signature. Roughly **$625** total.

- **LLC** (~$125): <https://efile.sunbiz.org/llc_file.html>. Registered agent =
  yourself, principal address = your Tampa address.
- **Application** ($500): `docs/fl/Third_Party_Vendor_Application_FILLED.pdf` is
  filled except entity name, both signature blocks, dates, phone, and street
  address — all of which are your signature or personal data.
  `docs/fl/application-packet-checklist.md` lists every blank and what encloses
  with it. Confirm the check payee with the Authority
  (support@myflcourtaccess.com / 850-577-4609) before writing it; the form never
  states the payee.
- **References**: three request emails ready in
  `docs/fl/drafts/reference-request-emails.md`. Send these *before* mailing, so
  the references are warned.

## 9. Counsel review of Terms and Privacy {#9}

`docs/legal/counsel-review-brief.md` reduces this to four questions that
genuinely need a lawyer, with everything else marked skim-only.

**Two of the four are not really legal questions — they are things the code and
the copy currently disagree about, and they are worth your attention before a
lawyer's:**

- The Privacy Policy says server-stored credentials "were permanently purged in
  July 2026," but the purge record is unfinished and the snapshots may still
  exist (item 2). Do not publish that sentence until it is true. (R-006)
- The policy promises self-serve deletion and machine-readable export; the API
  implements neither, and the append-only attestation log cannot honour the
  30-day purge promise as written. Either build them or redraft. (R-007)

Both pages still carry the `LEGAL REVIEW REQUIRED before deploy` banner, so
nothing is live.

---

## Not blocked — done this session, listed so you can check my work

Pushed to `master` (the 13 commits) and to a branch with a draft PR (this
session's work). Full detail in the PR description.

- **Suite: 481 passed, 0 failed** — including 3 that were red on master.
- macOS Keychain backend for non-GUI sessions; `ecfiler check` 10/12 on the Mac,
  `audit verify` clean.
- Persistent PACER session (`ecfiler session login` / `status`). Headed Chromium
  with a surviving profile is **measured working** on the Mac. Session lifetime
  is instrumented and honestly reports "unknown" until item 3 gives it something
  to measure. `docs/filing-topology.md`.
- EPA window monitor: installed, running under systemd, forced-positive verified
  firing on both watched pages and delivering. The VPS has no mail transport, so
  it delivers to the Sanger dashboard and macOS notifications; add an SMTP
  credential and it will email too.
- Florida domain model: UCN and submission lifecycle built from the primary
  sources, 61 tests.
- White paper rendered to PDF, identity corrected, footnote 4 given a verified
  real citation.

**Not done, and I want to be plain about it: no filing has round-tripped to an
NEF.** The code and the topology are built and tested; item 3 is what makes the
test possible.
