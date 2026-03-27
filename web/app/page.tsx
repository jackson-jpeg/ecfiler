"use client";

import { useState, useRef, useCallback } from "react";
import { streamAnalysis, streamBrowser, type FilingPreview, type AnalysisStep, type BrowserStep } from "@/lib/api";

type Step = "upload" | "analyzing" | "review" | "browser" | "done" | "error";

export default function FilePage() {
  const [step, setStep] = useState<Step>("upload");
  const [fileName, setFileName] = useState("");
  const [steps, setSteps] = useState<AnalysisStep[]>([]);
  const [filing, setFiling] = useState<FilingPreview | null>(null);
  const [browserSteps, setBrowserSteps] = useState<BrowserStep[]>([]);
  const [screenshot, setScreenshot] = useState("");
  const [browserDone, setBrowserDone] = useState(false);
  const [browserMsg, setBrowserMsg] = useState("");
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const reset = () => {
    setStep("upload"); setFileName(""); setSteps([]); setFiling(null);
    setBrowserSteps([]); setScreenshot(""); setBrowserDone(false); setError("");
  };

  const handleFile = useCallback(async (file: File) => {
    setFileName(file.name);
    setStep("analyzing");
    setSteps([]);

    try {
      for await (const event of streamAnalysis(file)) {
        if (event.type === "step") {
          setSteps((prev) => {
            const existing = prev.find((s) => s.id === event.data.id);
            if (existing) return prev.map((s) => s.id === event.data.id ? { ...s, ...event.data } : s);
            return [...prev, event.data];
          });
        }
        if (event.type === "result") {
          setFiling(event.data);
          setTimeout(() => setStep("review"), 300);
        }
        if (event.type === "error") throw new Error(event.message);
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Analysis failed");
      setStep("error");
    }
  }, []);

  const handleConfirm = useCallback(async () => {
    if (!filing) return;
    setStep("browser");
    setBrowserSteps([]);
    setScreenshot("");
    setBrowserDone(false);

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
        if (event.type === "done") {
          setBrowserDone(true);
          setBrowserMsg(event.message);
        }
      }
    } catch (e: unknown) {
      setBrowserDone(true);
      setBrowserMsg(e instanceof Error ? e.message : "Filing failed");
    }
  }, [filing]);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="px-8 py-8 max-w-2xl">
      <h1 className="text-xl font-bold tracking-tight mb-1">
        {step === "upload" ? "New Filing" : step === "analyzing" ? "Analyzing..." : step === "review" ? "Review Filing" : step === "browser" ? "Filing on CM/ECF" : step === "done" ? "Complete" : "Error"}
      </h1>

      {/* Upload */}
      {step === "upload" && (
        <div className="animate-in fade-in">
          <p className="text-sm text-zinc-500 mb-5">
            Drop a PDF. AI reads your document, extracts filing details, and shows you exactly what it will submit.
          </p>
          <div
            className="border-2 border-dashed border-zinc-200 rounded-2xl p-14 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-all"
            onClick={() => fileRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDrop}
          >
            <div className="w-12 h-12 bg-zinc-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.338-2.32 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
              </svg>
            </div>
            <div className="text-sm font-medium text-zinc-700 mb-1">Drop PDF or click to browse</div>
            <div className="text-xs text-zinc-400">Motions, briefs, complaints, notices, petitions</div>
            <input ref={fileRef} type="file" accept=".pdf" className="hidden" onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} />
          </div>
        </div>
      )}

      {/* Analyzing */}
      {step === "analyzing" && (
        <div className="animate-in fade-in mt-4">
          <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden">
            <div className="px-5 py-3 border-b border-zinc-100 flex items-center justify-between">
              <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">Processing</span>
              <span className="font-mono text-xs text-zinc-400">{fileName}</span>
            </div>
            <div className="px-5 py-3">
              {steps.map((s) => (
                <div key={s.id} className="flex items-start gap-3 py-2.5 animate-in fade-in">
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5 ${
                    s.status === "done" ? "bg-green-50 text-green-600" :
                    s.status === "running" ? "bg-blue-50 text-blue-600" :
                    s.status === "warn" ? "bg-amber-50 text-amber-600" : "bg-red-50 text-red-600"
                  }`}>
                    {s.status === "done" ? "✓" : s.status === "running" ? <span className="animate-pulse">•</span> : s.status === "warn" ? "!" : "×"}
                  </div>
                  <div>
                    <div className="text-sm font-medium">{s.label}</div>
                    {s.detail && <div className="font-mono text-xs text-zinc-400 mt-0.5">{s.detail}</div>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Review */}
      {step === "review" && filing && (
        <div className="animate-in fade-in mt-4 space-y-4">
          {/* AI message */}
          <div className="flex gap-3">
            <div className="w-6 h-6 bg-blue-600 rounded-md flex items-center justify-center text-white text-[9px] font-bold shrink-0 mt-1">E</div>
            <p className="text-sm text-zinc-500 leading-relaxed">I&apos;ve analyzed your document. Here&apos;s exactly what I&apos;ll submit to CM/ECF.</p>
          </div>

          {/* Filing summary */}
          <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden">
            <div className="px-5 py-3 border-b border-zinc-100 flex items-center justify-between">
              <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">Filing Summary</span>
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${filing.completeness_score >= 80 ? "bg-green-50 text-green-700" : "bg-amber-50 text-amber-700"}`}>
                {filing.completeness_score}% extracted
              </span>
            </div>
            <div className="p-5 space-y-4">
              <div>
                <div className="text-base font-bold tracking-tight">{filing.document_type}</div>
                <div className="font-mono text-xs text-zinc-400 mt-1">{fileName}</div>
              </div>
              <hr className="border-zinc-100" />
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wide mb-1">Case</div>
                  <div className="font-mono text-sm font-semibold">{filing.case_number || "—"}</div>
                </div>
                <div>
                  <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wide mb-1">Court</div>
                  <div className="text-sm font-semibold">{filing.court_id?.toUpperCase() || "—"}</div>
                </div>
              </div>
              {filing.case_caption && (
                <div>
                  <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wide mb-1">Caption</div>
                  <div className="text-sm">{filing.case_caption}</div>
                </div>
              )}
              <hr className="border-zinc-100" />
              <div>
                <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wide mb-1">Docket Text</div>
                <div className="text-sm font-semibold">{filing.event_description}</div>
                <div className="font-mono text-xs text-zinc-400 mt-1">Event code {filing.event_code}</div>
              </div>
              {filing.is_response && filing.responds_to && (
                <div className="bg-blue-50 p-3 rounded-lg">
                  <div className="text-[10px] font-semibold text-blue-600 uppercase tracking-wide mb-1">Responding to</div>
                  <div className="text-sm">{filing.responds_to}</div>
                </div>
              )}
              <hr className="border-zinc-100" />
              <div>
                <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wide mb-1">Filing Party</div>
                <div className="text-sm font-semibold">{filing.filing_party || "Not detected"}</div>
              </div>
            </div>
          </div>

          {/* Verification */}
          <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden">
            <div className="px-5 py-3 border-b border-zinc-100">
              <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">Verification</span>
            </div>
            <div className="px-5 py-3 space-y-1">
              <Check ok={filing.pdf_valid} text={filing.pdf_valid ? `PDF valid — ${filing.pdf_size_mb?.toFixed(1)}MB, ${filing.pdf_pages}p` : "PDF has issues"} />
              <Check ok={filing.redaction_issues === 0} text={filing.redaction_issues === 0 ? "No unredacted identifiers (Rule 5.2)" : `${filing.redaction_issues} redaction issue(s)`} warn={filing.redaction_issues > 0} />
              {filing.case_number && <Check ok text={<>Case <b className="font-mono">{filing.case_number}</b> matches PDF</>} />}
              {filing.event_code && <Check ok text={<>Event <b className="font-mono">{filing.event_code}</b> matches document</>} />}
              <Check ok={!filing.warnings?.some((w) => w.includes("certificate"))} warn={filing.warnings?.some((w) => w.includes("certificate"))} text={filing.warnings?.some((w) => w.includes("certificate")) ? "No certificate of service" : "Certificate of service present"} />
            </div>
          </div>

          {/* Warnings */}
          {filing.warnings?.filter((w) => !w.includes("certificate")).map((w) => (
            <div key={w} className="flex gap-2 px-4 py-2.5 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800">
              <span className="font-bold">!</span> {w}
            </div>
          ))}

          {/* Confirm */}
          <div className="flex gap-3 mt-2">
            <div className="w-6 h-6 bg-blue-600 rounded-md flex items-center justify-center text-white text-[9px] font-bold shrink-0 mt-1">E</div>
            <p className="text-sm text-zinc-500">{filing.ready ? "Everything checks out. Confirm to file." : "Some fields are missing."}</p>
          </div>
          <div className="flex gap-2 ml-9">
            <button onClick={handleConfirm} disabled={!filing.ready} className="px-6 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-25 disabled:cursor-not-allowed transition">
              Confirm & File
            </button>
            <button onClick={reset} className="px-4 py-2 text-sm text-zinc-400 hover:text-zinc-600 transition">Cancel</button>
          </div>
        </div>
      )}

      {/* Browser */}
      {step === "browser" && (
        <div className="animate-in fade-in mt-4 space-y-4">
          <div className="flex gap-3">
            <div className="w-6 h-6 bg-blue-600 rounded-md flex items-center justify-center text-white text-[9px] font-bold shrink-0 mt-1">E</div>
            <p className="text-sm text-zinc-500">Filing on CM/ECF. Watch each step below.</p>
          </div>

          {/* Browser frame */}
          <div className="border border-zinc-200 rounded-xl overflow-hidden">
            <div className="bg-white px-3 py-2 border-b border-zinc-200 flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-red-400" />
              <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
              <div className="w-2.5 h-2.5 rounded-full bg-green-400" />
              <span className="ml-2 font-mono text-[11px] text-zinc-400">ecf.{filing?.court_id || "nysd"}.uscourts.gov</span>
              {!browserDone && <span className="ml-auto text-[10px] text-blue-600 font-semibold animate-pulse">LIVE</span>}
            </div>
            <div className="bg-zinc-100 min-h-[280px] flex items-center justify-center">
              {screenshot ? (
                <img src={`data:image/png;base64,${screenshot}`} className="w-full" alt="CM/ECF" />
              ) : (
                <span className="text-sm text-zinc-400">Connecting...</span>
              )}
            </div>
          </div>

          {/* Steps */}
          <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden">
            <div className="px-5 py-3 border-b border-zinc-100">
              <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">Steps</span>
            </div>
            <div className="px-5 py-2">
              {browserSteps.map((s) => (
                <div key={s.step} className="flex items-start gap-3 py-2">
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0 ${
                    s.status === "done" ? "bg-green-50 text-green-600" : "bg-blue-50 text-blue-600"
                  }`}>
                    {s.status === "done" ? "✓" : <span className="animate-pulse">•</span>}
                  </div>
                  <div>
                    <div className="text-xs font-medium">{s.step}</div>
                    <div className="text-[11px] text-zinc-400">{s.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {browserDone && (
            <>
              <div className="flex gap-3">
                <div className="w-6 h-6 bg-blue-600 rounded-md flex items-center justify-center text-white text-[9px] font-bold shrink-0 mt-1">E</div>
                <p className="text-sm text-zinc-500">{browserMsg}</p>
              </div>
              <button onClick={reset} className="ml-9 px-5 py-2 bg-zinc-900 text-white text-sm font-semibold rounded-lg hover:bg-zinc-700 transition">
                Done
              </button>
            </>
          )}
        </div>
      )}

      {/* Error */}
      {step === "error" && (
        <div className="animate-in fade-in mt-6">
          <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
          </div>
          <h2 className="text-lg font-bold mb-2">Failed</h2>
          <p className="text-sm text-zinc-500 mb-5">{error}</p>
          <button onClick={reset} className="px-5 py-2 bg-zinc-900 text-white text-sm font-semibold rounded-lg hover:bg-zinc-700 transition">
            Try Again
          </button>
        </div>
      )}
    </div>
  );
}

function Check({ ok, warn, text }: { ok?: boolean; warn?: boolean; text: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2.5 py-1.5">
      <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
        warn ? "bg-amber-50 text-amber-600" : ok ? "bg-green-50 text-green-600" : "bg-red-50 text-red-600"
      }`}>
        {warn ? "!" : ok ? "✓" : "×"}
      </div>
      <span className="text-sm">{text}</span>
    </div>
  );
}
