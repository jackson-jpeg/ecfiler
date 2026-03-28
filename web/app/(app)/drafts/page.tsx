"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getDrafts } from "@/lib/api";

export default function DraftsPage() {
  const [drafts, setDrafts] = useState<Record<string, unknown>[]>([]);

  useEffect(() => { getDrafts().then(setDrafts); }, []);

  const deleteDraft = async (name: string) => {
    await fetch(`/api/drafts/${encodeURIComponent(name)}`, { method: "DELETE" });
    setDrafts(await getDrafts());
  };

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
            <span className="text-[13px] text-[#525252] font-medium">Drafts</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/file" className="text-[13px] text-[#1e3a5f] hover:text-[#162a47] transition font-medium">&larr; Back to Filing</Link>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <h1 className="text-xl font-bold tracking-tight mb-1">Drafts</h1>
        <p className="text-sm text-[#525252] mb-5">Resume incomplete filings.</p>

        <div className="bg-white border border-[#e8e5e0] rounded-xl overflow-hidden">
          {drafts.length > 0 ? (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left">
                  <th className="px-5 py-2.5 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">Name</th>
                  <th className="px-5 py-2.5 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">Court</th>
                  <th className="px-5 py-2.5 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">Case</th>
                  <th className="px-5 py-2.5 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">Saved</th>
                  <th className="px-5 py-2.5 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8] w-14"></th>
                </tr>
              </thead>
              <tbody>
                {drafts.map((d, i) => (
                  <tr key={i} className="hover:bg-[#fafaf8]/50">
                    <td className="px-5 py-2.5 font-medium border-b border-[#f0eee9]">{String(d.name || "")}</td>
                    <td className="px-5 py-2.5 font-mono text-[#525252] border-b border-[#f0eee9]">{String(d.court || "")}</td>
                    <td className="px-5 py-2.5 text-[#525252] border-b border-[#f0eee9]">{String(d.case || "")}</td>
                    <td className="px-5 py-2.5 text-[#8a8a8a] border-b border-[#f0eee9]">{String(d.saved_at || "").substring(0, 10)}</td>
                    <td className="px-5 py-2.5 border-b border-[#f0eee9]">
                      <button onClick={() => deleteDraft(String(d.file || d.name))} className="text-xs text-[#8a8a8a] hover:text-[#b91c1c]">delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-14 text-center text-[#8a8a8a] text-sm">No drafts saved</div>
          )}
        </div>
      </div>
    </div>
  );
}
