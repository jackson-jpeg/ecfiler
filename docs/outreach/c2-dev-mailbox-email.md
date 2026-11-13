# C2 — Dev-mailbox email (draft, held for approval)

**To:** developers@psc.uscourts.gov
**From:** jackson@sang3r.com
**Subject:** Three technical questions from a developer (PCL API / NextGen XML / modernization interfaces)

---

Hello,

I'm an independent software developer and a PACER account holder. I build ECFiler, an
open-source tool, still in development, that helps a filer prepare and check federal
filings on their own computer. It works against the documented public interfaces (the
PACER Authentication API and the PCL API). I have three technical questions I couldn't
resolve from the published documentation:

1. Does the PACER Case Locator API roadmap include docket-level data or
   near-real-time index updates, or should integrators continue to design around the
   nightly-refresh, case-index-only scope?

2. Is the NextGen CM/ECF XML Case Opening and Docketing interface intended to remain
   scoped to bankruptcy petition-preparation software, or is there any published plan
   to extend structured case-opening/docketing interfaces to other court types?

3. As the case-management modernization program proceeds, is there a channel where a
   practitioner-developer can direct interface requirements or feedback on future
   filing and data interfaces? Or is the EPA Public User Group the appropriate venue
   for that input?

Thank you for your time. Pointers to existing documentation are entirely sufficient
answers if I've missed something published.

Best regards,

Jackson Sanger
Independent Developer, ECFiler Project
jackson@sang3r.com · github.com/jackson-jpeg/ecfiler

---

<!-- lint:notes -->

### Register notes (why the draft reads this way)

- Three questions, each answerable in a sentence; no product pitch, no attachment,
  no ask for permission or endorsement.
- The signature states what Jackson actually is: an independent developer and PACER
  account holder building against documented public interfaces. An earlier draft
  described him as a docketing specialist at a national law firm, which is not true;
  a false professional identity in a letter to the AO would be indefensible if
  noticed, and the developer identity is the honest and sufficient standing for
  questions addressed to a *developer* mailbox.
- Question 3 deliberately tees up the EPA User Group so their answer creates a paper
  trail pointing to the venue we're already applying to.

### Refresh 2026-11-13 (true as of this date)

- **Address.** From/signature changed to `jackson@sang3r.com`. The ecfiler.com
  mailbox no longer exists, and no Gmail address goes on outbound correspondence.
  A reply to the old Gmail From would also have landed in a personal inbox.
- **Dropped "and I'm subscribed to the developer updates list".** It was true only
  once the GovDelivery signup (HUMAN-QUEUE #6, CAPTCHA) was done, and that row is
  still open. The letter now makes no claim that depends on a pending step, so it
  can be sent in either order.
- **"the court CM/ECF lookup feeds" removed.** The code uses exactly two documented
  interfaces: the PACER Authentication API (`ecfiler/pacer_auth.py`, `cso-auth`) and
  the PCL API (`ecfiler/pacer_search.py`, `pcl-public-api`). "Lookup feeds" named
  nothing specific.
- **"still in development" added.** No filing has completed through ECFiler (the
  only live run stopped at the court's permission wall; no NEF has been received).
  The phrase keeps the letter from implying a working product without making any
  claim about use.
- **No em dashes** in the letter body (two replaced with a period and a question).
- **Gmail draft is stale.** The draft in Jackson's Gmail predates all of the above
  (old From, the subscription claim, em dashes). Delete it and send this text from
  jackson@sang3r.com. Logged in `contact-tracker.md`.
- Follow-up: one polite nudge at +3 weeks, then stop.
