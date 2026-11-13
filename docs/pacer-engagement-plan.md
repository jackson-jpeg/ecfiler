# PACER / AO Engagement + Full Federal Court Knowledge

> **SUPERSESSION NOTICE (2026-07-27).** Sections A.2–A.4 of this document are
> superseded by the federal engagement strategy in `docs/outreach/` (C1–C6) and
> `docs/credential-architecture.md`. The A.2 "ask for confirmation" letter is the
> exact move the new strategy forbids: it petitions the AO for a blessing it cannot
> give, invites documented objection, and was premised on a credential-custody
> architecture that has since been removed. Post-2025-breach, during an active
> CM/ECF replacement program, the viable posture is contributing requirements as a
> practitioner (see `docs/outreach/c4-white-paper.md`), not seeking permission for
> browser automation. Track A.1 (PCL API), Track B (Free Law Project), Track C
> (bar ethics opinion), Track D (compliance memo), Track E (court corpus), the
> budget, and the risk register remain valid and are referenced by the new plan.
>
> **Checked 2026-11-13:** see "Changes since July" near the end. In short: the EPA
> user-group window did **not** open in Aug 2026, CM/ECF replacement has dates, PACER
> fees rise on 2027-01-01, and Rule 5.2 redaction amendments are out for comment.

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
- Already available to any PACER account holder for a modest per-search fee. *(Fee rises
  from $0.10 to $0.12 per page on 2027-01-01 — see "Changes since July", §3.)*
- ~~Register account → request PCL API credentials via PSC.~~ **Corrected 2026-11-13:**
  there are no separate PCL API credentials to request. The Oct 2026 PCL API guide: "A
  valid PACER account is required to use the PCL API." Authenticate with the PACER
  Authentication API, then send the token as `X-NEXT-GEN-CSO`. Use a **PACER-only
  (search) account** for this, because a CM/ECF-level account must enroll in MFA and
  would then need an `otpCode` on every unattended login (§3 below).
- Use for: live case validation, docket number normalization, court-of-origin detection.
- **Deliverable**: working PCL integration in `ecfiler/` with rate limiting + caching. Target ~1 week of engineering.

### A.2 AO vendor awareness letter — **SUPERSEDED, do not send** (see notice at top)
- Write a short letter introducing ecfiler: what it does, attorney-in-the-loop safety model (your 7-gate system, encryption, attestation), who you are.
- **Ask**: confirmation that PACER account usage and CM/ECF filing-via-browser-automation-with-attorney-attestation is consistent with AO terms, OR guidance on what adjustments would make it so.
- **Expected response**: AO will not endorse but will usually not object either. A non-objection email is a valuable asset.
- Route: PSC first, then CM/ECF Working Group if they redirect.
- **Deliverable**: paper trail regardless of response.

### A.3 CM/ECF vendor listing — **SUPERSEDED** (folded into C2's narrow questions)
- AO maintains a list of third-party CM/ECF-integrated tools for the **court-side** (Tyler, etc.). There's no official "filer-side" vendor list today.
- Long shot, but worth asking in A.2 whether any listing process exists for filer-side tools — if yes, apply; if no, you've established the precedent question on record.

### A.4 Training-database access confirmation — **SUPERSEDED as an A.2 rider; ask PSC directly if/when Track E scales beyond spot crawls**
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
- **94 District Courts** — each has CM/ECF + training DB + local rules PDF + event-code report.
  *(Shelf life, added 2026-11-13: the Judiciary says it will "move all new district court
  cases into CMM" by year-end 2027. District CM/ECF selector and event-code work (E.2/E.3)
  therefore has about a one-year life for new cases. See "Changes since July", §1.)*
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
| 1–2  | Outside counsel retained (D), ~~PCL account request~~ PACER-only search account for PCL (A.1; corrected 2026-11-13) |
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
| *(2027+: both PACER rows +20%, since per-page fees go from $0.10 to $0.12 on 2027-01-01, and the free tier rises from $30 to $40 per quarter)* | | |
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

## Changes since July (checked 2026-11-13)

Window: 2026-07-30 → 2026-11-13. Only primary sources are cited for facts, and
quotes are verbatim. Items found but dated before the window are marked *(pre-window
baseline)*. Nothing was submitted, subscribed to, logged into or sent.

### 1. CM/ECF replacement ("Case Management Modernization", CMM)

- **Dates set, and accelerated.** Judicial Conference update, **2026-09-17**
  (<https://www.uscourts.gov/data-news/judiciary-news/2026/09/17/judiciary-cites-progress-case-management-property-authority-and-ai>):
  "the first component is on track to be released before the end of 2026." /
  "By year end 2027, we will move all new district court cases into CMM." / "The
  appellate and bankruptcy courts will follow." (No date is given for appellate or
  bankruptcy, and no vendor is named.) The same release calls CM/ECF "outdated and
  vulnerable to security breaches."
- **Funding.** Executive Committee action, **2026-06-26** *(pre-window, but it takes
  effect inside our horizon)*
  (<https://www.uscourts.gov/data-news/judiciary-news/2026/06/26/judiciary-approves-funding-case-management-and-public-access-modernization>):
  "Cybersecurity concerns prompted the Judiciary to accelerate the timeline for
  completion." The new system will hold "management systems for all civil and criminal
  cases in a secure cloud environment" by end-2027. Fee details are in §3.
- **Congress.** No CMM-specific hearing or testimony was found in the window. FY2027
  runs on a CR (P.L. 119-103, signed 2026-09-02, through **2026-12-11**; CRS R49353,
  2026-09-17, <https://www.congress.gov/crs-product/R49353>, paraphrased and not
  fetched). The House FSGG bill (H.R. 8495) and the Judiciary's FY2027 JITF request,
  which includes a "$10.0 million" CMM line
  (<https://www.uscourts.gov/sites/default/files/document/section_11_-_jitf_fy2027.pdf>),
  both predate the window.
- **New cybersecurity incident, different system.** The Bankruptcy Noticing Center went
  down from about **2026-10-09**. AO notice of **2026-10-15**, updated **2026-10-27**
  (<https://www.uscourts.gov/data-news/judiciary-news/2026/10/15/update-bankruptcy-noticing-center-access-restored>):
  the contractor's "BAE Systems IT and websites supporting the Bankruptcy Noticing
  Center (BNC) have been impacted by a cybersecurity incident". On 2026-10-22 the
  Judicial Conference declared a Bankruptcy Rules emergency under FRBP 9038. Access
  was restored by 10-27. Court notices (e.g.
  <https://www.ganb.uscourts.gov/news/2026/10/15/important-information-regarding-bankruptcy-noticing-center-bnc-service-disruption>)
  say CM/ECF NEFs kept flowing. No public follow-up on the 2025 CM/ECF/PACER breach
  (investigation outcome, attribution) was found in the window.
- **No user-group or vendor announcement** about CMM filer interfaces, APIs or
  third-party access was found. The rules package in §4 is the only public channel
  open on anything adjacent.
- **What it means for ECFiler:** district CM/ECF screen work (R-014's route walk,
  E.2/E.3 selectors) is aimed at a system that stops taking **new** district cases by
  end-2027. Existing cases likely stay on CM/ECF longer, but that is an inference
  the AO has not stated. The C4 white paper's premise (requirements input to an
  active replacement program) is now *more* timely, not less.

### 2. EPA Public User Group window

- **It did not open.** The plan (via C3 and the contact tracker) expected a call
  "~Aug 2026". None has been issued as of 2026-11-13:
  - The group page (<https://www.uscourts.gov/court-records/electronic-public-access-public-user-group>,
    no published or updated date on the page) still shows "2025-2026 Membership", 11
    members, and the last meeting listed is July 15, 2025. Its main-content text
    today is **identical** to Wayback snapshots of 2026-07-28, 08-31, 10-15 and 10-28.
  - The PACER announcements index (<https://pacer.uscourts.gov/announcements>) runs to
    2026-10-15 and has no user-group item after "Applications Open for Public User
    Group" (2024-08-19).
  - The uscourts.gov news feed (<https://www.uscourts.gov/news/rss>) has nothing about
    the group from 2026-07-30 to 2026-11-02.
- **Why it is overdue, not missed.** The charter
  (<https://www.uscourts.gov/sites/default/files/epa_public_user_group_charter_final.pdf>,
  2022) says "Members will be invited to serve a two-year term." and "No member should
  serve more than two consecutive terms." The current terms run 2025-2026, so they end
  2026-12-31. The 2024 call came about 4.5 months before its terms began. Either a
  late call is still coming for 2027-2028, or the Chair is holding over or re-inviting
  members (the charter allows re-invitation "if there is an insufficient number of
  applicants"). Neither has been announced.
- **Correction to the C3/tracker baseline (those files are not edited here).** The
  2024 deadline was not Sept 2. The PACER notice
  (<https://pacer.uscourts.gov/announcements/2024/08/19/applications-open-public-user-group>,
  updated 2024-09-04) says "Deadline for applications for membership has been extended
  to Monday, Sept. 9, 2024". uscourts.gov announced it first, on 2024-08-02
  (<https://www.uscourts.gov/data-news/judiciary-news/2024/08/02/applications-open-pacer-user-group>),
  17 days before pacer.uscourts.gov did. So the 2024 window ran about 5 weeks, not
  "~2 weeks". The "window expected ~Aug 2026" lines in `c3-epa-application.md` and
  `contact-tracker.md` are now wrong.
- **The monitor is not running.** `ecfiler-epa-monitor.timer` was removed on
  **2026-09-24** in the VPS rescoping (`/root/retired/RESTORE.md`,
  `ecfiler-20260924.tar.gz`), and its last run was that day. From 2026-08-04 to
  09-24 it raised **22 "page changed" alerts (5 on the group page, 17 on the
  announcements page) and zero keyword hits** (`/var/lib/ecfiler-epa-monitor/alerts.log`).
  All 22 were noise. The group page's main content is identical in every snapshot
  above, and no announcement was posted between 07-08 and 10-15. The extractor
  diffs the whole page, chrome included.
- **Recommendation for `scripts/epa-window-monitor.sh` (script not edited):**
  1. Add `https://www.uscourts.gov/news/rss` as the primary source. Trigger: a new
     `<item>` whose title matches `/user group/i`. This is the channel that carried
     the 2024 call first.
  2. On the group page, diff only the `<main>` text. Trigger: the string
     `2025-2026 Membership` disappears, **or** "application" or "apply" appears in
     `<main>`.
  3. On `pacer.uscourts.gov/announcements`, use the keyword trigger only and drop the
     diff trigger (it produced 17 of the 22 false alerts). The existing keyword
     "accepting applications" matches the 2024 wording ("currently accepting
     applications").
  4. Deliver through `ops-page --tag ecfiler-epa` rather than the `sanger-monitor` env
     token and a bare `mac notify`. The box's standing rule says all paging goes through
     `ops-page`, and `/root/.sanger-monitor.env` belongs to a retired unit.
  5. Where it runs is Jackson's decision. ECFiler was deliberately retired from this
     VPS, and the box rule says not to reinstate retired units to make something work.
     The zero-infrastructure alternative is PACER's own "Email Updates" signup on
     pacer.uscourts.gov, which carried the 2024 notice. That signup is Jackson's to
     make; nothing was subscribed here.
  6. Stop watching when a 2027 roster is posted, or on 2027-03-31 with no call. After
     that the next cycle is unknown and the C6 fallback (informal channels) applies.

### 3. PACER authentication, MFA, passwords, API, fees

- **MFA is mandatory for every CM/ECF-level account (filers included) and optional for
  PACER-only accounts.** That is unchanged in the window. Auth API guide v.3, May 2025
  *(pre-window baseline, still the current guide)*
  (<https://pacer.uscourts.gov/sites/default/files/files/PACER%20Authentication%20API-2025_v2_0.pdf>):
  "Users with filing and all other types of CM/ECF-level access are required to enroll
  in MFA, while users with PACER-only (case search only) access have the option to
  enroll." and "This one-time passcode is required if the account is enrolled in
  multifactor authentication (MFA)." The API field is `otpCode`. TOTP apps are the only
  method: "You are not sent the one-time passcode by text or push notification."
  (Oct 2026 newsletter). No separate service-account or API-key path exists.
  ECFiler's attended login (`ecfiler/pacer_session.py`, where the human types the
  password and MFA code) already fits this.
- **New in the window: password standards are enforced.** July 2026 newsletter
  (<https://pacer.uscourts.gov/sites/default/files/files/July%202026%20Newsletter-v3_FINAL.pdf>,
  2026-07-08): "Starting August 17, 2026, PACER users who haven't updated their
  password in the past 18 months will be required to create a new one." Rules: 14-45
  characters, at least one lowercase, one uppercase and one special character, no
  name, username or email, no character three times in a row, and a change every 180
  days. The login prompt can be skipped 3 times, then the account locks. The October
  2026 newsletter (2026-10-15,
  <https://pacer.uscourts.gov/sites/default/files/files/October%202026%20v3_FINAL.pdf>)
  repeats it and adds: "If you use third-party software with PACER, check whether any
  updates are needed." Implications: any stored copy of a PACER password (R-001
  keyring, R-003 Mac keychain) now goes stale at least every 180 days. R-002's
  rotation is still owed, because enforcement only forces a change on passwords older
  than 18 months.
- **The PCL API guide was re-issued twice, with no breaking change.** "August 2026"
  (`PCL-API-08-2026-1.pdf`) and "October 2026" (`PCL-API-10-2026.pdf`, last-modified
  2026-10-27; <https://pacer.uscourts.gov/help/pacer/pacer-case-locator-pcl-api-user-guide>).
  A text diff against the Nov 2024 guide shows editorial changes, renumbering, an
  expanded nature-of-suit appendix, and one clarification: "Note that each of SSN,
  EIN, and TIN are searched using the ssn search field in the Request Body". The
  endpoints (`pcl.uscourts.gov` / `qa-pcl.uscourts.gov`), the `X-NEXT-GEN-CSO` token
  and the limits (5,400 items immediate, 108,000 batch) are unchanged. "All searches
  in the Production environment are billable."
- **Release notes for PACER-enabling applications**
  (<https://pacer.uscourts.gov/file-case/developer-resources/release-notes-pacer-enabling-applications>):
  there is no release after April 2026 (custom security questions, MFA help links), so
  there are no auth or API changes in the window.
- **Fees (decided 2026-06-26, newsletters 2026-07-08 and 2026-10-15):** "The increase
  of two cents per page, from 10 cents to 12 cents" takes effect **2027-01-01**. The
  quarterly exemption goes from $30 to $40, and the 30-page docket cap is unchanged.
  "The fee increase will remain in place for a five-year period." The budget table
  above is annotated.
- **No new developer program.** The developer resources page
  (<https://pacer.uscourts.gov/file-case/developer-resources>) still lists the same two
  APIs and the `developers@psc.uscourts.gov` mailbox, and still says "The federal
  Judiciary may suspend or reduce PACER access to any account".

### 4. Other things that affect a third-party filing-prep tool

- **Proposed Rule 5.2 redaction amendments**, published **2026-08-14**
  (<https://www.uscourts.gov/sites/default/files/document/preliminary_draft_of_proposed_amendments_-_august_2026.pdf>;
  comments to <https://www.regulations.gov/docket/USC-RULES-CV-2026-0003>). They
  would "Require complete redaction of social security numbers (SSNs), individual
  taxpayer identification numbers (ITINs) and employer identification numbers (EINs)
  in civil and criminal cases", ending today's last-four allowance and adding EINs.
  They would also "Require the use of pseudonyms rather than initials to reference
  minors", and make clear that the rule reaches "all documents in the court filing,
  including exhibits and attachments." Bankruptcy Rule 9037 keeps last-four for
  SSN/TIN. **Comments are due 2027-02-15. The earliest effective date is 2028-12-01.**
  This is directly on ECFiler's redaction scanner: plan a rule-set switch keyed to the
  effective date, with bankruptcy courts exempt. A written comment from a
  redaction-tool author fits the C4 "contribute requirements" posture. Whether to file
  one is Jackson's call, and nothing has been drafted or sent.
- **Self-represented e-filing amendments**, same package (Civil 5 and 6, Appellate 25,
  Bankruptcy 5005/8011/9006/9036, Criminal 45/49). They would "presumptively permit
  self-represented litigants to file electronically (unless a court order or local
  rule bars them from doing so)". A court that bars them must offer "an alternative
  electronic means for filing (such as by email or upload)". On the same timeline, the
  earliest effective date is **2028-12-01**. This widens the filer population a
  prep tool serves, but not before 2028.
- **AI guidance (2026-09-17 release):** the AO's interim AI guidance covers courts
  only: "all Judiciary users have been reminded that they are accountable for all work
  performed with the assistance of AI." Nothing in it addresses litigant or filer
  tools.
- **Third-party access and credential sharing:** no new national AO statement was found
  in the window. The operative texts are still per-court notices, all *pre-window*
  (e.g. <https://www.ksb.uscourts.gov/news/third-party-services-and-access-cmecf>,
  <https://www.laed.uscourts.gov/case-information/cmecf/duty-protect-cmecf-filing-and-pacer-account-credentials>),
  warning that shared credentials or secondary NEF recipients expose sealed material.
  One new datapoint cuts the other way: the AO's own Oct 2026 newsletter tells users,
  "If you share an account with teammates, coordinate with them to avoid an account
  lockout." **"July 2023 memorandum":** no AO memorandum of that date about third-party
  access could be identified, so there is nothing to report on follow-ups. If this
  means a specific document, it needs its citation.

### Corrections made in this file (2026-11-13)

- A.1, Timeline and Next actions #2: "request PCL API credentials via PSC" is struck.
  No separate PCL credential exists; a PACER account authenticates directly (Oct 2026
  guide).
- A.1 and the budget table: annotated for the 2027-01-01 fee increase.
- E.1 district courts: annotated with the CMM end-2027 cutover for new district cases.

---

## Immediate next actions (this week)

1. Shortlist 3 outside-counsel candidates, email them for proposals. *(Track D)*
2. Register a dedicated PACER account for API + scraping; ~~request PCL credentials~~ (no separate PCL credentials exist; keep it PACER-only so MFA stays optional, corrected 2026-11-13). *(Track A.1)*
3. Draft 2-paragraph intro email to Mike Lissner at Free Law Project. *(Track B)*
4. Build the event-catalog crawler mode in the Playwright harness — reuse existing court profiles; target S.D.N.Y. training DB first as proof of concept. *(Track E.2, engineering)*

I can start #4 now if you want; #1–#3 need your voice and decisions.
