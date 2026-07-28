import type { NextConfig } from "next";

// All browser API calls are relative (/api/*) and proxied server-side to the
// backend, so the client needs no CORS and no absolute API origin.
const API = process.env.BACKEND_URL || "https://api.ecfiler.com";

const nextConfig: NextConfig = {
  // Build-time public configuration. These are deliberately in-config rather
  // than in a committed .env file: everything here is public by design (the
  // Clerk key is the *publishable* key), and the repo's pre-commit hook
  // rightly refuses .env files.
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "",
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY:
      process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ??
      "pk_live_Y2xlcmsuZWNmaWxlci5jb20k",
    NEXT_PUBLIC_CLERK_SIGN_IN_URL: "/sign-in",
    NEXT_PUBLIC_CLERK_SIGN_UP_URL: "/sign-up",
    NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL: "/file",
    NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL: "/onboarding",
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${API}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
