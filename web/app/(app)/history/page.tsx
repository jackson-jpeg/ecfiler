"use client";

import { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { getHistory } from "@/lib/api";

type StatusFilter = "all" | "submitted" | "error";

const PAGE_SIZE = 20;

function formatDate(raw: unknown): string {
  if (!raw) return "";
  const d = new Date(String(raw));
  if (isNaN(d.getTime())) return String(raw).substring(0, 10);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function normalizeStatus(raw: unknown): string {
  const s = String(raw || "").toLowerCase().trim();
  if (s === "filed" || s === "submitted" || s === "success") return "submitted";
  if (s === "error" || s === "failed" || s === "rejected") return "error";
  return s || "pending";
}

function statusColor(status: string): { bg: string; text: string } {
  switch (status) {
    case "submitted":
      return { bg: "bg-[#f0fdf4]", text: "text-[#15803d]" };
    case "error":
      return { bg: "bg-[#fef2f2]", text: "text-[#b91c1c]" };
    default:
      return { bg: "bg-[#f5f5f4]", text: "text-[#8a8a8a]" };
  }
}

function exportCSV(rows: Record<string, unknown>[]) {
  const headers = ["Date", "Court", "Case Number", "Event Description", "Status"];
  const csvRows = [
    headers.join(","),
    ...rows.map((r) =>
      [
        String(r.filed_at || "").substring(0, 10),
        String(r.court_id || ""),
        `"${String(r.case_number || "").replace(/"/g, '""')}"`,
        `"${String(r.event_description || "").replace(/"/g, '""')}"`,
        String(r.status || ""),
      ].join(",")
    ),
  ];
  const blob = new Blob([csvRows.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `filing-history-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export default function HistoryPage() {
  const [history, setHistory] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [page, setPage] = useState(1);

  useEffect(() => {
    getHistory()
      .then(setHistory)
      .finally(() => setLoading(false));
  }, []);

  // Reset to page 1 when filters change
  useEffect(() => { setPage(1); }, [search, statusFilter]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase().trim();
    return history.filter((h) => {
      const status = normalizeStatus(h.status);
      if (statusFilter === "submitted" && status !== "submitted") return false;
      if (statusFilter === "error" && status !== "error") return false;
      if (q) {
        const haystack = [
          String(h.case_number || ""),
          String(h.court_id || ""),
          String(h.event_description || ""),
        ]
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }, [history, search, statusFilter]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  // Stats
  const totalFilings = history.length;
  const successCount = history.filter((h) => normalizeStatus(h.status) === "submitted").length;
  const successRate = totalFilings > 0 ? Math.round((successCount / totalFilings) * 100) : 0;
  const mostRecent = history.reduce((latest: string, h) => {
    const d = String(h.filed_at || "");
    return d > latest ? d : latest;
  }, "");

  const statusTabs: { key: StatusFilter; label: string; count: number }[] = [
    { key: "all", label: "All", count: history.length },
    {
      key: "submitted",
      label: "Submitted",
      count: history.filter((h) => normalizeStatus(h.status) === "submitted").length,
    },
    {
      key: "error",
      label: "Error",
      count: history.filter((h) => normalizeStatus(h.status) === "error").length,
    },
  ];

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
              <span className="text-[15px] font-semibold tracking-tight text-[#1a1a1a]">
                ECFiler
              </span>
            </Link>
            <div className="h-5 w-px bg-[#e8e5e0]" />
            <span className="text-[13px] text-[#525252] font-medium">Filing History</span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/file"
              className="text-[13px] text-[#1e3a5f] hover:text-[#162a47] transition font-medium"
            >
              &larr; Back to Filing
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        {/* Title row */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3 mb-6">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-[#1a1a1a] mb-1">
              Filing History
            </h1>
            <p className="text-sm text-[#525252]">Audit log of all court filings.</p>
          </div>
          {history.length > 0 && (
            <button
              onClick={() => exportCSV(filtered)}
              className="inline-flex items-center gap-2 px-4 py-2 text-[13px] font-medium text-[#1e3a5f] bg-white border border-[#e8e5e0] rounded-lg hover:bg-[#fafaf8] transition shadow-sm self-start sm:self-auto"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Export CSV
            </button>
          )}
        </div>

        {/* Stats bar */}
        {history.length > 0 && (
          <div className="grid grid-cols-3 gap-3 sm:gap-4 mb-6">
            <div className="bg-white border border-[#e8e5e0] rounded-2xl p-4 shadow-sm">
              <p className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1">
                Total Filings
              </p>
              <p className="text-2xl font-bold text-[#1a1a1a]">{totalFilings}</p>
            </div>
            <div className="bg-white border border-[#e8e5e0] rounded-2xl p-4 shadow-sm">
              <p className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1">
                Success Rate
              </p>
              <p className="text-2xl font-bold text-[#15803d]">{successRate}%</p>
            </div>
            <div className="bg-white border border-[#e8e5e0] rounded-2xl p-4 shadow-sm">
              <p className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1">
                Most Recent
              </p>
              <p className="text-lg font-bold text-[#1a1a1a] truncate">
                {mostRecent ? formatDate(mostRecent) : "--"}
              </p>
            </div>
          </div>
        )}

        {/* Search + filter bar */}
        {history.length > 0 && (
          <div className="flex flex-col sm:flex-row gap-3 mb-5">
            {/* Search */}
            <div className="relative flex-1">
              <svg
                className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8a8a8a]"
                width="15"
                height="15"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input
                type="text"
                placeholder="Search by case number, court, or event..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-2.5 text-[13px] bg-white border border-[#e8e5e0] rounded-lg text-[#1a1a1a] placeholder-[#8a8a8a] focus:outline-none focus:ring-2 focus:ring-[#1e3a5f]/20 focus:border-[#1e3a5f] transition"
              />
            </div>
            {/* Status tabs */}
            <div className="flex gap-1.5 bg-white border border-[#e8e5e0] rounded-lg p-1 self-start">
              {statusTabs.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setStatusFilter(tab.key)}
                  className={`px-3.5 py-1.5 text-[12px] font-medium rounded-md transition ${
                    statusFilter === tab.key
                      ? "bg-[#1e3a5f] text-white shadow-sm"
                      : "text-[#525252] hover:bg-[#f5f3ee]"
                  }`}
                >
                  {tab.label}
                  <span
                    className={`ml-1.5 text-[11px] ${
                      statusFilter === tab.key ? "text-white/70" : "text-[#8a8a8a]"
                    }`}
                  >
                    {tab.count}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="bg-white border border-[#e8e5e0] rounded-2xl p-14 text-center shadow-sm">
            <div className="inline-block w-6 h-6 border-2 border-[#e8e5e0] border-t-[#1e3a5f] rounded-full animate-spin mb-3" />
            <p className="text-sm text-[#8a8a8a]">Loading filing history...</p>
          </div>
        )}

        {/* Empty state */}
        {!loading && history.length === 0 && (
          <div className="bg-white border border-[#e8e5e0] rounded-2xl p-14 text-center shadow-sm">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-[#f5f3ee] flex items-center justify-center">
              <svg
                width="28"
                height="28"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#8a8a8a"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="12" y1="18" x2="12" y2="12" />
                <line x1="9" y1="15" x2="15" y2="15" />
              </svg>
            </div>
            <p className="text-[15px] font-semibold text-[#1a1a1a] mb-1">No filings yet</p>
            <p className="text-sm text-[#8a8a8a] mb-5">
              Drop a PDF to start your first filing.
            </p>
            <Link
              href="/file"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#1e3a5f] text-white text-[13px] font-medium rounded-lg hover:bg-[#162a47] transition shadow-sm"
            >
              Go to Filing
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="5" y1="12" x2="19" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
            </Link>
          </div>
        )}

        {/* No results for current filter */}
        {!loading && history.length > 0 && filtered.length === 0 && (
          <div className="bg-white border border-[#e8e5e0] rounded-2xl p-14 text-center shadow-sm">
            <p className="text-sm text-[#8a8a8a]">
              No filings match your current filters.
            </p>
            <button
              onClick={() => {
                setSearch("");
                setStatusFilter("all");
              }}
              className="mt-3 text-[13px] text-[#1e3a5f] font-medium hover:underline"
            >
              Clear filters
            </button>
          </div>
        )}

        {/* Desktop table */}
        {!loading && paginated.length > 0 && (
          <>
            <div className="hidden md:block bg-white border border-[#e8e5e0] rounded-2xl overflow-hidden shadow-sm">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left">
                    <th className="px-5 py-3 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">
                      Date
                    </th>
                    <th className="px-5 py-3 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">
                      Court
                    </th>
                    <th className="px-5 py-3 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">
                      Case
                    </th>
                    <th className="px-5 py-3 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">
                      Event
                    </th>
                    <th className="px-5 py-3 text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8] w-28">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {paginated.map((h, i) => {
                    const status = normalizeStatus(h.status);
                    const sc = statusColor(status);
                    const desc = String(h.event_description || "");
                    return (
                      <tr
                        key={i}
                        className="hover:bg-[#fafaf8]/60 transition-colors"
                      >
                        <td className="px-5 py-3 text-[#525252] border-b border-[#f0eee9] whitespace-nowrap">
                          {formatDate(h.filed_at)}
                        </td>
                        <td className="px-5 py-3 border-b border-[#f0eee9]">
                          <span className="inline-block px-2 py-0.5 text-[11px] font-semibold bg-[#f0f4f8] text-[#1e3a5f] rounded-md uppercase tracking-wide">
                            {String(h.court_id || "").toUpperCase()}
                          </span>
                        </td>
                        <td className="px-5 py-3 border-b border-[#f0eee9] font-mono text-[13px] text-[#1a1a1a]">
                          {String(h.case_number || "")}
                        </td>
                        <td className="px-5 py-3 text-[#525252] border-b border-[#f0eee9] max-w-[280px]">
                          <span className="block truncate" title={desc}>
                            {desc}
                          </span>
                        </td>
                        <td className="px-5 py-3 border-b border-[#f0eee9]">
                          <span
                            className={`inline-block text-[11px] px-2.5 py-1 rounded-full font-semibold capitalize ${sc.bg} ${sc.text}`}
                          >
                            {status}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Mobile cards */}
            <div className="md:hidden space-y-3">
              {paginated.map((h, i) => {
                const status = normalizeStatus(h.status);
                const sc = statusColor(status);
                const desc = String(h.event_description || "");
                return (
                  <div
                    key={i}
                    className="bg-white border border-[#e8e5e0] rounded-2xl p-4 shadow-sm"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-[12px] text-[#8a8a8a]">
                        {formatDate(h.filed_at)}
                      </span>
                      <span
                        className={`text-[11px] px-2.5 py-1 rounded-full font-semibold capitalize ${sc.bg} ${sc.text}`}
                      >
                        {status}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="inline-block px-2 py-0.5 text-[10px] font-semibold bg-[#f0f4f8] text-[#1e3a5f] rounded-md uppercase tracking-wide">
                        {String(h.court_id || "").toUpperCase()}
                      </span>
                      <span className="font-mono text-[13px] text-[#1a1a1a]">
                        {String(h.case_number || "")}
                      </span>
                    </div>
                    <p className="text-[13px] text-[#525252] line-clamp-2" title={desc}>
                      {desc}
                    </p>
                  </div>
                );
              })}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-5">
                <p className="text-[12px] text-[#8a8a8a]">
                  Showing {(page - 1) * PAGE_SIZE + 1}&ndash;{Math.min(page * PAGE_SIZE, filtered.length)} of {filtered.length}
                </p>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-3 py-1.5 text-[12px] font-medium bg-white border border-[#e8e5e0] rounded-lg disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[#fafaf8] transition text-[#525252]"
                  >
                    Previous
                  </button>
                  {Array.from({ length: totalPages }, (_, i) => i + 1)
                    .filter(
                      (p) =>
                        p === 1 ||
                        p === totalPages ||
                        (p >= page - 1 && p <= page + 1)
                    )
                    .reduce<(number | "...")[]>((acc, p, idx, arr) => {
                      if (idx > 0 && p - (arr[idx - 1] as number) > 1) acc.push("...");
                      acc.push(p);
                      return acc;
                    }, [])
                    .map((p, idx) =>
                      p === "..." ? (
                        <span key={`dot-${idx}`} className="px-1 text-[12px] text-[#8a8a8a]">
                          ...
                        </span>
                      ) : (
                        <button
                          key={p}
                          onClick={() => setPage(p as number)}
                          className={`w-8 h-8 text-[12px] font-medium rounded-lg transition ${
                            page === p
                              ? "bg-[#1e3a5f] text-white shadow-sm"
                              : "bg-white border border-[#e8e5e0] text-[#525252] hover:bg-[#fafaf8]"
                          }`}
                        >
                          {p}
                        </button>
                      )
                    )}
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="px-3 py-1.5 text-[12px] font-medium bg-white border border-[#e8e5e0] rounded-lg disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[#fafaf8] transition text-[#525252]"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
