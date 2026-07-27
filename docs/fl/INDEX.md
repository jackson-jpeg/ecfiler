# Florida Courts E-Filing Authority — Certified Vendor / Batch Filing Program: Capture Inventory

- **Fetched:** 2026-07-27
- **Program entry point:** https://www.myflcourtaccess.com/authority/certified-vendors (live; did NOT 404)
- **Program status:** ACTIVE. The page's "Batch Filing As a Third-Party Vendor" section links the application, license agreement, test checklist, fees, FAQs, and an informational video. The license agreement PDF was re-uploaded (ADA-tagged) in March 2026 and the vendor list is dated 05/01/2025 — both indicate ongoing maintenance.

## Captured extracts (all PDFs were fetched and text-extracted in full)

| File | Source document | Source URL |
|---|---|---|
| `vendor-application.md` | Third Party Vendor Application, rev. 01-01-2021 (5 pp.) | https://documents.myflcourtaccess.com/uploads/2021/08/Third_Party_Vendor_Application_01-01-2021.pdf |
| `batch-license-agreement.md` | License Agreement for Third-Party Batch Filing (1/16/2018 template, ADA re-upload 2026-03) (5 pp.) | http://documents.myflcourtaccess.com/uploads/2026/03/Third_Party_Batch_Filing-License_Agreement_11618_ada.pdf |
| `test-case-checklist.md` | TPV Test Case Checklist v1.0 (1/21/2017) (10 pp.) — all 9 scenarios TS001–TS009 captured | https://documents.myflcourtaccess.com/uploads/2021/08/TPVTestCaseDocumentation_v1.pdf |
| `fee-schedule.md` | "Third Party Batch Filing Charges" (02/27/2017; fee table is an embedded image — transcribed) + License Agreement §3 + application fee | https://documents.myflcourtaccess.com/uploads/2021/08/Proposed_third_party_fees.pdf |
| `batch-filer-faq.md` | Batch Filing FAQ (7/25/2016) — complete, verbatim | https://documents.myflcourtaccess.com/uploads/2021/08/Batch_FAQs_7_25_16.pdf |
| `technical-specs.md` | Synthesis: TPV Application; FL Courts Technology Standards v4.0 (May 2025, 86 pp.); Test Checklist; TPV presentations; Authority FAQs | see file header |
| `certified-vendor-list.md` | Web list (23 vendors) + official PDF list dated 05/01/2025 (24 vendors, scopes/restrictions) | http://documents.myflcourtaccess.com/uploads/2025/05/05012024-TPV-List-1.pdf |

Original PDFs are preserved in `docs/fl/sources/` (application, license agreement, test checklist, FAQ, fee sheet, 2025 vendor list, Morgan & Morgan certification example, 2022 conformed-copies presentation).

## Documents identified but NOT captured (for human download / follow-up)

Not public — provided only after application approval (confirmed by the application's own text: "The Portal will provide the Applicants with the specifications and requirements"):
- "Third Party Vendor and ECF Specification" (Portal extensions to OASIS ECF 4.01) — no public URL found on myflcourtaccess.com, cms.myflcourtaccess.com, documents.myflcourtaccess.com, or flcourts.gov.
- Florida request/response XSD schemas and WSDLs for the Batch Interface, FilingReviewCompleteResult, NotifyFilingReviewComplete services.
- QA/TEST environment endpoints and credentials; court-specific code lists; error-case catalog for resiliency testing.

Public but fetched only in part / recorded by URL:
- Certified Vendor Informational Video — https://www.youtube.com/watch?v=GbSiZ7BANDo (video; not transcribed).
- Portal Security Policy (06/16/2020) — https://documents.myflcourtaccess.com/uploads/2021/08/Florida_Courts_E-Filing_Authority_Portal_Security_Policy_06_16_20final.pdf (downloadable; not extracted).
- Portal E-Filer User Manual (Aug 2023) — https://documents.myflcourtaccess.com/uploads/2023/12/Portal-E-Filer-User-Manual-August-2023_wip.pdf (portal UI manual, not TPV-specific).
- March 2022 vendor list (for deltas) — https://documents.myflcourtaccess.com/uploads/2022/03/E-FilingAuthority_Certified_Vendors_03012022.pdf
- Morgan & Morgan Request for Certification (completed example, 08/25/2022; text extracted, key content folded into test-case-checklist.md and technical-specs.md) — https://cms.myflcourtaccess.com/uploads/2022/08/Morgan-and-Morgan-Request-for-Certification.pdf
- TPV "Request for Access to Conformed Copies" presentation (03/15/2022; extracted) — https://cms.myflcourtaccess.com/uploads/2022/01/8-Presentation-TPV-Request-to-Florida-Courts-E-Filing-Authority.pdf
- FL Courts Technology Standards v4.0 (May 2025; extracted, relevant sections quoted in technical-specs.md) — https://flcourts-media.flcourts.gov/content/download/2455476/file/florida-courts-technology-standards-may-2025%20v4.pdf
- AOSC13-49 Electronic Service via the Portal — http://www.floridasupremecourt.org/clerk/adminorders/2013/AOSC13-49.pdf

## Dead/changed links

- https://www.myflcourtaccess.com/authority/publicnotices.html (referenced in the 2016 FAQ and older announcements) — superseded; the site's public-notices page is now https://www.myflcourtaccess.com/authority/public-notices, and the application/license agreement now live on the Certified Vendors page.
- No 404s encountered on any current link.

## Deltas vs. assumptions ("active with ~23 vendors")

1. **Program is active** — confirmed. ~23 is right: 23 vendors on the web page, 24 on the official 05/01/2025 PDF (PDF adds Caffeine Code and Landau & Associates; web page adds PaperTracker; the two lists are out of sync).
2. **Fees:** $500 non-refundable application fee + tiered monthly license fee $125–$250 by monthly document volume. No per-filing transaction fee, no revenue share, no stated renewal fee. Authority may revise fees on 30 days' notice.
3. **No insurance/bond requirement** in the application — only financial-stability references (3) and background/litigation disclosures under penalty of perjury.
4. **Docs are old but current:** the application (2021), checklist (2017), fee sheet (2017), FAQ (2016) are still the operative linked versions. The license agreement template still says "201_" and "Tim Smith, Chairman."
5. **Key gap for a build:** the actual wire spec (ECF 4.01 Portal extensions, XSDs, WSDLs, endpoints) is gated behind the $500 application — public docs give service names (Third Party Vendor Batch Interface, FilingReviewCompleteResult, NotifyFilingReviewComplete), the ECF 4.01 baseline, and the certification test plan, but not the schemas.
6. **Certification is per filing-path-per-division with a new application required to expand scope**, and capabilities like fee-bearing submissions, multi-document submissions, and Correction/Abandoned Queue handling are certified (and restricted) separately — see vendor list restrictions.
