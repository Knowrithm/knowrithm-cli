"""Utility helpers shared across CLI command modules."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import click


def load_json_payload(payload: Optional[str]) -> Optional[Any]:
    """Convert a CLI ``--payload`` argument into a Python object.

    The option accepts either a raw JSON string or ``@`` followed by a file
    path, similar to how ``curl`` handles request bodies.
    """
    if payload is None:
        return None
    payload = payload.strip()
    if not payload:
        return None
    if payload.startswith("@"):
        path = Path(payload[1:])
        text = path.read_text(encoding="utf-8")
    else:
        text = payload
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise click.BadParameter(f"Invalid JSON payload: {exc}") from exc


def print_json(data: Any) -> None:
    """Pretty-print arbitrary data as JSON."""
    if data is None:
        click.echo("No data returned.")
        return
    click.echo(json.dumps(data, indent=2, sort_keys=True))


def join_flags(flags: Iterable[str]) -> str:
    """Render a human readable list of CLI flags."""
    flags = list(flags)
    if not flags:
        return ""
    if len(flags) == 1:
        return flags[0]
    return ", ".join(flags[:-1]) + f" and {flags[-1]}"


def wait_with_spinner(message: str, poller, *, interval: float = 2.0, timeout: float = 300.0) -> Any:
    """Poll ``poller`` until it returns a truthy result or the timeout is hit."""
    start = time.monotonic()
    spinner = click.style("⏳", fg="yellow")
    while True:
        result = poller()
        if result:
            return result
        if time.monotonic() - start > timeout:
            raise TimeoutError("Timed out waiting for task completion.")
        click.echo(f"{spinner} {message} (polling every {interval} seconds)...")
        time.sleep(interval)

