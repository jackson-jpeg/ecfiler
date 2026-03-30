"use client";

import { useState, useEffect, useCallback } from "react";

interface Court {
  court_id: string;
  name: string;
  court_type: string;
}

interface EventCode {
  code: string;
  description: string;
  category: string;
}

interface Props {
  onClose: () => void;
}

export function CourtsModal({ onClose }: Props) {
  const [query, setQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [courts, setCourts] = useState<Court[]>([]);
  const [selected, setSelected] = useState<Court | null>(null);
  const [events, setEvents] = useState<EventCode[]>([]);
  const [eventQuery, setEventQuery] = useState("");
  const [loadingEvents, setLoadingEvents] = useState(false);
  const [copiedId, setCopiedId] = useState("");
  const [defaultCourt, setDefaultCourt] = useState("");

  useEffect(() => {
    setDefaultCourt(localStorage.getItem("ecfiler_court") || "");
  }, []);

  // Debounce court search to avoid firing on every keystroke
  const [debouncedQuery, setDebouncedQuery] = useState("");
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 250);
    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (debouncedQuery) params.set("search", debouncedQuery);
    if (typeFilter !== "all") params.set("court_type", typeFilter);
    fetch(`/api/courts?${params}`).then(r => r.json()).then(setCourts).catch(() => {});
  }, [debouncedQuery, typeFilter]);

  const selectCourt = useCallback((court: Court) => {
    setSelected(court);
    setLoadingEvents(true);
    setEvents([]);
    setEventQuery("");
    fetch(`/api/courts/${court.court_id}/events`)
      .then(r => r.json())
      .then(setEvents)
      .catch(() => {})
      .finally(() => setLoadingEvents(false));
  }, []);

  const setAsDefault = useCallback((courtId: string) => {
    localStorage.setItem("ecfiler_court", courtId);
    setDefaultCourt(courtId);
  }, []);

  const copyToClipboard = useCallback((text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(""), 1500);
  }, []);

  const filteredEvents = eventQuery
    ? events.filter(e => e.description.toLowerCase().includes(eventQuery.toLowerCase()) || e.code.toLowerCase().includes(eventQuery.toLowerCase()))
    : events;

  // Group events by category
  const categories = [...new Set(filteredEvents.map(e => e.category).filter(Boolean))].sort();

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[8vh] sm:pt-[12vh]" onClick={onClose} role="dialog" aria-modal="true" aria-label="Court directory">
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
      <div className="relative w-[calc(100%-1rem)] sm:w-[600px] md:w-[680px] bg-white rounded-2xl shadow-2xl border border-[#e8e5e0] max-h-[80vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>

        {/* Header */}
        <div className="p-4 border-b border-[#f0eee9] bg-[#fafaf8] shrink-0">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              {selected && (
                <button onClick={() => setSelected(null)} className="text-[12px] text-[#1e3a5f] font-medium hover:underline mr-1">&larr;</button>
              )}
              <h2 className="text-[15px] font-bold text-[#1a1a1a]">{selected ? selected.name : "Federal Courts"}</h2>
            </div>
            <button onClick={onClose} className="w-7 h-7 rounded-lg bg-[#f0eee9] hover:bg-[#e8e5e0] flex items-center justify-center text-[#8a8a8a] hover:text-[#1a1a1a] transition text-sm">&times;</button>
          </div>

          {!selected ? (
            <>
              <input
                type="text" value={query} onChange={(e) => setQuery(e.target.value)} autoFocus
                placeholder="Search 207 federal courts..."
                className="w-full px-4 py-2.5 bg-white rounded-xl text-[14px] outline-none focus:ring-2 focus:ring-[#1e3a5f]/10 border border-[#e8e5e0] focus:border-[#1e3a5f] transition"
              />
              <div className="flex gap-1.5 mt-3">
                {[
                  { value: "all", label: "All" },
                  { value: "district", label: "District" },
                  { value: "bankruptcy", label: "Bankruptcy" },
                  { value: "appellate", label: "Appellate" },
                ].map(({ value, label }) => (
                  <button
                    key={value}
                    onClick={() => setTypeFilter(value)}
                    className={`px-3 py-1.5 text-[11px] font-semibold rounded-lg transition ${
                      typeFilter === value ? "bg-[#1e3a5f] text-white" : "bg-white text-[#525252] border border-[#e8e5e0] hover:bg-[#f5f3ee]"
                    }`}
                  >
                    {label}
                  </button>
                ))}
                <span className="ml-auto text-[11px] text-[#c4c4c4] self-center">{courts.length} courts</span>
              </div>
            </>
          ) : (
            <input
              type="text" value={eventQuery} onChange={(e) => setEventQuery(e.target.value)} autoFocus
              placeholder={`Search event codes for ${selected.court_id.toUpperCase()}...`}
              className="w-full px-4 py-2.5 bg-white rounded-xl text-[14px] outline-none focus:ring-2 focus:ring-[#1e3a5f]/10 border border-[#e8e5e0] focus:border-[#1e3a5f] transition"
            />
          )}
        </div>

        {/* Court list */}
        {!selected && (
          <div className="overflow-y-auto flex-1">
            {courts.slice(0, 50).map((c) => (
              <button
                key={c.court_id}
                onClick={() => selectCourt(c)}
                className="w-full flex items-center justify-between px-5 py-3.5 border-b border-[#f0eee9] last:border-0 hover:bg-[#f5f3ee] transition text-left group"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[13px] font-semibold text-[#1a1a1a] group-hover:text-[#1e3a5f] transition">{c.name}</span>
                    {c.court_id === defaultCourt && (
                      <span className="text-[8px] px-1.5 py-0.5 bg-[#1e3a5f] text-white rounded font-bold uppercase">Default</span>
                    )}
                  </div>
                  <div className="text-[11px] text-[#8a8a8a] font-mono mt-0.5">ecf.{c.court_id}.uscourts.gov</div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className={`text-[10px] px-2 py-0.5 rounded-md font-semibold ${
                    c.court_type === "district" ? "bg-[#e1effe] text-[#1e3a5f]" : c.court_type === "bankruptcy" ? "bg-[#f5f3ff] text-[#7c3aed]" : "bg-[#fffbeb] text-[#b45309]"
                  }`}>{c.court_type}</span>
                  <svg className="w-4 h-4 text-[#c4c4c4] group-hover:text-[#1e3a5f] transition" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                  </svg>
                </div>
              </button>
            ))}
            {courts.length === 0 && (
              <div className="p-10 text-center">
                <div className="text-[14px] text-[#8a8a8a]">No courts found</div>
                <div className="text-[12px] text-[#c4c4c4] mt-1">Try a different search term</div>
              </div>
            )}
          </div>
        )}

        {/* Court detail view */}
        {selected && (
          <div className="overflow-y-auto flex-1">
            {/* Court info card */}
            <div className="px-5 py-4 border-b border-[#f0eee9] bg-white">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-[10px] px-2 py-0.5 rounded-md font-semibold ${
                      selected.court_type === "district" ? "bg-[#e1effe] text-[#1e3a5f]" : selected.court_type === "bankruptcy" ? "bg-[#f5f3ff] text-[#7c3aed]" : "bg-[#fffbeb] text-[#b45309]"
                    }`}>{selected.court_type}</span>
                    <span className="text-[11px] font-mono text-[#8a8a8a]">{selected.court_id.toUpperCase()}</span>
                  </div>
                  <div className="flex items-center gap-3 mt-2">
                    <a
                      href={`https://ecf.${selected.court_id}.uscourts.gov`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[12px] text-[#1e3a5f] font-medium hover:underline flex items-center gap-1"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" /></svg>
                      Open CM/ECF
                    </a>
                    <button
                      onClick={() => copyToClipboard(`ecf.${selected.court_id}.uscourts.gov`, "url")}
                      className="text-[11px] text-[#8a8a8a] hover:text-[#1a1a1a] transition flex items-center gap-1"
                    >
                      {copiedId === "url" ? "Copied!" : "Copy URL"}
                    </button>
                  </div>
                </div>
                <button
                  onClick={() => setAsDefault(selected.court_id)}
                  className={`shrink-0 px-3 py-1.5 text-[11px] font-semibold rounded-lg transition ${
                    defaultCourt === selected.court_id
                      ? "bg-[#f0fdf4] text-[#15803d] border border-[#bbf7d0]"
                      : "bg-white text-[#1e3a5f] border border-[#e8e5e0] hover:bg-[#f0f4fa] hover:border-[#1e3a5f]/30"
                  }`}
                >
                  {defaultCourt === selected.court_id ? "✓ Default Court" : "Set as Default"}
                </button>
              </div>
            </div>

            {/* Event codes */}
            <div className="px-5 py-3 border-b border-[#f0eee9] bg-[#fafaf8]">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-[#8a8a8a] uppercase tracking-wide">Event Codes</span>
                <span className="text-[10px] text-[#c4c4c4]">{filteredEvents.length} codes</span>
              </div>
            </div>

            {loadingEvents ? (
              <div className="p-8 text-center">
                <div className="flex gap-1.5 justify-center mb-2">
                  <div className="w-2 h-2 bg-[#1e3a5f] rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <div className="w-2 h-2 bg-[#1e3a5f] rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <div className="w-2 h-2 bg-[#1e3a5f] rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
                <div className="text-[12px] text-[#8a8a8a]">Loading event codes...</div>
              </div>
            ) : categories.length > 0 ? (
              <div>
                {categories.map((cat) => (
                  <div key={cat}>
                    <div className="px-5 py-2 bg-[#fafaf8] border-b border-[#f0eee9] sticky top-0">
                      <span className="text-[10px] font-bold text-[#1e3a5f] uppercase tracking-wide">{cat}</span>
                    </div>
                    {filteredEvents.filter(e => e.category === cat).map((e) => (
                      <button
                        key={e.code}
                        onClick={() => copyToClipboard(e.code, e.code)}
                        className="w-full flex items-center justify-between px-5 py-2.5 border-b border-[#f0eee9] last:border-0 hover:bg-[#f5f3ee] transition text-left"
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <span className="text-[12px] font-mono font-bold text-[#1e3a5f] bg-[#f0f4fa] px-2 py-0.5 rounded shrink-0">{e.code}</span>
                          <span className="text-[12px] text-[#1a1a1a] truncate">{e.description}</span>
                        </div>
                        <span className="text-[10px] text-[#c4c4c4] shrink-0 ml-2">
                          {copiedId === e.code ? "Copied!" : "Copy"}
                        </span>
                      </button>
                    ))}
                  </div>
                ))}
              </div>
            ) : filteredEvents.length > 0 ? (
              filteredEvents.map((e) => (
                <button
                  key={e.code}
                  onClick={() => copyToClipboard(e.code, e.code)}
                  className="w-full flex items-center justify-between px-5 py-2.5 border-b border-[#f0eee9] last:border-0 hover:bg-[#f5f3ee] transition text-left"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-[12px] font-mono font-bold text-[#1e3a5f] bg-[#f0f4fa] px-2 py-0.5 rounded shrink-0">{e.code}</span>
                    <span className="text-[12px] text-[#1a1a1a] truncate">{e.description}</span>
                  </div>
                  <span className="text-[10px] text-[#c4c4c4] shrink-0 ml-2">
                    {copiedId === e.code ? "Copied!" : "Copy"}
                  </span>
                </button>
              ))
            ) : (
              <div className="p-8 text-center text-[13px] text-[#8a8a8a]">
                {eventQuery ? "No matching event codes" : "No event codes available"}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
