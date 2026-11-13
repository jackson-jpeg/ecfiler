// Is the signed-in filing workspace backed by a running API?
//
// Baked at build time from BACKEND_URL (see next.config.ts). Session 7
// (2026-11-13): the API was retired from the VPS on 2026-09-24 and is not
// coming back until ECFiler has a real signup or paying user to serve, so
// production builds with no BACKEND_URL and every surface that needs the API
// says so plainly instead of failing. Restoring the API is one env var:
// set BACKEND_URL in the Vercel project and redeploy.

export const WORKSPACE_ONLINE = process.env.NEXT_PUBLIC_WORKSPACE_ONLINE === "1";

/** One sentence, reused wherever the workspace would otherwise be offered. */
export const WORKSPACE_OFFLINE_NOTE =
  "The signed-in filing workspace (AI analysis, staging, drafts and history) is closed while ECFiler finishes testing against a court system. The free tools work now.";
