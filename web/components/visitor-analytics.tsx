"use client";

import Script from "next/script";
import { usePathname } from "next/navigation";

// Self-hosted Umami (no cookies), disclosed in /privacy section 6.
// Public pages only: the signed-in workspace and the Clerk auth pages are
// never counted. The script is not loaded when a visit starts on one of
// them, and once loaded (after a public page) the before-send hook drops
// any hit for them, since client-side navigation keeps the script running.
const PRIVATE_PREFIXES = [
  "/file",
  "/drafts",
  "/history",
  "/onboarding",
  "/settings",
  "/sign-in",
  "/sign-up",
];

export function isPublicPath(path: string): boolean {
  return !PRIVATE_PREFIXES.some((p) => path === p || path.startsWith(`${p}/`));
}

const BEFORE_SEND = "ecfilerUmamiBeforeSend";

if (typeof window !== "undefined") {
  (window as unknown as Record<string, unknown>)[BEFORE_SEND] = (
    _type: string,
    payload: { url?: string },
  ) => (isPublicPath(window.location.pathname) ? payload : false);
}

export function VisitorAnalytics() {
  const pathname = usePathname() ?? "/";
  if (!isPublicPath(pathname)) return null;
  return (
    <Script
      src="https://a.unpossible.studio/a/sgj.js"
      data-website-id="f08b9f66-5415-42c2-9049-c86fd32647ea"
      data-host-url="https://a.unpossible.studio/a"
      data-before-send={BEFORE_SEND}
      strategy="afterInteractive"
    />
  );
}
