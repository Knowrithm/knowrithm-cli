"""Entry point for the Knowrithm command-line interface."""

from __future__ import annotations

import click

from . import __version__
from .commands import register as register_commands


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(__version__, prog_name="Knowrithm CLI")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Interact with the Knowrithm platform from the terminal."""
    if ctx.invoked_subcommand is None:
        from .shell import run_interactive_mode
        run_interactive_mode(ctx)


# Register command groups at import time.
register_commands(cli)


def main() -> None:  # pragma: no cover - convenience entry point
    cli()


if __name__ == "__main__":  # pragma: no cover
    main()

