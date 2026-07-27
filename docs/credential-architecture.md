# ECFiler Credential Architecture

*Status: adopted 2026-07-27. This document is the authoritative statement of how
ECFiler handles attorney CM/ECF and PACER credentials, why, and what was changed to get
here. It is written to be readable by a clerk's office, an ethics committee, or
opposing counsel.*

---

## 1. The rule this architecture is built around

The filing login is not an ordinary password. Under the local rules of essentially
every federal district, use of an attorney's CM/ECF credentials **constitutes that
attorney's signature** for Rule 11 purposes. And on July 10, 2023, the Administrative
Office of the U.S. Courts warned filers against sharing CM/ECF or PACER credentials
with third-party service providers or designating providers as secondary NEF/NDA
recipients, because doing so can expose sealed and restricted material in violation of
court orders. Dozens of courts republished that warning, naming specific vendors by
example (see, e.g., D.P.R. Notice from the Clerk 23-06,
<https://www.prd.uscourts.gov/news/notice-clerk-23-06-warning-regarding-sharing-cmecf-o-pacer-credentials-third-party-service>;
D.C. Cir. notice,
<https://www.cadc.uscourts.gov/news/cmecf-access-case-information-and-documents-third-party-services>).
The industry response was uniform: serious vendors stopped storing ECF credentials
(see PacerPro's public policy,
<https://www.pacerpro.com/news/pacerpro-policy-regarding-federal-ecf-credentials-and-sealed-documents/>).

Two consequences drive everything below:

1. **Custody:** ECFiler must never hold an attorney's filing credentials on
   infrastructure the attorney does not control.
2. **Access scope:** custody is not the whole problem. The courts' 2023 notices name
   RECAP — a tool that never stores credentials — because the underlying concern is
   *access to restricted material*, not storage mechanics. So the architecture must
   also constrain what documents the software can see (see the companion
   [sealed-document policy](sealed-document-policy.md)).

## 2. The custody model

### 2.1 Primary: local execution

All software that authenticates to PACER or CM/ECF runs **on the attorney's own
machine** (the ECFiler CLI). Credentials live in the operating system keyring
(`keyring` library, service `ecfiler-pacer`), which is the OS-level encrypted secret
store unlockable only by the logged-in user. The Playwright browser session that
performs filing steps runs locally, under the attorney's account, on the attorney's
network. ECFiler's servers are never in the credential path — they cannot leak, log,
or misuse what they never receive.

This is functionally the posture the industry converged on after the 2023 memorandum:
the automation is an instrument operated by the attorney on the attorney's own
authenticated session, like a browser extension — not an agent holding the attorney's
identity on remote infrastructure.

### 2.2 Fallback: hosted "prepare, validate, stage — don't submit"

The hosted web application (ecfiler.com) performs document analysis, validation,
redaction scanning, event-code lookup, fee lookup, checklist generation, and staging.
Its output is a **validated filing package** — the PDF(s), canonical filing metadata,
a checklist, and a certificate of service — plus a link to the correct court's CM/ECF
and step-by-step handoff instructions. **The human files.** The hosted product needs no
filing credentials, asks for none, and stores none.

### 2.3 Models evaluated and rejected

| Model | Verdict | Why |
|---|---|---|
| Server-side encrypted credential store (AES-256 at rest, decrypt at filing time) | **Removed** (see §4) | Exactly the pattern the July 2023 AO memorandum targets, regardless of encryption quality. Fails a clerk's-office review on its face. |
| Hosted ephemeral session (attorney authenticates interactively per filing; nothing persisted) | Rejected | Credentials still transit and exist in memory on ECFiler infrastructure mid-session. Better than storage, but still credential custody during the window that matters. |
| Browser extension driving the attorney's own CM/ECF session | Viable future option | Zero custody, same trust posture as RECAP/PacerPro. A distinct build; not pursued now. Noted for the modernization era. |
| Local execution (CLI) + hosted prepare-only | **Adopted** | Zero server custody; the only actor who ever authenticates is the attorney, from their own machine. |

## 3. Data flow, as shipped

```
┌────────────────────────── Attorney's machine ──────────────────────────┐
│  OS keyring ──► ecfiler CLI ──► PACER CSO (token) ──► court CM/ECF     │
│                     │                                    │             │
│                     │◄── staged filing package ──┐       ▼             │
│                     ▼                            │   NEF / receipt     │
│  local audit trail (screenshots, receipt,        │   (captured locally)│
│  hash-chained attestation record)                │                     │
└──────────────────────────────────────────────────┼─────────────────────┘
                                                   │
┌────────────────────────── ECFiler servers ───────┼─────────────────────┐
│  PDF analysis · validation · redaction scan ·    │                     │
│  event/fee lookup · checklist · staging ─────────┘                     │
│                                                                        │
│  NEVER present: CM/ECF or PACER passwords, CSO tokens, sealed          │
│  documents, NEF secondary-recipient designations                       │
└────────────────────────────────────────────────────────────────────────┘
```

What each side can see:

- **Server can see:** uploaded public filing documents (retained per the published
  retention policy), filing metadata, the attorney's ECFiler account (Clerk-managed
  auth).
- **Server can never see:** PACER/CM-ECF passwords, CSO tokens, sealed or restricted
  documents (refused at upload — see sealed policy), NEF feeds.
- **Local machine keeps:** keyring-held password, per-filing screenshots, submission
  receipt/NEF, the attestation record.

## 4. What was removed, and the purge record

Before 2026-07-27 the web application offered optional server-side credential storage:
`POST /api/pacer/credentials` encrypted the password with AES-256-GCM
(PBKDF2-SHA256-derived key from an environment variable) into a server SQLite table.
Audit established that **no filing path ever consumed those credentials** — the only
decryption site was a key-health check. The store was vestigial, and it was the single
largest gap between ECFiler's architecture and the post-2023 industry standard.

Remediation (tracked in the repository history):

- Endpoints removed; `/api/pacer/credentials` returns `410 Gone` for one release with
  a pointer to the keyring documentation.
- Startup migration drops the credential table and runs `VACUUM` so ciphertext does not
  survive in SQLite free pages; the purge logs a tombstone with the row count.
- `ECFILER_ENCRYPTION_KEY` removed from all deployment environments after the purge
  deploy is verified; hosting-volume snapshots that predate the purge are deleted.
- **Purge record:** _to be completed at deploy time — date, row count, snapshot
  disposition, operator._

## 5. Threat model (summary)

| Threat | Mitigation |
|---|---|
| ECFiler server compromise | No credentials or sealed material present to steal; blast radius is public filing documents and metadata under the retention policy. |
| Attorney workstation compromise | Same exposure as any workstation used for CM/ECF; keyring is OS-protected; ECFiler adds no remote copy to steal. |
| Credential interception in transit | Passwords never transit ECFiler infrastructure; CSO authentication is attorney-machine → PACER over TLS. Tokens are never placed in URLs and are redacted from logs. |
| Sealed material exposure via tooling | Hosted product refuses sealed documents outright; local pipeline hard-fails when sealing intent is detected but cannot be verifiably honored (see sealed policy). |
| Unattributable filings ("who signed this?") | Hash-chained, append-only attestation record per filing: attestor identity, the exact summary shown at attestation, the exact payload submitted, and the returned NEF; chain head printed on each receipt so the record is anchored outside any single machine. |
| Automation misbehavior toward the courts | Honest identifying User-Agent, per-court concurrency of 1, backoff, and bulk operations gated to the AO's requested 6 p.m.–6 a.m. CT window. |

## 6. Unauthorized-practice-of-law surface and human checkpoints

Every feature whose output could be characterized as legal judgment carries a
mandatory human checkpoint that keeps ECFiler's role clerical. This table is the
product's UPL control inventory:

| Feature | Judgment risk | Human checkpoint |
|---|---|---|
| AI event-code suggestion | Selecting the docketing event can determine deadlines and fees — the highest-risk surface | Software always presents **multiple candidate events**; the attorney selects; no auto-pick, ever |
| AI docket-text generation | Docket text characterizes the filing | Text is editable and shown verbatim at the attestation gate; attorney approves the exact string |
| Fee-status election (paid / IFP / waived) | An IFP election is a legal position | Never inferred; explicit attorney selection required, surfaced at review |
| Certificate of service generation | States a legal fact about service | Generated as a draft; recipients and methods confirmed by the attorney before inclusion |
| Deficiency/completeness scoring | "Ready to file" resembles advice | Framed as mechanical checklist results with rule citations; filing proceeds only on attorney attestation |
| Redaction (Rule 5.2) scanning | Deciding what must be redacted is judgment | Scanner flags candidates; it never modifies the document; attorney resolves each flag |
| Final submission | The Rule 11 act itself | Two explicit gates: typed confirmation at review, and typed `YES` after the court's own confirmation screen is displayed; both recorded in the attestation chain |

## 7. What this architecture does *not* claim

- It does not make automated filing "approved." No federal court has blessed
  agent-assisted filing generally; whether a supervised software tool falls within a
  district's "authorized agent" local-rule provision is a question for each clerk's
  office, and ECFiler's position is that the attorney operates the tool, on their own
  machine, under Rule 5.3-style supervision.
- It does not provide, and cannot provide, a sanctioned server-side filing channel for
  federal district courts. None exists for anyone. The sanctioned programmatic
  channels published by the AO are read-side (PACER auth API, Case Locator API) and
  bankruptcy/appellate-specific write formats. ECFiler's hosted product is therefore
  prepare-only by design, not by temporary limitation.
