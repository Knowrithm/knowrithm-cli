"""Configuration related CLI commands."""

from __future__ import annotations

import json

import click

from .. import config
from ..utils import print_json


@click.group(name="config")
def cmd() -> None:
    """Inspect and update local CLI configuration."""


@cmd.command("show")
def show_config() -> None:
    """Display the current configuration with sensitive values masked."""
    cfg = config.load_config()
    safe_cfg = json.loads(json.dumps(cfg))  # deep copy
    api_secret = safe_cfg.get("auth", {}).get("api_key", {}).get("secret")
    if api_secret:
        safe_cfg["auth"]["api_key"]["secret"] = "***"
    print_json(safe_cfg)


@cmd.command("set-base-url")
@click.argument("url", metavar="URL")
def set_base_url(url: str) -> None:
    """Persist the Knowrithm API base URL."""
    config.set_base_url(url)
    click.secho(f"Base URL set to {url}", fg="green")


@cmd.command("set-verify-ssl")
@click.option(
    "--enable/--disable",
    "enabled",
    default=True,
    show_default=True,
    help="Enable or disable TLS certificate verification.",
)
def set_verify_ssl(enabled: bool) -> None:
    """Toggle TLS certificate verification."""
    config.set_verify_ssl(enabled)
    state = "enabled" if enabled else "disabled"
    click.secho(f"TLS verification {state}.", fg="green")


@cmd.command("path")
def show_path() -> None:
    """Print the path to the configuration file."""
    click.echo(str(config.CONFIG_FILE))

