// Health of what www.ecfiler.com actually serves.
//
// With no BACKEND_URL (production since session 7) the site is frontend-only:
// this answers 200 with workspace "offline", which is the truth, instead of
// the 502 the old proxy returned. With BACKEND_URL set it also checks the
// backend and answers 503 if the backend is down, so a restored API that
// dies is visible here.

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(): Promise<Response> {
  const commit = process.env.VERCEL_GIT_COMMIT_SHA || "dev";
  const backend = process.env.BACKEND_URL || "";
  const body: Record<string, unknown> = {
    status: "ok",
    service: "ecfiler-web",
    commit,
    workspace: backend ? "online" : "offline",
  };
  let status = 200;

  if (backend) {
    const r = await fetch(`${backend}/api/health`, { signal: AbortSignal.timeout(5_000) }).catch(() => null);
    body.backend = r?.ok ? "ok" : "down";
    if (!r?.ok) {
      body.status = "degraded";
      status = 503;
    }
  }

  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}
