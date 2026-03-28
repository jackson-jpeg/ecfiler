"use client";

import { useState, useRef } from "react";
import Link from "next/link";
import { validatePDF, type ValidationResult } from "@/lib/api";

interface Result extends ValidationResult { name: string }

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
        <h1 className="text-xl font-bold tracking-tight mb-1">Validate PDFs</h1>
        <p className="text-sm text-[#525252] mb-5">Check CM/ECF requirements. No API key needed.</p>

        <div
          className="border-2 border-dashed border-[#e8e5e0] rounded-xl p-10 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-all mb-5"
          onClick={() => ref.current?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => { e.preventDefault(); run(e.dataTransfer.files); }}
        >
          <div className="text-sm font-medium text-[#525252]">Drop PDFs here or click</div>
          <input ref={ref} type="file" accept=".pdf" multiple className="hidden" onChange={(e) => e.target.files && run(e.target.files)} />
        </div>

        {results.length > 0 && (
          <div className="bg-white border border-[#e8e5e0] rounded-xl overflow-hidden">
            <div className="px-5 py-3 border-b border-[#f0eee9] flex justify-between">
              <span className="text-xs font-semibold text-[#8a8a8a] uppercase tracking-wide">Results</span>
              <span className="font-mono text-xs text-[#8a8a8a]">{passed}/{results.length} passed</span>
            </div>
            {results.map((r, i) => (
              <div key={i} className="px-5 py-3 border-b border-[#f0eee9] last:border-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${r.valid ? "bg-[#f0fdf4] text-[#15803d]" : "bg-[#fef2f2] text-red-600"}`}>
                      {r.valid ? "\u2713" : "\u00d7"}
                    </div>
                    <span className="text-sm font-medium">{r.name}</span>
                  </div>
                  <span className="font-mono text-xs text-[#8a8a8a]">{r.file_size_mb?.toFixed(1)}MB, {r.page_count}p</span>
                </div>
                {r.errors?.map((e, j) => <div key={j} className="text-xs text-[#b91c1c] ml-7 mt-1">{e}</div>)}
                {r.warnings?.map((w, j) => <div key={j} className="text-xs text-amber-500 ml-7 mt-1">{w}</div>)}
                {r.valid && !r.errors?.length && <div className="text-xs text-[#15803d] ml-7 mt-1">Ready for CM/ECF</div>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
