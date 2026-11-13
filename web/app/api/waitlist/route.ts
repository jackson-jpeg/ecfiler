// Pro waitlist signup, with no backend: each signup is emailed to the
// operator through Resend and stored nowhere else.
//
// Session 7 (2026-11-13). Before this, the form POSTed to /api/waitlist on a
// backend that had been unreachable since July, and the client marked the
// signup "done" whenever fetch() resolved, so every signup since then was
// acknowledged and lost. This handler answers 200 only after Resend has
// accepted the message; the client shows success only on a 200.
//
// Env (Vercel project `ecfiler`, production):
//   RESEND_API_KEY      sending-only key scoped to the ecfiler.com domain
//   WAITLIST_NOTIFY_TO  the inbox that receives signups (kept out of the repo)

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const FROM = "ECFiler Waitlist <waitlist@ecfiler.com>";
// Deliberately simple: one @, a dot in the domain, no spaces. Resend and the
// receiving inbox are the real validators.
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function json(status: number, body: Record<string, unknown>): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}

export async function POST(request: Request): Promise<Response> {
  let payload: { email?: unknown; website?: unknown };
  try {
    payload = await request.json();
  } catch {
    return json(400, { error: "Send a JSON body with an email field." });
  }

  // Honeypot: the form renders a hidden "website" field that people never
  // fill. Answer as if it worked so a bot learns nothing.
  if (typeof payload.website === "string" && payload.website.trim() !== "") {
    return json(200, { ok: true });
  }

  const email = typeof payload.email === "string" ? payload.email.trim() : "";
  if (!email || email.length > 254 || !EMAIL_RE.test(email)) {
    return json(400, { error: "Enter a valid email address." });
  }

  const apiKey = process.env.RESEND_API_KEY;
  const to = process.env.WAITLIST_NOTIFY_TO;
  if (!apiKey || !to) {
    return json(503, { error: "The waitlist is unavailable right now. Please try again later." });
  }

  const when = new Date().toISOString();
  const resp = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from: FROM,
      to: [to],
      reply_to: email,
      subject: `ECFiler waitlist signup: ${email}`,
      text: `New ECFiler Pro waitlist signup.\n\nEmail: ${email}\nReceived: ${when}\nSource: www.ecfiler.com pricing section\n`,
    }),
    signal: AbortSignal.timeout(10_000),
  }).catch(() => null);

  if (!resp || !resp.ok) {
    return json(502, { error: "We could not record your signup. Please try again in a few minutes." });
  }
  return json(200, { ok: true });
}
