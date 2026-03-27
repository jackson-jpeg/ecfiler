import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Nav */}
      <nav className="border-b border-zinc-100">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-zinc-900 rounded-lg flex items-center justify-center text-white text-[11px] font-bold">E</div>
            <span className="text-[15px] font-semibold tracking-tight">ECFiler</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-zinc-500">
            <Link href="/file" className="hover:text-zinc-900 transition">App</Link>
            <Link href="/courts" className="hover:text-zinc-900 transition">Courts</Link>
            <a href="https://github.com/jackson-jpeg/ecfiler" target="_blank" className="hover:text-zinc-900 transition">GitHub</a>
          </div>
        </div>
      </nav>

      {/* Hero — centered */}
      <div className="max-w-5xl mx-auto px-6">
        <div className="pt-24 pb-16 max-w-2xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-zinc-100 rounded-full text-xs font-medium text-zinc-600 mb-6">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
            150 federal courts supported
          </div>
          <h1 className="text-5xl font-bold tracking-tight leading-[1.1] mb-5">
            File on CM/ECF<br />without the forms
          </h1>
          <p className="text-xl text-zinc-500 mb-8 leading-relaxed max-w-lg mx-auto">
            Drop a PDF. AI reads your document and prepares the entire filing. You review and confirm.
          </p>
          <div className="flex gap-3 justify-center">
            <Link href="/file" className="px-7 py-3 bg-zinc-900 text-white text-sm font-semibold rounded-xl hover:bg-zinc-800 transition shadow-sm">
              Start Filing
            </Link>
            <a href="https://github.com/jackson-jpeg/ecfiler" target="_blank" className="px-7 py-3 border border-zinc-200 text-zinc-700 text-sm font-semibold rounded-xl hover:border-zinc-300 hover:bg-zinc-50 transition">
              View Source
            </a>
          </div>
        </div>

        {/* Product screenshot / demo */}
        <div className="rounded-2xl border border-zinc-200 overflow-hidden shadow-2xl shadow-zinc-200/50 mb-24">
          <div className="bg-zinc-100 px-4 py-2.5 flex items-center gap-2 border-b border-zinc-200">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-zinc-300" />
              <div className="w-3 h-3 rounded-full bg-zinc-300" />
              <div className="w-3 h-3 rounded-full bg-zinc-300" />
            </div>
            <div className="flex-1 text-center text-xs text-zinc-400 font-mono">ecfiler.com/file</div>
          </div>
          <div className="bg-zinc-50 p-8 md:p-12">
            <div className="flex gap-6">
              {/* Fake sidebar */}
              <div className="hidden md:block w-44 shrink-0">
                <div className="bg-zinc-900 rounded-xl p-3 text-[11px]">
                  <div className="flex items-center gap-2 mb-4 px-1">
                    <div className="w-5 h-5 bg-blue-600 rounded-md" />
                    <span className="text-white font-semibold text-xs">ECFiler</span>
                  </div>
                  {["New Filing", "Drafts", "History", "Validate", "Certificate", "Courts"].map((item, i) => (
                    <div key={item} className={`px-2 py-1.5 rounded-md mb-0.5 ${i === 0 ? "bg-zinc-700 text-white" : "text-zinc-500"}`}>
                      {item}
                    </div>
                  ))}
                </div>
              </div>
              {/* Fake content */}
              <div className="flex-1 space-y-4">
                <div className="bg-white rounded-xl border border-zinc-200 p-5">
                  <div className="text-xs font-semibold text-zinc-400 uppercase tracking-wide mb-3">AI Analysis</div>
                  <div className="space-y-2.5">
                    {[
                      ["✓", "Validating PDF", "2.3MB, 15 pages, searchable", "text-green-600 bg-green-50"],
                      ["✓", "AI analyzing", "Case 1:24-cv-01234 — SDNY — Jones Corp", "text-green-600 bg-green-50"],
                      ["✓", "Redaction scan", "No issues found", "text-green-600 bg-green-50"],
                      ["✓", "Event matched", "Motion to Dismiss (12)", "text-green-600 bg-green-50"],
                    ].map(([icon, label, detail, cls]) => (
                      <div key={label} className="flex items-start gap-2.5">
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ${cls}`}>{icon}</div>
                        <div>
                          <div className="text-xs font-medium text-zinc-700">{label}</div>
                          <div className="text-[11px] text-zinc-400 font-mono">{detail}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="bg-white rounded-xl border border-zinc-200 p-4 flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold">Motion to Dismiss</div>
                    <div className="text-xs text-zinc-400 font-mono">1:24-cv-01234 · NYSD · Jones Corp (defendant)</div>
                  </div>
                  <div className="px-4 py-1.5 bg-zinc-900 text-white text-xs font-semibold rounded-lg">Confirm & File</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* How it works */}
        <div className="py-16 border-t border-zinc-100">
          <h2 className="text-2xl font-bold tracking-tight text-center mb-12">Three steps to file</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-10 max-w-3xl mx-auto">
            {[
              { n: "1", t: "Drop a PDF", d: "Upload your motion, brief, complaint, or any filing. AI reads the entire document in seconds." },
              { n: "2", t: "Review what AI found", d: "Case number, court, event code, party, docket text — all extracted. Verify each field." },
              { n: "3", t: "Confirm & file", d: "Watch ECFiler navigate CM/ECF step by step. Nothing submits without your explicit confirmation." },
            ].map((s) => (
              <div key={s.n} className="text-center">
                <div className="w-10 h-10 bg-zinc-900 text-white rounded-full flex items-center justify-center text-sm font-bold mx-auto mb-4">{s.n}</div>
                <div className="text-base font-semibold mb-2">{s.t}</div>
                <div className="text-sm text-zinc-500 leading-relaxed">{s.d}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Features */}
        <div className="py-16 border-t border-zinc-100">
          <h2 className="text-2xl font-bold tracking-tight text-center mb-12">Built for federal court filing</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto">
            {[
              { t: "150 federal courts", d: "Every district, bankruptcy, and appellate court in one tool." },
              { t: "AI event code matching", d: "Describe your filing in English. ECFiler finds the right code." },
              { t: "Redaction scanning", d: "Catches unredacted SSNs, DOBs, and account numbers (Rule 5.2)." },
              { t: "PDF validation", d: "Checks size, text, encryption before CM/ECF can reject it." },
              { t: "Certificate of service", d: "Generate text or PDF. Handles CM/ECF, email, and mail service." },
              { t: "7 safety gates", d: "PDF, redaction, event match, completeness, review, confirm, receipt." },
            ].map((f) => (
              <div key={f.t} className="border border-zinc-200 rounded-2xl p-5 hover:border-zinc-300 transition">
                <div className="text-sm font-semibold mb-1.5">{f.t}</div>
                <div className="text-sm text-zinc-500 leading-relaxed">{f.d}</div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="py-20 text-center border-t border-zinc-100">
          <h2 className="text-2xl font-bold tracking-tight mb-3">Ready to file?</h2>
          <p className="text-zinc-500 mb-6">Open source. Free to self-host. No credit card.</p>
          <Link href="/file" className="px-7 py-3 bg-zinc-900 text-white text-sm font-semibold rounded-xl hover:bg-zinc-800 transition shadow-sm">
            Open ECFiler
          </Link>
        </div>

        {/* Footer */}
        <div className="py-6 border-t border-zinc-100 text-center text-xs text-zinc-400 mb-4">
          ECFiler is a filing tool, not a legal advisor. The attorney is responsible for all filings.
          <span className="mx-2">&middot;</span>
          <a href="https://github.com/jackson-jpeg/ecfiler" className="hover:text-zinc-600 transition">GitHub</a>
          <span className="mx-2">&middot;</span>
          <a href="/api/docs" className="hover:text-zinc-600 transition">API</a>
        </div>
      </div>
    </div>
  );
}
