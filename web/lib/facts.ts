/**
 * Single source of truth for public-facing product facts.
 *
 * Every court count, retention period, and price shown anywhere in the web
 * app must come from this module so the marketing copy can never drift from
 * the registry (ecfiler/courts/registry.py) or storage policy
 * (ecfiler/storage/history.py).
 */

/** Total courts in the ECFiler registry. */
export const COURT_COUNT = 207;

/** Registry breakdown: 97 district + 94 bankruptcy + 16 appellate = 207. */
export const COURT_BREAKDOWN = {
  district: 97,
  bankruptcy: 94,
  appellate: 16,
} as const;

/** Days uploaded public documents are kept in original form before compressed archival. */
export const RETENTION_DAYS = 30;

/** Pro tier price, USD per attorney per month. */
export const PRO_PRICE = 99;

/** Canonical service tiers — shared by the landing page pricing section and the Terms of Service. */
export const TIERS = {
  free: {
    name: "Free Tools",
    price: 0,
    features: [
      "PDF validation & PDF/A checks",
      "Rule 5.2 redaction scanning",
      `${COURT_COUNT} federal courts directory`,
      "Filing fee lookup",
      "Certificate of service generator",
      "Event code browser",
    ],
    notIncluded: [
      "AI document analysis",
      "AI docket text generation",
      "AI event code matching",
      "Filing package staging",
    ],
  },
  pro: {
    name: "Pro",
    price: PRO_PRICE,
    features: [
      "Everything in Free",
      "AI document analysis",
      "AI docket text generation",
      "AI event code matching",
      "3-pass AI safety verification",
      "Filing package staging",
      "Guided CM/ECF handoff",
      "Filing history & PDF archive",
      "Team management",
      "Priority support",
    ],
  },
} as const;
