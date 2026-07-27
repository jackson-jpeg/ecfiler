# ECFiler Sealed and Restricted Document Policy

*Status: adopted 2026-07-27. Published policy — written to be read by courts,
clients, and counsel. Companion to [credential-architecture.md](credential-architecture.md).*

## The policy in one paragraph

**ECFiler's hosted service never accepts sealed or restricted documents, and
ECFiler software never lets a sealed document become a public filing.** A hosted
server is the wrong place for material a court has ordered protected, so we do not
put it there — not encrypted, not in memory, not briefly. Sealed filings belong on
the attorney's own machine (the ECFiler CLI) or in the court's conventional
under-seal procedure. Where sealing is requested and the software cannot verify the
court's electronic sealing controls, it stops. It never guesses.

## Why the courts' concern is our design constraint

The Administrative Office's July 10, 2023 memorandum, republished by courts
nationwide, warned filers that sharing credentials with — or forwarding NEFs to —
third-party services can expose sealed and restricted case material in violation of
court orders. Notably, the courts' notices name tools that never store credentials
at all: the concern is *access to protected material*, however it happens. ECFiler's
answer is structural, not procedural — the hosted service is built so that sealed
material cannot be present on it.

## The four enforcement layers

1. **Preflight (local pipeline).** A filing marked sealed without a stated sealing
   basis is an error, not a warning. Separately, a keyword gate scans event
   descriptions and docket text for sealing-related language (`seal`, `restricted`,
   `redacted`, `ex parte`, `in camera`); a hit on a filing *not* marked sealed
   requires the attorney's explicit confirmation that public filing is intended.
   ("Motion to Unseal"-style false positives are exactly why this is a confirmable
   gate rather than a hard block.)

2. **Browser layer (local CLI filing).** When sealing is requested, the software
   must find and set the court's ECF sealing control. If it cannot, the filing
   **aborts** with `SealingUnavailableError` — the legacy behavior of warning and
   continuing (which would have filed a sealed document publicly) has been removed.
   The live event page is re-scanned for sealing language before submission.

3. **Per-exhibit.** Sealed flags on individual exhibits propagate to the browser
   layer; a sealed exhibit that cannot be individually protected aborts the filing.

4. **Hosted service refusal.** The web application and API refuse sealed content
   outright (HTTP 403), display a hard-stop screen routing the filer to the CLI or
   conventional filing, and never persist sealed filing state — not even to the
   browser's session storage. This is consistent with the storage layer, which has
   never archived sealed PDFs and returns `410 Gone` for any sealed download.

## What happens when a court has no electronic sealing path

Some courts require sealed documents to be filed conventionally (on paper, under
seal, per local rule) rather than through ECF. When ECFiler aborts because sealing
controls are absent, the error says exactly that: *file conventionally under seal
per the court's local rule and sealing procedure.* The software does not attempt to
approximate sealing with docket-text notes or restricted-event guesses.

## Records

Filing history records that a sealed filing occurred (court, case, timestamp,
sealed flag) — never the document or its contents. The attestation log records the
attorney's confirmation and payload hashes, not document bodies.

## Reporting

If you believe ECFiler software has mishandled sealed or restricted material in any
way, contact [support contact] immediately; we treat any such report as a
highest-severity incident.
