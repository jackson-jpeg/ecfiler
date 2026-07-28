# C3 — EPA Public User Group application (FINAL — copy-paste package)

*Window expected to open ~Aug 2026 — i.e., imminently; check weekly starting now
(last cycle: opened Aug 2024, closed Sept 2, 2024, terms began Jan 1, 2025 — two-year
terms, up to 12 members). Selection criteria from the AO's own announcement: user type,
experience accessing records through PACER, frequency of usage, account status in good
standing, and commitment to collecting feedback from peers. Monitor:*
<https://www.uscourts.gov/court-records/electronic-public-access-public-user-group>

*The 2024 cycle used a web application form. Every field below carries final text to
paste into whatever the 2026 form presents. Fields whose exact options or existence
cannot be known until the form opens are marked `[VERIFY AT SUBMIT]`; the two facts
only Jackson can supply are marked `[JACKSON]`. Everything else is final.*

---

## Field package

**Full name:** Jackson Sanger

**Email:** realjacksons@gmail.com `[VERIFY AT SUBMIT — use the same email address as
the PACER account of record so "account in good standing" verifies cleanly]`

**Phone:** `[JACKSON — phone number]`

**City / State:** Tampa, Florida

**Affiliation / employer / organization:**
Applying in personal capacity. Litigation docketing specialist by profession
(legal sector; no employer is named or represented in this application), and author
and maintainer of ECFiler, an open-source court filing-preparation tool
(github.com/jackson-jpeg/ecfiler). *(If ECFiler LLC exists by submission — see
`docs/fl/entity-recommendation.md` — give the project affiliation as "ECFiler LLC
(founder)" and keep the personal-capacity framing.)*

**PACER account holder:** Yes — individual PACER account in good standing, held since
`[JACKSON — year account opened]`. Also registered on the QA-PACER test environment
for development use (per `docs/outreach/c1-registration-steps.md`), and subscribed to
the AO's developer updates list.

**User category:** `[VERIFY AT SUBMIT — the form's category list is unpublished until
it opens. Selection rule: pick the category for technology/service
providers/developers if one exists; otherwise "commercial user" or "other" with a
one-line description. Do NOT select "attorney" (Jackson is not one). One-line
description if a text field is offered:]* Litigation docketing specialist and
independent developer of open-source filing-preparation software; high-frequency
PACER user in both capacities, applying as an individual.

**Frequency / nature of PACER usage (usage-description field):**
High-frequency professional and individual use. PACER and CM/ECF are my daily working
environment as a litigation docketing specialist (stated in personal capacity; no
employer represented), and my individual account sees regular use — typically
`[JACKSON — honest frequency on the individual account, e.g. "several times per
week"]` — retrieving dockets and filed documents across district, bankruptcy, and
appellate courts to develop and test open-source filing-preparation tooling, plus
development use of the documented public interfaces (PACER Authentication API, PACER
Case Locator API, and the courts' published CM/ECF lookup feeds) and of court training
environments intended for practice filings. All automated access is rate-limited,
identifies itself with an honest User-Agent, and observes the AO's off-peak guidance
for bulk operations.

**Commitment to collecting feedback from peers (if asked directly):**
Yes. I maintain an open-source project with public issue tracking, and I am in regular
contact with the open-source legal technology community and the solo and small-firm
filers it is built for. I also work alongside docketing and filing professionals
daily. I commit to soliciting, collecting, and synthesizing feedback from both
communities between meetings and bringing it to the group in usable, specific form.

---

## Statement of interest (~250 words — final)

I am a litigation docketing specialist by profession and, in my personal capacity, the
author of ECFiler, an open-source tool built to help filers prepare compliant federal
court submissions: PDF and PDF/A validation, redaction scanning under Rule 5.2,
event-code verification, and pre-filing checklists, with every automated step
confirmed by the human filer. I work with the Judiciary's electronic public access
systems every day from both sides: professionally, in PACER and CM/ECF as part of
litigation docketing work, and as a developer building against the documented public
interfaces — the Authentication API, the PACER Case Locator API, and the courts'
published lookup feeds. I apply as an individual; no employer is represented here.

I am applying because the modernization of case management and public access systems
will determine what independent and open-source tools can responsibly do for the users
who depend on them: solo and small-firm attorneys, legal aid organizations, and
self-represented litigants who cannot afford enterprise platforms. That community's
requirements — documented and stable public interfaces, clear terms for automated
access, consistent validation rules across courts — are underrepresented next to large
commercial vendors, and I can state them concretely, from working code rather than
opinion.

I would contribute specific, current, technical experience of the public access
interfaces as they exist today, informed by daily professional use; a commitment to
gathering and synthesizing feedback from the open-source legal technology community
and the solo and small-firm filers it is built for; and a
contributor-of-requirements posture — I am not seeking special access for my own
project, but a channel for developer-users to be heard. I would gladly attend the
annual meeting and do the between-meeting work.

---

## One-page résumé (if the form accepts an upload — final skeleton)

**Jackson Sanger** — Tampa, FL · realjacksons@gmail.com · `[JACKSON — phone]`

**Litigation docketing specialist** (`[JACKSON — years, stated honestly; employer
deliberately unnamed — this application is personal]`)
- Daily PACER and CM/ECF work across federal district, bankruptcy, and appellate
  courts: docketing, deadline calculation, filing mechanics.

**Author and maintainer, ECFiler** (`[JACKSON — start year]`–present, personal
open-source project)
- ECFiler: open-source (MIT) filing-preparation tool for federal CM/ECF practice —
  PDF/PDF-A validation and conversion, Rule 5.2 redaction scanning, event-code
  verification, certificate-of-service generation, pre-flight checks, and an
  append-only, hash-chained audit trail; web UI, CLI, and API; court metadata for 207
  federal courts.
- Daily integration work against the Judiciary's documented public interfaces (PACER
  Authentication API, Case Locator API, CM/ECF court lookup feeds) and court training
  environments; QA-PACER registered; subscribed to the AO developer updates list.
- Applicant for certification as a Florida Courts E-Filing Portal third-party batch
  filing vendor `[VERIFY AT SUBMIT — state accurately: "applicant" once mailed,
  omit if not yet mailed]`.

**Prior:** `[JACKSON — one line per prior role, honestly stated]`

**Education:** `[JACKSON — degree, school, year]`

---

<!-- lint:notes -->

## Presentation decision (deliberate)

The application presents Jackson as exactly what he is: a solo, independent developer
of open-source filing-preparation tooling and a frequent individual PACER user. Points
of discipline, in order:

1. **True profession, personal capacity, no employer.** Jackson is in fact a
   litigation docketing specialist in Tampa — the profession is real and is claimed,
   because the AO's criteria reward genuine high-frequency professional PACER
   experience. What is never claimed: the employer's name or description (a firm that
   has not consented must not be implicated, and the AO's reply would file next to
   its name), any organizational voice ("we", "our staff"), or any suggestion that
   ECFiler is used in that professional work or by anyone — it has never filed for a
   client. Session-2 drafts removed the profession entirely on the mistaken premise
   it was fabricated; session 3 restored the true profession while keeping every
   employer reference out. `tests/test_copy_lint.py` enforces all of this.
2. **Developer-user, not vendor.** ECFiler is disclosed plainly and by name (it is the
   basis of the experience claimed), but the application does not pitch it. The
   posture throughout is contributor of requirements on behalf of the developer- and
   small-filer community — explicitly *not* petitioning for special access,
   partnership, or endorsement. If the form asks directly about commercial interests,
   answer fully: open-source MIT-licensed project; hosted tier exists; applying
   separately for Florida state e-filing vendor certification.
3. **Constituency, not company.** The peer-feedback commitment — a stated selection
   criterion — is grounded in the open-source legal tech community and the solo/small-
   firm and legal-aid users ECFiler targets, which is a real, reachable network for a
   public project with public issue tracking.
4. **Consistency check before submit:** the identity here must match C2
   (`docs/outreach/c2-dev-mailbox-email.md`) and any other correspondence already
   sent to the AO or PSC. C2 speaks as an independent developer and does not mention
   the profession — that is consistent (this file adds a fact, contradicts nothing),
   but re-read whatever was actually sent before this goes in. `[VERIFY AT SUBMIT]`

## Submission mechanics

- Check the monitor URL weekly from now; the window is expected to be ~2 weeks long.
- Log the open date, submission date, and confirmation in
  `docs/outreach/contact-tracker.md`.
- Save a copy of the completed form (screenshots or printed PDF) with this file.
