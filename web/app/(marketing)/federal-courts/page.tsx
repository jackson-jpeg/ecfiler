import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "All 207 Federal Courts with CM/ECF Filing | ECFiler",
  description: "Complete directory of federal courts using CM/ECF: district, bankruptcy, and appellate courts with direct links to each court's electronic filing system.",
};

// Hardcoded court data for static generation (no API dependency at build time)
const DISTRICT_COURTS = [
  "almd:Middle District of Alabama", "alnd:Northern District of Alabama", "alsd:Southern District of Alabama",
  "akd:District of Alaska", "azd:District of Arizona",
  "ared:Eastern District of Arkansas", "arwd:Western District of Arkansas",
  "cacd:Central District of California", "caed:Eastern District of California", "cand:Northern District of California", "casd:Southern District of California",
  "cod:District of Colorado", "ctd:District of Connecticut",
  "ded:District of Delaware", "dcd:District of Columbia",
  "flmd:Middle District of Florida", "flnd:Northern District of Florida", "flsd:Southern District of Florida",
  "gamd:Middle District of Georgia", "gand:Northern District of Georgia", "gasd:Southern District of Georgia",
  "hid:District of Hawaii", "idd:District of Idaho",
  "ilcd:Central District of Illinois", "ilnd:Northern District of Illinois", "ilsd:Southern District of Illinois",
  "innd:Northern District of Indiana", "insd:Southern District of Indiana",
  "iand:Northern District of Iowa", "iasd:Southern District of Iowa",
  "ksd:District of Kansas",
  "kyed:Eastern District of Kentucky", "kywd:Western District of Kentucky",
  "laed:Eastern District of Louisiana", "lamd:Middle District of Louisiana", "lawd:Western District of Louisiana",
  "med:District of Maine", "mdd:District of Maryland",
  "mad:District of Massachusetts",
  "mied:Eastern District of Michigan", "miwd:Western District of Michigan",
  "mnd:District of Minnesota",
  "msnd:Northern District of Mississippi", "mssd:Southern District of Mississippi",
  "moed:Eastern District of Missouri", "mowd:Western District of Missouri",
  "mtd:District of Montana", "ned:District of Nebraska",
  "nvd:District of Nevada",
  "nhd:District of New Hampshire", "njd:District of New Jersey",
  "nmd:District of New Mexico",
  "nyed:Eastern District of New York", "nynd:Northern District of New York", "nysd:Southern District of New York", "nywd:Western District of New York",
  "nced:Eastern District of North Carolina", "ncmd:Middle District of North Carolina", "ncwd:Western District of North Carolina",
  "ndd:District of North Dakota",
  "ohnd:Northern District of Ohio", "ohsd:Southern District of Ohio",
  "oked:Eastern District of Oklahoma", "oknd:Northern District of Oklahoma", "okwd:Western District of Oklahoma",
  "ord:District of Oregon",
  "paed:Eastern District of Pennsylvania", "pamd:Middle District of Pennsylvania", "pawd:Western District of Pennsylvania",
  "rid:District of Rhode Island",
  "scd:District of South Carolina",
  "sdd:District of South Dakota",
  "tned:Eastern District of Tennessee", "tnmd:Middle District of Tennessee", "tnwd:Western District of Tennessee",
  "txed:Eastern District of Texas", "txnd:Northern District of Texas", "txsd:Southern District of Texas", "txwd:Western District of Texas",
  "utd:District of Utah",
  "vtd:District of Vermont",
  "vaed:Eastern District of Virginia", "vawd:Western District of Virginia",
  "waed:Eastern District of Washington", "wawd:Western District of Washington",
  "wvnd:Northern District of West Virginia", "wvsd:Southern District of West Virginia",
  "wied:Eastern District of Wisconsin", "wiwd:Western District of Wisconsin",
  "wyd:District of Wyoming",
  "gud:District of Guam", "nmid:District of Northern Mariana Islands", "prd:District of Puerto Rico", "vid:District of Virgin Islands",
].map(s => { const [id, name] = s.split(":"); return { id, name }; });

const APPELLATE_COURTS = [
  "ca1:First Circuit", "ca2:Second Circuit", "ca3:Third Circuit", "ca4:Fourth Circuit",
  "ca5:Fifth Circuit", "ca6:Sixth Circuit", "ca7:Seventh Circuit", "ca8:Eighth Circuit",
  "ca9:Ninth Circuit", "ca10:Tenth Circuit", "ca11:Eleventh Circuit", "cadc:D.C. Circuit", "cafc:Federal Circuit",
].map(s => { const [id, name] = s.split(":"); return { id, name }; });

function CourtTable({ courts, type }: { courts: { id: string; name: string }[]; type: string }) {
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
            <tr key={c.id} className="hover:bg-[#fafaf8] transition-colors">
              <td className="px-4 py-2 font-mono text-[12px] font-semibold text-[#1e3a5f] border-b border-[#f0eee9]">{c.id}</td>
              <td className="px-4 py-2 text-[13px] text-[#1a1a1a] border-b border-[#f0eee9]">{c.name}</td>
              <td className="px-4 py-2 border-b border-[#f0eee9] hidden sm:table-cell">
                <a
                  href={`https://ecf.${c.id}.uscourts.gov`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[11px] text-[#1e3a5f] font-mono hover:underline"
                >
                  ecf.{c.id}.uscourts.gov &#x2197;
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
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
          Every federal court in the United States uses CM/ECF for electronic filing. ECFiler supports all 207 of them. Click any court to visit its CM/ECF site.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 mb-10">
        {[
          { n: String(DISTRICT_COURTS.length), label: "District Courts", color: "text-[#1e3a5f]", bg: "bg-[#f0f4fa]", border: "border-[#bfdbfe]" },
          { n: String(DISTRICT_COURTS.length), label: "Bankruptcy Courts", color: "text-[#7c3aed]", bg: "bg-[#f5f3ff]", border: "border-[#c4b5fd]" },
          { n: String(APPELLATE_COURTS.length), label: "Appellate Courts", color: "text-[#b45309]", bg: "bg-[#fffbeb]", border: "border-[#fde68a]" },
        ].map(({ n, label, color, bg, border }) => (
          <div key={label} className={`${bg} border ${border} rounded-xl p-4 text-center`}>
            <div className={`text-[22px] font-bold ${color}`}>{n}</div>
            <div className="text-[11px] text-[#8a8a8a] font-medium">{label}</div>
          </div>
        ))}
      </div>

      {/* District Courts */}
      <div className="mb-10">
        <h2 className="text-[18px] font-bold text-[#1a1a1a] mb-4 flex items-center gap-2">
          <span className="w-3 h-3 bg-[#1e3a5f] rounded-sm" />
          District Courts ({DISTRICT_COURTS.length})
        </h2>
        <CourtTable courts={DISTRICT_COURTS} type="district" />
      </div>

      {/* Appellate Courts */}
      <div className="mb-10">
        <h2 className="text-[18px] font-bold text-[#1a1a1a] mb-4 flex items-center gap-2">
          <span className="w-3 h-3 bg-[#b45309] rounded-sm" />
          Appellate Courts ({APPELLATE_COURTS.length})
        </h2>
        <CourtTable courts={APPELLATE_COURTS} type="appellate" />
      </div>

      {/* Note about bankruptcy */}
      <div className="bg-[#f5f3ff] border border-[#c4b5fd] rounded-2xl p-6 mb-10">
        <h3 className="text-[15px] font-bold text-[#7c3aed] mb-2">Bankruptcy Courts</h3>
        <p className="text-[13px] text-[#6b21a8] leading-relaxed">
          Each federal judicial district has a corresponding bankruptcy court (e.g., <code className="text-[12px] bg-white/50 px-1 py-0.5 rounded">nysb</code> for the Southern District of New York Bankruptcy Court).
          Bankruptcy courts use the same CM/ECF system at URLs like <code className="text-[12px] bg-white/50 px-1 py-0.5 rounded">ecf.nysb.uscourts.gov</code>.
          ECFiler supports all {DISTRICT_COURTS.length} bankruptcy courts.
        </p>
      </div>

      {/* CTA */}
      <div className="bg-gradient-to-r from-[#0f1f35] to-[#1e3a5f] rounded-2xl p-8 text-center">
        <h2 className="text-[20px] font-bold text-white mb-2">File on any of these courts</h2>
        <p className="text-[14px] text-white/50 mb-6">Drop a PDF. ECFiler detects the court automatically.</p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link href="/sign-up" className="px-6 py-2.5 bg-white text-[#1e3a5f] text-[14px] font-semibold rounded-xl hover:bg-[#f0f4fa] transition shadow-lg">Start Filing Free</Link>
          <Link href="/courts" className="px-6 py-2.5 border border-white/20 text-white/70 text-[14px] font-semibold rounded-xl hover:text-white hover:border-white/40 transition">Search Courts</Link>
        </div>
      </div>
    </div>
  );
}
