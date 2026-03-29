"use client";

import { usePathname } from "next/navigation";
import { Sidebar } from "@/components/sidebar";

/**
 * App shell that conditionally renders the sidebar.
 *
 * The filing workspace (/file) and onboarding (/onboarding) use their own
 * full-width layouts with custom headers. All other app pages get the sidebar.
 */
const FULL_WIDTH_ROUTES = ["/file", "/onboarding"];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const showSidebar = !FULL_WIDTH_ROUTES.includes(pathname);

  if (!showSidebar) {
    return <>{children}</>;
  }

  return (
    <div className="flex h-screen overflow-hidden has-sidebar">
      <div className="hidden lg:block">
        <Sidebar />
      </div>
      <main className="flex-1 overflow-y-auto">{children}</main>
    </div>
  );
}
