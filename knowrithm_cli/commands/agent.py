"""Agent management commands."""

from __future__ import annotations

from typing import Optional

import click

from ..utils import load_json_payload, print_json
from .common import auth_kwargs, auth_option, make_client


@click.group(name="agent")
def cmd() -> None:
    """Manage Knowrithm agents."""


@cmd.command("list")
@auth_option()
@click.option("--company-id", help="Filter by company ID (super admin only).")
@click.option("--status", help="Filter by agent status.")
@click.option("--search", help="Search string for name/description.")
@click.option("--page", default=1, type=int, show_default=True)
@click.option("--per-page", default=20, type=int, show_default=True)
def list_agents(
    auth: str,
    company_id: Optional[str],
    status: Optional[str],
    search: Optional[str],
    page: int,
    per_page: int,
) -> None:
    """List agents for the authenticated company."""
    client = make_client()
    params = {
        "page": page,
        "per_page": per_page,
    }
    if company_id:
        params["company_id"] = company_id
    if status:
        params["status"] = status
    if search:
        params["search"] = search
    response = client.get("/api/v1/agent", params=params, **auth_kwargs(auth))
    print_json(response)


@cmd.command("get")
@auth_option()
@click.argument("agent_id")
def get_agent(auth: str, agent_id: str) -> None:
    """Retrieve a specific agent by ID."""
    client = make_client()
    response = client.get(f"/api/v1/agent/{agent_id}", **auth_kwargs(auth))
    print_json(response)


@cmd.command("create")
@auth_option()
@click.option("--payload", required=True, help="JSON string or @path describing the agent.")
@click.option("--wait/--no-wait", default=True, show_default=True)
def create_agent(auth: str, payload: str, wait: bool) -> None:
    """Create a new agent."""
    body = load_json_payload(payload)
    if not isinstance(body, dict):
        raise click.ClickException("Agent payload must be a JSON object.")
    client = make_client()
    response = client.post("/api/v1/agent", json=body, **auth_kwargs(auth))
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("clone")
@auth_option()
@click.argument("agent_id")
@click.option("--payload", help="Optional JSON overrides for the cloned agent.")
@click.option("--wait/--no-wait", default=True, show_default=True)
def clone_agent(auth: str, agent_id: str, payload: Optional[str], wait: bool) -> None:
    """Clone an existing agent."""
    body = load_json_payload(payload) if payload else None
    client = make_client()
    response = client.post(f"/api/v1/agent/{agent_id}/clone", json=body, **auth_kwargs(auth))
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("update")
@auth_option()
@click.argument("agent_id")
@click.option("--payload", required=True, help="JSON string or @path with update fields.")
@click.option("--wait/--no-wait", default=True, show_default=True)
def update_agent(auth: str, agent_id: str, payload: str, wait: bool) -> None:
    """Update an agent."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.put(f"/api/v1/agent/{agent_id}", json=body, **auth_kwargs(auth))
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("delete")
@auth_option()
@click.argument("agent_id")
@click.option("--wait/--no-wait", default=False, show_default=True)
def delete_agent(auth: str, agent_id: str, wait: bool) -> None:
    """Soft delete an agent."""
    client = make_client()
    response = client.delete(f"/api/v1/agent/{agent_id}", **auth_kwargs(auth))
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("restore")
@auth_option()
@click.argument("agent_id")
@click.option("--wait/--no-wait", default=False, show_default=True)
def restore_agent(auth: str, agent_id: str, wait: bool) -> None:
    """Restore a soft-deleted agent."""
    client = make_client()
    response = client.patch(f"/api/v1/agent/{agent_id}/restore", **auth_kwargs(auth))
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("stats")
@auth_option()
@click.argument("agent_id")
def agent_stats(auth: str, agent_id: str) -> None:
    """Retrieve statistics for an agent."""
    client = make_client()
    response = client.get(f"/api/v1/agent/{agent_id}/stats", **auth_kwargs(auth))
    print_json(response)


@cmd.command("test")
@auth_option()
@click.argument("agent_id")
@click.option("--payload", help="Optional JSON test payload.")
@click.option("--wait/--no-wait", default=True, show_default=True)
def test_agent(auth: str, agent_id: str, payload: Optional[str], wait: bool) -> None:
    """Run a test query against an agent."""
    body = load_json_payload(payload) if payload else None
    client = make_client()
    response = client.post(
        f"/api/v1/agent/{agent_id}/test",
        json=body,
        **auth_kwargs(auth),
    )
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("embed-code")
@auth_option()
@click.argument("agent_id")
def embed_code(auth: str, agent_id: str) -> None:
    """Fetch widget embed code for an agent."""
    client = make_client()
    response = client.get(f"/api/v1/agent/{agent_id}/embed-code", **auth_kwargs(auth))
    print_json(response)

