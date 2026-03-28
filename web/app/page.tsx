"use client";

import Link from "next/link";
import { useState } from "react";
import { InteractiveDemo } from "@/components/demo";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#fafaf8]">
      {/* Nav */}
      <nav className="bg-white/90 backdrop-blur-md border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[12px] font-bold shadow-sm">E</div>
            <span className="text-[17px] font-semibold tracking-tight text-[#1a1a1a]">ECFiler</span>
          </Link>
          <div className="flex items-center gap-8 text-[14px]">
            <Link href="/courts" className="text-[#525252] hover:text-[#1a1a1a] transition font-medium">Courts</Link>
            <Link href="/what-is-cmecf" className="text-[#525252] hover:text-[#1a1a1a] transition font-medium">Resources</Link>
            <a href="https://github.com/jackson-jpeg/ecfiler" target="_blank" className="text-[#525252] hover:text-[#1a1a1a] transition font-medium">GitHub</a>
            <div className="w-px h-5 bg-[#e8e5e0]" />
            <Link href="/sign-in" className="text-[#525252] hover:text-[#1a1a1a] transition font-medium">Sign In</Link>
            <Link href="/sign-up" className="px-5 py-2 bg-[#1e3a5f] text-white text-[13px] font-semibold rounded-lg hover:bg-[#162a47] transition shadow-sm">Get Started Free</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-white via-[#fafaf8] to-[#f5f0e8]/30" />
        <div className="relative max-w-6xl mx-auto px-8 pt-24 pb-16">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2.5 px-4 py-1.5 bg-[#f0fdf4] border border-[#bbf7d0] rounded-full text-[12px] font-semibold text-[#15803d] mb-8">
              <span className="w-2 h-2 bg-[#15803d] rounded-full animate-pulse" />
              207 federal courts supported
            </div>
            <h1 className="text-[52px] leading-[1.08] font-bold tracking-[-0.035em] text-[#1a1a1a] mb-6">The intelligent way to<br />file on CM/ECF</h1>
            <p className="text-[20px] leading-[1.6] text-[#525252] mb-10 max-w-xl mx-auto">Drop your filing. AI extracts the case, court, event code, and party. Review what CM/ECF will receive. Confirm with one click.</p>
            <div className="flex gap-4 justify-center">
              <Link href="/sign-up" className="px-8 py-3.5 bg-[#1e3a5f] text-white text-[15px] font-semibold rounded-xl hover:bg-[#162a47] transition shadow-lg shadow-[#1e3a5f]/20">Start Filing &mdash; Free</Link>
              <Link href="/what-is-cmecf" className="px-8 py-3.5 bg-white text-[#1a1a1a] text-[15px] font-semibold rounded-xl border border-[#e8e5e0] hover:border-[#d4d0ca] hover:bg-[#fafaf8] transition">Learn More</Link>
            </div>
          </div>
        </div>
        {/* Interactive product demo */}
        <div className="max-w-5xl mx-auto px-8 pb-24">
          <InteractiveDemo />
        </div>
      </section>

      {/* Trust numbers */}
      <section className="border-y border-[#e8e5e0] bg-white">
        <div className="max-w-5xl mx-auto px-8 py-14 grid grid-cols-2 md:grid-cols-4 gap-10 text-center">
          {[["207", "Federal Courts", "District, Bankruptcy, Appellate"],["94", "Bankruptcy Courts", "Every federal district"],["7", "Safety Gates", "Before every filing"],["<1m", "To Prepare", "AI does the work"]].map(([value, label, sub]) => (
            <div key={label}><div className="text-[36px] font-bold tracking-tight text-[#1e3a5f]">{value}</div><div className="text-[14px] font-semibold text-[#1a1a1a] mt-1">{label}</div><div className="text-[12px] text-[#8a8a8a] mt-0.5">{sub}</div></div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-[#fafaf8]">
        <div className="max-w-6xl mx-auto px-8 py-24">
          <div className="text-center mb-16">
            <h2 className="text-[36px] font-bold tracking-tight text-[#1a1a1a] mb-4">How ECFiler works</h2>
            <p className="text-[17px] text-[#525252] max-w-lg mx-auto">No event code menus. No multi-step forms. Just drop your document.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-16 max-w-4xl mx-auto">
            {[{n:"01",t:"Drop your filing",d:"Upload any federal court document. AI reads the entire document in seconds.",c:"from-[#1e3a5f] to-[#0f2440]"},{n:"02",t:"Review what AI found",d:"Case number, court, event code, filing party, docket text. Every field extracted and verified.",c:"from-[#b8860b] to-[#8b6508]"},{n:"03",t:"Confirm and file",d:"See exactly what CM/ECF will receive. Filing fee displayed. One click to submit.",c:"from-[#15803d] to-[#166534]"}].map(({n,t,d,c}) => (
              <div key={n}><div className={`w-14 h-14 bg-gradient-to-br ${c} text-white rounded-2xl flex items-center justify-center text-[16px] font-bold mb-6 shadow-lg`}>{n}</div><h3 className="text-[18px] font-bold text-[#1a1a1a] mb-3">{t}</h3><p className="text-[14px] text-[#525252] leading-[1.7]">{d}</p></div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="bg-white border-y border-[#e8e5e0]">
        <div className="max-w-6xl mx-auto px-8 py-24">
          <div className="text-center mb-16">
            <h2 className="text-[36px] font-bold tracking-tight text-[#1a1a1a] mb-4">Built for federal practice</h2>
            <p className="text-[17px] text-[#525252] max-w-lg mx-auto">Every feature prevents filing errors and saves attorney time.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 max-w-5xl mx-auto">
            {[
              {t:"207 federal courts",d:"Every district, bankruptcy, and appellate court. BAPs and special courts included.",icon:"M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21"},
              {t:"AI event code matching",d:"Describe your filing in English. ECFiler matches the correct CM/ECF event code from hundreds of options.",icon:"M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z"},
              {t:"Rule 5.2 redaction scan",d:"AI detects unredacted SSNs, DOBs, financial accounts, and minor names before you file.",icon:"M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"},
              {t:"PDF pre-flight checks",d:"Validates size, searchable text, encryption, and PDF/A compliance before CM/ECF can reject your filing.",icon:"M10.125 2.25h-4.5c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"},
              {t:"Sealed & redacted filings",d:"File under seal or submit redacted versions with proper CM/ECF flags. One checkbox.",icon:"M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"},
              {t:"Exhibit management",d:"Drag and drop multiple exhibits. Auto-labeled as Exhibit A, B, C with editable descriptions.",icon:"M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"},
              {t:"Filing fee awareness",d:"Know the exact fee before you file — $405 complaints, $338 Chapter 7, $505 appeals. All built in.",icon:"M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z"},
            ].map(({t,d,icon}) => (
              <div key={t} className="bg-[#fafaf8] border border-[#e8e5e0] rounded-2xl p-7 hover:border-[#d4d0ca] hover:shadow-md transition-all duration-200 group">
                <div className="w-10 h-10 bg-[#f0f4fa] group-hover:bg-[#dbeafe] rounded-xl flex items-center justify-center mb-4 transition">
                  <svg className="w-5 h-5 text-[#1e3a5f]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
                  </svg>
                </div>
                <h3 className="text-[15px] font-bold text-[#1a1a1a] mb-2">{t}</h3>
                <p className="text-[13px] text-[#525252] leading-[1.7]">{d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How filing works today vs ECFiler */}
      <section className="bg-[#fafaf8]">
        <div className="max-w-6xl mx-auto px-8 py-24">
          <div className="text-center mb-16">
            <h2 className="text-[36px] font-bold tracking-tight text-[#1a1a1a] mb-4">Filing shouldn&apos;t take 15 minutes</h2>
            <p className="text-[17px] text-[#525252] max-w-lg mx-auto">CM/ECF was built in 2001. ECFiler brings it to 2026.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {/* Without ECFiler */}
            <div className="bg-white border border-[#e8e5e0] rounded-2xl p-8">
              <div className="text-[11px] font-semibold text-[#b91c1c] uppercase tracking-wide mb-5 flex items-center gap-2">
                <div className="w-5 h-5 bg-[#fef2f2] rounded-full flex items-center justify-center text-[10px]">&#x2717;</div>
                Without ECFiler
              </div>
              <div className="space-y-3">
                {["Navigate 10+ pages of CM/ECF forms", "Scroll through hundreds of event codes", "Manually check Rule 5.2 compliance", "Hope you selected the right filing fee", "No pre-flight PDF validation", "Copy-paste docket text from Word"].map((t) => (
                  <div key={t} className="flex items-start gap-2.5 text-[13px] text-[#8a8a8a]">
                    <span className="text-[#c4c4c4] mt-0.5">&#x2014;</span> {t}
                  </div>
                ))}
              </div>
            </div>
            {/* With ECFiler */}
            <div className="bg-gradient-to-br from-[#0f1f35] to-[#1e3a5f] border border-[#1e3a5f] rounded-2xl p-8">
              <div className="text-[11px] font-semibold text-[#bbf7d0] uppercase tracking-wide mb-5 flex items-center gap-2">
                <div className="w-5 h-5 bg-[#f0fdf4]/20 rounded-full flex items-center justify-center text-[10px]">&#x2713;</div>
                With ECFiler
              </div>
              <div className="space-y-3">
                {["Drop a PDF — AI does everything", "Event code matched in seconds", "Automatic redaction scanning", "Filing fee displayed before submit", "PDF validated, converted to PDF/A", "Docket text auto-generated and editable"].map((t) => (
                  <div key={t} className="flex items-start gap-2.5 text-[13px] text-white/80">
                    <span className="text-[#bbf7d0] mt-0.5">&#x2713;</span> {t}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Waitlist */}
      <Waitlist />

      {/* CTA */}
      <section className="bg-[#0f1f35]">
        <div className="max-w-6xl mx-auto px-8 py-24 text-center">
          <h2 className="text-[36px] font-bold tracking-tight text-white mb-4">Ready to modernize your filing?</h2>
          <p className="text-[17px] text-white/50 mb-10 max-w-md mx-auto">Open source. Free to use. 207 courts. No credit card required.</p>
          <div className="flex gap-4 justify-center">
            <Link href="/sign-up" className="px-8 py-3.5 bg-white text-[#1a1a1a] text-[15px] font-semibold rounded-xl hover:bg-[#f5f5f0] transition shadow-lg">Get Started Free</Link>
            <a href="https://github.com/jackson-jpeg/ecfiler" target="_blank" className="px-8 py-3.5 border border-white/20 text-white/70 text-[15px] font-semibold rounded-xl hover:border-white/40 hover:text-white transition">Star on GitHub</a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-[#e8e5e0]">
        <div className="max-w-6xl mx-auto px-8 py-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-md flex items-center justify-center text-white text-[9px] font-bold">E</div>
            <span className="text-[12px] text-[#8a8a8a]">ECFiler is a filing tool, not a legal advisor.</span>
          </div>
          <div className="flex gap-6 text-[12px] text-[#8a8a8a]">
            <a href="https://github.com/jackson-jpeg/ecfiler" className="hover:text-[#525252] transition">GitHub</a>
            <Link href="/courts" className="hover:text-[#525252] transition">Courts</Link>
            <Link href="/what-is-cmecf" className="hover:text-[#525252] transition">Resources</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

function Waitlist() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");
  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); if (!email) return; setStatus("loading");
    try { await fetch("/api/waitlist", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email }) }); setStatus("done"); } catch { setStatus("error"); }
  };
  return (
    <section className="bg-[#fafaf8] border-y border-[#e8e5e0]">
      <div className="max-w-6xl mx-auto px-8 py-20 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#fdf8ef] border border-[#fde68a] rounded-full text-[12px] font-semibold text-[#b8860b] mb-6">Coming Soon</div>
        <h2 className="text-[28px] font-bold tracking-tight text-[#1a1a1a] mb-3">ECFiler Pro</h2>
        <p className="text-[16px] text-[#525252] mb-8 max-w-md mx-auto">Hosted filing with team management, templates, and priority support. $99/attorney/month.</p>
        {status === "done" ? (
          <div className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#f0fdf4] border border-[#bbf7d0] rounded-xl text-[14px] text-[#15803d] font-medium"><span className="w-2 h-2 bg-[#15803d] rounded-full" />You&apos;re on the list.</div>
        ) : (
          <form onSubmit={submit} className="flex gap-3 max-w-sm mx-auto">
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@lawfirm.com" required className="flex-1 px-4 py-3 border border-[#e8e5e0] rounded-xl text-[14px] outline-none focus:border-[#1e3a5f] focus:ring-2 focus:ring-[#1e3a5f]/10 bg-white" />
            <button type="submit" disabled={status === "loading"} className="px-6 py-3 bg-[#1e3a5f] text-white text-[14px] font-semibold rounded-xl hover:bg-[#162a47] disabled:opacity-50 transition whitespace-nowrap shadow-sm">{status === "loading" ? "..." : "Join Waitlist"}</button>
          </form>
        )}
      </div>
    </section>
  );
}
