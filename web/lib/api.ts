const API = process.env.NEXT_PUBLIC_API_URL || "";

export interface FilingPreview {
  document_type: string;
  case_number: string;
  court_id: string;
  case_caption: string;
  event_code: string;
  event_description: string;
  filing_party: string;
  is_response: boolean;
  responds_to: string | null;
  pdf_valid: boolean;
  pdf_size_mb: number;
  pdf_pages: number;
  redaction_risk: string;
  redaction_issues: number;
  completeness_score: number;
  warnings: string[];
  confidence: string;
  ready: boolean;
  filing_fee?: number;
  filing_fee_text?: string;
}

export interface AnalysisStep {
  id: number;
  label: string;
  status: "running" | "done" | "warn" | "error";
  detail?: string;
}

export interface BrowserStep {
  step: string;
  status: "running" | "done";
  description: string;
  screenshot?: string;
}

export interface Court {
  court_id: string;
  name: string;
  court_type: "district" | "bankruptcy" | "appellate";
}

export interface ValidationResult {
  valid: boolean;
  file_size_mb: number;
  page_count: number;
  has_text: boolean;
  is_encrypted: boolean;
  errors: string[];
  warnings: string[];
}

export async function* streamAnalysis(
  file: File
): AsyncGenerator<{ type: "step"; data: AnalysisStep } | { type: "result"; data: FilingPreview } | { type: "error"; message: string }> {
  const fd = new FormData();
  fd.append("document", file);

  const resp = await fetch(`${API}/api/file/stream`, { method: "POST", body: fd });
  if (!resp.ok) throw new Error(await resp.text());

  const reader = resp.body!.getReader();
  const dec = new TextDecoder();
  let buf = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const parts = buf.split("\n\n");
    buf = parts.pop() || "";

    for (const part of parts) {
      const lines = part.split("\n");
      let event = "", data = "";
      for (const l of lines) {
        if (l.startsWith("event:")) event = l.slice(6).trim();
        if (l.startsWith("data:")) data = l.slice(5).trim();
      }
      if (!data) continue;
      const parsed = JSON.parse(data);

      if (event === "step") yield { type: "step", data: parsed };
      if (event === "result") yield { type: "result", data: parsed };
      if (event === "error") yield { type: "error", message: parsed.message };
    }
  }
}

export async function* streamBrowser(
  filing: FilingPreview
): AsyncGenerator<{ type: "browser"; data: BrowserStep } | { type: "done"; message: string }> {
  const resp = await fetch(`${API}/api/filing/browser-stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      court_id: filing.court_id,
      case_number: filing.case_number,
      event_code: filing.event_code,
      event_description: filing.event_description,
      filing_party_name: filing.filing_party?.split("(")[0]?.trim() || "",
      filing_party_role: filing.filing_party?.match(/\((\w+)\)/)?.[1] || "",
      document_path: "",
      dry_run: false,
    }),
  });
  if (!resp.ok) throw new Error(await resp.text());

  const reader = resp.body!.getReader();
  const dec = new TextDecoder();
  let buf = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const parts = buf.split("\n\n");
    buf = parts.pop() || "";

    for (const part of parts) {
      const lines = part.split("\n");
      let event = "", data = "";
      for (const l of lines) {
        if (l.startsWith("event:")) event = l.slice(6).trim();
        if (l.startsWith("data:")) data = l.slice(5).trim();
      }
      if (!data) continue;
      const parsed = JSON.parse(data);

      if (event === "browser") yield { type: "browser", data: parsed };
      if (event === "browser_done") yield { type: "done", message: parsed.message };
    }
  }
}

export async function searchCourts(query?: string, type?: string): Promise<Court[]> {
  const params = new URLSearchParams();
  if (query) params.set("search", query);
  if (type) params.set("court_type", type);
  const resp = await fetch(`${API}/api/courts?${params}`);
  return resp.json();
}

export async function validatePDF(file: File): Promise<ValidationResult> {
  const fd = new FormData();
  fd.append("document", file);
  const resp = await fetch(`${API}/api/validate`, { method: "POST", body: fd });
  return resp.json();
}

export async function generateCOS(
  attorney: string,
  caseNumber: string,
  recipients: { name: string; attorney_name: string; method: string }[]
): Promise<{ text: string }> {
  const resp = await fetch(`${API}/api/certificate-of-service`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ attorney_name: attorney, case_number: caseNumber, recipients }),
  });
  return resp.json();
}

export async function getHistory(): Promise<Record<string, unknown>[]> {
  const resp = await fetch(`${API}/api/history`);
  return resp.json();
}

export async function getDrafts(): Promise<Record<string, unknown>[]> {
  const resp = await fetch(`${API}/api/drafts`);
  return resp.json();
}
