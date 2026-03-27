"use client";

import { useState, useEffect } from "react";
import { getDrafts } from "@/lib/api";

export default function DraftsPage() {
  const [drafts, setDrafts] = useState<Record<string, unknown>[]>([]);

  useEffect(() => { getDrafts().then(setDrafts); }, []);

  const deleteDraft = async (name: string) => {
    await fetch(`/api/drafts/${encodeURIComponent(name)}`, { method: "DELETE" });
    setDrafts(await getDrafts());
  };

  return (
    <div className="px-8 py-8">
      <h1 className="text-xl font-bold tracking-tight mb-1">Drafts</h1>
      <p className="text-sm text-zinc-500 mb-5">Resume incomplete filings.</p>

      <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden">
        {drafts.length > 0 ? (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left">
                <th className="px-5 py-2.5 text-[10px] font-semibold text-zinc-400 uppercase tracking-wide border-b border-zinc-200 bg-zinc-50">Name</th>
                <th className="px-5 py-2.5 text-[10px] font-semibold text-zinc-400 uppercase tracking-wide border-b border-zinc-200 bg-zinc-50">Court</th>
                <th className="px-5 py-2.5 text-[10px] font-semibold text-zinc-400 uppercase tracking-wide border-b border-zinc-200 bg-zinc-50">Case</th>
                <th className="px-5 py-2.5 text-[10px] font-semibold text-zinc-400 uppercase tracking-wide border-b border-zinc-200 bg-zinc-50">Saved</th>
                <th className="px-5 py-2.5 text-[10px] font-semibold text-zinc-400 uppercase tracking-wide border-b border-zinc-200 bg-zinc-50 w-14"></th>
              </tr>
            </thead>
            <tbody>
              {drafts.map((d, i) => (
                <tr key={i} className="hover:bg-zinc-50/50">
                  <td className="px-5 py-2.5 font-medium border-b border-zinc-100">{String(d.name || "")}</td>
                  <td className="px-5 py-2.5 font-mono text-zinc-500 border-b border-zinc-100">{String(d.court || "")}</td>
                  <td className="px-5 py-2.5 text-zinc-500 border-b border-zinc-100">{String(d.case || "")}</td>
                  <td className="px-5 py-2.5 text-zinc-400 border-b border-zinc-100">{String(d.saved_at || "").substring(0, 10)}</td>
                  <td className="px-5 py-2.5 border-b border-zinc-100">
                    <button onClick={() => deleteDraft(String(d.file || d.name))} className="text-xs text-zinc-400 hover:text-red-500">delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="p-14 text-center text-zinc-400 text-sm">No drafts saved</div>
        )}
      </div>
    </div>
  );
}
