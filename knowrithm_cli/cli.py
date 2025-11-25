"""Entry point for the Knowrithm command-line interface."""

from __future__ import annotations

import click

from . import __version__
from .commands import register as register_commands


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="Knowrithm CLI")
def cli() -> None:
    """Interact with the Knowrithm platform from the terminal."""


# Register command groups at import time.
register_commands(cli)


def main() -> None:  # pragma: no cover - convenience entry point
    cli()


if __name__ == "__main__":  # pragma: no cover
    main()

