import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";

export const metadata: Metadata = {
  title: "ECFiler — AI-Powered Federal Court Filing",
  description: "Drop a PDF, AI extracts case, court, event code, and party. Review and file on CM/ECF with one click. 207 federal courts supported.",
  keywords: ["CM/ECF", "federal court filing", "PACER", "e-filing", "legal tech", "court automation"],
  openGraph: {
    title: "ECFiler — The Intelligent Way to File on CM/ECF",
    description: "Drop a PDF, AI extracts everything. Review what CM/ECF will receive. Confirm with one click. 207 federal courts.",
    url: "https://ecfiler.com",
    siteName: "ECFiler",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "ECFiler — AI-Powered Federal Court Filing",
    description: "Drop a PDF, AI extracts everything. File on CM/ECF with one click. 207 federal courts.",
  },
  metadataBase: new URL("https://ecfiler.com"),
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
        <body className="bg-[#fafaf8] text-[#1a1a1a]">
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
