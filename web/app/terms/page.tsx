import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Terms of Service | ECFiler",
  description:
    "Terms governing use of ECFiler, the AI-powered federal court e-filing platform. Covers attorney responsibilities, liability, and service terms.",
};

const TOC = [
  { id: "acceptance", label: "1. Acceptance of Terms" },
  { id: "nature-of-service", label: "2. Nature of the Service" },
  { id: "attorney-responsibility", label: "3. Attorney Responsibility" },
  { id: "ai-generated-content", label: "4. AI-Generated Content" },
  { id: "ai-verification", label: "5. 3-Pass AI Verification" },
  { id: "pacer-credentials", label: "6. PACER Credentials" },
  { id: "cmecf-availability", label: "7. CM/ECF Availability" },
  { id: "limitation-of-liability", label: "8. Limitation of Liability" },
  { id: "indemnification", label: "9. Indemnification" },
  { id: "service-tiers", label: "10. Service Tiers" },
  { id: "acceptable-use", label: "11. Acceptable Use" },
  { id: "intellectual-property", label: "12. Intellectual Property" },
  { id: "account-termination", label: "13. Account Termination" },
  { id: "dispute-resolution", label: "14. Dispute Resolution" },
  { id: "governing-law", label: "15. Governing Law" },
  { id: "changes", label: "16. Changes to These Terms" },
  { id: "contact", label: "17. Contact" },
];

export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-[#fafaf8]">
      {/* Sticky header */}
      <nav className="bg-white/90 backdrop-blur-md border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-3xl mx-auto px-5 sm:px-8 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[10px] font-bold shadow-sm">
              E
            </div>
            <span className="text-[15px] font-semibold tracking-tight text-[#1a1a1a]">
              ECFiler
            </span>
          </Link>
          <Link
            href="/"
            className="text-[13px] text-[#525252] hover:text-[#1a1a1a] transition font-medium"
          >
            &larr; Back to Home
          </Link>
        </div>
      </nav>

      <main className="max-w-3xl mx-auto px-5 sm:px-8 py-12 sm:py-16">
        {/* Header */}
        <div className="mb-10">
          <p className="text-[12px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-2">
            Last updated: March 2026
          </p>
          <h1 className="text-[28px] sm:text-[36px] font-bold tracking-tight text-[#1a1a1a] mb-3">
            Terms of Service
          </h1>
          <p className="text-[16px] sm:text-[17px] text-[#525252] leading-relaxed">
            These Terms of Service (&quot;Terms&quot;) govern your access to and
            use of the ECFiler platform (&quot;Service&quot;) operated by
            ECFiler (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;). By
            creating an account or using the Service, you agree to be bound by
            these Terms. If you do not agree, do not use the Service.
          </p>
        </div>

        {/* Table of Contents */}
        <div className="bg-white border border-[#e8e5e0] rounded-2xl p-6 mb-12">
          <h2 className="text-[14px] font-semibold text-[#1a1a1a] mb-3">
            Table of Contents
          </h2>
          <ol className="columns-1 sm:columns-2 gap-x-8 text-[13px] leading-relaxed">
            {TOC.map(({ id, label }) => (
              <li key={id} className="mb-1.5 break-inside-avoid">
                <a
                  href={`#${id}`}
                  className="text-[#1e3a5f] hover:text-[#162a47] transition underline-offset-2 hover:underline"
                >
                  {label}
                </a>
              </li>
            ))}
          </ol>
        </div>

        {/* Sections */}
        <div className="prose-ecfiler space-y-10 text-[15px] leading-[1.75] text-[#3a3a3a]">
          {/* 1 */}
          <section id="acceptance">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              1. Acceptance of Terms
            </h2>
            <p>
              By accessing or using ECFiler, you represent that you are at least
              18 years of age and have the legal authority to enter into these
              Terms. If you are using the Service on behalf of a law firm or
              organization, you represent that you have the authority to bind
              that entity to these Terms, and &quot;you&quot; refers to both you
              individually and the entity.
            </p>
          </section>

          {/* 2 */}
          <section id="nature-of-service">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              2. Nature of the Service
            </h2>
            <div className="bg-[#fef3c7] border border-[#f59e0b]/30 rounded-xl p-4 mt-3">
              <p className="text-[14px] text-[#92400e] font-medium">
                <strong>
                  ECFiler is a software tool that assists with electronic court
                  filing. ECFiler is not a law firm, does not practice law, and
                  does not provide legal advice.
                </strong>{" "}
                The Service provides technology to help licensed attorneys
                prepare and submit filings to the federal CM/ECF system. No
                attorney-client relationship is created between you and ECFiler
                by your use of the Service.
              </p>
            </div>
            <p className="mt-3">
              ECFiler automates portions of the CM/ECF filing workflow &mdash;
              including document analysis, event code suggestion, docket text
              generation, and PDF validation &mdash; but all filing decisions
              remain the sole responsibility of the attorney of record. The
              Service is a tool to assist your professional judgment, not a
              replacement for it.
            </p>
          </section>

          {/* 3 */}
          <section id="attorney-responsibility">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              3. Attorney Responsibility
            </h2>
            <p>
              You acknowledge and agree that:
            </p>
            <ul className="list-disc pl-5 space-y-1 mt-3">
              <li>
                <strong>
                  You are solely responsible for all filings made through
                  ECFiler using your PACER credentials.
                </strong>{" "}
                Every filing submitted through the Service carries the same
                legal effect as a filing made directly through the CM/ECF
                system.
              </li>
              <li>
                You are responsible for verifying the accuracy of all
                information before submitting a filing, including but not limited
                to: the correct court, case number, event code, parties, docket
                text, and the contents of all uploaded documents.
              </li>
              <li>
                You are responsible for compliance with all applicable federal
                rules, local court rules, and standing orders, including but not
                limited to: filing deadlines, page limits, formatting
                requirements, Rule 5.2 redaction obligations, and sealed-filing
                procedures.
              </li>
              <li>
                You are responsible for ensuring that you have authority to file
                in the case and court you select.
              </li>
              <li>
                You are responsible for the security of your PACER credentials
                and ECFiler account. You must notify us immediately if you
                believe your account has been compromised.
              </li>
            </ul>
          </section>

          {/* 4 */}
          <section id="ai-generated-content">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              4. AI-Generated Content
            </h2>
            <p>
              ECFiler uses artificial intelligence to assist with the filing
              workflow. AI-generated content includes, but is not limited to:
            </p>
            <ul className="list-disc pl-5 space-y-1 mt-3">
              <li>Suggested event codes based on document analysis</li>
              <li>Draft docket text</li>
              <li>Party identification and role classification</li>
              <li>Document type detection</li>
              <li>Case number and court extraction</li>
              <li>Redaction warnings under Rule 5.2</li>
            </ul>
            <div className="bg-[#fef3c7] border border-[#f59e0b]/30 rounded-xl p-4 mt-4">
              <p className="text-[14px] text-[#92400e] font-medium">
                <strong>
                  All AI-generated content must be reviewed and approved by the
                  filing attorney before submission.
                </strong>{" "}
                AI suggestions are assistive in nature and may contain errors.
                ECFiler does not guarantee the accuracy of any AI-generated
                event code, docket text, or metadata. The attorney of record
                bears full responsibility for the accuracy of every filing.
              </p>
            </div>
          </section>

          {/* 5 */}
          <section id="ai-verification">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              5. 3-Pass AI Verification
            </h2>
            <p>
              ECFiler employs a 3-pass AI verification system that analyzes your
              filing for potential issues before submission. This system checks
              for common errors including incorrect event codes, mismatched case
              numbers, formatting problems, and potential redaction issues. You
              acknowledge that:
            </p>
            <ul className="list-disc pl-5 space-y-1 mt-3">
              <li>
                The 3-pass verification is an <strong>assistive tool</strong>{" "}
                designed to catch common filing errors. It is not infallible and
                does not guarantee that your filing is error-free or will be
                accepted by the court.
              </li>
              <li>
                The verification system is{" "}
                <strong>not a substitute for attorney judgment</strong>.
                Attorneys must independently review all filings regardless of
                verification results.
              </li>
              <li>
                A &quot;passed&quot; verification does not constitute legal
                advice or a representation that the filing complies with all
                applicable rules.
              </li>
              <li>
                The verification system may not detect all potential issues,
                including but not limited to: substantive legal errors,
                court-specific local rule violations, or newly implemented rule
                changes.
              </li>
            </ul>
          </section>

          {/* 6 */}
          <section id="pacer-credentials">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              6. PACER Credentials
            </h2>
            <p>
              To use the filing features of ECFiler, you must provide your PACER
              credentials. By providing your credentials, you represent that:
            </p>
            <ul className="list-disc pl-5 space-y-1 mt-3">
              <li>
                You are the authorized holder of the PACER account or have
                explicit authorization from the account holder to use those
                credentials for electronic filing.
              </li>
              <li>
                You understand that filings submitted using your credentials
                through ECFiler carry the same legal force and effect as filings
                made directly on CM/ECF.
              </li>
              <li>
                You will not use ECFiler to submit filings using another
                attorney&apos;s PACER credentials without their express written
                authorization.
              </li>
            </ul>
            <p className="mt-3">
              For details on how we store and protect your PACER credentials,
              see our{" "}
              <Link
                href="/privacy#pacer-credentials"
                className="text-[#1e3a5f] underline underline-offset-2 hover:text-[#162a47] transition"
              >
                Privacy Policy, Section 2
              </Link>
              .
            </p>
          </section>

          {/* 7 */}
          <section id="cmecf-availability">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              7. CM/ECF Availability
            </h2>
            <p>
              ECFiler interacts with the CM/ECF systems operated by the federal
              judiciary. You acknowledge that:
            </p>
            <ul className="list-disc pl-5 space-y-1 mt-3">
              <li>
                <strong>
                  ECFiler does not control, operate, or guarantee the
                  availability of CM/ECF.
                </strong>{" "}
                CM/ECF systems may be unavailable due to scheduled maintenance,
                unscheduled outages, network issues, or changes to court
                systems.
              </li>
              <li>
                ECFiler does not guarantee that any filing will be accepted by
                the court. Courts may reject filings for any reason, including
                reasons unrelated to the ECFiler platform.
              </li>
              <li>
                You are responsible for verifying that your filing was
                successfully received by the court. A successful submission
                through ECFiler does not constitute confirmation of filing by
                the court until you receive a Notice of Electronic Filing (NEF).
              </li>
              <li>
                If CM/ECF is unavailable, you are responsible for pursuing
                alternative filing methods to meet applicable deadlines.
              </li>
            </ul>
          </section>

          {/* 8 */}
          <section id="limitation-of-liability">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              8. Limitation of Liability
            </h2>
            <div className="bg-white border border-[#e8e5e0] rounded-xl p-4 mt-3 text-[14px]">
              <p className="uppercase font-semibold text-[#1a1a1a] mb-3">
                TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW:
              </p>
              <ul className="list-disc pl-5 space-y-2">
                <li>
                  THE SERVICE IS PROVIDED &quot;AS IS&quot; AND &quot;AS
                  AVAILABLE&quot; WITHOUT WARRANTIES OF ANY KIND, WHETHER EXPRESS
                  OR IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF
                  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
                  NON-INFRINGEMENT.
                </li>
                <li>
                  ECFILER SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL,
                  SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT
                  LIMITED TO: REJECTED FILINGS, INCORRECT EVENT CODES, MISSED
                  DEADLINES, COURT SANCTIONS, MALPRACTICE CLAIMS, LOSS OF DATA,
                  OR LOSS OF REVENUE, ARISING OUT OF OR RELATED TO YOUR USE OF
                  THE SERVICE.
                </li>
                <li>
                  ECFILER&apos;S TOTAL AGGREGATE LIABILITY FOR ALL CLAIMS
                  ARISING OUT OF OR RELATED TO THESE TERMS OR THE SERVICE SHALL
                  NOT EXCEED THE GREATER OF (A) THE AMOUNT YOU PAID TO ECFILER
                  IN THE 12 MONTHS PRECEDING THE CLAIM, OR (B) ONE HUNDRED
                  DOLLARS ($100).
                </li>
                <li>
                  ECFILER IS NOT LIABLE FOR ANY ACTS OR OMISSIONS OF THE FEDERAL
                  JUDICIARY, THE ADMINISTRATIVE OFFICE OF THE U.S. COURTS,
                  PACER, OR ANY INDIVIDUAL COURT&apos;S CM/ECF SYSTEM.
                </li>
              </ul>
            </div>
            <p className="mt-3">
              Some jurisdictions do not allow the exclusion of certain
              warranties or the limitation of liability for certain damages. In
              such jurisdictions, ECFiler&apos;s liability shall be limited to
              the maximum extent permitted by law.
            </p>
          </section>

          {/* 9 */}
          <section id="indemnification">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              9. Indemnification
            </h2>
            <p>
              You agree to indemnify, defend, and hold harmless ECFiler and its
              officers, directors, employees, and agents from and against any
              claims, damages, losses, liabilities, costs, and expenses
              (including reasonable attorneys&apos; fees) arising out of or
              related to: (a) your use of the Service; (b) filings made through
              your account; (c) your violation of these Terms; (d) your
              violation of any applicable law, rule, or court order; or (e) any
              dispute between you and a third party related to filings made
              through the Service.
            </p>
          </section>

          {/* 10 */}
          <section id="service-tiers">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              10. Service Tiers
            </h2>
            <p>
              ECFiler offers multiple service tiers. Features and limitations are
              subject to change; current details are available on our pricing
              page.
            </p>
            <h3 className="text-[16px] font-semibold text-[#1a1a1a] mt-4 mb-2">
              Free Tier
            </h3>
            <ul className="list-disc pl-5 space-y-1">
              <li>Limited number of filings per month</li>
              <li>Basic AI document analysis and event code suggestions</li>
              <li>Standard PDF validation</li>
              <li>Filing history limited to 90 days</li>
              <li>Community support only</li>
            </ul>
            <h3 className="text-[16px] font-semibold text-[#1a1a1a] mt-4 mb-2">
              Pro Tier ($99/attorney/month)
            </h3>
            <ul className="list-disc pl-5 space-y-1">
              <li>Unlimited filings</li>
              <li>Advanced AI analysis with 3-pass verification</li>
              <li>Certificate of service generation</li>
              <li>Rule 5.2 redaction scanning</li>
              <li>Filing fee lookup and calculation</li>
              <li>Full filing history with document archival</li>
              <li>Priority support</li>
            </ul>
            <p className="mt-3">
              We reserve the right to modify pricing, features, and tier
              structure. Material changes to paid tiers will be communicated at
              least 30 days in advance. If you do not agree to changes in a paid
              tier, you may cancel your subscription before the next billing
              cycle.
            </p>
          </section>

          {/* 11 */}
          <section id="acceptable-use">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              11. Acceptable Use
            </h2>
            <p>You agree not to use the Service to:</p>
            <ul className="list-disc pl-5 space-y-1 mt-3">
              <li>
                Submit fraudulent, vexatious, or unauthorized filings.
              </li>
              <li>
                Attempt to gain unauthorized access to any court system, other
                user accounts, or ECFiler infrastructure.
              </li>
              <li>
                Use automated scripts, bots, or other tools to access the
                Service in a manner that exceeds reasonable use or circumvents
                rate limits.
              </li>
              <li>
                Reverse-engineer, decompile, or attempt to extract the source
                code of the Service (except to the extent permitted by
                applicable open-source licenses for components we have released
                under such licenses).
              </li>
              <li>
                Use the Service for any purpose that violates applicable law or
                regulation.
              </li>
              <li>
                Share your account credentials with unauthorized persons.
              </li>
            </ul>
          </section>

          {/* 12 */}
          <section id="intellectual-property">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              12. Intellectual Property
            </h2>
            <p>
              <strong>Your content:</strong> You retain all rights to the
              documents you upload and the filings you create. ECFiler does not
              claim ownership of your filing documents, case data, or legal work
              product. We access your content only as necessary to provide the
              Service.
            </p>
            <p className="mt-3">
              <strong>Our service:</strong> The ECFiler platform, including its
              software, AI models, user interface, and documentation, is
              protected by intellectual property laws. You are granted a limited,
              non-exclusive, non-transferable license to use the Service in
              accordance with these Terms.
            </p>
          </section>

          {/* 13 */}
          <section id="account-termination">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              13. Account Termination
            </h2>
            <p>
              <strong>By you:</strong> You may close your account at any time
              through your account settings. Upon closure, your data will be
              handled as described in our{" "}
              <Link
                href="/privacy#data-deletion"
                className="text-[#1e3a5f] underline underline-offset-2 hover:text-[#162a47] transition"
              >
                Privacy Policy, Section 11
              </Link>
              .
            </p>
            <p className="mt-3">
              <strong>By us:</strong> We reserve the right to suspend or
              terminate your account if we reasonably believe that: (a) you have
              violated these Terms; (b) your use of the Service poses a security
              risk; (c) your account has been compromised; or (d) continued
              provision of the Service to you would be unlawful. We will provide
              notice of termination and the reason for it, except where doing so
              would compromise security or violate law. Upon termination, you
              will have 30 days to export your data before it is permanently
              deleted.
            </p>
          </section>

          {/* 14 */}
          <section id="dispute-resolution">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              14. Dispute Resolution
            </h2>
            <p>
              Before initiating any formal dispute resolution, you agree to
              contact us at{" "}
              <a
                href="mailto:legal@ecfiler.com"
                className="text-[#1e3a5f] underline underline-offset-2 hover:text-[#162a47] transition"
              >
                legal@ecfiler.com
              </a>{" "}
              and attempt to resolve the dispute informally for at least 30
              days. If the dispute cannot be resolved informally, either party
              may pursue resolution through binding arbitration administered by
              the American Arbitration Association (AAA) under its Commercial
              Arbitration Rules. The arbitration shall be conducted by a single
              arbitrator in Wilmington, Delaware. Each party shall bear its own
              costs and attorneys&apos; fees unless the arbitrator determines
              otherwise.
            </p>
            <p className="mt-3">
              <strong>Class action waiver:</strong> You agree to resolve disputes
              on an individual basis. You waive any right to participate in a
              class action, class arbitration, or representative proceeding.
            </p>
          </section>

          {/* 15 */}
          <section id="governing-law">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              15. Governing Law
            </h2>
            <p>
              These Terms shall be governed by and construed in accordance with
              the laws of the State of Delaware, without regard to its conflict
              of law provisions. Any legal action or proceeding not subject to
              arbitration shall be brought exclusively in the state or federal
              courts located in Wilmington, Delaware, and you consent to the
              personal jurisdiction of such courts.
            </p>
          </section>

          {/* 16 */}
          <section id="changes">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              16. Changes to These Terms
            </h2>
            <p>
              We may revise these Terms from time to time. If we make material
              changes, we will notify you by email or by posting a prominent
              notice within the Service at least 14 days before the changes take
              effect. Material changes include, but are not limited to:
              modifications to limitation of liability, dispute resolution, or
              pricing. Your continued use of the Service after the effective
              date constitutes acceptance of the revised Terms. If you do not
              agree, you must stop using the Service and close your account.
            </p>
          </section>

          {/* 17 */}
          <section id="contact">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              17. Contact
            </h2>
            <p>
              If you have questions about these Terms, contact us at:
            </p>
            <div className="bg-white border border-[#e8e5e0] rounded-xl p-4 mt-3">
              <p className="font-semibold text-[#1a1a1a]">ECFiler Legal</p>
              <p>
                Email:{" "}
                <a
                  href="mailto:legal@ecfiler.com"
                  className="text-[#1e3a5f] underline underline-offset-2 hover:text-[#162a47] transition"
                >
                  legal@ecfiler.com
                </a>
              </p>
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="mt-16 pt-8 border-t border-[#e8e5e0] flex flex-col sm:flex-row items-center justify-between gap-4 text-[12px] text-[#8a8a8a]">
          <span>ECFiler is a filing tool, not a legal advisor.</span>
          <div className="flex gap-4">
            <Link
              href="/privacy"
              className="hover:text-[#525252] transition"
            >
              Privacy Policy
            </Link>
            <Link href="/" className="hover:text-[#525252] transition">
              Home
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
