"use client";

import { useState, useEffect } from "react";
import { searchCourts, type Court } from "@/lib/api";

export default function CourtsPage() {
  const [courts, setCourts] = useState<Court[]>([]);
  const [query, setQuery] = useState("");
  const [type, setType] = useState("");

  useEffect(() => {
    searchCourts(query || undefined, type || undefined).then(setCourts);
  }, [query, type]);

  return (
    <div className="px-8 py-8">
      <div className="flex items-center justify-between mb-1">
        <h1 className="text-xl font-bold tracking-tight">Courts</h1>
        <span className="font-mono text-xs text-zinc-400">{courts.length} courts</span>
      </div>
      <p className="text-sm text-zinc-500 mb-5">150 federal district, bankruptcy, and appellate courts.</p>

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search..."
          className="flex-1 px-3 py-2 border border-zinc-200 rounded-lg text-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-50"
        />
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="px-3 py-2 border border-zinc-200 rounded-lg text-sm bg-white outline-none focus:border-blue-400"
        >
          <option value="">All</option>
          <option value="district">District</option>
          <option value="bankruptcy">Bankruptcy</option>
          <option value="appellate">Appellate</option>
        </select>
      </div>

      <div className="bg-white border border-zinc-200 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left">
              <th className="px-5 py-2.5 text-[10px] font-semibold text-zinc-400 uppercase tracking-wide border-b border-zinc-200 bg-zinc-50 w-20">ID</th>
              <th className="px-5 py-2.5 text-[10px] font-semibold text-zinc-400 uppercase tracking-wide border-b border-zinc-200 bg-zinc-50">Name</th>
              <th className="px-5 py-2.5 text-[10px] font-semibold text-zinc-400 uppercase tracking-wide border-b border-zinc-200 bg-zinc-50 w-28">Type</th>
            </tr>
          </thead>
          <tbody>
            {courts.map((c) => (
              <tr key={c.court_id} className="hover:bg-zinc-50/50">
                <td className="px-5 py-2.5 font-mono font-semibold text-blue-600 border-b border-zinc-100">{c.court_id}</td>
                <td className="px-5 py-2.5 border-b border-zinc-100">{c.name}</td>
                <td className="px-5 py-2.5 border-b border-zinc-100">
                  <span className={`text-xs px-2 py-0.5 rounded-md font-medium ${
                    c.court_type === "district" ? "bg-blue-50 text-blue-600" :
                    c.court_type === "bankruptcy" ? "bg-purple-50 text-purple-600" : "bg-amber-50 text-amber-600"
                  }`}>{c.court_type}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {courts.length === 0 && <div className="p-12 text-center text-zinc-400 text-sm">No courts found</div>}
      </div>
    </div>
  );
}
