"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import Link from "next/link";
import { UserButton } from "@clerk/nextjs";
import { streamAnalysis, streamBrowser, getHistory, type FilingPreview, type AnalysisStep, type BrowserStep, type FilingOptions } from "@/lib/api";

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
  const [showEventSearch, setShowEventSearch] = useState(false);
  const [eventCodeOverride, setEventCodeOverride] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [filingStartTime, setFilingStartTime] = useState<number | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);
  const exhibitRef = useRef<HTMLInputElement>(null);

  useEffect(() => { getHistory().then((h) => setHistory(h.slice(0, 10))).catch(() => {}); }, []);

  // Elapsed time counter for filing phase
  useEffect(() => {
    if (phase === "filing" && !filingStartTime) setFilingStartTime(Date.now());
    if (phase !== "filing") { setFilingStartTime(null); setElapsedTime(0); return; }
    const interval = setInterval(() => {
      if (filingStartTime) setElapsedTime(Math.floor((Date.now() - filingStartTime) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [phase, filingStartTime]);

  const reset = () => {
    setPhase("ready"); setFileName(""); setSteps([]); setFiling(null);
    setBrowserSteps([]); setScreenshot(""); setBrowserDone(false); setError("");
    setExhibits([]); setIsSealed(false); setIsRedacted(false); setDocketText(""); setShowCertService(false); setShowEventSearch(false); setEventCodeOverride("");
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
          // Typing animation for docket text
          const fullText = event.data.event_description || "";
          setDocketText("");
          setIsTyping(true);
          setTimeout(() => {
            setPhase("review");
            let i = 0;
            const timer = setInterval(() => {
              i++;
              setDocketText(fullText.slice(0, i));
              if (i >= fullText.length) { clearInterval(timer); setIsTyping(false); }
            }, 25);
          }, 300);
        }
        if (event.type === "error") throw new Error(event.message);
      }
    } catch (e: unknown) { setError(e instanceof Error ? e.message : "Failed"); setPhase("error"); }
  }, []);

  const handleConfirm = useCallback(async () => {
    if (!filing) return;
    setPhase("filing"); setBrowserSteps([]); setScreenshot(""); setBrowserDone(false);
    try {
      const options = {
        docket_text: docketText || undefined,
        event_code_override: eventCodeOverride || undefined,
        is_sealed: isSealed,
        is_redacted: isRedacted,
        include_cos: showCertService,
        exhibits: exhibits.map((e) => ({ label: e.label, description: e.description })),
      };
      for await (const event of streamBrowser(filing, options)) {
        if (event.type === "browser") { if (event.data.screenshot) setScreenshot(event.data.screenshot); setBrowserSteps((prev) => { const ex = prev.find((s) => s.step === event.data.step); if (ex) return prev.map((s) => s.step === event.data.step ? { ...s, ...event.data } : s); return [...prev, event.data]; }); }
        if (event.type === "done") { setBrowserDone(true); setBrowserMsg(event.message); }
      }
    } catch (e: unknown) { setBrowserDone(true); setBrowserMsg(e instanceof Error ? e.message : "Failed"); }
  }, [filing, docketText, eventCodeOverride, isSealed, isRedacted, showCertService, exhibits]);

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
      <div className={`${phase === "filing" ? "max-w-6xl" : "max-w-3xl"} mx-auto px-4 sm:px-6 py-6 sm:py-10 transition-all duration-500`}>

        {/* Ready state */}
        {phase === "ready" && (
          <div>
            {/* Two-column layout */}
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-8">
              {/* Drop zone — 3 cols */}
              <div className="lg:col-span-3">
                <div
                  className="bg-white border border-[#d4d0ca] rounded-2xl p-10 text-center cursor-pointer hover:border-[#1e3a5f] hover:shadow-lg hover:shadow-[#1e3a5f]/5 transition-all group h-full flex flex-col items-center justify-center min-h-[260px] shadow-sm drop-glow"
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
                  <div key={s.id} className="flex items-start gap-4 py-3 border-b border-[#f0eee9] last:border-0 step-enter">
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
              ].filter(f => f.value).map(({ label, value, sub, mono, highlight }) => (
                <div key={label} className={`flex px-5 py-3.5 border-b border-[#f0eee9] last:border-0 ${highlight ? "bg-[#f0f4fa]" : ""}`}>
                  <div className="w-[110px] shrink-0 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide pt-0.5">{label}</div>
                  <div className={`text-[14px] ${mono ? "font-mono" : ""} text-[#1a1a1a]`}>
                    {value}
                    {sub && <div className="text-[11px] text-[#8a8a8a] font-mono mt-0.5">{sub}</div>}
                  </div>
                </div>
              ))}
              {/* Event Code — editable row */}
              <div className="flex px-5 py-3.5 border-b border-[#f0eee9] last:border-0 relative">
                <div className="w-[110px] shrink-0 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide pt-0.5">Event Code</div>
                <div className="flex-1">
                  <button onClick={() => setShowEventSearch(!showEventSearch)} className="flex items-center gap-2 text-[14px] font-mono text-[#1a1a1a] hover:text-[#1e3a5f] transition group">
                    {eventCodeOverride || filing.event_code}
                    <svg className="w-3.5 h-3.5 text-[#c4c4c4] group-hover:text-[#1e3a5f] transition" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931z" />
                    </svg>
                  </button>
                  <div className="text-[11px] text-[#8a8a8a] mt-0.5">{filing.event_description}</div>
                  {eventCodeOverride && eventCodeOverride !== filing.event_code && (
                    <button onClick={() => setEventCodeOverride("")} className="text-[10px] text-[#1e3a5f] hover:underline mt-1">Reset to AI suggestion ({filing.event_code})</button>
                  )}
                </div>
              </div>
              {showEventSearch && <EventCodeSearch courtId={filing.court_id} onSelect={(code, desc) => { setEventCodeOverride(code); setShowEventSearch(false); }} onClose={() => setShowEventSearch(false)} />}
            </div>

            {/* Docket Text — the hero of the review screen */}
            <div className="bg-white rounded-2xl border-2 border-[#1e3a5f]/20 overflow-hidden shadow-lg shadow-[#1e3a5f]/5 mb-5">
              <div className="px-6 py-4 bg-gradient-to-r from-[#0f1f35] to-[#1e3a5f] flex items-center justify-between">
                <div>
                  <div className="text-[13px] font-semibold text-white">Docket Text</div>
                  <div className="text-[11px] text-white/50 mt-0.5">This is exactly what appears on the court docket — edit before filing</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] px-2.5 py-1 rounded-md font-mono border ${isTyping ? "bg-white/20 text-white border-white/20 animate-pulse" : "bg-white/10 text-white/70 border-white/10"}`}>
                    {isTyping ? "AI typing..." : "editable"}
                  </span>
                </div>
              </div>
              <div className="p-6">
                <textarea
                  value={docketText}
                  onChange={(e) => setDocketText(e.target.value)}
                  rows={3}
                  className={`w-full px-5 py-4 border border-[#e8e5e0] rounded-xl text-[16px] font-semibold text-[#1a1a1a] outline-none focus:border-[#1e3a5f] focus:ring-2 focus:ring-[#1e3a5f]/10 resize-none bg-[#fafaf8] leading-relaxed ${isTyping ? "caret-[#1e3a5f]" : ""}`}
                  placeholder="Enter docket text..."
                  readOnly={isTyping}
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
        {phase === "filing" && (() => {
          const doneCount = browserSteps.filter((s) => s.status === "done").length;
          const totalSteps = Math.max(browserSteps.length, 1);
          const progressPct = browserDone ? 100 : Math.round((doneCount / totalSteps) * 95);
          const elapsedMin = Math.floor(elapsedTime / 60);
          const elapsedSec = elapsedTime % 60;
          const elapsedStr = `${elapsedMin}:${String(elapsedSec).padStart(2, "0")}`;
          const courtId = filing?.court_id || "nysd";
          const courtName = courtId.toUpperCase();

          return (
          <div>
            {/* Header row */}
            <div className="flex items-center justify-between mb-1">
              <h2 className="text-[20px] font-bold text-[#1a1a1a]">Filing on CM/ECF</h2>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5 font-mono text-[13px] text-[#525252] tabular-nums">
                  <svg className="w-3.5 h-3.5 text-[#8a8a8a]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  {elapsedStr}
                </div>
                <span className="text-[14px] font-bold text-[#1e3a5f] tabular-nums">{progressPct}%</span>
              </div>
            </div>
            <p className="text-[13px] text-[#525252] mb-3">{courtName} &middot; {filing?.case_number || ""}</p>

            {/* Progress bar */}
            <div className="w-full h-[6px] bg-[#e8e5e0] rounded-full mb-5 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700 ease-out"
                style={{
                  width: `${progressPct}%`,
                  background: browserDone
                    ? "linear-gradient(90deg, #15803d, #22c55e)"
                    : "linear-gradient(90deg, #1e3a5f, #2d5a8e, #1e3a5f)",
                  backgroundSize: browserDone ? "100% 100%" : "200% 100%",
                  animation: browserDone ? "none" : "ecf-shimmer 2s linear infinite",
                }}
              />
            </div>
            <style>{`@keyframes ecf-shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }`}</style>

            {/* Success banner with confetti */}
            {browserDone && (
              <div className="relative mb-5 rounded-2xl overflow-hidden">
                <div className="absolute inset-0 pointer-events-none overflow-hidden">
                  {[
                    { l: "5%", t: "10%", bg: "#fbbf24", w: "8px", h: "8px", r: "45deg", d: "0s", dur: "1.5s" },
                    { l: "15%", t: "30%", bg: "#34d399", w: "6px", h: "12px", r: "-12deg", d: "0.2s", dur: "1.8s" },
                    { l: "28%", t: "5%", bg: "#f87171", w: "10px", h: "6px", r: "30deg", d: "0.4s", dur: "1.3s" },
                    { l: "42%", t: "15%", bg: "#60a5fa", w: "7px", h: "7px", r: "0deg", d: "0.1s", dur: "1.6s" },
                    { l: "55%", t: "8%", bg: "#a78bfa", w: "5px", h: "10px", r: "60deg", d: "0.6s", dur: "1.2s" },
                    { l: "68%", t: "25%", bg: "#fbbf24", w: "8px", h: "4px", r: "-20deg", d: "0.5s", dur: "1.7s" },
                    { l: "78%", t: "12%", bg: "#34d399", w: "6px", h: "10px", r: "45deg", d: "0.3s", dur: "1.4s" },
                    { l: "88%", t: "5%", bg: "#f87171", w: "7px", h: "7px", r: "-45deg", d: "0.7s", dur: "1.5s" },
                    { l: "35%", t: "35%", bg: "#60a5fa", w: "5px", h: "8px", r: "15deg", d: "0.8s", dur: "1.3s" },
                    { l: "92%", t: "30%", bg: "#a78bfa", w: "9px", h: "5px", r: "75deg", d: "0.15s", dur: "1.9s" },
                  ].map((p, idx) => (
                    <div key={idx} className="absolute rounded-sm animate-bounce" style={{ left: p.l, top: p.t, width: p.w, height: p.h, backgroundColor: p.bg, transform: `rotate(${p.r})`, animationDelay: p.d, animationDuration: p.dur }} />
                  ))}
                </div>
                <div className="bg-gradient-to-r from-[#f0fdf4] via-[#dcfce7] to-[#f0fdf4] border border-[#bbf7d0] px-6 py-5 flex items-center justify-between relative z-10">
                  <div className="flex items-center gap-4">
                    <div className="w-11 h-11 bg-[#15803d] rounded-full flex items-center justify-center shadow-lg shadow-green-400/30">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={3}><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                    </div>
                    <div>
                      <div className="text-[17px] font-bold text-[#15803d] tracking-wide">SUCCESS</div>
                      <div className="text-[12px] text-[#166534]">{browserMsg || "Document filed successfully on CM/ECF"}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="font-mono text-[12px] text-[#15803d]/50">{elapsedStr} elapsed</span>
                    <button onClick={() => setPhase("done")} className="px-6 py-2.5 bg-[#15803d] text-white text-[13px] font-bold rounded-xl hover:bg-[#166534] transition shadow-lg shadow-green-800/20">
                      View Receipt
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Split panel: browser + timeline */}
            <div className="flex gap-5">
              {/* Left: Browser window */}
              <div className="flex-1 min-w-0">
                <div className="rounded-2xl border border-[#c4bfb6] overflow-hidden shadow-xl shadow-black/10">
                  {/* Browser chrome */}
                  <div className="bg-[#e8e5e0] px-4 py-2.5 flex items-center gap-3 border-b border-[#d4d0ca]">
                    <div className="flex gap-[6px]">
                      <div className="w-[11px] h-[11px] rounded-full bg-[#ff5f57] shadow-inner" />
                      <div className="w-[11px] h-[11px] rounded-full bg-[#febc2e] shadow-inner" />
                      <div className="w-[11px] h-[11px] rounded-full bg-[#28c840] shadow-inner" />
                    </div>
                    <div className="flex-1 bg-white/70 rounded-md px-3 py-1 flex items-center gap-2">
                      <svg className="w-3 h-3 text-[#8a8a8a] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" /></svg>
                      <span className="font-mono text-[11px] text-[#525252] truncate">https://ecf.{courtId}.uscourts.gov/cgi-bin/DktRpt.pl</span>
                    </div>
                    {!browserDone && (
                      <div className="flex items-center gap-1.5">
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#1e3a5f] opacity-50" />
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-[#1e3a5f]" />
                        </span>
                        <span className="text-[10px] text-[#1e3a5f] font-bold uppercase tracking-wider">Live</span>
                      </div>
                    )}
                    {browserDone && <span className="text-[10px] text-[#15803d] font-bold uppercase tracking-wider">Done</span>}
                  </div>

                  {/* Screenshot or mock CM/ECF */}
                  <div className="bg-white min-h-[420px]">
                    {screenshot ? (
                      <img src={`data:image/png;base64,${screenshot}`} className="w-full" alt="CM/ECF" />
                    ) : (
                      <div className="select-none">
                        {/* CM/ECF blue header */}
                        <div className="bg-[#003366] px-4 py-3 flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-9 h-9 bg-white/10 rounded flex items-center justify-center border border-white/20">
                              <svg className="w-5 h-5 text-white/90" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" /></svg>
                            </div>
                            <div>
                              <div className="text-white font-serif text-[15px] font-bold">CM/ECF - {courtName}</div>
                              <div className="text-blue-200/70 text-[11px] font-serif">U.S. District Court - Document Filing System</div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-white/40 text-[10px] font-mono tracking-wide">PACER</div>
                            <div className="text-white/30 text-[9px] font-mono">NextGen</div>
                          </div>
                        </div>

                        {/* Nav tabs */}
                        <div className="bg-[#004080] px-4 py-1.5 flex items-center gap-1 border-b border-[#002244]">
                          {["Query", "Reports", "Utilities", "Filing", "Search"].map((item, i) => (
                            <span key={item} className={`text-[11px] px-3 py-1 rounded-t ${i === 3 ? "bg-white/20 text-white font-bold" : "text-blue-200/60"} cursor-default`}>{item}</span>
                          ))}
                        </div>

                        {/* Breadcrumb */}
                        <div className="bg-[#f0f0f0] px-4 py-2 border-b border-[#d0d0d0] text-[11px] text-[#555] font-serif flex items-center gap-1">
                          <span className="text-[#1e3a5f] font-semibold">Civil</span>
                          <span className="text-[#999]">&rsaquo;</span>
                          <span>File a Document</span>
                          <span className="text-[#999]">&rsaquo;</span>
                          <span className="text-[#333]">{filing?.case_number || "Case"}</span>
                        </div>

                        {/* Form content */}
                        <div className="p-5">
                          <div className="mb-4">
                            <div className="text-[14px] font-serif font-bold text-[#333] mb-1">E-File a Document</div>
                            <div className="h-px bg-[#ccc]" />
                          </div>
                          <div className="space-y-3">
                            <div className="flex items-center gap-3">
                              <label className="text-[11px] font-serif text-[#333] w-28 shrink-0 text-right">Case Number:</label>
                              <div className="flex-1 h-7 bg-white border border-[#999] rounded-sm px-2 flex items-center shadow-inner shadow-black/5">
                                <span className="text-[11px] font-mono text-[#333]">{filing?.case_number || ""}</span>
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              <label className="text-[11px] font-serif text-[#333] w-28 shrink-0 text-right">Filing Type:</label>
                              <div className="flex-1 h-7 bg-white border border-[#999] rounded-sm px-2 flex items-center shadow-inner shadow-black/5">
                                <span className="text-[11px] font-mono text-[#555]">{filing?.event_description || "Motion"}</span>
                                <svg className="w-3 h-3 text-[#999] ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              <label className="text-[11px] font-serif text-[#333] w-28 shrink-0 text-right">Filing Party:</label>
                              <div className="flex-1 h-7 bg-white border border-[#999] rounded-sm px-2 flex items-center shadow-inner shadow-black/5">
                                <span className="text-[11px] font-mono text-[#555]">Attorney for Plaintiff</span>
                              </div>
                            </div>
                            <div className="flex items-start gap-3 pt-1">
                              <label className="text-[11px] font-serif text-[#333] w-28 shrink-0 text-right pt-2">PDF Document:</label>
                              <div className="flex-1 border border-dashed border-[#999] rounded bg-[#fafafa] p-3">
                                <div className="flex items-center gap-2">
                                  <svg className="w-5 h-5 text-[#c00]" fill="currentColor" viewBox="0 0 24 24"><path d="M7 2C5.9 2 5 2.9 5 4v16c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V8l-6-6H7zm7 7V3.5L18.5 8H14zM9 13h6v2H9v-2zm0 4h4v2H9v-2z" /></svg>
                                  <span className="text-[11px] text-[#333] font-medium">{fileName || "document.pdf"}</span>
                                  <span className="text-[10px] text-[#15803d] ml-2 font-semibold">Uploaded</span>
                                </div>
                              </div>
                            </div>
                          </div>
                          {!browserDone && (
                            <div className="mt-6 pt-4 border-t border-[#e0e0e0] flex items-center gap-3">
                              <div className="w-5 h-5 border-2 border-[#1e3a5f] border-t-transparent rounded-full animate-spin" />
                              <div>
                                <div className="text-[12px] text-[#333] font-medium">ECFiler is navigating CM/ECF...</div>
                                <div className="text-[10px] text-[#888]">{browserSteps.length > 0 ? browserSteps[browserSteps.length - 1].step : "Connecting to court system"}</div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Right: Step timeline */}
              <div className="w-[300px] shrink-0 hidden lg:block">
                <div className="bg-white rounded-2xl border border-[#e8e5e0] overflow-hidden shadow-sm sticky top-20">
                  <div className="px-5 py-3.5 border-b border-[#e8e5e0] bg-[#fafaf8] flex items-center justify-between">
                    <span className="text-[11px] font-bold text-[#1a1a1a] uppercase tracking-wider">Filing Progress</span>
                    <span className="text-[11px] font-mono text-[#8a8a8a]">{doneCount}/{browserSteps.length || 0}</span>
                  </div>
                  <div className="p-4 max-h-[500px] overflow-y-auto">
                    {browserSteps.length === 0 && (
                      <div className="flex items-center gap-3 py-4 px-2 text-[12px] text-[#8a8a8a]">
                        <div className="flex gap-1">
                          <div className="w-1.5 h-1.5 bg-[#1e3a5f] rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                          <div className="w-1.5 h-1.5 bg-[#1e3a5f] rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                          <div className="w-1.5 h-1.5 bg-[#1e3a5f] rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                        </div>
                        Initializing browser...
                      </div>
                    )}
                    <div className="space-y-0">
                      {browserSteps.map((s, i) => {
                        const isDone = s.status === "done";
                        const isActive = !isDone;
                        const isLast = i === browserSteps.length - 1;
                        return (
                          <div key={s.step} className="relative flex gap-3">
                            {!isLast && (
                              <div className="absolute left-[10px] top-[24px] bottom-0 w-[2px] rounded-full transition-colors duration-300" style={{ background: isDone ? "#bbf7d0" : "#e8e5e0" }} />
                            )}
                            <div className={`relative w-[21px] h-[21px] rounded-full flex items-center justify-center shrink-0 mt-0.5 transition-all duration-300 ${isDone ? "bg-[#15803d] shadow-sm shadow-green-400/20" : "bg-[#1e3a5f] shadow-md shadow-[#1e3a5f]/30"}`}>
                              {isDone ? (
                                <svg className="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={3}><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                              ) : (
                                <span className="w-2 h-2 bg-white rounded-full animate-pulse" />
                              )}
                            </div>
                            <div className={`pb-5 min-w-0 transition-opacity duration-300 ${isActive ? "opacity-100" : "opacity-60"}`}>
                              <div className={`text-[12px] font-semibold leading-tight ${isActive ? "text-[#1a1a1a]" : "text-[#525252]"}`}>{s.step}</div>
                              <div className="text-[10px] text-[#8a8a8a] leading-snug mt-0.5">{s.description}</div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  <div className="px-5 py-3 border-t border-[#e8e5e0] bg-[#fafaf8] flex items-center justify-between">
                    <span className="text-[10px] text-[#8a8a8a]">Elapsed</span>
                    <span className="font-mono text-[11px] text-[#525252] tabular-nums">{elapsedStr}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Mobile step list */}
            <div className="lg:hidden mt-5 bg-white rounded-xl border border-[#e8e5e0] overflow-hidden shadow-sm">
              <div className="px-4 py-2.5 border-b border-[#e8e5e0] bg-[#fafaf8] flex items-center justify-between">
                <span className="text-[10px] font-bold text-[#8a8a8a] uppercase tracking-wider">Steps</span>
                <span className="text-[10px] font-mono text-[#8a8a8a]">{doneCount}/{browserSteps.length || 0}</span>
              </div>
              {browserSteps.map((s) => (
                <div key={s.step} className="flex items-start gap-3 px-4 py-2.5 border-b border-[#f0eee9] last:border-0">
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold shrink-0 mt-0.5 ${s.status === "done" ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#1e3a5f] text-white"}`}>
                    {s.status === "done" ? "\u2713" : <span className="animate-pulse">{"\u25CF"}</span>}
                  </div>
                  <div className="min-w-0">
                    <div className="text-[11px] font-semibold text-[#1a1a1a]">{s.step}</div>
                    <div className="text-[10px] text-[#8a8a8a] truncate">{s.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          );
        })()}

        {/* Done */}
        {phase === "done" && filing && (
          <div className="max-w-xl mx-auto py-8">
            {/* Success header */}
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-gradient-to-br from-[#f0fdf4] to-[#dcfce7] rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-green-200/30">
                <svg className="w-10 h-10 text-[#15803d]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
              </div>
              <h2 className="text-[24px] font-bold text-[#1a1a1a] mb-2">Filing Submitted</h2>
              <p className="text-[14px] text-[#525252]">Your document has been filed on CM/ECF.</p>
            </div>

            {/* Receipt card */}
            <div className="bg-white rounded-2xl border border-[#e8e5e0] overflow-hidden shadow-sm mb-6">
              <div className="px-5 py-3 bg-[#fafaf8] border-b border-[#f0eee9] flex items-center justify-between">
                <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Filing Receipt</span>
                <span className="text-[10px] text-[#c4c4c4] font-mono">{new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })} at {new Date().toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })}</span>
              </div>
              {[
                { label: "Court", value: filing.court_id?.toUpperCase() },
                { label: "Case", value: filing.case_number },
                { label: "Docket Text", value: docketText || filing.event_description },
                { label: "Event Code", value: filing.event_code },
                ...(filing.filing_party ? [{ label: "Filed By", value: filing.filing_party }] : []),
                ...(exhibits.length > 0 ? [{ label: "Attachments", value: exhibits.map(e => e.label).join(", ") }] : []),
                ...(filing.filing_fee ? [{ label: "Fee", value: `$${filing.filing_fee}` }] : []),
                { label: "Status", value: "Submitted" },
              ].filter(f => f.value).map(({ label, value }) => (
                <div key={label} className="flex px-5 py-3 border-b border-[#f0eee9] last:border-0">
                  <div className="w-[100px] shrink-0 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide pt-0.5">{label}</div>
                  <div className="text-[13px] text-[#1a1a1a] font-medium">{value}</div>
                </div>
              ))}
            </div>

            {/* Actions */}
            <div className="flex items-center justify-center gap-3">
              <button onClick={reset} className="px-8 py-3 bg-[#1e3a5f] text-white text-[14px] font-semibold rounded-xl hover:bg-[#162a47] transition shadow-lg shadow-[#1e3a5f]/20">
                File Another Document
              </button>
              <button onClick={() => setShowHistory(true)} className="px-5 py-3 border border-[#e8e5e0] text-[13px] text-[#525252] font-medium rounded-xl hover:bg-[#fafaf8] transition">
                View History
              </button>
            </div>

            {/* Disclaimer */}
            <p className="text-[10px] text-[#c4c4c4] text-center mt-6">
              This receipt confirms submission to CM/ECF. The official Notice of Electronic Filing (NEF) will be sent by the court via email.
            </p>
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
          <div className="relative w-full sm:w-[380px] md:w-[420px] bg-white h-full shadow-2xl overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="sticky top-0 bg-white border-b border-[#e8e5e0] px-6 py-4 z-10">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-[16px] font-bold text-[#1a1a1a]">Filing History</h3>
                <button onClick={() => setShowHistory(false)} className="w-7 h-7 rounded-lg bg-[#f5f3ee] hover:bg-[#e8e5e0] flex items-center justify-center text-[#8a8a8a] hover:text-[#1a1a1a] transition text-sm">&times;</button>
              </div>
              <div className="text-[11px] text-[#8a8a8a]">{history.length} filing{history.length !== 1 ? "s" : ""} on record</div>
            </div>
            <div className="p-4">
              {history.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-12 h-12 bg-[#f5f3ee] rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-[#c4c4c4]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  </div>
                  <p className="text-[13px] text-[#8a8a8a] mb-1">No filings yet</p>
                  <p className="text-[11px] text-[#c4c4c4]">Drop a PDF to start your first filing</p>
                </div>
              ) : history.map((h, i) => (
                <div key={i} className="bg-[#fafaf8] border border-[#f0eee9] rounded-xl p-4 mb-2 hover:border-[#e8e5e0] transition">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="text-[13px] font-semibold text-[#1a1a1a] truncate">{String(h.event_description || "Filing")}</div>
                      <div className="text-[11px] text-[#8a8a8a] font-mono mt-0.5">
                        {String(h.court_id || "").toUpperCase()} &middot; {String(h.case_number || "")}
                      </div>
                    </div>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold shrink-0 ${
                      String(h.status) === "submitted" || String(h.status) === "filed" ? "bg-[#f0fdf4] text-[#15803d]" :
                      String(h.status) === "error" ? "bg-[#fef2f2] text-[#b91c1c]" : "bg-[#f5f3ee] text-[#8a8a8a]"
                    }`}>{String(h.status || "filed")}</span>
                  </div>
                  <div className="flex items-center gap-3 mt-2 text-[10px] text-[#c4c4c4]">
                    <span>{String(h.filed_at || "").substring(0, 10)}</span>
                    {h.docket_number ? <span className="font-mono">Dkt. #{String(h.docket_number)}</span> : null}
                  </div>
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

function EventCodeSearch({ courtId, onSelect, onClose }: { courtId: string; onSelect: (code: string, desc: string) => void; onClose: () => void }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<{ code: string; description: string }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query || query.length < 2) { setResults([]); return; }
    setLoading(true);
    const timer = setTimeout(() => {
      fetch(`/api/courts/${courtId || "nysd"}/events?search=${encodeURIComponent(query)}`)
        .then(r => r.json())
        .then((data) => { setResults(data.slice(0, 15)); setLoading(false); })
        .catch(() => setLoading(false));
    }, 250);
    return () => clearTimeout(timer);
  }, [query, courtId]);

  return (
    <div className="border-t border-[#e8e5e0] bg-[#fafaf8] p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Search Event Codes</span>
        <button onClick={onClose} className="text-[11px] text-[#8a8a8a] hover:text-[#1a1a1a] transition">Close</button>
      </div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="e.g., motion to dismiss, reply brief..."
        autoFocus
        className="w-full px-3 py-2 border border-[#e8e5e0] rounded-lg text-[13px] outline-none focus:border-[#1e3a5f] focus:ring-1 focus:ring-[#1e3a5f]/10 bg-white mb-2"
      />
      {loading && <div className="text-[11px] text-[#8a8a8a] py-2">Searching...</div>}
      {results.length > 0 && (
        <div className="max-h-[200px] overflow-y-auto border border-[#e8e5e0] rounded-lg bg-white">
          {results.map((r) => (
            <button
              key={r.code}
              onClick={() => onSelect(r.code, r.description)}
              className="w-full text-left px-3 py-2 border-b border-[#f0eee9] last:border-0 hover:bg-[#f0f4fa] transition"
            >
              <span className="text-[12px] font-mono text-[#1e3a5f] font-semibold">{r.code}</span>
              <span className="text-[12px] text-[#525252] ml-2">{r.description}</span>
            </button>
          ))}
        </div>
      )}
      {query.length >= 2 && !loading && results.length === 0 && (
        <div className="text-[11px] text-[#8a8a8a] py-2">No matching event codes</div>
      )}
    </div>
  );
}
