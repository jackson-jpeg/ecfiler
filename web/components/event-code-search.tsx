"use client";

import { useState, useEffect } from "react";

interface Props {
  courtId: string;
  onSelect: (code: string, desc: string) => void;
  onClose: () => void;
}

export function EventCodeSearch({ courtId, onSelect, onClose }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<{ code: string; description: string }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query || query.length < 2) { setResults([]); return; }
    setLoading(true);
    const timer = setTimeout(() => {
      fetch(`/api/courts/${courtId || "nysd"}/events?search=${encodeURIComponent(query)}`)
        .then(r => r.json())
        .then((data) => { setResults(data.slice(0, 15)); setLoading(false); })
        .catch(() => setLoading(false));
    }, 250);
    return () => clearTimeout(timer);
  }, [query, courtId]);

  return (
    <div className="border-t border-[#e8e5e0] bg-[#fafaf8] p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Search Event Codes</span>
        <button onClick={onClose} className="text-[11px] text-[#8a8a8a] hover:text-[#1a1a1a] transition">Close</button>
      </div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="e.g., motion to dismiss, reply brief..."
        autoFocus
        className="w-full px-3 py-2 border border-[#e8e5e0] rounded-lg text-[13px] outline-none focus:border-[#1e3a5f] focus:ring-1 focus:ring-[#1e3a5f]/10 bg-white mb-2"
      />
      {loading && <div className="text-[11px] text-[#8a8a8a] py-2">Searching...</div>}
      {results.length > 0 && (
        <div className="max-h-[200px] overflow-y-auto border border-[#e8e5e0] rounded-lg bg-white">
          {results.map((r) => (
            <button
              key={r.code}
              onClick={() => onSelect(r.code, r.description)}
              className="w-full text-left px-3 py-2 border-b border-[#f0eee9] last:border-0 hover:bg-[#f0f4fa] transition"
            >
              <span className="text-[12px] font-mono text-[#1e3a5f] font-semibold">{r.code}</span>
              <span className="text-[12px] text-[#525252] ml-2">{r.description}</span>
            </button>
          ))}
        </div>
      )}
      {query.length >= 2 && !loading && results.length === 0 && (
        <div className="text-[11px] text-[#8a8a8a] py-2">No matching event codes</div>
      )}
    </div>
  );
}
