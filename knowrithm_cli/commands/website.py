"""Website awareness and crawling commands."""

from __future__ import annotations

from typing import Optional

import click

from ..core.formatters import format_output
from ..core.name_resolver import NameResolver
from ..utils import load_json_payload
from .common import auth_kwargs, auth_option, format_option, make_client


@click.group(name="website")
def cmd() -> None:
    """Manage website sources and crawling."""


@cmd.command("list")
@auth_option()
@format_option()
@click.option("--agent-id", help="Filter by agent ID.")
def list_sources(auth: str, format: str, agent_id: Optional[str]) -> None:
    """List website sources."""
    client = make_client()
    params = {}
    if agent_id:
        params["agent_id"] = agent_id
    response = client.get("/api/v1/website/source", params=params, **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("agent")
@auth_option()
@format_option()
@click.argument("agent_id_or_name", required=False)
def agent_sources(auth: str, format: str, agent_id_or_name: Optional[str]) -> None:
    """List website sources for an agent (by name or ID).
    
    If no agent ID/name is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not agent_id_or_name:
        from ..interactive import select_agent
        click.echo("\n🤖 Select an agent to list sources for:")
        agent_id_or_name, _ = select_agent(client, message="Select agent")
        
    resolver = NameResolver(client)
    
    # Resolve agent name to ID
    agent_id = resolver.resolve_agent(agent_id_or_name)
    
    response = client.get(
        f"/api/v1/website/agent/{agent_id}/sources",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("get")
@auth_option()
@format_option()
@click.argument("source_id", required=False)
def get_source(auth: str, format: str, source_id: Optional[str]) -> None:
    """Retrieve a website source by ID.
    
    If no source ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not source_id:
        from ..interactive import select_website_source
        click.echo("\n🌐 Select a website source to view:")
        source_id, _ = select_website_source(client, message="Select source")
        
    response = client.get(f"/api/v1/website/{source_id}", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("create")
@auth_option()
@format_option()
@click.option("--payload", required=True, help="JSON payload describing the source.")
def create_source(auth: str, format: str, payload: str) -> None:
    """Create a new website source."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post(
        "/api/v1/website/source",
        json=body,
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("update")
@auth_option()
@format_option()
@click.argument("source_id", required=False)
@click.option("--payload", required=True, help="JSON payload with updates.")
def update_source(auth: str, format: str, source_id: Optional[str], payload: str) -> None:
    """Update a website source.
    
    If no source ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not source_id:
        from ..interactive import select_website_source
        click.echo("\n✏️  Select a website source to update:")
        source_id, _ = select_website_source(client, message="Select source")
        
    body = load_json_payload(payload)
    response = client.put(
        f"/api/v1/website/source/{source_id}",
        json=body,
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("delete")
@auth_option()
@format_option()
@click.argument("source_id", required=False)
@click.option("--wait/--no-wait", default=False, show_default=True)
def delete_source(auth: str, format: str, source_id: Optional[str], wait: bool) -> None:
    """Delete a website source.
    
    If no source ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not source_id:
        from ..interactive import select_website_source
        click.echo("\n🗑️  Select a website source to delete:")
        source_id, _ = select_website_source(client, message="Select source")
        
    response = client.delete(
        f"/api/v1/website/source/{source_id}",
        **auth_kwargs(auth),
    )
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    click.echo(format_output(response, format))


@cmd.command("crawl")
@auth_option()
@format_option()
@click.argument("source_id", required=False)
@click.option("--payload", help="Optional JSON payload (e.g., max_pages).")
@click.option("--wait/--no-wait", default=False, show_default=True)
def crawl(auth: str, format: str, source_id: Optional[str], payload: Optional[str], wait: bool) -> None:
    """Trigger a crawl job for a website source.
    
    If no source ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not source_id:
        from ..interactive import select_website_source
        click.echo("\n🕷️  Select a website source to crawl:")
        source_id, _ = select_website_source(client, message="Select source")
        
    body = load_json_payload(payload) if payload else None
    response = client.post(
        f"/api/v1/website/source/{source_id}/crawl",
        json=body,
        **auth_kwargs(auth),
    )
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    click.echo(format_output(response, format))


@cmd.command("pages")
@auth_option()
@format_option()
@click.argument("source_id", required=False)
def list_pages(auth: str, format: str, source_id: Optional[str]) -> None:
    """List pages discovered for a source.
    
    If no source ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not source_id:
        from ..interactive import select_website_source
        click.echo("\n📄 Select a website source to list pages:")
        source_id, _ = select_website_source(client, message="Select source")
        
    response = client.get(
        f"/api/v1/website/source/{source_id}/pages",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("handshake")
@format_option()
@click.option("--payload", required=True, help="JSON payload describing the widget handshake.")
def handshake(format: str, payload: str) -> None:
    """Call the widget handshake endpoint (unauthenticated)."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post(
        "/api/v1/website/handshake",
        json=body,
        require_auth=False,
        use_jwt=False,
    )
    click.echo(format_output(response, format))
