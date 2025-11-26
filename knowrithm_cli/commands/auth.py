"""Authentication and credential management commands."""

from __future__ import annotations

from typing import Any, Dict, Optional

import click

from .. import config
from ..client import KnowrithmClient
from ..core.formatters import format_output
from ..utils import load_json_payload
from .common import auth_kwargs, auth_option, format_option, make_client


@click.group(name="auth")
def cmd() -> None:
    """Authenticate and manage access credentials."""


def _store_tokens(token_payload: Dict[str, Any]) -> None:
    access_token = token_payload.get("access_token")
    refresh_token = token_payload.get("refresh_token")
    expires_at = token_payload.get("expires_at") or token_payload.get("expires_in")
    if access_token:
        config.store_jwt_tokens(access_token, refresh_token, expires_at=expires_at)
        click.secho("Tokens stored in local configuration.", fg="green")


def _extract_tokens(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not payload:
        return None
    for key in ("tokens", "data", "result"):
        if isinstance(payload.get(key), dict):
            maybe = payload[key]
            if "access_token" in maybe:
                return maybe
    if "access_token" in payload:
        return payload
    return None


from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

@cmd.command("login")
@format_option()
@click.option("--email", prompt=True, help="User email.")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="Account password.",
)
@click.option("--wait/--no-wait", default=True, help="Wait for async task responses.")
def login(email: str, password: str, wait: bool, format: str) -> None:
    """Authenticate with email/password and cache JWT tokens."""
    client = make_client()
    payload = {"email": email, "password": password}
    response = client.post(
        "/api/v1/auth/login",
        json=payload,
        require_auth=False,
        use_jwt=False,
    )
    if response.get("task_id") and wait:
        response = client.handle_async_response(response, wait=True)
    tokens = _extract_tokens(response)
    if tokens:
        _store_tokens(tokens)
    
    # Check for user data in various locations
    user_data = response.get("user")
    if not user_data and isinstance(response.get("data"), dict):
        user_data = response["data"].get("user")
    
    if format == "table" and user_data:
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="bold cyan")
        table.add_column("Value", style="white")
        
        full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        table.add_row("User:", f"{full_name} ({user_data.get('email', '')})")
        table.add_row("Role:", user_data.get("role", "Unknown").title())
        table.add_row("ID:", user_data.get("id", "Unknown"))
        
        status = user_data.get("status", "unknown")
        status_style = "green" if status == "active" else "yellow"
        table.add_row("Status:", f"[{status_style}]{status.title()}[/{status_style}]")
        
        console.print(Panel(
            table,
            title="[bold green]Login Successful[/bold green]",
            border_style="green",
            expand=False
        ))
    else:
        click.echo(format_output(response, format))


@cmd.command("logout")
@format_option()
def logout(format: str) -> None:
    """Revoke the current session and clear cached tokens."""
    client = make_client()
    response = client.post("/api/v1/auth/logout")
    config.clear_jwt_tokens()
    click.secho("Logged out and cleared cached tokens.", fg="green")
    click.echo(format_output(response, format))


@cmd.command("refresh")
@format_option()
def refresh_tokens(format: str) -> None:
    """Refresh the access token using the cached refresh token."""
    tokens = config.get_jwt_tokens()
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise click.ClickException(
            "No refresh token stored. Please login again or provide an API key."
        )
    client = make_client()
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
        use_jwt=False,
        require_auth=False,
    )
    tokens = _extract_tokens(response) or response
    if tokens:
        _store_tokens(tokens)
    click.echo(format_output(response, format))


@cmd.command("register")
@format_option()
@click.option("--payload", help="JSON string or @path to describe the new admin user.")
def register(payload: Optional[str], format: str) -> None:
    """Register a new company admin account (public endpoint)."""
    body = load_json_payload(payload)
    if not isinstance(body, dict):
        raise click.ClickException("Registration requires a JSON object payload.")
    client = make_client()
    response = client.post(
        "/api/v1/auth/register",
        json=body,
        require_auth=False,
        use_jwt=False,
    )
    click.echo(format_output(response, format))


@cmd.command("me")
@auth_option()
@format_option()
def me(auth: str, format: str) -> None:
    """Return details for the authenticated user."""
    client = make_client()
    response = client.get("/api/v1/auth/user/me", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("set-api-key")
@click.option("--key", prompt=True, hide_input=False, help="API key.")
@click.option("--secret", prompt=True, hide_input=True, help="API secret.")
def set_api_key(key: str, secret: str) -> None:
    """Persist an API key + secret pair for future requests."""
    config.store_api_credentials(key, secret)
    click.secho("API credentials stored.", fg="green")


@cmd.command("clear")
@click.option(
    "--all",
    "clear_all",
    is_flag=True,
    help="Clear both JWT tokens and API key credentials.",
)
@click.option("--tokens", is_flag=True, help="Clear only JWT tokens.")
@click.option("--api-key", "clear_api", is_flag=True, help="Clear only API key credentials.")
def clear(clear_all: bool, tokens: bool, clear_api: bool) -> None:
    """Clear cached credentials."""
    if clear_all or tokens:
        config.clear_jwt_tokens()
        click.secho("Cleared JWT tokens.", fg="yellow")
    if clear_all or clear_api:
        config.clear_api_credentials()
        click.secho("Cleared API key credentials.", fg="yellow")
    if not (clear_all or tokens or clear_api):
        click.echo("Nothing to clear. Use --tokens, --api-key or --all.")


@cmd.command("validate")
@auth_option()
@format_option()
def validate(auth: str, format: str) -> None:
    """Validate current credentials with the backend."""
    client = make_client()
    response = client.get("/api/v1/auth/validate", **auth_kwargs(auth))
    click.echo(format_output(response, format))
