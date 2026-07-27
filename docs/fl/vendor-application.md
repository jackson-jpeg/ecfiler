# Florida Courts E-Filing Portal — Third Party Vendor Application (Batch Filing)

- **Source URL:** https://documents.myflcourtaccess.com/uploads/2021/08/Third_Party_Vendor_Application_01-01-2021.pdf
- **Linked from:** https://www.myflcourtaccess.com/authority/certified-vendors ("Batch Filing Application")
- **Document revision:** rev. 01-01-2021 (5 pages)
- **Fetched:** 2026-07-27 (full text extracted from the PDF)

## Applicant Contact Information (form fields, page 1)

- Applicant Name
- Contact Name
- Contact Email
- Contact Phone #

## Overview of Process (verbatim)

> Applicants (individuals or entities (including law firms, etc.) seeking to batch file (i.e., accomplish Machine to Machine filing) through the Florida Courts E-Filing Portal (the "Portal") must first complete this Application and pay a nonrefundable $500.00 application fee.

> The Applicant must complete the following steps in order to seek certification as an authorized third-party vendor:
>
> - Applicants seeking to batch file through the Portal must submit a Third-Party Vendor Application to the Florida Courts E-Filing Authority (the "Authority").
> - The application and fee must be mailed to:
>
>   Florida Courts E-Filing Authority
>   P.O. Box 16428
>   Tallahassee, FL 32317
>
> - Applicants must complete the testing period to develop and test the vendor-developed interface required to batch file through the portal.
> - Applicants who successfully complete the testing process may apply to the Authority for certification. To do so, the Applicant will be required to execute a license agreement for Authority approval.
> - Once the License Agreement is approved by the Authority, the Applicant will be certified to batch file through the Portal.

## Certification focus areas (verbatim)

> The certification process focuses on three main areas:
> 1. **Functionality.** Functionality test cases will determine the Applicant's ability to implement and consume the web services defined in the Third Party Vendor and ECF Specification.
> 2. **Adherence to Standards.** Applicant must adhere to the web services definition stated in Florida's associated XSD document that contains the schema for input XML (requests) and output XML (responses) messages.
> 3. **Resiliency.** Additional test cases focus on the Applicant's ability to handle errors identified and communicated by the Portal, such as scheduled service and unscheduled system outages. Applicants must successfully account for each of the provided error test cases during the certification process. This includes providing validation logic that addresses all preventable failures (e.g., applicant error prevention failures) and non-preventable failures (e.g., user error).

## Business Rules (verbatim)

> 1. The Portal will provide the Applicants with one access point to submit documents
> 2. The Portal will provide the Applicants with the specifications and requirements
> 3. The Portal team will work with the Applicants to ensure compliance with the standards and the ability to communicate with the Portal

## Business Requirements (verbatim)

> 1. The Applicant must use the ECF 4.01 Specification and Portal extensions to integrate all available services
> 2. Organizations must be able to consume the URL for Third Party Vendor Batch Interface service
> 3. Provide call back URL
> 4. Provide the Portal with IP address
> 5. Perform an end to end test

## Functional Requirements (verbatim)

> 1. The documents are submitted by the Applicants to the Portal
> 2. The Portal will deliver those submissions to the appropriate Clerk
> 3. The various statuses will be returned to the Applicant as the submissions are processed
> 4. E-service will be performed
> 5. Submissions will be completed by the County

## XML Review (verbatim)

> Each Applicant is required to submit XML via email before sending the XML electronically via the web service. The Applicant shall provide a sample XML of each case type and filing path (New and/or Existing). The Authority will confirm the development of the XML and determine if the Applicant is ready to begin testing electronically with the Portal. Upon completion of this review, Applicants will receive notification that the XML submitted has been correctly developed.

## XML Submission (verbatim)

> Once an Applicant has received approval of the XML development, they may begin testing electronically in the Florida Courts E-Filing QA Portal (the "QA Portal"). The Applicant shall electronically submit XML samples to each of the case types they wish to be certified. The Applicant shall also submit XML in each filing path (New and/or Existing). All XML submissions must be electronically sent to the QA environment.

## User Credentials (verbatim)

> Each Applicant must have active credentials to the QA Portal. Without these credentials the Applicant will not be able to access the QA environment via the web service. The Authority will provide the Applicant with these credentials after the Application has been approved.
>
> The Applicant will also need credentials in the TEST environment. These credentials will be provided after the Applicant has completed their testing in the QA environment. The Applicant shall provide an end to end test before receiving final certification.

## Established Connectivity (verbatim)

> Connection must be established between the Applicant's application and Portal. The connection will be between the Applicant's software and the QA and TEST environments. The two applications must be able to consume XML from each other.

## Filing Status Retrieval (verbatim)

> There are two methods of retrieving statuses from the Portal. The Applicant can use the **FilingReviewCompleteResult** (polling service) to poll the portal for status updates. The other option would be to use the **NotifyFilingReviewComplete** (status returned by portal service) to receive the status from the portal.

If using NotifyFilingReviewComplete, the applicant must provide: IP Address; Fully Qualified Domain Name; Web Service URL; HTTP or HTTPS.

## End to End Processing (verbatim)

> Each Applicant is required to submit XML that has been accepted by the Portal, County CMS, and received the status back to the Applicant. The Applicant must submit roundtrip processing on all case types and filing paths before approval of final certification.

## Filing Paths — case type selection grid (page 3)

Applicant must be granted approval per case type. Grid columns: Pleading on Existing Case / Case Initiation / Proposed Orders.

| ECF Case Type | CCIS Court Type | Notes |
|---|---|---|
| Citation | Traffic Infractions (TR) | Case Initiation "Not Supported" |
| Citation | Criminal Traffic (CT) | |
| Civil | Circuit Civil (CA) | |
| Civil | County Civil (CC) | |
| Civil | Small Claims (SC) | |
| Civil | Probate (CP) | |
| Civil | Guardianship (GA) | |
| Civil | Mental Health (MH) | |
| Criminal | Felony (CF) | Case Initiation "Not Supported" |
| Criminal | County Ordinance (CO) | |
| Criminal | Misdemeanor (MM) | |
| Criminal | Municipal Ordinance (MO) | |
| Criminal | Non-Criminal Infraction (IN) | |
| Domestic | Domestic Relations/Family (DR) | |
| Juvenile | Delinquency (CJ) | |
| Juvenile | Dependency (DP) | |

## Acknowledgments and Agreements (verbatim, page 4)

> Applicant acknowledges and agrees that:
> - Applicant may not copy, download, scrape, store, publish, transmit, retransmit, disseminate, broadcast, circulate, sell, resell, reverse engineer, modify or make derivative works of any of the components of the Portal.
> - Under no circumstances may the Portal be used, in whole or in part, as the basis for creating a product that provides the same, or substantially the same, functionality as the Portal.
> - Applicant expressly acknowledges and accepts its responsibility under applicable law for any loss, damage, or injury to persons or property arising from Applicant's authorized use of the Portal, including, but not limited to, the unauthorized disclosure of confidential information.
> - Applicant forever discharges and holds harmless the Authority and its Contractors from all present and future claims, demands, costs, judgments, suits, losses, debts, liabilities, damages, actions, causes, charges and expenses, including, but not limited to, court costs and attorneys' fees, arising out of or related to its use of the Portal.

Signature block (page 4): [NAME OF COMPANY]; Signature of Applicant; Date of Application; Printed Name of Applicant; Title.

> I have read, fully understand and agree to be bound by the terms and conditions of this Application. I hereby represent and warrant that I have all requisite power, authority, and authorization to sign this Application. I understand that all information submitted during the testing phase will be used to determine my eligibility to batch file and there is no guarantee that I will be certified to batch file.

## Eligibility / company disclosure (page 5)

**I. Contact Information:** Name; Address; Phone; E-mail.

**II. Status of Company:**
- If a Corporation: state and date of incorporation; President's, Vice President's, Secretary's, Treasurer's names.
- If a Partnership: state and date of organization; type of partnership (general, limited, or association); name of partners.
- If a Joint Venture: state and date of organization; name, address and form of organization of joint venture partners.

**III. Corporate History:**
- A. Number of years in business under present name?
- B. List all Subsidiary or Affiliated Companies.
- C. List any regulatory fine, proceeding, or litigation filed against the Firm in the past five (5) years.
- D. Any principals of the Firm ever been convicted of a first-degree misdemeanor or felony?
- E. Currently under investigation by any public or private, state or federal law enforcement or regulatory body?
- F. List three (3) references regarding the financial stability of the Firm.

Declaration (verbatim):

> I declare under penalty of perjury that the foregoing is true and correct. The undersigned hereby authorize(s) and request(s) any surety company, bank depository, contractor, person, firm or corporation to furnish any pertinent information requested by the Florida Courts E-Filing Authority ("Authority") deemed necessary to verify the statements made in this form or regarding the standing and general reputation of the applicant.

Second signature block (page 5): Company Name; date line ("Dated this __ day of ____, 20__"); Signature; Title.

## Notes for gap analysis

- **No insurance or bond requirement appears anywhere in the application.** The reference to "any surety company, bank depository" is only an authorization to verify financial standing; three financial-stability references are required instead.
- Eligibility is broad: "individuals or entities (including law firms, etc.)"; for-profit entities allowed.
- The application asks for the specific case types/divisions up front; certification is per filing path per division, and (per the Request for Certification form) adding a division later requires a **new application**.
