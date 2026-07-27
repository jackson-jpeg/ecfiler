# Florida Courts E-Filing Portal — Third Party Vendor Test Case Checklist

- **Source URL:** https://documents.myflcourtaccess.com/uploads/2021/08/TPVTestCaseDocumentation_v1.pdf
- **Linked from:** https://www.myflcourtaccess.com/authority/certified-vendors ("Test Case Checklist")
- **Version:** 1.0, created 1/21/2017 by the Portal Team (per Document Version Control table). 10 pages.
- **Fetched:** 2026-07-27 (full text extracted from the PDF)

## Purpose (verbatim)

> To define the test case scenarios required to be successfully completed in order to receive Certification in a filing path [New Case or Existing Case] and a Division [Circuit Civil, County Civil, Probate, Domestic Relations/Family, Juvenile Dependency, Juvenile Delinquency, Circuit Criminal, Criminal Traffic].

## Vendor Request for Certification

The vendor indicates the division(s) — Circuit Civil, County Civil, Probate, Domestic Relations/Family, Juvenile Delinquency, Juvenile Dependency, Circuit Criminal, Criminal Traffic — and the filing path (New or Existing Case) for which certification is requested.

## Terms and Definitions (verbatim)

- **Abandoned Filing Queue:** When a submission is returned to the Correction Queue the filer has five business days to correct the deficiency. If the submission is not corrected and resubmitted in those five days, the submission is moved to the Abandoned Filing Queue.
- **CMS:** Case Maintenance System
- **Correction Queue:** When a submission has a deficiency that needs to be corrected by the filer, the Clerk returns the submission to the Correction Queue.
- **Court/Clerk Case Number:** The case number used by the Clerk or the Court which is an abbreviated version of the Uniform Case Number (UCN).
- **Exhibit:** A document that is filed in support of a lead document.
- **Existing Case:** The filing path for a case that has been created and a Uniform Case Number assigned.
- **Filing Fee:** The statutory fee that is required to be paid when submitting a new case.
- **Lead Document:** The document that is filed with the Clerk that is requesting an action.
- **NEF:** Notice of Electronic Filing provides service of the documents in the submission and a PDF of the documents.
- **New Case:** The filing path that creates a new case to be filed with the Clerk.
- **Notification Email:** The emails that the Portal returns to the filer as the submission goes through the process.
- **Submission Number:** The number assigned to the submission when it is received by the Portal.
- **TPV:** Third Party Vendor
- **UCN:** The Uniform Case Number is a 20 character number assigned to a new case and is required for state reporting purposes.

## Instructions (verbatim)

> The Third Party Vendor shall complete the Vendor Information section of this document along with the Vendor Request for Certification. Based on the filing path, either New Case or Existing Case, the Third Party Vendor shall complete the Test Scenarios that apply to the filing path in which they are seeking Certification. The Third Party Vendor shall submit the Test Scenario to each County and fill in the Submission Number for each Test Scenario.
>
> The Test Scenarios may be completed and submitted one at a time or they may be done all together. The Test Scenario however must be submitted to all counties listed before sending to the Portal Team. Once the Portal Team or the County has reviewed and accepted the submission and the County has verified that the information has been accepted by their CMS, we will provide the results back to the TPV in this completed document.
>
> If a submission fails to process properly with one of the Counties, the Test Scenario must be repeated with all the Counties.
>
> Only complete the Scenarios that apply to the filing paths for which you are requesting certification. For example, if you are not seeking certification for the New Case filing path, you do not need to complete the Test Scenarios for a New Case.

## Submission Requirements (verbatim)

> 1) The appropriate test scenarios must be executed for each County below:
>    - Alachua County
>    - Brevard County
>    - Duval or Collier County
>    - Marion or Walton County
>    - Miami-Dade County
>    - Orange County
>    - Polk County
>    - Sarasota or St. Lucie County
> 2) Review Filing Requests (submitted by TPV) should contain court specific values and valid case information
> 3) If a TPV does not have the necessary test data for a given court, the Service Desk can provide the sample data to be used (example: Case Number, UCN, Document Group, Type, etc.)

Each scenario's Test Results table is filled per court (CMS): Submission #, Received Time, Completion Time, Pass/Fail, Remarks — one row each for Alachua; Brevard; Duval or Collier; Marion or Walton; Miami-Dade; Orange; Polk; Sarasota or St. Lucie. (Eight distinct county CMS targets per scenario.)

## Test Scenarios (complete list, TS001–TS009)

### TS001 — Existing Case filing path with 1 lead document, no filing fee
Description: Existing case filing with one lead document and no filing fee.

| Task # | Task Description |
|---|---|
| 1 | TPV Submit — existing case filing with one lead document and no filing fee |
| 2 | TPV Completes the Submission Number and sends email with the document attached to Support with a copy to Kyle Reichert |
| 3 | Portal Team/Clerk — Review and Accept |
| 4 | Clerk — Verify information in CMS |
| 5 | TPV Retrieve Status |
| 6 | TPV Retrieve Review Results |
| 7 | Portal Team Completes Test Results Section and Return to TPV |

### TS002 — Existing Case: 1+ lead documents & 1+ exhibit documents, no filing fee
Description: Existing Case filing with one or more lead documents and one or more exhibit documents and no filing fee.
Tasks: TPV Submit; email Submission Number to Support (cc Kyle Reichert); Portal Team/Clerk Review; Clerk Verify in CMS; TPV Retrieve Review Results; TPV Retrieve Status.

### TS003 — Existing Case: 1+ lead documents & 0+ exhibit documents, with filing fee
Description: Existing Case filing with one or more lead documents and zero or more exhibit documents and filing fee.
Tasks: same 6-step pattern as TS002.

### TS004 — Existing Case: 1+ lead documents & 0+ exhibit documents, fee waiver
Description: Existing Case filing with one or more lead documents and zero or more exhibit documents and **fee waiver request**.
Tasks: same 6-step pattern as TS002. (Note: the PDF's inner "Name:" field for TS004 mistakenly repeats "TS003 ... filing fee" — the section heading and description control.)

### TS005 — Existing Case: 1+ lead documents & 0+ exhibit documents, no filing fee — Correction Queue

| Task # | Task Description |
|---|---|
| 1 | TPV Submit — Existing Case filing with one or more lead documents and zero or more exhibit documents and no filing fee |
| 2 | TPV Completes the Submission Number and sends email with the document attached to Support with a copy to Kyle Reichert |
| 3 | Portal Team/Clerk — Send to correction queue |
| 4 | TPV — correction — Replace first lead document |
| 5 | TPV — correction — Add a new lead document |
| 6 | TPV — Submit corrected filing |
| 7 | Portal Team/Clerk — Review |
| 8 | Clerk — Verify information in CMS |
| 9 | TPV Retrieve Review Results |
| 10 | TPV Retrieve Status |

### TS006 — Existing Case: 1+ lead documents & 0+ exhibit documents, no filing fee — Abandoned

| Task # | Task Description |
|---|---|
| 1 | TPV Submit — Existing Case filing, 1+ lead documents, 0+ exhibits, no filing fee |
| 2 | TPV Completes the Submission Number and sends email to Support (cc Kyle Reichert) |
| 3 | Portal Team/Clerk — Send to correction queue |
| 4 | TPV — Take no action — no corrections |
| 5 | Portal Team/Clerk — Send to Abandoned queue |
| 6 | TPV Retrieve Review Results |
| 7 | TPV Retrieve Status |

### TS007 — New Case: 1+ lead documents & 0+ exhibit documents, with filing fee
Description: New case filing with one or more lead documents and zero or more exhibit documents and one or more plaintiffs and one or more defendants and filing fee.
Tasks: TPV Submit; email Submission Number to Support (cc Kyle Reichert); Portal Team/Clerk Review; Clerk Verify in CMS; TPV Retrieve Review Results; TPV Retrieve Status.

### TS008 — New Case: 1+ documents & 0+ exhibit documents, using fee waiver
Tasks: same 6-step pattern as TS007. (Note: the PDF's inner Name/Description fields for TS008 repeat the TS007 "filing fee" text — the section heading, table of contents, and results-summary table all say **fee waiver**, which controls.)

### TS009 — New Case: 1+ documents & 0+ exhibit documents, filing fee — Correction Queue

| Task # | Task Description |
|---|---|
| 1 | TPV Submit — new case filing, 1+ lead documents, 0+ exhibits, 1+ plaintiffs, 1+ defendants, filing fee |
| 2 | TPV Completes the Submission Number and sends email to Support (cc Kyle Reichert) |
| 3 | Portal Team/Clerk — Send to correction queue |
| 4 | TPV — correction — Change name of first plaintiff/petitioner |
| 5 | TPV — correction — Add a defendant |
| 6 | TPV — correction — Replace first lead document |
| 7 | TPV — correction — Add a new lead document |
| 8 | TPV — Submit corrected filing |
| 9 | Portal Team/Clerk — Review |
| 10 | Clerk — Verify information in CMS |
| 11 | TPV Retrieve Review Results |
| 12 | TPV Retrieve Status |

## Test Scenarios Results Summary (checklist as titled in the summary table)

| ID | Scenario | Pass/Fail |
|---|---|---|
| TS001 | Existing Case — 1 lead document, no filing fee | (blank) |
| TS002 | Existing Case — 1 or more lead documents & 1 or more exhibit document and no filing fee | (blank) |
| TS003 | Existing Case — 1 or more lead documents & 0 or more exhibit documents with a filing fee | (blank) |
| TS004 | Existing Case — 1 or more lead documents & 0 or more exhibit documents and fee waiver | (blank) |
| TS005 | Existing Case — 1 or more lead documents & 0 or more exhibit documents & no filing fee — Correction Queue | (blank) |
| TS006 | Existing Case — 1 or more lead documents & 0 or more exhibit documents & no filing fee — Abandoned Filing Queue | (blank) |
| TS007 | New Case — 1 or more lead documents & 0 or more exhibit documents with a filing fee | (blank) |
| TS008 | New Case — 1 or more documents & 0 or more exhibit documents using fee waiver | (blank) |
| TS009 | New Case — 1 or more lead documents & 0 or more exhibit documents with a filing fee — Correction Queue | (blank) |

## Support Contact (verbatim)

> If at any time in the process you need assistance, please contact support at support@myflcourtaccess.com or call 850-577-4609.

## Notes for a 1:1 test plan

- 9 scenarios x 8 county CMS targets = up to 72 test submissions per filing path/division combination (Existing Case = TS001–TS006; New Case = TS007–TS009).
- Any single-county failure requires re-running that scenario against **all** counties.
- Correction-queue tests exercise: replace lead document, add lead document, change first plaintiff/petitioner name, add defendant, resubmit.
- Abandoned-queue test requires deliberately taking no action so the submission ages out (5 business days) into the Abandoned Filing Queue, then retrieving results/status.
- Status retrieval is exercised in every scenario ("TPV Retrieve Status" / "TPV Retrieve Review Results"), matching the FilingReviewCompleteResult (polling) / NotifyFilingReviewComplete (callback) services in the application.
- The completed checklist plus application, fee, and executed license agreement feed a "Third Party Vendor Request for Certification" summary prepared by CiviTek (example: https://cms.myflcourtaccess.com/uploads/2022/08/Morgan-and-Morgan-Request-for-Certification.pdf).
