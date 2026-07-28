"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { feeTable, getFee, formatFee, type CourtType } from "@/lib/fees";

const COURT_TYPES: { id: CourtType; label: string }[] = [
  { id: "district", label: "District" },
  { id: "bankruptcy", label: "Bankruptcy" },
  { id: "appellate", label: "Appellate" },
];

export default function FeesPage() {
  const [type, setType] = useState<CourtType>("district");
  const [query, setQuery] = useState("");

  const match = useMemo(() => (query.trim() ? getFee(query, type) : null), [query, type]);
  const table = useMemo(() => feeTable(type), [type]);

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
            <span className="text-[13px] text-[#525252] font-medium">Filing Fee Lookup</span>
          </div>
          <Link href="/tools" className="text-[13px] text-[#1e3a5f] hover:text-[#162a47] transition font-medium">All free tools</Link>
        </div>
      </header>

      <div className="max-w-3xl mx-auto px-5 sm:px-6 py-8">
        <h1 className="text-[22px] font-bold tracking-tight text-[#1a1a1a] mb-1">Federal filing fees</h1>
        <p className="text-[13px] text-[#525252] mb-6">
          From 28 U.S.C. § 1914 and the Judicial Conference fee schedule
          (effective December 2024). Fee statuses change — confirm on{" "}
          <a href="https://www.uscourts.gov/services-forms/fees" target="_blank" rel="noopener noreferrer" className="text-[#1e3a5f] underline">uscourts.gov</a>{" "}
          before paying.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <div className="flex rounded-xl border border-[#e8e5e0] bg-white overflow-hidden">
            {COURT_TYPES.map((t) => (
              <button
                key={t.id}
                onClick={() => setType(t.id)}
                className={`px-4 py-2 text-[13px] font-medium transition ${
                  type === t.id ? "bg-[#1e3a5f] text-white" : "text-[#525252] hover:bg-[#fafaf8]"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Describe the filing — e.g. notice of appeal"
            className="flex-1 px-4 py-2 bg-white border border-[#e8e5e0] rounded-xl text-[14px] outline-none focus:border-[#1e3a5f]"
          />
        </div>

        {query.trim() && (
          <div className={`rounded-2xl border p-5 mb-8 ${match ? "bg-white border-[#1e3a5f]/30" : "bg-[#fffbeb] border-[#fde68a]"}`}>
            {match ? (
              <>
                <div className="text-[11px] font-bold text-[#8a8a8a] uppercase tracking-widest mb-1">Match</div>
                <div className="text-[16px] font-bold text-[#0f1f35]">{formatFee(match)}</div>
              </>
            ) : (
              <div className="text-[13px] text-[#b45309]">
                No fee entry matches that description. Check the full schedule
                below or your court&apos;s fee page.
              </div>
            )}
          </div>
        )}

        <h2 className="text-[11px] font-bold text-[#8a8a8a] uppercase tracking-widest mb-2">
          Full {type} schedule
        </h2>
        <div className="bg-white border border-[#e8e5e0] rounded-2xl overflow-hidden">
          {table.map(([key, fee]) => (
            <div key={key} className="flex items-start gap-4 px-4 py-2.5 border-b border-[#f0eee9] last:border-0">
              <span className={`text-[13px] font-mono font-semibold w-20 shrink-0 ${fee.amount ? "text-[#0f1f35]" : "text-[#15803d]"}`}>
                {fee.amount ? `$${fee.amount.toFixed(2)}` : "$0"}
              </span>
              <div>
                <div className="text-[13px] text-[#1a1a1a]">{fee.description}</div>
                {fee.notes && <div className="text-[11px] text-[#8a8a8a]">{fee.notes}</div>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
