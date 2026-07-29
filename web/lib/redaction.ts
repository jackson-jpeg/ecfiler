// Client-side Rule 5.2 redaction scan — the regex pass.
//
// lib/data/redaction_patterns.json is exported from the Python source of
// truth (ecfiler/pdf/redaction_check.py); tests/test_web_data_parity.py
// fails when the patterns drift. The scan below mirrors
// redaction_check.regex_scan, including the SSN/EIN context-word checks.
// The AI contextual pass (minor names, DOBs in prose) is server-side only.

import patterns from "./data/redaction_patterns.json";

export interface RedactionIssue {
  issue_type: string;
  text: string;
  confidence: "high" | "medium" | "low";
  suggestion: string;
}

export interface RedactionReport {
  issues: RedactionIssue[];
  risk_level: "none" | "low" | "high";
}

interface RawPattern {
  source: string;
  ignoreCase: boolean;
}

function compile(p: RawPattern): RegExp {
  return new RegExp(p.source, p.ignoreCase ? "gi" : "g");
}

const SSN = (patterns.ssn as RawPattern[]).map(compile);
const ACCOUNT = (patterns.account as RawPattern[]).map(compile);
const DOB = (patterns.dob as RawPattern[]).map(compile);
const EIN = (patterns.ein as RawPattern[]).map(compile);
const SSN_CONTEXT: string[] = patterns.ssn_context_words;
const EIN_CONTEXT: string[] = patterns.ein_context_words;

/** Mirror of ecfiler.pdf.redaction_check.regex_scan. */
export function regexScan(text: string): RedactionIssue[] {
  const issues: RedactionIssue[] = [];

  for (const pattern of SSN) {
    for (const match of text.matchAll(pattern)) {
      const matched = match[0];
      // Bare 9-digit runs only count near SSN context words.
      if (matched.length === 9 && !matched.includes("-")) {
        const start = Math.max(0, (match.index ?? 0) - 50);
        const context = text.slice(start, match.index).toLowerCase();
        if (!SSN_CONTEXT.some((w) => context.includes(w))) continue;
      }
      issues.push({
        issue_type: "ssn",
        text: matched,
        confidence: "high",
        suggestion: `Redact to XXX-XX-${matched.slice(-4)}`,
      });
    }
  }

  for (const pattern of ACCOUNT) {
    for (const match of text.matchAll(pattern)) {
      issues.push({
        issue_type: "account_number",
        text: match[0],
        confidence: "high",
        suggestion: "Redact to last 4 digits only",
      });
    }
  }

  for (const pattern of DOB) {
    for (const match of text.matchAll(pattern)) {
      issues.push({
        issue_type: "dob",
        text: match[0],
        confidence: "high",
        suggestion: "Redact to year only",
      });
    }
  }

  for (const pattern of EIN) {
    for (const match of text.matchAll(pattern)) {
      const start = Math.max(0, (match.index ?? 0) - 80);
      const context = text.slice(start, match.index).toLowerCase();
      if (EIN_CONTEXT.some((w) => context.includes(w))) {
        issues.push({
          issue_type: "ssn",
          text: match[0],
          confidence: "medium",
          suggestion: "Redact EIN/Tax ID to last 4 digits",
        });
      }
    }
  }

  return issues;
}

export function scanText(text: string): RedactionReport {
  const issues = regexScan(text);
  const risk_level = issues.some((i) => i.confidence === "high")
    ? "high"
    : issues.length > 0
      ? "low"
      : "none";
  return { issues, risk_level };
}

/** Extract text from a PDF entirely in the browser via pdf.js. */
export async function extractPdfText(file: File): Promise<{ text: string; pages: number }> {
  const pdfjs = await import("pdfjs-dist");
  pdfjs.GlobalWorkerOptions.workerSrc = new URL(
    "pdfjs-dist/build/pdf.worker.min.mjs",
    import.meta.url
  ).toString();
  const doc = await pdfjs.getDocument({ data: await file.arrayBuffer() }).promise;
  const parts: string[] = [];
  for (let i = 1; i <= doc.numPages; i++) {
    const page = await doc.getPage(i);
    const content = await page.getTextContent();
    parts.push(
      content.items
        .map((item) => ("str" in item ? item.str : ""))
        .join(" ")
    );
  }
  return { text: parts.join("\n\n"), pages: doc.numPages };
}
