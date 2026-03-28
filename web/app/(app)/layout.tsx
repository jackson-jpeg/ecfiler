import type { Metadata } from "next";
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { ToastProvider } from "@/components/toast";

export const metadata: Metadata = {
  title: {
    template: "%s | ECFiler",
    default: "ECFiler — Federal Court Filing",
  },
};

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const { userId } = await auth();
  if (!userId) redirect("/sign-in");
  return <ToastProvider>{children}</ToastProvider>;
}
