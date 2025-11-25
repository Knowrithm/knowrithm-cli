"""Analytics and reporting commands."""

from __future__ import annotations

from typing import Optional

import click

from ..core.formatters import format_output
from ..utils import load_json_payload
from .common import auth_kwargs, auth_option, format_option, make_client


@click.group(name="analytics")
def cmd() -> None:
    """Access analytics dashboards and exports."""


@cmd.command("dashboard")
@auth_option()
@format_option(default="json")
@click.option("--company-id", help="Optional company ID (super admin).")
def dashboard(auth: str, format: str, company_id: Optional[str]) -> None:
    """Retrieve the main analytics dashboard."""
    client = make_client()
    params = {}
    if company_id:
        params["company_id"] = company_id
    response = client.get("/api/v1/analytic/dashboard", params=params, **auth_kwargs(auth))
    
    # For table format, provide a summary view instead of full nested data
    if format == "table":
        # Extract key metrics for table display
        summary_data = []
        
        # Core metrics
        if "core_metrics" in response:
            core = response["core_metrics"]
            summary_data.append({
                "Category": "Core Metrics",
                "Conversations": core.get("conversation_count", 0),
                "Documents": core.get("document_count", 0),
                "Leads": core.get("lead_count", 0),
                "Users": core.get("total_users", 0),
                "DB Connections": core.get("connection_count", 0)
            })
        
        # Conversation analytics
        if "conversation_analytics" in response:
            conv = response["conversation_analytics"]
            msg_analytics = conv.get("message_analytics", {})
            summary_data.append({
                "Category": "Conversations",
                "Total Messages": msg_analytics.get("total_messages", 0),
                "Avg Processing Time": f"{msg_analytics.get('average_processing_time', 0):.2f}s",
                "Active": conv.get("conversation_status", {}).get("active", 0),
                "Engaged Leads": conv.get("lead_engagement", {}).get("engaged_leads", 0),
                "Top Conversations": len(conv.get("top_conversations", []))
            })
        
        # Document analytics
        if "document_analytics" in response:
            docs = response["document_analytics"]
            storage = docs.get("storage_analytics", {})
            summary_data.append({
                "Category": "Documents",
                "Total Size (MB)": storage.get("total_size_mb", "0"),
                "Avg Size (MB)": storage.get("average_size_mb", "0"),
                "Total Words": storage.get("total_words", 0),
                "Processed": docs.get("processing_status", {}).get("processed", 0),
                "Processing": docs.get("processing_status", {}).get("processing", 0)
            })
        
        # Lead analytics
        if "lead_analytics" in response:
            leads = response["lead_analytics"]
            consent = leads.get("consent_analytics", {})
            summary_data.append({
                "Category": "Leads",
                "Data Consent": f"{consent.get('data_consent_rate', 0):.1f}%",
                "Marketing Consent": f"{consent.get('marketing_consent_rate', 0):.1f}%",
                "New Status": leads.get("lead_status_distribution", {}).get("new", 0),
                "Sources": ", ".join(leads.get("lead_sources", {}).keys()),
                "Total": consent.get("total_leads", 0)
            })
        
        # Agent analytics
        if "agent_analytics" in response:
            agents = response["agent_analytics"]
            if isinstance(agents, list):
                for agent in agents[:3]:  # Show top 3 agents
                    summary_data.append({
                        "Category": f"Agent: {agent.get('name', 'Unknown')}",
                        "Status": agent.get("status", "N/A"),
                        "Conversations": agent.get("total_conversations", 0),
                        "Messages": agent.get("total_messages", 0),
                        "Avg Rating": f"{agent.get('average_rating', 0):.2f}",
                        "Info": ""
                    })
        
        click.echo(format_output(summary_data, "table"))
    else:
        click.echo(format_output(response, format))


@cmd.command("agent")
@auth_option()
@format_option()
@click.argument("agent_id")
@click.option("--start-date", help="ISO start date.")
@click.option("--end-date", help="ISO end date.")
def agent_analytics(auth: str, format: str, agent_id: str, start_date: Optional[str], end_date: Optional[str]) -> None:
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
    click.echo(format_output(response, format))


@cmd.command("agent-performance")
@auth_option()
@format_option()
@click.argument("agent_id")
@click.option("--start-date")
@click.option("--end-date")
def agent_performance(auth: str, format: str, agent_id: str, start_date: Optional[str], end_date: Optional[str]) -> None:
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
    click.echo(format_output(response, format))


@cmd.command("conversation")
@auth_option()
@format_option()
@click.argument("conversation_id")
def conversation_analytics(auth: str, format: str, conversation_id: str) -> None:
    """Retrieve analytics for a conversation."""
    client = make_client()
    response = client.get(
        f"/api/v1/analytic/conversation/{conversation_id}",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("leads")
@auth_option()
@format_option(default="json")
@click.option("--start-date")
@click.option("--end-date")
@click.option("--days", type=int, help="Number of days to look back (alternative to start-date)")
@click.option("--company-id", help="Super admin override company ID.")
def leads_analytics(auth: str, format: str, start_date: Optional[str], end_date: Optional[str], days: Optional[int], company_id: Optional[str]) -> None:
    """Retrieve lead analytics."""
    client = make_client()
    params = {}
    
    if days:
        from datetime import datetime, timedelta
        end = datetime.now()
        start = end - timedelta(days=days)
        params["start_date"] = start.isoformat()
        params["end_date"] = end.isoformat()
    else:
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
    
    if company_id:
        params["company_id"] = company_id
    response = client.get("/api/v1/analytic/leads", params=params, **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("usage")
@auth_option()
@format_option(default="json")
@click.option("--start-date")
@click.option("--end-date")
def usage(auth: str, format: str, start_date: Optional[str], end_date: Optional[str]) -> None:
    """Retrieve platform usage analytics."""
    client = make_client()
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    response = client.get("/api/v1/analytic/usage", params=params, **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("export")
@auth_option()
@click.option("--payload", help="JSON payload describing the export request.")
@click.option("--type", "export_type", type=click.Choice(["conversations", "leads", "agents", "usage"]), help="Type of data to export")
@click.option("--format", "output_format", type=click.Choice(["csv", "json"]), default="csv", help="Export format")
@click.option("--start-date", help="Start date for export")
@click.option("--end-date", help="End date for export")
def export(
    auth: str,
    payload: Optional[str],
    export_type: Optional[str],
    output_format: str,
    start_date: Optional[str],
    end_date: Optional[str]
) -> None:
    """Export analytics data.
    
    Examples:
        # Export conversations as CSV
        knowrithm analytics export --type conversations --format csv
        
        # Export leads with date range
        knowrithm analytics export --type leads --format json --start-date 2024-01-01
        
        # Custom export with payload
        knowrithm analytics export --payload '{"type": "agents", "format": "csv"}'
    """
    client = make_client()
    
    if payload:
        body = load_json_payload(payload)
    else:
        if not export_type:
            raise click.ClickException("Either --payload or --type is required")
        
        body = {
            "type": export_type,
            "format": output_format
        }
        
        if start_date:
            body["start_date"] = start_date
        if end_date:
            body["end_date"] = end_date
    
    response = client.post("/api/v1/analytic/export", json=body, **auth_kwargs(auth))
    
    # If response is CSV (wrapped in raw dict by client), print directly
    if isinstance(response, dict) and "raw" in response and len(response) == 1:
        click.echo(response["raw"])
    elif isinstance(response, str):
        click.echo(response)
    else:
        click.echo(format_output(response, output_format))
