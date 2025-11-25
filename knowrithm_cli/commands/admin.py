"""Admin management commands."""

from __future__ import annotations

from typing import Optional

import click

from ..core.formatters import format_output
from ..utils import load_json_payload
from .common import auth_kwargs, auth_option, format_option, make_client


@click.group(name="admin")
def cmd() -> None:
    """Administrative commands for user and system management."""


@cmd.group(name="users")
def users_cmd() -> None:
    """Manage system users."""


@users_cmd.command("list")
@auth_option()
@format_option()
@click.option("--role", help="Filter by user role (e.g., admin, user).")
@click.option("--status", help="Filter by user status (e.g., active, inactive).")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
def list_users(
    auth: str,
    format: str,
    role: Optional[str],
    status: Optional[str],
    page: int,
    per_page: int
) -> None:
    """List system users."""
    client = make_client()
    params = {"page": page, "per_page": per_page}
    if role:
        params["role"] = role
    if status:
        params["status"] = status
        
    # Try admin endpoint first, falling back if needed
    try:
        response = client.get("/api/v1/admin/users", params=params, **auth_kwargs(auth))
    except Exception:
        try:
            # Fallback to standard users endpoint
            response = client.get("/api/v1/users", params=params, **auth_kwargs(auth))
        except Exception:
            try:
                # Fallback to company users endpoint
                response = client.get("/api/v1/company/users", params=params, **auth_kwargs(auth))
            except Exception:
                try:
                    # Fallback to auth users endpoint
                    response = client.get("/api/v1/auth/users", params=params, **auth_kwargs(auth))
                except Exception:
                    # Fallback to super-admin users endpoint
                    response = client.get("/api/v1/super-admin/users", params=params, **auth_kwargs(auth))
        
    click.echo(format_output(response, format))


@cmd.command("audit-log")
@auth_option()
@format_option()
@click.option("--user-id", help="Filter by user ID.")
@click.option("--action", help="Filter by action type.")
@click.option("--entity-type", help="Filter by entity type (e.g., agent, conversation, auth).")
@click.option("--risk-level", help="Filter by risk level (e.g., low, medium, high).")
@click.option("--start-date", help="Start date for logs.")
@click.option("--end-date", help="End date for logs.")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
def audit_log(
    auth: str,
    format: str,
    user_id: Optional[str],
    action: Optional[str],
    entity_type: Optional[str],
    risk_level: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    page: int,
    per_page: int
) -> None:
    """View system audit logs."""
    client = make_client()
    params = {"page": page, "per_page": per_page}
    if user_id:
        params["user_id"] = user_id
    if action:
        params["action"] = action
    if entity_type:
        params["entity_type"] = entity_type
    if risk_level:
        params["risk_level"] = risk_level
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
        
    try:
        response = client.get("/api/v1/admin/audit-log", params=params, **auth_kwargs(auth))
    except Exception:
        response = client.get("/api/v1/audit-log", params=params, **auth_kwargs(auth))
    
    # Extract audit logs from response
    logs_data = None
    if "data" in response:
        data_field = response["data"]
        if isinstance(data_field, str):
            try:
                import json
                parsed_data = json.loads(data_field)
                # Check if it's a list directly or nested
                if isinstance(parsed_data, list):
                    logs_data = parsed_data
                else:
                    logs_data = parsed_data.get("logs", parsed_data.get("audit_logs", parsed_data.get("data", [])))
            except (json.JSONDecodeError, AttributeError):
                pass
        elif isinstance(data_field, list):
            logs_data = data_field
        elif isinstance(data_field, dict):
            logs_data = data_field.get("logs", data_field.get("audit_logs", []))
    
    # If not found in data field, check if response itself is a list or has logs
    if not logs_data:
        if isinstance(response, list):
            logs_data = response
        else:
            logs_data = response.get("logs", response.get("audit_logs", []))
    
    # Display in a timeline format for better readability
    if logs_data and isinstance(logs_data, list) and format == "table":
        click.echo(f"\n📋 Audit Log ({len(logs_data)} entries)\n")
        click.echo("=" * 100)
        
        for log in logs_data:
            timestamp = log.get("timestamp", log.get("created_at", ""))
            action_type = log.get("event_type", log.get("action", log.get("action_type", "unknown")))
            description = log.get("description", log.get("message", ""))
            entity_type_val = log.get("event_category", log.get("entity_type", ""))
            user_role = log.get("entity", log.get("user_role", ""))
            ip_address = log.get("ip_address", "")
            risk_level_val = log.get("risk_level", "")
            
            # Action type emoji
            action_emoji = "📝"
            if "login" in action_type.lower():
                action_emoji = "🔐"
            elif "delete" in action_type.lower():
                action_emoji = "🗑️"
            elif "create" in action_type.lower():
                action_emoji = "✨"
            elif "update" in action_type.lower():
                action_emoji = "✏️"
            elif "message" in action_type.lower() or "chat" in action_type.lower():
                action_emoji = "💬"
            
            click.echo(f"\n{action_emoji} {action_type}")
            if timestamp:
                click.echo(f"   🕐 {timestamp}")
            if description:
                # Truncate long descriptions
                if len(description) > 150:
                    description = description[:147] + "..."
                click.echo(f"   📄 {description}")
            
            # Additional metadata
            metadata_parts = []
            if user_role:
                metadata_parts.append(f"Entity: {user_role}")
            if entity_type_val:
                metadata_parts.append(f"Category: {entity_type_val}")
            if risk_level_val:
                metadata_parts.append(f"Risk: {risk_level_val}")
            if ip_address:
                metadata_parts.append(f"IP: {ip_address}")
            
            if metadata_parts:
                click.echo(f"   ℹ️  {' | '.join(metadata_parts)}")
            
            click.echo("-" * 100)
    else:
        # Fallback to standard formatting
        click.echo(format_output(response, format))


@cmd.command("metrics")
@auth_option()
@format_option()
def metrics(auth: str, format: str) -> None:
    """View system metrics and statistics."""
    client = make_client()
    
    try:
        response = client.get("/api/v1/admin/metrics", **auth_kwargs(auth))
    except Exception:
        try:
            response = client.get("/api/v1/system/metrics", **auth_kwargs(auth))
        except Exception:
            response = client.get("/api/v1/metrics", **auth_kwargs(auth))
    
    click.echo(format_output(response, format))
