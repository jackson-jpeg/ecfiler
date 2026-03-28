"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getHistory } from "@/lib/api";

export default function HistoryPage() {
  const [history, setHistory] = useState<Record<string, unknown>[]>([]);

  useEffect(() => { getHistory().then(setHistory); }, []);

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
            <span className="text-[13px] text-[#525252] font-medium">Filing History</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/file" className="text-[13px] text-[#1e3a5f] hover:text-[#162a47] transition font-medium">&larr; Back to Filing</Link>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <h1 className="text-xl font-bold tracking-tight mb-1">Filing History</h1>
        <p className="text-sm text-[#525252] mb-5">Audit log of all filings.</p>

        <div className="bg-white border border-[#e8e5e0] rounded-xl overflow-hidden">
          {history.length > 0 ? (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left">
                  <th className="px-5 py-2.5 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">Date</th>
                  <th className="px-5 py-2.5 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">Court</th>
                  <th className="px-5 py-2.5 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">Case</th>
                  <th className="px-5 py-2.5 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">Event</th>
                  <th className="px-5 py-2.5 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">Status</th>
                </tr>
              </thead>
              <tbody>
                {history.map((h, i) => (
                  <tr key={i} className="hover:bg-[#fafaf8]/50">
                    <td className="px-5 py-2.5 text-[#8a8a8a] border-b border-[#f0eee9]">{String(h.filed_at || "").substring(0, 10)}</td>
                    <td className="px-5 py-2.5 font-mono border-b border-[#f0eee9]">{String(h.court_id || "")}</td>
                    <td className="px-5 py-2.5 border-b border-[#f0eee9]">{String(h.case_number || "")}</td>
                    <td className="px-5 py-2.5 text-[#525252] border-b border-[#f0eee9]">{String(h.event_description || "").substring(0, 40)}</td>
                    <td className="px-5 py-2.5 border-b border-[#f0eee9]">
                      <span className="text-xs px-2 py-0.5 rounded-md font-medium bg-[#f0fdf4] text-[#15803d]">{String(h.status || "")}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-14 text-center text-[#8a8a8a] text-sm">No filings yet</div>
          )}
        </div>
      </div>
    </div>
  );
}
