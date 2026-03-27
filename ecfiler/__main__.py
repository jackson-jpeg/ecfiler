"""Entry point: python -m ecfiler"""

import click

from ecfiler.app import run_app


@click.command()
@click.option("--config", "-c", type=click.Path(), help="Path to config file")
@click.option("--dry-run", is_flag=True, help="Walk through filing without submitting")
@click.option("--court", type=str, help="Court ID to use (overrides default)")
def main(config: str | None, dry_run: bool, court: str | None) -> None:
    """ECFiler — Automated filing for Federal CM/ECF court systems."""
    run_app(config_path=config, dry_run=dry_run, court_override=court)


if __name__ == "__main__":
    main()
