import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "What is CM/ECF? Guide to Federal Court Electronic Filing | ECFiler",
  description: "CM/ECF (Case Management/Electronic Case Files) is the federal judiciary's electronic filing system. Learn how it works, who uses it, and how to file.",
};

export default function WhatIsCMECF() {
  return (
    <article className="prose prose-zinc max-w-none">
      <h1 className="text-3xl font-bold tracking-tight mb-2">What is CM/ECF?</h1>
      <p className="text-lg text-zinc-500 mb-8">A complete guide to the federal court electronic filing system.</p>

      <h2>Overview</h2>
      <p>
        CM/ECF (Case Management/Electronic Case Files) is the system used by all federal courts in the United States for electronic document filing. It allows attorneys and authorized parties to file pleadings, motions, briefs, and other documents with the court electronically, rather than in paper form.
      </p>
      <p>
        The system is maintained by the Administrative Office of the U.S. Courts and is used across all 94 federal district courts, 94 bankruptcy courts, and 13 circuit courts of appeals — <strong>207 courts total</strong>.
      </p>

      <h2>How CM/ECF works</h2>
      <p>Filing a document on CM/ECF involves several steps:</p>
      <ol>
        <li><strong>Login</strong> — Authenticate through PACER Central Sign-On (CSO) with your PACER credentials.</li>
        <li><strong>Select the case</strong> — Enter the case number to navigate to the correct case.</li>
        <li><strong>Choose an event code</strong> — Select from hundreds of event codes that categorize your filing (e.g., &quot;Motion to Dismiss,&quot; &quot;Reply Brief,&quot; &quot;Notice of Appearance&quot;).</li>
        <li><strong>Upload your PDF</strong> — Attach the main document and any attachments. Documents must be in PDF format.</li>
        <li><strong>Fill in docket text</strong> — Add or modify the text that will appear on the case docket.</li>
        <li><strong>Submit</strong> — Review and submit. The court generates a Notice of Electronic Filing (NEF) confirming the filing.</li>
      </ol>

      <h2>Who uses CM/ECF?</h2>
      <p>
        CM/ECF is used by attorneys admitted to practice in federal court, pro se litigants (in some courts), court clerks, and judges. To file electronically, you need:
      </p>
      <ul>
        <li>A PACER account with filing credentials</li>
        <li>Bar admission to the specific court</li>
        <li>Documents in PDF format meeting court requirements</li>
      </ul>

      <h2>NextGen CM/ECF</h2>
      <p>
        The federal courts have been migrating to NextGen CM/ECF, which unifies the login system across courts through PACER Central Sign-On. NextGen modernizes the interface and eliminates the need for Java. Most courts have completed the migration as of 2025.
      </p>

      <h2>Common challenges with CM/ECF</h2>
      <ul>
        <li><strong>Event code selection</strong> — Courts have hundreds of event codes. Selecting the wrong one can delay your filing.</li>
        <li><strong>PDF requirements</strong> — Documents must be searchable, under 100MB, not encrypted, and not contain fillable form fields.</li>
        <li><strong>Redaction</strong> — Rule 5.2 requires redacting personal identifiers (SSNs, DOBs, financial accounts).</li>
        <li><strong>Court-specific rules</strong> — Each court may have local rules that affect filing procedures.</li>
        <li><strong>Multi-step process</strong> — Each filing requires navigating multiple pages and forms.</li>
      </ul>

      <h2>Automating CM/ECF filing</h2>
      <p>
        <Link href="/file" className="text-blue-600 font-semibold hover:underline">ECFiler</Link> automates the CM/ECF filing process by reading your document with AI, extracting the case number, court, event code, and filing party, then preparing the entire filing for one-click confirmation. It supports all 207 federal courts.
      </p>

      <div className="bg-zinc-50 border border-zinc-200 rounded-2xl p-6 mt-8 not-prose">
        <h3 className="text-base font-bold mb-2">Try ECFiler</h3>
        <p className="text-sm text-zinc-500 mb-4">Drop a PDF. AI handles the rest. 207 federal courts.</p>
        <Link href="/file" className="px-5 py-2 bg-zinc-900 text-white text-sm font-semibold rounded-lg hover:bg-zinc-800 transition">
          Start Filing &rarr;
        </Link>
      </div>
    </article>
  );
}
