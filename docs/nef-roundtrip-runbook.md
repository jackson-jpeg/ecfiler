# NEF round-trip runbook

*Written 2026-07-28. The QA PACER account (HUMAN-QUEUE item 3) is the only
missing piece. Everything below the fold is proven against the mock CM/ECF (ledger L09);
activation day is execution, not building.*

## What is already proven (the dry run — ledger L09)

`tests/test_browser_e2e.py::TestStagedToNefRoundTrip` runs the entire path
end to end with the mock CM/ECF standing in for the QA environment, and it
passes:

1. **Stage on the hosted API** — `POST /api/filing/stage` with the attorney
   attestation; server refuses without it (422). A `kind="staged"`
   attestation lands in the server chain and `verify_chain()` passes.
2. **Pull with the real CLI** — `ecfiler stage-pull <code>` against the API
   saves the package as draft `staged_<case>` on the filing machine
   (`ECFILER_DEV_USER` provides dev-mode auth for QA dry-runs; production
   uses the Clerk session token).
3. **File in the browser** — Playwright walks the full ten-step CM/ECF flow
   (tips → case → caption → event → party → upload → docket text → confirm →
   submit) to the receipt page.
4. **Capture the NEF** — `court.get_receipt_info(page)` extracts docket
   number 58 and the full page text containing "Notice of Electronic
   Filing"; `browser.save_receipt()` archives the receipt HTML.
5. **Attest the submission** — a `kind="submitted"` record with
   `nef_text` set is appended; the chain-head hash is written into the
   saved receipt (`<!-- ECFiler attestation chain head: … -->`), the chain
   verifies end to end, and the NEF text round-trips from the payload store.

Attestation-record shape for a real NEF (confirmed by the dry run):
`kind="submitted"`, `attestor_name`, the two-gate attestation text,
`payload` (court, case, event, docket text, documents, sealing),
`nef_sha256` in the chain, raw `nef_text` in the deletable payload store,
`trace_path` pointing at the trace zip.

`ecfiler session status` behaves correctly with no profile ("No persisted
session."), and the observation store (JSONL append, lifetime accounting) is
covered by `tests/test_pacer_session.py`.

## Sandbox allow-rules — paste this first (queue row 1)

Two Mac commands were sandbox-blocked in session 2 and will block again the
moment the live run starts (launching the headed browser at the PACER login
page over the tunnel; writing the Mac key file). The fix is one paste.
Merge this block into `.claude/settings.json` at the repo root (or
`/root/.claude/settings.json` to apply globally) — if the file already has a
`permissions.allow` array, append the two strings to it:

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

`make qa-day MODE=live` checks for this and refuses to start without it.

## The QA target (established 2026-07-29 — ledger L15)

The runbook previously assumed a generic "QA court". Measured with the live
QA account:

- The account lives in the **PACER QA realm**: CSO at
  `qa-login.uscourts.gov` (the `qa-pacer.login` host in older notes does not
  resolve). `session auth-test --qa` confirms the credential end to end.
- Per-court training databases (`ecf-train.<court>.uscourts.gov`) resolve in
  DNS but **refuse connections** from both machines — they are not the
  target.
- The QA realm publishes its own court roster at
  `qa-pacer.uscourts.gov/file-case/court-cmecf-lookup`. Its `*.aocms.uscourts.gov`
  test courts are firewalled from here. The reachable district target is:

  **Az Test District Court (roster code AZTTDC)**
  `https://ecf.tc1d.aztc.uscourts.gov` — District CM/ECF v10.8.4, login
  federated with `qa-login.uscourts.gov` (verified from the Mac — ledger L15).

- Stage with `court_id=azd` (standard district selectors); the live run
  overrides every URL with `TARGET=https://ecf.tc1d.aztc.uscourts.gov`.
  The filing case number must exist in that court — after login, look one
  up via the court's Query menu before staging.

## QA day — one command

Prerequisite: HUMAN-QUEUE's QA-account row (register, activates overnight)
and the allow-rules paste above.

```
# One-time, after the QA account activates:
[MAC] printf '%s' 'QA-PASSWORD' | bash ~/ecfiler/scripts/mac/keychain-setup.sh 'QA-USERNAME'
[MAC] ~/ecfiler/scripts/mac/ecfiler-mac session login --qa
[MAC] cd ~/ecfiler && make qa-day MODE=live

# Stage a filing at www.ecfiler.com → /file → note the stage code, then:
[MAC] cd ~/ecfiler && make qa-day MODE=live STAGE=<code> TARGET=https://ecf.tc1d.aztc.uscourts.gov
```

Hosted staging needs the api.ecfiler.com DNS row (HUMAN-QUEUE #1). Until it
runs, stage against a local API instead:

```
[MAC] cd ~/ecfiler && ECFILER_DEV_AUTH=1 .venv/bin/python -m uvicorn ecfiler.api.app:app --port 8001 &
[MAC] # stage via the API (attestation required), note the stage_code it returns
[MAC] ECFILER_SERVER=http://127.0.0.1:8001 ECFILER_DEV_USER=qa-day ~/ecfiler/scripts/mac/ecfiler-mac stage-pull <code>
```

`make qa-day MODE=live` (scripts/mac/qa-day.sh) gates on six preconditions —
macOS + venv, PACER credential readable from `ecfiler.keychain-db`, headed
Chromium profile with a live persisted `--qa` session, the sandbox
allow-rules above, receipts dir writable, attestation chain verifying — and
refuses to start if any is red. With a `STAGE` code it pulls the package,
hands off to the attended workflow (the CONFIRM and YES gates stay human),
then prints `audit verify` plus the receipt and trace listings.

The dry run (no preconditions, runs anywhere including the VPS):

```
[VPS] cd ~/ecfiler && make qa-day
[MAC] cd ~/ecfiler && make qa-day
```

Then: copy the receipt, `audit verify` output, and the trace into
`docs/qa-roundtrip/` and update `docs/filing-topology.md` §4 ("What is not
proven yet") — that section's first bullet stops being true at that moment.

Production PACER remains out of scope until the round trip is proven **and**
the production credential is rotated (queue item 1, R-002).

## Failure handling

Unchanged from `docs/filing-topology.md`: ECFiler reports the last confirmed
step from the trace zip; CM/ECF has no idempotency key, so no blind retries —
duplicate submissions mean duplicate docket entries and duplicate fees. The
deadline belongs to the human.
