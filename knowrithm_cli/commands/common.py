"""Shared helpers for command modules."""

from __future__ import annotations

from typing import Any, Dict, Optional

import click

from ..client import KnowrithmClient


AUTH_CHOICES = ["jwt", "api-key", "none", "auto"]


def auth_option(help_text: Optional[str] = None):
    """Reusable click option for choosing an authentication scheme."""

    def decorator(func):
        return click.option(
            "--auth",
            type=click.Choice(AUTH_CHOICES),
            default="auto",
            show_default=True,
            help=help_text
            or "Authentication strategy (auto picks JWT if available, otherwise API key).",
        )(func)

    return decorator


def format_option(default: str = "table"):
    """Reusable click option for choosing output format."""

    def decorator(func):
        return click.option(
            "--format",
            type=click.Choice(["json", "table", "csv", "yaml", "tree"]),
            default=default,
            show_default=True,
            help="Output format for the response.",
        )(func)

    return decorator


def make_client(**kwargs: Any) -> KnowrithmClient:
    """Instantiate the API client."""
    return KnowrithmClient(**kwargs)


def auth_kwargs(auth_choice: str) -> Dict[str, Any]:
    """Translate ``--auth`` into keyword arguments for KnowrithmClient.request."""
    auth_choice = (auth_choice or "auto").lower()
    if auth_choice == "jwt":
        return {"use_jwt": True, "use_api_key": False, "require_auth": True}
    if auth_choice == "api-key":
        return {"use_jwt": False, "use_api_key": True, "require_auth": True}
    if auth_choice == "none":
        return {"use_jwt": False, "use_api_key": False, "require_auth": False}
    # auto
    return {"require_auth": True}

