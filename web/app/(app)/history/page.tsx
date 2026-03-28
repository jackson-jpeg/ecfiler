"use client";

import { useState, useEffect } from "react";
import { getHistory } from "@/lib/api";

export default function HistoryPage() {
  const [history, setHistory] = useState<Record<string, unknown>[]>([]);

  useEffect(() => { getHistory().then(setHistory); }, []);

  return (
    <div className="px-8 py-8">
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
  );
}
