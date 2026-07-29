"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { getEvents, listCourts, type EventCode } from "@/lib/courts-data";

const COURT_TYPES = [
  { id: "district", label: "District", sampleCourt: "nysd" },
  { id: "bankruptcy", label: "Bankruptcy", sampleCourt: "nysb" },
  { id: "appellate", label: "Appellate", sampleCourt: "ca2" },
] as const;

export default function EventsPage() {
  const [type, setType] = useState<(typeof COURT_TYPES)[number]>(COURT_TYPES[0]);
  const [query, setQuery] = useState("");

  const sampleCourtId = useMemo(() => {
    const courts = listCourts(type.id);
    return courts.some((c) => c.court_id === type.sampleCourt)
      ? type.sampleCourt
      : courts[0]?.court_id ?? "nysd";
  }, [type]);

  const events: EventCode[] = useMemo(
    () => getEvents(sampleCourtId, query || undefined),
    [sampleCourtId, query]
  );

  const byCategory = useMemo(() => {
    const grouped = new Map<string, EventCode[]>();
    for (const e of events) {
      const list = grouped.get(e.category) ?? [];
      list.push(e);
      grouped.set(e.category, list);
    }
    return [...grouped.entries()];
  }, [events]);

  return (
    <div className="min-h-screen bg-[#f5f3ee]">
      <header className="bg-white border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-5 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-4 sm:gap-6">
            <Link href="/" className="flex items-center gap-2.5">
              <div className="w-7 h-7 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[10px] font-bold">E</div>
              <span className="text-[15px] font-semibold tracking-tight text-[#1a1a1a] hidden sm:inline">ECFiler</span>
            </Link>
            <div className="h-5 w-px bg-[#e8e5e0]" />
            <span className="text-[13px] text-[#525252] font-medium">Event Code Browser</span>
          </div>
          <Link href="/tools" className="text-[13px] text-[#1e3a5f] hover:text-[#162a47] transition font-medium">All free tools</Link>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-5 sm:px-6 py-8">
        <h1 className="text-[22px] font-bold tracking-tight text-[#1a1a1a] mb-1">CM/ECF event codes</h1>
        <p className="text-[13px] text-[#525252] mb-6">
          Common docketing events by court type. Codes and menu names vary by
          court — confirm the event in your court&apos;s CM/ECF menu before filing.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <div className="flex rounded-xl border border-[#e8e5e0] bg-white overflow-hidden">
            {COURT_TYPES.map((t) => (
              <button
                key={t.id}
                onClick={() => setType(t)}
                className={`px-4 py-2 text-[13px] font-medium transition ${
                  type.id === t.id ? "bg-[#1e3a5f] text-white" : "text-[#525252] hover:bg-[#fafaf8]"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search events — e.g. motion to dismiss"
            className="flex-1 px-4 py-2 bg-white border border-[#e8e5e0] rounded-xl text-[14px] outline-none focus:border-[#1e3a5f]"
          />
        </div>

        {events.length === 0 && (
          <div className="text-[13px] text-[#8a8a8a] bg-white border border-[#e8e5e0] rounded-xl p-6 text-center">
            No events match &ldquo;{query}&rdquo;.
          </div>
        )}

        {byCategory.map(([category, list]) => (
          <div key={category} className="mb-6">
            <h2 className="text-[11px] font-bold text-[#8a8a8a] uppercase tracking-widest mb-2">{category}</h2>
            <div className="bg-white border border-[#e8e5e0] rounded-2xl overflow-hidden">
              {list.map((e) => (
                <div key={`${e.code}-${e.description}`} className="flex items-center gap-4 px-4 py-2.5 border-b border-[#f0eee9] last:border-0">
                  <span className="font-mono text-[12px] font-semibold text-[#1e3a5f] w-14 shrink-0">{e.code}</span>
                  <span className="text-[13px] text-[#1a1a1a]">{e.description}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
