"""Company management commands."""

from __future__ import annotations

from typing import Optional

import click

from ..utils import load_json_payload, print_json
from .common import auth_kwargs, auth_option, make_client


@click.group(name="company")
def cmd() -> None:
    """Manage tenant/company resources."""


@cmd.command("list")
@auth_option()
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
def list_companies(auth: str, page: int, per_page: int) -> None:
    """List companies (super admin only)."""
    client = make_client()
    response = client.get(
        "/api/v1/super-admin/company",
        params={"page": page, "per_page": per_page},
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("current")
@auth_option()
def current_company(auth: str) -> None:
    """Retrieve the authenticated company."""
    client = make_client()
    response = client.get("/api/v1/company", **auth_kwargs(auth))
    print_json(response)


@cmd.command("get")
@auth_option()
@click.argument("company_id")
def get_company(auth: str, company_id: str) -> None:
    """Retrieve a specific company by ID."""
    client = make_client()
    response = client.get(f"/api/v1/company/{company_id}", **auth_kwargs(auth))
    print_json(response)


@cmd.command("create")
@click.option("--payload", required=True, help="JSON payload or @path describing the company.")
def create_company(payload: str) -> None:
    """Create a company (public onboarding)."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post(
        "/api/v1/company",
        json=body,
        require_auth=False,
        use_jwt=False,
    )
    print_json(response)


@cmd.command("update")
@auth_option()
@click.argument("company_id")
@click.option("--payload", required=True, help="JSON payload with updates.")
def update_company(auth: str, company_id: str, payload: str) -> None:
    """Update company metadata."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.put(
        f"/api/v1/company/{company_id}",
        json=body,
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("patch")
@auth_option()
@click.argument("company_id")
@click.option("--payload", required=True, help="JSON payload with partial update fields.")
def patch_company(auth: str, company_id: str, payload: str) -> None:
    """Partially update a company."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.patch(
        f"/api/v1/company/{company_id}",
        json=body,
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("delete")
@auth_option()
@click.argument("company_id")
def delete_company(auth: str, company_id: str) -> None:
    """Soft delete a company."""
    client = make_client()
    response = client.delete(
        f"/api/v1/company/{company_id}",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("restore")
@auth_option()
@click.argument("company_id")
def restore_company(auth: str, company_id: str) -> None:
    """Restore a soft-deleted company."""
    client = make_client()
    response = client.patch(
        f"/api/v1/company/{company_id}/restore",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("deleted")
@auth_option()
def deleted_companies(auth: str) -> None:
    """List deleted companies."""
    client = make_client()
    response = client.get("/api/v1/company/deleted", **auth_kwargs(auth))
    print_json(response)


@cmd.command("bulk-delete")
@auth_option()
@click.option("--payload", required=True, help="JSON payload with company_ids.")
def bulk_delete(auth: str, payload: str) -> None:
    """Bulk delete companies."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.delete(
        "/api/v1/company/bulk-delete",
        json=body,
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("bulk-restore")
@auth_option()
@click.option("--payload", required=True, help="JSON payload with company_ids.")
def bulk_restore(auth: str, payload: str) -> None:
    """Bulk restore companies."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.patch(
        "/api/v1/company/bulk-restore",
        json=body,
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("statistics")
@auth_option()
@click.argument("company_id", required=False)
@click.option("--days", type=int, help="Number of days to include.")
def statistics(auth: str, company_id: Optional[str], days: Optional[int]) -> None:
    """Retrieve lead statistics for a company."""
    client = make_client()
    params = {}
    if days is not None:
        params["days"] = days
    path = "/api/v1/company/statistics"
    if company_id:
        path = f"/api/v1/company/{company_id}/statistics"
    response = client.get(path, params=params, **auth_kwargs(auth))
    print_json(response)


@cmd.command("related-data")
@auth_option()
@click.argument("company_id")
def related_data(auth: str, company_id: str) -> None:
    """Inspect related data counts before deletion."""
    client = make_client()
    response = client.get(
        f"/api/v1/company/{company_id}/related-data",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("cascade-delete")
@auth_option()
@click.argument("company_id")
@click.option("--payload", help="Optional JSON payload with cascade options.")
def cascade_delete(auth: str, company_id: str, payload: Optional[str]) -> None:
    """Trigger cascade deletion for a company (super admin)."""
    body = load_json_payload(payload) if payload else None
    client = make_client()
    response = client.delete(
        f"/api/v1/company/{company_id}/cascade-delete",
        json=body,
        **auth_kwargs(auth),
    )
    print_json(response)
