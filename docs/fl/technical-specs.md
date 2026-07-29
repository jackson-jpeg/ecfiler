# Florida Courts E-Filing Portal — TPV/Batch Technical Interface Notes

- **Fetched:** 2026-07-27
- **Primary sources:**
  - Third Party Vendor Application, rev. 01-01-2021 — https://documents.myflcourtaccess.com/uploads/2021/08/Third_Party_Vendor_Application_01-01-2021.pdf
  - Florida Courts Technology Standards, Version 4.0, adopted May 2023, revised May 2025 — https://flcourts-media.flcourts.gov/content/download/2455476/file/florida-courts-technology-standards-may-2025%20v4.pdf (86 pp., full text extracted)
  - TPV Test Case Checklist v1.0 — https://documents.myflcourtaccess.com/uploads/2021/08/TPVTestCaseDocumentation_v1.pdf
  - "Request for Access to Conformed Copies" TPV presentation to the Authority, March 15, 2022 — https://cms.myflcourtaccess.com/uploads/2022/01/8-Presentation-TPV-Request-to-Florida-Courts-E-Filing-Authority.pdf
  - Morgan & Morgan Request for Certification (completed example, 08/25/2022) — https://cms.myflcourtaccess.com/uploads/2022/08/Morgan-and-Morgan-Request-for-Certification.pdf
  - Authority FAQs page — https://www.myflcourtaccess.com/authority/faqs
  - Portal Security Policy (06/16/2020) — https://documents.myflcourtaccess.com/uploads/2021/08/Florida_Courts_E-Filing_Authority_Portal_Security_Policy_06_16_20final.pdf (not extracted; URL recorded)

## 1. ECF / LegalXML version and message contract

From the TPV Application (verbatim):

> The Applicant must use the **ECF 4.01 Specification and Portal extensions** to integrate all available services.

> Applicant must adhere to the web services definition stated in **Florida's associated XSD document** that contains the schema for input XML (requests) and output XML (responses) messages.

> Functionality test cases will determine the Applicant's ability to implement and consume the web services defined in the **Third Party Vendor and ECF Specification**.

- The referenced "Third Party Vendor and ECF Specification" and the Florida XSDs are **not published publicly** — they are provided by the Portal team/CiviTek after application approval ("The Portal will provide the Applicants with the specifications and requirements"). The OASIS base spec is public: Electronic Court Filing Version 4.01, https://www.oasis-open.org/standards/ (cited in Appendix B of the FL Technology Standards).
- FL Technology Standards v4.0, Section 7 (Data Exchange): data-exchange MDEs "will follow these two principal elements as formulated in the ECF 4.0.1 (or current) standard" — core specifications defining MDEs/operations/messages, plus Service Interaction Profiles. Data content is constrained through namespaces and XSD files; XML schemas "are the only normative representations of the messages."
- Transport (Standards 7.4, near-verbatim): "All data transport should be secured and encrypted in compliance with ECF 4.0.1, Section 5, Service Interaction Profiles." HTTPS (HTTP over TLS) required for public-facing interfaces; CA-registered certificates with 2048-bit or longer keys; WSDL "strongly recommended."

## 2. Web services named in the program documents

- **Third Party Vendor Batch Interface service** — the submission access point ("Organizations must be able to consume the URL for Third Party Vendor Batch Interface service"). Vendor must provide a **callback URL** and its **IP address**.
- **ReviewFiling** (implied by "Review Filing Requests (submitted by TPV) should contain court specific values and valid case information" — Test Case Checklist).
- **FilingReviewCompleteResult** — polling service to poll the Portal for status updates.
- **NotifyFilingReviewComplete** — push/callback service; Portal posts status to the vendor. Vendor must supply: IP Address, Fully Qualified Domain Name, Web Service URL, HTTP or HTTPS.
- Statuses are returned as submissions are processed; e-service is performed by the Portal; submissions are completed by the County (Application, Functional Requirements).

## 3. Environments and credentials

From the TPV Application (near-verbatim):

- **QA Portal** (Florida Courts E-Filing QA Portal): first electronic testing environment. Credentials issued by the Authority **after application approval**; without them the web service cannot be accessed.
- **TEST environment**: credentials issued after QA testing completes; used for the final **end-to-end test** before certification.
- Sequence: email XML samples for review → approval → electronic submission to QA → TEST credentials → end-to-end roundtrip (accepted by Portal, County CMS, status returned) on **all** requested case types and filing paths → certification.
- The Morgan & Morgan example confirms CiviTek administers this: XML samples per case type and filing path approved by CiviTek; credentials issued for TEST, QA, or both.

## 4. Document standards (Florida Courts Technology Standards v4.0, Section 2)

Verbatim/near-verbatim from Sections 2.1.2–2.1.4:

- "The Portal will accept new filings in Word, PDF, and PDF/A formats. The preferred format for filing is the PDF/A format where original document intelligence has been maintained."
- Delivery to clerk: PDF/A as filed if already approved PDF/A; Word converted to PDF/A; other searchable PDF converted to PDF/A; **non-searchable PDF rasterized** (bitmap) into approved PDF/A. "Digital signatures and digital notarizations will not be passed or maintained by the Portal."
- **Size:** "A single submission, whether consisting of a single document or multiple documents, shall not exceed 50 megabytes (50 MB) in size." (Trial courts; appellate/Supreme Court limits are higher — 200 MB per Portal FAQs.)
- Formatting: letter size 8.5x11, one-inch margins, consecutively numbered pages, black and white, searchable and printable; recording space 3"x3" top-right first page, 1"x3" subsequent pages for documents to be recorded.
- Scanned documents: OCR, minimum 300 DPI.
- **Permitted PDF/A intelligence elements:** bookmarks, electronic signatures, attachments created using the Insert feature to append pages, internal links, embedded internal hyperlinks, embedded persistent external hyperlinks, embedded images.
- **Prohibited PDF/A elements:** embedded attachments, comments, annotations, hidden deleted items (purge them), embedded non-persistent external hyperlinks, embedded thumbnails, form fields and actions, JavaScript, embedded non-display data.
- **Encryption prohibited:** "A compliant PDF/A file must be open and available to anyone or any software that processes the file. User IDs and passwords may not be embedded."
- Accessibility: must comply with Fla. R. Gen. Prac. & Jud. Admin. 2.526; ADA/Section 508 (Standards Section 8.1).
- File names: no `"` `#` `%` `&` `*` `:` `<` `>` characters (Section 2.1.6); max 150 bytes including spaces.
- "Deviation from these guidelines may result in the submitted filing being moved to the Correction Queue by the Clerk with the filer being notified via e-mail and requested to correct the issue(s) with the document(s) and resubmit the filing."
- Confidentiality: filer is responsible under Rules 2.420 and 2.425; Portal displays a mandated warning about the Notice of Confidential Information requirement.

## 5. Correction queue / abandoned queue behavior (Standards Sections 2.2.5, 2.2.9)

Near-verbatim:

- "A filing may be placed in a correction queue for any reason that prevents the filing from being accepted into the clerk's case maintenance system ('CMS'), e.g., documents that cannot be associated with a pending case; a corrupt file; or an incorrect filing fee."
- "Once placed in a correction queue, the clerk shall attempt to contact the filer using the filer's registered e-mail address and ask the filer to correct the identified issue(s) and resubmit. If not corrected, the filing will remain in a correction queue for no more than 5 (five) business days, after which time the filing will be moved to the abandoned filing queue."
- The Portal validates each submission pre-transmission (incomplete data, unacceptable document type, viruses); virus-infected or corrupt submissions go to the correction queue; filer is emailed immediately on detected discrepancies; "validation rules will be specific to the type of submission (for example, new case initiation as opposed to filings in an existing case)."
- "The Portal shall support both a single session filing process and a **system-to-system** process." (Section 2.2.8 — the TPV batch interface is the system-to-system path.)
- Docket sequence numbers are NOT included in the Portal-to-CMS interface and are not returned to the filer (Section 2.2.6).
- TPV-specific queue mechanics are exercised in test scenarios TS005/TS006/TS009: replace lead document, add lead document, change first plaintiff name, add defendant, resubmit; no-action submissions age out to the Abandoned Filing Queue after 5 business days (see test-case-checklist.md).

## 6. E-service (Fla. R. Gen. Prac. & Jud. Admin. 2.516)

- The batch interface performs e-service as a functional requirement: "E-service will be performed" (TPV Application). The NEF ("Notice of Electronic Filing provides service of the documents in the submission and a PDF of the documents" — Test Case Checklist definitions) is the service artifact.
- Service through the Portal is authorized by AOSC13-49, "Electronic Service via the Florida Courts E-Filing Portal" — http://www.floridasupremecourt.org/clerk/adminorders/2013/AOSC13-49.pdf (linked from https://www.myflcourtaccess.com/authority/documents), implementing e-service under Rule 2.516 (e-mail service / service via the Portal equivalent).
- No TPV-specific 2.516 guidance is published; the Portal maintains the e-service lists per case and serves the NEF on submission.

## 7. Fees / payment settlement mechanics

- Statutory filing fees are collected through the Portal at submission: "The payment method is settled at the time the filing is submitted." Accepted: Discover, MasterCard, American Express, VISA; Electronic Check (checking/savings). Convenience fees: "Credit Cards = 3.5% of Filing Fee"; "Electronic Check = $5 flat rate". Bank statement descriptor: `ePortal + {filing ID}`. (Authority FAQs page, https://www.myflcourtaccess.com/authority/faqs.)
- An incorrect filing fee is an enumerated correction-queue reason (Standards 2.2.5).
- Fee waiver flows are first-class in the TPV interface: dedicated certification scenarios TS004 (existing case, fee waiver) and TS008 (new case, fee waiver).
- Vendor-side program charges (separate from statutory fees): $500 application fee + tiered monthly license fee — see fee-schedule.md. Some vendors are certified with a "No submission with fee" restriction (see certified-vendor-list.md), i.e., fee-bearing submissions are a separately certified capability.

## 8. Conformed copies (2022 program discussion)

The March 15, 2022 presentation to the Authority ("Request for Access to Conformed Copies") documents that parties/TPVs sought return of conformed (file-stamped) copies through the interface; options discussed were (a) Portal includes documents in responses to parties and TPVs, or (b) parties/TPVs retrieve documents they eFile from CCIS. Data flow diagram: Filer/TPV → Portal → Clerk/Court → Court CMS → CCIS. Status of implementation not stated in public documents.

## 9. What is NOT public (must be requested after applying)

- The "Third Party Vendor and ECF Specification" document (Portal extensions to ECF 4.01).
- Florida's XSD schema files for request/response messages; WSDL for the Batch Interface, FilingReviewCompleteResult, and NotifyFilingReviewComplete services.
- QA/TEST environment URLs and credentials.
- Court-specific code lists (Document Group/Type, case types per county) — the Service Desk provides sample data during testing (Test Case Checklist, Submission Requirements #3).
- Error-code catalog for the resiliency test cases (application references "provided error test cases").

Support contact for the program: support@myflcourtaccess.com, 850-577-4609.

## 10. ECF 4.01 message-layer skeleton (built 2026-07-29 — gap item #4)

`ecfiler/courts/florida/ecf401.py` (tests: `tests/test_ecf401.py`). Every
design decision traces to a captured source; everything Florida-proprietary
is isolated behind one placeholder namespace and priced as rework.

| Decision in code | Primary source |
|---|---|
| Message set: ReviewFiling request (CoreFilingMessage), MessageReceipt at submission, FilingReviewComplete on review | TPV Application (verbatim, §1 above): "must use the ECF 4.01 Specification and Portal extensions"; services named in §2 above (Batch Interface, FilingReviewCompleteResult, NotifyFilingReviewComplete) |
| Namespaces keep the `-4.0` suffix (ECF 4.01 is an errata release of 4.0); NIEM 2.0 for core/justice content | OASIS Electronic Court Filing Version 4.01 (public), https://www.oasis-open.org/standards/ ; FL Technology Standards v4.0 §7 ("XML schemas are the only normative representations of the messages") |
| Florida-specific placement (county code, filing code) isolated in `FL_EXTENSION_NS`, a placeholder URI | §9 above — Florida's XSDs and the "Third Party Vendor and ECF Specification" are released only after application approval; nothing outside that constant may hard-code a Florida wire detail |
| Existing Case only; new-case construction unrepresentable (raises) | Recommended certification scope, `docs/fl-certification-gap-analysis.md` §5 |
| Fee-bearing submissions raise | Same scope decision (§5 point 5); machine-to-machine fee settlement undocumented (§7 above) |
| Case identity carried as the 20-character UCN via `parse_ucn` (strict) | AOSC order / Tech Memo captured in `ecfiler/courts/florida/ucn.py` |
| 50 MB submission cap enforced at request construction | Technology Standards §2.1.2 (§4 above, verbatim) |
| Filename rules enforced on every attachment | Technology Standards §2.1.6 via `document_rules.validate_filename` |
| Review statuses map onto the `SubmissionStatus` lifecycle; unknown statuses raise rather than guess | Test Case Checklist TS001–TS006 status vocabulary; Application "statuses are returned as submissions are processed" |

**Expected rework when the gated XSDs arrive** (gap analysis §6 item #5):
element placement/ordering, the real extension namespace URI, attachment
encoding details (inline base64 vs reference), SOAP envelope + WSDL
bindings, and the authoritative status vocabulary. The invariants (illegal
states raise; UCN, size, filename enforcement) carry over unchanged.
