"""LLM settings and provider management commands."""

from __future__ import annotations

from typing import Optional

import click

from ..utils import load_json_payload, print_json
from .common import auth_kwargs, auth_option, make_client


@click.group(name="settings")
def cmd() -> None:
    """Manage LLM and embedding settings."""


@cmd.command("create")
@auth_option()
@click.option("--payload", required=True, help="JSON payload for settings creation.")
@click.option("--wait/--no-wait", default=True, show_default=True)
def create_settings(auth: str, payload: str, wait: bool) -> None:
    """Create LLM settings via provider/model IDs."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post("/api/v1/settings", json=body, **auth_kwargs(auth))
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("create-sdk")
@auth_option()
@click.option("--payload", required=True, help="JSON payload using provider/model names.")
@click.option("--wait/--no-wait", default=True, show_default=True)
def create_settings_sdk(auth: str, payload: str, wait: bool) -> None:
    """Create settings using provider/model names (SDK endpoint)."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post("/api/v1/sdk/settings", json=body, **auth_kwargs(auth))
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("list-company")
@auth_option()
@click.argument("company_id")
def list_company_settings(auth: str, company_id: str) -> None:
    """List settings for a company."""
    client = make_client()
    response = client.get(
        f"/api/v1/settings/company/{company_id}",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("list-agent")
@auth_option()
@click.argument("agent_id")
def list_agent_settings(auth: str, agent_id: str) -> None:
    """List settings for a given agent."""
    client = make_client()
    response = client.get(
        f"/api/v1/settings/agent/{agent_id}",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("get")
@auth_option()
@click.argument("settings_id")
def get_settings(auth: str, settings_id: str) -> None:
    """Retrieve a settings record."""
    client = make_client()
    response = client.get(f"/api/v1/settings/{settings_id}", **auth_kwargs(auth))
    print_json(response)


@cmd.command("update")
@auth_option()
@click.argument("settings_id")
@click.option("--payload", required=True, help="JSON payload with updated fields.")
@click.option("--wait/--no-wait", default=True, show_default=True)
def update_settings(auth: str, settings_id: str, payload: str, wait: bool) -> None:
    """Update an LLM settings record."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.put(
        f"/api/v1/settings/{settings_id}",
        json=body,
        **auth_kwargs(auth),
    )
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("delete")
@auth_option()
@click.argument("settings_id")
@click.option("--wait/--no-wait", default=False, show_default=True)
def delete_settings(auth: str, settings_id: str, wait: bool) -> None:
    """Delete an LLM settings record."""
    client = make_client()
    response = client.delete(f"/api/v1/settings/{settings_id}", **auth_kwargs(auth))
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("test")
@auth_option()
@click.argument("settings_id")
@click.option("--payload", help="Optional JSON payload with overrides.")
@click.option("--wait/--no-wait", default=True, show_default=True)
def test_settings(auth: str, settings_id: str, payload: Optional[str], wait: bool) -> None:
    """Validate settings by executing a test call."""
    body = load_json_payload(payload) if payload else None
    client = make_client()
    response = client.post(
        f"/api/v1/settings/test/{settings_id}",
        json=body,
        **auth_kwargs(auth),
    )
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)
