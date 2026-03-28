import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import { Analytics } from "@vercel/analytics/react";
import { SpeedInsights } from "@vercel/speed-insights/next";
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
          <Analytics />
          <SpeedInsights />
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{
              __html: JSON.stringify({
                "@context": "https://schema.org",
                "@type": "SoftwareApplication",
                "name": "ECFiler",
                "applicationCategory": "LegalService",
                "operatingSystem": "Web",
                "description": "AI-powered tool for filing documents on federal CM/ECF court systems. Supports all 207 federal courts.",
                "url": "https://ecfiler.com",
                "offers": [
                  { "@type": "Offer", "price": "0", "priceCurrency": "USD", "description": "Free tier" },
                  { "@type": "Offer", "price": "99", "priceCurrency": "USD", "description": "Pro tier per attorney per month" },
                ],
                "featureList": [
                  "AI document analysis",
                  "207 federal courts",
                  "Event code matching",
                  "Rule 5.2 redaction scanning",
                  "PDF validation",
                  "Filing fee lookup",
                  "Certificate of service generation",
                ],
              }),
            }}
          />
        </body>
      </html>
    </ClerkProvider>
  );
}
