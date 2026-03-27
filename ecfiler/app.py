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
        console.print("  [2] Filing History")
        console.print("  [3] Settings")
        console.print("  [4] Setup Credentials")
        console.print("  [5] Quit")
        console.print()

        choice = Prompt.ask("Select", choices=["1", "2", "3", "4", "5"], default="1")

        match choice:
            case "1":
                _new_filing(cfg)
            case "2":
                _filing_history(cfg)
            case "3":
                _settings(cfg)
            case "4":
                _setup_credentials(cfg)
            case "5":
                console.print("[dim]Goodbye.[/dim]")
                break


def _new_filing(cfg: AppConfig) -> None:
    """Start a new filing workflow."""
    from ecfiler.filing.workflow import FilingWorkflow

    workflow = FilingWorkflow(cfg)
    workflow.run()


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
