"use client";

import { useState, useEffect, useRef } from "react";

const STEPS = [
  { label: "Validating PDF", detail: "2.3MB, 15 pages, searchable, PDF/A" },
  { label: "Extracting text", detail: "3,847 characters from 15 pages" },
  { label: "AI document analysis", detail: "Identified: Motion to Dismiss for Failure to State a Claim" },
  { label: "Redaction scan", detail: "No unredacted identifiers (Rule 5.2 clean)" },
  { label: "Matching event code", detail: "Event 12 — Motion to Dismiss (97% confidence)" },
  { label: "Generating docket text", detail: "Motion to Dismiss for Failure to State a Claim" },
];

const CHECKS = [
  { ok: true, text: "PDF valid — 2.3MB, 15 pages, searchable" },
  { ok: true, text: "No unredacted identifiers (Rule 5.2)" },
  { ok: true, text: "Case 1:24-cv-01234-ABC matches document" },
  { ok: true, text: "Event code 12 matches document type" },
  { ok: true, text: "Signed by J. Smith, Esq." },
];

const BROWSER_STEPS = [
  { step: "Authenticating with PACER", desc: "Token obtained via CSO API" },
  { step: "Navigating to CM/ECF", desc: "ecf.nysd.uscourts.gov" },
  { step: "Opening filing module", desc: "Civil → File a Document" },
  { step: "Selecting case", desc: "1:24-cv-01234-ABC" },
  { step: "Selecting event", desc: "Motion to Dismiss (12)" },
  { step: "Uploading document", desc: "motion_to_dismiss.pdf" },
  { step: "Filing submitted", desc: "Docket #58 assigned" },
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
        const t = setTimeout(() => { setPhase("review"); setDocketTyped(""); }, 500);
        return () => clearTimeout(t);
      }
      const t = setTimeout(() => setVisibleSteps((v) => v + 1), 600);
      return () => clearTimeout(t);
    }
    if (phase === "review") {
      // Type out docket text
      if (docketTyped.length < docketText.length) {
        const t = setTimeout(() => setDocketTyped(docketText.slice(0, docketTyped.length + 1)), 30);
        return () => clearTimeout(t);
      }
      // After typing done, wait then transition to filing
      const t = setTimeout(() => { setPhase("filing"); setBrowserStep(0); }, 3000);
      return () => clearTimeout(t);
    }
    if (phase === "filing") {
      if (browserStep >= BROWSER_STEPS.length) {
        // Loop back after showing filing complete
        const t = setTimeout(() => { setPhase("analyzing"); setVisibleSteps(0); }, 4000);
        return () => clearTimeout(t);
      }
      const t = setTimeout(() => setBrowserStep((v) => v + 1), 800);
      return () => clearTimeout(t);
    }
  }, [phase, visibleSteps, docketTyped, browserStep]);

  const start = () => { setPhase("analyzing"); setVisibleSteps(0); };

  // Auto-start when scrolled into view
  const demoRef = useRef<HTMLDivElement>(null);
  const hasAutoStarted = useRef(false);
  useEffect(() => {
    const el = demoRef.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAutoStarted.current && phase === "idle") {
          hasAutoStarted.current = true;
          setTimeout(start, 500);
        }
      },
      { threshold: 0.4 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [phase]);

  return (
    <div ref={demoRef} className="rounded-2xl border border-[#9e9a94] overflow-hidden shadow-2xl shadow-black/20 bg-white">
      {/* Browser chrome */}
      <div className="bg-[#c8c4be] px-4 sm:px-5 py-2.5 flex items-center gap-3 border-b border-[#a8a49e]">
        <div className="flex gap-[6px]">
          <div className="w-[11px] h-[11px] rounded-full bg-[#ff5f57]" />
          <div className="w-[11px] h-[11px] rounded-full bg-[#febc2e]" />
          <div className="w-[11px] h-[11px] rounded-full bg-[#28c840]" />
        </div>
        <div className="flex-1 mx-4 sm:mx-8">
          <div className="bg-white rounded-md px-3 sm:px-4 py-[5px] text-[10px] sm:text-[11px] text-[#525252] font-mono text-center border border-[#a8a49e]">
            {phase === "filing" ? "ecf.nysd.uscourts.gov" : "ecfiler.com/file"}
          </div>
        </div>
        {(phase === "analyzing" || phase === "filing") && (
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 bg-[#1e3a5f] rounded-full animate-pulse" />
            <span className="text-[9px] font-semibold text-[#525252]">LIVE</span>
          </div>
        )}
      </div>

      {/* App content */}
      <div className="bg-[#f5f3ee]" style={{ minHeight: "min(440px, 75vh)" }}>
        {/* Top bar */}
        <div className="bg-white border-b border-[#e8e5e0] px-4 sm:px-5 h-10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <div className="w-5 h-5 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-md flex items-center justify-center text-white text-[7px] font-bold">E</div>
              <span className="text-[11px] font-semibold text-[#1a1a1a]">ECFiler</span>
            </div>
            <div className="h-3 w-px bg-[#e8e5e0]" />
            <span className="text-[10px] text-[#8a8a8a]">History</span>
            <span className="text-[10px] text-[#8a8a8a]">Courts</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-[#8a8a8a]">Settings</span>
            <div className="w-5 h-5 bg-[#e8e5e0] rounded-full" />
          </div>
        </div>

        <div className="p-4 sm:p-5">
          {/* Idle — drop zone */}
          {phase === "idle" && (
            <div>
              <div
                onClick={start}
                className="border-2 border-dashed border-[#c4bfb6] rounded-xl p-8 text-center cursor-pointer hover:border-[#1e3a5f] hover:bg-white/70 hover:shadow-lg transition-all group"
              >
                <div className="w-10 h-10 bg-[#e8e5e0] group-hover:bg-[#dbeafe] rounded-xl flex items-center justify-center mx-auto mb-3 transition">
                  <svg className="w-5 h-5 text-[#8a8a8a] group-hover:text-[#1e3a5f] transition" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.338-2.32 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
                  </svg>
                </div>
                <div className="text-[12px] font-semibold text-[#525252] group-hover:text-[#1e3a5f] transition">Click to see a live demo</div>
                <div className="text-[10px] text-[#8a8a8a] mt-1">Watch AI analyze a filing and submit to CM/ECF</div>
              </div>
              <div className="grid grid-cols-3 gap-2 mt-3">
                {[
                  { n: "207", label: "Federal Courts" },
                  { n: "7", label: "Safety Checks" },
                  { n: "<1m", label: "To File" },
                ].map(({ n, label }) => (
                  <div key={label} className="bg-white rounded-lg border border-[#e8e5e0] p-2.5 text-center">
                    <div className="text-[14px] font-bold text-[#1e3a5f]">{n}</div>
                    <div className="text-[8px] text-[#8a8a8a] font-medium">{label}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analyzing */}
          {phase === "analyzing" && (
            <div className="bg-white rounded-xl border border-[#e8e5e0] overflow-hidden shadow-sm">
              <div className="px-4 py-3 border-b border-[#f0eee9] bg-[#fafaf8]">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-[13px] font-bold text-[#1a1a1a]">Analyzing Document</div>
                    <div className="text-[10px] text-[#8a8a8a] font-mono">motion_to_dismiss.pdf</div>
                  </div>
                  <span className="text-[9px] font-medium text-[#8a8a8a]">{Math.min(visibleSteps, STEPS.length)}/{STEPS.length}</span>
                </div>
                <div className="mt-2 h-1 bg-[#e8e5e0] rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-[#1e3a5f] to-[#3b82f6] rounded-full transition-all duration-500" style={{ width: `${(visibleSteps / STEPS.length) * 100}%` }} />
                </div>
              </div>
              {STEPS.slice(0, visibleSteps).map((step, i) => (
                <div key={step.label} className="flex items-center gap-3 px-4 py-2 border-b border-[#f0eee9] last:border-0" style={{ animation: "fadeIn 0.3s ease-out" }}>
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold shrink-0 ${i < visibleSteps - 1 ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#1e3a5f] text-white"}`}>
                    {i < visibleSteps - 1 ? "✓" : <span className="animate-pulse">●</span>}
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className="text-[11px] font-medium text-[#1a1a1a]">{step.label}</span>
                    {i < visibleSteps - 1 && <span className="text-[9px] text-[#8a8a8a] font-mono ml-2 hidden sm:inline">{step.detail}</span>}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Review */}
          {phase === "review" && (
            <div>
              <div className="bg-white rounded-xl border-2 border-[#1e3a5f]/20 overflow-hidden shadow-md mb-3">
                <div className="px-4 py-2.5 bg-gradient-to-r from-[#0f1f35] to-[#1e3a5f] flex items-center justify-between">
                  <div>
                    <div className="text-[11px] font-semibold text-white">Docket Text</div>
                    <div className="text-[8px] text-white/40">AI generating...</div>
                  </div>
                  <span className={`text-[8px] px-2 py-0.5 rounded font-mono border ${docketTyped.length < docketText.length ? "bg-white/20 text-white border-white/20 animate-pulse" : "bg-white/10 text-white/60 border-white/10"}`}>
                    {docketTyped.length < docketText.length ? "AI typing..." : "editable"}
                  </span>
                </div>
                <div className="p-4">
                  <div className="w-full px-3 py-2.5 border border-[#e8e5e0] rounded-lg text-[13px] font-semibold text-[#1a1a1a] bg-[#fafaf8] min-h-[40px]">
                    {docketTyped}<span className={docketTyped.length < docketText.length ? "inline-block w-[2px] h-[14px] bg-[#1e3a5f] ml-px animate-pulse align-text-bottom" : "hidden"} />
                  </div>
                </div>
                <div className="px-4 py-2.5 bg-[#fafaf8] border-t border-[#f0eee9]">
                  <div className="text-[8px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1">CM/ECF Docket Preview</div>
                  <div className="text-[10px] text-[#1a1a1a]">
                    <span className="text-[#c4c4c4] font-mono">#--</span>{" "}
                    <span className="font-semibold">{docketTyped || "..."}</span>{" "}
                    filed by Jones Corp. <span className="text-[#8a8a8a]">(1:24-cv-01234)</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 mb-3">
                {[
                  { label: "Court", value: "S.D.N.Y.", color: "text-[#1e3a5f]" },
                  { label: "Case", value: "1:24-cv-01234", color: "text-[#1a1a1a]" },
                  { label: "Fee", value: "$0.00", color: "text-[#15803d]" },
                ].map(({ label, value, color }) => (
                  <div key={label} className="bg-white rounded-lg border border-[#e8e5e0] p-2">
                    <div className="text-[8px] font-semibold text-[#8a8a8a] uppercase tracking-wide">{label}</div>
                    <div className={`text-[11px] font-bold ${color} font-mono`}>{value}</div>
                  </div>
                ))}
              </div>

              <div className="bg-gradient-to-r from-[#0f1f35] to-[#1e3a5f] rounded-xl p-3 flex items-center justify-between">
                <div>
                  <div className="text-[11px] font-bold text-white">Ready to file</div>
                  <div className="text-[8px] text-white/40">5 checks passed · SDNY</div>
                </div>
                <div className="px-4 py-1.5 bg-white text-[#1e3a5f] text-[10px] font-bold rounded-lg shadow">
                  Confirm &amp; File
                </div>
              </div>
            </div>
          )}

          {/* Filing — CM/ECF browser view */}
          {phase === "filing" && (
            <div>
              {/* Browser chrome within the app */}
              <div className="rounded-xl border border-[#c4bfb6] overflow-hidden shadow-lg mb-3">
                <div className="bg-[#e8e5e0] px-3 py-1.5 flex items-center gap-2 border-b border-[#d4d0ca]">
                  <div className="flex gap-[4px]">
                    <div className="w-[8px] h-[8px] rounded-full bg-[#ff5f57]" />
                    <div className="w-[8px] h-[8px] rounded-full bg-[#febc2e]" />
                    <div className="w-[8px] h-[8px] rounded-full bg-[#28c840]" />
                  </div>
                  <div className="flex-1 text-center font-mono text-[9px] text-[#525252]">ecf.nysd.uscourts.gov</div>
                  {browserStep < BROWSER_STEPS.length && <span className="text-[8px] text-[#1e3a5f] font-semibold animate-pulse">LIVE</span>}
                </div>
                <div className="bg-[#f8f7f5] p-3 min-h-[120px]">
                  {/* Mock CM/ECF content */}
                  <div className="bg-white border border-[#d4d0ca] rounded p-3">
                    <div className="text-[10px] font-bold text-[#1a1a1a] mb-2 border-b border-[#e8e5e0] pb-1">
                      CM/ECF — Southern District of New York
                    </div>
                    {BROWSER_STEPS.slice(0, browserStep).map((s, i) => (
                      <div key={s.step} className="flex items-center gap-2 py-1" style={{ animation: "fadeIn 0.3s ease-out" }}>
                        <div className={`w-3.5 h-3.5 rounded-full flex items-center justify-center text-[7px] font-bold ${i < browserStep - 1 ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#1e3a5f] text-white"}`}>
                          {i < browserStep - 1 ? "✓" : "●"}
                        </div>
                        <span className="text-[9px] font-medium text-[#1a1a1a]">{s.step}</span>
                        <span className="text-[8px] text-[#8a8a8a] ml-auto hidden sm:inline">{s.desc}</span>
                      </div>
                    ))}
                    {browserStep >= BROWSER_STEPS.length && (
                      <div className="mt-2 pt-2 border-t border-[#e8e5e0]">
                        <div className="text-[10px] font-bold text-[#15803d] flex items-center gap-1.5">
                          <span className="w-4 h-4 bg-[#f0fdf4] rounded-full flex items-center justify-center text-[8px]">✓</span>
                          Filing Complete — Docket #58
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Progress */}
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-[#8a8a8a]">{Math.min(browserStep, BROWSER_STEPS.length)}/{BROWSER_STEPS.length} steps</span>
                {browserStep >= BROWSER_STEPS.length && (
                  <span className="text-[#15803d] font-semibold">Filed successfully</span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }`}</style>
    </div>
  );
}
