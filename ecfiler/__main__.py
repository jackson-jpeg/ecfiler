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


@main.command("quick")
@click.argument("template_name")
@click.argument("case_number")
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--court", type=str, help="Override court from template")
@click.option("--dry-run", is_flag=True, help="Stop before submitting")
def quick_file(
    template_name: str,
    case_number: str,
    pdf_path: str,
    court: str | None,
    dry_run: bool,
) -> None:
    """Quick file using a saved template.

    Example: ecfiler quick motion-dismiss 1:24-cv-01234 ./brief.pdf
    """
    from rich.console import Console

    from ecfiler.storage.templates import load_template, list_templates

    console = Console()
    template = load_template(template_name)

    if template is None:
        console.print(f"[red]Template '{template_name}' not found.[/red]")
        available = list_templates()
        if available:
            console.print(f"Available templates: {', '.join(available)}")
        else:
            console.print("[dim]No templates saved yet. File normally first, then save as template.[/dim]")
        return

    console.print(f"\n  Template: [bold]{template_name}[/bold]")
    console.print(f"  Court:    {court or template.get('court_id', '?')}")
    console.print(f"  Case:     {case_number}")
    console.print(f"  Event:    {template.get('event_description', '?')}")
    console.print(f"  Document: {pdf_path}")

    if dry_run:
        console.print("\n  [yellow]DRY RUN — template validated, would proceed to filing.[/yellow]")
        return

    console.print("\n  [dim]To file, use the interactive workflow: ecfiler[/dim]")


@main.command("demo")
def demo_mode() -> None:
    """Run a demo filing walkthrough (no PACER account needed).

    Shows the complete ECFiler workflow using sample data.
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()

    console.print(
        Panel(
            "[bold cyan]ECFiler Demo Mode[/bold cyan]\n"
            "[dim]This walkthrough shows the complete filing workflow using sample data.\n"
            "No PACER account or court access is needed.[/dim]",
            border_style="cyan",
        )
    )

    import time

    steps = [
        ("Selecting court", "S.D.N.Y. (nysd)"),
        ("Looking up case", "1:24-cv-01234 — Smith v. Jones Corp | Judge Williams | Open"),
        ("AI suggesting event code", "Reply Memorandum of Law in Support (Code 102) — Confidence: high"),
        ("Filing on behalf of", "Smith (plaintiff) by Jane Doe, Esq. (Bar #JD5678)"),
        ("Responding to", "Docket #45 — Motion to Dismiss (filed 2024-11-15)"),
        ("Validating PDF", "reply_brief.pdf — 2.3MB, 15 pages, searchable, PDF/A"),
        ("Scanning redaction", "No Rule 5.2 personal identifiers found"),
        ("AI validation", "Document title matches event code. No missing attachments."),
    ]

    for label, result in steps:
        console.print(f"\n  [dim]{label}...[/dim]")
        time.sleep(0.5)
        console.print(f"  [green]✓[/green] {result}")

    # Show review screen
    console.print()
    console.print(
        Panel(
            "[bold red]FILING REVIEW — ATTORNEY APPROVAL REQUIRED[/bold red]",
            border_style="red",
        )
    )

    table = Table(show_header=False, border_style="dim")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Court", "S.D.N.Y. (district)")
    table.add_row("Case", "1:24-cv-01234")
    table.add_row("Title", "Smith v. Jones Corp")
    table.add_row("Judge", "Williams")
    table.add_row("Event", "Reply Memorandum of Law in Support (102)")
    table.add_row("Filing for", "Smith (plaintiff) by Jane Doe")
    table.add_row("[yellow]Response to[/yellow]", "Docket #45 — Motion to Dismiss")
    table.add_row("Document", "[green]✓[/green] reply_brief.pdf (2.3MB)")
    console.print(table)

    console.print("\n  [dim]In a real filing, you would type CONFIRM here.[/dim]")
    console.print(
        "\n  [green]✓[/green] [bold]Demo complete.[/bold] "
        "To file for real, run [bold]ecfiler[/bold] and configure your PACER credentials."
    )


@main.command("save-template")
@click.argument("name")
@click.option("--court", required=True, help="Court ID (e.g., nysd)")
@click.option("--event-code", required=True, help="Event code")
@click.option("--event-desc", required=True, help="Event description")
@click.option("--party-role", default="plaintiff", help="Filing party role")
def save_template_cmd(
    name: str,
    court: str,
    event_code: str,
    event_desc: str,
    party_role: str,
) -> None:
    """Save a filing template for quick reuse.

    Example: ecfiler save-template mtd --court nysd --event-code 12 --event-desc "Motion to Dismiss"
    """
    from rich.console import Console

    from ecfiler.storage.templates import save_template

    console = Console()

    data = {
        "court_id": court,
        "event_code": event_code,
        "event_description": event_desc,
        "party_role": party_role,
    }

    path = save_template(name, data)
    console.print(f"  [green]✓[/green] Template '{name}' saved to {path}")
    console.print(f"  [dim]Use with: ecfiler quick {name} <case_number> <pdf_path>[/dim]")


@main.command("smart")
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Stop before submitting")
@click.pass_context
def smart_file(ctx: click.Context, pdf_path: str, dry_run: bool) -> None:
    """Smart file — drop a PDF, AI figures out the rest.

    Analyzes your document to auto-extract case number, court, party,
    event type, and response context. You just review and confirm.

    Example: ecfiler smart ./motion_to_dismiss.pdf
    """
    from ecfiler.agent.smart_filer import SmartFiler
    from ecfiler.config import load_config

    config = load_config(ctx.obj.get("config"))
    if dry_run or ctx.obj.get("dry_run"):
        config.general.dry_run = True

    filer = SmartFiler(config)
    filer.file(pdf_path, dry_run=config.general.dry_run)


@main.command("serve")
@click.option("--host", default="127.0.0.1", help="Bind address")
@click.option("--port", default=8000, help="Port number")
@click.option("--reload", "do_reload", is_flag=True, help="Auto-reload on code changes")
def serve(host: str, port: int, do_reload: bool) -> None:
    """Start the ECFiler API server.

    Runs the FastAPI backend at http://host:port.
    API docs at http://host:port/docs.

    Example: ecfiler serve --port 8080
    """
    import uvicorn

    from rich.console import Console

    console = Console()
    console.print(f"\n  [bold cyan]ECFiler API Server[/bold cyan]")
    console.print(f"  [dim]http://{host}:{port}[/dim]")
    console.print(f"  [dim]API docs: http://{host}:{port}/docs[/dim]")
    console.print(f"  [dim]Health: http://{host}:{port}/api/health[/dim]\n")

    uvicorn.run(
        "ecfiler.api.app:app",
        host=host,
        port=port,
        reload=do_reload,
    )


@main.command("check")
@click.pass_context
def check_setup(ctx: click.Context) -> None:
    """Verify ECFiler setup — API key, PACER credentials, browser, PDF tools.

    Run this before your first filing to make sure everything is configured.
    """
    from rich.console import Console
    from rich.table import Table

    from ecfiler.diagnostics import run_diagnostics

    console = Console()
    console.print("\n  [bold]ECFiler Setup Diagnostics[/bold]\n")

    report = run_diagnostics(ctx.obj.get("config"))

    table = Table(show_header=True, border_style="dim")
    table.add_column("Check", width=16)
    table.add_column("Status", width=6)
    table.add_column("Details")
    table.add_column("Fix", style="dim")

    for check in report.checks:
        status = "[green]PASS[/green]" if check.passed else "[red]FAIL[/red]"
        table.add_row(check.name, status, check.message, check.fix)

    console.print(table)
    console.print()

    if report.all_passed:
        console.print(f"  [green]All {report.pass_count} checks passed.[/green] Ready to file.")
    elif report.required_passed:
        console.print(
            f"  [yellow]{report.pass_count} passed, {report.fail_count} failed.[/yellow] "
            f"Core checks OK — some features may be limited."
        )
    else:
        console.print(
            f"  [red]{report.fail_count} checks failed.[/red] "
            f"Fix the issues above before filing."
        )


if __name__ == "__main__":
    main()
