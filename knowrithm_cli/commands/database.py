"""Database connection management commands."""

from __future__ import annotations

from typing import Optional

import click

from ..utils import load_json_payload, print_json
from .common import auth_kwargs, auth_option, make_client


@click.group(name="database")
def cmd() -> None:
    """Manage database connections."""


@cmd.command("list")
@auth_option()
def list_connections(auth: str) -> None:
    """List database connections owned by the user."""
    client = make_client()
    response = client.get("/api/v1/database-connection", **auth_kwargs(auth))
    print_json(response)


@cmd.command("deleted")
@auth_option()
def deleted_connections(auth: str) -> None:
    """List deleted connections."""
    client = make_client()
    response = client.get("/api/v1/database-connection/deleted", **auth_kwargs(auth))
    print_json(response)


@cmd.command("create")
@auth_option()
@click.option("--payload", required=True, help="JSON payload describing the connection.")
def create_connection(auth: str, payload: str) -> None:
    """Create a new database connection."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post("/api/v1/database-connection", json=body, **auth_kwargs(auth))
    print_json(response)


@cmd.command("get")
@auth_option()
@click.argument("connection_id")
def get_connection(auth: str, connection_id: str) -> None:
    """Get details for a connection."""
    client = make_client()
    response = client.get(f"/api/v1/database-connection/{connection_id}", **auth_kwargs(auth))
    print_json(response)


@cmd.command("delete")
@auth_option()
@click.argument("connection_id")
def delete_connection(auth: str, connection_id: str) -> None:
    """Soft delete a connection."""
    client = make_client()
    response = client.delete(f"/api/v1/database-connection/{connection_id}", **auth_kwargs(auth))
    print_json(response)


@cmd.command("restore")
@auth_option()
@click.argument("connection_id")
def restore_connection(auth: str, connection_id: str) -> None:
    """Restore a deleted connection."""
    client = make_client()
    response = client.patch(
        f"/api/v1/database-connection/{connection_id}/restore",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("test")
@auth_option()
@click.argument("connection_id")
def test_connection(auth: str, connection_id: str) -> None:
    """Test a database connection."""
    client = make_client()
    response = client.post(
        f"/api/v1/database-connection/{connection_id}/test",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("analyze")
@auth_option()
@click.argument("connection_id")
@click.option("--wait/--no-wait", default=False, show_default=True)
def analyze_connection(auth: str, connection_id: str, wait: bool) -> None:
    """Queue semantic analysis for a connection."""
    client = make_client()
    response = client.post(
        f"/api/v1/database-connection/{connection_id}/analyze",
        **auth_kwargs(auth),
    )
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("analyze-all")
@auth_option()
@click.option("--payload", help="Optional JSON payload with filters.")
@click.option("--wait/--no-wait", default=False, show_default=True)
def analyze_all(auth: str, payload: Optional[str], wait: bool) -> None:
    """Analyze all active connections."""
    body = load_json_payload(payload) if payload else None
    client = make_client()
    response = client.post(
        "/api/v1/database-connection/analyze",
        json=body,
        **auth_kwargs(auth),
    )
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("tables")
@auth_option()
@click.argument("connection_id")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=50, type=int)
def list_tables(auth: str, connection_id: str, page: int, per_page: int) -> None:
    """List table metadata for a connection."""
    client = make_client()
    response = client.get(
        f"/api/v1/database-connection/{connection_id}/table",
        params={"page": page, "per_page": per_page},
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("table")
@auth_option()
@click.argument("table_id")
def get_table(auth: str, table_id: str) -> None:
    """Retrieve metadata for a single table."""
    client = make_client()
    response = client.get(
        f"/api/v1/database-connection/table/{table_id}",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("table-delete")
@auth_option()
@click.argument("table_id")
def delete_table(auth: str, table_id: str) -> None:
    """Delete table metadata."""
    client = make_client()
    response = client.delete(
        f"/api/v1/database-connection/table/{table_id}",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("table-restore")
@auth_option()
@click.argument("table_id")
def restore_table(auth: str, table_id: str) -> None:
    """Restore a deleted table metadata record."""
    client = make_client()
    response = client.patch(
        f"/api/v1/database-connection/table/{table_id}/restore",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("semantic-snapshot")
@auth_option()
@click.argument("connection_id")
def semantic_snapshot(auth: str, connection_id: str) -> None:
    """Retrieve the semantic snapshot for a connection."""
    client = make_client()
    response = client.get(
        f"/api/v1/database-connection/{connection_id}/semantic-snapshot",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("knowledge-graph")
@auth_option()
@click.argument("connection_id")
def knowledge_graph(auth: str, connection_id: str) -> None:
    """Retrieve the knowledge graph for a connection."""
    client = make_client()
    response = client.get(
        f"/api/v1/database-connection/{connection_id}/knowledge-graph",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("sample-queries")
@auth_option()
@click.argument("connection_id")
def sample_queries(auth: str, connection_id: str) -> None:
    """Retrieve generated sample queries for a connection."""
    client = make_client()
    response = client.get(
        f"/api/v1/database-connection/{connection_id}/sample-queries",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("text-to-sql")
@auth_option()
@click.argument("connection_id")
@click.option("--payload", required=True, help="JSON payload with natural language question.")
def text_to_sql(auth: str, connection_id: str, payload: str) -> None:
    """Generate SQL from natural language."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post(
        f"/api/v1/database-connection/{connection_id}/text-to-sql",
        json=body,
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("export")
@auth_option()
@click.option("--payload", required=True, help="JSON payload with connection_id and options.")
def export(auth: str, payload: str) -> None:
    """Export database content to documents."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post(
        "/api/v1/database-connection/export",
        json=body,
        **auth_kwargs(auth),
    )
    print_json(response)
