"""Analytics and reporting commands."""

from __future__ import annotations

from typing import Optional

import click

from ..utils import load_json_payload, print_json
from .common import auth_kwargs, auth_option, make_client


@click.group(name="analytics")
def cmd() -> None:
    """Access analytics dashboards and exports."""


@cmd.command("dashboard")
@auth_option()
@click.option("--company-id", help="Optional company ID (super admin).")
def dashboard(auth: str, company_id: Optional[str]) -> None:
    """Retrieve the main analytics dashboard."""
    client = make_client()
    params = {}
    if company_id:
        params["company_id"] = company_id
    response = client.get("/api/v1/analytic/dashboard", params=params, **auth_kwargs(auth))
    print_json(response)


@cmd.command("agent")
@auth_option()
@click.argument("agent_id")
@click.option("--start-date", help="ISO start date.")
@click.option("--end-date", help="ISO end date.")
def agent_analytics(auth: str, agent_id: str, start_date: Optional[str], end_date: Optional[str]) -> None:
    """Retrieve analytics for a single agent."""
    client = make_client()
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    response = client.get(
        f"/api/v1/analytic/agent/{agent_id}",
        params=params,
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("agent-performance")
@auth_option()
@click.argument("agent_id")
@click.option("--start-date")
@click.option("--end-date")
def agent_performance(auth: str, agent_id: str, start_date: Optional[str], end_date: Optional[str]) -> None:
    """Compare agent performance to company averages."""
    client = make_client()
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    response = client.get(
        f"/api/v1/analytic/agent/{agent_id}/performance-comparison",
        params=params,
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("conversation")
@auth_option()
@click.argument("conversation_id")
def conversation_analytics(auth: str, conversation_id: str) -> None:
    """Retrieve analytics for a conversation."""
    client = make_client()
    response = client.get(
        f"/api/v1/analytic/conversation/{conversation_id}",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("leads")
@auth_option()
@click.option("--start-date")
@click.option("--end-date")
@click.option("--company-id", help="Super admin override company ID.")
def leads_analytics(auth: str, start_date: Optional[str], end_date: Optional[str], company_id: Optional[str]) -> None:
    """Retrieve lead analytics."""
    client = make_client()
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if company_id:
        params["company_id"] = company_id
    response = client.get("/api/v1/analytic/leads", params=params, **auth_kwargs(auth))
    print_json(response)


@cmd.command("usage")
@auth_option()
@click.option("--start-date")
@click.option("--end-date")
def usage(auth: str, start_date: Optional[str], end_date: Optional[str]) -> None:
    """Retrieve platform usage analytics."""
    client = make_client()
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    response = client.get("/api/v1/analytic/usage", params=params, **auth_kwargs(auth))
    print_json(response)


@cmd.command("export")
@auth_option()
@click.option("--payload", required=True, help="JSON payload describing the export request.")
def export(auth: str, payload: str) -> None:
    """Export analytics data (conversations, leads, agents, or usage)."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post("/api/v1/analytic/export", json=body, **auth_kwargs(auth))
    print_json(response)
