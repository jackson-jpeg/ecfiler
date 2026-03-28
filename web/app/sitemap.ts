import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://ecfiler.com";
  const lastModified = new Date();

  return [
    { url: base, lastModified, changeFrequency: "weekly", priority: 1.0 },
    { url: `${base}/sign-in`, lastModified, changeFrequency: "monthly", priority: 0.6 },
    { url: `${base}/sign-up`, lastModified, changeFrequency: "monthly", priority: 0.6 },
    { url: `${base}/courts`, lastModified, changeFrequency: "monthly", priority: 0.8 },
    { url: `${base}/what-is-cmecf`, lastModified, changeFrequency: "monthly", priority: 0.8 },
    { url: `${base}/federal-courts`, lastModified, changeFrequency: "monthly", priority: 0.8 },
  ];
}
