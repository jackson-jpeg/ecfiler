"use client";

import { useState, useRef } from "react";
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
    <div className="px-8 py-8 max-w-2xl">
      <h1 className="text-xl font-bold tracking-tight mb-1">Validate PDFs</h1>
      <p className="text-sm text-zinc-500 mb-5">Check CM/ECF requirements. No API key needed.</p>

      <div
        className="border-2 border-dashed border-zinc-200 rounded-xl p-10 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-all mb-5"
        onClick={() => ref.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => { e.preventDefault(); run(e.dataTransfer.files); }}
      >
        <div className="text-sm font-medium text-zinc-600">Drop PDFs here or click</div>
        <input ref={ref} type="file" accept=".pdf" multiple className="hidden" onChange={(e) => e.target.files && run(e.target.files)} />
      </div>

      {results.length > 0 && (
        <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-zinc-100 flex justify-between">
            <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">Results</span>
            <span className="font-mono text-xs text-zinc-400">{passed}/{results.length} passed</span>
          </div>
          {results.map((r, i) => (
            <div key={i} className="px-5 py-3 border-b border-zinc-100 last:border-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${r.valid ? "bg-green-50 text-green-600" : "bg-red-50 text-red-600"}`}>
                    {r.valid ? "✓" : "×"}
                  </div>
                  <span className="text-sm font-medium">{r.name}</span>
                </div>
                <span className="font-mono text-xs text-zinc-400">{r.file_size_mb?.toFixed(1)}MB, {r.page_count}p</span>
              </div>
              {r.errors?.map((e, j) => <div key={j} className="text-xs text-red-500 ml-7 mt-1">{e}</div>)}
              {r.warnings?.map((w, j) => <div key={j} className="text-xs text-amber-500 ml-7 mt-1">{w}</div>)}
              {r.valid && !r.errors?.length && <div className="text-xs text-green-600 ml-7 mt-1">Ready for CM/ECF</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
