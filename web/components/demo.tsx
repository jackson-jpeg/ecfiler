"use client";

import { useState, useEffect } from "react";

const STEPS = [
  { label: "Validating PDF", detail: "2.3MB, 15 pages, searchable" },
  { label: "Reading document", detail: "3,847 characters extracted" },
  { label: "AI analyzing", detail: "Case 1:24-cv-01234 — SDNY — Jones Corp" },
  { label: "Scanning redaction", detail: "No issues found (Rule 5.2)" },
  { label: "Matching event code", detail: "Motion to Dismiss (Code 12)" },
];

const FIELDS = [
  { label: "Document", value: "Motion to Dismiss for Failure to State a Claim" },
  { label: "Case", value: "1:24-cv-01234-ABC", mono: true },
  { label: "Court", value: "S.D.N.Y. (nysd)" },
  { label: "Docket Text", value: "Motion to Dismiss", bold: true },
  { label: "Filing Party", value: "Jones Corporation (defendant)" },
  { label: "Fee", value: "$0.00 — No filing fee" },
];

export function InteractiveDemo() {
  const [phase, setPhase] = useState<"idle" | "analyzing" | "review">("idle");
  const [visibleSteps, setVisibleSteps] = useState(0);

  useEffect(() => {
    if (phase !== "analyzing") return;
    if (visibleSteps >= STEPS.length) {
      const t = setTimeout(() => setPhase("review"), 600);
      return () => clearTimeout(t);
    }
    const t = setTimeout(() => setVisibleSteps((v) => v + 1), 800);
    return () => clearTimeout(t);
  }, [phase, visibleSteps]);

  const start = () => {
    setPhase("analyzing");
    setVisibleSteps(0);
  };

  const reset = () => {
    setPhase("idle");
    setVisibleSteps(0);
  };

  return (
    <div className="rounded-2xl border border-[#b8b3aa] overflow-hidden shadow-2xl shadow-black/12 bg-white">
      {/* Browser chrome */}
      <div className="bg-[#ddd9d3] px-5 py-2.5 flex items-center gap-3 border-b border-[#c4bfb6]">
        <div className="flex gap-[6px]">
          <div className="w-[11px] h-[11px] rounded-full bg-[#ff5f57]" />
          <div className="w-[11px] h-[11px] rounded-full bg-[#febc2e]" />
          <div className="w-[11px] h-[11px] rounded-full bg-[#28c840]" />
        </div>
        <div className="flex-1 mx-8">
          <div className="bg-white rounded-md px-4 py-[5px] text-[11px] text-[#525252] font-mono text-center border border-[#c4bfb6]">
            ecfiler.com/file
          </div>
        </div>
      </div>

      {/* App content */}
      <div className="flex" style={{ minHeight: 380 }}>
        {/* Mini sidebar */}
        <div className="hidden md:block w-[180px] bg-[#0f1f35] p-3 shrink-0">
          <div className="flex items-center gap-2 mb-5 px-2 pt-1">
            <div className="w-6 h-6 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-md flex items-center justify-center text-white text-[9px] font-bold">E</div>
            <span className="text-white font-semibold text-[11px]">ECFiler</span>
          </div>
          <div className="text-[8px] text-white/20 uppercase tracking-[0.15em] px-2 mb-1.5">Filing</div>
          {["Filing Dashboard", "Drafts", "History"].map((item, i) => (
            <div key={item} className={`text-[10px] px-2 py-[6px] rounded-md mb-px ${i === 0 ? "bg-white/[0.08] text-white font-medium" : "text-white/25"}`}>{item}</div>
          ))}
          <div className="text-[8px] text-white/20 uppercase tracking-[0.15em] px-2 mb-1.5 mt-4">Tools</div>
          {["PDF Validator", "Certificate of Service", "Court Directory", "Settings"].map((item) => (
            <div key={item} className="text-[10px] px-2 py-[6px] text-white/25">{item}</div>
          ))}
        </div>

        {/* Main area */}
        <div className="flex-1 bg-[#f5f3ee] p-6">
          {/* Idle — drop zone */}
          {phase === "idle" && (
            <div>
              <div className="text-[14px] font-bold text-[#1a1a1a] mb-1">Filing Dashboard</div>
              <div className="text-[11px] text-[#8a8a8a] mb-5">Drop a document to start filing.</div>
              <div
                onClick={start}
                className="border-2 border-dashed border-[#c4bfb6] rounded-xl p-10 text-center cursor-pointer hover:border-[#1e3a5f] hover:bg-white/50 transition-all group"
              >
                <div className="w-10 h-10 bg-[#e8e5e0] group-hover:bg-[#dbeafe] rounded-xl flex items-center justify-center mx-auto mb-3 transition">
                  <svg className="w-5 h-5 text-[#8a8a8a] group-hover:text-[#1e3a5f] transition" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.338-2.32 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
                  </svg>
                </div>
                <div className="text-[12px] font-semibold text-[#525252] group-hover:text-[#1e3a5f] transition">Click to try the demo</div>
                <div className="text-[10px] text-[#8a8a8a] mt-0.5">See how AI analyzes a federal court filing</div>
              </div>
            </div>
          )}

          {/* Analyzing */}
          {phase === "analyzing" && (
            <div>
              <div className="text-[14px] font-bold text-[#1a1a1a] mb-1">Analyzing</div>
              <div className="text-[11px] text-[#8a8a8a] mb-4 font-mono">motion_to_dismiss.pdf</div>
              <div className="bg-white rounded-xl border border-[#d4d0ca] overflow-hidden shadow-sm">
                {STEPS.slice(0, visibleSteps).map((step, i) => (
                  <div key={step.label} className="flex items-center gap-3 px-4 py-3 border-b border-[#f0eee9] last:border-0" style={{ animation: "fadeIn 0.3s ease-out" }}>
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold ${
                      i < visibleSteps - 1 ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#e1effe] text-[#1e3a5f]"
                    }`}>
                      {i < visibleSteps - 1 ? "✓" : <span className="animate-pulse">●</span>}
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[12px] font-medium text-[#1a1a1a]">{step.label}</span>
                      {i < visibleSteps - 1 && <span className="text-[10px] text-[#8a8a8a] font-mono ml-2">{step.detail}</span>}
                    </div>
                  </div>
                ))}
                {visibleSteps < STEPS.length && (
                  <div className="px-4 py-3 flex items-center gap-3">
                    <div className="w-5 h-5 rounded-full bg-[#e1effe] flex items-center justify-center">
                      <span className="w-1.5 h-1.5 bg-[#1e3a5f] rounded-full animate-pulse" />
                    </div>
                    <span className="text-[12px] text-[#8a8a8a]">{STEPS[visibleSteps]?.label}...</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Review */}
          {phase === "review" && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="text-[14px] font-bold text-[#1a1a1a]">Review Filing</div>
                  <div className="text-[11px] text-[#8a8a8a]">Confirm before submitting to CM/ECF.</div>
                </div>
                <span className="text-[10px] px-2.5 py-1 bg-[#f0fdf4] text-[#15803d] rounded-full font-semibold border border-[#bbf7d0]">100% extracted</span>
              </div>
              <div className="bg-white rounded-xl border border-[#d4d0ca] overflow-hidden shadow-sm mb-3">
                {FIELDS.map(({ label, value, mono, bold }) => (
                  <div key={label} className="flex px-4 py-2.5 border-b border-[#f0eee9] last:border-0">
                    <div className="w-[90px] shrink-0 text-[9px] font-semibold text-[#8a8a8a] uppercase tracking-wide pt-0.5">{label}</div>
                    <div className={`text-[12px] ${bold ? "font-semibold" : ""} ${mono ? "font-mono" : ""} text-[#1a1a1a]`}>{value}</div>
                  </div>
                ))}
              </div>
              <div className="flex items-center gap-3">
                <button onClick={reset} className="px-5 py-2 bg-[#1e3a5f] text-white text-[11px] font-semibold rounded-lg hover:bg-[#162a47] transition shadow-sm">
                  Confirm &amp; File
                </button>
                <button onClick={reset} className="text-[11px] text-[#8a8a8a] hover:text-[#525252] transition">Try again</button>
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }`}</style>
    </div>
  );
}
