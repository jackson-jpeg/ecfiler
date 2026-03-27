"use client";

import { useState, useEffect, useRef } from "react";
import { searchCourts, type Court } from "@/lib/api";

export default function CourtsPage() {
  const [courts, setCourts] = useState<Court[]>([]);
  const [query, setQuery] = useState("");
  const [type, setType] = useState("");
  const [loading, setLoading] = useState(true);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    setLoading(true);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => {
      searchCourts(query || undefined, type || undefined).then((c) => { setCourts(c); setLoading(false); });
    }, query ? 200 : 0);
  }, [query, type]);

  const districtCount = courts.filter((c) => c.court_type === "district").length;
  const bankruptcyCount = courts.filter((c) => c.court_type === "bankruptcy").length;
  const appellateCount = courts.filter((c) => c.court_type === "appellate").length;

  return (
    <div className="p-8 lg:p-12">
      <h1 className="text-2xl font-bold tracking-tight mb-2">Courts</h1>
      <p className="text-zinc-500 mb-6">Federal district, bankruptcy, and appellate courts.</p>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 mb-6 max-w-md">
        <button onClick={() => setType(type === "district" ? "" : "district")} className={`rounded-2xl border p-3 text-center transition ${type === "district" ? "border-blue-300 bg-blue-50" : "border-zinc-200 hover:border-zinc-300"}`}>
          <div className="text-xl font-bold text-zinc-900">{districtCount || "—"}</div>
          <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wide">District</div>
        </button>
        <button onClick={() => setType(type === "bankruptcy" ? "" : "bankruptcy")} className={`rounded-2xl border p-3 text-center transition ${type === "bankruptcy" ? "border-purple-300 bg-purple-50" : "border-zinc-200 hover:border-zinc-300"}`}>
          <div className="text-xl font-bold text-zinc-900">{bankruptcyCount || "—"}</div>
          <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wide">Bankruptcy</div>
        </button>
        <button onClick={() => setType(type === "appellate" ? "" : "appellate")} className={`rounded-2xl border p-3 text-center transition ${type === "appellate" ? "border-amber-300 bg-amber-50" : "border-zinc-200 hover:border-zinc-300"}`}>
          <div className="text-xl font-bold text-zinc-900">{appellateCount || "—"}</div>
          <div className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wide">Appellate</div>
        </button>
      </div>

      {/* Search */}
      <div className="mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by name or court ID..."
          className="w-full max-w-md px-4 py-2.5 border border-zinc-200 rounded-xl text-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-50 bg-white"
        />
      </div>

      {/* Table */}
      <div className="bg-white border border-zinc-200 rounded-2xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left">
              <th className="px-5 py-3 text-[10px] font-semibold text-zinc-400 uppercase tracking-wide border-b border-zinc-200 bg-zinc-50/50 w-24">ID</th>
              <th className="px-5 py-3 text-[10px] font-semibold text-zinc-400 uppercase tracking-wide border-b border-zinc-200 bg-zinc-50/50">Name</th>
              <th className="px-5 py-3 text-[10px] font-semibold text-zinc-400 uppercase tracking-wide border-b border-zinc-200 bg-zinc-50/50 w-28">Type</th>
              <th className="px-5 py-3 text-[10px] font-semibold text-zinc-400 uppercase tracking-wide border-b border-zinc-200 bg-zinc-50/50 w-48">ECF URL</th>
            </tr>
          </thead>
          <tbody>
            {courts.map((c) => (
              <tr key={c.court_id} className="hover:bg-zinc-50/50 transition-colors">
                <td className="px-5 py-2.5 font-mono font-semibold text-blue-600 border-b border-zinc-100">{c.court_id}</td>
                <td className="px-5 py-2.5 border-b border-zinc-100">{c.name}</td>
                <td className="px-5 py-2.5 border-b border-zinc-100">
                  <span className={`text-[11px] px-2 py-0.5 rounded-md font-semibold ${
                    c.court_type === "district" ? "bg-blue-50 text-blue-600" :
                    c.court_type === "bankruptcy" ? "bg-purple-50 text-purple-600" : "bg-amber-50 text-amber-600"
                  }`}>{c.court_type}</span>
                </td>
                <td className="px-5 py-2.5 border-b border-zinc-100 font-mono text-xs text-zinc-400">ecf.{c.court_id}.uscourts.gov</td>
              </tr>
            ))}
          </tbody>
        </table>
        {courts.length === 0 && !loading && <div className="p-14 text-center text-zinc-400 text-sm">No courts found</div>}
        {loading && <div className="p-14 text-center text-zinc-400 text-sm">Loading...</div>}
      </div>
    </div>
  );
}
