# The attended NEF run: one sitting, under 15 minutes

*Written 2026-11-13 (session 7). Run it only after the approval check below
answers "may file". Everything before the browser is checked by the operator
from the VPS first; Jackson's part starts at step 3.*

## Why the gates stay at the keyboard

The workflow asks over a dozen interactive questions (menu, court, case,
attachments, a "continue anyway?" gate), and two of them are the safety gates:
**CONFIRM** at the review screen and **YES** at CM/ECF's own confirmation
screen. YES is the account holder submitting a document to a court system
under his PACER account. The person typing it has to be the person looking at
the headed browser on the Mac. A YES relayed through chat would be an
attestation about a screen the confirmer never saw. So both gates stay where
they are, and the sitting is cut down to the minutes that need Jackson.

## Operator prep (VPS, before Jackson sits down; no Jackson time)

```
[MAC] cd ~/ecfiler && .venv/bin/python -m playwright install chromium   # ~540 MB; removed 2026-11-13 when the Mac disk filled, so reinstall first (check free space)
[MAC] ~/ecfiler/scripts/mac/ecfiler-mac session filing-access --qa --username ecfilercom --court azttdc
[MAC] cd ~/ecfiler && make qa-day MODE=live            # preflight only, must be 12/12 green
```

If approval came for a court other than AZTTDC, the operator first adds it to
`ecfiler/courts/data/qa_courts.json` and re-stages the sample motion for it on
the Mac (a QA-mode API on the Mac's loopback, `stage-pull --server
http://127.0.0.1:8901`), so step 3 below is unchanged.

## Jackson (Mac terminal, about 10 minutes)

1. Sit at the Mac, plugged in, Terminal open. (1 min)
2. Paste: (30 s)

   ```
   [MAC] cd ~/ecfiler && make qa-day MODE=live STAGE=resume TARGET=https://ecf.tc1d.aztc.uscourts.gov
   ```

3. It prints the 12 preflight PASS lines and `PASS draft staged_0_07-cv-00170.json
   → azttdc @ https://ecf.tc1d.aztc.uscourts.gov (qa)`, then opens a Chromium
   window. At the menu type **2** (Resume Draft), then pick the
   `staged_0_07-cv-00170` draft. (1 min)
4. Answer the prompts with their defaults (Enter) unless something looks
   wrong. The document is `~/ecfiler/docs/qa-roundtrip/sample-motion.pdf`.
   (3 min)
5. **CONFIRM**: read the review table (court Az Test District Court, case
   0:07-cv-00170, the sample motion, docket text) and type `CONFIRM`. (1 min)
6. Watch the browser walk CM/ECF. At CM/ECF's final confirmation screen, read
   it and type **`YES`** in the terminal. (3 min)
7. Leave the terminal open until it prints `== Proof ==` and the `audit
   verify` result. Tell the operator "done". (1 min)

If anything stops the run, do not retry: CM/ECF has no idempotency key, so a
blind retry is a second docket entry. Tell the operator what it printed.

## Operator wrap-up (no Jackson time)

Collect `~/.ecfiler/receipts/` (NEF text + docket number), the
`kind="submitted"` attestation and the trace zip into `docs/qa-roundtrip/`;
run `ecfiler-mac audit verify` and the server-side chain check; add the
ledger row; update `docs/filing-topology.md` §4; then take the four scoped
`Bash(ssh macbook…)` allow-rules out of the repo's `.claude/settings.json`
and `/root/.claude/settings.json`, as asked in July.
