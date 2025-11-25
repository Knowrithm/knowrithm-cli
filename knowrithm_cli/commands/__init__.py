"""Command groups registered with the top-level CLI."""

from __future__ import annotations

from typing import Iterable

import click

# Each module exposes a click.Group instance named ``cmd`` (or similar). We
# import lazily inside ``register`` to avoid unnecessary startup overhead when
# users only request ``--help``.


def register(cli: click.Group) -> None:
    """Attach all sub-command groups to the root CLI."""
    for group in _load_groups():
        cli.add_command(group)


def _load_groups() -> Iterable[click.Group]:
    from . import (
        analytics,
        agent,
        auth,
        company,
        config_cmd,
        context_cmd,
        conversation,
        database,
        document,
        lead,
        settings,
        system,
        website,
    )

    return (
        config_cmd.cmd,
        auth.cmd,
        context_cmd.cmd,
        agent.cmd,
        conversation.cmd,
        document.cmd,
        database.cmd,
        lead.cmd,
        company.cmd,
        settings.cmd,
        analytics.cmd,
        website.cmd,
        system.cmd,
    )

