"""Entry point: python -m ecfiler"""

import click

from ecfiler import __version__


@click.group(invoke_without_command=True)
@click.option("--config", "-c", type=click.Path(), help="Path to config file")
@click.option("--dry-run", is_flag=True, help="Walk through filing without submitting")
@click.option("--court", type=str, help="Court ID to use (overrides default)")
@click.version_option(version=__version__)
@click.pass_context
def main(ctx: click.Context, config: str | None, dry_run: bool, court: str | None) -> None:
    """ECFiler — Automated filing for Federal CM/ECF court systems."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["dry_run"] = dry_run
    ctx.obj["court"] = court

    # If no subcommand, launch the interactive TUI
    if ctx.invoked_subcommand is None:
        from ecfiler.app import run_app

        run_app(config_path=config, dry_run=dry_run, court_override=court)


@main.command()
@click.pass_context
def setup(ctx: click.Context) -> None:
    """Store PACER credentials in system keyring."""
    from rich.console import Console
    from rich.prompt import Prompt

    from ecfiler.pacer_auth import PacerAuth

    console = Console()
    console.print("\n[bold]PACER Credential Setup[/bold]")
    console.print("[dim]Your password will be stored in the system keyring (not plaintext).[/dim]\n")

    username = Prompt.ask("  PACER username (email)")
    if not username:
        console.print("[red]  Username required.[/red]")
        return

    password = Prompt.ask("  PACER password", password=True)
    if not password:
        console.print("[red]  Password required.[/red]")
        return

    auth = PacerAuth(username)
    auth.store_password(password)
    console.print(f"\n  [green]✓[/green] Credentials stored for [bold]{username}[/bold]")

    # Optionally test the credentials
    if click.confirm("  Test authentication with PACER?", default=True):
        console.print("  [dim]Authenticating...[/dim]")
        try:
            token = auth.authenticate()
            console.print(f"  [green]✓[/green] Authentication successful (token: {token.token[:12]}...)")
        except Exception as e:
            console.print(f"  [red]✗[/red] Authentication failed: {e}")
        finally:
            auth.close()


@main.command("courts")
@click.option("--type", "-t", "court_type", type=click.Choice(["district", "bankruptcy", "appellate"]))
@click.option("--search", "-s", "query", type=str, help="Search by name or ID")
def list_courts(court_type: str | None, query: str | None) -> None:
    """List available federal courts."""
    from rich.console import Console
    from rich.table import Table

    from ecfiler.courts.registry import CourtRegistry

    console = Console()
    registry = CourtRegistry()

    if query:
        courts = registry.search(query)
        title = f"Courts matching '{query}'"
    else:
        courts = registry.list_courts(court_type)
        title = f"{'All' if not court_type else court_type.title()} Courts"

    if not courts:
        console.print(f"[yellow]No courts found.[/yellow]")
        return

    table = Table(title=f"{title} ({len(courts)})", border_style="dim")
    table.add_column("ID", style="bold cyan", width=8)
    table.add_column("Name")
    table.add_column("Type", width=12)
    table.add_column("ECF URL", style="dim")

    for court in courts:
        court_id = court["court_id"]
        ecf_url = f"ecf.{court_id}.uscourts.gov"
        table.add_row(court_id, court["name"], court["type"], ecf_url)

    console.print(table)


@main.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--redaction/--no-redaction", default=True, help="Run redaction scan")
def validate(pdf_path: str, redaction: bool) -> None:
    """Validate a PDF for CM/ECF filing requirements."""
    from rich.console import Console

    from ecfiler.pdf.validator import extract_text, validate_pdf

    console = Console()
    console.print(f"\n  Validating: [bold]{pdf_path}[/bold]\n")

    result = validate_pdf(pdf_path)

    if result.valid:
        console.print(f"  [green]✓ VALID[/green]  {result.summary}")
    else:
        console.print(f"  [red]✗ INVALID[/red]  {result.summary}")

    for err in result.errors:
        console.print(f"    [red]Error: {err}[/red]")
    for warn in result.warnings:
        console.print(f"    [yellow]Warning: {warn}[/yellow]")

    # Redaction scan
    if redaction and result.valid:
        console.print("\n  [dim]Scanning for redaction issues...[/dim]")
        from ecfiler.pdf.redaction_check import scan_document

        text = extract_text(pdf_path)
        report = scan_document(text)

        if report.has_issues:
            console.print(f"  [yellow]⚠ {len(report.issues)} potential redaction issue(s):[/yellow]")
            for issue in report.issues:
                console.print(
                    f"    [{issue.confidence}] {issue.issue_type}: "
                    f"'{issue.text[:60]}' — {issue.suggestion}"
                )
        else:
            console.print("  [green]✓[/green] No redaction issues detected")


@main.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output path (default: adds _pdfa suffix)")
@click.option("--ocr/--no-ocr", default=True, help="Add OCR text layer if missing")
def convert(pdf_path: str, output: str | None, ocr: bool) -> None:
    """Convert a PDF to PDF/A format for court filing."""
    from rich.console import Console

    from ecfiler.pdf.converter import convert_to_pdfa, is_ocrmypdf_available

    console = Console()

    if not is_ocrmypdf_available():
        console.print(
            "[red]ocrmypdf is not installed.[/red]\n"
            "Install with: pip install 'ecfiler[pdf-convert]' && apt install ghostscript tesseract-ocr"
        )
        return

    console.print(f"  Converting: [bold]{pdf_path}[/bold]")
    result = convert_to_pdfa(pdf_path, output_path=output, add_ocr=ocr)

    if result.success:
        console.print(f"  [green]✓[/green] {result.message}")
    else:
        console.print(f"  [red]✗[/red] {result.message}")


@main.command()
@click.option("--limit", "-n", default=20, help="Number of entries to show")
@click.option("--search", "-s", "query", type=str, help="Search by case number or event")
def history(limit: int, query: str | None) -> None:
    """View filing history."""
    from rich.console import Console

    from ecfiler.storage.history import FilingHistory

    console = Console()
    hist = FilingHistory()

    if query:
        entries = hist.search(query)
        if not entries:
            console.print(f"  [dim]No filings matching '{query}'[/dim]")
            return
        # Reuse show_recent display but with search results
        console.print(f"\n  [bold]Filings matching '{query}':[/bold]")
    else:
        entries = hist.get_recent(limit)

    if not entries:
        console.print("  [dim]No filing history yet.[/dim]")
        return

    hist.show_recent(console, limit)


if __name__ == "__main__":
    main()
