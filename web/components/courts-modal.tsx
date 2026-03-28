"use client";

import { useState, useEffect } from "react";

interface Props {
  onClose: () => void;
}

export function CourtsModal({ onClose }: Props) {
  const [query, setQuery] = useState("");
  const [courts, setCourts] = useState<{ court_id: string; name: string; court_type: string }[]>([]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (query) params.set("search", query);
    fetch(`/api/courts?${params}`).then(r => r.json()).then(setCourts).catch(() => {});
  }, [query]);

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]" onClick={onClose}>
      <div className="absolute inset-0 bg-black/20 backdrop-blur-sm" />
      <div className="relative w-[calc(100%-2rem)] sm:w-[500px] md:w-[560px] bg-white rounded-2xl shadow-2xl border border-[#e8e5e0] max-h-[60vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="p-4 border-b border-[#f0eee9]">
          <input
            type="text" value={query} onChange={(e) => setQuery(e.target.value)} autoFocus
            placeholder="Search 207 federal courts..."
            className="w-full px-4 py-2.5 bg-[#f5f3ee] rounded-xl text-[14px] outline-none focus:bg-white focus:ring-2 focus:ring-[#1e3a5f]/10 border border-transparent focus:border-[#1e3a5f] transition"
          />
        </div>
        <div className="overflow-y-auto flex-1">
          {courts.slice(0, 20).map((c) => (
            <div key={c.court_id} className="flex items-center justify-between px-5 py-3 border-b border-[#f0eee9] last:border-0 hover:bg-[#fafaf8] transition cursor-default">
              <div>
                <div className="text-[13px] font-medium text-[#1a1a1a]">{c.name}</div>
                <div className="text-[11px] text-[#8a8a8a] font-mono">ecf.{c.court_id}.uscourts.gov</div>
              </div>
              <span className={`text-[10px] px-2 py-0.5 rounded-md font-semibold ${
                c.court_type === "district" ? "bg-[#e1effe] text-[#1e3a5f]" : c.court_type === "bankruptcy" ? "bg-[#f5f3ff] text-[#7c3aed]" : "bg-[#fffbeb] text-[#b45309]"
              }`}>{c.court_type}</span>
            </div>
          ))}
          {courts.length === 0 && <div className="p-8 text-center text-[13px] text-[#8a8a8a]">No courts found</div>}
        </div>
      </div>
    </div>
  );
}
