# Filing topology — which machine does what, and what happens when the session dies

Status as of 2026-07-28. Everything below marked **measured** was observed on
this hardware; everything marked **unverified** is honestly labelled as such.
Nothing here is inferred from PACER documentation that we have not tested.

---

## 1. The two machines

| | VPS (Linux, Hostinger) | MacBook Air (macOS 26.3) |
|---|---|---|
| Role | Development, tests, docs, monitors | **The only machine that files** |
| Keyring | plaintext `keyrings.alt` file backend | real macOS Keychain |
| Browser | headless Chromium only | headed Chromium, **measured working** over SSH |
| PACER credential | present (accepted risk, `docs/risk-register.md` R-001) | `ecfiler.keychain-db`, R-003 |
| Reaches a court | **never** | yes, under the filer's own session |

The split is not stylistic. A filing session is a human's authenticated session
with a federal court; it needs a real keychain and a real display, and both live
on the Mac. The VPS runs the things that must run daily whether or not a laptop
is open — currently the EPA window monitor
(`scripts/epa-window-monitor.sh`, systemd timer `ecfiler-epa-monitor.timer`).

### Running ECFiler on the Mac

```
[mac] ~/ecfiler/scripts/mac/ecfiler-mac check
```

`scripts/mac/ecfiler-mac` is required for any **non-GUI** invocation (SSH, cron,
launchd). In those sessions macOS creates a fresh security session in which
every keychain is locked, and the stock `keyring` macOS backend then fails with
`errSecInteractionNotAllowed` (-25308) — it cannot address an alternate keychain
(keyring#623) and its search aborts as soon as it touches the locked login
keychain. The wrapper unlocks the dedicated `ecfiler.keychain-db`, exports
`ECFILER_KEYCHAIN`, and `ecfiler/keychain_macos.py` then reads the credential
through `/usr/bin/security`, which has neither limitation. From a GUI Terminal
the plain `~/ecfiler/.venv/bin/ecfiler` works and this is all inert.

**Measured 2026-07-28:** `ecfiler check` on the Mac reports 10/12 passing.
The two failures are `anthropic_key` and `anthropic_api`, both of which need
`ANTHROPIC_API_KEY` in `~/.ecfiler/env.sh` — a queue item, not a defect.
`pacer` passes against the real Keychain, and `ecfiler audit verify` reports the
attestation chain intact.

---

## 2. PACER MFA — the actual problem and the actual answer

PACER's Central Sign-On enforces multi-factor authentication on production
accounts. An unattended process therefore cannot authenticate from scratch:
something has to read a code from a phone. **We do not attempt to defeat this**,
and no design below tries to.

The answer is to persist the session that a human login produces, and to be
honest with the operator when it lapses.

### Option (a) — headed Chromium with a persistent profile → **adopted**

**Measured 2026-07-28.** A headed Chromium launched over SSH on the Mac starts
successfully and its `launch_persistent_context` profile survives across
separate runs (verified with a `localStorage` probe written in run 1 and read
back in run 2). This is the mechanism the design rests on, and it works.

`BrowserSession(user_data_dir=...)` switches to a persistent context; the CSO
cookies land in `~/.ecfiler/pacer-profile`, mode 0700.

### Option (b) — first-login MFA handoff → **adopted, built**

```
[mac] ~/ecfiler/scripts/mac/ecfiler-mac session login          # production
[mac] ~/ecfiler/scripts/mac/ecfiler-mac session login --qa     # QA
```

Opens a headed browser at the CSO login page and waits (default 10 minutes) for
the page to reach an authenticated state. **Jackson types the password and the
MFA code; ECFiler types neither.** Neither the password nor the second factor
passes through the ECFiler process at any point on this path. On success the
session is persisted and the event is recorded.

### Option (c) — session lifetime → **instrumented, not yet known**

This is the part it would be easy to lie about. PACER does not publish the
browser CSO session timeout, and we have not yet been able to measure it,
because measuring it requires an account to log into and the QA account does not
exist yet (see §4). So the code refuses to assume:

```
[mac] ~/ecfiler/scripts/mac/ecfiler-mac session status
```

probes the persisted session headlessly, appends the observation to
`~/.ecfiler/pacer-session.jsonl` with the session's age, and reports the
**longest age at which the session was still valid** and the **shortest age at
which it was found expired**. With no observations it prints
`Measured lifetime: unknown — no observations yet`, which is the truth today.

Do not confuse this with the ~60-minute figure in `ecfiler/pacer_auth.py`. That
is the documented lifetime of a token from the PACER *authentication API*, a
different mechanism with a different expiry. The browser session is what matters
for filing and its lifetime is currently unmeasured.

---

## 3. What happens when the session dies mid-deadline

The failure that matters is not "the session expired" — it is "the session
expired between the fee screen and the submit button, at 11:52 p.m. on the day a
response is due." The rules, in order of importance:

1. **Never auto-reauthenticate mid-filing.** A silent re-login would require
   holding the password and satisfying MFA unattended. Neither happens.
2. **Fail loudly and early.** `session status` is cheap; run it *before* a
   filing run, not after the documents are uploaded. A dead session found at
   the start costs one interactive login; found at the submit step it costs a
   half-completed docket entry.
3. **A half-submitted filing is the dangerous state,** not a refused one. If the
   session dies after documents are uploaded but before submission completes,
   ECFiler stops and reports the last confirmed step from the per-filing audit
   trace (`~/.ecfiler/traces/trace_<label>_<stamp>.zip`). The operator checks
   the docket before retrying, because CM/ECF has no idempotency key
   (this is Requirement 3 in `docs/outreach/c4-white-paper.md`) and a blind
   retry is how duplicate entries and duplicate fees happen.
4. **The deadline belongs to the human.** ECFiler has no mechanism to file
   without a person present and should never appear to promise one. If a
   session dies at 11:52 p.m., the correct outcome is a person being told
   immediately and clearly, not a queue that retries at 3 a.m.

Recommended operating practice: run `session login` at the start of a filing
session rather than discovering expiry under time pressure, and re-run it
whenever `session status` reports expired.

---

## 4. What is not proven yet

Stated plainly, because "tests pass" is not "it filed":

- **No end-to-end staged filing has round-tripped to an NEF.** Still true after
  the first attended attempt (2026-07-29, ledger L16). The QA PACER account now
  exists, authenticates, and seeded a live browser session; all twelve preflight
  gates passed on the filing machine; the staged package pulled down as a draft.
  The run then stopped at the hosted→local seam — the draft did not parse as a
  `Filing` (R-013) — and a second bug in the same path had the draft naming the
  wrong court (R-012). No browser reached the court, no receipt or trace exists,
  and the attestation chain on the filing machine is still empty. Both bugs are
  fixed and pinned; the run has not been repeated. **This document should not be
  read as claiming a filing has happened.**
- **Session lifetime is unknown** (§2c). Measurement has started — the QA
  session store has two observations — but nothing has expired yet, so there is
  no lower bound.
- Production PACER filing is out of scope by policy this session, and the
  production credential is treated as compromised until rotated
  (`docs/risk-register.md` R-002).

The honest summary: the topology is designed, the code is built and unit-tested,
the browser mechanism is measured working, and the QA account is live. What the
first attended run showed is that the parts nobody had driven end to end — the
seam between the hosted package and the local CLI, and the court identity that
crosses it — were the parts that were broken. Both are fixed with structural
guarantees rather than care, and the next attended run is what turns any of
this into a proven filing.
