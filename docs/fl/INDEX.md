# Florida Courts E-Filing Authority — Certified Vendor / Batch Filing Program: Capture Inventory

- **Fetched:** 2026-07-27; **re-checked 2026-11-13** (section below)
- **Program entry point:** https://www.myflcourtaccess.com/authority/certified-vendors (live; did NOT 404)
- **Program status:** ACTIVE. The page's "Batch Filing As a Third-Party Vendor" section links the application, license agreement, test checklist, fees, FAQs, and an informational video. The license agreement PDF was re-uploaded (ADA-tagged) in March 2026 and the vendor list is dated 05/01/2025 — both indicate ongoing maintenance.

## Re-check 2026-11-13: what changed since July 2026

**Requirements: no substantive change.** Application rev. 01-01-2021, **$500**
nonrefundable fee, P.O. Box 16428 mailing address, license agreement (1/16/2018
template), monthly fees $125 to $250, test checklist v1.0: all still current. What
did change:

| What | Before (2026-07-27) | Now (2026-11-13) | Source |
|---|---|---|---|
| Application file linked | `uploads/2021/08/Third_Party_Vendor_Application_01-01-2021.pdf` | ADA re-upload `uploads/2026/05/Third_Party_Vendor_Application_01-01-2021_ADA.pdf` (Last-Modified 2026-05-06); same words at the same coordinates on all 5 pages | https://documents.myflcourtaccess.com/uploads/2026/05/Third_Party_Vendor_Application_01-01-2021_ADA.pdf |
| Test checklist file linked | `uploads/2021/08/TPVTestCaseDocumentation_v1.pdf` | ADA re-upload `uploads/2026/05/TPVTestCaseDocumentation_v1_ADA.pdf`; text identical, still v1.0 | https://documents.myflcourtaccess.com/uploads/2026/05/TPVTestCaseDocumentation_v1_ADA.pdf |
| Official vendor list | 05/01/2025, 24 vendors | **07/30/2026, 27 vendors** (+Bail Bond Hub, Heist Weiss & Wolk, Pro Legal Serve; eFileMadeEasy renamed First Legal Buyer) | http://documents.myflcourtaccess.com/uploads/2026/07/07302026-TPV-List.pdf |
| License agreement, Vendor Fees PDF, Batch FAQ | as captured | byte-identical (sha256) | Certified Vendors page |
| TPV fee/process review | none known | **Board work group appointed 2026-06-22** (Hon. John Tomasino) to review TPV processes and fees; no report as of 2026-11-13 | https://cms.myflcourtaccess.com/uploads/2026/07/Minutes-June-22-2026-1.pdf §XI |

Board materials read for this check (all via the Authority's own WordPress API,
`https://cms.myflcourtaccess.com/wp-json/wp/v2/meetings`, because the Meetings page
renders them with JavaScript):

- 2026-06-22 minutes (work group appointed): https://cms.myflcourtaccess.com/uploads/2026/07/Minutes-June-22-2026-1.pdf
- 2026-07-27 agenda and draft minutes (Pro Legal Serve approved; no work-group report): https://cms.myflcourtaccess.com/uploads/2026/07/Agenda-July-27-2026.pdf, https://cms.myflcourtaccess.com/uploads/2026/09/Minutes-July-27-2026-draft.pdf
- 2026-09-30 agenda (TPV approvals: Connect2Court, Southron, Flash Justice; no fee item): https://cms.myflcourtaccess.com/uploads/2026/09/E-Filing-Agenda-September-30-2026.pdf. Its minutes are not posted yet.
- 2026-11-02 agenda (security briefing and a CaseAccess integration request from a legal-research vendor; no TPV item): https://cms.myflcourtaccess.com/uploads/2026/10/E-Filing-Agenda-November-2-2026-2.pdf
- Next meeting 2026-12-08, 2:00 pm ET, WebEx: https://cms.myflcourtaccess.com/uploads/2026/10/Public-Notice-12-08-26.pdf
- Related, not a TPV requirement: on 2026-06-16 the Florida Supreme Court asked the
  Authority to add a Portal notice that filers are responsible for the accuracy of
  everything they submit, "including documents that have been produced using
  technology such as generative artificial intelligence" (Rule 2.515(d)):
  https://cms.myflcourtaccess.com/uploads/2026/06/06162026-Portal-Notification-on-GenAI.pdf.
  Relevant to how ECFiler's AI checks are described to Florida filers.

New files in `docs/fl/sources/` (originals kept): `Third_Party_Vendor_Application_01-01-2021_ADA.pdf`,
`TPVTestCaseDocumentation_v1_ADA.pdf`, `07302026-TPV-List.pdf`,
`Minutes-June-22-2026-1.pdf`, `Minutes-July-27-2026-draft.pdf`,
`E-Filing-Agenda-September-30-2026.pdf`, `06162026-Portal-Notification-on-GenAI.pdf`.
All read as data only, with PyMuPDF under `python3 -I`.

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
