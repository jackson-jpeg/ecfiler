const API = process.env.NEXT_PUBLIC_API_URL || "";

/**
 * Get the Clerk user ID from the cookie or return empty string.
 * This is used to scope all API calls to the authenticated user.
 */
function getUserId(): string {
  if (typeof window === "undefined") return "";
  // Clerk stores the user session — we read the user ID that was
  // set by our auth wrapper on the client side.
  return window.__ecfiler_user_id || "";
}

/** Set the user ID for API calls (called once from layout/auth wrapper). */
export function setUserId(id: string) {
  if (typeof window !== "undefined") {
    window.__ecfiler_user_id = id;
  }
}

/** Set the Clerk session token for API calls. */
export function setSessionToken(token: string) {
  if (typeof window !== "undefined") {
    window.__ecfiler_session_token = token;
  }
}

// Extend Window for the user ID and session token
declare global {
  interface Window {
    __ecfiler_user_id?: string;
    __ecfiler_session_token?: string;
  }
}

/** Standard headers including auth token and user isolation. */
function authHeaders(extra?: Record<string, string>): Record<string, string> {
  const headers: Record<string, string> = { "X-User-Id": getUserId(), ...extra };
  const token = typeof window !== "undefined" ? window.__ecfiler_session_token : undefined;
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

/** Fetch with timeout support. Throws on timeout or non-ok response. */
async function fetchWithTimeout(
  url: string,
  opts?: RequestInit,
  timeoutMs: number = 30000,
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const resp = await fetch(url, { ...opts, signal: controller.signal });
    return resp;
  } catch (e: unknown) {
    if (e instanceof DOMException && e.name === "AbortError") {
      throw new Error("Request timed out");
    }
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

export interface FilingPreview {
  document_type: string;
  case_number: string;
  court_id: string;
  case_caption: string;
  event_code: string;
  event_description: string;
  filing_party: string;
  attorney_name?: string;
  attorney_firm?: string;
  is_response: boolean;
  responds_to: string | null;
  responds_to_docket?: string;
  pdf_valid: boolean;
  pdf_size_mb: number;
  pdf_pages: number;
  pdf_is_pdfa: boolean;
  redaction_risk: string;
  redaction_issues: number;
  completeness_score: number;
  warnings: string[];
  confidence: string;
  ready: boolean;
  filing_fee?: number;
  filing_fee_text?: string;
  has_certificate_of_service?: boolean;
  has_proposed_order?: boolean;
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

export interface FilingRecord {
  id: number;
  user_id: string;
  court_id: string;
  case_number: string;
  docket_number: string;
  event_description: string;
  status: string;
  filed_at: string;
  confirmation_text: string;
  receipt_path: string;
  pdf_path: string;
  pdf_compressed: number;
  is_sealed: number;
  created_at: string;
}

export async function* streamAnalysis(
  file: File
): AsyncGenerator<{ type: "step"; data: AnalysisStep } | { type: "result"; data: FilingPreview } | { type: "error"; message: string }> {
  const fd = new FormData();
  fd.append("document", file);

  const resp = await fetch(`${API}/api/file/stream`, {
    method: "POST",
    body: fd,
    headers: authHeaders(),
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

      if (event === "step") yield { type: "step", data: parsed };
      if (event === "result") yield { type: "result", data: parsed };
      if (event === "error") yield { type: "error", message: parsed.message };
    }
  }
}

export interface FilingOptions {
  docket_text?: string;
  event_code_override?: string;
  is_sealed?: boolean;
  is_redacted?: boolean;
  include_cos?: boolean;
  exhibits?: { label: string; description: string }[];
}

export async function* streamBrowser(
  filing: FilingPreview,
  options?: FilingOptions,
): AsyncGenerator<{ type: "browser"; data: BrowserStep } | { type: "done"; message: string }> {
  const resp = await fetch(`${API}/api/filing/browser-stream`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      court_id: filing.court_id,
      case_number: filing.case_number,
      event_code: options?.event_code_override || filing.event_code,
      event_description: options?.docket_text || filing.event_description,
      filing_party_name: filing.filing_party?.split("(")[0]?.trim() || "",
      filing_party_role: filing.filing_party?.match(/\((\w+)\)/)?.[1] || "",
      document_path: "",
      dry_run: false,
      is_sealed: options?.is_sealed || false,
      is_redacted: options?.is_redacted || false,
      include_certificate_of_service: options?.include_cos || false,
      exhibits: options?.exhibits || [],
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
  const resp = await fetchWithTimeout(`${API}/api/courts?${params}`);
  if (!resp.ok) throw new Error(await resp.text());
  return resp.json();
}

export async function validatePDF(file: File): Promise<ValidationResult> {
  const fd = new FormData();
  fd.append("document", file);
  const resp = await fetchWithTimeout(`${API}/api/validate`, { method: "POST", body: fd }, 60000);
  if (!resp.ok) throw new Error(await resp.text());
  return resp.json();
}

export async function generateCOS(
  attorney: string,
  caseNumber: string,
  recipients: { name: string; attorney_name: string; method: string }[]
): Promise<{ text: string }> {
  const resp = await fetchWithTimeout(`${API}/api/certificate-of-service`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ attorney_name: attorney, case_number: caseNumber, recipients }),
  });
  if (!resp.ok) throw new Error(await resp.text());
  return resp.json();
}

export interface HistoryResponse {
  items: FilingRecord[];
  total: number;
}

export async function getHistory(): Promise<FilingRecord[]> {
  const resp = await fetchWithTimeout(`${API}/api/history`, { headers: authHeaders() });
  if (!resp.ok) throw new Error(await resp.text());
  const data = await resp.json();
  // Support both old (array) and new ({items, total}) response shapes
  return Array.isArray(data) ? data : data.items;
}

export async function getHistoryWithTotal(): Promise<HistoryResponse> {
  const resp = await fetchWithTimeout(`${API}/api/history`, { headers: authHeaders() });
  if (!resp.ok) throw new Error(await resp.text());
  const data = await resp.json();
  if (Array.isArray(data)) return { items: data, total: data.length };
  return data;
}

export async function getFilingDetail(id: number): Promise<FilingRecord> {
  const resp = await fetchWithTimeout(`${API}/api/history/${id}`, { headers: authHeaders() });
  if (!resp.ok) throw new Error("Filing not found");
  return resp.json();
}

export function getFilingPdfUrl(id: number): string {
  return `${API}/api/history/${id}/pdf`;
}

export async function getDrafts(): Promise<Record<string, unknown>[]> {
  const resp = await fetchWithTimeout(`${API}/api/drafts`, { headers: authHeaders() });
  if (!resp.ok) throw new Error(await resp.text());
  return resp.json();
}
