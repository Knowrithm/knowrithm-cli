"""Company management commands."""

from __future__ import annotations

from typing import Optional

import click

from ..utils import load_json_payload
from ..core.formatters import format_output
from .common import auth_kwargs, auth_option, format_option, make_client
from .common import auth_kwargs, auth_option, make_client


@click.group(name="company")
def cmd() -> None:
    """Manage tenant/company resources."""


@cmd.command("list")
@auth_option()
@format_option()
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
def list_companies(auth: str, format: str, page: int, per_page: int) -> None:
    """List companies (super admin only)."""
    client = make_client()
    response = client.get(
        "/api/v1/super-admin/company",
        params={"page": page, "per_page": per_page},
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("current")
@auth_option()
@format_option()
def current_company(auth: str, format: str) -> None:
    """Retrieve the authenticated company."""
    client = make_client()
    response = client.get("/api/v1/company", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("get")
@auth_option()
@format_option()
@click.argument("company_id", required=False)
def get_company(auth: str, format: str, company_id: Optional[str]) -> None:
    """Retrieve a specific company by ID.
    
    If no company ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not company_id:
        from ..interactive import select_company
        click.echo("\n🏢 Select a company to view:")
        company_id, _ = select_company(client, message="Select company")
        
    response = client.get(f"/api/v1/company/{company_id}", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("create")
@format_option()
@click.option("--payload", required=True, help="JSON payload or @path describing the company.")
def create_company(format: str, payload: str) -> None:
    """Create a company (public onboarding)."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post(
        "/api/v1/company",
        json=body,
        require_auth=False,
        use_jwt=False,
    )
    click.echo(format_output(response, format))


@cmd.command("update")
@auth_option()
@format_option()
@click.argument("company_id", required=False)
@click.option("--payload", required=True, help="JSON payload with updates.")
def update_company(auth: str, format: str, company_id: Optional[str], payload: str) -> None:
    """Update company metadata.
    
    If no company ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not company_id:
        from ..interactive import select_company
        click.echo("\n✏️  Select a company to update:")
        company_id, _ = select_company(client, message="Select company")
        
    body = load_json_payload(payload)
    response = client.put(
        f"/api/v1/company/{company_id}",
        json=body,
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("patch")
@auth_option()
@format_option()
@click.argument("company_id", required=False)
@click.option("--payload", required=True, help="JSON payload with partial update fields.")
def patch_company(auth: str, format: str, company_id: Optional[str], payload: str) -> None:
    """Partially update a company.
    
    If no company ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not company_id:
        from ..interactive import select_company
        click.echo("\n✏️  Select a company to patch:")
        company_id, _ = select_company(client, message="Select company")
        
    body = load_json_payload(payload)
    response = client.patch(
        f"/api/v1/company/{company_id}",
        json=body,
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("delete")
@auth_option()
@format_option()
@click.argument("company_id", required=False)
def delete_company(auth: str, format: str, company_id: Optional[str]) -> None:
    """Soft delete a company.
    
    If no company ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not company_id:
        from ..interactive import select_company
        click.echo("\n🗑️  Select a company to delete:")
        company_id, _ = select_company(client, message="Select company")
        
    response = client.delete(
        f"/api/v1/company/{company_id}",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("restore")
@auth_option()
@format_option()
@click.argument("company_id", required=False)
def restore_company(auth: str, format: str, company_id: Optional[str]) -> None:
    """Restore a soft-deleted company.
    
    If no company ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not company_id:
        # Try to list deleted companies
        try:
            response = client.get("/api/v1/company/deleted", **auth_kwargs(auth))
            companies = response.get("companies", [])
            if not companies:
                click.echo("❌ No deleted companies found.")
                return
                
            from ..interactive import select_from_dict
            
            def format_comp(comp):
                return f"{comp.get('name', 'Unknown')} (Deleted: {comp.get('deleted_at', 'N/A')})"
                
            click.echo("\n♻️  Select a company to restore:")
            company_id, _ = select_from_dict(
                "Select company to restore",
                companies,
                display_key="name",
                value_key="id",
                format_choice=format_comp
            )
        except Exception as e:
            click.echo(f"❌ Error fetching deleted companies: {e}")
            return

    response = client.patch(
        f"/api/v1/company/{company_id}/restore",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("deleted")
@auth_option()
@format_option()
def deleted_companies(auth: str, format: str) -> None:
    """List deleted companies."""
    client = make_client()
    response = client.get("/api/v1/company/deleted", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("bulk-delete")
@auth_option()
@format_option()
@click.option("--payload", required=True, help="JSON payload with company_ids.")
def bulk_delete(auth: str, format: str, payload: str) -> None:
    """Bulk delete companies."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.delete(
        "/api/v1/company/bulk-delete",
        json=body,
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("bulk-restore")
@auth_option()
@format_option()
@click.option("--payload", required=True, help="JSON payload with company_ids.")
def bulk_restore(auth: str, format: str, payload: str) -> None:
    """Bulk restore companies."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.patch(
        "/api/v1/company/bulk-restore",
        json=body,
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("statistics")
@auth_option()
@format_option()
@click.argument("company_id", required=False)
@click.option("--days", type=int, help="Number of days to include.")
def statistics(auth: str, format: str, company_id: Optional[str], days: Optional[int]) -> None:
    """Retrieve lead statistics for a company.
    
    If no company ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not company_id:
        from ..interactive import select_company
        click.echo("\n📊 Select a company to view statistics:")
        company_id, _ = select_company(client, message="Select company")
        
    params = {}
    if days is not None:
        params["days"] = days
    path = "/api/v1/company/statistics"
    if company_id:
        path = f"/api/v1/company/{company_id}/statistics"
    response = client.get(path, params=params, **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("related-data")
@auth_option()
@format_option()
@click.argument("company_id", required=False)
def related_data(auth: str, format: str, company_id: Optional[str]) -> None:
    """Inspect related data counts before deletion.
    
    If no company ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not company_id:
        from ..interactive import select_company
        click.echo("\n🔍 Select a company to view related data:")
        company_id, _ = select_company(client, message="Select company")
        
    response = client.get(
        f"/api/v1/company/{company_id}/related-data",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("cascade-delete")
@auth_option()
@format_option()
@click.argument("company_id", required=False)
@click.option("--payload", help="Optional JSON payload with cascade options.")
def cascade_delete(auth: str, format: str, company_id: Optional[str], payload: Optional[str]) -> None:
    """Trigger cascade deletion for a company (super admin).
    
    If no company ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not company_id:
        from ..interactive import select_company
        click.echo("\n💥 Select a company to cascade delete:")
        company_id, _ = select_company(client, message="Select company")
        
    body = load_json_payload(payload) if payload else None
    response = client.delete(
        f"/api/v1/company/{company_id}/cascade-delete",
        json=body,
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))
