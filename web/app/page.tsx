"use client";

import Link from "next/link";
import { useState, useEffect, useRef } from "react";
import { InteractiveDemo } from "@/components/demo";


export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pageRef = useRef<HTMLDivElement>(null);

  // Scroll-reveal all sections
  useEffect(() => {
    const el = pageRef.current;
    if (!el) return;
    const sections = el.querySelectorAll("section");
    const observer = new IntersectionObserver(
      (entries) => entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("reveal"); observer.unobserve(e.target); } }),
      { threshold: 0.1 }
    );
    sections.forEach((s) => observer.observe(s));
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={pageRef} className="min-h-screen bg-[#fafaf8]">
      {/* Nav */}
      <nav className="bg-white/90 backdrop-blur-md border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-5 sm:px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[12px] font-bold shadow-sm">E</div>
            <span className="text-[17px] font-semibold tracking-tight text-[#1a1a1a]">ECFiler</span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-[14px]">
            <Link href="/federal-courts" className="text-[#525252] hover:text-[#1a1a1a] transition font-medium">Courts</Link>
            <Link href="/what-is-cmecf" className="text-[#525252] hover:text-[#1a1a1a] transition font-medium">Resources</Link>
            <a href="https://github.com/jackson-jpeg/ecfiler" target="_blank" className="text-[#525252] hover:text-[#1a1a1a] transition font-medium">GitHub</a>
            <div className="w-px h-5 bg-[#e8e5e0]" />
            <Link href="/sign-in" className="text-[#525252] hover:text-[#1a1a1a] transition font-medium">Sign In</Link>
            <Link href="/sign-up" className="px-5 py-2 bg-[#1e3a5f] text-white text-[13px] font-semibold rounded-lg hover:bg-[#162a47] transition shadow-sm">Get Started Free</Link>
          </div>
          <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="md:hidden p-2 text-[#525252] hover:text-[#1a1a1a] transition" aria-label="Toggle menu">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              )}
            </svg>
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-[#e8e5e0] bg-white px-5 py-4 flex flex-col gap-4 text-[14px]">
            <Link href="/federal-courts" onClick={() => setMobileMenuOpen(false)} className="text-[#525252] hover:text-[#1a1a1a] transition font-medium">Courts</Link>
            <Link href="/what-is-cmecf" onClick={() => setMobileMenuOpen(false)} className="text-[#525252] hover:text-[#1a1a1a] transition font-medium">Resources</Link>
            <a href="https://github.com/jackson-jpeg/ecfiler" target="_blank" className="text-[#525252] hover:text-[#1a1a1a] transition font-medium">GitHub</a>
            <hr className="border-[#e8e5e0]" />
            <Link href="/sign-in" onClick={() => setMobileMenuOpen(false)} className="text-[#525252] hover:text-[#1a1a1a] transition font-medium">Sign In</Link>
            <Link href="/sign-up" onClick={() => setMobileMenuOpen(false)} className="px-5 py-2 bg-[#1e3a5f] text-white text-[13px] font-semibold rounded-lg hover:bg-[#162a47] transition shadow-sm text-center">Get Started Free</Link>
          </div>
        )}
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden bg-white">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e3a5f08_1px,transparent_1px),linear-gradient(to_bottom,#1e3a5f08_1px,transparent_1px)] bg-[size:64px_64px]" />
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-[radial-gradient(ellipse,#1e3a5f0a,transparent_70%)]" />
        </div>
        <div className="relative max-w-6xl mx-auto px-5 sm:px-8 pt-20 sm:pt-28 pb-16 sm:pb-20">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-3 px-4 py-2 bg-[#0f1f35] rounded-full text-[12px] font-semibold text-white mb-8 shadow-lg shadow-[#1e3a5f]/20">
              <span className="relative flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" /><span className="relative inline-flex rounded-full h-2 w-2 bg-green-400" /></span>
              207 federal courts supported
            </div>
            <h1 className="text-[36px] sm:text-[48px] md:text-[60px] leading-[1.05] font-bold tracking-[-0.04em] text-[#0f1f35] mb-6">
              Stop wrestling with<br />
              <span className="gradient-text-animated">CM/ECF forms</span>
            </h1>
            <p className="text-[17px] sm:text-[19px] md:text-[21px] leading-[1.6] text-[#525252] mb-10 max-w-xl mx-auto">Drop a PDF. AI reads the document, extracts case number, court, event code, and filing party. You review and file with one click.</p>
            <div className="flex flex-col sm:flex-row w-full sm:w-auto gap-4 justify-center">
              <Link href="/sign-up" className="w-full sm:w-auto px-10 py-4 bg-[#1e3a5f] text-white text-[16px] font-bold rounded-xl hover:bg-[#162a47] transition-all shadow-xl shadow-[#1e3a5f]/25 hover:shadow-2xl hover:shadow-[#1e3a5f]/30 hover:-translate-y-0.5 text-center">Start Filing Free</Link>
              <Link href="/what-is-cmecf" className="w-full sm:w-auto px-10 py-4 bg-white text-[#1a1a1a] text-[16px] font-semibold rounded-xl border-2 border-[#e8e5e0] hover:border-[#1e3a5f] hover:text-[#1e3a5f] transition-all text-center">Learn More</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Numbers bar — bold, dark */}
      <section className="bg-[#0f1f35] border-y border-[#1e3a5f]">
        <div className="max-w-5xl mx-auto px-5 sm:px-8 py-10 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {[
            ["207", "Federal Courts", "District, Bankruptcy, Appellate"],
            ["3-Pass", "AI Verification", "Before every filing"],
            ["<1min", "To Prepare", "AI does the heavy lifting"],
            ["$0", "To Start", "Free tools, no credit card"],
          ].map(([value, label, sub]) => (
            <div key={label}>
              <div className="text-[32px] sm:text-[40px] font-bold tracking-tight text-white">{value}</div>
              <div className="text-[13px] font-semibold text-white/70 mt-1">{label}</div>
              <div className="text-[11px] text-white/30 mt-0.5">{sub}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Interactive product demo */}
      <section className="relative bg-[#0f1f35] py-16 sm:py-20">
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: "radial-gradient(circle at 2px 2px, white 1px, transparent 0)", backgroundSize: "32px 32px" }} />
        <div className="relative max-w-5xl mx-auto px-5 sm:px-8">
          <div className="text-center mb-10">
            <div className="text-[11px] font-bold text-white/40 uppercase tracking-[0.2em] mb-3">Live Demo</div>
            <h2 className="text-[24px] sm:text-[30px] font-bold text-white tracking-tight">See it in action</h2>
            <p className="text-[14px] sm:text-[16px] text-white/50 mt-2 max-w-lg mx-auto">Watch AI analyze a motion, verify it with 3 safety passes, and file it on CM/ECF.</p>
          </div>
          <InteractiveDemo />
        </div>
      </section>

      {/* How it works — 3 bold steps */}
      <section className="bg-white">
        <div className="max-w-6xl mx-auto px-5 sm:px-8 py-20 sm:py-28">
          <div className="text-center mb-16">
            <div className="text-[11px] font-bold text-[#1e3a5f] uppercase tracking-[0.2em] mb-3">How It Works</div>
            <h2 className="text-[28px] sm:text-[36px] md:text-[42px] font-bold tracking-tight text-[#0f1f35] mb-4">Three steps. Under a minute.</h2>
            <p className="text-[17px] text-[#525252] max-w-lg mx-auto">No event code menus. No multi-step forms. Just drop your document.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-0 max-w-5xl mx-auto">
            {[
              { n: "01", t: "Drop your filing", d: "Upload any federal court document — motion, brief, complaint, notice. AI reads the entire document in seconds.", color: "from-[#1e3a5f] to-[#0f2440]", accent: "#1e3a5f" },
              { n: "02", t: "AI extracts everything", d: "Case number, court, event code, filing party, docket text. Every field extracted, cross-referenced, and verified with 3 safety passes.", color: "from-[#b8860b] to-[#8b6508]", accent: "#b8860b" },
              { n: "03", t: "Review and file", d: "See exactly what CM/ECF will receive. Attest, click once, and watch the filing happen live in your browser.", color: "from-[#15803d] to-[#166534]", accent: "#15803d" },
            ].map(({ n, t, d, color, accent }, i) => (
              <div key={n} className="relative p-8 md:p-10">
                {i < 2 && <div className="hidden md:block absolute right-0 top-1/2 -translate-y-1/2 w-px h-16 bg-[#e8e5e0]" />}
                <div className={`w-16 h-16 bg-gradient-to-br ${color} text-white rounded-2xl flex items-center justify-center text-[20px] font-bold mb-6 shadow-lg`} style={{ boxShadow: `0 8px 24px ${accent}30` }}>{n}</div>
                <h3 className="text-[20px] font-bold text-[#0f1f35] mb-3">{t}</h3>
                <p className="text-[15px] text-[#525252] leading-[1.7]">{d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Before / After comparison — high contrast */}
      <section className="bg-[#fafaf8] border-y border-[#e8e5e0]">
        <div className="max-w-6xl mx-auto px-5 sm:px-8 py-20 sm:py-28">
          <div className="text-center mb-16">
            <div className="text-[11px] font-bold text-[#b91c1c] uppercase tracking-[0.2em] mb-3">The Problem</div>
            <h2 className="text-[28px] sm:text-[36px] md:text-[42px] font-bold tracking-tight text-[#0f1f35] mb-4">CM/ECF was built in 2001</h2>
            <p className="text-[17px] text-[#525252] max-w-lg mx-auto">ECFiler brings it to {new Date().getFullYear()}.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {/* Without */}
            <div className="bg-white border-2 border-[#fecaca] rounded-2xl p-8 relative">
              <div className="absolute -top-3 left-6 text-[10px] font-bold text-[#b91c1c] uppercase tracking-wider bg-[#fef2f2] border border-[#fecaca] px-3 py-1 rounded-full">Without ECFiler</div>
              <div className="space-y-4 mt-2">
                {[
                  "Navigate 10+ pages of CM/ECF forms",
                  "Scroll through hundreds of event codes",
                  "Manually check Rule 5.2 compliance",
                  "Hope you selected the right filing fee",
                  "No pre-flight PDF validation",
                  "Copy-paste docket text from Word",
                ].map((t) => (
                  <div key={t} className="flex items-start gap-3 text-[14px] text-[#666]">
                    <div className="w-5 h-5 rounded-full bg-[#fef2f2] flex items-center justify-center shrink-0 mt-0.5">
                      <span className="text-[#b91c1c] text-[10px] font-bold">&#x2717;</span>
                    </div>
                    {t}
                  </div>
                ))}
              </div>
              <div className="mt-6 pt-5 border-t border-[#fecaca]/50 text-center">
                <span className="text-[28px] font-bold text-[#b91c1c]">~15 min</span>
                <span className="text-[13px] text-[#999] block mt-1">per filing</span>
              </div>
            </div>
            {/* With */}
            <div className="bg-gradient-to-br from-[#0f1f35] to-[#1e3a5f] rounded-2xl p-8 relative shadow-xl shadow-[#1e3a5f]/20">
              <div className="absolute -top-3 left-6 text-[10px] font-bold text-[#15803d] uppercase tracking-wider bg-[#f0fdf4] border border-[#bbf7d0] px-3 py-1 rounded-full">With ECFiler</div>
              <div className="space-y-4 mt-2">
                {[
                  "Drop a PDF — AI does everything",
                  "Event code matched in seconds",
                  "Automatic redaction scanning",
                  "Filing fee displayed before submit",
                  "PDF validated and converted to PDF/A",
                  "Docket text AI-generated and editable",
                ].map((t) => (
                  <div key={t} className="flex items-start gap-3 text-[14px] text-white/90">
                    <div className="w-5 h-5 rounded-full bg-[#15803d]/30 flex items-center justify-center shrink-0 mt-0.5">
                      <span className="text-[#bbf7d0] text-[10px] font-bold">&#x2713;</span>
                    </div>
                    {t}
                  </div>
                ))}
              </div>
              <div className="mt-6 pt-5 border-t border-white/10 text-center">
                <span className="text-[28px] font-bold text-white">&lt;1 min</span>
                <span className="text-[13px] text-white/40 block mt-1">per filing</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features grid — bigger cards, more visual weight */}
      <section className="bg-white">
        <div className="max-w-6xl mx-auto px-5 sm:px-8 py-20 sm:py-28">
          <div className="text-center mb-16">
            <div className="text-[11px] font-bold text-[#1e3a5f] uppercase tracking-[0.2em] mb-3">Features</div>
            <h2 className="text-[28px] sm:text-[36px] md:text-[42px] font-bold tracking-tight text-[#0f1f35] mb-4">Built for federal practice</h2>
            <p className="text-[17px] text-[#525252] max-w-lg mx-auto">Every feature prevents filing errors and saves attorney time.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 max-w-5xl mx-auto">
            {[
              { t: "207 federal courts", d: "Every district, bankruptcy, and appellate court. BAPs and special courts included.", icon: "M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21", accent: "from-[#1e3a5f] to-[#3b82f6]" },
              { t: "AI event code matching", d: "Describe your filing in plain English. AI matches the correct CM/ECF event code from hundreds of options.", icon: "M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456z", accent: "from-[#7c3aed] to-[#a855f7]" },
              { t: "Rule 5.2 redaction scan", d: "AI detects unredacted SSNs, DOBs, financial accounts, and minor names before you file.", icon: "M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z", accent: "from-[#15803d] to-[#22c55e]" },
              { t: "PDF pre-flight checks", d: "Validates size, searchable text, encryption, and PDF/A compliance before CM/ECF can reject your filing.", icon: "M10.125 2.25h-4.5c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z", accent: "from-[#b91c1c] to-[#ef4444]" },
              { t: "Sealed & redacted filings", d: "File under seal or submit redacted versions with proper CM/ECF flags. One checkbox.", icon: "M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z", accent: "from-[#b45309] to-[#f59e0b]" },
              { t: "3-pass AI verification", d: "Document integrity, cross-reference, and readiness checks. Attorney attestation required before filing.", icon: "M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z", accent: "from-[#1e3a5f] to-[#0f2440]" },
            ].map(({ t, d, icon, accent }) => (
              <div key={t} className="bg-[#fafaf8] border border-[#e8e5e0] rounded-2xl p-7 hover:border-[#1e3a5f]/30 hover:shadow-lg hover:shadow-[#1e3a5f]/5 transition-all duration-300 group hover:-translate-y-1">
                <div className={`w-11 h-11 bg-gradient-to-br ${accent} rounded-xl flex items-center justify-center mb-5 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
                  </svg>
                </div>
                <h3 className="text-[16px] font-bold text-[#0f1f35] mb-2">{t}</h3>
                <p className="text-[13px] text-[#525252] leading-[1.7]">{d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust bar */}
      <section className="bg-[#fafaf8] border-y border-[#e8e5e0]">
        <div className="max-w-5xl mx-auto px-5 sm:px-8 py-16 sm:py-20">
          <div className="text-center mb-10">
            <div className="text-[11px] font-bold text-[#1e3a5f] uppercase tracking-[0.2em] mb-3">Why Attorneys Trust ECFiler</div>
            <h2 className="text-[28px] sm:text-[36px] font-bold tracking-tight text-[#0f1f35]">Your filing, your control</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: "M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z", title: "10+ min saved per filing", desc: "No more navigating CM/ECF menus. Drop a PDF and go.", stat: "10+" },
              { icon: "M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z", title: "3-pass safety checks", desc: "Nothing is filed without passing document integrity, AI cross-reference, and readiness verification.", stat: "3" },
              { icon: "M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z", title: "Your credentials, encrypted", desc: "AES-256 encryption at rest. Credentials only decrypted at the moment of filing.", stat: "256" },
              { icon: "M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z M15 12a3 3 0 11-6 0 3 3 0 016 0z", title: "Full transparency", desc: "See every step. Edit the docket text. Attorney attestation required before filing.", stat: "100%" },
            ].map(({ icon, title, desc, stat }) => (
              <div key={title} className="bg-white border border-[#e8e5e0] rounded-2xl p-6 text-center hover:shadow-md transition-shadow">
                <div className="w-14 h-14 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-[#1e3a5f]/15">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
                  </svg>
                </div>
                <h3 className="text-[15px] font-bold text-[#0f1f35] mb-2">{title}</h3>
                <p className="text-[12px] text-[#525252] leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech bar */}
      <section className="bg-white border-b border-[#e8e5e0]">
        <div className="max-w-5xl mx-auto px-5 sm:px-8 py-8">
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-8 text-[12px] text-[#8a8a8a] font-medium">
            <span className="text-[10px] uppercase tracking-wider font-bold text-[#1e3a5f]">Built with</span>
            <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-4">
              {["Claude AI", "Playwright", "Next.js", "PACER API", "CM/ECF NextGen"].map((t) => (
                <span key={t} className="px-3.5 py-2 bg-[#fafaf8] border border-[#e8e5e0] rounded-lg text-[#525252] font-medium">{t}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="bg-[#fafaf8]">
        <div className="max-w-5xl mx-auto px-5 sm:px-8 py-20 sm:py-28">
          <div className="text-center mb-12">
            <div className="text-[11px] font-bold text-[#1e3a5f] uppercase tracking-[0.2em] mb-3">Pricing</div>
            <h2 className="text-[28px] sm:text-[36px] md:text-[42px] font-bold tracking-tight text-[#0f1f35] mb-4">Simple, honest pricing</h2>
            <p className="text-[17px] text-[#525252]">Free tools forever. Upgrade when you need AI power.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
            {/* Free */}
            <div className="bg-white border border-[#e8e5e0] rounded-2xl p-8 shadow-sm">
              <div className="text-[11px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-2">Free Tools</div>
              <div className="text-[42px] font-bold text-[#0f1f35] mb-1">$0</div>
              <div className="text-[13px] text-[#8a8a8a] mb-6">Forever. No credit card.</div>
              <Link href="/sign-up" className="block w-full py-3 text-center bg-white text-[#1e3a5f] text-[14px] font-semibold rounded-xl border-2 border-[#e8e5e0] hover:border-[#1e3a5f] hover:bg-[#f0f4fa] transition mb-6">Get Started</Link>
              <div className="space-y-3">
                {[
                  "PDF validation & PDF/A checks",
                  "Rule 5.2 redaction scanning",
                  "207 federal courts directory",
                  "Filing fee lookup",
                  "Certificate of service generator",
                  "Event code browser",
                ].map((f) => (
                  <div key={f} className="flex items-center gap-2.5 text-[13px] text-[#525252]">
                    <div className="w-5 h-5 bg-[#f0fdf4] text-[#15803d] rounded-full flex items-center justify-center text-[9px] font-bold shrink-0">&#10003;</div>
                    {f}
                  </div>
                ))}
              </div>
              <div className="mt-5 pt-5 border-t border-[#f0eee9]">
                <div className="space-y-3">
                  {[
                    "AI document analysis",
                    "AI docket text generation",
                    "AI event code matching",
                    "Automated CM/ECF filing",
                  ].map((f) => (
                    <div key={f} className="flex items-center gap-2.5 text-[13px] text-[#c4c4c4]">
                      <div className="w-5 h-5 bg-[#f5f5f0] text-[#d4d0ca] rounded-full flex items-center justify-center text-[9px] font-bold shrink-0">&mdash;</div>
                      {f}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Pro */}
            <div className="bg-gradient-to-br from-[#0f1f35] to-[#1e3a5f] rounded-2xl p-8 relative overflow-hidden ring-2 ring-[#b8860b]/30 shadow-xl shadow-[#1e3a5f]/20">
              <div className="absolute top-4 right-4 text-[10px] px-2.5 py-1 bg-[#b8860b] text-white rounded-full font-bold shadow-lg">Recommended</div>
              <div className="text-[11px] font-semibold text-white/40 uppercase tracking-wide mb-2">Pro</div>
              <div className="flex items-baseline gap-1 mb-1">
                <span className="text-[42px] font-bold text-white">$99</span>
                <span className="text-[14px] text-white/40">/attorney/mo</span>
              </div>
              <div className="text-[13px] text-white/40 mb-6">Cancel anytime. Stripe billing.</div>
              <Waitlist />
              <div className="space-y-3 mt-6">
                {[
                  "Everything in Free",
                  "AI document analysis",
                  "AI docket text generation",
                  "AI event code matching",
                  "3-pass AI safety verification",
                  "Automated CM/ECF submission",
                  "Live browser view of filing",
                  "Filing history & PDF archive",
                  "Team management",
                  "Priority support",
                ].map((f) => (
                  <div key={f} className="flex items-center gap-2.5 text-[13px] text-white/80">
                    <div className="w-5 h-5 bg-white/10 text-[#bbf7d0] rounded-full flex items-center justify-center text-[9px] font-bold shrink-0">&#10003;</div>
                    {f}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-[#0f1f35] relative overflow-hidden">
        <div className="absolute inset-0 opacity-[0.04]" style={{ backgroundImage: "radial-gradient(circle at 2px 2px, white 1px, transparent 0)", backgroundSize: "32px 32px" }} />
        <div className="relative max-w-6xl mx-auto px-5 sm:px-8 py-20 sm:py-28 text-center">
          <h2 className="text-[28px] sm:text-[36px] md:text-[42px] font-bold tracking-tight text-white mb-4">Ready to modernize your filing?</h2>
          <p className="text-[17px] text-white/50 mb-10 max-w-md mx-auto">Free tools. 207 courts. No credit card required.</p>
          <div className="flex flex-col sm:flex-row w-full sm:w-auto gap-4 justify-center">
            <Link href="/sign-up" className="w-full sm:w-auto px-10 py-4 bg-white text-[#0f1f35] text-[16px] font-bold rounded-xl hover:bg-[#f5f5f0] transition-all shadow-xl hover:shadow-2xl hover:-translate-y-0.5 text-center">Get Started Free</Link>
            <a href="https://github.com/jackson-jpeg/ecfiler" target="_blank" className="w-full sm:w-auto px-10 py-4 border-2 border-white/20 text-white/80 text-[16px] font-semibold rounded-xl hover:border-white/40 hover:text-white transition-all text-center">Star on GitHub</a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-[#e8e5e0]">
        <div className="max-w-6xl mx-auto px-5 sm:px-8 py-10">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-6 h-6 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-md flex items-center justify-center text-white text-[9px] font-bold">E</div>
                <span className="text-[13px] font-semibold text-[#1a1a1a]">ECFiler</span>
              </div>
              <p className="text-[11px] text-[#8a8a8a] leading-relaxed">AI-powered federal court filing. 207 courts supported.</p>
            </div>
            <div>
              <div className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-3">Product</div>
              <div className="space-y-2 text-[12px]">
                <Link href="/file" className="block text-[#525252] hover:text-[#1a1a1a] transition">Filing Workspace</Link>
                <Link href="/federal-courts" className="block text-[#525252] hover:text-[#1a1a1a] transition">Court Directory</Link>
                <Link href="/sign-up" className="block text-[#525252] hover:text-[#1a1a1a] transition">Sign Up</Link>
              </div>
            </div>
            <div>
              <div className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-3">Resources</div>
              <div className="space-y-2 text-[12px]">
                <Link href="/what-is-cmecf" className="block text-[#525252] hover:text-[#1a1a1a] transition">What is CM/ECF?</Link>
                <a href="https://github.com/jackson-jpeg/ecfiler" className="block text-[#525252] hover:text-[#1a1a1a] transition">GitHub</a>
                <a href="https://pacer.uscourts.gov" target="_blank" className="block text-[#525252] hover:text-[#1a1a1a] transition">PACER</a>
              </div>
            </div>
            <div>
              <div className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-3">Legal</div>
              <div className="space-y-2 text-[12px]">
                <Link href="/privacy" className="block text-[#525252] hover:text-[#1a1a1a] transition">Privacy Policy</Link>
                <Link href="/terms" className="block text-[#525252] hover:text-[#1a1a1a] transition">Terms of Service</Link>
                <span className="block text-[#8a8a8a]">Filing tool, not legal advice</span>
              </div>
            </div>
          </div>
          <div className="border-t border-[#f0eee9] pt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
            <span className="text-[11px] text-[#c4c4c4]">&copy; {new Date().getFullYear()} ECFiler. Not affiliated with the U.S. Courts.</span>
            <span className="text-[11px] text-[#c4c4c4]">ecfiler.com</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

function Waitlist() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [count, setCount] = useState(0);

  useEffect(() => {
    fetch("/api/waitlist/count").then(r => r.json()).then(d => setCount(d.count || 0)).catch(() => {});
  }, [status]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); if (!email) return; setStatus("loading");
    try { await fetch("/api/waitlist", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email }) }); setStatus("done"); } catch { setStatus("error"); }
  };
  return (
    <div>
      {status === "done" ? (
        <div className="flex items-center gap-2 px-4 py-2.5 bg-white/10 border border-white/10 rounded-xl text-[13px] text-[#bbf7d0] font-medium">
          <span className="w-2 h-2 bg-[#bbf7d0] rounded-full" />You&apos;re on the list
        </div>
      ) : (
        <form onSubmit={submit} className="flex gap-2">
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@lawfirm.com" required className="flex-1 px-3 py-2.5 bg-white/10 border border-white/10 rounded-xl text-[13px] text-white placeholder-white/30 outline-none focus:border-white/30" />
          <button type="submit" disabled={status === "loading"} className="px-4 py-2.5 bg-[#b8860b] text-white text-[13px] font-semibold rounded-xl hover:bg-[#a07709] disabled:opacity-50 transition shadow-lg shadow-[#b8860b]/30">
            {status === "loading" ? "..." : "Join Waitlist"}
          </button>
        </form>
      )}
      {count > 0 && status !== "done" && <div className="text-[10px] text-white/30 mt-2">{count} attorney{count !== 1 ? "s" : ""} on the waitlist</div>}
    </div>
  );
}
