import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = "https://ecfiler.com";
  return [
    { url: base, lastModified: new Date(), changeFrequency: "weekly", priority: 1.0 },
    { url: `${base}/file`, lastModified: new Date(), changeFrequency: "weekly", priority: 0.9 },
    { url: `${base}/courts`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.8 },
    { url: `${base}/validate`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.7 },
    { url: `${base}/certificate`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.7 },
    { url: `${base}/what-is-cmecf`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.8 },
    { url: `${base}/federal-courts`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.8 },
  ];
}
