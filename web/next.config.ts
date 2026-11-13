import type { NextConfig } from "next";

// All browser API calls are relative (/api/*). When BACKEND_URL is set they
// are proxied server-side to the backend, so the client needs no CORS and no
// absolute API origin. When it is unset (production since session 7) there
// is no proxy at all: the only /api/* routes are the route handlers in
// web/app/api/ (waitlist, health), and anything else is a plain 404 rather
// than a 502 from a backend that is not there. See web/lib/workspace.ts.
const API = process.env.BACKEND_URL || "";

const nextConfig: NextConfig = {
  // Build-time public configuration. These are deliberately in-config rather
  // than in a committed .env file: everything here is public by design (the
  // Clerk key is the *publishable* key), and the repo's pre-commit hook
  // rightly refuses .env files.
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "",
    NEXT_PUBLIC_WORKSPACE_ONLINE: API ? "1" : "",
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY:
      process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ??
      "pk_live_Y2xlcmsuZWNmaWxlci5jb20k",
    NEXT_PUBLIC_CLERK_SIGN_IN_URL: "/sign-in",
    NEXT_PUBLIC_CLERK_SIGN_UP_URL: "/sign-up",
    NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL: "/file",
    NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL: "/onboarding",
  },
  async rewrites() {
    if (!API) return [];
    return [
      {
        source: "/api/:path*",
        destination: `${API}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
