"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { scanText, extractPdfText, type RedactionReport } from "@/lib/redaction";

const TYPE_LABELS: Record<string, string> = {
  ssn: "SSN / Tax ID",
  account_number: "Account number",
  dob: "Date of birth",
};

export default function RedactionPage() {
  const [text, setText] = useState("");
  const [report, setReport] = useState<RedactionReport | null>(null);
  const [scannedName, setScannedName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const runOnText = (value: string, name: string) => {
    setReport(scanText(value));
    setScannedName(name);
  };

  const onFile = async (files: FileList | null) => {
    if (!files?.length) return;
    setBusy(true);
    setError("");
    try {
      const { text: extracted, pages } = await extractPdfText(files[0]);
      if (!extracted.trim()) {
        setError(
          "No extractable text found — this PDF appears to be a scanned image. The scan only reads text layers; OCR the document first."
        );
        setReport(null);
      } else {
        runOnText(extracted, `${files[0].name} (${pages} pages)`);
      }
    } catch {
      setError("Could not read that PDF. It may be corrupt or encrypted.");
      setReport(null);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f5f3ee]">
      <header className="bg-white border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-5 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-4 sm:gap-6">
            <Link href="/" className="flex items-center gap-2.5">
              <div className="w-7 h-7 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[10px] font-bold">E</div>
              <span className="text-[15px] font-semibold tracking-tight text-[#1a1a1a] hidden sm:inline">ECFiler</span>
            </Link>
            <div className="h-5 w-px bg-[#e8e5e0]" />
            <span className="text-[13px] text-[#525252] font-medium">Rule 5.2 Redaction Scan</span>
          </div>
          <Link href="/tools" className="text-[13px] text-[#1e3a5f] hover:text-[#162a47] transition font-medium">All free tools</Link>
        </div>
      </header>

      <div className="max-w-3xl mx-auto px-5 sm:px-6 py-8">
        <h1 className="text-[22px] font-bold tracking-tight text-[#1a1a1a] mb-1">Rule 5.2 redaction scan</h1>
        <p className="text-[13px] text-[#525252] mb-2">
          Pattern scan for unredacted SSNs, taxpayer IDs, financial account
          numbers, and dates of birth (Fed. R. Civ. P. 5.2). Runs entirely in
          your browser — the document is never uploaded.
        </p>
        <p className="text-[12px] text-[#8a8a8a] mb-6">
          This is the pattern pass only. It cannot catch identifiers that need
          context to spot (minor children&apos;s names, prose birth dates) — the
          AI contextual pass in the signed-in filing workspace covers those,
          and neither replaces your own review.
        </p>

        <div
          onClick={() => !busy && fileRef.current?.click()}
          className="bg-white border-2 border-dashed border-[#b0aca4] rounded-2xl p-8 text-center cursor-pointer hover:border-[#1e3a5f] transition mb-4"
        >
          <input ref={fileRef} type="file" accept=".pdf,application/pdf" hidden onChange={(e) => onFile(e.target.files)} />
          <div className="text-[14px] font-bold text-[#1a1a1a] mb-1">{busy ? "Extracting text…" : "Drop a PDF or click to choose"}</div>
          <div className="text-[12px] text-[#8a8a8a]">Stays on your machine</div>
        </div>

        <div className="text-center text-[11px] font-bold text-[#8a8a8a] uppercase tracking-widest mb-4">or paste text</div>

        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={5}
          placeholder="Paste document text here…"
          className="w-full px-4 py-3 bg-white border border-[#e8e5e0] rounded-xl text-[13px] font-mono outline-none focus:border-[#1e3a5f] mb-3"
        />
        <button
          onClick={() => text.trim() && runOnText(text, "pasted text")}
          disabled={!text.trim() || busy}
          className="px-6 py-2.5 bg-[#1e3a5f] text-white text-[13px] font-semibold rounded-xl hover:bg-[#162a47] disabled:opacity-40 transition mb-8"
        >
          Scan pasted text
        </button>

        {error && (
          <div className="bg-[#fef2f2] border border-[#fecaca] rounded-xl p-4 text-[13px] text-[#b91c1c] mb-6">{error}</div>
        )}

        {report && (
          <div className="bg-white border border-[#e8e5e0] rounded-2xl overflow-hidden">
            <div
              className={`px-5 py-4 border-b border-[#f0eee9] ${
                report.risk_level === "high" ? "bg-[#fef2f2]" : report.risk_level === "low" ? "bg-[#fffbeb]" : "bg-[#f0fdf4]"
              }`}
            >
              <div className="text-[14px] font-bold text-[#1a1a1a]">
                {report.risk_level === "none"
                  ? "No unredacted identifiers found"
                  : `${report.issues.length} potential identifier${report.issues.length === 1 ? "" : "s"} found`}
              </div>
              <div className="text-[12px] text-[#8a8a8a] mt-0.5">Scanned: {scannedName}</div>
            </div>
            {report.issues.map((issue, i) => (
              <div key={i} className="px-5 py-3 border-b border-[#f0eee9] last:border-0 flex items-start gap-4">
                <span className="text-[10px] font-bold uppercase tracking-wide text-[#b91c1c] bg-[#fef2f2] border border-[#fecaca] rounded-full px-2.5 py-1 shrink-0">
                  {TYPE_LABELS[issue.issue_type] ?? issue.issue_type}
                </span>
                <div>
                  <div className="text-[13px] font-mono text-[#1a1a1a]">{issue.text}</div>
                  <div className="text-[12px] text-[#525252]">{issue.suggestion}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
