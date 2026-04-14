# PACER / AO Engagement + Full Federal Court Knowledge

## Goal

Secure legitimacy, technical access, and comprehensive data for ecfiler:
1. **Legal/PR cover** — AO acknowledgment, or at minimum non-objection on record
2. **Technical access** — PACER Case Locator (PCL) API, per-court RSS, possibly vendor-list inclusion
3. **Ethics opinion** — at least one state bar blessing on attorney-supervised automation
4. **Compliance memo** — outside counsel review of TOS, UPL, Rule 5.3, data handling
5. **Full court corpus** — event codes, form layouts, selectors, fee rules for all **94 district + 13 appellate + 91 bankruptcy = 198 federal courts**

Pre-launch. Solo-attorney audience. We have time and no customers yet — spend it on defensive assets.

---

## The landscape

- **AO (Administrative Office of U.S. Courts)** runs PACER + CM/ECF at the policy level. Contact: `pacer@psc.uscourts.gov` and `cmecf_support@ao.uscourts.gov`. PACER Service Center (PSC) in San Antonio handles day-to-day.
- **Per-court clerks** own the local CM/ECF install. Local rules + event codes vary. Each has a **training database** accessible to any PACER account holder — this is explicitly designed for practice filings and is the legitimate source for event codes and layouts.
- **Free Law Project / CourtListener / RECAP** is the unofficial data commons. They already have partial event-code coverage and friendly AO relations. Partnership > competition.
- **State bars** issue ethics opinions. ABA Model Rule 1.1 cmt 8 (tech competence), 5.3 (supervision of nonlawyer assistants), 5.5 (UPL). California, NY, Florida, Texas, DC are the opinion-bellwethers.

---

## Track A — AO / PACER (weeks 1–12)

### A.1 PCL API access (easy, do first)
- Already available to any PACER account holder for a modest per-search fee.
- Register account → request PCL API credentials via PSC.
- Use for: live case validation, docket number normalization, court-of-origin detection.
- **Deliverable**: working PCL integration in `ecfiler/` with rate limiting + caching. Target ~1 week of engineering.

### A.2 AO vendor awareness letter
- Write a short letter introducing ecfiler: what it does, attorney-in-the-loop safety model (your 7-gate system, encryption, attestation), who you are.
- **Ask**: confirmation that PACER account usage and CM/ECF filing-via-browser-automation-with-attorney-attestation is consistent with AO terms, OR guidance on what adjustments would make it so.
- **Expected response**: AO will not endorse but will usually not object either. A non-objection email is a valuable asset.
- Route: PSC first, then CM/ECF Working Group if they redirect.
- **Deliverable**: paper trail regardless of response.

### A.3 CM/ECF vendor listing
- AO maintains a list of third-party CM/ECF-integrated tools for the **court-side** (Tyler, etc.). There's no official "filer-side" vendor list today.
- Long shot, but worth asking in A.2 whether any listing process exists for filer-side tools — if yes, apply; if no, you've established the precedent question on record.

### A.4 Training-database access confirmation
- Before the systematic scrape in Track E, confirm in the A.2 letter that using per-court training DBs to extract event-code catalogs for a compliance-assistance tool is acceptable. This is the lowest-risk variant of "we're scraping federal courts" that we can pitch.

---

## Track B — Free Law Project / CourtListener (weeks 2–6)

Highest leverage per hour. FLP is mission-aligned, has AO relationships, and publishes relevant data.

- **B.1** — Email Mike Lissner (ED, Free Law Project). Introduce ecfiler, emphasize solo-attorney access-to-justice angle. Ask about:
  - CourtListener API for docket/case data (already public, confirm commercial-use posture)
  - Whether RECAP event-code data is shareable or co-developable
  - Whether FLP would co-sign or reference ecfiler in any future comm to AO
- **B.2** — Join the `#courtlistener` community; file issues / PRs if we find event-code gaps in their data; establish a reciprocal relationship.
- **Deliverable**: one of (a) FLP API key + data feed, (b) a reference letter / quote we can use in AO outreach, (c) a "no thanks" that we move past.

---

## Track C — State bar ethics opinion (weeks 4–16)

The strongest defensive asset we can get. A formal opinion from any major state bar saying "attorney use of automated filing tools is OK when [conditions]" becomes a shield nationally.

- **C.1** — Draft the opinion request. Frame as: "May an attorney use a software tool that (i) accepts the attorney's PACER credentials, (ii) performs CM/ECF filing steps under attorney supervision, (iii) requires explicit attorney attestation before final submit?" Describe the 7-gate safety system, the attestation flow, credential encryption.
- **C.2** — Submit to California State Bar Standing Committee on Professional Responsibility (COPRAC), DC Bar Legal Ethics Committee, and NY State Bar Committee on Professional Ethics — parallel tracks, pick best responder.
- **C.3** — If formal opinion is slow (12+ months typical), ask for informal staff guidance in writing. Still valuable.
- **Budget**: $0 to file but ~40 hours of your + counsel's drafting time.
- **Deliverable**: at least one written opinion or informal letter.

---

## Track D — Outside counsel compliance memo (weeks 1–4)

Fastest, most private, most actionable. Don't skip this to save money — it informs every other track.

- **D.1** — Retain a lawyer with federal court procedure + tech/software experience. Candidates: Ropes & Gray, Fenwick, Cooley (expensive); or a specialist solo like Carolyn Elefant (MyShingle), or a legaltech-focused firm.
- **D.2** — Scope: PACER TOS review, CM/ECF local-rule sampling (top 10 courts), UPL analysis across 3–5 target states, data-handling review (encryption, credential storage, audit logs), Rule 5.3 supervision framework.
- **D.3** — Output: a memo + a specific list of product changes required for legal defensibility. Apply changes before public launch.
- **Budget**: $15–40k typical for this scope.
- **Deliverable**: written memo, product-change punch list.

---

## Track E — Full federal court corpus (weeks 2–20, parallel)

Your specific capability ask. This is the data engineering project.

### E.1 Inventory & sources
- **94 District Courts** — each has CM/ECF + training DB + local rules PDF + event-code report
- **13 Circuit Courts of Appeals** — NextGen CM/ECF-appellate; different schema
- **91 Bankruptcy Courts** — separate CM/ECF install per court, different event taxonomy
- **Sources per court**:
  - `https://ecf.<court>.uscourts.gov/cgi-bin/login.pl` — real CM/ECF
  - Training DB URL (pattern varies; often `ecf-train.<court>...` or a link from court's website)
  - Local rules PDF (court website, public)
  - Clerk's filing manual (often public PDF)
  - Existing `ecfiler/courts/data/*.json` profiles (start here, extend)

### E.2 Event code extraction
- For each court, log into training DB with a PACER account.
- Walk each filing category (civil, criminal, MDL, misc; bankruptcy chapters; appellate motions/briefs/petitions).
- Extract: event code, display name, required attachments, fee, sealing policy, party-role prompts.
- Persist to `ecfiler/courts/data/<court_id>/events.json`.
- **Automation**: reuse your existing Playwright infrastructure; add an "event-catalog crawler" mode that enumerates events rather than files them.
- **Ethics**: training DBs are explicitly meant for practice — scraping them for a compliance tool is defensible. Do A.4 first for belt-and-suspenders.

### E.3 Layout / selector extraction
- Capture DOM selectors per-court per-step. Detect NextGen vs legacy.
- Output: per-court `selectors.json` that plugs into existing `CourtSelectors` structure.
- Handle the long tail: some courts heavily customize (E.D. Va., N.D. Cal.); others are vanilla.

### E.4 Fee rules
- Already have top-level fee schedule (`ecfiler/filing/fees.py`) per court-type. Extend to per-court overrides where local surcharges or waiver policies differ. Clerk's office fee schedule is public per court.

### E.5 Local rules ingestion
- Don't parse full local rules (too variable). Do extract specific items: page limits, font requirements, redaction rules, certificate-of-service templates, filing deadlines, judge-specific standing orders where published.
- Store as structured annotations the AI can use during the redaction/compliance passes.

### E.6 Maintenance
- Courts update event codes quarterly-ish. Build a diffing crawler that re-scrapes and flags changes. Subscribe to PACER announcements and individual clerk listservs where available.

### E.7 Rollout phases
- **Phase 1 (weeks 2–4)**: Top 15 courts by filing volume (S.D.N.Y., C.D. Cal., N.D. Ill., D.D.C., E.D. Va., N.D. Cal., S.D. Fla., E.D. Tex., D. Del., D.N.J., M.D. Fla., E.D.N.Y., N.D. Ga., N.D. Tex., W.D. Wash.) — covers ~60% of federal filings.
- **Phase 2 (weeks 4–10)**: remaining districts + all circuits.
- **Phase 3 (weeks 10–20)**: bankruptcy courts (last because bankruptcy has its own workflow complexity).

---

## Timeline summary

| Week | Milestone |
|------|-----------|
| 1–2  | Outside counsel retained (D), PCL account request (A.1) |
| 2–4  | FLP/CourtListener outreach (B), top-15 court scrape begins (E.1–E.2) |
| 4–6  | AO letter drafted + sent (A.2), compliance memo received (D.3) |
| 6–10 | Ethics opinion drafted + submitted (C), all districts scraped (E.2) |
| 10–16 | Appellate + bankruptcy scrape (E), AO response handled |
| 16+  | Ethics opinion tracking, ongoing maintenance (E.6), launch |

## Budget estimate

| Item | Low | High |
|------|-----|------|
| Outside counsel memo | $15k | $40k |
| PCL API usage (first year) | $1k | $5k |
| PACER account fees (scraping) | $500 | $2k |
| Ethics opinion filing | $0 | $0 |
| Engineering time (your own) | — | ~300 hrs |
| **Total cash** | **~$16.5k** | **~$47k** |

## Risks to manage

- **AO tells us to stop**: Unlikely but possible. A non-objection letter in Track A is specifically to short-circuit this. If it happens, pivot to "attorney prep tool" that hands off to human-driven filing.
- **Bar opinion goes against us**: Possible. Frame the request carefully (emphasize attorney supervision, not autonomy). If one bar says no, adjust product + re-ask another.
- **Scraping detection**: Training DBs are intended for practice, but high-volume crawling could trip rate limits. Throttle conservatively (≤1 req/sec per court), use dedicated PACER accounts, rotate.
- **Event-code drift**: Courts change codes without warning. E.6 maintenance crawler is mandatory, not optional.
- **UPL surface**: The AI suggesting event codes is the highest UPL risk. Mitigations: always present multiple options, require attorney selection, never autopick without confirmation, include "this is software, not legal advice" disclosures.

---

## Immediate next actions (this week)

1. Shortlist 3 outside-counsel candidates, email them for proposals. *(Track D)*
2. Register a dedicated PACER account for API + scraping; request PCL credentials. *(Track A.1)*
3. Draft 2-paragraph intro email to Mike Lissner at Free Law Project. *(Track B)*
4. Build the event-catalog crawler mode in the Playwright harness — reuse existing court profiles; target S.D.N.Y. training DB first as proof of concept. *(Track E.2, engineering)*

I can start #4 now if you want; #1–#3 need your voice and decisions.
