// Client-side Certificate of Service generation.
// Mirrors ecfiler/agent/certificate_of_service.py — the certificate is pure
// string formatting, so the free tool runs entirely in the browser.

export interface ServiceRecipient {
  name: string;
  attorney_name: string;
  method: string; // CM/ECF, email, mail, hand, overnight
  attorney_firm?: string;
  email?: string;
  address?: string;
}

export interface GeneratedCertificate {
  text: string;
  filing_date: string;
  method: string;
  is_all_ecf: boolean;
}

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

function methodDescription(r: ServiceRecipient): string {
  switch (r.method) {
    case "email":
      return `Via email to: ${r.email ?? ""}`;
    case "mail":
      return `Via first-class U.S. mail to:\n        ${r.address ?? ""}`;
    case "hand":
      return "Via hand delivery";
    case "overnight":
      return `Via overnight delivery to:\n        ${r.address ?? ""}`;
    default:
      return `Via ${r.method}`;
  }
}

export function generateCertificate(
  recipients: ServiceRecipient[],
  attorneyName: string
): GeneratedCertificate {
  const now = new Date();
  const dateStr = `${MONTHS[now.getMonth()]} ${String(now.getDate()).padStart(2, "0")}, ${now.getFullYear()}`;
  const isAllEcf = recipients.every((r) => r.method === "CM/ECF");

  const lines: string[] = ["CERTIFICATE OF SERVICE", ""];

  if (isAllEcf) {
    lines.push(
      `I hereby certify that on ${dateStr}, I electronically filed ` +
        `the foregoing document with the Clerk of Court using the CM/ECF ` +
        `system, which will send a Notice of Electronic Filing to all ` +
        `counsel of record who are registered CM/ECF users.`
    );
  } else {
    const ecfRecipients = recipients.filter((r) => r.method === "CM/ECF");
    const otherRecipients = recipients.filter((r) => r.method !== "CM/ECF");

    lines.push(
      `I hereby certify that on ${dateStr}, I electronically filed ` +
        `the foregoing document with the Clerk of Court using the CM/ECF ` +
        `system, which will send a Notice of Electronic Filing to the ` +
        `following registered CM/ECF users:`
    );
    lines.push("");

    for (const r of ecfRecipients) {
      const name = r.attorney_name || r.name;
      const firm = r.attorney_firm ? `, ${r.attorney_firm}` : "";
      lines.push(`    ${name}${firm}`);
    }

    if (otherRecipients.length > 0) {
      lines.push("");
      lines.push(
        "I further certify that I have served the foregoing document " +
          "on the following by the method indicated:"
      );
      lines.push("");

      for (const r of otherRecipients) {
        const name = r.attorney_name || r.name;
        const firm = r.attorney_firm ? `, ${r.attorney_firm}` : "";
        lines.push(`    ${name}${firm}`);
        lines.push(`    ${methodDescription(r)}`);
        lines.push("");
      }
    }
  }

  lines.push("");
  lines.push(`    /s/ ${attorneyName}`);
  lines.push(`    ${attorneyName}`);

  return {
    text: lines.join("\n"),
    filing_date: dateStr,
    method: isAllEcf ? "CM/ECF" : "mixed",
    is_all_ecf: isAllEcf,
  };
}
