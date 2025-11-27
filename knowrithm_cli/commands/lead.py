"""Lead management commands."""

from __future__ import annotations

from typing import Optional

import click

from ..core.formatters import format_output
from ..utils import load_json_payload
from .common import auth_kwargs, auth_option, format_option, make_client


@click.group(name="lead")
def cmd() -> None:
    """Manage leads and registrations."""


@cmd.command("register")
@format_option()
@click.option("--payload", required=True, help="JSON payload for public lead registration.")
def register(format: str, payload: str) -> None:
    """Public lead registration (no authentication required)."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post(
        "/api/v1/lead/register",
        json=body,
        require_auth=False,
        use_jwt=False,
    )
    click.echo(format_output(response, format))


@cmd.command("create")
@auth_option()
@format_option()
@click.option("--payload", required=True, help="JSON payload describing the lead.")
def create(auth: str, format: str, payload: str) -> None:
    """Create a lead within the authenticated company."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post("/api/v1/lead", json=body, **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("list")
@auth_option()
@format_option()
@click.option("--status", help="Filter by lead status.")
@click.option("--search", help="Search by name/email.")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
def list_leads(auth: str, format: str, status: Optional[str], search: Optional[str], page: int, per_page: int) -> None:
    """List company leads."""
    client = make_client()
    params = {"page": page, "per_page": per_page}
    if status:
        params["status"] = status
    if search:
        params["search"] = search
    response = client.get("/api/v1/lead/company", params=params, **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("get")
@auth_option()
@format_option()
@click.argument("lead_id", required=False)
def get_lead(auth: str, format: str, lead_id: Optional[str]) -> None:
    """Retrieve a specific lead.
    
    If no lead ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not lead_id:
        from ..interactive import select_lead
        click.echo("\n👤 Select a lead to view:")
        lead_id, _ = select_lead(client, message="Select lead")
        
    response = client.get(f"/api/v1/lead/{lead_id}", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("update")
@auth_option()
@format_option()
@click.argument("lead_id", required=False)
@click.option("--payload", required=True, help="JSON payload with fields to update.")
def update_lead(auth: str, format: str, lead_id: Optional[str], payload: str) -> None:
    """Update a lead.
    
    If no lead ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not lead_id:
        from ..interactive import select_lead
        click.echo("\n✏️  Select a lead to update:")
        lead_id, _ = select_lead(client, message="Select lead")
        
    body = load_json_payload(payload)
    response = client.put(
        f"/api/v1/lead/{lead_id}",
        json=body,
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("delete")
@auth_option()
@format_option()
@click.argument("lead_id", required=False)
def delete_lead(auth: str, format: str, lead_id: Optional[str]) -> None:
    """Delete (soft delete) a lead.
    
    If no lead ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not lead_id:
        from ..interactive import select_lead
        click.echo("\n🗑️  Select a lead to delete:")
        lead_id, _ = select_lead(client, message="Select lead")
        
    response = client.delete(f"/api/v1/lead/{lead_id}", **auth_kwargs(auth))
    click.echo(format_output(response, format))
