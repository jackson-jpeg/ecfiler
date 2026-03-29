import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy Policy | ECFiler",
  description:
    "How ECFiler collects, stores, and protects your data — including PACER credentials, filing documents, and usage information.",
};

const TOC = [
  { id: "information-we-collect", label: "1. Information We Collect" },
  { id: "pacer-credentials", label: "2. PACER Credential Storage" },
  { id: "filing-documents", label: "3. Filing Document Retention" },
  { id: "sealed-documents", label: "4. Sealed Documents" },
  { id: "authentication", label: "5. Authentication" },
  { id: "analytics", label: "6. Analytics & Performance" },
  { id: "infrastructure", label: "7. Infrastructure & Data Storage" },
  { id: "third-parties", label: "8. Third-Party Data Sharing" },
  { id: "data-rights", label: "9. Your Data Rights" },
  { id: "ccpa", label: "10. California Privacy Rights (CCPA)" },
  { id: "data-deletion", label: "11. Account & Data Deletion" },
  { id: "children", label: "12. Children's Privacy" },
  { id: "changes", label: "13. Changes to This Policy" },
  { id: "contact", label: "14. Contact" },
];

export default function PrivacyPolicy() {
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
            Privacy Policy
          </h1>
          <p className="text-[16px] sm:text-[17px] text-[#525252] leading-relaxed">
            ECFiler (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;) operates
            the ecfiler.com website and the ECFiler platform (the
            &quot;Service&quot;). This Privacy Policy explains how we collect,
            use, store, and protect information when you use the Service. ECFiler
            is designed for licensed attorneys and legal professionals who file
            documents on the federal CM/ECF system. We take the confidentiality
            of legal data seriously.
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
          <section id="information-we-collect">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              1. Information We Collect
            </h2>
            <p>We collect the following categories of information:</p>
            <h3 className="text-[16px] font-semibold text-[#1a1a1a] mt-4 mb-2">
              Account Information
            </h3>
            <ul className="list-disc pl-5 space-y-1">
              <li>
                <strong>Email address and name</strong> &mdash; collected during
                account registration through our authentication provider, Clerk.
              </li>
              <li>
                <strong>Bar admission and attorney identifiers</strong> &mdash;
                if you choose to provide them in your profile.
              </li>
            </ul>
            <h3 className="text-[16px] font-semibold text-[#1a1a1a] mt-4 mb-2">
              PACER / CM/ECF Credentials
            </h3>
            <ul className="list-disc pl-5 space-y-1">
              <li>
                <strong>PACER username and password</strong> &mdash; provided by
                you to enable electronic filing through the CM/ECF system. These
                credentials are encrypted at rest and are never displayed in
                plaintext after initial entry. See Section 2 for details.
              </li>
            </ul>
            <h3 className="text-[16px] font-semibold text-[#1a1a1a] mt-4 mb-2">
              Filing Data
            </h3>
            <ul className="list-disc pl-5 space-y-1">
              <li>
                <strong>PDF documents</strong> you upload for filing, including
                main documents and attachments.
              </li>
              <li>
                <strong>Case information</strong> &mdash; case numbers, court
                identifiers, party names, and event codes associated with your
                filings.
              </li>
              <li>
                <strong>AI-generated metadata</strong> &mdash; docket text
                suggestions, event code predictions, and document analysis
                results produced by our AI systems during the filing workflow.
              </li>
              <li>
                <strong>Filing history</strong> &mdash; records of filings
                submitted through the Service, including timestamps, courts, and
                status.
              </li>
            </ul>
            <h3 className="text-[16px] font-semibold text-[#1a1a1a] mt-4 mb-2">
              Usage Information
            </h3>
            <ul className="list-disc pl-5 space-y-1">
              <li>
                Anonymous page-view and performance metrics collected through
                Vercel Analytics and Speed Insights (see Section 6).
              </li>
              <li>
                Browser type, operating system, and screen resolution for
                compatibility purposes.
              </li>
            </ul>
          </section>

          {/* 2 */}
          <section id="pacer-credentials">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              2. PACER Credential Storage
            </h2>
            <p>
              Your PACER credentials are among the most sensitive data we handle.
              We apply the following safeguards:
            </p>
            <ul className="list-disc pl-5 space-y-1 mt-3">
              <li>
                Credentials are <strong>encrypted at rest using AES-256</strong>{" "}
                encryption. The encryption key is stored separately from the
                encrypted credential data and is not accessible to application
                code outside the filing execution path.
              </li>
              <li>
                Credentials are <strong>decrypted only at the moment of filing</strong>{" "}
                &mdash; specifically, when an authenticated session with CM/ECF
                is required to submit your document. Decryption occurs in an
                isolated process and the plaintext credentials are not logged,
                cached, or written to disk.
              </li>
              <li>
                We do <strong>not</strong> store your PACER credentials in
                browser cookies, local storage, or any client-side mechanism.
              </li>
              <li>
                PACER passwords are never displayed in the ECFiler interface
                after initial entry. You may update or remove your stored
                credentials at any time from your account settings.
              </li>
              <li>
                All communication between ECFiler and the CM/ECF system occurs
                over TLS 1.2 or higher.
              </li>
            </ul>
          </section>

          {/* 3 */}
          <section id="filing-documents">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              3. Filing Document Retention
            </h2>
            <p>
              Documents you upload to ECFiler are stored on a per-user basis and
              are accessible only to your account. Our retention practices are as
              follows:
            </p>
            <ul className="list-disc pl-5 space-y-1 mt-3">
              <li>
                <strong>Active documents</strong> (filed within the last 30
                days) are stored in their original form to support your filing
                history and any resubmission needs.
              </li>
              <li>
                <strong>After 30 days</strong>, documents are compressed and
                moved to archival storage. Compressed documents remain accessible
                through your filing history but may take slightly longer to
                retrieve.
              </li>
              <li>
                You may delete individual documents or your entire filing history
                at any time from your account settings.
              </li>
              <li>
                If you delete your account, all associated documents are
                permanently deleted within 30 days (see Section 11).
              </li>
            </ul>
          </section>

          {/* 4 */}
          <section id="sealed-documents">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              4. Sealed Documents
            </h2>
            <div className="bg-[#fef3c7] border border-[#f59e0b]/30 rounded-xl p-4 mt-3">
              <p className="text-[14px] text-[#92400e] font-medium">
                <strong>ECFiler never retains sealed documents on its servers.</strong>{" "}
                When a filing is identified as sealed (either by the event code
                selected or by you designating it as such), the uploaded PDF is
                held in memory only for the duration of the filing transaction.
                Once the filing is submitted to CM/ECF &mdash; or if the filing
                is canceled &mdash; the document is immediately and
                irreversibly purged. No copy is written to disk, logged, or
                backed up. Your filing history will record that a sealed filing
                was made (court, case number, timestamp) but will not contain the
                document itself or its contents.
              </p>
            </div>
          </section>

          {/* 5 */}
          <section id="authentication">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              5. Authentication
            </h2>
            <p>
              ECFiler uses{" "}
              <a
                href="https://clerk.com/privacy"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[#1e3a5f] underline underline-offset-2 hover:text-[#162a47] transition"
              >
                Clerk
              </a>{" "}
              as our authentication and user-management provider. When you sign
              up or sign in, Clerk processes your email address, name, and
              authentication tokens. Clerk may also collect device and browser
              information for security purposes (e.g., detecting suspicious
              login attempts). ECFiler does not store your password for your
              ECFiler account &mdash; that is managed entirely by Clerk. Please
              review{" "}
              <a
                href="https://clerk.com/privacy"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[#1e3a5f] underline underline-offset-2 hover:text-[#162a47] transition"
              >
                Clerk&apos;s Privacy Policy
              </a>{" "}
              for full details on their data practices.
            </p>
          </section>

          {/* 6 */}
          <section id="analytics">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              6. Analytics & Performance
            </h2>
            <p>
              We use <strong>Vercel Analytics</strong> and{" "}
              <strong>Vercel Speed Insights</strong> to collect anonymous,
              aggregated usage metrics. These tools help us understand page
              performance, load times, and general usage patterns. Specifically:
            </p>
            <ul className="list-disc pl-5 space-y-1 mt-3">
              <li>
                Vercel Analytics collects anonymous page-view data. It does not
                use cookies and does not track individual users across sessions.
              </li>
              <li>
                Vercel Speed Insights measures real-user performance metrics
                (e.g., page load time, time to interactive) to help us optimize
                the application.
              </li>
              <li>
                Neither tool collects personally identifiable information, filing
                content, case data, or PACER credentials.
              </li>
            </ul>
            <p className="mt-3">
              We do not use Google Analytics, Facebook Pixel, or any
              advertising-related tracking on the Service.
            </p>
          </section>

          {/* 7 */}
          <section id="infrastructure">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              7. Infrastructure & Data Storage
            </h2>
            <p>ECFiler&apos;s infrastructure is hosted by two providers:</p>
            <ul className="list-disc pl-5 space-y-1 mt-3">
              <li>
                <strong>Vercel</strong> &mdash; hosts the frontend application
                (the website and user interface you interact with). Vercel
                operates data centers in the United States and complies with SOC
                2 Type II standards.
              </li>
              <li>
                <strong>Railway</strong> &mdash; hosts the backend API server,
                database, and document storage. Railway infrastructure is
                provisioned in U.S.-based data centers.
              </li>
            </ul>
            <p className="mt-3">
              All data transmitted between your browser and ECFiler, and between
              ECFiler and CM/ECF, is encrypted in transit using TLS 1.2 or
              higher. Data at rest is encrypted using AES-256 (see Section 2 for
              credential-specific details).
            </p>
          </section>

          {/* 8 */}
          <section id="third-parties">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              8. Third-Party Data Sharing
            </h2>
            <div className="bg-white border border-[#e8e5e0] rounded-xl p-4 mt-3">
              <p className="font-semibold text-[#1a1a1a] mb-2">
                We do not sell, rent, or trade your personal information or
                filing data to any third party.
              </p>
              <p>
                We share data with third parties only in the following limited
                circumstances:
              </p>
              <ul className="list-disc pl-5 space-y-1 mt-2">
                <li>
                  <strong>CM/ECF</strong> &mdash; your PACER credentials and
                  filing documents are transmitted to the federal court&apos;s
                  CM/ECF system when you submit a filing. This is the core
                  function of the Service.
                </li>
                <li>
                  <strong>Clerk (authentication)</strong> &mdash; email and
                  account data as described in Section 5.
                </li>
                <li>
                  <strong>Vercel and Railway</strong> &mdash; as infrastructure
                  providers, these companies process data on our behalf under
                  data processing agreements.
                </li>
                <li>
                  <strong>Legal compliance</strong> &mdash; we may disclose
                  information if required by law, subpoena, court order, or
                  government request. We will notify you of such requests to the
                  extent legally permitted.
                </li>
              </ul>
            </div>
          </section>

          {/* 9 */}
          <section id="data-rights">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              9. Your Data Rights
            </h2>
            <p>Regardless of your location, you have the right to:</p>
            <ul className="list-disc pl-5 space-y-1 mt-3">
              <li>
                <strong>Access</strong> the personal data we hold about you.
              </li>
              <li>
                <strong>Correct</strong> inaccurate personal data.
              </li>
              <li>
                <strong>Delete</strong> your account and all associated data (see
                Section 11).
              </li>
              <li>
                <strong>Export</strong> your filing history in a
                machine-readable format.
              </li>
              <li>
                <strong>Withdraw consent</strong> for optional data processing
                (e.g., analytics) at any time.
              </li>
            </ul>
            <p className="mt-3">
              To exercise any of these rights, contact us at{" "}
              <a
                href="mailto:privacy@ecfiler.com"
                className="text-[#1e3a5f] underline underline-offset-2 hover:text-[#162a47] transition"
              >
                privacy@ecfiler.com
              </a>
              . We will respond within 30 days.
            </p>
          </section>

          {/* 10 */}
          <section id="ccpa">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              10. California Privacy Rights (CCPA)
            </h2>
            <p>
              If you are a California resident, the California Consumer Privacy
              Act (CCPA) provides you with additional rights regarding your
              personal information:
            </p>
            <ul className="list-disc pl-5 space-y-1 mt-3">
              <li>
                <strong>Right to know</strong> &mdash; you may request a
                detailed disclosure of the categories and specific pieces of
                personal information we have collected about you in the preceding
                12 months.
              </li>
              <li>
                <strong>Right to delete</strong> &mdash; you may request deletion
                of your personal information, subject to certain exceptions
                (e.g., data required for completing a transaction you
                initiated).
              </li>
              <li>
                <strong>Right to non-discrimination</strong> &mdash; we will not
                discriminate against you for exercising your CCPA rights. You
                will not receive different pricing or service levels.
              </li>
              <li>
                <strong>No sale of personal information</strong> &mdash; ECFiler
                does not sell personal information as defined under the CCPA. We
                have not sold personal information in the preceding 12 months.
              </li>
            </ul>
            <p className="mt-3">
              To submit a CCPA request, email{" "}
              <a
                href="mailto:privacy@ecfiler.com"
                className="text-[#1e3a5f] underline underline-offset-2 hover:text-[#162a47] transition"
              >
                privacy@ecfiler.com
              </a>{" "}
              with the subject line &quot;CCPA Request.&quot; We will verify
              your identity before processing your request and respond within 45
              days as required by law.
            </p>
          </section>

          {/* 11 */}
          <section id="data-deletion">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              11. Account & Data Deletion
            </h2>
            <p>
              You may delete your ECFiler account at any time from your account
              settings page. Upon account deletion:
            </p>
            <ul className="list-disc pl-5 space-y-1 mt-3">
              <li>
                Your PACER credentials are immediately and permanently deleted.
              </li>
              <li>
                Your filing history, uploaded documents, and all associated
                metadata are queued for permanent deletion and will be purged
                within 30 calendar days.
              </li>
              <li>
                Your Clerk authentication account is deleted, removing your email
                and login data from our authentication provider.
              </li>
              <li>
                Anonymous, aggregated analytics data (which cannot be linked back
                to you) may be retained.
              </li>
            </ul>
            <p className="mt-3">
              If you need assistance with account deletion, contact{" "}
              <a
                href="mailto:privacy@ecfiler.com"
                className="text-[#1e3a5f] underline underline-offset-2 hover:text-[#162a47] transition"
              >
                privacy@ecfiler.com
              </a>
              .
            </p>
          </section>

          {/* 12 */}
          <section id="children">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              12. Children&apos;s Privacy
            </h2>
            <p>
              ECFiler is intended for use by licensed attorneys and legal
              professionals. We do not knowingly collect personal information
              from individuals under the age of 18. If we learn that we have
              collected information from a minor, we will promptly delete it.
            </p>
          </section>

          {/* 13 */}
          <section id="changes">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              13. Changes to This Policy
            </h2>
            <p>
              We may update this Privacy Policy from time to time to reflect
              changes in our practices, technology, or legal requirements. If we
              make material changes, we will notify you by email (using the
              address associated with your account) or by posting a prominent
              notice within the Service at least 14 days before the changes take
              effect. Your continued use of the Service after the effective date
              constitutes acceptance of the updated policy.
            </p>
          </section>

          {/* 14 */}
          <section id="contact">
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-3">
              14. Contact
            </h2>
            <p>
              If you have questions about this Privacy Policy or our data
              practices, contact us at:
            </p>
            <div className="bg-white border border-[#e8e5e0] rounded-xl p-4 mt-3">
              <p className="font-semibold text-[#1a1a1a]">ECFiler Privacy</p>
              <p>
                Email:{" "}
                <a
                  href="mailto:privacy@ecfiler.com"
                  className="text-[#1e3a5f] underline underline-offset-2 hover:text-[#162a47] transition"
                >
                  privacy@ecfiler.com
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
              href="/terms"
              className="hover:text-[#525252] transition"
            >
              Terms of Service
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
