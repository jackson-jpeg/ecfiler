"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import Link from "next/link";
import { UserButton } from "@clerk/nextjs";
import { streamAnalysis, streamBrowser, getHistory, type FilingPreview, type AnalysisStep, type BrowserStep } from "@/lib/api";

type Phase = "ready" | "analyzing" | "review" | "filing" | "done" | "error";

interface Exhibit {
  id: string;
  file: File;
  label: string;
  description: string;
}

const EXHIBIT_LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

export default function WorkspacePage() {
  const [phase, setPhase] = useState<Phase>("ready");
  const [fileName, setFileName] = useState("");
  const [steps, setSteps] = useState<AnalysisStep[]>([]);
  const [filing, setFiling] = useState<FilingPreview | null>(null);
  const [browserSteps, setBrowserSteps] = useState<BrowserStep[]>([]);
  const [screenshot, setScreenshot] = useState("");
  const [browserDone, setBrowserDone] = useState(false);
  const [browserMsg, setBrowserMsg] = useState("");
  const [error, setError] = useState("");
  const [history, setHistory] = useState<Record<string, unknown>[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showCourts, setShowCourts] = useState(false);
  const [docketText, setDocketText] = useState("");
  const [isSealed, setIsSealed] = useState(false);
  const [isRedacted, setIsRedacted] = useState(false);
  const [exhibits, setExhibits] = useState<Exhibit[]>([]);
  const [showCertService, setShowCertService] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const exhibitRef = useRef<HTMLInputElement>(null);

  useEffect(() => { getHistory().then((h) => setHistory(h.slice(0, 10))).catch(() => {}); }, []);

  const reset = () => {
    setPhase("ready"); setFileName(""); setSteps([]); setFiling(null);
    setBrowserSteps([]); setScreenshot(""); setBrowserDone(false); setError("");
    setExhibits([]); setIsSealed(false); setIsRedacted(false); setDocketText(""); setShowCertService(false);
    getHistory().then((h) => setHistory(h.slice(0, 10))).catch(() => {});
  };

  const addExhibits = useCallback((files: FileList) => {
    setExhibits((prev) => {
      const newExhibits: Exhibit[] = Array.from(files).map((f, i) => ({
        id: `${Date.now()}-${i}`,
        file: f,
        label: `Exhibit ${EXHIBIT_LABELS[prev.length + i] || String(prev.length + i + 1)}`,
        description: f.name.replace(/\.pdf$/i, "").replace(/[_-]/g, " "),
      }));
      return [...prev, ...newExhibits];
    });
  }, []);

  const removeExhibit = useCallback((id: string) => {
    setExhibits((prev) => {
      const filtered = prev.filter((e) => e.id !== id);
      return filtered.map((e, i) => ({ ...e, label: `Exhibit ${EXHIBIT_LABELS[i] || String(i + 1)}` }));
    });
  }, []);

  const updateExhibitDesc = useCallback((id: string, description: string) => {
    setExhibits((prev) => prev.map((e) => e.id === id ? { ...e, description } : e));
  }, []);

  const handleFile = useCallback(async (file: File) => {
    setFileName(file.name); setPhase("analyzing"); setSteps([]);
    try {
      for await (const event of streamAnalysis(file)) {
        if (event.type === "step") setSteps((prev) => { const ex = prev.find((s) => s.id === event.data.id); if (ex) return prev.map((s) => s.id === event.data.id ? { ...s, ...event.data } : s); return [...prev, event.data]; });
        if (event.type === "result") { 
          setFiling(event.data); 
          setDocketText(event.data.event_description || ""); 
          setTimeout(() => setPhase("review"), 300); 
        }
        if (event.type === "error") throw new Error(event.message);
      }
    } catch (e: unknown) { setError(e instanceof Error ? e.message : "Failed"); setPhase("error"); }
  }, []);

  const handleConfirm = useCallback(async () => {
    if (!filing) return;
    setPhase("filing"); setBrowserSteps([]); setScreenshot(""); setBrowserDone(false);
    try {
      for await (const event of streamBrowser(filing)) {
        if (event.type === "browser") { if (event.data.screenshot) setScreenshot(event.data.screenshot); setBrowserSteps((prev) => { const ex = prev.find((s) => s.step === event.data.step); if (ex) return prev.map((s) => s.step === event.data.step ? { ...s, ...event.data } : s); return [...prev, event.data]; }); }
        if (event.type === "done") { setBrowserDone(true); setBrowserMsg(event.message); }
      }
    } catch (e: unknown) { setBrowserDone(true); setBrowserMsg(e instanceof Error ? e.message : "Failed"); }
  }, [filing]);

  // Keyboard shortcut: Cmd+Enter to file
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter" && phase === "review" && filing?.ready) {
        e.preventDefault();
        handleConfirm();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [phase, filing, handleConfirm]);

  return (
    <div className="min-h-screen bg-[#f5f3ee]">
      {/* Top bar */}
      <header className="bg-white border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3 sm:gap-6">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-7 h-7 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[10px] font-bold">E</div>
              <span className="text-[15px] font-semibold tracking-tight text-[#1a1a1a] hidden sm:inline">ECFiler</span>
            </Link>
            <div className="h-5 w-px bg-[#e8e5e0]" />
            <button onClick={() => setShowHistory(!showHistory)} className="text-[13px] text-[#525252] hover:text-[#1a1a1a] transition font-medium">
              History {history.length > 0 && <span className="text-[10px] bg-[#f0eee9] px-1.5 py-0.5 rounded-full ml-1">{history.length}</span>}
            </button>
            <button onClick={() => setShowCourts(!showCourts)} className="text-[13px] text-[#525252] hover:text-[#1a1a1a] transition font-medium">Courts</button>
          </div>
          <div className="flex items-center gap-3 sm:gap-4">
            <Link href="/settings" className="text-[13px] text-[#8a8a8a] hover:text-[#525252] transition hidden sm:inline">Settings</Link>
            <UserButton appearance={{ elements: { avatarBox: "w-7 h-7" } }} />
          </div>
        </div>
      </header>

      {/* Main workspace */}
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 sm:py-10">

        {/* Ready state */}
        {phase === "ready" && (
          <div>
            {/* Two-column layout */}
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-8">
              {/* Drop zone — 3 cols */}
              <div className="lg:col-span-3">
                <div
                  className="bg-white border border-[#d4d0ca] rounded-2xl p-10 text-center cursor-pointer hover:border-[#1e3a5f] hover:shadow-lg hover:shadow-[#1e3a5f]/5 transition-all group h-full flex flex-col items-center justify-center min-h-[260px] shadow-sm"
                  onClick={() => fileRef.current?.click()}
                  onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add("!border-[#1e3a5f]", "!bg-[#f0f4fa]", "!shadow-lg"); }}
                  onDragLeave={(e) => { e.currentTarget.classList.remove("!border-[#1e3a5f]", "!bg-[#f0f4fa]", "!shadow-lg"); }}
                  onDrop={(e) => {
                    e.preventDefault(); e.currentTarget.classList.remove("!border-[#1e3a5f]", "!bg-[#f0f4fa]", "!shadow-lg");
                    const files = Array.from(e.dataTransfer.files).filter(f => f.type === "application/pdf" || f.name.endsWith(".pdf"));
                    if (files.length === 0) return;
                    handleFile(files[0]);
                    if (files.length > 1) {
                      const exhibitFiles = new DataTransfer();
                      files.slice(1).forEach(f => exhibitFiles.items.add(f));
                      addExhibits(exhibitFiles.files);
                    }
                  }}
                >
                  <div className="w-14 h-14 bg-[#f0eee9] group-hover:bg-[#dbeafe] rounded-2xl flex items-center justify-center mx-auto mb-4 transition">
                    <svg className="w-7 h-7 text-[#8a8a8a] group-hover:text-[#1e3a5f] transition" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.338-2.32 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
                    </svg>
                  </div>
                  <div className="text-[15px] font-semibold text-[#1a1a1a] mb-1">Drop your PDF here</div>
                  <div className="text-[13px] text-[#8a8a8a] mb-4">or click to browse &middot; drop multiple for exhibits</div>
                  <div className="flex flex-wrap justify-center gap-1.5">
                    {["Motions", "Briefs", "Complaints", "Notices", "Petitions", "Exhibits"].map((t) => (
                      <span key={t} className="text-[10px] px-2 py-0.5 bg-[#f0eee9] text-[#8a8a8a] rounded-md font-medium">{t}</span>
                    ))}
                  </div>
                  <input ref={fileRef} type="file" accept=".pdf" multiple className="hidden" onChange={(e) => {
                    if (!e.target.files?.length) return;
                    handleFile(e.target.files[0]);
                    if (e.target.files.length > 1) {
                      const rest = new DataTransfer();
                      Array.from(e.target.files).slice(1).forEach(f => rest.items.add(f));
                      addExhibits(rest.files);
                    }
                  }} />
                </div>
              </div>

              {/* Right panel — 2 cols */}
              <div className="lg:col-span-2 space-y-4">
                {/* Stats */}
                <div className="bg-white border border-[#e8e5e0] rounded-2xl p-5 shadow-sm">
                  <div className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-3">Your Activity</div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-[#f5f3ee] rounded-xl p-3 text-center">
                      <div className="text-[22px] font-bold text-[#1e3a5f]">{history.length}</div>
                      <div className="text-[10px] text-[#8a8a8a] font-medium">Filings</div>
                    </div>
                    <div className="bg-[#f5f3ee] rounded-xl p-3 text-center">
                      <div className="text-[22px] font-bold text-[#1e3a5f]">207</div>
                      <div className="text-[10px] text-[#8a8a8a] font-medium">Courts</div>
                    </div>
                  </div>
                </div>

                {/* How it works */}
                <div className="bg-white border border-[#e8e5e0] rounded-2xl p-5 shadow-sm">
                  <div className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-3">How It Works</div>
                  <div className="space-y-3">
                    {[
                      { n: "1", text: "Drop a PDF — motion, brief, complaint, or any filing" },
                      { n: "2", text: "AI extracts case, court, event code, and party" },
                      { n: "3", text: "Review verification checks and confirm" },
                    ].map((s) => (
                      <div key={s.n} className="flex gap-3">
                        <div className="w-5 h-5 bg-[#1e3a5f] text-white rounded-full flex items-center justify-center text-[9px] font-bold shrink-0 mt-0.5">{s.n}</div>
                        <div className="text-[12px] text-[#525252] leading-relaxed">{s.text}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Quick links */}
                <div className="bg-white border border-[#e8e5e0] rounded-2xl p-5 shadow-sm">
                  <div className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-3">Quick Actions</div>
                  <div className="space-y-1.5">
                    <button onClick={() => setShowCourts(true)} className="w-full text-left px-3 py-2 rounded-lg text-[12px] text-[#525252] hover:bg-[#f5f3ee] hover:text-[#1a1a1a] transition flex items-center gap-2">
                      <span className="text-[#8a8a8a]">🏛</span> Search courts
                    </button>
                    <Link href="/settings" className="block px-3 py-2 rounded-lg text-[12px] text-[#525252] hover:bg-[#f5f3ee] hover:text-[#1a1a1a] transition flex items-center gap-2">
                      <span className="text-[#8a8a8a]">⚙</span> PACER credentials
                    </Link>
                    <button onClick={() => setShowHistory(true)} className="w-full text-left px-3 py-2 rounded-lg text-[12px] text-[#525252] hover:bg-[#f5f3ee] hover:text-[#1a1a1a] transition flex items-center gap-2">
                      <span className="text-[#8a8a8a]">📋</span> Filing history
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent filings — full width */}
            {history.length > 0 && (
              <div className="bg-white rounded-2xl border border-[#e8e5e0] overflow-hidden shadow-sm">
                <div className="px-5 py-3 border-b border-[#f0eee9] flex items-center justify-between">
                  <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Recent Filings</span>
                  <button onClick={() => setShowHistory(true)} className="text-[11px] text-[#1e3a5f] font-medium hover:underline">View all</button>
                </div>
                {history.slice(0, 5).map((h, i) => (
                  <div key={i} className="flex items-center justify-between px-5 py-3 border-b border-[#f0eee9] last:border-0 hover:bg-[#fafaf8] transition">
                    <div>
                      <div className="text-[13px] font-medium text-[#1a1a1a]">{String(h.event_description || "Filing")}</div>
                      <div className="text-[11px] text-[#8a8a8a] font-mono">{String(h.court_id || "")} &middot; {String(h.case_number || "")}</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] px-2 py-0.5 bg-[#f0fdf4] text-[#15803d] rounded-full font-semibold">{String(h.status || "filed")}</span>
                      <span className="text-[11px] text-[#c4c4c4]">{String(h.filed_at || "").substring(0, 10)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Analyzing */}
        {phase === "analyzing" && (
          <div className="max-w-xl mx-auto">
            <div className="flex items-center justify-between mb-6">
              <button onClick={reset} className="text-[13px] text-[#8a8a8a] hover:text-[#525252] transition">&larr; Cancel</button>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-[#1e3a5f] rounded-full animate-pulse" />
                <span className="text-[12px] font-medium text-[#1e3a5f]">Processing</span>
              </div>
            </div>

            <div className="bg-white rounded-2xl border border-[#e8e5e0] overflow-hidden shadow-lg shadow-black/5">
              <div className="px-6 py-4 border-b border-[#f0eee9] bg-[#fafaf8]">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-[16px] font-bold text-[#1a1a1a]">Analyzing Document</div>
                    <div className="text-[12px] text-[#8a8a8a] font-mono mt-0.5">{fileName}</div>
                  </div>
                  <div className="text-[11px] text-[#8a8a8a] font-medium">{steps.filter(s => s.status === "done").length}/{steps.length || "..."} steps</div>
                </div>
                {/* Progress bar */}
                <div className="mt-3 h-1 bg-[#e8e5e0] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-[#1e3a5f] to-[#3b82f6] rounded-full transition-all duration-500"
                    style={{ width: steps.length ? `${(steps.filter(s => s.status === "done").length / Math.max(steps.length, 6)) * 100}%` : "5%" }}
                  />
                </div>
              </div>
              <div className="px-6 py-4">
                {steps.map((s, i) => (
                  <div key={s.id} className="flex items-start gap-4 py-3 border-b border-[#f0eee9] last:border-0">
                    <div className="relative">
                      <div className={`w-8 h-8 rounded-xl flex items-center justify-center text-[12px] font-bold transition-all ${
                        s.status === "done" ? "bg-[#f0fdf4] text-[#15803d] shadow-sm shadow-green-200/50" :
                        s.status === "running" ? "bg-[#1e3a5f] text-white shadow-md shadow-[#1e3a5f]/30" :
                        s.status === "warn" ? "bg-[#fffbeb] text-[#b45309]" : "bg-[#fef2f2] text-[#b91c1c]"
                      }`}>
                        {s.status === "done" ? "✓" : s.status === "running" ? <span className="animate-pulse">●</span> : s.status === "warn" ? "!" : "×"}
                      </div>
                      {i < steps.length - 1 && <div className={`absolute left-1/2 top-full w-px h-3 -translate-x-1/2 ${s.status === "done" ? "bg-[#bbf7d0]" : "bg-[#e8e5e0]"}`} />}
                    </div>
                    <div className="pt-1">
                      <div className={`text-[14px] font-semibold ${s.status === "running" ? "text-[#1e3a5f]" : "text-[#1a1a1a]"}`}>{s.label}</div>
                      {s.detail && <div className="font-mono text-[12px] text-[#8a8a8a] mt-1">{s.detail}</div>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Review */}
        {phase === "review" && filing && (
          <div>
            <button onClick={reset} className="text-[13px] text-[#8a8a8a] hover:text-[#525252] transition mb-6">&larr; Start over</button>

            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-[20px] font-bold text-[#1a1a1a]">Review Filing</h2>
                <p className="text-[13px] text-[#525252]">Confirm everything before submitting to CM/ECF.</p>
              </div>
              <span className={`text-[12px] px-3 py-1 rounded-full font-semibold border ${
                filing.completeness_score >= 80 ? "bg-[#f0fdf4] text-[#15803d] border-[#bbf7d0]" : "bg-[#fffbeb] text-[#b45309] border-[#fde68a]"
              }`}>{filing.completeness_score}% extracted</span>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
              {[
                { label: "PDF", value: `${filing.pdf_size_mb?.toFixed(1)}MB · ${filing.pdf_pages}p${filing.pdf_is_pdfa ? " · PDF/A" : ""}`, ok: filing.pdf_valid },
                { label: "Redaction", value: filing.redaction_issues === 0 ? "Clean" : `${filing.redaction_issues} issue(s)`, ok: filing.redaction_issues === 0 },
                { label: "Fee", value: filing.filing_fee_text || (filing.filing_fee ? `$${filing.filing_fee}` : "None"), ok: true },
                { label: "Confidence", value: filing.confidence || "High", ok: filing.completeness_score >= 80 },
              ].map(({ label, value, ok }) => (
                <div key={label} className={`rounded-xl border p-4 ${ok ? "bg-[#f0fdf4] border-[#bbf7d0]" : "bg-[#fffbeb] border-[#fde68a]"}`}>
                  <div className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1">{label}</div>
                  <div className={`text-[15px] font-bold ${ok ? "text-[#15803d]" : "text-[#b45309]"}`}>{value}</div>
                </div>
              ))}
            </div>

            {/* Court-specific notices */}
            {filing.court_id && ["nysd", "edny", "sdny"].includes(filing.court_id.toLowerCase()) && !filing.pdf_is_pdfa && (
              <div className="flex items-start gap-3 px-4 py-3 bg-[#f0f4fa] border border-[#bfdbfe] rounded-xl text-[12px] text-[#1e40af] mb-5">
                <svg className="w-4 h-4 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
                </svg>
                <div>
                  <span className="font-semibold">{filing.court_id.toUpperCase()} requires PDF/A format.</span>{" "}
                  Your document is not PDF/A — ECFiler will automatically convert it before filing.
                </div>
              </div>
            )}
            {filing.court_id && ["nysd", "edny", "sdny"].includes(filing.court_id.toLowerCase()) && filing.pdf_is_pdfa && (
              <div className="flex items-start gap-3 px-4 py-3 bg-[#f0fdf4] border border-[#bbf7d0] rounded-xl text-[12px] text-[#15803d] mb-5">
                <svg className="w-4 h-4 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <span className="font-semibold">PDF/A compliant.</span>{" "}
                  Your document meets {filing.court_id.toUpperCase()}&apos;s PDF/A requirement.
                </div>
              </div>
            )}

            {/* Filing details */}
            <div className="bg-white rounded-2xl border border-[#e8e5e0] overflow-hidden shadow-sm mb-5">
              {[
                { label: "Document", value: filing.document_type, sub: fileName },
                { label: "Case", value: filing.case_number || "—", mono: true },
                { label: "Court", value: filing.court_id?.toUpperCase() || "—" },
                { label: "Caption", value: filing.case_caption || "" },
                ...(filing.is_response && filing.responds_to ? [{ label: "Response to", value: filing.responds_to, sub: filing.responds_to_docket ? `Docket #${filing.responds_to_docket}` : undefined, highlight: true }] : []),
                { label: "Filing Party", value: filing.filing_party || "Not detected" },
                ...(filing.attorney_name ? [{ label: "Attorney", value: filing.attorney_name, sub: filing.attorney_firm || undefined }] : []),
                { label: "Event Code", value: filing.event_code, mono: true },
              ].filter(f => f.value).map(({ label, value, sub, mono, highlight }) => (
                <div key={label} className={`flex px-5 py-3.5 border-b border-[#f0eee9] last:border-0 ${highlight ? "bg-[#f0f4fa]" : ""}`}>
                  <div className="w-[110px] shrink-0 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide pt-0.5">{label}</div>
                  <div className={`text-[14px] ${mono ? "font-mono" : ""} text-[#1a1a1a]`}>
                    {value}
                    {sub && <div className="text-[11px] text-[#8a8a8a] font-mono mt-0.5">{sub}</div>}
                  </div>
                </div>
              ))}
            </div>

            {/* Docket Text — the hero of the review screen */}
            <div className="bg-white rounded-2xl border-2 border-[#1e3a5f]/20 overflow-hidden shadow-lg shadow-[#1e3a5f]/5 mb-5">
              <div className="px-6 py-4 bg-gradient-to-r from-[#0f1f35] to-[#1e3a5f] flex items-center justify-between">
                <div>
                  <div className="text-[13px] font-semibold text-white">Docket Text</div>
                  <div className="text-[11px] text-white/50 mt-0.5">This is exactly what appears on the court docket — edit before filing</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] px-2.5 py-1 bg-white/10 text-white/70 rounded-md font-mono border border-white/10">editable</span>
                </div>
              </div>
              <div className="p-6">
                <textarea
                  value={docketText}
                  onChange={(e) => setDocketText(e.target.value)}
                  rows={3}
                  className="w-full px-5 py-4 border border-[#e8e5e0] rounded-xl text-[16px] font-semibold text-[#1a1a1a] outline-none focus:border-[#1e3a5f] focus:ring-2 focus:ring-[#1e3a5f]/10 resize-none bg-[#fafaf8] leading-relaxed"
                  placeholder="Enter docket text..."
                />
                <div className="flex items-center justify-between mt-4">
                  <div className="flex items-center gap-3">
                    <button onClick={() => setDocketText(filing.event_description)} className="text-[12px] px-3 py-1.5 bg-[#f0f4fa] text-[#1e3a5f] font-medium rounded-lg hover:bg-[#dbeafe] transition border border-[#1e3a5f]/10">
                      Reset to AI suggestion
                    </button>
                    {filing.is_response && filing.responds_to && (
                      <span className="text-[11px] text-[#8a8a8a] bg-[#f5f3ee] px-2.5 py-1 rounded-md">
                        In response to: <span className="font-mono font-medium text-[#525252]">{filing.responds_to}</span>
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-[#c4c4c4]">{docketText.length} chars</div>
                </div>
              </div>
              {/* Live preview */}
              <div className="px-6 py-4 bg-[#fafaf8] border-t border-[#f0eee9]">
                <div className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-2">CM/ECF Docket Preview</div>
                <div className="flex items-start gap-3">
                  <div className="text-[12px] font-mono text-[#c4c4c4] shrink-0 pt-0.5">#--</div>
                  <div>
                    <div className="text-[13px] text-[#1a1a1a]">
                      <span className="font-semibold">{docketText || "..."}</span>
                      {" "}filed by {filing.filing_party || "Unknown"}.
                      {filing.case_number && <span className="text-[#8a8a8a]"> ({filing.case_number})</span>}
                    </div>
                    <div className="text-[11px] text-[#8a8a8a] mt-0.5">
                      {exhibits.length > 0
                        ? `(Attachments: ${exhibits.map((_, i) => `# ${i + 1} ${exhibits[i].label}`).join(", ")})`
                        : "(Attachments: # 1)"}
                      {isSealed ? " (SEALED)" : ""}{isRedacted ? " (REDACTED)" : ""}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Filing options */}
            <div className="bg-white rounded-2xl border border-[#e8e5e0] overflow-hidden shadow-sm mb-5">
              <div className="px-5 py-3 border-b border-[#f0eee9]">
                <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Filing Options</span>
              </div>
              <div className="p-5 space-y-3">
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition ${isSealed ? "bg-[#1e3a5f] border-[#1e3a5f]" : "border-[#d4d0ca] group-hover:border-[#8a8a8a]"}`}>
                    {isSealed && <span className="text-white text-[10px] font-bold">✓</span>}
                  </div>
                  <input type="checkbox" checked={isSealed} onChange={(e) => setIsSealed(e.target.checked)} className="hidden" />
                  <div>
                    <div className="text-[13px] font-medium text-[#1a1a1a]">File under seal</div>
                    <div className="text-[11px] text-[#8a8a8a]">Document will not be publicly accessible on CM/ECF</div>
                  </div>
                </label>
                <label className="flex items-center gap-3 cursor-pointer group">
                  <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition ${isRedacted ? "bg-[#1e3a5f] border-[#1e3a5f]" : "border-[#d4d0ca] group-hover:border-[#8a8a8a]"}`}>
                    {isRedacted && <span className="text-white text-[10px] font-bold">✓</span>}
                  </div>
                  <input type="checkbox" checked={isRedacted} onChange={(e) => setIsRedacted(e.target.checked)} className="hidden" />
                  <div>
                    <div className="text-[13px] font-medium text-[#1a1a1a]">Redacted version filed</div>
                    <div className="text-[11px] text-[#8a8a8a]">This is the publicly-available redacted version per Rule 5.2</div>
                  </div>
                </label>
              </div>
            </div>

            {/* Exhibits & Attachments */}
            <div className="bg-white rounded-2xl border border-[#e8e5e0] overflow-hidden shadow-sm mb-5">
              <div className="px-5 py-3 border-b border-[#f0eee9] flex items-center justify-between">
                <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Attachments &amp; Exhibits</span>
                <button onClick={() => exhibitRef.current?.click()} className="text-[11px] text-[#1e3a5f] font-semibold hover:underline">+ Add files</button>
              </div>
              <input ref={exhibitRef} type="file" accept=".pdf" multiple className="hidden" onChange={(e) => e.target.files && addExhibits(e.target.files)} />
              {exhibits.length === 0 ? (
                <div
                  className="px-5 py-8 text-center cursor-pointer hover:bg-[#fafaf8] transition border-2 border-dashed border-transparent hover:border-[#e8e5e0] mx-4 my-4 rounded-xl"
                  onClick={() => exhibitRef.current?.click()}
                  onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add("!border-[#1e3a5f]", "!bg-[#f0f4fa]"); }}
                  onDragLeave={(e) => { e.currentTarget.classList.remove("!border-[#1e3a5f]", "!bg-[#f0f4fa]"); }}
                  onDrop={(e) => { e.preventDefault(); e.currentTarget.classList.remove("!border-[#1e3a5f]", "!bg-[#f0f4fa]"); if (e.dataTransfer.files.length) addExhibits(e.dataTransfer.files); }}
                >
                  <div className="text-[13px] text-[#8a8a8a]">Drop exhibits here or click to browse</div>
                  <div className="text-[11px] text-[#c4c4c4] mt-1">Auto-labeled as Exhibit A, B, C...</div>
                </div>
              ) : (
                <div className="p-4 space-y-2">
                  {exhibits.map((ex) => (
                    <div key={ex.id} className="flex items-center gap-3 p-3 bg-[#fafaf8] rounded-xl border border-[#f0eee9] group">
                      <div className="w-9 h-9 bg-[#1e3a5f] text-white rounded-lg flex items-center justify-center text-[11px] font-bold shrink-0">{ex.label.split(" ")[1]}</div>
                      <div className="flex-1 min-w-0">
                        <input
                          type="text"
                          value={ex.description}
                          onChange={(e) => updateExhibitDesc(ex.id, e.target.value)}
                          className="w-full text-[13px] font-medium text-[#1a1a1a] bg-transparent outline-none border-b border-transparent focus:border-[#1e3a5f] transition pb-0.5"
                          placeholder="Description..."
                        />
                        <div className="text-[10px] text-[#8a8a8a] font-mono mt-0.5">{ex.file.name} &middot; {(ex.file.size / 1024 / 1024).toFixed(1)}MB</div>
                      </div>
                      <button onClick={() => removeExhibit(ex.id)} className="text-[#c4c4c4] hover:text-[#b91c1c] transition opacity-0 group-hover:opacity-100 text-lg shrink-0">&times;</button>
                    </div>
                  ))}
                  <button onClick={() => exhibitRef.current?.click()} className="w-full py-2.5 border border-dashed border-[#d4d0ca] rounded-xl text-[12px] text-[#8a8a8a] hover:text-[#1e3a5f] hover:border-[#1e3a5f] transition">+ Add more exhibits</button>
                </div>
              )}
            </div>

            {/* Certificate of Service */}
            <div className="bg-white rounded-2xl border border-[#e8e5e0] overflow-hidden shadow-sm mb-5">
              <div className="px-5 py-3 border-b border-[#f0eee9] flex items-center justify-between">
                <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Certificate of Service</span>
                <label className="flex items-center gap-2 cursor-pointer">
                  <div className={`relative w-9 h-5 rounded-full transition ${showCertService ? "bg-[#1e3a5f]" : "bg-[#d4d0ca]"}`}>
                    <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-all ${showCertService ? "left-[18px]" : "left-0.5"}`} />
                  </div>
                  <input type="checkbox" checked={showCertService} onChange={(e) => setShowCertService(e.target.checked)} className="hidden" />
                  <span className="text-[12px] text-[#525252] font-medium">{showCertService ? "Included" : "Not included"}</span>
                </label>
              </div>
              {showCertService && (
                <div className="px-5 py-4">
                  <div className="bg-[#fafaf8] border border-[#f0eee9] rounded-xl p-4">
                    <div className="text-[11px] text-[#8a8a8a] font-medium mb-2">Auto-generated certificate</div>
                    <div className="text-[12px] text-[#525252] leading-relaxed font-serif italic">
                      I hereby certify that on {new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })},
                      I electronically filed the foregoing {docketText || filing.event_description} with the Clerk of Court
                      using the CM/ECF system, which will send notification of such filing to all counsel of record.
                    </div>
                  </div>
                  <div className="text-[10px] text-[#c4c4c4] mt-2">Will be appended as the final page of the filing</div>
                </div>
              )}
            </div>

            {/* Verification */}
            <div className="bg-white rounded-xl border border-[#e8e5e0] overflow-hidden shadow-sm mb-5">
              <div className="px-5 py-3 border-b border-[#f0eee9]">
                <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Verification</span>
              </div>
              <div className="px-5 py-3 space-y-2">
                {[
                  { ok: filing.pdf_valid, text: `PDF valid — ${filing.pdf_size_mb?.toFixed(1)}MB, ${filing.pdf_pages} pages${filing.pdf_is_pdfa ? ", PDF/A" : ""}` },
                  { ok: filing.redaction_issues === 0, text: filing.redaction_issues === 0 ? "No unredacted identifiers (Rule 5.2)" : `${filing.redaction_issues} redaction issue(s)`, warn: filing.redaction_issues > 0 },
                  ...(filing.case_number ? [{ ok: true, text: `Case ${filing.case_number} matches PDF` }] : []),
                  ...(filing.event_code ? [{ ok: true, text: `Event code ${filing.event_code} matches document type` }] : []),
                  { ok: filing.has_certificate_of_service !== false, text: filing.has_certificate_of_service ? "Certificate of service present" : "No certificate of service detected", warn: !filing.has_certificate_of_service },
                  ...(filing.has_proposed_order ? [{ ok: true, text: "Proposed order detected" }] : []),
                  ...(filing.attorney_name ? [{ ok: true, text: `Signed by ${filing.attorney_name}` }] : [{ ok: false, text: "No signature block detected", warn: true }]),
                ].map(({ ok, text, warn }) => (
                  <div key={text} className="flex items-center gap-2.5">
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${warn ? "bg-[#fffbeb] text-[#b45309]" : ok ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#fef2f2] text-[#b91c1c]"}`}>
                      {warn ? "!" : ok ? "✓" : "×"}
                    </div>
                    <span className="text-[13px] text-[#1a1a1a]">{text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Warnings */}
            {filing.warnings?.filter(w => !w.includes("certificate")).map((w) => (
              <div key={w} className="flex gap-2 px-4 py-3 bg-[#fffbeb] border border-[#fde68a] rounded-xl text-[13px] text-[#92400e] mb-3">
                <span className="font-bold">!</span> {w}
              </div>
            ))}

            {/* Actions */}
            <div className="bg-gradient-to-r from-[#0f1f35] to-[#1e3a5f] rounded-2xl p-6 shadow-xl shadow-[#1e3a5f]/15">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-[14px] font-bold text-white">{filing.ready ? "Ready to file" : "Missing required fields"}</div>
                  <div className="text-[12px] text-white/50 mt-0.5">
                    {filing.ready
                      ? `${filing.court_id?.toUpperCase()} · ${filing.case_number}${exhibits.length > 0 ? ` · ${exhibits.length} attachment${exhibits.length > 1 ? "s" : ""}` : ""}${filing.filing_fee ? ` · $${filing.filing_fee} fee` : ""}`
                      : "Review the issues above."}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <button onClick={reset} className="px-5 py-2.5 text-[13px] text-white/50 hover:text-white transition border border-white/10 rounded-xl hover:bg-white/5">Cancel</button>
                  <button onClick={handleConfirm} disabled={!filing.ready} className="px-8 py-3 bg-white text-[#1e3a5f] text-[14px] font-bold rounded-xl hover:bg-[#f0f4fa] disabled:opacity-20 disabled:cursor-not-allowed transition shadow-lg">
                    Confirm &amp; File
                  </button>
                </div>
              </div>
              {filing.ready && (
                <div className="mt-3 flex items-center gap-2 text-[10px] text-white/30">
                  <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-white/40 font-mono border border-white/10">⌘</kbd>
                  <span>+</span>
                  <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-white/40 font-mono border border-white/10">Enter</kbd>
                  <span>to file</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Filing — browser view */}
        {phase === "filing" && (
          <div>
            <h2 className="text-[20px] font-bold text-[#1a1a1a] mb-1">Filing on CM/ECF</h2>
            <p className="text-[13px] text-[#525252] mb-5">Navigating the court&apos;s filing system.</p>

            <div className="rounded-2xl border border-[#c4bfb6] overflow-hidden shadow-xl shadow-black/10 mb-5">
              <div className="bg-[#e8e5e0] px-4 py-2 flex items-center gap-2 border-b border-[#d4d0ca]">
                <div className="flex gap-[5px]"><div className="w-[10px] h-[10px] rounded-full bg-[#ff5f57]" /><div className="w-[10px] h-[10px] rounded-full bg-[#febc2e]" /><div className="w-[10px] h-[10px] rounded-full bg-[#28c840]" /></div>
                <div className="flex-1 text-center font-mono text-[11px] text-[#525252]">ecf.{filing?.court_id || "nysd"}.uscourts.gov</div>
                {!browserDone && <span className="text-[10px] text-[#1e3a5f] font-semibold animate-pulse">LIVE</span>}
              </div>
              <div className="bg-[#f0eee9] min-h-[300px] flex items-center justify-center">
                {screenshot ? <img src={`data:image/png;base64,${screenshot}`} className="w-full" alt="CM/ECF" /> : <span className="text-[13px] text-[#8a8a8a]">Connecting...</span>}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-[#e8e5e0] overflow-hidden shadow-sm mb-5">
              {browserSteps.map((s) => (
                <div key={s.step} className="flex items-start gap-3 px-5 py-3 border-b border-[#f0eee9] last:border-0">
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5 ${s.status === "done" ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#e1effe] text-[#1e3a5f]"}`}>
                    {s.status === "done" ? "✓" : <span className="animate-pulse">●</span>}
                  </div>
                  <div><div className="text-[12px] font-semibold text-[#1a1a1a]">{s.step}</div><div className="text-[11px] text-[#8a8a8a]">{s.description}</div></div>
                </div>
              ))}
            </div>

            {browserDone && (
              <div className="flex items-center gap-4">
                <button onClick={() => setPhase("done")} className="px-6 py-2.5 bg-[#1e3a5f] text-white text-[13px] font-semibold rounded-xl hover:bg-[#162a47] transition shadow-sm">View Receipt</button>
                <span className="text-[13px] text-[#525252]">{browserMsg}</span>
              </div>
            )}
          </div>
        )}

        {/* Done */}
        {phase === "done" && filing && (
          <div className="max-w-xl mx-auto text-center py-8">
            <div className="w-20 h-20 bg-gradient-to-br from-[#f0fdf4] to-[#dcfce7] rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-green-200/30">
              <svg className="w-10 h-10 text-[#15803d]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
            </div>
            <h2 className="text-[24px] font-bold text-[#1a1a1a] mb-2">Filing Submitted</h2>
            <p className="text-[14px] text-[#525252] mb-8">Your document has been filed on CM/ECF.</p>

            <div className="bg-white rounded-2xl border border-[#e8e5e0] overflow-hidden shadow-sm mb-8 text-left">
              {[
                { label: "Court", value: filing.court_id?.toUpperCase() },
                { label: "Case", value: filing.case_number },
                { label: "Document", value: docketText || filing.event_description },
                ...(exhibits.length > 0 ? [{ label: "Attachments", value: `${exhibits.length} exhibit${exhibits.length > 1 ? "s" : ""}` }] : []),
              ].filter(f => f.value).map(({ label, value }) => (
                <div key={label} className="flex px-5 py-3 border-b border-[#f0eee9] last:border-0">
                  <div className="w-[100px] shrink-0 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide pt-0.5">{label}</div>
                  <div className="text-[13px] text-[#1a1a1a] font-medium">{value}</div>
                </div>
              ))}
            </div>

            <div className="flex items-center justify-center gap-3">
              <button onClick={reset} className="px-8 py-3 bg-[#1e3a5f] text-white text-[14px] font-semibold rounded-xl hover:bg-[#162a47] transition shadow-lg shadow-[#1e3a5f]/20">
                File Another Document
              </button>
              <button onClick={() => setShowHistory(true)} className="px-5 py-3 border border-[#e8e5e0] text-[13px] text-[#525252] font-medium rounded-xl hover:bg-[#fafaf8] transition">
                View History
              </button>
            </div>
          </div>
        )}

        {/* Error */}
        {phase === "error" && (
          <div className="text-center py-12">
            <div className="w-14 h-14 bg-[#fef2f2] rounded-2xl flex items-center justify-center mx-auto mb-5">
              <svg className="w-7 h-7 text-[#b91c1c]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>
            </div>
            <h2 className="text-[18px] font-bold text-[#1a1a1a] mb-2">Something went wrong</h2>
            <p className="text-[14px] text-[#525252] mb-6">{error}</p>
            <button onClick={reset} className="px-6 py-2.5 bg-[#1e3a5f] text-white text-[13px] font-semibold rounded-xl hover:bg-[#162a47] transition">Try Again</button>
          </div>
        )}
      </div>

      {/* History slide-out */}
      {showHistory && (
        <div className="fixed inset-0 z-50 flex justify-end" onClick={() => setShowHistory(false)}>
          <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" />
          <div className="relative w-full sm:w-[380px] md:w-[400px] bg-white h-full shadow-2xl overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="sticky top-0 bg-white border-b border-[#e8e5e0] px-6 py-4 flex items-center justify-between">
              <h3 className="text-[16px] font-bold text-[#1a1a1a]">Filing History</h3>
              <button onClick={() => setShowHistory(false)} className="text-[#8a8a8a] hover:text-[#1a1a1a] transition text-lg">&times;</button>
            </div>
            <div className="p-6">
              {history.length === 0 ? (
                <p className="text-[13px] text-[#8a8a8a] text-center py-8">No filings yet</p>
              ) : history.map((h, i) => (
                <div key={i} className="py-3 border-b border-[#f0eee9] last:border-0">
                  <div className="text-[13px] font-medium text-[#1a1a1a]">{String(h.event_description || "Filing")}</div>
                  <div className="text-[11px] text-[#8a8a8a] font-mono mt-0.5">{String(h.court_id || "")} &middot; {String(h.case_number || "")} &middot; {String(h.filed_at || "").substring(0, 10)}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Courts modal */}
      {showCourts && (
        <CourtsModal onClose={() => setShowCourts(false)} />
      )}
    </div>
  );
}

function CourtsModal({ onClose }: { onClose: () => void }) {
  const [query, setQuery] = useState("");
  const [courts, setCourts] = useState<{ court_id: string; name: string; court_type: string }[]>([]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (query) params.set("search", query);
    fetch(`/api/courts?${params}`).then(r => r.json()).then(setCourts).catch(() => {});
  }, [query]);

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]" onClick={onClose}>
      <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" />
      <div className="relative w-[calc(100%-2rem)] sm:w-[500px] md:w-[560px] bg-white rounded-2xl shadow-2xl border border-[#e8e5e0] max-h-[60vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="p-4 border-b border-[#f0eee9]">
          <input
            type="text" value={query} onChange={(e) => setQuery(e.target.value)} autoFocus
            placeholder="Search 207 federal courts..."
            className="w-full px-4 py-2.5 bg-[#f5f3ee] rounded-xl text-[14px] outline-none focus:bg-white focus:ring-2 focus:ring-[#1e3a5f]/10 border border-transparent focus:border-[#1e3a5f] transition"
          />
        </div>
        <div className="overflow-y-auto flex-1">
          {courts.slice(0, 20).map((c) => (
            <div key={c.court_id} className="flex items-center justify-between px-5 py-3 border-b border-[#f0eee9] last:border-0 hover:bg-[#fafaf8] transition cursor-default">
              <div>
                <div className="text-[13px] font-medium text-[#1a1a1a]">{c.name}</div>
                <div className="text-[11px] text-[#8a8a8a] font-mono">ecf.{c.court_id}.uscourts.gov</div>
              </div>
              <span className={`text-[10px] px-2 py-0.5 rounded-md font-semibold ${
                c.court_type === "district" ? "bg-[#e1effe] text-[#1e3a5f]" : c.court_type === "bankruptcy" ? "bg-[#f5f3ff] text-[#7c3aed]" : "bg-[#fffbeb] text-[#b45309]"
              }`}>{c.court_type}</span>
            </div>
          ))}
          {courts.length === 0 && <div className="p-8 text-center text-[13px] text-[#8a8a8a]">No courts found</div>}
        </div>
      </div>
    </div>
  );
}
