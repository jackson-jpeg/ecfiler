"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import Link from "next/link";
import { streamAnalysis, streamBrowser, getHistory, getDrafts, type FilingPreview, type AnalysisStep, type BrowserStep } from "@/lib/api";

type Step = "dashboard" | "analyzing" | "review" | "browser" | "done" | "error";

export default function FilePage() {
  const [step, setStep] = useState<Step>("dashboard");
  const [fileName, setFileName] = useState("");
  const [steps, setSteps] = useState<AnalysisStep[]>([]);
  const [filing, setFiling] = useState<FilingPreview | null>(null);
  const [browserSteps, setBrowserSteps] = useState<BrowserStep[]>([]);
  const [screenshot, setScreenshot] = useState("");
  const [browserDone, setBrowserDone] = useState(false);
  const [browserMsg, setBrowserMsg] = useState("");
  const [error, setError] = useState("");
  const [recentFilings, setRecentFilings] = useState<Record<string, unknown>[]>([]);
  const [drafts, setDrafts] = useState<Record<string, unknown>[]>([]);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    getHistory().then((h) => setRecentFilings(h.slice(0, 5))).catch(() => {});
    getDrafts().then(setDrafts).catch(() => {});
  }, []);

  const reset = () => {
    setStep("dashboard"); setFileName(""); setSteps([]); setFiling(null);
    setBrowserSteps([]); setScreenshot(""); setBrowserDone(false); setError("");
    getHistory().then((h) => setRecentFilings(h.slice(0, 5))).catch(() => {});
  };

  const handleFile = useCallback(async (file: File) => {
    setFileName(file.name); setStep("analyzing"); setSteps([]);
    try {
      for await (const event of streamAnalysis(file)) {
        if (event.type === "step") {
          setSteps((prev) => {
            const existing = prev.find((s) => s.id === event.data.id);
            if (existing) return prev.map((s) => s.id === event.data.id ? { ...s, ...event.data } : s);
            return [...prev, event.data];
          });
        }
        if (event.type === "result") { setFiling(event.data); setTimeout(() => setStep("review"), 300); }
        if (event.type === "error") throw new Error(event.message);
      }
    } catch (e: unknown) { setError(e instanceof Error ? e.message : "Analysis failed"); setStep("error"); }
  }, []);

  const handleConfirm = useCallback(async () => {
    if (!filing) return;
    setStep("browser"); setBrowserSteps([]); setScreenshot(""); setBrowserDone(false);
    try {
      for await (const event of streamBrowser(filing)) {
        if (event.type === "browser") {
          if (event.data.screenshot) setScreenshot(event.data.screenshot);
          setBrowserSteps((prev) => {
            const existing = prev.find((s) => s.step === event.data.step);
            if (existing) return prev.map((s) => s.step === event.data.step ? { ...s, ...event.data } : s);
            return [...prev, event.data];
          });
        }
        if (event.type === "done") { setBrowserDone(true); setBrowserMsg(event.message); }
      }
    } catch (e: unknown) { setBrowserDone(true); setBrowserMsg(e instanceof Error ? e.message : "Failed"); }
  }, [filing]);

  // ========== DASHBOARD ==========
  if (step === "dashboard") {
    return (
      <div className="p-8 lg:p-12">
        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold tracking-tight mb-1">Filing Dashboard</h1>
            <p className="text-[#525252] text-sm">Drop a document to start, or use the tools below.</p>
          </div>
          <div className="flex gap-2">
            <Link href="/validate" className="px-4 py-2 border border-[#e8e5e0] text-[#525252] text-xs font-semibold rounded-lg hover:border-[#d4d0ca] transition">Validate PDF</Link>
            <Link href="/certificate" className="px-4 py-2 border border-[#e8e5e0] text-[#525252] text-xs font-semibold rounded-lg hover:border-[#d4d0ca] transition">Certificate of Service</Link>
          </div>
        </div>

        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Drop zone — takes 2 columns */}
          <div className="lg:col-span-2">
            <div
              className="border-2 border-dashed border-[#e8e5e0] rounded-2xl p-12 text-center cursor-pointer hover:border-blue-300 hover:bg-blue-50/20 transition-all group h-full flex flex-col items-center justify-center min-h-[240px]"
              onClick={() => fileRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add("border-blue-400", "bg-blue-50/30"); }}
              onDragLeave={(e) => { e.currentTarget.classList.remove("border-blue-400", "bg-blue-50/30"); }}
              onDrop={(e) => { e.preventDefault(); e.currentTarget.classList.remove("border-blue-400", "bg-blue-50/30"); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
            >
              <div className="w-14 h-14 bg-[#f5f5f0] group-hover:bg-blue-100 rounded-2xl flex items-center justify-center mb-5 transition">
                <svg className="w-7 h-7 text-[#8a8a8a] group-hover:text-blue-500 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.338-2.32 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
                </svg>
              </div>
              <div className="text-sm font-semibold text-[#1a1a1a] mb-1">Drop your PDF here</div>
              <div className="text-xs text-[#8a8a8a]">or click to browse &middot; AI reads the document and extracts everything</div>
              <input ref={fileRef} type="file" accept=".pdf" className="hidden" onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} />
            </div>
          </div>

          {/* Quick info panel */}
          <div className="space-y-4">
            <div className="bg-white border border-[#e8e5e0] rounded-2xl p-5">
              <div className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-3">How it works</div>
              <div className="space-y-3">
                {[
                  { n: "1", text: "Drop a PDF — any motion, brief, complaint, or notice" },
                  { n: "2", text: "AI extracts case, court, party, event code" },
                  { n: "3", text: "Review and confirm before CM/ECF submission" },
                ].map((s) => (
                  <div key={s.n} className="flex gap-3">
                    <div className="w-5 h-5 bg-[#1e3a5f] text-white rounded-full flex items-center justify-center text-[10px] font-bold shrink-0">{s.n}</div>
                    <div className="text-xs text-[#525252] leading-relaxed">{s.text}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white border border-[#e8e5e0] rounded-2xl p-5">
              <div className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-2">Supported</div>
              <div className="flex flex-wrap gap-1.5">
                {["Motions", "Briefs", "Complaints", "Answers", "Notices", "Stipulations", "Petitions", "Replies"].map((t) => (
                  <span key={t} className="text-[11px] px-2.5 py-1 bg-[#f5f5f0] text-[#525252] rounded-lg font-medium">{t}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Recent filings + Drafts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
          {/* Recent */}
          <div className="bg-white border border-[#e8e5e0] rounded-2xl overflow-hidden">
            <div className="px-5 py-3 border-b border-[#f0eee9] flex items-center justify-between">
              <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Recent Filings</span>
              <Link href="/history" className="text-[11px] text-[#1e3a5f] font-medium hover:underline">View all</Link>
            </div>
            {recentFilings.length > 0 ? (
              <div>
                {recentFilings.map((h, i) => (
                  <div key={i} className="flex items-center justify-between px-5 py-3 border-b border-[#f0eee9] last:border-0">
                    <div className="min-w-0">
                      <div className="text-sm font-medium truncate">{String(h.event_description || "Filing")}</div>
                      <div className="text-xs text-[#8a8a8a] font-mono">{String(h.court_id || "")} &middot; {String(h.case_number || "")}</div>
                    </div>
                    <div className="text-xs text-[#8a8a8a] shrink-0 ml-4">{String(h.filed_at || "").substring(0, 10)}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-[#8a8a8a] text-xs">No filings yet. Drop a PDF above to start.</div>
            )}
          </div>

          {/* Drafts */}
          <div className="bg-white border border-[#e8e5e0] rounded-2xl overflow-hidden">
            <div className="px-5 py-3 border-b border-[#f0eee9] flex items-center justify-between">
              <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Saved Drafts</span>
              <Link href="/drafts" className="text-[11px] text-[#1e3a5f] font-medium hover:underline">View all</Link>
            </div>
            {drafts.length > 0 ? (
              <div>
                {drafts.slice(0, 5).map((d, i) => (
                  <div key={i} className="flex items-center justify-between px-5 py-3 border-b border-[#f0eee9] last:border-0">
                    <div className="min-w-0">
                      <div className="text-sm font-medium truncate">{String(d.name || "Draft")}</div>
                      <div className="text-xs text-[#8a8a8a] font-mono">{String(d.court || "")} &middot; {String(d.case || "")}</div>
                    </div>
                    <div className="text-xs text-[#8a8a8a] shrink-0 ml-4">{String(d.saved_at || "").substring(0, 10)}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-[#8a8a8a] text-xs">No drafts. Cancel a filing to save progress.</div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ========== STEP INDICATOR (for non-dashboard steps) ==========
  const stepMap: Record<string, number> = { analyzing: 1, review: 2, browser: 3, done: 4, error: -1 };
  const currentStep = stepMap[step] ?? 0;

  return (
    <div className="p-8 lg:p-12">
      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-8">
        <button onClick={reset} className="text-xs text-[#8a8a8a] hover:text-[#525252] transition mr-2">&larr; Dashboard</button>
        {["Analyze", "Review", "File"].map((label, i) => {
          const idx = i + 1;
          const isActive = idx === currentStep;
          const isDone = idx < currentStep;
          return (
            <div key={label} className="flex items-center gap-2">
              {i > 0 && <div className={`w-6 h-px ${isDone ? "bg-[#15803d]" : "bg-[#e8e5e0]"}`} />}
              <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold ${
                isDone ? "bg-[#f0fdf4] text-[#15803d]" : isActive ? "bg-[#1e3a5f] text-white" : "bg-[#f5f5f0] text-[#8a8a8a]"
              }`}>
                {isDone ? "✓" : idx}
              </div>
              <span className={`text-xs font-medium ${isActive ? "text-[#1a1a1a]" : isDone ? "text-[#15803d]" : "text-[#8a8a8a]"}`}>{label}</span>
            </div>
          );
        })}
      </div>

      {/* Analyzing */}
      {step === "analyzing" && (
        <div className="max-w-lg">
          <h1 className="text-2xl font-bold tracking-tight mb-2">Analyzing</h1>
          <p className="text-[#525252] text-sm mb-6">Reading <span className="font-mono text-[#1a1a1a]">{fileName}</span></p>
          <div className="bg-white border border-[#e8e5e0] rounded-2xl overflow-hidden">
            {steps.map((s) => (
              <div key={s.id} className="flex items-start gap-3 px-5 py-4 border-b border-[#f0eee9] last:border-0">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold shrink-0 mt-0.5 ${
                  s.status === "done" ? "bg-[#f0fdf4] text-[#15803d]" : s.status === "running" ? "bg-blue-50 text-[#1e3a5f]" : s.status === "warn" ? "bg-[#fffbeb] text-[#b45309]" : "bg-[#fef2f2] text-red-600"
                }`}>
                  {s.status === "done" ? "✓" : s.status === "running" ? <span className="animate-pulse">●</span> : s.status === "warn" ? "!" : "×"}
                </div>
                <div className="min-w-0">
                  <div className="text-sm font-medium">{s.label}</div>
                  {s.detail && <div className="font-mono text-xs text-[#8a8a8a] mt-1 truncate">{s.detail}</div>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Review */}
      {step === "review" && filing && (
        <div className="max-w-2xl">
          <h1 className="text-2xl font-bold tracking-tight mb-2">Review Filing</h1>
          <p className="text-[#525252] text-sm mb-6">Confirm everything below before submitting to CM/ECF.</p>

          {/* Stats row */}
          <div className="grid grid-cols-3 gap-3 mb-6">
            <StatCard label="Extraction" value={`${filing.completeness_score}%`} ok={filing.completeness_score >= 80} />
            <StatCard label="PDF" value={`${filing.pdf_size_mb?.toFixed(1)}MB · ${filing.pdf_pages}p`} ok={filing.pdf_valid} />
            <StatCard label="Redaction" value={filing.redaction_issues === 0 ? "Clean" : `${filing.redaction_issues} issue(s)`} ok={filing.redaction_issues === 0} />
          </div>

          {/* Data */}
          <div className="bg-white border border-[#e8e5e0] rounded-2xl overflow-hidden mb-6">
            <DataRow label="Document" value={filing.document_type} sub={fileName} />
            <DataRow label="Case" value={filing.case_number || "—"} mono />
            <DataRow label="Court" value={filing.court_id?.toUpperCase() || "—"} />
            {filing.case_caption && <DataRow label="Caption" value={filing.case_caption} />}
            <DataRow label="Docket Text" value={filing.event_description} sub={`Event code ${filing.event_code}`} bold />
            {filing.is_response && filing.responds_to && <DataRow label="Response to" value={filing.responds_to} highlight />}
            <DataRow label="Filing Party" value={filing.filing_party || "Not detected"} />
            <DataRow label="Confidence" value={filing.confidence} />
          </div>

          {filing.warnings?.filter(w => !w.includes("certificate")).map((w) => (
            <div key={w} className="flex gap-2 px-4 py-3 bg-[#fffbeb] border border-[#fde68a] rounded-xl text-sm text-[#92400e] mb-3">
              <span className="font-bold shrink-0">!</span> {w}
            </div>
          ))}

          <div className="flex gap-3 mt-6">
            <button onClick={handleConfirm} disabled={!filing.ready} className="px-8 py-3 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] disabled:opacity-20 disabled:cursor-not-allowed transition shadow-sm">
              Confirm &amp; File
            </button>
            <button onClick={reset} className="px-6 py-3 text-sm text-[#525252] hover:text-[#1a1a1a] transition">Cancel</button>
          </div>
        </div>
      )}

      {/* Browser */}
      {step === "browser" && (
        <div className="max-w-2xl">
          <h1 className="text-2xl font-bold tracking-tight mb-2">Filing on CM/ECF</h1>
          <p className="text-[#525252] text-sm mb-6">Navigating the court&apos;s electronic filing system.</p>
          <div className="border border-[#e8e5e0] rounded-2xl overflow-hidden mb-6 shadow-lg shadow-[#e8e5e0]/50">
            <div className="bg-[#f5f5f0] px-4 py-2 flex items-center gap-2 border-b border-[#e8e5e0]">
              <div className="flex gap-1.5"><div className="w-3 h-3 rounded-full bg-[#d4d0ca]"/><div className="w-3 h-3 rounded-full bg-[#d4d0ca]"/><div className="w-3 h-3 rounded-full bg-[#d4d0ca]"/></div>
              <div className="flex-1 text-center font-mono text-[11px] text-[#8a8a8a]">ecf.{filing?.court_id || "nysd"}.uscourts.gov</div>
              {!browserDone && <span className="text-[10px] text-[#1e3a5f] font-semibold animate-pulse">LIVE</span>}
            </div>
            <div className="bg-[#fafaf8] min-h-[300px] flex items-center justify-center">
              {screenshot ? <img src={`data:image/png;base64,${screenshot}`} className="w-full" alt="CM/ECF" /> : <span className="text-sm text-[#8a8a8a]">Connecting...</span>}
            </div>
          </div>
          <div className="bg-white border border-[#e8e5e0] rounded-2xl overflow-hidden mb-6">
            {browserSteps.map((s) => (
              <div key={s.step} className="flex items-start gap-3 px-5 py-3 border-b border-[#f0eee9] last:border-0">
                <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5 ${s.status === "done" ? "bg-[#f0fdf4] text-[#15803d]" : "bg-blue-50 text-[#1e3a5f]"}`}>
                  {s.status === "done" ? "✓" : <span className="animate-pulse">●</span>}
                </div>
                <div><div className="text-xs font-semibold">{s.step}</div><div className="text-xs text-[#8a8a8a]">{s.description}</div></div>
              </div>
            ))}
          </div>
          {browserDone && (
            <div className="flex items-center gap-3">
              <button onClick={reset} className="px-6 py-2.5 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] transition shadow-sm">Done</button>
              <span className="text-sm text-[#525252]">{browserMsg}</span>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {step === "error" && (
        <div className="max-w-md">
          <div className="w-12 h-12 bg-[#fef2f2] rounded-2xl flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-[#b91c1c]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
          </div>
          <h1 className="text-xl font-bold mb-2">Something went wrong</h1>
          <p className="text-sm text-[#525252] mb-6">{error}</p>
          <button onClick={reset} className="px-6 py-2.5 bg-[#1e3a5f] text-white text-sm font-semibold rounded-xl hover:bg-[#162a47] transition">Try Again</button>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return (
    <div className={`rounded-2xl border p-4 ${ok ? "border-green-200 bg-[#f0fdf4]/50" : "border-[#fde68a] bg-[#fffbeb]/50"}`}>
      <div className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1">{label}</div>
      <div className={`text-lg font-bold ${ok ? "text-[#15803d]" : "text-amber-700"}`}>{value}</div>
    </div>
  );
}

function DataRow({ label, value, sub, mono, bold, highlight }: { label: string; value: string; sub?: string; mono?: boolean; bold?: boolean; highlight?: boolean }) {
  return (
    <div className={`flex px-5 py-3.5 border-b border-[#f0eee9] last:border-0 ${highlight ? "bg-blue-50/50" : ""}`}>
      <div className="w-28 shrink-0 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide pt-0.5">{label}</div>
      <div className="min-w-0">
        <div className={`text-sm ${bold ? "font-semibold" : ""} ${mono ? "font-mono" : ""}`}>{value}</div>
        {sub && <div className="text-xs text-[#8a8a8a] font-mono mt-0.5">{sub}</div>}
      </div>
    </div>
  );
}
