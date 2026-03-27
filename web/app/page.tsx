import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="flex-1 overflow-y-auto">
      <div className="px-8 py-20 max-w-xl">
        <h1 className="text-4xl font-bold tracking-tight leading-tight mb-4">
          File on CM/ECF<br />without the forms.
        </h1>
        <p className="text-lg text-zinc-500 mb-8 leading-relaxed">
          Drop a PDF. AI reads your document, extracts the case, court, party, and event type.
          You review and confirm. 150 federal courts.
        </p>
        <div className="flex gap-3">
          <Link href="/file" className="px-6 py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition">
            Start Filing
          </Link>
          <a href="https://github.com/jackson-jpeg/ecfiler" target="_blank" className="px-6 py-2.5 border border-zinc-200 text-zinc-600 text-sm font-semibold rounded-lg hover:border-zinc-300 transition">
            View Source
          </a>
        </div>
      </div>

      <div className="px-8 py-12 border-t border-zinc-100">
        <h2 className="text-lg font-bold tracking-tight mb-6">How it works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl">
          {[
            { n: "1", t: "Drop a PDF", d: "Upload your motion, brief, complaint, or any filing. AI reads the entire document." },
            { n: "2", t: "Review extraction", d: "See the case number, court, event code, party, and docket text. Verify each field." },
            { n: "3", t: "Confirm & file", d: "Watch ECFiler navigate CM/ECF in real-time. Nothing submits without your confirmation." },
          ].map((s) => (
            <div key={s.n}>
              <div className="w-7 h-7 bg-zinc-900 text-white rounded-full flex items-center justify-center text-xs font-bold mb-3">{s.n}</div>
              <div className="text-sm font-semibold mb-1">{s.t}</div>
              <div className="text-sm text-zinc-500 leading-relaxed">{s.d}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="px-8 py-12 border-t border-zinc-100">
        <h2 className="text-lg font-bold tracking-tight mb-6">Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-3xl">
          {[
            { t: "150 federal courts", d: "District, bankruptcy, and appellate. One tool for every venue." },
            { t: "AI event code matching", d: "Describe your filing. ECFiler finds the right CM/ECF event code." },
            { t: "Redaction scanning", d: "Checks for unredacted SSNs, DOBs, and financial accounts (Rule 5.2)." },
            { t: "PDF validation", d: "Size, searchable text, encryption, form fields." },
            { t: "Certificate of service", d: "Generate and download as PDF." },
            { t: "7 safety gates", d: "PDF check, redaction, event match, completeness, review, confirm, receipt." },
          ].map((f) => (
            <div key={f.t} className="border border-zinc-200 rounded-xl p-4 bg-white">
              <div className="text-sm font-semibold mb-1">{f.t}</div>
              <div className="text-sm text-zinc-500">{f.d}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="px-8 py-8 border-t border-zinc-100 text-xs text-zinc-400">
        ECFiler is a filing tool, not a legal advisor.
        <span className="mx-2">&middot;</span>
        <a href="https://github.com/jackson-jpeg/ecfiler" className="hover:text-zinc-600">GitHub</a>
      </div>
    </div>
  );
}
