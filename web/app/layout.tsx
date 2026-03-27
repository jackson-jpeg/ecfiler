import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";

export const metadata: Metadata = {
  title: "ECFiler",
  description: "Federal CM/ECF court filing",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <head>
          <link
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
            rel="stylesheet"
          />
        </head>
        <body className="bg-zinc-50 text-zinc-900">
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
