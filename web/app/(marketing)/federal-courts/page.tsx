import type { Metadata } from "next";
import Link from "next/link";
import { listCourts, type Court } from "@/lib/courts-data";

// Every count on this page is computed from lib/data/*.json — the same data
// the registry (ecfiler/courts/registry.py) ships, parity-enforced by
// tests/test_web_data_parity.py. No hand-typed court numbers anywhere.
const DISTRICT_ALL = listCourts("district");
const BANKRUPTCY = listCourts("bankruptcy");
const APPELLATE_ALL = listCourts("appellate");

// The registry types three national courts as "district" and the three
// Bankruptcy Appellate Panels as "appellate"; split them out so the total
// decomposes explicitly.
const NATIONAL_IDS = new Set(["jpml", "citd", "usfcc"]);
const DISTRICT = DISTRICT_ALL.filter((c) => !NATIONAL_IDS.has(c.court_id));
const NATIONAL = DISTRICT_ALL.filter((c) => NATIONAL_IDS.has(c.court_id));
const CIRCUITS = APPELLATE_ALL.filter((c) => !c.court_id.startsWith("bap"));
const BAPS = APPELLATE_ALL.filter((c) => c.court_id.startsWith("bap"));

const TOTAL = DISTRICT_ALL.length + BANKRUPTCY.length + APPELLATE_ALL.length;

export const metadata: Metadata = {
  title: `All ${TOTAL} Federal Courts with CM/ECF Filing | ECFiler`,
  description: `Complete directory of all ${TOTAL} federal courts using CM/ECF: ${DISTRICT.length} district courts, ${BANKRUPTCY.length} bankruptcy courts, ${CIRCUITS.length} courts of appeals, ${BAPS.length} bankruptcy appellate panels, and ${NATIONAL.length} national courts, with direct links to each court's electronic filing system.`,
};

function CourtTable({ courts }: { courts: Court[] }) {
  return (
    <div className="bg-white border border-[#e8e5e0] rounded-2xl overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr>
            <th className="px-4 py-2.5 text-left text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8] w-20">ID</th>
            <th className="px-4 py-2.5 text-left text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8]">Court Name</th>
            <th className="px-4 py-2.5 text-left text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide border-b border-[#e8e5e0] bg-[#fafaf8] hidden sm:table-cell">CM/ECF Link</th>
          </tr>
        </thead>
        <tbody>
          {courts.map((c) => (
            <tr key={c.court_id} className="hover:bg-[#fafaf8] transition-colors">
              <td className="px-4 py-2 font-mono text-[12px] font-semibold text-[#1e3a5f] border-b border-[#f0eee9]">{c.court_id}</td>
              <td className="px-4 py-2 text-[13px] text-[#1a1a1a] border-b border-[#f0eee9]">{c.name}</td>
              <td className="px-4 py-2 border-b border-[#f0eee9] hidden sm:table-cell">
                <a
                  href={c.ecf_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[11px] text-[#1e3a5f] font-mono hover:underline"
                >
                  {c.ecf_url.replace("https://", "")} &#x2197;
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Section({ title, color, courts }: { title: string; color: string; courts: Court[] }) {
  return (
    <div className="mb-10">
      <h2 className="text-[18px] font-bold text-[#1a1a1a] mb-4 flex items-center gap-2">
        <span className={`w-3 h-3 ${color} rounded-sm`} />
        {title} ({courts.length})
      </h2>
      <CourtTable courts={courts} />
    </div>
  );
}

export default function FederalCourtsPage() {
  return (
    <div>
      {/* Hero */}
      <div className="mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#f0fdf4] border border-[#bbf7d0] rounded-full text-[11px] font-semibold text-[#15803d] mb-4">
          <span className="w-1.5 h-1.5 bg-[#15803d] rounded-full" />
          All courts supported by ECFiler
        </div>
        <h1 className="text-[28px] sm:text-[36px] font-bold tracking-tight text-[#1a1a1a] mb-3">Federal Court Directory</h1>
        <p className="text-[16px] text-[#525252] leading-relaxed max-w-2xl">
          ECFiler prepares and stages filings for all {TOTAL} federal courts in
          its registry: {DISTRICT.length} district courts, {BANKRUPTCY.length}{" "}
          bankruptcy courts, {CIRCUITS.length} courts of appeals,{" "}
          {BAPS.length} bankruptcy appellate panels, and {NATIONAL.length}{" "}
          national courts. Click any court to visit its CM/ECF site.
        </p>
      </div>

      {/* Stats — computed, and they sum to the headline */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-10">
        {[
          { n: DISTRICT.length, label: "District Courts", color: "text-[#1e3a5f]", bg: "bg-[#f0f4fa]", border: "border-[#bfdbfe]" },
          { n: BANKRUPTCY.length, label: "Bankruptcy Courts", color: "text-[#7c3aed]", bg: "bg-[#f5f3ff]", border: "border-[#c4b5fd]" },
          { n: CIRCUITS.length, label: "Courts of Appeals", color: "text-[#b45309]", bg: "bg-[#fffbeb]", border: "border-[#fde68a]" },
          { n: BAPS.length, label: "Bankruptcy Appellate Panels", color: "text-[#b45309]", bg: "bg-[#fffbeb]", border: "border-[#fde68a]" },
          { n: NATIONAL.length, label: "National Courts", color: "text-[#15803d]", bg: "bg-[#f0fdf4]", border: "border-[#bbf7d0]" },
        ].map(({ n, label, color, bg, border }) => (
          <div key={label} className={`${bg} border ${border} rounded-xl p-4 text-center`}>
            <div className={`text-[22px] font-bold ${color}`}>{n}</div>
            <div className="text-[11px] text-[#8a8a8a] font-medium">{label}</div>
          </div>
        ))}
      </div>
      <p className="text-[13px] text-[#8a8a8a] -mt-6 mb-10">
        {DISTRICT.length} + {BANKRUPTCY.length} + {CIRCUITS.length} +{" "}
        {BAPS.length} + {NATIONAL.length} = {TOTAL}. The district count
        includes the four territorial courts (Guam, Northern Mariana Islands,
        Puerto Rico, Virgin Islands); the national courts are the Judicial
        Panel on Multidistrict Litigation, the Court of International Trade,
        and the Court of Federal Claims.
      </p>

      <Section title="District Courts" color="bg-[#1e3a5f]" courts={DISTRICT} />
      <Section title="Bankruptcy Courts" color="bg-[#7c3aed]" courts={BANKRUPTCY} />
      <Section title="Courts of Appeals" color="bg-[#b45309]" courts={CIRCUITS} />
      <Section title="Bankruptcy Appellate Panels" color="bg-[#b45309]" courts={BAPS} />
      <Section title="National Courts" color="bg-[#15803d]" courts={NATIONAL} />

      {/* CTA */}
      <div className="bg-gradient-to-r from-[#0f1f35] to-[#1e3a5f] rounded-2xl p-8 text-center">
        <h2 className="text-[20px] font-bold text-white mb-2">Prepare filings for any of these courts</h2>
        <p className="text-[14px] text-white/50 mb-6">Drop a PDF. ECFiler detects the court automatically and stages the filing for you to submit.</p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link href="/sign-up" className="px-6 py-2.5 bg-white text-[#1e3a5f] text-[14px] font-semibold rounded-xl hover:bg-[#f0f4fa] transition shadow-lg">Start Filing Free</Link>
          <Link href="/courts" className="px-6 py-2.5 border border-white/20 text-white/70 text-[14px] font-semibold rounded-xl hover:text-white hover:border-white/40 transition">Search Courts</Link>
        </div>
      </div>
    </div>
  );
}
