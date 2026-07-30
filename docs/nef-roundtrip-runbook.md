# NEF round-trip runbook

*Written 2026-07-28, rewritten 2026-07-29 after the first attended run.
The QA account is live; every step up to the browser is proven (ledger L15,
L19) on the real machines. The filing itself has not happened — the
first attempt stopped at two bugs in the hosted→local seam (L16, L17), both
since fixed. What follows is the re-run.*

## The re-run, one command — blocked on e-filing privileges

**Read the next section first.** As of 2026-07-30 this command cannot
succeed: the QA account may read the target court but not file in it, and
the run now stops and says so within seconds (ledger L20). Once
`session filing-access --qa --court azttdc` reports filing access, this is
the command.

The package is staged and its pull is pre-verified (ledger L19) on the filing
machine. At the workflow menu choose **[2] Resume Draft**; the document is
`/Users/jackson/ecfiler/docs/qa-roundtrip/sample-motion.pdf`:

```
[MAC] cd ~/ecfiler && make qa-day MODE=live STAGE=56DB64etAjX \
        TARGET=https://ecf.tc1d.aztc.uscourts.gov \
        SERVER=http://100.126.58.33:8901 DEVUSER=qa-day
```

`CONFIRM` at attorney review and `YES` at the CM/ECF confirmation screen are
human by design. If the staging API is not answering (it does not survive a
VPS reboot), restart it with the command in "Hosted staging" below and
re-stage — stage codes are per-package, not permanent.

## Requesting e-filing privileges (blocking — start this first)

**The 2026-07-30 run stopped here (ledger L20).** The QA account can read the
Az Test District Court but not file in it: CM/ECF served Query, Reports,
Utilities, Help, Log Out and no Civil or Criminal menu. A PACER account
grants access to *read* dockets. Filing is a separate privilege that each
court grants and must approve, and the QA site says so in its own words:
after registering for a PACER account you "apply for attorney admissions or
electronic filing registration available for the selected court"
(`qa-pacer.uscourts.gov/register-account/attorney-filers-cmecf`).

Court approval takes days, not minutes. Nothing else on this page can happen
until it clears. Steps 2–5 are a web form and are Jackson's alone:

```
[MAC] open https://qa-pacer.psc.uscourts.gov/pscof/manage/maint.jsf
```

1. That is the QA realm's Manage My Account → **Maintenance** tab. It
   redirects to `qa-login.uscourts.gov` first (302 when checked from both
   machines, 2026-07-30). Log in with the QA credential — the same one in
   `ecfiler.keychain-db`. Do not paste it anywhere else.
2. Choose **Attorney Admissions / E-File Registration** (NextGen wording; on
   some builds it reads "E-File Registration").
3. Court type **District Court**, court **Az Test District Court** — the
   roster code is AZTTDC and its CM/ECF is
   `https://ecf.tc1d.aztc.uscourts.gov`. If the court does not appear in the
   dropdown, it does not accept registrations through this route: use
   **Contact Us** on `qa-pacer.uscourts.gov` and ask the PACER Service Center
   for filer credentials in the Az Test District Court training database,
   naming the QA username.
4. Complete the filer sections and submit. Expect an acknowledgement, then a
   wait for the court.
5. Note the date submitted in `HUMAN-QUEUE.md` so the wait is visible.

Then check for approval without attempting a filing — this logs in, reads
the CM/ECF menu bar, and answers in one line:

```
[MAC] ~/ecfiler/scripts/mac/ecfiler-mac session filing-access --qa --court azttdc
```

`✗ Read-only at azttdc` means the court has not approved yet. `✓ This
account may file in azttdc` means the re-run below can proceed.

Two things stay true even after approval. The filing path beyond the case
lookup has never run against a real court — the mock is the only thing that
has exercised it (L09) — and the route from the Civil menu to an event list
is not built (R-014), because it cannot be written against a screen no
account here can reach. Expect the first approved run to find more.

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

- **Stage with `court_id=azttdc`.** The QA court is a first-class registry
  entry (`ecfiler/courts/data/qa_courts.json`) loaded only when
  `ECFILER_PACER_QA=1`. Both the staging API and the CLI must run with that
  variable set, or staging answers 422 and the CLI cannot resolve the court.

  This replaces the previous instruction to "stage with `court_id=azd` and
  override the URL at submit time." That is how session 6's run produced a
  draft naming the real District of Arizona (ledger L16/L17). `ECFILER_ECF_URL`
  is now a confirmation of the target, not a retargeting mechanism: if it
  disagrees with the resolved court's own URL, the run aborts before the
  browser opens (`ecfiler/filing/invariants.py`). A staged package carries
  the court it was staged for, and nothing downstream may change it.

- The filing case number must exist in that court. Find one without leaving
  the terminal:

  ```
  [MAC] ~/ecfiler/scripts/mac/ecfiler-mac session find-cases --qa --court azttdc --party <name>
  ```

## QA day — one command

Prerequisite: HUMAN-QUEUE's QA-account row (register, activates overnight)
and the allow-rules paste above.

```
# One-time, after the QA account activates:
[MAC] printf '%s' 'QA-PASSWORD' | bash ~/ecfiler/scripts/mac/keychain-setup.sh 'QA-USERNAME'
[MAC] ~/ecfiler/scripts/mac/ecfiler-mac session login --qa
[MAC] cd ~/ecfiler && make qa-day MODE=live

# Stage a filing for court_id=azttdc (see below), then:
[MAC] cd ~/ecfiler && make qa-day MODE=live STAGE=<code> \
        TARGET=https://ecf.tc1d.aztc.uscourts.gov \
        SERVER=http://100.126.58.33:8901 DEVUSER=qa-day
```

At the workflow's menu choose **[2] Resume Draft** — the staged package is
the draft. `[1] New Filing` builds a fresh filing from scratch and discards
the attested package. In QA mode the court list holds the QA courts only;
production courts are not merely hidden, they are absent from the registry.

Hosted staging needs the api.ecfiler.com DNS row (HUMAN-QUEUE #1). Until it
runs, stage against a QA-mode API instead. `ECFILER_PACER_QA=1` is what puts
the QA court in the registry — without it the stage call answers 422:

```
[VPS] cd ~/ecfiler && ECFILER_DEV_AUTH=1 ECFILER_PACER_QA=1 \
        ECFILER_DATA_DIR=/root/.ecfiler-qa-staging \
        .venv/bin/python -m uvicorn ecfiler.api.app:app --host 100.126.58.33 --port 8901 &
[VPS] # POST /api/filing/stage with court_id=azttdc and the attestation;
[VPS] # note the stage_code it returns
[MAC] ~/ecfiler/scripts/mac/ecfiler-mac stage-pull <code> \
        --server http://100.126.58.33:8901 --dev-user qa-day
```

The Tailscale address is the VPS (`100.126.58.33`), reachable from the Mac —
`CLAUDE.md`'s `100.101.181.105` is stale.

`make qa-day MODE=live` (scripts/mac/qa-day.sh) gates on twelve
preconditions — macOS, repo venv, `ecfiler.keychain-db` exists / its
password file exists / it unlocks, the QA credential is stored, the QA
credential authenticates against cso-auth, the Chromium profile exists, the
persisted `--qa` session is live, the sandbox allow-rules are present, the
receipts dir is writable, and the attestation chain verifies — and refuses
to start if any is red. With a `STAGE` code it pulls the package, checks the
pulled draft names the target court (below), hands off to the attended
workflow (the CONFIRM and YES gates stay human), then prints `audit verify`
plus the receipt and trace listings.

After the pull, the script re-reads the draft and refuses to continue unless
its staged provenance names the same court and the same ECF URL as `TARGET`,
in the QA environment. That gate exists because session 6's run pulled a
draft naming `azd` and nothing noticed (L16).

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
