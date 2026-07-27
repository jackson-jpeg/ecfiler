# C1 — Day-one registrations (Jackson executes; ~10 minutes total)

Both of these bind your identity, so they're prepared here for you to click through.
Both verified live 2026-07-27 against
<https://pacer.uscourts.gov/file-case/developer-resources>.

## 1. Subscribe to the AO developer updates list (GovDelivery)

- URL: <https://public.govdelivery.com/accounts/USFEDCOURTS/subscriber/new?topic_id=USFEDCOURTS_1821>
  (this is the exact link the official Developer Resources page publishes for
  "developer updates")
- Enter name + email. Recommend your professional email, since this list is the paper
  trail of good-faith engagement.
- After signup, in subscriber preferences confirm the topic is the developer-resources
  one; optionally also add PACER Announcements.

## 2. Register a QA PACER account (test environment)

- URL: <https://qa-pacer.psc.uscourts.gov/pscof/registration.jsf>
- Register as an individual. **Skip the credit-card section** — QA searches are free.
- Activation is overnight; expect access the next business day.
- QA endpoints once active: `qa-pacer.uscourts.gov` (auth), `qa-pcl.uscourts.gov`
  (Case Locator API).
- Keep the QA credentials out of the repo; keyring or password manager.

## After both: record dates in `contact-tracker.md`.
