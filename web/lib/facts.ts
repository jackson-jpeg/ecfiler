/**
 * Single source of truth for public-facing product facts.
 *
 * Every court count, retention period, and price shown anywhere in the web
 * app must come from this module so the marketing copy can never drift from
 * the registry (ecfiler/courts/registry.py) or storage policy
 * (ecfiler/storage/history.py).
 */

/**
 * Total courts in the ECFiler registry.
 *
 * Pinned to the shipped data (lib/data/*.json) by
 * tests/test_web_data_parity.py::test_facts_constants_match_data — if the
 * registry changes, that test forces this constant to move with it.
 */
export const COURT_COUNT = 207;

/**
 * Registry breakdown: 97 district-type + 94 bankruptcy + 16 appellate = 207.
 * "District-type" includes the four territorial courts and three national
 * courts (JPML, Court of International Trade, Court of Federal Claims);
 * "appellate" is 13 courts of appeals + 3 bankruptcy appellate panels.
 * Same parity test as COURT_COUNT.
 */
export const COURT_BREAKDOWN = {
  district: 97,
  bankruptcy: 94,
  appellate: 16,
} as const;

/** "Last updated" line shown on the Privacy Policy and Terms of Service. */
export const LEGAL_LAST_UPDATED = "July 2026";

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
      "5-point readiness check",
      "Filing package staging",
      "Guided CM/ECF handoff",
      "Filing history & PDF archive",
      "Team management",
      "Priority support",
    ],
  },
} as const;
