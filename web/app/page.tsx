"use client";

import Link from "next/link";
import { useState } from "react";

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Nav */}
      <nav className="bg-white/80 backdrop-blur-sm border-b border-zinc-100 sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-zinc-900 rounded-lg flex items-center justify-center text-white text-[11px] font-bold">E</div>
            <span className="text-[15px] font-semibold tracking-tight">ECFiler</span>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <Link href="/courts" className="text-zinc-500 hover:text-zinc-900 transition">Courts</Link>
            <a href="https://github.com/jackson-jpeg/ecfiler" target="_blank" className="text-zinc-500 hover:text-zinc-900 transition">GitHub</a>
            <Link href="/sign-in" className="text-zinc-500 hover:text-zinc-900 transition font-medium">Sign In</Link>
            <Link href="/sign-up" className="px-4 py-1.5 bg-zinc-900 text-white text-sm font-medium rounded-lg hover:bg-zinc-800 transition">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <div className="bg-gradient-to-b from-zinc-50 to-white">
        <div className="max-w-5xl mx-auto px-6 pt-20 pb-8">
          <div className="max-w-2xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-50 border border-green-200 rounded-full text-xs font-medium text-green-700 mb-6">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
              207 federal courts &middot; Open source
            </div>
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight leading-[1.08] mb-5">
              File on CM/ECF<br />without the forms
            </h1>
            <p className="text-xl text-zinc-500 mb-8 leading-relaxed max-w-lg mx-auto">
              Drop a PDF. AI reads your document and prepares the entire filing. You review and confirm.
            </p>
            <div className="flex gap-3 justify-center mb-4">
              <Link href="/file" className="px-7 py-3 bg-zinc-900 text-white text-sm font-semibold rounded-xl hover:bg-zinc-800 transition shadow-lg shadow-zinc-900/20">
                Start Filing &rarr;
              </Link>
              <a href="https://github.com/jackson-jpeg/ecfiler" target="_blank" className="px-7 py-3 bg-white border border-zinc-200 text-zinc-700 text-sm font-semibold rounded-xl hover:border-zinc-300 hover:bg-zinc-50 transition">
                View Source
              </a>
            </div>
          </div>
        </div>

        {/* Product mockup */}
        <div className="max-w-4xl mx-auto px-6 pb-20">
          <div className="rounded-2xl border border-zinc-200 overflow-hidden shadow-2xl shadow-zinc-300/30 bg-white">
            {/* Browser chrome */}
            <div className="bg-zinc-100 px-4 py-2.5 flex items-center gap-2 border-b border-zinc-200">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-400/60" />
                <div className="w-3 h-3 rounded-full bg-amber-400/60" />
                <div className="w-3 h-3 rounded-full bg-green-400/60" />
              </div>
              <div className="flex-1 mx-8">
                <div className="bg-white rounded-md px-3 py-1 text-xs text-zinc-400 font-mono text-center border border-zinc-200">
                  ecfiler.com/file
                </div>
              </div>
            </div>
            {/* App content */}
            <div className="bg-zinc-50 p-6 md:p-8">
              <div className="flex gap-5">
                {/* Mini sidebar */}
                <div className="hidden md:block w-40 shrink-0">
                  <div className="bg-zinc-900 rounded-xl p-3">
                    <div className="flex items-center gap-2 mb-3 px-1">
                      <div className="w-5 h-5 bg-blue-600 rounded-md" />
                      <span className="text-white font-semibold text-[11px]">ECFiler</span>
                    </div>
                    <div className="text-[9px] text-zinc-500 uppercase tracking-wider px-2 mb-1">Filing</div>
                    {["New Filing", "Drafts", "History"].map((item, i) => (
                      <div key={item} className={`text-[11px] px-2 py-1.5 rounded-md mb-0.5 ${i === 0 ? "bg-zinc-700 text-white font-medium" : "text-zinc-500"}`}>{item}</div>
                    ))}
                    <div className="text-[9px] text-zinc-500 uppercase tracking-wider px-2 mb-1 mt-3">Tools</div>
                    {["Validate PDF", "Certificate", "Courts"].map((item) => (
                      <div key={item} className="text-[11px] px-2 py-1.5 text-zinc-500">{item}</div>
                    ))}
                  </div>
                </div>
                {/* Main content — showing review state */}
                <div className="flex-1 space-y-3">
                  {/* Stat cards */}
                  <div className="grid grid-cols-3 gap-2">
                    <div className="bg-green-50 border border-green-200 rounded-xl px-3 py-2">
                      <div className="text-[9px] font-semibold text-zinc-400 uppercase">Extraction</div>
                      <div className="text-base font-bold text-green-700">100%</div>
                    </div>
                    <div className="bg-green-50 border border-green-200 rounded-xl px-3 py-2">
                      <div className="text-[9px] font-semibold text-zinc-400 uppercase">PDF</div>
                      <div className="text-base font-bold text-green-700">2.3MB</div>
                    </div>
                    <div className="bg-green-50 border border-green-200 rounded-xl px-3 py-2">
                      <div className="text-[9px] font-semibold text-zinc-400 uppercase">Redaction</div>
                      <div className="text-base font-bold text-green-700">Clean</div>
                    </div>
                  </div>
                  {/* Filing data */}
                  <div className="bg-white rounded-xl border border-zinc-200 text-[12px]">
                    {[
                      ["Document", "Motion to Dismiss for Failure to State a Claim"],
                      ["Case", "1:24-cv-01234-ABC"],
                      ["Court", "NYSD"],
                      ["Docket Text", "Motion to Dismiss"],
                      ["Filing Party", "Jones Corporation (defendant)"],
                    ].map(([k, v]) => (
                      <div key={k} className="flex px-4 py-2 border-b border-zinc-100 last:border-0">
                        <div className="w-24 text-[10px] font-semibold text-zinc-400 uppercase shrink-0">{k}</div>
                        <div className="font-medium">{v}</div>
                      </div>
                    ))}
                  </div>
                  {/* Confirm */}
                  <div className="flex items-center gap-3">
                    <div className="px-5 py-2 bg-zinc-900 text-white text-[11px] font-semibold rounded-lg">Confirm & File</div>
                    <div className="text-[11px] text-zinc-400">Cancel</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Numbers */}
      <div className="border-y border-zinc-100 bg-white">
        <div className="max-w-4xl mx-auto px-6 py-10 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[
            ["207", "Federal Courts"],
            ["94", "Bankruptcy Courts"],
            ["7", "Safety Gates"],
            ["<1min", "To File"],
          ].map(([n, label]) => (
            <div key={label}>
              <div className="text-3xl font-bold tracking-tight text-zinc-900">{n}</div>
              <div className="text-sm text-zinc-500 mt-1">{label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* How it works */}
      <div className="bg-white">
        <div className="max-w-5xl mx-auto px-6 py-20">
          <h2 className="text-3xl font-bold tracking-tight text-center mb-4">Three steps to file</h2>
          <p className="text-zinc-500 text-center mb-14 max-w-md mx-auto">No forms. No dropdowns. No scrolling through event codes. Just drop a PDF.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-3xl mx-auto">
            {[
              { n: "1", t: "Drop a PDF", d: "Upload your motion, brief, complaint, or any filing. AI reads the entire document in seconds.", color: "bg-blue-600" },
              { n: "2", t: "Review what AI found", d: "Case number, court, event code, party, docket text. Everything extracted and verified.", color: "bg-violet-600" },
              { n: "3", t: "Confirm & file", d: "Watch ECFiler navigate CM/ECF step by step. Nothing submits without your explicit confirmation.", color: "bg-green-600" },
            ].map((s) => (
              <div key={s.n} className="text-center">
                <div className={`w-12 h-12 ${s.color} text-white rounded-2xl flex items-center justify-center text-lg font-bold mx-auto mb-5`}>{s.n}</div>
                <div className="text-lg font-semibold mb-2">{s.t}</div>
                <div className="text-sm text-zinc-500 leading-relaxed">{s.d}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="bg-zinc-50 border-y border-zinc-100">
        <div className="max-w-5xl mx-auto px-6 py-20">
          <h2 className="text-3xl font-bold tracking-tight text-center mb-4">Built for federal court filing</h2>
          <p className="text-zinc-500 text-center mb-14 max-w-md mx-auto">Every feature exists to prevent filing errors and save attorney time.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto">
            {[
              { t: "207 federal courts", d: "Every district, bankruptcy, and appellate court. BAPs and special courts included." },
              { t: "AI event code matching", d: "Describe your filing in English. ECFiler matches it to the right CM/ECF event code." },
              { t: "Redaction scanning", d: "Catches unredacted SSNs, DOBs, and account numbers before you file (Rule 5.2)." },
              { t: "PDF pre-flight", d: "Checks size, searchable text, encryption, form fields. Catches problems before CM/ECF does." },
              { t: "Certificate of service", d: "Generate properly formatted certificates. Download as PDF. Handles all service methods." },
              { t: "7 safety gates", d: "PDF validation, redaction scan, event match, completeness check, review, confirm, receipt." },
            ].map((f) => (
              <div key={f.t} className="bg-white border border-zinc-200 rounded-2xl p-6 hover:border-zinc-300 hover:shadow-sm transition">
                <div className="text-sm font-bold mb-2">{f.t}</div>
                <div className="text-sm text-zinc-500 leading-relaxed">{f.d}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Waitlist */}
      <Waitlist />

      {/* CTA */}
      <div className="bg-zinc-900">
        <div className="max-w-5xl mx-auto px-6 py-20 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-white mb-3">Ready to file?</h2>
          <p className="text-zinc-400 mb-8 max-w-md mx-auto">Open source. Free to self-host. 207 courts. No credit card required.</p>
          <div className="flex gap-3 justify-center">
            <Link href="/file" className="px-7 py-3 bg-white text-zinc-900 text-sm font-semibold rounded-xl hover:bg-zinc-100 transition">
              Open ECFiler &rarr;
            </Link>
            <a href="https://github.com/jackson-jpeg/ecfiler" target="_blank" className="px-7 py-3 border border-zinc-700 text-zinc-300 text-sm font-semibold rounded-xl hover:border-zinc-500 hover:text-white transition">
              Star on GitHub
            </a>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white border-t border-zinc-100">
        <div className="max-w-5xl mx-auto px-6 py-6 flex items-center justify-between text-xs text-zinc-400">
          <div>ECFiler is a filing tool, not a legal advisor.</div>
          <div className="flex gap-4">
            <a href="https://github.com/jackson-jpeg/ecfiler" className="hover:text-zinc-600 transition">GitHub</a>
            <Link href="/courts" className="hover:text-zinc-600 transition">Courts</Link>
          </div>
        </div>
      </div>
    </div>
  );
}

function Waitlist() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setStatus("loading");
    try {
      await fetch("/api/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      setStatus("done");
    } catch {
      setStatus("error");
    }
  };

  return (
    <div className="bg-white border-y border-zinc-100">
      <div className="max-w-5xl mx-auto px-6 py-16 text-center">
        <h2 className="text-2xl font-bold tracking-tight mb-2">Get early access to ECFiler Pro</h2>
        <p className="text-zinc-500 mb-6 max-w-md mx-auto">
          Hosted version with team management, filing templates, and priority support. $99/attorney/month.
        </p>
        {status === "done" ? (
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-50 border border-green-200 rounded-xl text-sm text-green-700 font-medium">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
            You&apos;re on the list. We&apos;ll be in touch.
          </div>
        ) : (
          <form onSubmit={submit} className="flex gap-2 max-w-sm mx-auto">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@lawfirm.com"
              required
              className="flex-1 px-4 py-2.5 border border-zinc-200 rounded-xl text-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-50"
            />
            <button
              type="submit"
              disabled={status === "loading"}
              className="px-5 py-2.5 bg-zinc-900 text-white text-sm font-semibold rounded-xl hover:bg-zinc-800 disabled:opacity-50 transition whitespace-nowrap"
            >
              {status === "loading" ? "..." : "Join Waitlist"}
            </button>
          </form>
        )}
        {status === "error" && <p className="text-xs text-red-500 mt-2">Something went wrong. Try again.</p>}
      </div>
    </div>
  );
}
