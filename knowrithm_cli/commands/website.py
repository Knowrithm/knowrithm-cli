"""Website awareness and crawling commands."""

from __future__ import annotations

from typing import Optional

import click

from ..utils import load_json_payload, print_json
from .common import auth_kwargs, auth_option, make_client


@click.group(name="website")
def cmd() -> None:
    """Manage website sources and crawling."""


@cmd.command("list")
@auth_option()
@click.option("--agent-id", help="Filter by agent ID.")
def list_sources(auth: str, agent_id: Optional[str]) -> None:
    """List website sources."""
    client = make_client()
    params = {}
    if agent_id:
        params["agent_id"] = agent_id
    response = client.get("/api/v1/website/source", params=params, **auth_kwargs(auth))
    print_json(response)


@cmd.command("agent")
@auth_option()
@click.argument("agent_id")
def agent_sources(auth: str, agent_id: str) -> None:
    """List website sources for an agent."""
    client = make_client()
    response = client.get(
        f"/api/v1/website/agent/{agent_id}/sources",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("register")
@auth_option()
@click.option("--payload", required=True, help="JSON payload describing the website source.")
def register_source(auth: str, payload: str) -> None:
    """Register a website source for crawling."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post(
        "/api/v1/website/source",
        json=body,
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("crawl")
@auth_option()
@click.argument("source_id")
@click.option("--payload", help="Optional JSON payload (e.g., max_pages).")
@click.option("--wait/--no-wait", default=False, show_default=True)
def crawl(auth: str, source_id: str, payload: Optional[str], wait: bool) -> None:
    """Trigger a crawl job for a website source."""
    body = load_json_payload(payload) if payload else None
    client = make_client()
    response = client.post(
        f"/api/v1/website/source/{source_id}/crawl",
        json=body,
        **auth_kwargs(auth),
    )
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("pages")
@auth_option()
@click.argument("source_id")
def list_pages(auth: str, source_id: str) -> None:
    """List pages discovered for a source."""
    client = make_client()
    response = client.get(
        f"/api/v1/website/source/{source_id}/pages",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("delete")
@auth_option()
@click.argument("source_id")
@click.option("--wait/--no-wait", default=False, show_default=True)
def delete_source(auth: str, source_id: str, wait: bool) -> None:
    """Delete a website source."""
    client = make_client()
    response = client.delete(
        f"/api/v1/website/source/{source_id}",
        **auth_kwargs(auth),
    )
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("handshake")
@click.option("--payload", required=True, help="JSON payload describing the widget handshake.")
def handshake(payload: str) -> None:
    """Call the widget handshake endpoint (unauthenticated)."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post(
        "/api/v1/website/handshake",
        json=body,
        require_auth=False,
        use_jwt=False,
    )
    print_json(response)

