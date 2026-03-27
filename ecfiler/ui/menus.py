"""Rich-based menu system for ECFiler TUI."""

from __future__ import annotations

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table


def numbered_menu(
    console: Console,
    title: str,
    options: list[str],
    default: int = 1,
) -> int:
    """Display a numbered menu and return the selected index (0-based).

    Args:
        console: Rich console
        title: Menu title
        options: List of option labels
        default: Default choice (1-based)

    Returns:
        0-based index of the selected option
    """
    console.print(f"\n  [bold]{title}[/bold]")
    for i, opt in enumerate(options, 1):
        marker = ">" if i == default else " "
        console.print(f"  {marker}[{i}] {opt}")

    choices = [str(i) for i in range(1, len(options) + 1)]
    choice = Prompt.ask("  Select", choices=choices, default=str(default))
    return int(choice) - 1


def table_menu(
    console: Console,
    title: str,
    rows: list[dict[str, str]],
    columns: list[str],
    id_column: str = "id",
) -> str:
    """Display a table of options and return the selected ID.

    Args:
        console: Rich console
        title: Table title
        rows: List of row dicts
        columns: Column names to display
        id_column: Which column contains the selectable ID

    Returns:
        The ID value of the selected row
    """
    table = Table(title=title, border_style="dim")
    table.add_column("#", style="bold", width=4)
    for col in columns:
        table.add_column(col.title())

    for i, row in enumerate(rows, 1):
        table.add_row(str(i), *[row.get(col, "") for col in columns])

    console.print(table)

    choices = [str(i) for i in range(1, len(rows) + 1)]
    choice = Prompt.ask("  Select", choices=choices)
    return rows[int(choice) - 1].get(id_column, "")


def confirm_action(
    console: Console,
    message: str,
    confirm_word: str = "CONFIRM",
) -> bool:
    """Require the user to type a specific word to confirm.

    More secure than y/n for critical actions like filing.
    """
    response = Prompt.ask(
        f"  {message} Type [bold]{confirm_word}[/bold] to proceed"
    )
    return response.upper() == confirm_word.upper()
