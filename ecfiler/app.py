"""Main application entry point and menu loop."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from ecfiler import __version__
from ecfiler.config import AppConfig, load_config

console = Console()


def run_app(
    config_path: str | None = None,
    dry_run: bool = False,
    court_override: str | None = None,
) -> None:
    """Main application loop."""
    cfg = load_config(config_path)

    if dry_run:
        cfg.general.dry_run = True
    if court_override:
        cfg.general.default_court = court_override

    _show_banner()
    _main_menu(cfg)


def _show_banner() -> None:
    console.print(
        Panel(
            f"[bold cyan]ECFiler[/bold cyan] v{__version__}\n"
            "[dim]Automated filing for Federal CM/ECF courts[/dim]",
            border_style="cyan",
        )
    )


def _main_menu(cfg: AppConfig) -> None:
    """Top-level menu loop."""
    while True:
        console.print()
        console.print("[bold]Main Menu[/bold]")
        console.print("  [1] New Filing")
        console.print("  [2] Resume Draft")
        console.print("  [3] Filing History")
        console.print("  [4] Settings")
        console.print("  [5] Setup Credentials")
        console.print("  [6] Quit")
        console.print()

        choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5", "6"], default="1")

        match choice:
            case "1":
                _new_filing(cfg)
            case "2":
                _resume_draft(cfg)
            case "3":
                _filing_history(cfg)
            case "4":
                _settings(cfg)
            case "5":
                _setup_credentials(cfg)
            case "6":
                console.print("[dim]Goodbye.[/dim]")
                break


def _new_filing(cfg: AppConfig) -> None:
    """Start a new filing workflow."""
    from ecfiler.filing.workflow import FilingWorkflow

    workflow = FilingWorkflow(cfg)
    workflow.run()


def _resume_draft(cfg: AppConfig) -> None:
    """Resume a saved draft filing."""
    from ecfiler.filing.drafts import delete_draft, list_drafts, load_draft

    drafts = list_drafts()
    if not drafts:
        console.print("\n  [dim]No saved drafts.[/dim]")
        return

    console.print("\n  [bold]Saved Drafts[/bold]")
    for i, d in enumerate(drafts, 1):
        console.print(
            f"  [{i}] {d['name']} — {d['court']} {d['case']} "
            f"{d['event'][:30]} ({d['saved_at'][:10]})"
        )

    choice = Prompt.ask(
        "  Select draft",
        choices=[str(i) for i in range(1, len(drafts) + 1)],
    )
    selected = drafts[int(choice) - 1]
    data = load_draft(selected["file"])

    if not data:
        console.print("  [red]Failed to load draft.[/red]")
        return

    console.print(f"\n  Resuming: [bold]{selected['name']}[/bold]")

    # Reconstruct the Filing from draft data and run the workflow
    from ecfiler.filing.models import Filing
    from ecfiler.filing.workflow import FilingWorkflow

    try:
        filing = Filing.model_validate(data)
        workflow = FilingWorkflow(cfg)
        workflow.filing = filing

        # Show what we have so far and jump to review
        console.print(f"  Court: {filing.court_id}")
        console.print(f"  Case:  {filing.case.case_number}")
        console.print(f"  Event: {filing.event.description}")

        if Prompt.ask("  Continue to review?", choices=["y", "n"], default="y") == "y":
            # Run from AI validation onward
            workflow._step_preflight()
            workflow._step_ai_validation()
            if workflow._step_attorney_review():
                if cfg.general.dry_run:
                    console.print("\n  [yellow]DRY RUN — stopping.[/yellow]")
                else:
                    receipt = workflow._step_submit_filing()
                    if receipt:
                        workflow._step_save_receipt(receipt)
                # Clean up draft on successful review
                delete_draft(selected["file"])
                console.print(f"  [dim]Draft '{selected['name']}' removed.[/dim]")
    except Exception as e:
        console.print(f"  [red]Error resuming draft: {e}[/red]")


def _filing_history(cfg: AppConfig) -> None:
    """View past filings."""
    from ecfiler.storage.history import FilingHistory

    history = FilingHistory()
    history.show_recent(console)


def _settings(cfg: AppConfig) -> None:
    """View/edit settings."""
    from ecfiler.config import CONFIG_FILE

    console.print(f"\n[bold]Config file:[/bold] {CONFIG_FILE}")
    console.print(f"  Default court: {cfg.general.default_court or '[dim]not set[/dim]'}")
    console.print(f"  Claude model:  {cfg.general.claude_model}")
    console.print(f"  Dry run:       {cfg.general.dry_run}")
    console.print(f"  PACER user:    {cfg.pacer.username or '[dim]not set[/dim]'}")
    console.print(f"  Attorney:      {cfg.attorney.name or '[dim]not set[/dim]'}")
    console.print(f"\n[dim]Edit {CONFIG_FILE} to change settings.[/dim]")


def _setup_credentials(cfg: AppConfig) -> None:
    """Store PACER credentials in keyring."""
    from ecfiler.pacer_auth import PacerAuth

    username = Prompt.ask("PACER username (email)", default=cfg.pacer.username or "")
    if not username:
        console.print("[red]Username required.[/red]")
        return

    password = Prompt.ask("PACER password", password=True)
    if not password:
        console.print("[red]Password required.[/red]")
        return

    auth = PacerAuth(username)
    auth.store_password(password)
    console.print(f"[green]✓[/green] Credentials stored for {username}")
    auth.close()
