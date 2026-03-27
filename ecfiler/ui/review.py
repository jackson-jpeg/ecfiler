"""Filing review screen — the critical attorney approval gate."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from ecfiler.filing.models import Filing


def show_review_screen(console: Console, filing: Filing, dry_run: bool = False) -> bool:
    """Display the filing review screen and get attorney confirmation.

    This is Safety Gate 5 — the attorney must type CONFIRM to proceed.

    Args:
        console: Rich console
        filing: The filing to review
        dry_run: Whether this is a dry run

    Returns:
        True if attorney confirmed, False otherwise
    """
    console.print()
    console.print(
        Panel(
            "[bold red]⚠️  FILING REVIEW — ATTORNEY APPROVAL REQUIRED[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
    )

    # Filing details table
    table = Table(show_header=False, border_style="bright_black", padding=(0, 2))
    table.add_column("Field", style="bold cyan", width=14)
    table.add_column("Value")

    table.add_row("Court", f"{filing.court_id} ({filing.court_type.value})")
    table.add_row("Case", filing.case.case_number)
    if filing.case.title:
        table.add_row("Case Title", filing.case.title)
    if filing.case.judge:
        table.add_row("Judge", filing.case.judge)

    table.add_row("Event", f"{filing.event.description}")
    table.add_row("Event Code", filing.event.code)

    console.print(table)

    # Documents section
    console.print("\n  [bold]Documents:[/bold]")
    for doc in filing.documents:
        is_main = "[bold]MAIN[/bold]" if doc.is_main else "attachment"
        if doc.validation:
            status = "[green]✓ valid[/green]" if doc.is_valid else "[red]✗ invalid[/red]"
            details = f"{doc.validation.file_size_mb:.1f}MB, {doc.validation.page_count} pages"
        else:
            status = "[yellow]? unchecked[/yellow]"
            details = ""

        console.print(f"    {status} {doc.filename} ({is_main}) {details}")

    # Related entry
    if filing.related_entry:
        console.print(
            f"\n  [bold]Related to:[/bold] Docket #{filing.related_entry.docket_number}"
            f" {filing.related_entry.description}"
        )

    # Redaction issues
    if filing.redaction_issues:
        console.print(f"\n  [yellow]⚠ {len(filing.redaction_issues)} redaction warning(s)[/yellow]")

    # Dry run notice
    if dry_run:
        console.print("\n  [yellow][DRY RUN — will NOT submit][/yellow]")

    # Confirmation prompt
    console.print()
    response = Prompt.ask(
        "  Type [bold]CONFIRM[/bold] to submit, or [bold]CANCEL[/bold] to abort"
    )

    return response.strip().upper() == "CONFIRM"
