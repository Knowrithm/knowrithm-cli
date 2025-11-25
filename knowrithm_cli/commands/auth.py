"""Authentication and credential management commands."""

from __future__ import annotations

from typing import Any, Dict, Optional

import click

from .. import config
from ..client import KnowrithmClient
from ..utils import load_json_payload, print_json
from .common import auth_kwargs, auth_option, make_client


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


@cmd.command("login")
@click.option("--email", prompt=True, help="User email.")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=False,
    help="Account password.",
)
@click.option("--wait/--no-wait", default=True, help="Wait for async task responses.")
def login(email: str, password: str, wait: bool) -> None:
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
    print_json(response)


@cmd.command("logout")
def logout() -> None:
    """Revoke the current session and clear cached tokens."""
    client = make_client()
    response = client.post("/api/v1/auth/logout")
    config.clear_jwt_tokens()
    click.secho("Logged out and cleared cached tokens.", fg="green")
    print_json(response)


@cmd.command("refresh")
def refresh_tokens() -> None:
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
    print_json(response)


@cmd.command("register")
@click.option("--payload", help="JSON string or @path to describe the new admin user.")
def register(payload: Optional[str]) -> None:
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
    print_json(response)


@cmd.command("me")
@auth_option()
def me(auth: str) -> None:
    """Return details for the authenticated user."""
    client = make_client()
    response = client.get("/api/v1/auth/user/me", **auth_kwargs(auth))
    print_json(response)


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
def validate(auth: str) -> None:
    """Validate current credentials with the backend."""
    client = make_client()
    response = client.get("/api/v1/auth/validate", **auth_kwargs(auth))
    print_json(response)

