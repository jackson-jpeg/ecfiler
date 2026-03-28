"use client";

import { useState, useEffect, useRef } from "react";

const STEPS = [
  { label: "Validating PDF", detail: "2.3MB · 15 pages · searchable · PDF/A", icon: "doc" },
  { label: "Extracting text", detail: "3,847 characters from 15 pages", icon: "text" },
  { label: "AI document analysis", detail: "Motion to Dismiss for Failure to State a Claim", icon: "ai" },
  { label: "Redaction scan (Rule 5.2)", detail: "No unredacted identifiers found", icon: "shield" },
  { label: "Matching event code", detail: "Event 12 — Motion to Dismiss · 97% confidence", icon: "match" },
  { label: "Generating docket text", detail: "Cross-referencing case 1:24-cv-01234-ABC", icon: "gen" },
];

const BROWSER_STEPS = [
  { step: "Authenticating with PACER", desc: "Secure token via CSO API" },
  { step: "Navigating to CM/ECF", desc: "ecf.nysd.uscourts.gov" },
  { step: "Opening filing module", desc: "Civil → File a Document" },
  { step: "Entering case number", desc: "1:24-cv-01234-ABC confirmed" },
  { step: "Selecting event code", desc: "Motion to Dismiss (12)" },
  { step: "Uploading PDF", desc: "motion_to_dismiss.pdf · 2.3MB" },
  { step: "Submitting to court", desc: "Final submission confirmed" },
  { step: "Filing complete", desc: "Docket #58 assigned by clerk" },
];

type Phase = "idle" | "analyzing" | "review" | "filing";

export function InteractiveDemo() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [visibleSteps, setVisibleSteps] = useState(0);
  const [browserStep, setBrowserStep] = useState(0);
  const [docketTyped, setDocketTyped] = useState("");
  const docketText = "Motion to Dismiss for Failure to State a Claim";

  useEffect(() => {
    if (phase === "analyzing") {
      if (visibleSteps >= STEPS.length) {
        const t = setTimeout(() => { setPhase("review"); setDocketTyped(""); }, 600);
        return () => clearTimeout(t);
      }
      const t = setTimeout(() => setVisibleSteps((v) => v + 1), 700);
      return () => clearTimeout(t);
    }
    if (phase === "review") {
      if (docketTyped.length < docketText.length) {
        const t = setTimeout(() => setDocketTyped(docketText.slice(0, docketTyped.length + 1)), 28);
        return () => clearTimeout(t);
      }
      const t = setTimeout(() => { setPhase("filing"); setBrowserStep(0); }, 3500);
      return () => clearTimeout(t);
    }
    if (phase === "filing") {
      if (browserStep >= BROWSER_STEPS.length) {
        const t = setTimeout(() => { setPhase("analyzing"); setVisibleSteps(0); }, 4500);
        return () => clearTimeout(t);
      }
      const t = setTimeout(() => setBrowserStep((v) => v + 1), 750);
      return () => clearTimeout(t);
    }
  }, [phase, visibleSteps, docketTyped, browserStep]);

  const start = () => { setPhase("analyzing"); setVisibleSteps(0); };

  const demoRef = useRef<HTMLDivElement>(null);
  const hasAutoStarted = useRef(false);
  useEffect(() => {
    const el = demoRef.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAutoStarted.current && phase === "idle") {
          hasAutoStarted.current = true;
          setTimeout(start, 400);
        }
      },
      { threshold: 0.3 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [phase]);

  const progressPct = phase === "analyzing"
    ? Math.round((visibleSteps / STEPS.length) * 100)
    : phase === "filing"
    ? Math.round((Math.min(browserStep, BROWSER_STEPS.length) / BROWSER_STEPS.length) * 100)
    : 100;

  return (
    <div ref={demoRef} className="rounded-2xl overflow-hidden shadow-2xl shadow-black/30 ring-1 ring-black/10">
      {/* macOS-style window chrome */}
      <div className="bg-[#2a2a2a] px-4 sm:px-5 py-3 flex items-center gap-3">
        <div className="flex gap-2">
          <div className="w-3 h-3 rounded-full bg-[#ff5f57] shadow-inner shadow-black/20" />
          <div className="w-3 h-3 rounded-full bg-[#febc2e] shadow-inner shadow-black/20" />
          <div className="w-3 h-3 rounded-full bg-[#28c840] shadow-inner shadow-black/20" />
        </div>
        <div className="flex-1 mx-6 sm:mx-12">
          <div className="bg-[#1a1a1a] rounded-lg px-4 py-1.5 text-[11px] sm:text-[12px] text-[#999] font-mono text-center flex items-center justify-center gap-2">
            <svg className="w-3 h-3 text-[#666] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" /></svg>
            {phase === "filing" ? "ecf.nysd.uscourts.gov" : "ecfiler.com/file"}
          </div>
        </div>
        {(phase === "analyzing" || phase === "filing") && (
          <div className="flex items-center gap-1.5 shrink-0">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
            </span>
            <span className="text-[10px] font-bold text-green-400 uppercase tracking-wider">Live</span>
          </div>
        )}
      </div>

      {/* App content */}
      <div className="bg-[#f5f3ee]" style={{ minHeight: "min(480px, 75vh)" }}>
        {/* Top bar */}
        <div className="bg-white border-b border-[#e0ddd7] px-4 sm:px-5 h-11 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[9px] font-bold shadow-sm">E</div>
              <span className="text-[13px] font-bold text-[#1a1a1a]">ECFiler</span>
            </div>
            <div className="h-4 w-px bg-[#e0ddd7]" />
            <span className="text-[11px] text-[#666] font-medium">History</span>
            <span className="text-[11px] text-[#666] font-medium">Courts</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
              <span className="text-[9px] text-[#999]">Connected</span>
            </div>
            <div className="w-6 h-6 bg-gradient-to-br from-[#1e3a5f] to-[#2d5a8e] rounded-full ring-1 ring-black/5" />
          </div>
        </div>

        <div className="p-4 sm:p-6">
          {/* Idle */}
          {phase === "idle" && (
            <div>
              <div
                onClick={start}
                className="bg-white border-2 border-dashed border-[#b0aca4] rounded-2xl p-10 text-center cursor-pointer hover:border-[#1e3a5f] hover:shadow-xl hover:shadow-[#1e3a5f]/10 transition-all group"
              >
                <div className="w-14 h-14 bg-[#f0eee9] group-hover:bg-[#dbeafe] rounded-2xl flex items-center justify-center mx-auto mb-4 transition-all group-hover:scale-110">
                  <svg className="w-7 h-7 text-[#8a8a8a] group-hover:text-[#1e3a5f] transition" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.338-2.32 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
                  </svg>
                </div>
                <div className="text-[15px] font-bold text-[#1a1a1a] group-hover:text-[#1e3a5f] transition mb-1">Click to see a live demo</div>
                <div className="text-[13px] text-[#8a8a8a]">Watch AI analyze a motion and file it on CM/ECF</div>
              </div>
              <div className="grid grid-cols-3 gap-3 mt-4">
                {[
                  { n: "207", label: "Federal Courts", sub: "All districts" },
                  { n: "3-Pass", label: "AI Verification", sub: "Before every filing" },
                  { n: "<1min", label: "To Prepare", sub: "AI does the work" },
                ].map(({ n, label, sub }) => (
                  <div key={label} className="bg-white rounded-xl border border-[#e0ddd7] p-3.5 text-center shadow-sm">
                    <div className="text-[18px] font-bold text-[#1e3a5f]">{n}</div>
                    <div className="text-[11px] font-semibold text-[#1a1a1a] mt-0.5">{label}</div>
                    <div className="text-[9px] text-[#999]">{sub}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analyzing */}
          {phase === "analyzing" && (
            <div className="bg-white rounded-2xl border border-[#e0ddd7] overflow-hidden shadow-lg shadow-black/5">
              <div className="px-5 py-4 border-b border-[#f0eee9] bg-[#fafaf8]">
                <div className="flex items-center justify-between mb-0.5">
                  <div>
                    <div className="text-[15px] font-bold text-[#1a1a1a]">Analyzing Document</div>
                    <div className="text-[12px] text-[#666] font-mono mt-0.5">motion_to_dismiss.pdf · 2.3MB · 15 pages</div>
                  </div>
                  <span className="text-[12px] font-bold text-[#1e3a5f] tabular-nums">{Math.min(visibleSteps, STEPS.length)}/{STEPS.length}</span>
                </div>
                <div className="mt-3 h-1.5 bg-[#e8e5e0] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-[#1e3a5f] to-[#3b82f6] rounded-full transition-all duration-500"
                    style={{ width: `${(visibleSteps / STEPS.length) * 100}%` }}
                  />
                </div>
              </div>
              <div className="px-5 py-3">
                {STEPS.slice(0, visibleSteps).map((step, i) => {
                  const done = i < visibleSteps - 1 || visibleSteps >= STEPS.length;
                  return (
                    <div key={step.label} className="flex items-start gap-3.5 py-2.5 border-b border-[#f0eee9] last:border-0 demo-step-enter">
                      <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-[11px] font-bold shrink-0 transition-all ${
                        done ? "bg-[#dcfce7] text-[#15803d]" : "bg-[#1e3a5f] text-white shadow-md shadow-[#1e3a5f]/30"
                      }`}>
                        {done ? "✓" : <span className="animate-pulse">●</span>}
                      </div>
                      <div className="pt-0.5 min-w-0">
                        <div className={`text-[13px] font-semibold ${done ? "text-[#1a1a1a]" : "text-[#1e3a5f]"}`}>{step.label}</div>
                        {done && <div className="text-[11px] text-[#666] font-mono mt-0.5 truncate">{step.detail}</div>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Review */}
          {phase === "review" && (
            <div>
              {/* Docket text — hero */}
              <div className="bg-white rounded-2xl border-2 border-[#1e3a5f]/30 overflow-hidden shadow-lg shadow-[#1e3a5f]/10 mb-4">
                <div className="px-5 py-3 bg-gradient-to-r from-[#0f1f35] to-[#1e3a5f] flex items-center justify-between">
                  <div>
                    <div className="text-[13px] font-bold text-white">Docket Text</div>
                    <div className="text-[10px] text-white/50 mt-0.5">This will appear on the court docket</div>
                  </div>
                  <span className={`text-[10px] px-2.5 py-1 rounded-lg font-mono font-bold border ${
                    docketTyped.length < docketText.length
                      ? "bg-white/20 text-white border-white/20 animate-pulse"
                      : "bg-[#15803d]/30 text-[#bbf7d0] border-[#15803d]/40"
                  }`}>
                    {docketTyped.length < docketText.length ? "AI typing..." : "✓ Ready"}
                  </span>
                </div>
                <div className="p-5">
                  <div className="w-full px-4 py-3 border-2 border-[#e8e5e0] rounded-xl text-[15px] font-semibold text-[#1a1a1a] bg-[#fafaf8] min-h-[48px] leading-relaxed">
                    {docketTyped}<span className={docketTyped.length < docketText.length ? "inline-block w-[2px] h-[16px] bg-[#1e3a5f] ml-0.5 animate-pulse align-text-bottom" : "hidden"} />
                  </div>
                </div>
                {/* Live docket preview */}
                <div className="px-5 py-3 bg-[#fafaf8] border-t border-[#f0eee9]">
                  <div className="text-[9px] font-bold text-[#8a8a8a] uppercase tracking-widest mb-1.5">CM/ECF Docket Preview</div>
                  <div className="text-[12px] text-[#1a1a1a]">
                    <span className="text-[#c4c4c4] font-mono">#--</span>{" "}
                    <span className="font-bold">{docketTyped || "..."}</span>{" "}
                    filed by Jones Corp. <span className="text-[#8a8a8a]">(1:24-cv-01234)</span>
                  </div>
                </div>
              </div>

              {/* Verification badges */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-4">
                {[
                  { label: "Court", value: "S.D.N.Y.", ok: true },
                  { label: "Case", value: "1:24-cv-01234", ok: true },
                  { label: "Event", value: "Mtn to Dismiss", ok: true },
                  { label: "Confidence", value: "97%", ok: true },
                ].map(({ label, value, ok }) => (
                  <div key={label} className={`rounded-xl border p-3 ${ok ? "bg-[#f0fdf4] border-[#bbf7d0]" : "bg-[#fffbeb] border-[#fde68a]"}`}>
                    <div className="text-[9px] font-bold text-[#8a8a8a] uppercase tracking-wide">{label}</div>
                    <div className={`text-[14px] font-bold ${ok ? "text-[#15803d]" : "text-[#b45309]"}`}>{value}</div>
                  </div>
                ))}
              </div>

              {/* File button */}
              <div className="bg-gradient-to-r from-[#0f1f35] to-[#1e3a5f] rounded-xl p-4 flex items-center justify-between shadow-lg shadow-[#1e3a5f]/20">
                <div>
                  <div className="text-[13px] font-bold text-white">3 safety passes completed</div>
                  <div className="text-[10px] text-white/50">All checks passed · Ready to file</div>
                </div>
                <div className="px-5 py-2 bg-white text-[#1e3a5f] text-[12px] font-bold rounded-lg shadow-lg">
                  Confirm &amp; File
                </div>
              </div>
            </div>
          )}

          {/* Filing — CM/ECF browser view */}
          {phase === "filing" && (
            <div>
              {/* Browser within the app */}
              <div className="rounded-2xl border border-[#999] overflow-hidden shadow-xl shadow-black/15 mb-3">
                {/* CM/ECF chrome */}
                <div className="bg-[#e0ddd7] px-4 py-2 flex items-center gap-3 border-b border-[#ccc]">
                  <div className="flex gap-[5px]">
                    <div className="w-[10px] h-[10px] rounded-full bg-[#ff5f57]" />
                    <div className="w-[10px] h-[10px] rounded-full bg-[#febc2e]" />
                    <div className="w-[10px] h-[10px] rounded-full bg-[#28c840]" />
                  </div>
                  <div className="flex-1 bg-white rounded-md px-3 py-1 flex items-center gap-2">
                    <svg className="w-3 h-3 text-[#666] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" /></svg>
                    <span className="font-mono text-[11px] text-[#333]">ecf.nysd.uscourts.gov</span>
                  </div>
                  {browserStep < BROWSER_STEPS.length && (
                    <div className="flex items-center gap-1.5 shrink-0">
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#1e3a5f] opacity-50" />
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-[#1e3a5f]" />
                      </span>
                      <span className="text-[9px] font-bold text-[#1e3a5f] uppercase tracking-wider">Live</span>
                    </div>
                  )}
                  {browserStep >= BROWSER_STEPS.length && (
                    <span className="text-[9px] font-bold text-[#15803d] uppercase tracking-wider">Done</span>
                  )}
                </div>

                {/* CM/ECF header */}
                <div className="bg-[#003366] px-4 py-2.5 flex items-center gap-3">
                  <div className="w-7 h-7 bg-white/10 rounded flex items-center justify-center border border-white/20">
                    <svg className="w-4 h-4 text-white/90" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" /></svg>
                  </div>
                  <div>
                    <div className="text-white font-serif text-[13px] font-bold">CM/ECF — S.D.N.Y.</div>
                    <div className="text-blue-200/60 text-[9px] font-serif">U.S. District Court — Document Filing System</div>
                  </div>
                </div>

                {/* Steps content */}
                <div className="bg-white p-4 min-h-[160px]">
                  <div className="space-y-0">
                    {BROWSER_STEPS.slice(0, browserStep).map((s, i) => {
                      const done = i < browserStep - 1 || browserStep >= BROWSER_STEPS.length;
                      const isLast = i === Math.min(browserStep, BROWSER_STEPS.length) - 1;
                      const isFinal = i === BROWSER_STEPS.length - 1 && browserStep >= BROWSER_STEPS.length;
                      return (
                        <div key={s.step} className="flex items-center gap-3 py-1.5 demo-step-enter">
                          <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold shrink-0 ${
                            isFinal ? "bg-[#15803d] text-white" : done ? "bg-[#dcfce7] text-[#15803d]" : "bg-[#1e3a5f] text-white"
                          }`}>
                            {done || isFinal ? "✓" : <span className="animate-pulse">●</span>}
                          </div>
                          <span className={`text-[12px] font-medium ${isFinal ? "text-[#15803d] font-bold" : "text-[#1a1a1a]"}`}>{s.step}</span>
                          <span className="text-[10px] text-[#999] ml-auto hidden sm:inline">{s.desc}</span>
                        </div>
                      );
                    })}
                  </div>
                  {browserStep >= BROWSER_STEPS.length && (
                    <div className="mt-3 pt-3 border-t border-[#e8e5e0] flex items-center gap-3 demo-step-enter">
                      <div className="w-8 h-8 bg-[#15803d] rounded-full flex items-center justify-center shadow-md shadow-green-400/30">
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={3}><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                      </div>
                      <div>
                        <div className="text-[14px] font-bold text-[#15803d]">Filing Complete</div>
                        <div className="text-[11px] text-[#666]">Docket #58 assigned · NEF sent to all parties</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Progress bar below */}
              <div className="flex items-center justify-between">
                <div className="flex-1 mr-4">
                  <div className="h-1.5 bg-[#e8e5e0] rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${progressPct}%`,
                        background: browserStep >= BROWSER_STEPS.length
                          ? "linear-gradient(90deg, #15803d, #22c55e)"
                          : "linear-gradient(90deg, #1e3a5f, #3b82f6)",
                      }}
                    />
                  </div>
                </div>
                <span className={`text-[11px] font-bold tabular-nums ${browserStep >= BROWSER_STEPS.length ? "text-[#15803d]" : "text-[#1e3a5f]"}`}>
                  {browserStep >= BROWSER_STEPS.length ? "Filed" : `${Math.min(browserStep, BROWSER_STEPS.length)}/${BROWSER_STEPS.length}`}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes demoStepEnter { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
        .demo-step-enter { animation: demoStepEnter 0.3s ease-out; }
      `}</style>
    </div>
  );
}
