# C7: one note to the people who made an ECFiler account

*Drafted 2026-11-13 (session 7). NOT SENT. Waits for Jackson's okay
(HUMAN-QUEUE #3). Recipients are not listed here on purpose: they are the
outside accounts in the ECFiler Clerk app (9 on 2026-11-13; the one sang3r.com
account is Jackson's own and is left out). The operator reads them from Clerk
at send time.*

Hinshaw check: the two law-firm addresses are on `njlawflorida.com` and
`ofjlaw.com`. Neither is a Hinshaw & Culbertson domain (`hinshawlaw.com`), so
nobody is left out. The operator repeats this check against Clerk at send
time, in case a new account has arrived.

## How it goes out (after the okay)

One message per person, not one message with everyone on it. From
`ECFiler <hello@ecfiler.com>` (the verified Resend domain; send-only, so
replies go to the reply-to), reply-to `jackson@sang3r.com`. Plain text. No
tracking. The operator logs each Resend id in the ledger.

## The note (user-facing copy: no em dashes)

**Subject:** Your ECFiler account: where things stand

> Hi,
>
> You made an ECFiler account this year, and I owe you a straight update.
> ECFiler is not open yet. The signed-in filing workspace has been closed
> while I finish testing real filings against a federal court test system,
> so your account has not been able to do anything. I'm sorry if you tried.
>
> Your sign-in is still there. When filing opens, you will hear about it
> from me first.
>
> The free tools work today, with no account: court directory, filing fee
> lookup, event codes, a Rule 5.2 redaction scan, PDF validation and a
> certificate of service builder. They're at https://www.ecfiler.com/tools.
>
> If you'd rather I delete your account, reply and say so, and I will.
>
> Jackson
> ECFiler

## Why each sentence is true

| Sentence | Evidence |
|---|---|
| Workspace closed, account could not do anything | `web/lib/workspace.ts`; the API never had a public address (`docs/hosting-topology.md`, L25) |
| Testing against a court test system | L20, L27; `docs/qa-roundtrip/attended-run.md` |
| Sign-in still there | the Clerk app holds the accounts (session 7 recon) |
| Free tools, no account | the `/tools` routes pass anonymous GET 200 in `scripts/verify-production.sh` (L28) |
| Deletion on request | Clerk user delete; nothing else holds their data while the workspace is closed (Privacy §7) |
