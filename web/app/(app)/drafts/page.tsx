"use client";

import { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { getDrafts } from "@/lib/api";

/* ── Types ──────────────────────────────────────────────────────── */

interface UnifiedDraft {
  id: string;
  source: "server" | "local";
  name: string;
  documentType: string;
  court: string;
  caseNumber: string;
  savedAt: string;
  isSealed: boolean;
  isRedacted: boolean;
  raw: Record<string, unknown>;
}

/* ── Helpers ─────────────────────────────────────────────────────── */

function relativeTime(iso: string): string {
  const ms = Date.now() - new Date(iso).getTime();
  const sec = Math.floor(ms / 1000);
  if (sec < 60) return "just now";
  const min = Math.floor(sec / 60);
  if (min < 60) return `${min}m ago`;
  const hrs = Math.floor(min / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 30) return `${days}d ago`;
  return new Date(iso).toLocaleDateString();
}

function loadLocalDrafts(): UnifiedDraft[] {
  const drafts: UnifiedDraft[] = [];
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (!key?.startsWith("ecfiler_draft_")) continue;
    try {
      const raw = JSON.parse(localStorage.getItem(key)!) as Record<string, unknown>;
      const filing = (raw.filing ?? {}) as Record<string, unknown>;
      drafts.push({
        id: key,
        source: "local",
        name: key,
        documentType: String(filing.document_type || filing.event_description || "Unknown"),
        court: String(filing.court_id || ""),
        caseNumber: String(filing.case_number || ""),
        savedAt: String(raw.savedAt || ""),
        isSealed: Boolean(raw.isSealed),
        isRedacted: Boolean(raw.isRedacted),
        raw,
      });
    } catch { /* skip corrupt entries */ }
  }
  return drafts;
}

function normalizeServerDraft(d: Record<string, unknown>, idx: number): UnifiedDraft {
  return {
    id: String(d.file || d.name || `server-${idx}`),
    source: "server",
    name: String(d.name || d.file || ""),
    documentType: String(d.document_type || d.name || "Filing"),
    court: String(d.court || ""),
    caseNumber: String(d.case || d.case_number || ""),
    savedAt: String(d.saved_at || d.savedAt || ""),
    isSealed: Boolean(d.is_sealed),
    isRedacted: Boolean(d.is_redacted),
    raw: d,
  };
}

/* ── Component ──────────────────────────────────────────────────── */

export default function DraftsPage() {
  const [serverDrafts, setServerDrafts] = useState<UnifiedDraft[]>([]);
  const [localDrafts, setLocalDrafts] = useState<UnifiedDraft[]>([]);
  const [search, setSearch] = useState("");
  const [sortNewest, setSortNewest] = useState(true);
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  /* ── Load drafts ─────────────────────────────────────────────── */

  const refresh = () => {
    setLoading(true);
    getDrafts()
      .then((data) => setServerDrafts(data.map(normalizeServerDraft)))
      .catch(() => setServerDrafts([]))
      .finally(() => setLoading(false));
    setLocalDrafts(loadLocalDrafts());
  };

  useEffect(() => { refresh(); }, []);

  /* ── Derived state ───────────────────────────────────────────── */

  const allDrafts = useMemo(() => {
    let list = [...serverDrafts, ...localDrafts];

    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (d) =>
          d.documentType.toLowerCase().includes(q) ||
          d.court.toLowerCase().includes(q) ||
          d.caseNumber.toLowerCase().includes(q),
      );
    }

    list.sort((a, b) => {
      const ta = new Date(a.savedAt).getTime() || 0;
      const tb = new Date(b.savedAt).getTime() || 0;
      return sortNewest ? tb - ta : ta - tb;
    });

    return list;
  }, [serverDrafts, localDrafts, search, sortNewest]);

  /* ── Delete handlers ─────────────────────────────────────────── */

  const deleteDraft = async (draft: UnifiedDraft) => {
    if (draft.source === "local") {
      localStorage.removeItem(draft.id);
      setLocalDrafts(loadLocalDrafts());
    } else {
      await fetch(`/api/drafts/${encodeURIComponent(draft.id)}`, { method: "DELETE" });
      const data = await getDrafts();
      setServerDrafts(data.map(normalizeServerDraft));
    }
    setConfirmId(null);
  };

  /* ── Resume handler ──────────────────────────────────────────── */

  const resumeHref = (draft: UnifiedDraft): string => {
    if (draft.source === "local") {
      return `/file?resume_draft=${encodeURIComponent(draft.id)}`;
    }
    const params = new URLSearchParams();
    if (draft.court) params.set("court", draft.court);
    if (draft.caseNumber) params.set("case", draft.caseNumber);
    if (draft.name) params.set("draft", draft.name);
    return `/file?${params.toString()}`;
  };

  /* ── Render ──────────────────────────────────────────────────── */

  return (
    <div className="min-h-screen bg-[#f5f3ee]">
      {/* Header */}
      <header className="bg-white border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/file" className="flex items-center gap-2.5">
              <div className="w-7 h-7 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[10px] font-bold">
                E
              </div>
              <span className="text-[15px] font-semibold tracking-tight text-[#1a1a1a]">ECFiler</span>
            </Link>
            <div className="h-5 w-px bg-[#e8e5e0]" />
            <span className="text-[13px] text-[#525252] font-medium">Drafts</span>
          </div>
          <Link
            href="/file"
            className="text-[13px] text-[#1e3a5f] hover:text-[#162a47] transition font-medium"
          >
            &larr; Back to Filing
          </Link>
        </div>
      </header>

      {/* Body */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Title row */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-6">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-[#1a1a1a] mb-1">Drafts</h1>
            <p className="text-sm text-[#525252]">Resume incomplete filings.</p>
          </div>

          {/* Search & sort */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <svg
                className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#8a8a8a]"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z" />
              </svg>
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Filter by court or type..."
                className="pl-9 pr-3 py-2 text-[13px] bg-white border border-[#e8e5e0] rounded-xl w-56 focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/20 focus:border-[#1e3a5f]/40 transition placeholder:text-[#b5b5b5]"
              />
            </div>
            <button
              onClick={() => setSortNewest((v) => !v)}
              className="flex items-center gap-1.5 px-3 py-2 text-[12px] font-medium text-[#525252] bg-white border border-[#e8e5e0] rounded-xl hover:border-[#c8c5c0] transition"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 4h13M3 8h9M3 12h5m4 0l4 4m0 0l4-4m-4 4V4" />
              </svg>
              {sortNewest ? "Newest" : "Oldest"}
            </button>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white border border-[#e8e5e0] rounded-2xl p-5 animate-pulse">
                <div className="flex items-start justify-between">
                  <div className="space-y-2.5 flex-1">
                    <div className="h-4 bg-[#e8e5e0] rounded w-2/3" />
                    <div className="h-3 bg-[#f0eee9] rounded w-1/3" />
                    <div className="h-3 bg-[#f0eee9] rounded w-1/2" />
                  </div>
                  <div className="h-8 w-20 bg-[#f0eee9] rounded-lg" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && allDrafts.length === 0 && (
          <div className="flex flex-col items-center justify-center py-24">
            <div className="w-16 h-16 rounded-2xl bg-white border border-[#e8e5e0] flex items-center justify-center mb-5 shadow-sm">
              <svg className="w-7 h-7 text-[#c0bdb8]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
            </div>
            <p className="text-[15px] font-semibold text-[#1a1a1a] mb-1">No drafts yet</p>
            <p className="text-[13px] text-[#8a8a8a] mb-5">
              {search ? "Nothing matches your filter." : "Start a filing and save it as a draft to see it here."}
            </p>
            {!search && (
              <Link
                href="/file"
                className="px-4 py-2 text-[13px] font-medium text-white bg-[#1e3a5f] hover:bg-[#162a47] rounded-xl transition"
              >
                Start a Filing
              </Link>
            )}
          </div>
        )}

        {/* Draft cards */}
        {!loading && allDrafts.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {allDrafts.map((draft) => (
              <div
                key={draft.id}
                className="bg-white border border-[#e8e5e0] rounded-2xl shadow-sm p-5 flex flex-col justify-between hover:shadow-md transition"
              >
                {/* Top */}
                <div className="mb-4">
                  {/* Source badge + date */}
                  <div className="flex items-center justify-between mb-3">
                    <span
                      className={`inline-block text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-md ${
                        draft.source === "local"
                          ? "bg-amber-50 text-amber-600 border border-amber-200"
                          : "bg-blue-50 text-[#1e3a5f] border border-blue-200"
                      }`}
                    >
                      {draft.source === "local" ? "Local" : "Server"}
                    </span>
                    <span className="text-[11px] text-[#8a8a8a]">
                      {draft.savedAt ? relativeTime(draft.savedAt) : "Unknown"}
                    </span>
                  </div>

                  {/* Document type */}
                  <h3 className="text-[14px] font-semibold text-[#1a1a1a] leading-snug mb-2 line-clamp-2">
                    {draft.documentType || "Untitled Draft"}
                  </h3>

                  {/* Meta */}
                  <div className="space-y-1.5">
                    {draft.court && (
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide w-12 shrink-0">Court</span>
                        <span className="text-[12px] text-[#525252] font-mono truncate">{draft.court}</span>
                      </div>
                    )}
                    {draft.caseNumber && (
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide w-12 shrink-0">Case</span>
                        <span className="text-[12px] text-[#525252] truncate">{draft.caseNumber}</span>
                      </div>
                    )}
                  </div>

                  {/* Badges */}
                  {(draft.isSealed || draft.isRedacted) && (
                    <div className="flex items-center gap-2 mt-3">
                      {draft.isSealed && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-md bg-red-50 text-red-600 border border-red-200">
                          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
                          </svg>
                          Sealed
                        </span>
                      )}
                      {draft.isRedacted && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-md bg-orange-50 text-orange-600 border border-orange-200">
                          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12c1.292 4.338 5.31 7.5 10.066 7.5.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                          </svg>
                          Redacted
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 pt-3 border-t border-[#f0eee9]">
                  <Link
                    href={resumeHref(draft)}
                    className="flex-1 text-center px-3 py-2 text-[12px] font-semibold text-white bg-[#1e3a5f] hover:bg-[#162a47] rounded-xl transition"
                  >
                    Resume
                  </Link>
                  {confirmId === draft.id ? (
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => deleteDraft(draft)}
                        className="px-3 py-2 text-[12px] font-semibold text-white bg-red-600 hover:bg-red-700 rounded-xl transition"
                      >
                        Confirm
                      </button>
                      <button
                        onClick={() => setConfirmId(null)}
                        className="px-3 py-2 text-[12px] font-medium text-[#525252] bg-[#f5f3ee] hover:bg-[#eae7e2] rounded-xl transition"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setConfirmId(draft.id)}
                      className="px-3 py-2 text-[12px] font-medium text-[#8a8a8a] hover:text-red-600 bg-[#f5f3ee] hover:bg-red-50 rounded-xl transition"
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Count */}
        {!loading && allDrafts.length > 0 && (
          <p className="text-center text-[11px] text-[#8a8a8a] mt-6">
            {allDrafts.length} draft{allDrafts.length !== 1 ? "s" : ""}
            {search && " matching filter"}
          </p>
        )}
      </div>
    </div>
  );
}
