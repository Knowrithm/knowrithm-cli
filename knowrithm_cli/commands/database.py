"""Database connection management commands."""

from __future__ import annotations

from typing import Optional

import click

from ..core.formatters import format_output
from ..utils import load_json_payload
from .common import auth_kwargs, auth_option, format_option, make_client


@click.group(name="database")
def cmd() -> None:
    """Manage database connections."""


@cmd.command("list")
@auth_option()
@format_option()
def list_connections(auth: str, format: str) -> None:
    """List database connections owned by the user."""
    client = make_client()
    response = client.get("/api/v1/database-connection", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("deleted")
@auth_option()
@format_option()
def deleted_connections(auth: str, format: str) -> None:
    """List deleted connections."""
    client = make_client()
    response = client.get("/api/v1/database-connection/deleted", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("create")
@auth_option()
@format_option()
@click.option("--payload", required=True, help="JSON payload describing the connection.")
def create_connection(auth: str, format: str, payload: str) -> None:
    """Create a new database connection."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post("/api/v1/database-connection", json=body, **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("get")
@auth_option()
@format_option()
@click.argument("connection_id", required=False)
def get_connection(auth: str, format: str, connection_id: Optional[str]) -> None:
    """Get details for a connection.
    
    If no connection ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not connection_id:
        from ..interactive import select_database
        click.echo("\n🔍 Select a database connection to view:")
        connection_id, _ = select_database(client, message="Select connection")
        
    response = client.get(f"/api/v1/database-connection/{connection_id}", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("delete")
@auth_option()
@format_option()
@click.argument("connection_id", required=False)
def delete_connection(auth: str, format: str, connection_id: Optional[str]) -> None:
    """Soft delete a connection.
    
    If no connection ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not connection_id:
        from ..interactive import select_database
        click.echo("\n🗑️  Select a database connection to delete:")
        connection_id, _ = select_database(client, message="Select connection")
        
    response = client.delete(f"/api/v1/database-connection/{connection_id}", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("restore")
@auth_option()
@format_option()
@click.argument("connection_id", required=False)
def restore_connection(auth: str, format: str, connection_id: Optional[str]) -> None:
    """Restore a deleted connection.
    
    If no connection ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not connection_id:
        # Try to list deleted connections
        try:
            response = client.get("/api/v1/database-connection/deleted", **auth_kwargs(auth))
            connections = response.get("connections", [])
            if not connections:
                click.echo("❌ No deleted connections found.")
                return
                
            from ..interactive import select_from_dict
            
            def format_conn(conn):
                return f"{conn.get('name', 'Unknown')} (Deleted: {conn.get('deleted_at', 'N/A')})"
                
            click.echo("\n♻️  Select a connection to restore:")
            connection_id, _ = select_from_dict(
                "Select connection to restore",
                connections,
                display_key="name",
                value_key="id",
                format_choice=format_conn
            )
        except Exception as e:
            click.echo(f"❌ Error fetching deleted connections: {e}")
            return

    response = client.patch(
        f"/api/v1/database-connection/{connection_id}/restore",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("test")
@auth_option()
@format_option()
@click.argument("connection_id", required=False)
def test_connection(auth: str, format: str, connection_id: Optional[str]) -> None:
    """Test a database connection.
    
    If no connection ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not connection_id:
        from ..interactive import select_database
        click.echo("\n🧪 Select a database connection to test:")
        connection_id, _ = select_database(client, message="Select connection")
        
    response = client.post(
        f"/api/v1/database-connection/{connection_id}/test",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("analyze")
@auth_option()
@format_option()
@click.argument("connection_id", required=False)
@click.option("--wait/--no-wait", default=False, show_default=True)
def analyze_connection(auth: str, format: str, connection_id: Optional[str], wait: bool) -> None:
    """Queue semantic analysis for a connection.
    
    If no connection ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not connection_id:
        from ..interactive import select_database
        click.echo("\n🧠 Select a database connection to analyze:")
        connection_id, _ = select_database(client, message="Select connection")
        
    response = client.post(
        f"/api/v1/database-connection/{connection_id}/analyze",
        **auth_kwargs(auth),
    )
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    click.echo(format_output(response, format))


@cmd.command("analyze-all")
@auth_option()
@format_option()
@click.option("--payload", help="Optional JSON payload with filters.")
@click.option("--wait/--no-wait", default=False, show_default=True)
def analyze_all(auth: str, format: str, payload: Optional[str], wait: bool) -> None:
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
    click.echo(format_output(response, format))


@cmd.command("tables")
@auth_option()
@format_option()
@click.argument("connection_id", required=False)
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=50, type=int)
def list_tables(auth: str, format: str, connection_id: Optional[str], page: int, per_page: int) -> None:
    """List table metadata for a connection.
    
    If no connection ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not connection_id:
        from ..interactive import select_database
        click.echo("\n📋 Select a database connection to view tables:")
        connection_id, _ = select_database(client, message="Select connection")
        
    response = client.get(
        f"/api/v1/database-connection/{connection_id}/table",
        params={"page": page, "per_page": per_page},
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("table")
@auth_option()
@format_option()
@click.argument("table_id")
def get_table(auth: str, format: str, table_id: str) -> None:
    """Retrieve metadata for a single table."""
    client = make_client()
    response = client.get(
        f"/api/v1/database-connection/table/{table_id}",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("table-delete")
@auth_option()
@format_option()
@click.argument("table_id")
def delete_table(auth: str, format: str, table_id: str) -> None:
    """Delete table metadata."""
    client = make_client()
    response = client.delete(
        f"/api/v1/database-connection/table/{table_id}",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("table-restore")
@auth_option()
@format_option()
@click.argument("table_id")
def restore_table(auth: str, format: str, table_id: str) -> None:
    """Restore a deleted table metadata record."""
    client = make_client()
    response = client.patch(
        f"/api/v1/database-connection/table/{table_id}/restore",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("semantic-snapshot")
@auth_option()
@format_option()
@click.argument("connection_id", required=False)
def semantic_snapshot(auth: str, format: str, connection_id: Optional[str]) -> None:
    """Retrieve the semantic snapshot for a connection.
    
    If no connection ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not connection_id:
        from ..interactive import select_database
        click.echo("\n📸 Select a database connection to view snapshot:")
        connection_id, _ = select_database(client, message="Select connection")
        
    response = client.get(
        f"/api/v1/database-connection/{connection_id}/semantic-snapshot",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("knowledge-graph")
@auth_option()
@format_option()
@click.argument("connection_id", required=False)
def knowledge_graph(auth: str, format: str, connection_id: Optional[str]) -> None:
    """Retrieve the knowledge graph for a connection.
    
    If no connection ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not connection_id:
        from ..interactive import select_database
        click.echo("\n🕸️  Select a database connection to view knowledge graph:")
        connection_id, _ = select_database(client, message="Select connection")
        
    response = client.get(
        f"/api/v1/database-connection/{connection_id}/knowledge-graph",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("sample-queries")
@auth_option()
@format_option()
@click.argument("connection_id", required=False)
def sample_queries(auth: str, format: str, connection_id: Optional[str]) -> None:
    """Retrieve generated sample queries for a connection.
    
    If no connection ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not connection_id:
        from ..interactive import select_database
        click.echo("\n❓ Select a database connection to view sample queries:")
        connection_id, _ = select_database(client, message="Select connection")
        
    response = client.get(
        f"/api/v1/database-connection/{connection_id}/sample-queries",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("text-to-sql")
@auth_option()
@format_option()
@click.argument("connection_id", required=False)
@click.option("--payload", help="JSON payload with natural language question.")
@click.option("--question", "-q", help="Natural language question (alternative to --payload)")
def text_to_sql(auth: str, format: str, connection_id: Optional[str], payload: Optional[str], question: Optional[str]) -> None:
    """Generate SQL from natural language.
    
    If no connection ID is provided, an interactive selection menu will be shown.
    """
    client = make_client()
    
    if not connection_id:
        from ..interactive import select_database
        click.echo("\n🗣️  Select a database connection to query:")
        connection_id, _ = select_database(client, message="Select connection")
        
    if question:
        body = {"question": question}
    elif payload:
        body = load_json_payload(payload)
    else:
        # Interactive question input
        from ..interactive import text_input
        click.echo("\n❓ Enter your question:")
        q = text_input("Question")
        body = {"question": q}
        
    response = client.post(
        f"/api/v1/database-connection/{connection_id}/text-to-sql",
        json=body,
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("export")
@auth_option()
@format_option()
@click.option("--payload", required=True, help="JSON payload with connection_id and options.")
def export(auth: str, format: str, payload: str) -> None:
    """Export database content to documents."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post(
        "/api/v1/database-connection/export",
        json=body,
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))
