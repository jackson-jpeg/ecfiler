"""Output formatting for ECFiler."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ecfiler.filing.models import Filing, FilingReceipt


def display_filing_summary(console: Console, filing: Filing) -> None:
    """Display a filing summary table."""
    table = Table(show_header=False, border_style="dim", title="Filing Summary")
    table.add_column("Field", style="bold", width=14)
    table.add_column("Value")

    table.add_row("Court", f"{filing.court_id} ({filing.court_type.value})")
    table.add_row("Case", filing.case.case_number)
    if filing.case.title:
        table.add_row("Title", filing.case.title)
    table.add_row("Event", f"{filing.event.description} ({filing.event.code})")

    for doc in filing.documents:
        label = "Document" if doc.is_main else "Attachment"
        status = "[green]✓[/green]" if doc.is_valid else "[red]✗[/red]"
        size = f"{doc.validation.file_size_mb:.1f}MB" if doc.validation else "?"
        table.add_row(label, f"{status} {doc.filename} ({size})")

    if filing.related_entry:
        table.add_row(
            "Related",
            f"Docket #{filing.related_entry.docket_number}",
        )

    console.print(table)


def display_receipt(console: Console, receipt: FilingReceipt) -> None:
    """Display a filing receipt."""
    console.print(
        Panel(
            f"[bold green]✅ FILED SUCCESSFULLY[/bold green]\n\n"
            f"  Court:    {receipt.court_id}\n"
            f"  Case:     {receipt.case_number}\n"
            f"  Docket #: {receipt.docket_number or 'pending'}\n"
            f"  Event:    {receipt.event_description}\n"
            f"  Time:     {receipt.filed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"  Receipt:  {receipt.receipt_path}",
            border_style="green",
            title="Filing Confirmation",
        )
    )


def display_court_list(console: Console, courts: list[dict[str, str]]) -> None:
    """Display a table of courts."""
    table = Table(title=f"Courts ({len(courts)})")
    table.add_column("#", style="bold", width=4)
    table.add_column("ID", width=8)
    table.add_column("Name")
    table.add_column("Type", width=12)

    for i, court in enumerate(courts, 1):
        table.add_row(
            str(i),
            court["court_id"],
            court["name"],
            court.get("type", "district"),
        )

    console.print(table)
