import type { Metadata } from "next";
import Link from "next/link";
import { COURT_COUNT } from "@/lib/facts";

export const metadata: Metadata = {
  title: "Free CM/ECF Filing Tools | ECFiler",
  description:
    "Free tools for federal court filing: court directory, event code browser, PDF validation, filing fee lookup, Rule 5.2 redaction scan, and certificate of service generator. No account, no credit card.",
};

const TOOLS = [
  {
    href: "/courts",
    title: "Court Directory",
    desc: `Search all ${COURT_COUNT} federal courts — district, bankruptcy, and appellate — with CM/ECF links.`,
    clientSide: true,
  },
  {
    href: "/events",
    title: "Event Code Browser",
    desc: "Browse and search common CM/ECF event codes for district, bankruptcy, and appellate courts.",
    clientSide: true,
  },
  {
    href: "/fees",
    title: "Filing Fee Lookup",
    desc: "Look up federal filing fees from the Judicial Conference fee schedule. IFP waiver noted where available.",
    clientSide: true,
  },
  {
    href: "/redaction",
    title: "Rule 5.2 Redaction Scan",
    desc: "Scan a PDF or pasted text for unredacted SSNs, account numbers, and dates of birth — entirely in your browser. Nothing is uploaded.",
    clientSide: true,
  },
  {
    href: "/validate",
    title: "PDF Validation",
    desc: "Check size, searchable text, encryption, and PDF/A compliance before CM/ECF can reject the file.",
    clientSide: false,
  },
  {
    href: "/certificate",
    title: "Certificate of Service",
    desc: "Generate a properly formatted certificate of service for a federal filing.",
    clientSide: true,
  },
];

export default function ToolsPage() {
  return (
    <div className="min-h-screen bg-[#f5f3ee]">
      <header className="bg-white border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-5 sm:px-6 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[10px] font-bold">E</div>
            <span className="text-[15px] font-semibold tracking-tight text-[#1a1a1a]">ECFiler</span>
          </Link>
          <div className="flex items-center gap-4 text-[13px]">
            <Link href="/federal-courts" className="text-[#525252] hover:text-[#1a1a1a] transition font-medium hidden sm:inline">Courts</Link>
            <Link href="/sign-in" className="text-[#525252] hover:text-[#1a1a1a] transition font-medium">Sign In</Link>
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-5 sm:px-6 py-10">
        <h1 className="text-[26px] sm:text-[32px] font-bold tracking-tight text-[#1a1a1a] mb-2">Free filing tools</h1>
        <p className="text-[15px] text-[#525252] mb-8 max-w-2xl">
          No account, no credit card. Tools marked &ldquo;runs in your browser&rdquo; work
          entirely client-side — your documents never leave your machine.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {TOOLS.map((t) => (
            <Link
              key={t.href}
              href={t.href}
              className="bg-white border border-[#e8e5e0] rounded-2xl p-6 hover:border-[#1e3a5f]/40 hover:shadow-lg hover:shadow-[#1e3a5f]/5 transition-all group"
            >
              <h2 className="text-[16px] font-bold text-[#0f1f35] group-hover:text-[#1e3a5f] transition mb-2">{t.title}</h2>
              <p className="text-[13px] text-[#525252] leading-[1.65] mb-3">{t.desc}</p>
              <span className="text-[10px] font-semibold uppercase tracking-wide text-[#8a8a8a]">
                {t.clientSide ? "Runs in your browser" : "Uses the ECFiler server"}
              </span>
            </Link>
          ))}
        </div>

        <div className="mt-10 text-[13px] text-[#8a8a8a]">
          Need AI document analysis and filing-package staging?{" "}
          <Link href="/sign-up" className="text-[#1e3a5f] font-semibold hover:underline">Create a free account</Link>.
        </div>
      </div>
    </div>
  );
}
