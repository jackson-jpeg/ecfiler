"""User input prompts with validation."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt


def prompt_file_path(
    console: Console,
    label: str = "File path",
    must_exist: bool = True,
    extension: str = ".pdf",
) -> str:
    """Prompt for a file path with validation.

    Args:
        console: Rich console
        label: Prompt label
        must_exist: Whether the file must exist
        extension: Required file extension

    Returns:
        Validated file path string
    """
    while True:
        path_str = Prompt.ask(f"  {label}")
        path_str = path_str.strip().strip("'\"")

        path = Path(path_str).expanduser().resolve()

        if must_exist and not path.exists():
            console.print(f"  [red]File not found: {path}[/red]")
            continue

        if extension and path.suffix.lower() != extension.lower():
            console.print(f"  [yellow]Expected {extension} file, got {path.suffix}[/yellow]")
            if not Prompt.ask("  Continue anyway?", choices=["y", "n"], default="n") == "y":
                continue

        return str(path)


def prompt_case_number(console: Console) -> str:
    """Prompt for a case number with basic format validation."""
    while True:
        case_num = Prompt.ask("  Case number")
        case_num = case_num.strip()

        if not case_num:
            console.print("  [red]Case number required.[/red]")
            continue

        return case_num


def prompt_court_id(console: Console, default: str = "") -> str:
    """Prompt for a court ID."""
    prompt = "  Court ID"
    if default:
        court_id = Prompt.ask(prompt, default=default)
    else:
        court_id = Prompt.ask(prompt)
    return court_id.strip().lower()
