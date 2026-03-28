import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "What is CM/ECF? Guide to Federal Court Electronic Filing | ECFiler",
  description: "CM/ECF (Case Management/Electronic Case Files) is the federal judiciary's electronic filing system. Learn how it works, who uses it, and how to file.",
};

const STEPS = [
  { n: "1", title: "Authenticate", desc: "Log in via PACER Central Sign-On (CSO) with your filing credentials." },
  { n: "2", title: "Select the case", desc: "Enter the case number to navigate to the correct case docket." },
  { n: "3", title: "Choose an event code", desc: "Select from hundreds of codes that categorize your filing (e.g., Motion to Dismiss, Reply Brief)." },
  { n: "4", title: "Upload your PDF", desc: "Attach the main document and any exhibits. PDFs must be searchable and under 100MB." },
  { n: "5", title: "Enter docket text", desc: "Add or edit the text that will appear on the case docket." },
  { n: "6", title: "Submit", desc: "Review and submit. The court generates a Notice of Electronic Filing (NEF)." },
];

const CHALLENGES = [
  { title: "Event code selection", desc: "Courts have hundreds of event codes. Wrong code = rejected or delayed filing.", icon: "M9.568 3H5.25A2.25 2.25 0 003 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 005.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 009.568 3z M6 6h.008v.008H6V6z" },
  { title: "PDF requirements", desc: "Documents must be searchable, not encrypted, no form fields, and some courts require PDF/A.", icon: "M10.125 2.25h-4.5c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" },
  { title: "Rule 5.2 redaction", desc: "SSNs, DOBs, financial accounts, and minor names must be redacted before filing.", icon: "M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" },
  { title: "Court-specific rules", desc: "Each court has local rules affecting filing procedures, page limits, and formatting.", icon: "M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21" },
  { title: "Filing fees", desc: "Complaints ($405), appeals ($605), bankruptcy ($338-$1,738) — must pay before filing processes.", icon: "M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" },
  { title: "Multi-step process", desc: "Each filing requires navigating 6+ pages of forms — time-consuming and error-prone.", icon: "M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z" },
];

export default function WhatIsCMECF() {
  return (
    <div>
      {/* Hero */}
      <div className="mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#f0f4fa] border border-[#bfdbfe] rounded-full text-[11px] font-semibold text-[#1e3a5f] mb-4">Resource Guide</div>
        <h1 className="text-[28px] sm:text-[36px] font-bold tracking-tight text-[#1a1a1a] mb-3">What is CM/ECF?</h1>
        <p className="text-[16px] sm:text-[18px] text-[#525252] leading-relaxed max-w-2xl">
          CM/ECF (Case Management/Electronic Case Files) is the system used by all <strong>207 federal courts</strong> for electronic document filing. It replaced paper filing and is maintained by the Administrative Office of the U.S. Courts.
        </p>
      </div>

      {/* Key facts */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-12">
        {[
          { n: "207", label: "Federal Courts" },
          { n: "1996", label: "First Deployed" },
          { n: "100%", label: "Adoption Rate" },
          { n: "NextGen", label: "Current Version" },
        ].map(({ n, label }) => (
          <div key={label} className="bg-white border border-[#e8e5e0] rounded-xl p-4 text-center">
            <div className="text-[22px] font-bold text-[#1e3a5f]">{n}</div>
            <div className="text-[11px] text-[#8a8a8a] font-medium">{label}</div>
          </div>
        ))}
      </div>

      {/* How it works */}
      <div className="mb-12">
        <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-6">How CM/ECF filing works</h2>
        <div className="bg-white border border-[#e8e5e0] rounded-2xl overflow-hidden">
          {STEPS.map(({ n, title, desc }) => (
            <div key={n} className="flex items-start gap-4 px-5 py-4 border-b border-[#f0eee9] last:border-0">
              <div className="w-8 h-8 bg-[#1e3a5f] text-white rounded-lg flex items-center justify-center text-[12px] font-bold shrink-0 mt-0.5">{n}</div>
              <div>
                <div className="text-[14px] font-semibold text-[#1a1a1a]">{title}</div>
                <div className="text-[13px] text-[#525252] mt-0.5">{desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Who uses it */}
      <div className="mb-12">
        <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-4">Who uses CM/ECF?</h2>
        <div className="bg-white border border-[#e8e5e0] rounded-2xl p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[
              { role: "Attorneys", desc: "Admitted to practice in the specific federal court" },
              { role: "Pro se litigants", desc: "Self-represented parties (in courts that allow it)" },
              { role: "Court clerks", desc: "File court orders and administrative documents" },
              { role: "Judges", desc: "Issue orders and review filings through the system" },
            ].map(({ role, desc }) => (
              <div key={role} className="flex items-start gap-3">
                <div className="w-5 h-5 bg-[#f0fdf4] text-[#15803d] rounded-full flex items-center justify-center text-[9px] font-bold shrink-0 mt-0.5">&#10003;</div>
                <div>
                  <div className="text-[13px] font-semibold text-[#1a1a1a]">{role}</div>
                  <div className="text-[12px] text-[#8a8a8a]">{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Challenges */}
      <div className="mb-12">
        <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-6">Common challenges with CM/ECF</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {CHALLENGES.map(({ title, desc, icon }) => (
            <div key={title} className="bg-white border border-[#e8e5e0] rounded-xl p-5 hover:border-[#d4d0ca] hover:shadow-sm transition">
              <div className="w-9 h-9 bg-[#fef2f2] rounded-lg flex items-center justify-center mb-3">
                <svg className="w-4.5 h-4.5 text-[#b91c1c]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
                </svg>
              </div>
              <h3 className="text-[14px] font-bold text-[#1a1a1a] mb-1">{title}</h3>
              <p className="text-[12px] text-[#525252] leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* NextGen */}
      <div className="mb-12">
        <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-4">NextGen CM/ECF</h2>
        <div className="bg-[#f0f4fa] border border-[#bfdbfe] rounded-2xl p-6">
          <p className="text-[14px] text-[#1e40af] leading-relaxed">
            The federal courts have migrated to <strong>NextGen CM/ECF</strong>, which unifies authentication through PACER Central Sign-On, modernizes the interface, and eliminates the Java requirement. Most courts completed migration by 2025.
          </p>
        </div>
      </div>

      {/* CTA */}
      <div className="bg-gradient-to-r from-[#0f1f35] to-[#1e3a5f] rounded-2xl p-8 text-center">
        <h2 className="text-[20px] font-bold text-white mb-2">ECFiler automates all of this</h2>
        <p className="text-[14px] text-white/60 mb-6 max-w-md mx-auto">Drop a PDF. AI reads the document, extracts everything, and files with one click. 207 federal courts supported.</p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link href="/sign-up" className="px-6 py-2.5 bg-white text-[#1e3a5f] text-[14px] font-semibold rounded-xl hover:bg-[#f0f4fa] transition shadow-lg">Start Filing Free</Link>
          <Link href="/federal-courts" className="px-6 py-2.5 border border-white/20 text-white/70 text-[14px] font-semibold rounded-xl hover:text-white hover:border-white/40 transition">Browse All Courts</Link>
        </div>
      </div>
    </div>
  );
}
