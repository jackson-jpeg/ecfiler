# NEF round-trip runbook

*Written 2026-07-28. The QA PACER account (HUMAN-QUEUE item 3) is the only
missing piece. Everything below the fold is proven against the mock CM/ECF;
activation day is execution, not building.*

## What is already proven (the dry run)

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

## QA day — the exact sequence

Prerequisite: HUMAN-QUEUE item 3 (register the QA account, activates
overnight) and the sandbox-permission row (see queue row 1 — two of these
commands were sandbox-blocked in session 2 and will block again without it).

```
# One-time, after the QA account activates (from HUMAN-QUEUE item 3):
[mac] printf '%s' 'QA-PASSWORD' | bash ~/ecfiler/scripts/mac/keychain-setup.sh 'QA-USERNAME'
[mac] ~/ecfiler/scripts/mac/ecfiler-mac session login --qa        # headed browser, human solves login
[mac] ~/ecfiler/scripts/mac/ecfiler-mac session status --qa       # expect: live, 1 observation

# Stage on the hosted app (or use an already-staged package):
#   www.ecfiler.com → /file → stage → note the stage code

# Pull and file:
[mac] ~/ecfiler/scripts/mac/ecfiler-mac stage-pull <STAGE-CODE>   # token from the web session
[mac] ~/ecfiler/scripts/mac/ecfiler-mac                            # interactive workflow, QA court,
                                                                   # CONFIRM + YES gates, NEF captured

# Prove it:
[mac] ~/ecfiler/scripts/mac/ecfiler-mac audit verify               # chain ok, includes the NEF record
[mac] ls ~/.ecfiler/receipts/                                      # receipt with chain-head anchor
[mac] ls ~/.ecfiler/traces/                                        # trace zip for the repo record
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
