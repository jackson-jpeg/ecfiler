# C5 — Clerk inquiry: how to actually send it

**The Middle District of Florida does not publish an email address for CM/ECF
questions.** It publishes a web form, and that is the channel:

**<https://www.flmd.uscourts.gov/webforms/contact-cmecf>**

Verified 2026-07-28: the page reads "Complete the form below to request
assistance with CM/ECF. You must include both an email address and a telephone
number. A staff member will contact you as soon as possible."

So there is no email draft for C5: a draft addressed to a guessed
`clerk@flmd.uscourts.gov` would bounce or land nowhere. The letter text in
`c5-clerk-inquiry.md` is reflowed below to fit the form's fields.

---

## Form answers

| Form field | Value |
|---|---|
| Your Name \* | `Jackson Sanger` |
| Email Address \* | `jackson@sang3r.com` |
| Phone Number \* | `[JACKSON]`, format nnn-nnn-nnnn |
| Lawyer Name (if different from above) | *(leave blank: Jackson is not an attorney and writes for no lawyer)* |
| Lawyer Bar Number | *(leave blank)* |
| Topic \* | **CM/ECF Filing or General Information** (not Login or Password) |
| Division \* | **Tampa** (appears once the topic is chosen) |
| Case Number | *(leave blank: this is not case-specific)* |
| CAPTCHA | Jackson solves it |

Fields re-read from the live form on 2026-11-13 (`submitted[...]` names in the
page source). Since July the form gained the two optional Lawyer fields and a
CAPTCHA, and the free-text box for this topic is labelled "How may we help you?".
The page header names the Clerk of Court as Megan Mann.

## "How may we help you?" (paste this)

> I write in a personal capacity. By profession I am a litigation docketing
> specialist in Tampa; separately, I build an open-source tool that attorneys
> and their staff can run to help prepare filings, and I would like to build it
> to match what this court expects. I am not an attorney, and this inquiry is
> not made on behalf of any employer or client. I have a question I could not
> answer from the Administrative Procedures for Electronic Filing, and I would
> be grateful for the court's guidance.
>
> The tool is still in development and has not yet completed a filing in any
> court. It runs on the filer's own computer. It checks documents before filing
> (PDF format, and a scan for personal identifiers that need redaction), walks
> the filer through a pre-filing checklist, and fills in the CM/ECF screens for
> the filer to review. It is built to submit only through the filer's own CM/ECF
> login, in their own browser session, after the person at the keyboard reviews
> and authorizes that specific filing. Login credentials are never transmitted
> to or stored by any outside service, including mine.
>
> My question: does the court consider this kind of attorney-supervised,
> software-assisted preparation and submission to fall within the ordinary use
> of an attorney's ECF account by that attorney and their authorized staff? And
> is there anything the court would want filers using such tools to do, or to
> avoid, to stay squarely within its expectations?
>
> I would rather learn the court's preferences before the tool is finished than
> have filers discover them the hard way. If a different office or person is the
> right one for this question, I would appreciate a pointer.
>
> Thank you for your time.
>
> Jackson Sanger
> Independent Developer, ECFiler Project
> jackson@sang3r.com · github.com/jackson-jpeg/ecfiler

---

**Before submitting**, check whether the M.D. Fla. Administrative Procedures for
Electronic Filing contain an "authorized agent" or staff-use provision. If they
do, cite it by section number in the second paragraph: a question that shows
the filer read the local rules gets a materially better answer. If they don't,
send as written.

Estimated: 4 minutes, most of it the optional rules check and the CAPTCHA.

S.D. Fla. is the optional second send, only after M.D. Fla. responds or four
weeks pass. Record the date in `contact-tracker.md`.

---

**Refreshed 2026-11-13.** Email field and signature are `jackson@sang3r.com` (the
ecfiler.com mailbox no longer exists; no Gmail on outbound correspondence). The
pasted text is regenerated from `c5-clerk-inquiry.md` as of today: it now says the
tool is still in development and has not completed a filing, drops "deadline
checks" (the code has a checklist, not deadline computation), and says "runs on"
rather than "runs entirely on" the filer's computer (the optional AI checks send
document text to Anthropic under the filer's own key). Reasons in that file's notes.
The web form will send its confirmation and the clerk's reply to the Email field,
so it must be a mailbox Jackson reads.

