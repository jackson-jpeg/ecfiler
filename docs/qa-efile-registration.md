# E-filing rights for the QA account: which route, and how

Research date: 2026-11-13 (session 7 branch). Every page cited below was read
on that date unless it says otherwise. Nothing was submitted, registered, sent
or logged into while writing this. "Inferred" marks a conclusion that no source
states outright.

Context: ledger L15 and L20, risk register R-014 and R-015, HUMAN-QUEUE item 3,
runbook section "Requesting e-filing privileges".

## Answer

1. **Filer type:** a **Non-Attorney E-File Registration**. Never "Attorney Admissions / E-File Registration": that path asserts bar admission, which Jackson does not have. The runbook's step 2 currently names the attorney path and is wrong for this account.
2. **Where:** QA realm Manage My Account (`https://qa-pacer.psc.uscourts.gov/pscof/manage/maint.jsf`) → Maintenance → Non-Attorney E-File Registration. Court: Az Test District Court (AZTTDC) first. If it is not in the dropdown, Az Tc1b Bankruptcy Court (AZTTBK, `https://ecf.tc1b.aztc.uscourts.gov`, reachable) with role Creditor. Same day, send the short email below to the PACER Service Center (`pacer@psc.uscourts.gov`), because a QA test court likely has no clerk watching its registration queue (inferred).
3. **Who approves:** the court the request is routed to. For QA courts that is whoever runs the AO test servers (the bankruptcy hosts call themselves "Testing Services Division"), not a clerk's office (inferred). The PSC is the only published human contact for the QA realm.
4. **Expected time:** no source states a QA turnaround. Real courts quote 48 hours (Minnesota Bankruptcy's training database) to "varies from court to court". Plan on 1 to 2 weeks including one email round trip (inferred). If the PSC says QA accounts cannot e-file, this route is closed and the honest fallback is a production non-attorney registration in a real court for a real reason, which is out of scope here.
5. **Jackson personally:** about 15 minutes. Log in on the Mac, read the court and role dropdowns (tells us which QA courts accept registration), submit the form, send the email. No one else can do either step: both bind his identity.

## Findings with sources

### 1. Filer types, and which a non-attorney can hold

- PACER divides filers into **attorney** and **non-attorney**. The QA site's own page (`https://qa-pacer.uscourts.gov/register-account/non-attorney-filers-cmecf`, identical text on `https://pacer.uscourts.gov/register-account/non-attorney-filers-cmecf`):
  > "Non-attorneys are considered: pro se filers, court reporters, interested parties, filing agents, creditors, trustees, or U.S. Trustees. Not all courts accept non-attorney filers and some only accept specific types of non-attorney filers."
- The attorney page (`https://qa-pacer.uscourts.gov/register-account/attorney-filers-cmecf`): "First time users will be prompted to register for a PACER account and then select to apply for attorney admissions or electronic filing registration available for the selected court." That is the attorney path. Jackson cannot use it.
- **Role in Court** dropdown values, as real courts document them (production; the QA dropdown is unseen):
  - Middle District of Tennessee Bankruptcy (`https://www.tnmb.uscourts.gov/sites/tnmb/files/How_to_Register_as_a_NonAttorney_Filer_with_TNMB.pdf`): "Trustee; US Trustee; Creditor (Limited Filer); Court Reporter (Transcriber); Party (Pro Se & Interested Parties); and Filing Agents."
  - Nevada Bankruptcy (`https://www.nvb.uscourts.gov/downloads/cm-ecf/nextgen/New%20E-File%20Registration%20-%20Non-Atty.pdf`): Court Reporter, Creditor, Filing Agent, Trustee, US Trustee.
  - Northern District of New York Bankruptcy, revised 2026-04-21 (`https://www.nynb.uscourts.gov/sites/nynb/files/CMECF/Non-Attorney%20E-File%20Registration%20for%20NYNB%20through%20PACER_04-21-2026.pdf`): "A Non-Attorney E-File Registration may be submitted for a Creditor, Filing Agent, Trustee, U.S. Trustee, Claims Agent, or Auditor."
- Which a non-attorney can **legitimately** hold, for Jackson specifically:
  - **Creditor (limited filer)** in a bankruptcy court is the natural fit. It needs no bar admission, and the AO's claims spec (`https://pacer.uscourts.gov/sites/default/files/files/BankruptcyCreditorClaimsSpecs.pdf`, revised 12/29/2017) describes exactly this account: "A claims filer (who is not an attorney already registered with CM/ECF) may obtain a limited access login and password from each court". In production it presumes he is a creditor in a real case. In a QA court the cases are fictitious, so the role is a test role (inferred).
  - **Filing Agent** files *for* an attorney or trustee, whose name goes in the docket text, and NYNB requires "the attorney or trustee must email our Court to request that your 'Filing Agent' account be added". It needs a sponsoring attorney. Not usable alone.
  - **Party (pro se / interested party)** in a district court means being a party to a case. Only plausible in a test court with fictitious cases (inferred).
  - Trustee, U.S. Trustee, Court Reporter: not true of Jackson. Do not choose.
- **NEF caveat.** Nevada's guide says "a filing agent or creditor will not receive Notices of Electronic Filing (NEFs)" by email for case activity. That is about notices of *other* filings. The filer of a transaction still gets the NEF for it: the claims spec says claims filers "receive electronic notice of electronic filing (NEF) for successful transactions". CM/ECF also displays the NEF on screen at the end of every filing (standard CM/ECF behavior, not confirmed on a QA court: inferred).
- **QA bankruptcy test courts exist.** The QA roster lists 32 bankruptcy entries. Eight answer from the VPS: AZTTBK/TC1BK (`ecf.tc1b`, "Testing Services Division - BK CM/ECF TC1B Server"), TC1BTE (`ecf-test.tc1b`, 302), TC4LBK (`ecf.tc4b`), TC8LBK (`ecf.tc8b`, 302), TCEBK (`ecf.tceb`), TC9BK (`ecf.tc9b`, "Bankruptcy Ver 10.10 - LIVE") and TCFBK (`ecf.tcfb`). The roster's AZTTBK page names `webmaster@aztc.uscourts.gov` as the court email. That is a test-data contact field, not a confirmed mailbox (inferred). Do not write to it.

### 2. QA Manage My Account and E-File Registration

- The production procedure, quoted from `https://pacer.uscourts.gov/register-account/non-attorney-filers-cmecf`:
  > "For courts using NextGen CM/ECF: Log into Manage My Account, select the Maintenance tab, and select Non-Attorney E-File Registration."
  > "Upon completion, the registration is transmitted to the court for verification and processing. Document filing and access to restricted cases/documents in a court is not permitted until that court processes the registration request."
  > "Processing time for electronic filing registration varies from court to court."
- The PACER FAQ (`https://pacer.uscourts.gov/help/faqs/file-a-case?items_per_page=All`): "Click either Attorney Admissions/E-File Registration or Non-Attorney Admissions E-File Registration. Once request is submitted, you will need to wait for the court to process the request and grant you electronic filing privileges."
- **The QA realm has the same registration machinery.** `https://qa-pacer.psc.uscourts.gov/pscof/registration.jsf?filerType=N` returns 200 with the heading "Non-Attorney E-File Registration" (filerType=A gives "Attorney Admissions and/or E-File Registration"). The QA attorney page links straight to `registration.jsf?filerType=A`. So the QA PSC offers e-file registration as a function. **Whether any QA court appears in its court dropdown is unknown.** That list loads only after login (or after the account-information step of a new registration), and neither was attempted.
- `https://qa-pacer.psc.uscourts.gov/pscof/manage/maint.jsf` now 302s to `https://qa-pacer.psc.uscourts.gov/pscof/login.xhtml` (checked 2026-11-13 from the VPS). On 2026-07-30 it went to `qa-login.uscourts.gov`. Either way it is a login wall.
- Approval and turnaround: no QA-specific statement exists anywhere found. Comparable published figures:
  - Minnesota Bankruptcy's *training* database (`https://www.mnb.uscourts.gov/sites/mnb/files/Training_PACER_Registration%20and%20Request%20E-Filing%20Privileges.pdf`, revised January 2021): "You will receive an email from the Court that your CM/ECF account has been created and you are ready to file. If you do not hear from the Court in 48 hours, call the Court's technical help desk".
  - South Dakota Bankruptcy's training database (`https://www.sdb.uscourts.gov/sites/sdb/files/Filing%20in%20the%20NextGen%20CMECF%20Training%20Database.pdf`) asks the registrant to email named staff after submitting. Registrations to a test database are worked by people only when someone is told about them.

### 3. QA and test courts

- QA roster (`https://qa-pacer.uscourts.gov/file-case/court-cmecf-lookup`, fetched 2026-11-13): **94 rows.** 32 bankruptcy, 37 appellate or BAP, 23 district or "National" (AZTTDC and TC8LDC are typed National), plus PCL and SCOTUS. Full table below.
- Reachability from the VPS (`curl -m 15`, GET, 2026-11-13): **every `*.aztc.uscourts.gov` host on the QA roster answers (200 or 302)**, except `ecf-train.tc1b` (timeout) and `ecf-test.tc4b` / `ecf-train.tc4b` (TLS certificate name mismatch). **Every `*.aocms.uscourts.gov` host times out**, and three (`cmgb`, `cmwb`, `pv2b`) do not resolve. That matches L15. A spot check from the Mac the same day agreed: `ecf.tc1d` and `ecf.tc1b` 200, `ecf.cmmd.aocms` timeout.
- AZTTDC detail page: the roster calls it "NextGen CM/ECF Release 1.8 (Revision 1.8.5)", "District Cm/ecf V 1.8.5 [7/17/2026] - Live". The server's own login page says "District Ver 10.8.4 - LIVE" and sends the browser to `qa-login.uscourts.gov/csologin/login.jsf?pscCourtId=AZTTDC`.
- Our registry (`ecfiler/courts/data/qa_courts.json`) holds only `azttdc`. Adding AZTTBK would also need a bankruptcy filing route, which does not exist (R-014).
- **A third realm exists and has never been considered in this repo: TRAIN.** `https://train-pacer.uscourts.gov` (PSC at `train-pacer.psc.uscourts.gov`, login at `train-login.uscourts.gov`, which has a `services/cso-auth` endpoint answering 405 to GET, just as QA's does). Its roster (`https://train-pacer.uscourts.gov/file-case/court-cmecf-lookup`) lists 361 entries: real courts' `ecf-train.<court>` (155) and `ecf-test.<court>` (204) databases. Real clerk's offices staff these, and they publish procedures for registering in them, non-attorneys included (SDB above: "If you are requesting filing privileges as a non-attorney, complete Steps 17-20"). **It is unusable from here.** Of 356 distinct URLs probed from the VPS, 351 time out, 3 do not resolve, and only `ecf.tc7b.aztc` (an AO test server) and `train-pcl` answer. From the Mac, `ecf-train.sdb` and `ecf-train.mnb` also time out, while live `ecf.sdb.uscourts.gov` answers 200 from the VPS. So the training databases are filtered by source address (inferred). Who is allowed through is unknown.

### 4. AO and PACER developer documentation on test filer accounts

- Developer Resources (`https://pacer.uscourts.gov/file-case/developer-resources`): APIs for authentication and PCL, release notes, court lookup feeds, bankruptcy XML case-opening specs "intended for bankruptcy petition preparation software vendors". **No test filer account offer.** Its contact line: "Suggestions for additional content or comments about developer resources may be emailed" (mailto `developers@psc.uscourts.gov`).
- PACER Authentication API guide (`https://pacer.uscourts.gov/sites/default/files/files/PACER%20Authentication%20API-2025_v2_0.pdf`, p. 4):
  > "For API testing, a separate PACER QA environment is available. This environment contains test data for searching, and searches are not billable. To access this environment, a QA PACER account is required. This account is separate from any other PACER accounts and can only be used in the QA environment."
- PCL API guide (`https://pacer.uscourts.gov/sites/default/files/files/PCL-API-10-2026.pdf`, §2): "The QA environment contains a subset of test PCL data and searches are not billable."
- Both describe QA for *searching*. **Neither mentions filing in QA.** No document found offers software vendors a test *filer* account. The one vendor-adjacent filing provision is the bankruptcy claims spec above, and it is per court: "obtain a limited access login and password from each court".
- PSC contact routes (QA Contact Us, `https://qa-pacer.uscourts.gov/contact-us`): phone 1-800-676-6856, San Antonio 210-301-6440, 8 a.m. to 6 p.m. CT weekdays, email `pacer@psc.uscourts.gov`, and a web form. These are the production PSC's contacts. The QA site has no separate desk.
- PACER FAQ: "Access to the filing portion of CM/ECF is available to authorized users only. ... Authorization and training of users is provided by the individual federal court."
- **Conclusion: there is no published, sanctioned route for a software developer to get a test filer account.** The registration machinery exists in QA. Whether anyone processes it there is the open question, and only the PSC can answer it.

### 5. Why this route

- It costs one form and one email, uses the account that already works end to end (L20 reached case-number entry), and needs no code change if AZTTDC is approved.
- The training realm would be the better-documented route (real clerks, published 48-hour turnaround, non-attorney roles named), but nothing in it is reachable from either machine. It is a fallback only if the PSC says so and someone explains how access is granted.
- A production non-attorney registration in a real court would be fast and well documented, but it needs a real role in a real case. A test filing in a live court is not a legitimate use. Out.
- The email goes to the PSC rather than `developers@psc.uscourts.gov`. The PSC owns QA accounts and is the only contact the QA site publishes. The developer mailbox is published for comments on the developer pages. If the PSC does not answer within two weeks, the same text can go to the developer mailbox once (judgment call).

## QA court table

From `https://qa-pacer.uscourts.gov/file-case/court-cmecf-lookup`, 2026-11-13. "Reachable" is one GET with a 15-second timeout from the VPS. "Accepts e-file registration" is unknown for every court until open unknown 1 is answered. An unreachable court is moot whatever the answer. Our registry today: `azttdc` only.

| Code | Name | Type | CM/ECF URL | Reachable from VPS (HTTP) | Accepts e-file registration |
|---|---|---|---|---|---|
| AOTTBK | Ao Oca-td Test Bankruptcy Court | Bankruptcy | https://ecf.cm1b.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMMLBK | Ao-cmso Bankruptcy Court (cmmb) | Bankruptcy | https://ecf.cmmb.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMMLDC | Ao-cmso District Court (cmmd) | District | https://ecf.cmmd.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| TC5LDC | Az (tc5d) | District | https://ecf.tc5d.aztc.uscourts.gov | y (200) | unknown |
| TC6LDC | Az (tc6d) | District | https://ecf.tc6d.aztc.uscourts.gov | y (200) | unknown |
| TC7DC | Az (tc7d-live) | District | https://ecf.tc7d.aztc.uscourts.gov | y (200) | unknown |
| AZT4CA | Az Current Gen (tc4a) | Appeals | https://ecf.tc4a.aztc.uscourts.gov | y (200) | unknown |
| TC1TBK | Az Tc1b (train) - Bankruptcy Court | Bankruptcy | http://ecf-train.tc1b.aztc.uscourts.gov | n (timeout) | moot (unreachable) |
| AZTTBK | Az Tc1b Bankruptcy Court | Bankruptcy | https://ecf.tc1b.aztc.uscourts.gov | y (200) | unknown |
| TC1BK | Az Tc1b Bankruptcy Court | Bankruptcy | https://ecf.tc1b.aztc.uscourts.gov | y (200) | unknown |
| TC1BTE | Az Tc1b-(test)- Bankruptcy Court | Bankruptcy | https://ecf-test.tc1b.aztc.uscourts.gov | y (302) | unknown |
| TC4LBK | Az Tc4b | Bankruptcy | https://ecf.tc4b.aztc.uscourts.gov | y (200) | unknown |
| TC4D | Az Tc4d (live) | District | https://ecf.tc9d.aztc.uscourts.gov | y (200) | unknown |
| TC8LBK | Az Tc8b Bankruptcy Court | Bankruptcy | https://ecf.tc8b.aztc.uscourts.gov | y (302) | unknown |
| TC8LDC | Az Tc8d District Court | National | http://ecf.tc8d.aztc.uscourts.gov | y (302) | unknown |
| TCEBK | Az Tceb Bankruptcy Court | Bankruptcy | https://ecf.tceb.aztc.uscourts.gov | y (200) | unknown |
| AZTTDC | Az Test District Court | National | https://ecf.tc1d.aztc.uscourts.gov | y (200) | unknown |
| TCELDC | Az Tsd District (tced) | District | https://ecf.tced.aztc.uscourts.gov | y (200) | unknown |
| TC9BK | Az Tsd Tc9b | Bankruptcy | https://ecf.tc9b.aztc.uscourts.gov | y (200) | unknown |
| TC9DC | Az Tsd Tc9d | District | https://ecf.tc9d.aztc.uscourts.gov | y (200) | unknown |
| TCFBK | Az Tsd Tcfb | Bankruptcy | https://ecf.tcfb.aztc.uscourts.gov | y (200) | unknown |
| CMAAP | Cmso (cmaa) | Appeals | https://ecf.cmaa.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMAAB | Cmso (cmaa-bap) | Appeals | https://ecf.cmaa.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMDA | Cmso (cmda) Court of Appeals | Appeals | https://ecf.cmda.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMDB | Cmso (cmdb) Bankruptcy Court | Bankruptcy | https://ecf.cmdb.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMDD | Cmso (cmdd) District Court | District | https://ecf.cmdd.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMNLBK | Cmso (cmnb) Bankruptcy Court | Bankruptcy | https://ecf.cmnb.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMRLBK | Cmso (cmrb) Bankruptcy Court | Bankruptcy | https://ecf.cmrb.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMXAP | Cmso (cmxa) Court of Appeals | Appeals | https://ecf.cmxa.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMXAB | Cmso (cmxa-bap) Court of Appeals | Appeals | https://ecf.cmxa.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PVALCA | Cmso (pvaa) - Rhel7 Nextgen | Appeals | https://ecf.pvaa.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PVALBK | Cmso (pvab)- Rhel7 Nextgen | Bankruptcy | https://ecf.pvab.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PVALDC | Cmso (pvad)- Rhel7 Nextgen | District | https://ecf.pvad.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PVKLBK | Cmso (pvkb) Bankruptcy Court | Bankruptcy | https://ecf.pvkb.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PVNLBK | Cmso (pvnb) Bankruptcy Court | Bankruptcy | https://ecf.pvnb.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM1BK | Cmso Bankruptcy Court (cm1bk) | Bankruptcy | https://ecf.cm1b.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM2XBK | Cmso Bankruptcy Court (cm2b) | Bankruptcy | https://ecf.cm2b.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM6B | Cmso Bankruptcy Court (cm6b) | Bankruptcy | https://ecf.cm6b.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMLBK | Cmso Bankruptcy Court (cmlb) | Bankruptcy | https://ecf.cmlb.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMYXBK | Cmso Bankruptcy Court (cmyb) | Bankruptcy | https://ecf.cmyb.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMZBK | Cmso Bankruptcy Court (cmzb) | Bankruptcy | https://ecf.cmzb.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PVFB | Cmso Bankruptcy Court (pvfb) | Bankruptcy | https://ecf.pvfb.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM5A | Cmso Cm5a | Appeals | https://ecf.cm5a.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM5AB | Cmso Cm5a-bap | Appeals | https://ecf.cm5a.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM5B | Cmso Cm5b | Bankruptcy | https://ecf.cm5b.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM5D | Cmso Cm5d | District | https://ecf.cm5d.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM8D | Cmso Cm8d | District | https://ecf.cm8d.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMAB | Cmso Cmab | Bankruptcy | https://ecf.cmab.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMGB | Cmso Cmgb | Bankruptcy | https://ecf.cmgb.aocms.uscourts.gov | n (no DNS) | moot (unreachable) |
| CMWB | Cmso Cmwb | Bankruptcy | https://ecf.cmwb.aocms.uscourts.gov | n (no DNS) | moot (unreachable) |
| CMYAB | Cmso Cmya-bap | Appeals | https://ecf.cmya.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM1AC | Cmso Court of Appeals (cm1a) | Appeals | https://ecf.cm1a.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM2XAC | Cmso Court of Appeals (cm2a) | Appeals | https://ecf.cm2a.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM8AP | Cmso Court of Appeals (cm8a) | Appeals | https://ecf.cm8a.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM8APB | Cmso Court of Appeals (cm8a-bap) | Appeals | https://ecf.cm8a.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMCAC | Cmso Court of Appeals (cmca) | Appeals | https://ecf.cmca.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMJAC | Cmso Court of Appeals (cmja) | Appeals | https://ecf.cmja.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMJAB | Cmso Court of Appeals (cmja-bap) | Appeals | https://ecf.cmja.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMKA | Cmso Court of Appeals (cmka) | Appeals | https://ecf.cmka.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMLAC | Cmso Court of Appeals (cmla) | Appeals | https://ecf.cmla.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMMAB | Cmso Court of Appeals (cmma-bap) | Appeals | https://ecf.cmma.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PVDAC | Cmso Court of Appeals (pvda) | Appeals | https://ecf.pvda.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PVFAC | Cmso Court of Appeals (pvfa) | Appeals | https://ecf.pvfa.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM1D | Cmso District Court (cm1d) | District | https://ecf.cm1d.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMLXDC | Cmso District Court (cmldc) | District | https://ecf.cmld.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMODC | Cmso District Court (cmod) | District | https://ecf.cmod.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMQDC | Cmso District Court (cmqd) | District | https://ecf.cmqd.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMYXDC | Cmso District Court (cmyd) | District | https://ecf.cmyd.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PVFDC | Cmso District Court (pvfd) | District | https://ecf.pvfd.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PVLLDC | Cmso District Court (pvld) | District | https://ecf.pvld.aocms.uscourts.gov/ | n (timeout) | moot (unreachable) |
| PVNDC | Cmso District Court (pvnd) | District | https://ecf.pvnd.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM2XDC | Cmso District Court(cm2d) | District | https://ecf.cm2d.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PVDDC | Cmso District Court(pvdd) | District | https://ecf.pvdd.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PV2B | Cmso Pv2b | Bankruptcy | https://ecf.pv2b.aocms.uscourts.gov | n (no DNS) | moot (unreachable) |
| PVGA | Cmso Pvga | Appeals | https://ecf.pvga.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PVGB | Cmso Pvgb | Bankruptcy | https://ecf.pvgb.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CM2AB | Court of Appeals Cmso (cm2a-bap) | Appeals | https://ecf.cm2a.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| CMYXAC | Court of Appeals Cmso (cmya) | Appeals | https://ecf.cmya.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| PVTLAB | Court of Appeals Cmso (pvta-bap) | Appeals | https://ecf.pvta.aocms.uscourts.gov/ | n (timeout) | moot (unreachable) |
| 00PCL | Pacer Case Locator | District | https://qa-pcl.uscourts.gov | y (302) | n/a (PCL, not a court) |
| SCOTUS | Supreme Court of the United States | National |  | no URL | n/a |
| TC4XBK | Tc4b (test) | Bankruptcy | https://ecf-test.tc4b.aztc.uscourts.gov | n (TLS name mismatch) | moot (unreachable) |
| TC4TBK | Tc4b (train) | Bankruptcy | https://ecf-train.tc4b.aztc.uscourts.gov | n (TLS name mismatch) | moot (unreachable) |
| CMMLCA | U.S. Court of Appeals, Ao-cmso (cmma) | Appeals | https://ecf.cmma.aocms.uscourts.gov | n (timeout) | moot (unreachable) |
| TC4LCA | U.S. Court of Appeals, Az (tc4a) - Live | Appeals | https://ecf.tc4a.aztc.uscourts.gov | y (200) | unknown |
| TC7LCA | U.S. Court of Appeals, Az (tc7a) | Appeals | https://ecf.tc7a.aztc.uscourts.gov | y (200) | unknown |
| AZTTCA | U.S. Court of Appeals, Az Tc1a | Appeals | https://ecf.tc1a.aztc.uscourts.gov | y (200) | unknown |
| AZ2XCA | U.S. Court of Appeals, Az Tc2a-test | Appeals | https://ecf-test.tc2a.aztc.uscourts.gov | y (200) | unknown |
| TC5LCA | U.S. Court of Appeals, Az Tc5a - Live | Appeals | https://ecf.tc5a.aztc.uscourts.gov | y (200) | unknown |
| TC5BCA | U.S. Court of Appeals, Az Tc5a BAP Live | Appeals | https://ecf.tc5a.aztc.uscourts.gov/ | y (200) | unknown |
| TC6LCA | U.S. Court of Appeals, Az Tc6a | Appeals | https://ecf.tc6a.aztc.uscourts.gov | y (200) | unknown |
| TC7BCA | U.S. Court of Appeals, Az Tc7a BAP Live | Appeals | https://ecf.tc7a.aztc.uscourts.gov/ | y (200) | unknown |
| TC8LCA | U.S. Court of Appeals, Az Tc8a | Appeals | https://ecf.tc8a.aztc.uscourts.gov | y (200) | unknown |
| PVTLCA | U.S. Court of Appeals, Cmso (pvta) | Appeals | https://ecf.pvta.aocms.uscourts.gov | n (timeout) | moot (unreachable) |

## Click path

On the Mac, in a normal browser. Every step is Jackson's.

1. Open `https://qa-pacer.psc.uscourts.gov/pscof/manage/maint.jsf`. It redirects to a login page. Log in with the QA account `ecfilercom`.
2. Click the **Maintenance** tab.
3. Click **Non-Attorney E-File Registration**. (Not "Attorney Admissions / E-File Registration".)
4. **Court Type:** U.S. District Courts. **Court:** open the dropdown and **write down every QA court listed, for district and then bankruptcy**. That list answers open unknown 1. Pick **Az Test District Court** if present.
5. **Role in Court:** pick the most accurate non-attorney role offered. In a district court that is likely "Party" or "Pro Se" or "Interested Party". Write down the list.
6. If AZTTDC is not listed: Court Type **U.S. Bankruptcy Courts**, Court **Az Tc1b Bankruptcy Court** (or any of AZTTBK, TC1BK, TC4LBK, TC9BK, TCEBK, TCFBK, the reachable ones), Role **Creditor**.
7. If no QA court is listed under either type: stop. Do not submit anything. Send the email in its "nothing listed" form.
8. Check the box acknowledging that you are the individual registering. Complete the starred fields: name, address, email `jackson@sang3r.com`. Choose email notice options (the NEF needs them on). Click **Next**.
9. Payment screen: leave blank (QA is not billable) and click **Next**.
10. Read and acknowledge the Non-Attorney E-Filing Terms and Conditions, then **Submit**. Screenshot the confirmation page.
11. Record the date, court and role in `HUMAN-QUEUE.md` item 3.
12. Send the email below the same day.
13. To check status: Maintenance → **Check E-File Status**. This is per court guides for production; the QA label is unseen. "Processed" means granted. Then run the existing non-filing check:

```
[MAC] ~/ecfiler/scripts/mac/ecfiler-mac session filing-access --qa --court azttdc
```

(For a bankruptcy court the registry needs an entry first. Not done here.)

## Draft request

To: `pacer@psc.uscourts.gov` (or the form at `https://qa-pacer.uscourts.gov/contact-us`)
From: `jackson@sang3r.com`
Subject: QA account ecfilercom: e-filing privileges in a QA test court

> Hello,
>
> I have a QA PACER account, username ecfilercom, which I registered at qa-pacer.uscourts.gov to test software I am writing against the published PACER interfaces. The account logs in and can query the Az Test District Court (AZTTDC, https://ecf.tc1d.aztc.uscourts.gov). CM/ECF shows it only Query, Reports, Utilities, Help and Log Out, so it has no filing privileges there.
>
> I would like to make one test filing in a QA test court and see the Notice of Electronic Filing that CM/ECF returns. On [DATE] I submitted a Non-Attorney E-File Registration through the QA Manage My Account for [COURT], role [ROLE]. *(If nothing was listed, replace this sentence with: "The QA Manage My Account did not list any QA test court when I opened Non-Attorney E-File Registration.")*
>
> Can a QA account be given e-filing privileges in AZTTDC or another QA test court, such as the Az Tc1b Bankruptcy Court? If so, who processes the request? If the QA environment is not meant for test filings, a pointer to the right environment would fully answer my question.
>
> About me: I am not an attorney. I work in litigation docketing, and I am writing in a personal capacity as an independent developer. This is development testing against test data only.
>
> Thank you,
> Jackson Sanger
> jackson@sang3r.com

Checked against the identity rules in `tests/test_copy_lint.py`: no employer named or implied, singular voice throughout, no claim that the software is in use, no em dashes, no gmail address.

## Open unknowns

1. **Which QA courts the QA e-file registration dropdown lists, and which roles.** It is visible only after logging in to the QA Manage My Account (click path steps 4 to 6). Nobody has looked.
2. **Whether anyone processes registrations sent to a QA test court**, and how fast. Only the PSC can say.
3. **Whether the QA account's terms allow filing at all.** The API guides describe QA as "test data for searching". Silence is not permission, and not prohibition either.
4. **Whether a QA test court's NEF is emailed or only shown on screen** for a non-attorney or creditor role (inferred: on screen at least).
5. **How the training realm's `ecf-train` and `ecf-test` hosts grant network access.** They time out from both machines, while live courts on the same address blocks answer. Possibly an allowlist. Unknown who is let through.
6. **AZTTDC's version:** the roster says NextGen 1.8.5 and the server banner says "District Ver 10.8.4". This matters only for selectors later (R-014).
7. Not verified: the "Check E-File Status" label in the QA Manage My Account. It comes from production court guides.
