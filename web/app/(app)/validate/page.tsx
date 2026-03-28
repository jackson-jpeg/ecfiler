"use client";

import { useState, useRef } from "react";
import Link from "next/link";
import { validatePDF, type ValidationResult } from "@/lib/api";

interface Result extends ValidationResult { name: string }

/* Inline icons for validation checks */
function CheckCircle({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function XCircle({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function WarnTriangle({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
    </svg>
  );
}

function FileIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
    </svg>
  );
}

export default function ValidatePage() {
  const [results, setResults] = useState<Result[]>([]);
  const ref = useRef<HTMLInputElement>(null);

  const run = async (files: FileList) => {
    setResults([]);
    for (const file of Array.from(files)) {
      const v = await validatePDF(file);
      setResults((prev) => [...prev, { ...v, name: file.name }]);
    }
  };

  const passed = results.filter((r) => r.valid).length;

  return (
    <div className="min-h-screen bg-[#f5f3ee]">
      <header className="bg-white border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/file" className="flex items-center gap-2.5">
              <div className="w-7 h-7 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[10px] font-bold">E</div>
              <span className="text-[15px] font-semibold tracking-tight text-[#1a1a1a]">ECFiler</span>
            </Link>
            <div className="h-5 w-px bg-[#e8e5e0]" />
            <span className="text-[13px] text-[#525252] font-medium">PDF Validator</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/file" className="text-[13px] text-[#1e3a5f] hover:text-[#162a47] transition font-medium">&larr; Back to Filing</Link>
          </div>
        </div>
      </header>

      <div className="max-w-3xl mx-auto px-6 py-8">
        {/* Info banner */}
        <div className="bg-gradient-to-r from-[#1e3a5f] to-[#2a5080] rounded-xl p-5 mb-8 shadow-sm">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg className="w-5 h-5 text-white/90" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
              </svg>
            </div>
            <div>
              <p className="text-white font-semibold text-sm mb-1">PDF validation is built into the filing flow</p>
              <p className="text-white/70 text-xs leading-relaxed mb-3">
                Drop a PDF on the filing workspace for automatic validation. This standalone tool is available for quick checks outside the filing workflow.
              </p>
              <Link
                href="/file"
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-white bg-white/15 hover:bg-white/25 px-3.5 py-1.5 rounded-lg transition"
              >
                Go to Filing Workspace
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                </svg>
              </Link>
            </div>
          </div>
        </div>

        <h1 className="text-xl font-bold tracking-tight text-[#1a1a1a] mb-1">Validate PDFs</h1>
        <p className="text-sm text-[#525252] mb-5">Check CM/ECF requirements. No API key needed.</p>

        <div
          className="bg-white border-2 border-dashed border-[#e8e5e0] rounded-xl p-10 text-center cursor-pointer hover:border-[#1e3a5f]/40 hover:bg-[#1e3a5f]/[0.02] transition-all mb-6 group"
          onClick={() => ref.current?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => { e.preventDefault(); run(e.dataTransfer.files); }}
        >
          <div className="w-12 h-12 rounded-xl bg-[#1e3a5f]/[0.06] flex items-center justify-center mx-auto mb-3 group-hover:bg-[#1e3a5f]/[0.1] transition">
            <FileIcon className="w-6 h-6 text-[#1e3a5f]/60" />
          </div>
          <div className="text-sm font-medium text-[#525252]">Drop PDFs here or click to browse</div>
          <div className="text-xs text-[#8a8a8a] mt-1">Supports multiple files</div>
          <input ref={ref} type="file" accept=".pdf" multiple className="hidden" onChange={(e) => e.target.files && run(e.target.files)} />
        </div>

        {results.length > 0 && (
          <div className="bg-white border border-[#e8e5e0] rounded-xl overflow-hidden shadow-sm">
            <div className="px-5 py-3.5 border-b border-[#f0eee9] flex justify-between items-center">
              <span className="text-xs font-semibold text-[#8a8a8a] uppercase tracking-wide">Results</span>
              <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                passed === results.length
                  ? "bg-[#f0fdf4] text-[#15803d]"
                  : "bg-[#fef2f2] text-[#b91c1c]"
              }`}>
                {passed}/{results.length} passed
              </span>
            </div>
            {results.map((r, i) => (
              <div key={i} className="px-5 py-4 border-b border-[#f0eee9] last:border-0">
                {/* File header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2.5">
                    {r.valid ? (
                      <CheckCircle className="w-5 h-5 text-[#15803d]" />
                    ) : (
                      <XCircle className="w-5 h-5 text-[#b91c1c]" />
                    )}
                    <span className="text-sm font-semibold text-[#1a1a1a]">{r.name}</span>
                  </div>
                  <span className="font-mono text-xs text-[#8a8a8a]">{r.file_size_mb?.toFixed(1)} MB &middot; {r.page_count} pages</span>
                </div>

                {/* Validation checks grid */}
                <div className="ml-8 grid grid-cols-2 gap-2 mb-2">
                  <div className={`flex items-center gap-2 text-xs px-3 py-2 rounded-lg ${
                    r.file_size_mb <= 35 ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#fef2f2] text-[#b91c1c]"
                  }`}>
                    {r.file_size_mb <= 35 ? <CheckCircle className="w-3.5 h-3.5 flex-shrink-0" /> : <XCircle className="w-3.5 h-3.5 flex-shrink-0" />}
                    File size ({r.file_size_mb?.toFixed(1)} MB)
                  </div>
                  <div className={`flex items-center gap-2 text-xs px-3 py-2 rounded-lg ${
                    r.has_text ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#fef2f2] text-[#b91c1c]"
                  }`}>
                    {r.has_text ? <CheckCircle className="w-3.5 h-3.5 flex-shrink-0" /> : <XCircle className="w-3.5 h-3.5 flex-shrink-0" />}
                    Text searchable
                  </div>
                  <div className={`flex items-center gap-2 text-xs px-3 py-2 rounded-lg ${
                    !r.is_encrypted ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#fef2f2] text-[#b91c1c]"
                  }`}>
                    {!r.is_encrypted ? <CheckCircle className="w-3.5 h-3.5 flex-shrink-0" /> : <XCircle className="w-3.5 h-3.5 flex-shrink-0" />}
                    Not encrypted
                  </div>
                  <div className="flex items-center gap-2 text-xs px-3 py-2 rounded-lg bg-[#f0fdf4] text-[#15803d]">
                    <CheckCircle className="w-3.5 h-3.5 flex-shrink-0" />
                    Valid PDF format
                  </div>
                </div>

                {/* Errors */}
                {r.errors?.map((e, j) => (
                  <div key={`err-${j}`} className="flex items-start gap-2 ml-8 mt-2 text-xs text-[#b91c1c]">
                    <XCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                    {e}
                  </div>
                ))}

                {/* Warnings */}
                {r.warnings?.map((w, j) => (
                  <div key={`warn-${j}`} className="flex items-start gap-2 ml-8 mt-2 text-xs text-[#b45309]">
                    <WarnTriangle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                    {w}
                  </div>
                ))}

                {/* Success message */}
                {r.valid && !r.errors?.length && (
                  <div className="flex items-center gap-2 ml-8 mt-2 text-xs text-[#15803d] font-medium">
                    <CheckCircle className="w-3.5 h-3.5 flex-shrink-0" />
                    Ready for CM/ECF filing
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
