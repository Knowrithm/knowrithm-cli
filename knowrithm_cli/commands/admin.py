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
@click.option("--start-date", help="Start date for logs.")
@click.option("--end-date", help="End date for logs.")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
def audit_log(
    auth: str,
    format: str,
    user_id: Optional[str],
    action: Optional[str],
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
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
        
    try:
        response = client.get("/api/v1/admin/audit-log", params=params, **auth_kwargs(auth))
    except Exception:
        response = client.get("/api/v1/audit-log", params=params, **auth_kwargs(auth))
        
    click.echo(format_output(response, format))
