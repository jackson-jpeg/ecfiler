"use client";

import { useState, useEffect, useRef } from "react";

const STEPS = [
  { label: "Validating PDF", detail: "2.3MB, 15 pages, searchable, no encryption" },
  { label: "Extracting text", detail: "3,847 characters from 15 pages" },
  { label: "AI document analysis", detail: "Identified: Motion to Dismiss for Failure to State a Claim" },
  { label: "Redaction scan", detail: "No unredacted identifiers (Rule 5.2 clean)" },
  { label: "Matching event code", detail: "Event 12 — Motion to Dismiss (97% confidence)" },
  { label: "Verification complete", detail: "Case 1:24-cv-01234-ABC — S.D.N.Y." },
];

const CHECKS = [
  { ok: true, text: "PDF valid — 2.3MB, 15 pages, searchable" },
  { ok: true, text: "No unredacted identifiers (Rule 5.2)" },
  { ok: true, text: "Case 1:24-cv-01234-ABC matches document" },
  { ok: true, text: "Event code 12 matches document type" },
  { ok: true, warn: true, text: "Certificate of service detected" },
];

export function InteractiveDemo() {
  const [phase, setPhase] = useState<"idle" | "analyzing" | "review">("idle");
  const [visibleSteps, setVisibleSteps] = useState(0);

  useEffect(() => {
    if (phase === "analyzing") {
      if (visibleSteps >= STEPS.length) {
        const t = setTimeout(() => setPhase("review"), 500);
        return () => clearTimeout(t);
      }
      const t = setTimeout(() => setVisibleSteps((v) => v + 1), 700);
      return () => clearTimeout(t);
    }
    if (phase === "review") {
      // Auto-restart after 6 seconds
      const t = setTimeout(() => { setPhase("analyzing"); setVisibleSteps(0); }, 6000);
      return () => clearTimeout(t);
    }
  }, [phase, visibleSteps]);

  const start = () => { setPhase("analyzing"); setVisibleSteps(0); };
  const reset = () => { setPhase("idle"); setVisibleSteps(0); };

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
          setTimeout(start, 500); // Small delay for dramatic effect
        }
      },
      { threshold: 0.5 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [phase]);

  return (
    <div ref={demoRef} className="rounded-2xl border border-[#9e9a94] overflow-hidden shadow-2xl shadow-black/20 bg-white">
      {/* Browser chrome */}
      <div className="bg-[#c8c4be] px-5 py-2.5 flex items-center gap-3 border-b border-[#a8a49e]">
        <div className="flex gap-[6px]">
          <div className="w-[11px] h-[11px] rounded-full bg-[#ff5f57]" />
          <div className="w-[11px] h-[11px] rounded-full bg-[#febc2e]" />
          <div className="w-[11px] h-[11px] rounded-full bg-[#28c840]" />
        </div>
        <div className="flex-1 mx-4 sm:mx-8">
          <div className="bg-white rounded-md px-3 sm:px-4 py-[5px] text-[10px] sm:text-[11px] text-[#525252] font-mono text-center border border-[#a8a49e]">
            ecfiler.com/file
          </div>
        </div>
      </div>

      {/* App content — matches actual app layout */}
      <div className="bg-[#f5f3ee]" style={{ minHeight: "min(420px, 70vh)" }}>
        {/* Top bar */}
        <div className="bg-white border-b border-[#e8e5e0] px-5 h-10 flex items-center justify-between">
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

        <div className="p-5">
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
                <div className="text-[12px] font-semibold text-[#525252] group-hover:text-[#1e3a5f] transition">Click to try the demo</div>
                <div className="text-[10px] text-[#8a8a8a] mt-1">See how AI analyzes a federal court filing in real-time</div>
                <div className="flex flex-wrap justify-center gap-1 mt-3">
                  {["Motions", "Briefs", "Complaints", "Notices", "Exhibits"].map((t) => (
                    <span key={t} className="text-[8px] px-1.5 py-0.5 bg-[#e8e5e0] text-[#8a8a8a] rounded font-medium">{t}</span>
                  ))}
                </div>
              </div>
              {/* Mini stats */}
              <div className="grid grid-cols-3 gap-2 mt-3">
                <div className="bg-white rounded-lg border border-[#e8e5e0] p-2.5 text-center">
                  <div className="text-[14px] font-bold text-[#1e3a5f]">207</div>
                  <div className="text-[8px] text-[#8a8a8a] font-medium">Federal Courts</div>
                </div>
                <div className="bg-white rounded-lg border border-[#e8e5e0] p-2.5 text-center">
                  <div className="text-[14px] font-bold text-[#1e3a5f]">6</div>
                  <div className="text-[8px] text-[#8a8a8a] font-medium">AI Checks</div>
                </div>
                <div className="bg-white rounded-lg border border-[#e8e5e0] p-2.5 text-center">
                  <div className="text-[14px] font-bold text-[#15803d]">100%</div>
                  <div className="text-[8px] text-[#8a8a8a] font-medium">Accuracy</div>
                </div>
              </div>
            </div>
          )}

          {/* Analyzing */}
          {phase === "analyzing" && (
            <div>
              <div className="bg-white rounded-xl border border-[#e8e5e0] overflow-hidden shadow-sm">
                <div className="px-4 py-3 border-b border-[#f0eee9] bg-[#fafaf8]">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-[13px] font-bold text-[#1a1a1a]">Analyzing Document</div>
                      <div className="text-[10px] text-[#8a8a8a] font-mono">motion_to_dismiss.pdf</div>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 bg-[#1e3a5f] rounded-full animate-pulse" />
                      <span className="text-[10px] font-medium text-[#1e3a5f]">Processing</span>
                    </div>
                  </div>
                  {/* Progress bar */}
                  <div className="mt-2 h-1 bg-[#e8e5e0] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-[#1e3a5f] to-[#3b82f6] rounded-full transition-all duration-500"
                      style={{ width: `${(visibleSteps / STEPS.length) * 100}%` }}
                    />
                  </div>
                </div>
                {STEPS.slice(0, visibleSteps).map((step, i) => (
                  <div key={step.label} className="flex items-center gap-3 px-4 py-2.5 border-b border-[#f0eee9] last:border-0" style={{ animation: "fadeIn 0.3s ease-out" }}>
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold shrink-0 ${
                      i < visibleSteps - 1 ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#1e3a5f] text-white"
                    }`}>
                      {i < visibleSteps - 1 ? "✓" : <span className="animate-pulse">●</span>}
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-[11px] font-medium text-[#1a1a1a]">{step.label}</span>
                      {i < visibleSteps - 1 && <span className="text-[9px] text-[#8a8a8a] font-mono ml-2">{step.detail}</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Review */}
          {phase === "review" && (
            <div>
              {/* Docket text hero — matches real app */}
              <div className="bg-white rounded-xl border-2 border-[#1e3a5f]/20 overflow-hidden shadow-md mb-3">
                <div className="px-4 py-2.5 bg-gradient-to-r from-[#0f1f35] to-[#1e3a5f] flex items-center justify-between">
                  <div>
                    <div className="text-[11px] font-semibold text-white">Docket Text</div>
                    <div className="text-[8px] text-white/40">Edit before filing</div>
                  </div>
                  <span className="text-[8px] px-2 py-0.5 bg-white/10 text-white/60 rounded font-mono border border-white/10">editable</span>
                </div>
                <div className="p-4">
                  <div className="w-full px-3 py-2.5 border border-[#e8e5e0] rounded-lg text-[13px] font-semibold text-[#1a1a1a] bg-[#fafaf8]">
                    Motion to Dismiss for Failure to State a Claim
                  </div>
                </div>
                <div className="px-4 py-2.5 bg-[#fafaf8] border-t border-[#f0eee9]">
                  <div className="text-[8px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1">CM/ECF Docket Preview</div>
                  <div className="text-[10px] text-[#1a1a1a]">
                    <span className="text-[#c4c4c4] font-mono">#--</span>{" "}
                    <span className="font-semibold">Motion to Dismiss for Failure to State a Claim</span>{" "}
                    filed by Jones Corporation (defendant). <span className="text-[#8a8a8a]">(1:24-cv-01234-ABC)</span>
                  </div>
                </div>
              </div>

              {/* Quick info */}
              <div className="grid grid-cols-3 gap-2 mb-3">
                {[
                  { label: "Court", value: "S.D.N.Y.", color: "text-[#1e3a5f]" },
                  { label: "Case", value: "1:24-cv-01234", color: "text-[#1a1a1a]" },
                  { label: "Fee", value: "$0.00", color: "text-[#15803d]" },
                ].map(({ label, value, color }) => (
                  <div key={label} className="bg-white rounded-lg border border-[#e8e5e0] p-2.5">
                    <div className="text-[8px] font-semibold text-[#8a8a8a] uppercase tracking-wide">{label}</div>
                    <div className={`text-[12px] font-bold ${color} font-mono`}>{value}</div>
                  </div>
                ))}
              </div>

              {/* Checks */}
              <div className="bg-white rounded-xl border border-[#e8e5e0] p-3 mb-3">
                {CHECKS.map(({ ok, text }) => (
                  <div key={text} className="flex items-center gap-2 py-1">
                    <div className={`w-4 h-4 rounded-full flex items-center justify-center text-[8px] font-bold ${ok ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#fef2f2] text-[#b91c1c]"}`}>✓</div>
                    <span className="text-[10px] text-[#1a1a1a]">{text}</span>
                  </div>
                ))}
              </div>

              {/* Action bar */}
              <div className="bg-gradient-to-r from-[#0f1f35] to-[#1e3a5f] rounded-xl p-3 flex items-center justify-between">
                <div>
                  <div className="text-[11px] font-bold text-white">Ready to file</div>
                  <div className="text-[8px] text-white/40">SDNY · 1:24-cv-01234 · No fee</div>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={reset} className="px-3 py-1.5 text-[10px] text-white/40 hover:text-white transition border border-white/10 rounded-lg">Cancel</button>
                  <button onClick={reset} className="px-4 py-1.5 bg-white text-[#1e3a5f] text-[10px] font-bold rounded-lg hover:bg-[#f0f4fa] transition shadow">
                    Confirm &amp; File
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }`}</style>
    </div>
  );
}
