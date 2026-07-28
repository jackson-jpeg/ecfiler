# C1 — Registration answer sheets (copy-paste, then click)

Both registrations are gated by a CAPTCHA, and the PACER one is an account
registration made under Jackson's identity with terms assent. Neither is
something automation should complete on his behalf, so what follows is the
exact keystroke-level answer set: open the URL, paste, solve the CAPTCHA, submit.

Field values marked `[JACKSON]` are personal data that exists nowhere in this
repo or on either machine. Everything else is filled in below.

---

## 1. GovDelivery — AO developer updates list

**URL:** <https://public.govdelivery.com/accounts/USFEDCOURTS/subscriber/new?topic_id=USFEDCOURTS_1821>

| Field | Value |
|---|---|
| Email Address | `realjacksons@gmail.com` |
| User Verification | MTCaptcha — type the characters shown |

Then **Submit**. The topic (`USFEDCOURTS_1821`, developer updates) is carried by
the URL, so no topic picking is needed.

**After submitting:** GovDelivery emails a confirmation link — click it, or the
subscription stays pending. Then, optionally, in subscriber preferences add
"PACER Announcements" as a second topic; the EPA monitor already watches that
page, so this is belt-and-suspenders rather than load-bearing.

*Status at time of writing: the form was reached and the email field filled, but
the MTCaptcha is an anti-automation control on a federal site and was left for
Jackson. Estimated: 30 seconds.*

---

## 2. QA PACER account (test environment — separate from the production account)

**URL:** <https://qa-pacer.psc.uscourts.gov/pscof/registration.jsf>
**Form:** "PACER — Case Search Only Registration"

| Field | Value |
|---|---|
| Prefix | *(leave as Select Prefix)* |
| First Name \* | `Jackson` |
| Middle Name | *(blank)* |
| Last Name \* | `Sanger` |
| Generation / Suffix | *(leave unselected)* |
| Date of Birth \* | `[JACKSON]` |
| Firm/Office | `ECFiler` — or the LLC name once formed (see `docs/fl/entity-recommendation.md`) |
| Unit/Department | *(blank)* |
| Address \* | `[JACKSON — street address]` |
| Room/Suite | *(blank)* |
| City \* | `Tampa` |
| State \* | `Florida` |
| Zip/Postal Code \* | `[JACKSON]` |
| Country \* | `United States of America` *(prefilled)* |
| Primary Phone \* | `[JACKSON]` |
| Alternate / Text / Fax | *(blank)* |
| Email \* | `realjacksons@gmail.com` |
| Confirm Email \* | `realjacksons@gmail.com` |
| User Type \* | `Individual` — **not** an attorney or firm type. He is not admitted to any bar, and user type is a representation to the AO. |
| CJA Attorney Panel checkbox | **unchecked** |
| User Verification \* | reCAPTCHA "I'm not a robot" |

Then **Next**.

**On the following screen — skip the credit-card section.** QA searches are free,
and there is no reason to put a payment instrument on a test account.

**Activation is overnight.** Expect access the next business day. Once active:

- Auth endpoint: `qa-pacer.uscourts.gov`
- Case Locator API: `qa-pcl.uscourts.gov`
- CSO login (what `ecfiler session login --qa` opens): `qa-pacer.login.uscourts.gov`

**Store the QA credentials in the keychain, not in this repo:**

```
[mac] printf '%s' '<qa-password>' | bash ~/ecfiler/scripts/mac/keychain-setup.sh '<qa-username>'
```

*Estimated: 60 seconds of typing, plus the overnight wait.*

---

## Why the QA account is the gating item for everything else

The staged-filing round trip to an NEF cannot happen until this account exists
and activates. `ecfiler session login --qa` and the whole QA filing path are
built and tested, but they have nothing to authenticate against until then.
Production PACER is explicitly out of bounds for that test.

Record both dates in `contact-tracker.md` once done.
