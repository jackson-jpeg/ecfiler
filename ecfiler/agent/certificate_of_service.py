"""Automatic Certificate of Service generation.

Every filing in federal court needs a certificate of service stating
how/when the document was served on other parties. CM/ECF generates
a Notice of Electronic Filing (NEF) that serves as electronic service,
but the certificate still needs to be part of the filed document.

This module generates a properly formatted certificate based on:
- Case parties from PACER lookup
- The CM/ECF NEF service list
- Local court rules for the specific court
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from ecfiler.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ServiceRecipient:
    """A party/attorney to be listed on the certificate of service."""

    name: str
    role: str  # plaintiff, defendant, etc.
    attorney_name: str = ""
    attorney_firm: str = ""
    method: str = "CM/ECF"  # CM/ECF, email, mail, hand delivery
    email: str = ""
    address: str = ""


@dataclass
class CertificateOfService:
    """A generated certificate of service."""

    text: str
    filing_date: str
    method: str
    recipients: list[ServiceRecipient]
    attorney_name: str
    is_all_ecf: bool  # True if all parties are CM/ECF registered


def generate_certificate(
    recipients: list[ServiceRecipient],
    attorney_name: str,
    filing_date: date | None = None,
    case_number: str = "",
    court_name: str = "",
) -> CertificateOfService:
    """Generate a certificate of service.

    Args:
        recipients: Parties to be served
        attorney_name: Name of the filing attorney
        filing_date: Date of filing (default: today)
        case_number: Case number for the header
        court_name: Court name for the header

    Returns:
        CertificateOfService with the full text
    """
    if filing_date is None:
        filing_date = date.today()

    date_str = filing_date.strftime("%B %d, %Y")
    is_all_ecf = all(r.method == "CM/ECF" for r in recipients)

    lines: list[str] = []

    # Header
    lines.append("CERTIFICATE OF SERVICE")
    lines.append("")

    # Body — standard language
    if is_all_ecf:
        lines.append(
            f"I hereby certify that on {date_str}, I electronically filed "
            f"the foregoing document with the Clerk of Court using the CM/ECF "
            f"system, which will send a Notice of Electronic Filing to all "
            f"counsel of record who are registered CM/ECF users."
        )
    else:
        ecf_recipients = [r for r in recipients if r.method == "CM/ECF"]
        other_recipients = [r for r in recipients if r.method != "CM/ECF"]

        lines.append(
            f"I hereby certify that on {date_str}, I electronically filed "
            f"the foregoing document with the Clerk of Court using the CM/ECF "
            f"system, which will send a Notice of Electronic Filing to the "
            f"following registered CM/ECF users:"
        )
        lines.append("")

        for r in ecf_recipients:
            name = r.attorney_name or r.name
            firm = f", {r.attorney_firm}" if r.attorney_firm else ""
            lines.append(f"    {name}{firm}")

        if other_recipients:
            lines.append("")
            lines.append(
                "I further certify that I have served the foregoing document "
                "on the following by the method indicated:"
            )
            lines.append("")

            for r in other_recipients:
                name = r.attorney_name or r.name
                firm = f", {r.attorney_firm}" if r.attorney_firm else ""
                method_desc = _method_description(r)
                lines.append(f"    {name}{firm}")
                lines.append(f"    {method_desc}")
                lines.append("")

    # Signature block
    lines.append("")
    lines.append(f"    /s/ {attorney_name}")
    lines.append(f"    {attorney_name}")

    text = "\n".join(lines)

    logger.info(
        "Generated certificate of service: %d recipients, all_ecf=%s",
        len(recipients),
        is_all_ecf,
    )

    return CertificateOfService(
        text=text,
        filing_date=date_str,
        method="CM/ECF" if is_all_ecf else "mixed",
        recipients=recipients,
        attorney_name=attorney_name,
        is_all_ecf=is_all_ecf,
    )


def generate_certificate_pdf(
    certificate: CertificateOfService,
    output_path: str,
    case_number: str = "",
    court_name: str = "",
) -> str:
    """Generate the certificate of service as a PDF.

    Args:
        certificate: The certificate to render
        output_path: Where to save the PDF
        case_number: Case number for the header
        court_name: Court name for the header

    Returns:
        Path to the generated PDF
    """
    import fitz

    doc = fitz.open()
    page = doc.new_page(width=612, height=792)  # Letter size

    # Margins
    x_margin = 72  # 1 inch
    y = 72
    width = 612 - 2 * x_margin

    # Court/case header (if provided)
    if court_name:
        rect = fitz.Rect(x_margin, y, x_margin + width, y + 14)
        page.insert_textbox(rect, court_name, fontsize=10, align=fitz.TEXT_ALIGN_CENTER)
        y += 18

    if case_number:
        rect = fitz.Rect(x_margin, y, x_margin + width, y + 14)
        page.insert_textbox(rect, f"Case No. {case_number}", fontsize=10, align=fitz.TEXT_ALIGN_CENTER)
        y += 28

    # Certificate title
    rect = fitz.Rect(x_margin, y, x_margin + width, y + 16)
    page.insert_textbox(rect, "CERTIFICATE OF SERVICE", fontsize=12, align=fitz.TEXT_ALIGN_CENTER)
    y += 30

    # Body text — wrap at width
    for line in certificate.text.split("\n"):
        if line.strip() == "CERTIFICATE OF SERVICE":
            continue  # Already rendered as title
        if not line.strip():
            y += 12
            continue

        rect = fitz.Rect(x_margin, y, x_margin + width, y + 200)
        text_length = page.insert_textbox(rect, line.strip(), fontsize=11, align=fitz.TEXT_ALIGN_LEFT)
        # Estimate how many lines the text took
        estimated_lines = max(1, len(line.strip()) // 75 + 1)
        y += estimated_lines * 14

        if y > 720:
            page = doc.new_page(width=612, height=792)
            y = 72

    doc.save(output_path)
    doc.close()

    logger.info("Certificate of service PDF saved: %s", output_path)
    return output_path


def _method_description(recipient: ServiceRecipient) -> str:
    """Describe the service method for a recipient."""
    match recipient.method:
        case "email":
            return f"Via email to: {recipient.email}"
        case "mail":
            return f"Via first-class U.S. mail to:\n        {recipient.address}"
        case "hand":
            return "Via hand delivery"
        case "overnight":
            return f"Via overnight delivery to:\n        {recipient.address}"
        case _:
            return f"Via {recipient.method}"
