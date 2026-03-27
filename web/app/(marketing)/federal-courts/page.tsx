import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "All 207 Federal Courts with CM/ECF Filing | ECFiler",
  description: "Complete list of federal courts using CM/ECF for electronic filing: 97 district courts, 94 bankruptcy courts, 16 appellate courts.",
};

export default function FederalCourtsPage() {
  return (
    <article className="prose prose-zinc max-w-none">
      <h1 className="text-3xl font-bold tracking-tight mb-2">Federal Courts with CM/ECF</h1>
      <p className="text-lg text-zinc-500 mb-8">All 207 federal courts that use CM/ECF for electronic filing.</p>

      <p>
        Every federal court in the United States uses CM/ECF for electronic document filing. <Link href="/file" className="text-blue-600 font-semibold hover:underline">ECFiler</Link> supports all 207 of them.
      </p>

      <h2>Court types</h2>

      <h3>District Courts (97)</h3>
      <p>
        The 94 federal judicial districts plus the Judicial Panel on Multidistrict Litigation (JPML), the Court of International Trade, and the Court of Federal Claims. District courts handle civil and criminal cases at the trial level.
      </p>

      <h3>Bankruptcy Courts (94)</h3>
      <p>
        Each federal judicial district has a bankruptcy court. Bankruptcy courts handle Chapter 7, 11, 12, and 13 cases. Many support XML case opening for automated petition filing.
      </p>

      <h3>Appellate Courts (16)</h3>
      <p>
        The 13 circuit courts of appeals (1st through 11th, D.C. Circuit, and Federal Circuit) plus three Bankruptcy Appellate Panels (1st, 9th, and 10th Circuits). Appellate courts have different filing procedures, including page/word count requirements and certificates of compliance.
      </p>

      <h2>Finding your court</h2>
      <p>
        Use <Link href="/courts" className="text-blue-600 font-semibold hover:underline">ECFiler&apos;s court search</Link> to find any federal court by name, abbreviation, or location. Each court&apos;s CM/ECF system has a URL in the format <code>ecf.[court_id].uscourts.gov</code>.
      </p>

      <div className="bg-zinc-50 border border-zinc-200 rounded-2xl p-6 mt-8 not-prose">
        <h3 className="text-base font-bold mb-2">Search all 207 courts</h3>
        <p className="text-sm text-zinc-500 mb-4">Find any federal court by name, state, or court ID.</p>
        <Link href="/courts" className="px-5 py-2 bg-zinc-900 text-white text-sm font-semibold rounded-lg hover:bg-zinc-800 transition">
          Browse Courts &rarr;
        </Link>
      </div>
    </article>
  );
}
