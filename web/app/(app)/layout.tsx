import type { Metadata } from "next";
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { ToastProvider } from "@/components/toast";
import { CommandPalette } from "@/components/command-palette";
import { UserInit } from "@/components/user-init";
import { AppShell } from "@/components/app-shell";
import { WorkspaceOffline } from "@/components/workspace-offline";
import { WORKSPACE_ONLINE } from "@/lib/workspace";

export const metadata: Metadata = {
  title: {
    template: "%s | ECFiler",
    default: "ECFiler: Federal Court Filing",
  },
};

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  // No backend, no workspace: every page in this group needs the API, so
  // none of them render (and none of them fire API calls) until it is back.
  if (!WORKSPACE_ONLINE) {
    const { userId } = await auth();
    return <WorkspaceOffline signedIn={Boolean(userId)} />;
  }
  const { userId } = await auth();
  if (!userId) redirect("/sign-in");
  return (
    <ToastProvider>
      <UserInit />
      <CommandPalette />
      <AppShell>{children}</AppShell>
    </ToastProvider>
  );
}
