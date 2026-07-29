import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://ecfiler.com";
  const lastModified = new Date();

  return [
    // Public pages
    { url: base, lastModified, changeFrequency: "weekly", priority: 1.0 },
    { url: `${base}/sign-in`, lastModified, changeFrequency: "monthly", priority: 0.5 },
    { url: `${base}/sign-up`, lastModified, changeFrequency: "monthly", priority: 0.7 },

    // Marketing / resources
    { url: `${base}/federal-courts`, lastModified, changeFrequency: "monthly", priority: 0.8 },
    { url: `${base}/what-is-cmecf`, lastModified, changeFrequency: "monthly", priority: 0.8 },

    // Legal
    { url: `${base}/privacy`, lastModified, changeFrequency: "monthly", priority: 0.3 },
    { url: `${base}/terms`, lastModified, changeFrequency: "monthly", priority: 0.3 },

    // Free tools — public, no account
    { url: `${base}/tools`, lastModified, changeFrequency: "monthly", priority: 0.8 },
    { url: `${base}/courts`, lastModified, changeFrequency: "monthly", priority: 0.7 },
    { url: `${base}/events`, lastModified, changeFrequency: "monthly", priority: 0.6 },
    { url: `${base}/fees`, lastModified, changeFrequency: "monthly", priority: 0.6 },
    { url: `${base}/redaction`, lastModified, changeFrequency: "monthly", priority: 0.6 },
    { url: `${base}/validate`, lastModified, changeFrequency: "monthly", priority: 0.6 },
    { url: `${base}/certificate`, lastModified, changeFrequency: "monthly", priority: 0.6 },

    // App pages (require auth)
    { url: `${base}/file`, lastModified, changeFrequency: "weekly", priority: 0.9 },
    { url: `${base}/history`, lastModified, changeFrequency: "weekly", priority: 0.5 },
    { url: `${base}/drafts`, lastModified, changeFrequency: "weekly", priority: 0.4 },
    { url: `${base}/settings`, lastModified, changeFrequency: "monthly", priority: 0.4 },
  ];
}
