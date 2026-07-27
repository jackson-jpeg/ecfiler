"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import Link from "next/link";
import { UserButton, useUser } from "@clerk/nextjs";
import { streamAnalysis, stageFiling, getHistory, type FilingPreview, type AnalysisStep, type StagedPackage, type FilingOptions } from "@/lib/api";
import { EventCodeSearch } from "@/components/event-code-search";
import { CourtsModal } from "@/components/courts-modal";
import { useToast } from "@/components/toast";

type Phase = "ready" | "analyzing" | "review" | "staging" | "done" | "error";

interface Exhibit {
  id: string;
  file: File;
  label: string;
  description: string;
  sealed?: boolean;
}

const EXHIBIT_LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

export default function WorkspacePage() {
  const { user } = useUser();
  const [phase, setPhase] = useState<Phase>("ready");
  const [fileName, setFileName] = useState("");
  const [fileSize, setFileSize] = useState(0);
  const [steps, setSteps] = useState<AnalysisStep[]>([]);
  const [filing, setFiling] = useState<FilingPreview | null>(null);
  const [stagedPackage, setStagedPackage] = useState<StagedPackage | null>(null);
  const [error, setError] = useState("");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [history, setHistory] = useState<any[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showCourts, setShowCourts] = useState(false);
  const [docketText, setDocketText] = useState("");
  const [isSealed, setIsSealed] = useState(false);
  const [isRedacted, setIsRedacted] = useState(false);
  const [isIfp, setIsIfp] = useState(false);
  const [exhibits, setExhibits] = useState<Exhibit[]>([]);
  const [showCertService, setShowCertService] = useState(false);
  const [showEventSearch, setShowEventSearch] = useState(false);
  const [eventCodeOverride, setEventCodeOverride] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showConfirmGate, setShowConfirmGate] = useState(false);
  const [attorneyAttest, setAttorneyAttest] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const exhibitRef = useRef<HTMLInputElement>(null);

  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const dragCounter = useRef(0);
  const { toast } = useToast();

  // Sealed content is refused by the hosted service — hard stop, no staging,
  // no persistence beyond memory. See docs/sealed-document-policy.md.
  const hasSealedContent = isSealed || exhibits.some((e) => !!e.sealed);

  useEffect(() => {
    getHistory().then((h) => setHistory(h.slice(0, 10))).catch(() => {});
    fetch("/api/health").then(r => r.ok ? setBackendOk(true) : setBackendOk(false)).catch(() => setBackendOk(false));
  }, []);

  // Auto-save review state to sessionStorage so accidental refreshes don't lose work.
  // Sealed filings are never persisted — memory only.
  useEffect(() => {
    if (phase === "review" && filing && hasSealedContent) {
      sessionStorage.removeItem("ecfiler_review");
      return;
    }
    if (phase === "review" && filing) {
      sessionStorage.setItem("ecfiler_review", JSON.stringify({
        filing, docketText, eventCodeOverride, isSealed, isRedacted, isIfp, showCertService, fileName, fileSize,
        exhibits: exhibits.map((e) => ({
          name: e.file.name, size: e.file.size, label: e.label, description: e.description, sealed: !!e.sealed,
        })),
      }));
    }
    if (phase === "ready" || phase === "done") {
      sessionStorage.removeItem("ecfiler_review");
    }
  }, [phase, filing, docketText, eventCodeOverride, isSealed, isRedacted, isIfp, showCertService, fileName, fileSize, exhibits, hasSealedContent]);

  // Restore review state on mount (survives accidental refresh)
  useEffect(() => {
    const saved = sessionStorage.getItem("ecfiler_review");
    if (saved && phase === "ready") {
      try {
        const state = JSON.parse(saved);
        if (state.filing) {
          setFiling(state.filing);
          setDocketText(state.docketText || "");
          setEventCodeOverride(state.eventCodeOverride || "");
          setIsSealed(state.isSealed || false);
          setIsRedacted(state.isRedacted || false);
          setIsIfp(state.isIfp || false);
          setShowCertService(state.showCertService || false);
          setFileName(state.fileName || "");
          setFileSize(state.fileSize || 0);
          setPhase("review");
          toast("Restored your previous analysis session", "success");
        }
      } catch {
        sessionStorage.removeItem("ecfiler_review");
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const reset = () => {
    setPhase("ready"); setFileName(""); setSteps([]); setFiling(null);
    setStagedPackage(null); setError("");
    setExhibits([]); setIsSealed(false); setIsRedacted(false); setIsIfp(false); setDocketText(""); setShowCertService(false); setShowEventSearch(false); setEventCodeOverride(""); setShowConfirmGate(false); setAttorneyAttest(false);
    sessionStorage.removeItem("ecfiler_review");
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

  const updateExhibitLabel = useCallback((id: string, label: string) => {
    setExhibits((prev) => prev.map((e) => e.id === id ? { ...e, label } : e));
  }, []);

  const toggleExhibitSealed = useCallback((id: string) => {
    setExhibits((prev) => prev.map((e) => e.id === id ? { ...e, sealed: !e.sealed } : e));
  }, []);

  const moveExhibit = useCallback((index: number, dir: -1 | 1) => {
    setExhibits((prev) => {
      const next = [...prev];
      const j = index + dir;
      if (j < 0 || j >= next.length) return prev;
      [next[index], next[j]] = [next[j], next[index]];
      return next.map((e, i) => ({ ...e, label: `Exhibit ${EXHIBIT_LABELS[i] || String(i + 1)}` }));
    });
  }, []);

  const handleFile = useCallback(async (file: File, exhibitFiles?: File[]) => {
    setFileName(file.name); setFileSize(file.size); setPhase("analyzing"); setSteps([]);
    const exhibitMeta = (exhibitFiles || []).map((f, i) => ({
      name: f.name,
      size: f.size,
      label: `Exhibit ${EXHIBIT_LABELS[i] || String(i + 1)}`,
      description: f.name.replace(/\.pdf$/i, "").replace(/[_-]/g, " "),
      sealed: false,
    }));
    try {
      for await (const event of streamAnalysis(file, exhibitMeta.length ? exhibitMeta : undefined)) {
        if (event.type === "step") setSteps((prev) => { const ex = prev.find((s) => s.id === event.data.id); if (ex) return prev.map((s) => s.id === event.data.id ? { ...s, ...event.data } : s); return [...prev, event.data]; });
        if (event.type === "result") {
          setFiling(event.data);
          toast(`Analysis complete — ${event.data.completeness_score}% extracted`, "success");
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
    } catch (e: unknown) { const msg = e instanceof Error ? e.message : "Failed"; setError(msg); setPhase("error"); toast(msg, "error"); }
  }, []);

  const handleConfirm = useCallback(async () => {
    if (!filing) return;
    setPhase("staging");
    try {
      const options: FilingOptions = {
        docket_text: docketText || undefined,
        event_code_override: eventCodeOverride || undefined,
        is_sealed: isSealed,
        is_redacted: isRedacted,
        include_cos: showCertService,
        exhibits: exhibits.map((e) => ({ label: e.label, description: e.description })),
        fee_status: (isIfp ? "ifp" : "paid") as "paid" | "waived" | "ifp",
      };
      // The checkbox gates this call; the server records exactly what was
      // attested, by whom, and the language they saw.
      const attestation = {
        attested: true,
        attestor_name: user?.fullName || user?.primaryEmailAddress?.emailAddress || "unnamed",
        attestation_text:
          `I have reviewed the document, docket text, event code, and all filing details above. ` +
          `I am preparing this filing for submission to ${filing.court_id?.toUpperCase()} in ` +
          `case ${filing.case_number}, and I take responsibility for what is filed.`,
        client_timestamp: new Date().toISOString(),
      };
      const pkg = await stageFiling(filing, attestation, options);
      setStagedPackage(pkg);
      setPhase("done");
      toast("Filing package staged", "success");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to stage filing package";
      setError(msg); setPhase("error"); toast(msg, "error");
    }
  }, [filing, docketText, eventCodeOverride, isSealed, isRedacted, isIfp, showCertService, exhibits, user, toast]);

  const copyText = useCallback((text: string, label: string) => {
    navigator.clipboard.writeText(text).then(
      () => toast(`${label} copied to clipboard`, "success"),
      () => toast("Copy failed", "error"),
    );
  }, [toast]);

  const downloadPackage = useCallback(() => {
    if (!stagedPackage) return;
    const blob = new Blob([JSON.stringify(stagedPackage, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `filing-package-${stagedPackage.stage_code}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }, [stagedPackage]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Cmd+Enter to stage — only if confirmation gate is open and attested
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter" && phase === "review" && filing?.ready && !hasSealedContent) {
        e.preventDefault();
        if (showConfirmGate && attorneyAttest) {
          handleConfirm();
        } else if (!showConfirmGate) {
          setShowConfirmGate(true);
          setAttorneyAttest(false);
        }
      }
      // Escape to close modals or go back
      if (e.key === "Escape") {
        if (showHistory) { setShowHistory(false); return; }
        if (showCourts) { setShowCourts(false); return; }
        if (showEventSearch) { setShowEventSearch(false); return; }
        if (phase === "review" || phase === "analyzing") { reset(); return; }
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [phase, filing, handleConfirm, showHistory, showCourts, showEventSearch, showConfirmGate, attorneyAttest, reset]);

  return (
    <div
      className="min-h-screen bg-[#f5f3ee] relative"
      onDragEnter={(e) => { e.preventDefault(); dragCounter.current++; if (phase === "ready" || phase === "review") setIsDraggingOver(true); }}
      onDragOver={(e) => e.preventDefault()}
      onDragLeave={(e) => { e.preventDefault(); dragCounter.current--; if (dragCounter.current <= 0) { setIsDraggingOver(false); dragCounter.current = 0; } }}
      onDrop={(e) => {
        e.preventDefault(); setIsDraggingOver(false); dragCounter.current = 0;
        if (phase !== "ready" && phase !== "review") return;
        const files = Array.from(e.dataTransfer.files).filter(f => f.type === "application/pdf" || f.name.endsWith(".pdf"));
        if (files.length === 0) return;
        if (phase === "ready") {
          const rest = files.slice(1);
          handleFile(files[0], rest);
          if (rest.length > 0) { const dt = new DataTransfer(); rest.forEach(f => dt.items.add(f)); addExhibits(dt.files); }
        } else if (phase === "review") {
          addExhibits(e.dataTransfer.files);
        }
      }}
    >
      {/* Full-page drag overlay */}
      {isDraggingOver && (
        <div className="fixed inset-0 z-[100] bg-[#1e3a5f]/10 backdrop-blur-[2px] flex items-center justify-center pointer-events-none">
          <div className="bg-white rounded-2xl shadow-2xl border-2 border-dashed border-[#1e3a5f] px-12 py-10 text-center">
            <svg className="w-12 h-12 text-[#1e3a5f] mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.338-2.32 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
            </svg>
            <div className="text-[16px] font-semibold text-[#1e3a5f]">{phase === "review" ? "Drop to add as exhibit" : "Drop PDF to start filing"}</div>
            <div className="text-[12px] text-[#8a8a8a] mt-1">Release to upload</div>
          </div>
        </div>
      )}
      {/* Top bar */}
      <header className="bg-white border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3 sm:gap-6">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-7 h-7 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[10px] font-bold">E</div>
              <span className="text-[15px] font-semibold tracking-tight text-[#1a1a1a] hidden sm:inline">ECFiler</span>
            </Link>
            <div className="h-5 w-px bg-[#e8e5e0]" />
            <button onClick={() => setShowHistory(!showHistory)} className="text-[13px] text-[#525252] hover:text-[#1a1a1a] transition font-medium" aria-label={`Filing history — ${history.length} filings`} aria-expanded={showHistory}>
              History {history.length > 0 && <span className="text-[10px] bg-[#f0eee9] px-1.5 py-0.5 rounded-full ml-1">{history.length}</span>}
            </button>
            <button onClick={() => setShowCourts(!showCourts)} className="text-[13px] text-[#525252] hover:text-[#1a1a1a] transition font-medium" aria-label="Search federal courts" aria-expanded={showCourts}>Courts</button>
          </div>
          <div className="flex items-center gap-3 sm:gap-4">
            {backendOk !== null && (
              <div className="flex items-center gap-1.5" title={backendOk ? "Backend connected" : "Backend unreachable"}>
                <span className={`w-1.5 h-1.5 rounded-full ${backendOk ? "bg-[#15803d]" : "bg-[#b91c1c] animate-pulse"}`} />
                <span className="text-[10px] text-[#c4c4c4] hidden sm:inline">{backendOk ? "Connected" : "Offline"}</span>
              </div>
            )}
            <kbd className="hidden sm:flex items-center gap-1 text-[10px] text-[#c4c4c4] bg-[#f5f3ee] px-2 py-1 rounded-lg border border-[#e8e5e0] cursor-pointer hover:text-[#8a8a8a] hover:border-[#d4d0ca] transition" title="Command palette" onClick={() => { const e = new KeyboardEvent("keydown", { key: "k", metaKey: true }); window.dispatchEvent(e); }}>
              <span className="font-mono">&#8984;K</span>
            </kbd>
            <Link href="/settings" className="text-[13px] text-[#8a8a8a] hover:text-[#525252] transition hidden sm:inline">Settings</Link>
            <UserButton appearance={{ elements: { avatarBox: "w-7 h-7" } }} />
          </div>
        </div>
      </header>

      {/* Main workspace */}
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 sm:py-10 transition-all duration-500">

        {/* Ready state */}
        {phase === "ready" && (
          <div>
            {/* Two-column layout */}
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-8">
              {/* Drop zone — 3 cols */}
              <div className="lg:col-span-3">
                <div
                  role="button"
                  tabIndex={0}
                  aria-label="Upload PDF for filing — click or drag and drop"
                  className="bg-white border border-[#d4d0ca] rounded-2xl p-10 text-center cursor-pointer hover:border-[#1e3a5f] hover:shadow-lg hover:shadow-[#1e3a5f]/5 transition-all group h-full flex flex-col items-center justify-center min-h-[260px] shadow-sm drop-glow"
                  onClick={() => fileRef.current?.click()}
                  onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fileRef.current?.click(); } }}
                  onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add("!border-[#1e3a5f]", "!bg-[#f0f4fa]", "!shadow-lg"); }}
                  onDragLeave={(e) => { e.currentTarget.classList.remove("!border-[#1e3a5f]", "!bg-[#f0f4fa]", "!shadow-lg"); }}
                  onDrop={(e) => {
                    e.preventDefault(); e.currentTarget.classList.remove("!border-[#1e3a5f]", "!bg-[#f0f4fa]", "!shadow-lg");
                    const files = Array.from(e.dataTransfer.files).filter(f => f.type === "application/pdf" || f.name.endsWith(".pdf"));
                    if (files.length === 0) return;
                    const rest = files.slice(1);
                    handleFile(files[0], rest);
                    if (rest.length > 0) {
                      const exhibitFiles = new DataTransfer();
                      rest.forEach(f => exhibitFiles.items.add(f));
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
                  <div className="text-[13px] text-[#8a8a8a] mb-1">or click to browse</div>
                  <div className="text-[11px] text-[#c4c4c4] mb-4">Drop multiple files — first is the main document, rest become exhibits</div>
                  <div className="flex flex-wrap justify-center gap-1.5">
                    {["Motions", "Briefs", "Complaints", "Notices", "Petitions", "Exhibits"].map((t) => (
                      <span key={t} className="text-[10px] px-2 py-0.5 bg-[#f0eee9] text-[#8a8a8a] rounded-md font-medium">{t}</span>
                    ))}
                  </div>
                  <input ref={fileRef} type="file" accept=".pdf" multiple className="hidden" aria-label="Select PDF files for filing" onChange={(e) => {
                    if (!e.target.files?.length) return;
                    const restFiles = Array.from(e.target.files).slice(1);
                    handleFile(e.target.files[0], restFiles);
                    if (restFiles.length > 0) {
                      const rest = new DataTransfer();
                      restFiles.forEach(f => rest.items.add(f));
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
                      { n: "3", text: "Review, stage the package, and file it yourself on CM/ECF" },
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
                    <Link href="/drafts" className="block px-3 py-2 rounded-lg text-[12px] text-[#525252] hover:bg-[#f5f3ee] hover:text-[#1a1a1a] transition flex items-center gap-2">
                      <span className="text-[#8a8a8a]">📝</span> Saved drafts
                    </Link>
                    <button onClick={() => setShowHistory(true)} className="w-full text-left px-3 py-2 rounded-lg text-[12px] text-[#525252] hover:bg-[#f5f3ee] hover:text-[#1a1a1a] transition flex items-center gap-2">
                      <span className="text-[#8a8a8a]">📋</span> Filing history
                    </button>
                  </div>
                </div>

                {/* Keyboard shortcuts */}
                <div className="bg-white border border-[#e8e5e0] rounded-2xl p-5 shadow-sm">
                  <div className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-3">Keyboard Shortcuts</div>
                  <div className="space-y-2">
                    {[
                      { keys: ["⌘", "K"], label: "Command palette" },
                      { keys: ["⌘", "↵"], label: "Confirm & stage" },
                      { keys: ["Esc"], label: "Cancel / close" },
                    ].map(({ keys, label }) => (
                      <div key={label} className="flex items-center justify-between">
                        <span className="text-[11px] text-[#525252]">{label}</span>
                        <div className="flex items-center gap-1">
                          {keys.map((k) => (
                            <kbd key={k} className="px-1.5 py-0.5 text-[10px] font-mono bg-[#f5f3ee] text-[#8a8a8a] border border-[#e8e5e0] rounded">{k}</kbd>
                          ))}
                        </div>
                      </div>
                    ))}
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
                    <div className="text-[12px] text-[#8a8a8a] font-mono mt-0.5">{fileName}{fileSize > 0 ? ` · ${(fileSize / 1024 / 1024).toFixed(1)}MB` : ""}</div>
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
              <div className="px-6 py-4" role="log" aria-live="polite" aria-label="Analysis progress">
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
                <p className="text-[13px] text-[#525252]">AI has analyzed your document. Verify every field below — you will submit the staged package on CM/ECF yourself.</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className={`text-[12px] px-3 py-1 rounded-full font-semibold border ${
                  filing.completeness_score >= 80 ? "bg-[#f0fdf4] text-[#15803d] border-[#bbf7d0]" : "bg-[#fffbeb] text-[#b45309] border-[#fde68a]"
                }`}>{filing.completeness_score}% confidence</span>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
              {[
                { label: "PDF", value: `${filing.pdf_size_mb?.toFixed(1)}MB · ${filing.pdf_pages}p${filing.pdf_is_pdfa ? " · PDF/A" : ""}`, ok: filing.pdf_valid },
                { label: "Redaction", value: filing.redaction_issues === 0 ? "Clean" : `${filing.redaction_issues} issue(s)`, ok: filing.redaction_issues === 0 },
                { label: "Fee", value: isIfp ? "$0 (fee waiver requested)" : (filing.filing_fee_text || (filing.filing_fee ? `$${filing.filing_fee}` : "None")), ok: true },
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
                  Your document is not PDF/A — convert it before you submit on CM/ECF.
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
                {filing.filing_fee ? (
                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition ${isIfp ? "bg-[#1e3a5f] border-[#1e3a5f]" : "border-[#d4d0ca] group-hover:border-[#8a8a8a]"}`}>
                      {isIfp && <span className="text-white text-[10px] font-bold">✓</span>}
                    </div>
                    <input type="checkbox" checked={isIfp} onChange={(e) => setIsIfp(e.target.checked)} className="hidden" />
                    <div>
                      <div className="text-[13px] font-medium text-[#1a1a1a]">Request fee waiver (IFP)</div>
                      <div className="text-[11px] text-[#8a8a8a]">
                        {isIfp ? "$0 (fee waiver requested)" : "File in forma pauperis — requires pending IFP application"}
                      </div>
                    </div>
                  </label>
                ) : null}
              </div>
            </div>

            {/* Exhibits & Attachments */}
            <div className="bg-white rounded-2xl border border-[#e8e5e0] overflow-hidden shadow-sm mb-5">
              <div className="px-5 py-3 border-b border-[#f0eee9] flex items-center justify-between">
                <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Attachments &amp; Exhibits</span>
                <button onClick={() => exhibitRef.current?.click()} className="text-[11px] text-[#1e3a5f] font-semibold hover:underline">+ Add files</button>
              </div>
              <input ref={exhibitRef} type="file" accept=".pdf" multiple className="hidden" aria-label="Select exhibit PDFs" onChange={(e) => e.target.files && addExhibits(e.target.files)} />
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
                  {exhibits.map((ex, i) => (
                    <div key={ex.id} className="flex items-center gap-3 p-3 bg-[#fafaf8] rounded-xl border border-[#f0eee9] group">
                      <div className="flex flex-col gap-0.5 shrink-0">
                        <button
                          onClick={() => moveExhibit(i, -1)}
                          disabled={i === 0}
                          aria-label={`Move ${ex.label} up`}
                          className="w-5 h-5 flex items-center justify-center rounded text-[#8a8a8a] hover:text-[#1e3a5f] hover:bg-[#f0eee9] disabled:opacity-20 disabled:cursor-not-allowed text-[11px]"
                        >&#9650;</button>
                        <button
                          onClick={() => moveExhibit(i, 1)}
                          disabled={i === exhibits.length - 1}
                          aria-label={`Move ${ex.label} down`}
                          className="w-5 h-5 flex items-center justify-center rounded text-[#8a8a8a] hover:text-[#1e3a5f] hover:bg-[#f0eee9] disabled:opacity-20 disabled:cursor-not-allowed text-[11px]"
                        >&#9660;</button>
                      </div>
                      <div className="w-9 h-9 bg-[#1e3a5f] text-white rounded-lg flex items-center justify-center text-[11px] font-bold shrink-0">{ex.label.split(" ")[1]}</div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <input
                            type="text"
                            value={ex.label}
                            onChange={(e) => updateExhibitLabel(ex.id, e.target.value)}
                            aria-label="Exhibit label"
                            className="w-24 text-[11px] font-semibold text-[#525252] bg-transparent outline-none border-b border-transparent focus:border-[#1e3a5f] transition"
                          />
                          <input
                            type="text"
                            value={ex.description}
                            onChange={(e) => updateExhibitDesc(ex.id, e.target.value)}
                            className="flex-1 text-[13px] font-medium text-[#1a1a1a] bg-transparent outline-none border-b border-transparent focus:border-[#1e3a5f] transition pb-0.5"
                            placeholder="Description..."
                          />
                        </div>
                        <div className="text-[10px] text-[#8a8a8a] font-mono mt-0.5 flex items-center gap-3">
                          <span>{ex.file.name} &middot; {(ex.file.size / 1024 / 1024).toFixed(1)}MB</span>
                          <label className="flex items-center gap-1 cursor-pointer select-none">
                            <input
                              type="checkbox"
                              checked={!!ex.sealed}
                              onChange={() => toggleExhibitSealed(ex.id)}
                              className="w-3 h-3 accent-[#1e3a5f]"
                            />
                            <span className="text-[10px] text-[#525252]">Sealed</span>
                          </label>
                        </div>
                      </div>
                      <button onClick={() => removeExhibit(ex.id)} aria-label="Remove exhibit" className="text-[#c4c4c4] hover:text-[#b91c1c] transition opacity-0 group-hover:opacity-100 text-lg shrink-0">&times;</button>
                    </div>
                  ))}
                  {filing?.exhibit_issues && filing.exhibit_issues.length > 0 && (
                    <div className="rounded-xl border border-[#fecaca] bg-[#fef2f2] px-3 py-2 text-[11px] text-[#b91c1c]">
                      <div className="font-semibold mb-1">Exhibit validation issues:</div>
                      <ul className="list-disc list-inside space-y-0.5">
                        {filing.exhibit_issues.map((msg, idx) => (<li key={idx}>{msg}</li>))}
                      </ul>
                    </div>
                  )}
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

            {/* AI Safety Gates — 3 verification passes */}
            <div className="bg-white rounded-2xl border-2 border-[#e8e5e0] overflow-hidden shadow-sm mb-5">
              <div className="px-5 py-3 border-b border-[#f0eee9] bg-[#fafaf8] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#1e3a5f]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" /></svg>
                  <span className="text-[11px] font-bold text-[#1e3a5f] uppercase tracking-wide">AI Safety Verification</span>
                </div>
                <span className="text-[10px] text-[#8a8a8a] font-medium">3-pass check</span>
              </div>

              {/* Gate 1: Document Integrity */}
              <div className="px-5 py-4 border-b border-[#f0eee9]">
                <div className="flex items-center gap-2 mb-3">
                  <div className={`w-6 h-6 rounded-lg flex items-center justify-center text-[10px] font-bold ${filing.pdf_valid ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#fef2f2] text-[#b91c1c]"}`}>
                    {filing.pdf_valid ? "✓" : "×"}
                  </div>
                  <span className="text-[12px] font-bold text-[#1a1a1a]">Pass 1 — Document Integrity</span>
                  <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${filing.pdf_valid ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#fef2f2] text-[#b91c1c]"}`}>{filing.pdf_valid ? "PASSED" : "FAILED"}</span>
                </div>
                <div className="pl-8 space-y-1.5">
                  {[
                    { ok: filing.pdf_valid, text: `PDF valid — ${filing.pdf_size_mb?.toFixed(1)}MB, ${filing.pdf_pages} pages${filing.pdf_is_pdfa ? ", PDF/A compliant" : ""}` },
                    { ok: filing.redaction_issues === 0, text: filing.redaction_issues === 0 ? "No unredacted PII (Rule 5.2 scan passed)" : `${filing.redaction_issues} potential redaction issue(s) — review required`, warn: filing.redaction_issues > 0 },
                    ...(filing.attorney_name ? [{ ok: true, text: `Signature block verified: ${filing.attorney_name}` }] : [{ ok: false, text: "No signature block detected — verify before filing", warn: true }]),
                  ].map(({ ok, text, warn }) => (
                    <div key={text} className="flex items-center gap-2">
                      <span className={`text-[10px] ${warn ? "text-[#b45309]" : ok ? "text-[#15803d]" : "text-[#b91c1c]"}`}>{warn ? "⚠" : ok ? "✓" : "✗"}</span>
                      <span className="text-[12px] text-[#525252]">{text}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Gate 2: AI Cross-Reference */}
              <div className="px-5 py-4 border-b border-[#f0eee9]">
                <div className="flex items-center gap-2 mb-3">
                  <div className={`w-6 h-6 rounded-lg flex items-center justify-center text-[10px] font-bold ${filing.completeness_score >= 60 && filing.event_code ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#fffbeb] text-[#b45309]"}`}>
                    {filing.completeness_score >= 60 && filing.event_code ? "✓" : "!"}
                  </div>
                  <span className="text-[12px] font-bold text-[#1a1a1a]">Pass 2 — AI Cross-Reference</span>
                  <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${filing.completeness_score >= 60 ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#fffbeb] text-[#b45309]"}`}>{filing.completeness_score >= 60 ? "PASSED" : "REVIEW"}</span>
                </div>
                <div className="pl-8 space-y-1.5">
                  {[
                    ...(filing.case_number ? [{ ok: true, text: `Case number ${filing.case_number} extracted and cross-referenced` }] : [{ ok: false, text: "Case number could not be verified", warn: true }]),
                    ...(filing.event_code ? [{ ok: true, text: `Event code ${eventCodeOverride || filing.event_code} matched to document type "${filing.document_type}"` }] : [{ ok: false, text: "Event code could not be determined", warn: true }]),
                    { ok: filing.completeness_score >= 80, text: `AI confidence: ${filing.completeness_score}% — ${filing.completeness_score >= 80 ? "high confidence extraction" : filing.completeness_score >= 60 ? "moderate confidence — verify fields manually" : "low confidence — manual review required"}`, warn: filing.completeness_score < 80 },
                    { ok: filing.has_certificate_of_service !== false, text: filing.has_certificate_of_service ? "Certificate of service detected in document" : "No certificate of service found — add one if required", warn: !filing.has_certificate_of_service },
                  ].map(({ ok, text, warn }) => (
                    <div key={text} className="flex items-center gap-2">
                      <span className={`text-[10px] ${warn ? "text-[#b45309]" : ok ? "text-[#15803d]" : "text-[#b91c1c]"}`}>{warn ? "⚠" : ok ? "✓" : "✗"}</span>
                      <span className="text-[12px] text-[#525252]">{text}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Gate 3: Filing Readiness */}
              <div className="px-5 py-4">
                <div className="flex items-center gap-2 mb-3">
                  <div className={`w-6 h-6 rounded-lg flex items-center justify-center text-[10px] font-bold ${filing.ready ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#fef2f2] text-[#b91c1c]"}`}>
                    {filing.ready ? "✓" : "×"}
                  </div>
                  <span className="text-[12px] font-bold text-[#1a1a1a]">Pass 3 — Filing Readiness</span>
                  <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${filing.ready ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#fef2f2] text-[#b91c1c]"}`}>{filing.ready ? "READY" : "NOT READY"}</span>
                </div>
                <div className="pl-8 space-y-1.5">
                  {[
                    { ok: !!filing.court_id, text: filing.court_id ? `Court ${filing.court_id.toUpperCase()} identified and valid` : "Court not identified" },
                    { ok: !!filing.filing_party, text: filing.filing_party ? `Filing party: ${filing.filing_party}` : "Filing party not determined" },
                    { ok: !!docketText, text: docketText ? `Docket text set (${docketText.length} chars)` : "Docket text is empty — enter text above", warn: !docketText },
                    ...(filing.has_proposed_order ? [{ ok: true, text: "Proposed order detected and flagged" }] : []),
                    ...(filing.is_response && filing.responds_to ? [{ ok: true, text: `Response to: ${filing.responds_to}${filing.responds_to_docket ? ` (Docket #${filing.responds_to_docket})` : ""}` }] : []),
                    { ok: filing.ready, text: filing.ready ? "All required fields present — cleared for filing" : "Missing required fields — cannot file", warn: !filing.ready },
                  ].map(({ ok, text, warn }) => (
                    <div key={text} className="flex items-center gap-2">
                      <span className={`text-[10px] ${warn ? "text-[#b45309]" : ok ? "text-[#15803d]" : "text-[#b91c1c]"}`}>{warn ? "⚠" : ok ? "✓" : "✗"}</span>
                      <span className="text-[12px] text-[#525252]">{text}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Warnings */}
            {filing.warnings?.filter(w => !w.includes("certificate")).map((w) => (
              <div key={w} className="flex gap-2 px-4 py-3 bg-[#fffbeb] border border-[#fde68a] rounded-xl text-[13px] text-[#92400e] mb-3">
                <span className="font-bold">!</span> {w}
              </div>
            ))}

            {/* Sealed content — hard stop. The hosted service never stages or
                submits sealed documents. */}
            {hasSealedContent && (
              <div className="border-2 border-[#b45309]/40 bg-[#fffbeb] rounded-2xl p-6">
                <div className="flex items-start gap-3">
                  <svg className="w-6 h-6 text-[#b45309] shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.8}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                  </svg>
                  <div>
                    <div className="text-[15px] font-bold text-[#92400e]">Sealed filings can&apos;t go through the hosted service</div>
                    <div className="text-[13px] text-[#92400e]/90 mt-1.5 leading-relaxed">
                      ECFiler&apos;s servers never handle documents a court has ordered protected — that includes
                      staging them here. Nothing about this filing has been saved. To file under seal:
                    </div>
                    <ul className="text-[13px] text-[#92400e]/90 mt-2 space-y-1 list-disc pl-5">
                      <li>Use the ECFiler CLI on your own machine, which files locally under your control, or</li>
                      <li>File conventionally under seal per the court&apos;s local rule and sealing procedure.</li>
                    </ul>
                    <div className="text-[12px] text-[#92400e]/70 mt-3">
                      Unchecking the sealed flags will re-enable hosted preparation for public filings.
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Actions — Step 1: Review gate */}
            {!showConfirmGate && !hasSealedContent && (
              <div className="bg-gradient-to-r from-[#0f1f35] to-[#1e3a5f] rounded-2xl p-6 shadow-xl shadow-[#1e3a5f]/15">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-[14px] font-bold text-white">{filing.ready ? "All 3 safety checks passed" : "Missing required fields"}</div>
                    <div className="text-[12px] text-white/50 mt-0.5">
                      {filing.ready
                        ? `${filing.court_id?.toUpperCase()} · ${filing.case_number}${exhibits.length > 0 ? ` · ${exhibits.length} attachment${exhibits.length > 1 ? "s" : ""}` : ""}${filing.filing_fee ? ` · $${filing.filing_fee} fee` : ""}`
                        : "Review the issues above."}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button onClick={reset} className="px-4 py-2.5 text-[12px] text-white/40 hover:text-white/70 transition" aria-label="Cancel filing">Cancel</button>
                    <button
                      onClick={() => {
                        const draft = { filing, docketText, eventCodeOverride, isSealed, isRedacted, exhibits: exhibits.map(e => ({ label: e.label, description: e.description })), savedAt: new Date().toISOString() };
                        localStorage.setItem(`ecfiler_draft_${Date.now()}`, JSON.stringify(draft));
                        toast("Draft saved — find it in Drafts", "success");
                        setTimeout(() => reset(), 1200);
                      }}
                      className="px-4 py-2.5 text-[12px] text-white/50 hover:text-white transition border border-white/10 rounded-xl hover:bg-white/5"
                      aria-label="Save as draft for later"
                    >Save Draft</button>
                    <button
                      onClick={() => { setShowConfirmGate(true); setAttorneyAttest(false); }}
                      disabled={!filing.ready}
                      className="px-8 py-3 bg-white text-[#1e3a5f] text-[14px] font-bold rounded-xl hover:bg-[#f0f4fa] disabled:opacity-20 disabled:cursor-not-allowed transition shadow-lg"
                      aria-label={filing.ready ? "Proceed to final confirmation" : "Cannot stage — missing required fields"}
                    >
                      Proceed to Stage &rarr;
                    </button>
                  </div>
                </div>
                {filing.ready && (
                  <div className="mt-3 flex items-center gap-2 text-[10px] text-white/30">
                    <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-white/40 font-mono border border-white/10">⌘</kbd>
                    <span>+</span>
                    <kbd className="px-1.5 py-0.5 bg-white/10 rounded text-white/40 font-mono border border-white/10">Enter</kbd>
                    <span>to stage</span>
                  </div>
                )}
              </div>
            )}

            {/* Actions — Step 2: Final confirmation gate */}
            {showConfirmGate && !hasSealedContent && (
              <div className="border-2 border-[#b91c1c]/30 rounded-2xl overflow-hidden shadow-xl">
                {/* Header */}
                <div className="bg-gradient-to-r from-[#7f1d1d] to-[#991b1b] px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-[16px] font-bold text-white">Final Confirmation Required</div>
                      <div className="text-[12px] text-white/60">ECFiler stages the package — you submit it on CM/ECF. What you file becomes part of the permanent court record.</div>
                    </div>
                  </div>
                </div>

                {/* Filing summary */}
                <div className="bg-white px-6 py-5">
                  <div className="text-[10px] font-bold text-[#8a8a8a] uppercase tracking-wide mb-3">You are about to stage</div>
                  <div className="bg-[#fafaf8] border border-[#e8e5e0] rounded-xl p-4 mb-4 space-y-2">
                    <div className="flex justify-between">
                      <span className="text-[12px] text-[#8a8a8a]">Court</span>
                      <span className="text-[12px] font-mono font-semibold text-[#1a1a1a]">{filing.court_id?.toUpperCase()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[12px] text-[#8a8a8a]">Case</span>
                      <span className="text-[12px] font-mono font-semibold text-[#1a1a1a]">{filing.case_number}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[12px] text-[#8a8a8a]">Event Code</span>
                      <span className="text-[12px] font-mono font-semibold text-[#1a1a1a]">{eventCodeOverride || filing.event_code} — {filing.document_type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[12px] text-[#8a8a8a]">Filing Party</span>
                      <span className="text-[12px] font-semibold text-[#1a1a1a]">{filing.filing_party || "—"}</span>
                    </div>
                    {filing.filing_fee ? (
                      <div className="flex justify-between items-center py-1 -mx-1 px-2 rounded bg-[#fffbeb] border border-[#fde68a]">
                        <span className="text-[12px] font-semibold text-[#b45309]">Filing Fee</span>
                        <span className="text-[14px] font-bold text-[#b45309]">{isIfp ? "$0 (fee waiver requested)" : (filing.filing_fee_text || `$${filing.filing_fee}`)}</span>
                      </div>
                    ) : null}
                    {isSealed && (
                      <div className="flex justify-between">
                        <span className="text-[12px] text-[#8a8a8a]">Sealed</span>
                        <span className="text-[12px] font-bold text-[#b91c1c]">Yes — filed under seal</span>
                      </div>
                    )}
                    {isRedacted && (
                      <div className="flex justify-between">
                        <span className="text-[12px] text-[#8a8a8a]">Redacted</span>
                        <span className="text-[12px] font-semibold text-[#1a1a1a]">Redacted version per Rule 5.2</span>
                      </div>
                    )}
                  </div>

                  {/* Exact docket text as it will appear on CM/ECF */}
                  <div className="mb-4">
                    <div className="text-[10px] font-bold text-[#8a8a8a] uppercase tracking-wide mb-2">Exact docket text to be entered</div>
                    <div className="border-2 border-[#1e3a5f]/20 rounded-xl overflow-hidden">
                      <div className="bg-[#0f1f35] px-4 py-2 flex items-center gap-2">
                        <svg className="w-3.5 h-3.5 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 011.037-.443 48.282 48.282 0 005.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" /></svg>
                        <span className="text-[10px] text-white/50 font-medium">CM/ECF Docket Entry Preview</span>
                      </div>
                      <div className="bg-white p-4">
                        <p className="text-[14px] text-[#1a1a1a] font-medium leading-relaxed">
                          {docketText || filing.event_description}
                        </p>
                        <div className="text-[11px] text-[#8a8a8a] mt-2">
                          Filed by {filing.filing_party || "Unknown"}.
                          {filing.case_number && <span> ({filing.case_number})</span>}
                          {exhibits.length > 0 && (
                            <span> (Attachments: {exhibits.map((e, i) => `# ${i + 1} ${e.label}`).join(", ")})</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Documents being filed */}
                  <div className="mb-4">
                    <div className="text-[10px] font-bold text-[#8a8a8a] uppercase tracking-wide mb-2">Documents to be filed</div>
                    <div className="border border-[#e8e5e0] rounded-xl overflow-hidden">
                      {/* Main document */}
                      <div className="flex items-center gap-3 px-4 py-3 bg-[#fafaf8]">
                        <div className="w-8 h-8 bg-[#b91c1c] rounded-lg flex items-center justify-center shrink-0">
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M7 2C5.9 2 5 2.9 5 4v16c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V8l-6-6H7zm7 7V3.5L18.5 8H14zM9 13h6v2H9v-2zm0 4h4v2H9v-2z" /></svg>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-[13px] font-semibold text-[#1a1a1a] truncate">{fileName}</div>
                          <div className="text-[10px] text-[#8a8a8a]">Main document &middot; {filing.pdf_size_mb?.toFixed(1)}MB &middot; {filing.pdf_pages} pages{filing.pdf_is_pdfa ? " · PDF/A" : ""}</div>
                        </div>
                        <span className="text-[10px] px-2 py-0.5 bg-[#f0fdf4] text-[#15803d] rounded-full font-semibold shrink-0">Validated</span>
                      </div>
                      {/* Exhibits */}
                      {exhibits.map((ex, i) => (
                        <div key={ex.id} className="flex items-center gap-3 px-4 py-3 border-t border-[#f0eee9]">
                          <div className="w-8 h-8 bg-[#1e3a5f] rounded-lg flex items-center justify-center text-white text-[11px] font-bold shrink-0">{ex.label.split(" ")[1]}</div>
                          <div className="flex-1 min-w-0">
                            <div className="text-[13px] font-medium text-[#1a1a1a] truncate">{ex.description || ex.file.name}</div>
                            <div className="text-[10px] text-[#8a8a8a]">{ex.label} &middot; {(ex.file.size / 1024 / 1024).toFixed(1)}MB</div>
                          </div>
                          <span className="text-[10px] px-2 py-0.5 bg-[#f5f3ee] text-[#8a8a8a] rounded-full font-medium shrink-0">Attachment #{i + 1}</span>
                        </div>
                      ))}
                      {exhibits.length === 0 && (
                        <div className="px-4 py-2 border-t border-[#f0eee9] text-[11px] text-[#c4c4c4]">No additional attachments</div>
                      )}
                    </div>
                  </div>

                  {/* AI verification summary */}
                  <div className="flex items-center gap-3 p-3 bg-[#f0fdf4] border border-[#bbf7d0] rounded-xl mb-4">
                    <svg className="w-5 h-5 text-[#15803d] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                    </svg>
                    <div>
                      <div className="text-[12px] font-semibold text-[#15803d]">AI verified — 3 safety passes completed</div>
                      <div className="text-[11px] text-[#166534]">Document integrity, cross-reference, and filing readiness checks all passed.</div>
                    </div>
                  </div>

                  {/* Attorney attestation */}
                  <label className="flex items-start gap-3 cursor-pointer group p-4 rounded-xl border-2 border-[#e8e5e0] hover:border-[#1e3a5f]/30 transition mb-4">
                    <div className={`w-5 h-5 mt-0.5 rounded border-2 flex items-center justify-center transition shrink-0 ${attorneyAttest ? "bg-[#1e3a5f] border-[#1e3a5f]" : "border-[#d4d0ca] group-hover:border-[#8a8a8a]"}`}>
                      {attorneyAttest && <span className="text-white text-[10px] font-bold">✓</span>}
                    </div>
                    <input type="checkbox" checked={attorneyAttest} onChange={(e) => setAttorneyAttest(e.target.checked)} className="hidden" />
                    <div>
                      <div className="text-[13px] font-semibold text-[#1a1a1a]">Attorney Attestation</div>
                      <div className="text-[12px] text-[#525252] leading-relaxed mt-1">
                        I have reviewed the document, docket text, event code, and all filing details above.
                        I am preparing this filing for submission to <span className="font-semibold">{filing.court_id?.toUpperCase()}</span> in
                        case <span className="font-mono font-semibold">{filing.case_number}</span>, and
                        I take responsibility for what is filed.
                      </div>
                    </div>
                  </label>

                  {/* Action buttons */}
                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => { setShowConfirmGate(false); setAttorneyAttest(false); }}
                      className="px-5 py-2.5 text-[13px] text-[#525252] hover:text-[#1a1a1a] transition font-medium"
                    >
                      &larr; Go Back
                    </button>
                    <button
                      onClick={handleConfirm}
                      disabled={!attorneyAttest}
                      className="px-10 py-3.5 bg-[#b91c1c] text-white text-[14px] font-bold rounded-xl hover:bg-[#991b1b] disabled:opacity-20 disabled:cursor-not-allowed transition shadow-lg disabled:shadow-none"
                      aria-label={attorneyAttest ? `Stage filing package for ${filing.court_id?.toUpperCase()}` : "Check the attestation box to proceed"}
                    >
                      Stage Filing Package
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Staging — assembling the package */}
        {phase === "staging" && (
          <div className="max-w-xl mx-auto py-16">
            <div className="bg-white rounded-2xl border border-[#e8e5e0] shadow-sm px-8 py-12 text-center">
              <div className="w-10 h-10 border-[3px] border-[#1e3a5f] border-t-transparent rounded-full animate-spin mx-auto mb-5" />
              <div className="text-[16px] font-semibold text-[#1a1a1a]">Assembling your filing package&hellip;</div>
              <div className="text-[12px] text-[#8a8a8a] mt-1.5">Validating filing details and generating step-by-step instructions</div>
            </div>
          </div>
        )}

        {/* Done — package staged, the human files it */}
        {phase === "done" && stagedPackage && (
          <div className="max-w-xl mx-auto py-8">
            {/* Success header */}
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-gradient-to-br from-[#f0fdf4] to-[#dcfce7] rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-green-200/30">
                <svg className="w-10 h-10 text-[#15803d]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
              </div>
              <h2 className="text-[24px] font-bold text-[#1a1a1a] mb-2">Package staged — ready for you to file</h2>
              <p className="text-[14px] text-[#525252]">ECFiler prepared and validated everything. You submit it on CM/ECF with your own credentials.</p>
            </div>

            {/* Court card */}
            <div className="bg-white rounded-2xl border border-[#e8e5e0] shadow-sm p-5 mb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="text-[15px] font-bold text-[#1a1a1a]">{stagedPackage.court_name}</div>
                <div className="text-[12px] text-[#8a8a8a] font-mono mt-0.5">{stagedPackage.case_number}</div>
              </div>
              <a
                href={stagedPackage.ecf_login_url}
                target="_blank"
                rel="noopener"
                className="px-6 py-3 bg-[#1e3a5f] text-white text-[13px] font-bold rounded-xl hover:bg-[#162a47] transition shadow-lg shadow-[#1e3a5f]/20 shrink-0 text-center"
              >
                Open {stagedPackage.court_id?.toUpperCase()} CM/ECF &rarr;
              </a>
            </div>

            {/* Instructions */}
            {stagedPackage.instructions?.length > 0 && (
              <div className="bg-white rounded-2xl border border-[#e8e5e0] shadow-sm overflow-hidden mb-5">
                <div className="px-5 py-3 border-b border-[#f0eee9] bg-[#fafaf8]">
                  <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">How to file this package</span>
                </div>
                <ol className="p-5 space-y-3">
                  {stagedPackage.instructions.map((step, i) => (
                    <li key={i} className="flex gap-3">
                      <div className="w-5 h-5 bg-[#1e3a5f] text-white rounded-full flex items-center justify-center text-[9px] font-bold shrink-0 mt-0.5">{i + 1}</div>
                      <div className="text-[13px] text-[#525252] leading-relaxed">{step}</div>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* Docket text */}
            <div className="bg-white rounded-2xl border border-[#e8e5e0] shadow-sm overflow-hidden mb-5">
              <div className="px-5 py-3 border-b border-[#f0eee9] bg-[#fafaf8] flex items-center justify-between">
                <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Docket text — paste into CM/ECF</span>
                <button onClick={() => copyText(stagedPackage.docket_text, "Docket text")} className="text-[11px] text-[#1e3a5f] font-semibold hover:underline">Copy</button>
              </div>
              <div className="p-5">
                <p className="font-mono text-[13px] text-[#1a1a1a] leading-relaxed bg-[#fafaf8] border border-[#f0eee9] rounded-xl p-4 whitespace-pre-wrap">{stagedPackage.docket_text}</p>
              </div>
            </div>

            {/* Filing details */}
            <div className="bg-white rounded-2xl border border-[#e8e5e0] shadow-sm overflow-hidden mb-5">
              {[
                { label: "Event Code", value: `${stagedPackage.event_code} — ${stagedPackage.event_description}`, mono: true },
                { label: "Filing Party", value: stagedPackage.filing_party },
                ...(stagedPackage.fee_text ? [{ label: "Fee", value: stagedPackage.fee_text }] : []),
                ...(stagedPackage.exhibits?.length > 0 ? [{ label: "Exhibits", value: stagedPackage.exhibits.map((e) => `${e.label}${e.description ? ` — ${e.description}` : ""}`).join("; ") }] : []),
              ].filter((f) => f.value).map(({ label, value, mono }) => (
                <div key={label} className="flex px-5 py-3 border-b border-[#f0eee9] last:border-0">
                  <div className="w-[110px] shrink-0 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide pt-0.5">{label}</div>
                  <div className={`text-[13px] text-[#1a1a1a] font-medium ${mono ? "font-mono" : ""}`}>{value}</div>
                </div>
              ))}
            </div>

            {/* Pre-filing checklist */}
            {stagedPackage.checklist?.length > 0 && (
              <div className="bg-white rounded-2xl border border-[#e8e5e0] shadow-sm overflow-hidden mb-5">
                <div className="px-5 py-3 border-b border-[#f0eee9] bg-[#fafaf8]">
                  <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Pre-filing checklist</span>
                </div>
                <div className="p-5 space-y-2.5">
                  {stagedPackage.checklist.map((item, i) => (
                    <label key={i} className="flex items-start gap-3 cursor-pointer">
                      <input type="checkbox" className="w-4 h-4 mt-0.5 accent-[#1e3a5f] shrink-0" />
                      <span className="text-[13px] text-[#525252] leading-relaxed">
                        {item.text}
                        {item.required && <span className="ml-2 text-[9px] px-1.5 py-0.5 bg-[#fef2f2] text-[#b91c1c] rounded font-bold uppercase align-middle">Required</span>}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Stage code — CLI handoff */}
            <div className="bg-[#0f1f35] rounded-2xl p-5 mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-semibold text-white/50 uppercase tracking-wide">Prefer to file from the terminal?</span>
                <button onClick={() => copyText(`ecfiler stage-pull ${stagedPackage.stage_code}`, "Command")} className="text-[11px] text-white/60 font-semibold hover:text-white transition">Copy</button>
              </div>
              <code className="block font-mono text-[13px] text-[#7dd3fc] bg-white/5 border border-white/10 rounded-lg px-4 py-3 overflow-x-auto">ecfiler stage-pull {stagedPackage.stage_code}</code>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-center gap-3">
              <button onClick={reset} className="px-8 py-3 bg-[#1e3a5f] text-white text-[14px] font-semibold rounded-xl hover:bg-[#162a47] transition shadow-lg shadow-[#1e3a5f]/20">
                Start another filing
              </button>
              <button onClick={downloadPackage} className="px-5 py-3 border border-[#e8e5e0] text-[13px] text-[#525252] font-medium rounded-xl hover:bg-[#fafaf8] transition">
                Download package (JSON)
              </button>
            </div>

            {/* Disclaimer */}
            <p className="text-[10px] text-[#c4c4c4] text-center mt-6">
              Nothing has been filed yet. ECFiler staged this package — you complete the filing on CM/ECF, and the court sends the official Notice of Electronic Filing (NEF).
            </p>
          </div>
        )}

        {/* Error */}
        {phase === "error" && (
          <div className="max-w-md mx-auto text-center py-12">
            <div className="w-16 h-16 bg-[#fef2f2] rounded-2xl flex items-center justify-center mx-auto mb-5">
              <svg className="w-8 h-8 text-[#b91c1c]" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>
            </div>
            <h2 className="text-[18px] font-bold text-[#1a1a1a] mb-2">Something went wrong</h2>
            <p className="text-[14px] text-[#525252] mb-4">{error}</p>
            {error.includes("Failed to fetch") || error.includes("network") ? (
              <div className="bg-[#fffbeb] border border-[#fde68a] rounded-xl p-4 mb-6 text-left">
                <div className="text-[12px] font-semibold text-[#92400e] mb-1">Connection issue</div>
                <div className="text-[11px] text-[#78350f]">The backend server may be starting up. Railway free tier spins down after inactivity. Try again in 10-15 seconds.</div>
              </div>
            ) : (
              <div className="bg-[#fef2f2] border border-[#fecaca] rounded-xl p-4 mb-6 text-left">
                <div className="text-[12px] font-semibold text-[#991b1b] mb-1">Analysis failed</div>
                <div className="text-[11px] text-[#7f1d1d]">The document may be corrupted, password-protected, or in an unsupported format. Try a different PDF.</div>
              </div>
            )}
            <div className="flex items-center justify-center gap-3">
              <button onClick={reset} className="px-6 py-2.5 bg-[#1e3a5f] text-white text-[13px] font-semibold rounded-xl hover:bg-[#162a47] transition shadow-sm">Try Again</button>
              <Link href="/validate" className="px-5 py-2.5 border border-[#e8e5e0] text-[13px] text-[#525252] font-medium rounded-xl hover:bg-[#fafaf8] transition">Validate PDF</Link>
            </div>
          </div>
        )}
      </div>

      {/* History slide-out */}
      {showHistory && (
        <div className="fixed inset-0 z-50 flex justify-end" onClick={() => setShowHistory(false)} role="dialog" aria-modal="true" aria-label="Filing history">
          <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" />
          <div className="relative w-full sm:w-[380px] md:w-[420px] bg-white h-full shadow-2xl overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="sticky top-0 bg-white border-b border-[#e8e5e0] px-6 py-4 z-10">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-[16px] font-bold text-[#1a1a1a]">Filing History</h3>
                <button onClick={() => setShowHistory(false)} aria-label="Close history" className="w-7 h-7 rounded-lg bg-[#f5f3ee] hover:bg-[#e8e5e0] flex items-center justify-center text-[#8a8a8a] hover:text-[#1a1a1a] transition text-sm">&times;</button>
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


