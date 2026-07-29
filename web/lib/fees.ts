// Client-side federal filing fee lookup.
//
// lib/data/fees.json is an exact export of the Python source of truth
// (ecfiler/filing/fees.py — 28 U.S.C. § 1914 and the Judicial Conference
// fee schedule effective December 2024); tests/test_web_data_parity.py
// fails when they drift. The lookup logic below mirrors fees.get_fee so
// the static site answers exactly like the API's /api/fee endpoint.

import feesData from "./data/fees.json";

export interface FilingFee {
  amount: number;
  description: string;
  waivable: boolean;
  notes: string;
}

export type CourtType = "district" | "bankruptcy" | "appellate";

const FEES = feesData as Record<CourtType, Record<string, FilingFee>>;

export function feeTable(courtType: CourtType): [string, FilingFee][] {
  return Object.entries(FEES[courtType]).sort(
    (a, b) => b[1].amount - a[1].amount || a[0].localeCompare(b[0])
  );
}

/** Mirror of ecfiler.filing.fees.get_fee — keep the branch order identical. */
export function getFee(eventDescription: string, courtType: CourtType): FilingFee | null {
  const desc = eventDescription.toLowerCase();
  let fees: Record<string, FilingFee>;

  if (courtType === "bankruptcy") {
    fees = FEES.bankruptcy;
    if (desc.includes("chapter 7") || desc.includes("voluntary petition")) return fees.chapter7 ?? null;
    if (desc.includes("chapter 11")) {
      if (desc.includes("subchapter v") || desc.includes("sub v")) return fees.chapter11_sub5 ?? null;
      return fees.chapter11 ?? null;
    }
    if (desc.includes("chapter 12")) return fees.chapter12 ?? null;
    if (desc.includes("chapter 13")) return fees.chapter13 ?? null;
    if (desc.includes("adversary")) return fees.adversary ?? null;
  } else if (courtType === "appellate") {
    fees = FEES.appellate;
    if (desc.includes("petition for review")) return fees.petition_review ?? null;
    if (desc.includes("petition") && desc.includes("permission")) return fees.petition_permission ?? null;
    if (desc.includes("rehearing")) return fees.petition_rehearing ?? null;
  } else {
    fees = FEES.district;
  }

  const noFee: FilingFee = { amount: 0, description: "No fee", waivable: true, notes: "" };
  if (desc.includes("answer")) return fees.answer ?? noFee;
  if (desc.includes("response") || desc.includes("opposition")) return fees.response ?? noFee;
  if (desc.includes("reply")) return fees.reply ?? noFee;
  if (desc.includes("stipulation")) return fees.stipulation ?? noFee;
  if (desc.includes("brief") || desc.includes("memorandum")) return fees.brief ?? noFee;
  if (desc.includes("reopen")) return fees.motion_reopen ?? null;
  if (desc.includes("appeal")) return fees.appeal ?? null;
  if (desc.includes("removal")) return fees.removal ?? FEES.district.removal;
  if (desc.includes("complaint") || (desc.includes("petition") && courtType === "district"))
    return fees.complaint ?? FEES.district.complaint;
  if (desc.includes("motion")) return fees.motion ?? noFee;
  if (desc.includes("notice")) return fees.notice ?? noFee;

  return null;
}

/** Mirror of ecfiler.filing.fees.format_fee. */
export function formatFee(fee: FilingFee): string {
  if (fee.amount === 0) return "No filing fee";
  let text = `$${fee.amount.toFixed(2)} — ${fee.description}`;
  if (fee.notes) text += ` (${fee.notes})`;
  if (fee.waivable) text += " [IFP waiver available]";
  return text;
}
