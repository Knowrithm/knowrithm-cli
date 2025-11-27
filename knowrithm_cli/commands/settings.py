"""LLM settings and provider management commands."""

from __future__ import annotations

from typing import Optional

import click

from ..core.formatters import format_output
from ..utils import load_json_payload
from .common import auth_kwargs, auth_option, format_option, make_client


@click.group(name="settings")
def cmd() -> None:
    """Manage LLM and embedding settings."""


@cmd.command("create")
@auth_option()
@format_option()
@click.option("--payload", required=True, help="JSON payload for settings creation.")
@click.option("--wait/--no-wait", default=True, show_default=True)
def create_settings(auth: str, format: str, payload: str, wait: bool) -> None:
    """Create LLM settings via provider/model IDs."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post("/api/v1/settings", json=body, **auth_kwargs(auth))
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    click.echo(format_output(response, format))


@cmd.command("create-sdk")
@auth_option()
@format_option()
@click.option("--payload", required=True, help="JSON payload using provider/model names.")
@click.option("--wait/--no-wait", default=True, show_default=True)
def create_settings_sdk(auth: str, format: str, payload: str, wait: bool) -> None:
    """Create settings using provider/model names (SDK endpoint)."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post("/api/v1/sdk/settings", json=body, **auth_kwargs(auth))
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    click.echo(format_output(response, format))


@cmd.command("list-company")
@auth_option()
@format_option()
@click.argument("company_id", required=False)
def list_company_settings(auth: str, format: str, company_id: Optional[str]) -> None:
    """List settings for a company.
    
    If no company ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not company_id:
        from ..interactive import select_company
        click.echo("\n🏢 Select a company to list settings for:")
        company_id, _ = select_company(client, message="Select company")
        
    response = client.get(
        f"/api/v1/settings/company/{company_id}",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("list-agent")
@auth_option()
@format_option()
@click.argument("agent_id", required=False)
def list_agent_settings(auth: str, format: str, agent_id: Optional[str]) -> None:
    """List settings for a given agent.
    
    If no agent ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not agent_id:
        from ..interactive import select_agent
        click.echo("\n🤖 Select an agent to list settings for:")
        agent_id, _ = select_agent(client, message="Select agent")
        
    response = client.get(
        f"/api/v1/settings/agent/{agent_id}",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("get")
@auth_option()
@format_option()
@click.argument("settings_id", required=False)
def get_settings(auth: str, format: str, settings_id: Optional[str]) -> None:
    """Retrieve a settings record.
    
    If no settings ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not settings_id:
        from ..interactive import select_settings
        click.echo("\n⚙️  Select settings to view:")
        settings_id, _ = select_settings(client, message="Select settings")
        
    response = client.get(f"/api/v1/settings/{settings_id}", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("update")
@auth_option()
@format_option()
@click.argument("settings_id", required=False)
@click.option("--payload", required=True, help="JSON payload with updated fields.")
@click.option("--wait/--no-wait", default=True, show_default=True)
def update_settings(auth: str, format: str, settings_id: Optional[str], payload: str, wait: bool) -> None:
    """Update an LLM settings record.
    
    If no settings ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not settings_id:
        from ..interactive import select_settings
        click.echo("\n✏️  Select settings to update:")
        settings_id, _ = select_settings(client, message="Select settings")
        
    body = load_json_payload(payload)
    response = client.put(
        f"/api/v1/settings/{settings_id}",
        json=body,
        **auth_kwargs(auth),
    )
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    click.echo(format_output(response, format))


@cmd.command("delete")
@auth_option()
@format_option()
@click.argument("settings_id", required=False)
@click.option("--wait/--no-wait", default=False, show_default=True)
def delete_settings(auth: str, format: str, settings_id: Optional[str], wait: bool) -> None:
    """Delete an LLM settings record.
    
    If no settings ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not settings_id:
        from ..interactive import select_settings
        click.echo("\n🗑️  Select settings to delete:")
        settings_id, _ = select_settings(client, message="Select settings")
        
    response = client.delete(f"/api/v1/settings/{settings_id}", **auth_kwargs(auth))
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    click.echo(format_output(response, format))


@cmd.command("test")
@auth_option()
@format_option()
@click.argument("settings_id", required=False)
@click.option("--payload", help="Optional JSON payload with overrides.")
@click.option("--wait/--no-wait", default=True, show_default=True)
def test_settings(auth: str, format: str, settings_id: Optional[str], payload: Optional[str], wait: bool) -> None:
    """Validate settings by executing a test call.
    
    If no settings ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not settings_id:
        from ..interactive import select_settings
        click.echo("\n🧪 Select settings to test:")
        settings_id, _ = select_settings(client, message="Select settings")
        
    body = load_json_payload(payload) if payload else None
    response = client.post(
        f"/api/v1/settings/test/{settings_id}",
        json=body,
        **auth_kwargs(auth),
    )
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    click.echo(format_output(response, format))
