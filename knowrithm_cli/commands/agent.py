"""Enhanced agent management commands with name resolution and interactive features."""

from __future__ import annotations

from typing import Optional

import click

from ..client import KnowrithmClient
from ..core import get_context, NameResolver, format_output
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
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table", "csv", "yaml"], case_sensitive=False),
    default="table",
    show_default=True,
    help="Output format",
)
def list_agents(
    auth: str,
    company_id: Optional[str],
    status: Optional[str],
    search: Optional[str],
    page: int,
    per_page: int,
    output_format: str,
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
    
    # Format output
    output = format_output(response, output_format)
    click.echo(output)


@cmd.command("get")
@auth_option()
@click.argument("agent_name_or_id")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table", "tree", "yaml"], case_sensitive=False),
    default="json",
    show_default=True,
    help="Output format",
)
def get_agent(auth: str, agent_name_or_id: str, output_format: str) -> None:
    """Retrieve a specific agent by name or ID."""
    client = make_client()
    resolver = NameResolver(client)
    
    try:
        agent_id = resolver.resolve_agent(agent_name_or_id)
    except click.ClickException as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    
    response = client.get(f"/api/v1/agent/{agent_id}", **auth_kwargs(auth))
    
    # Format output
    if output_format == "tree":
        output = format_output(response, output_format, title=f"Agent: {agent_name_or_id}")
    else:
        output = format_output(response, output_format)
    click.echo(output)


@cmd.command("create")
@auth_option()
@click.option("--payload", help="JSON string or @path describing the agent.")
@click.option("--name", help="Agent name (interactive mode)")
@click.option("--description", help="Agent description (interactive mode)")
@click.option("--wait/--no-wait", default=True, show_default=True)
@click.option("--interactive", "-i", is_flag=True, help="Interactive creation mode")
def create_agent(
    auth: str,
    payload: Optional[str],
    name: Optional[str],
    description: Optional[str],
    wait: bool,
    interactive: bool,
) -> None:
    """Create a new agent.
    
    Examples:
        # Interactive mode
        knowrithm agent create --interactive
        
        # Quick create with name
        knowrithm agent create --name "Support Bot" --description "Customer support agent"
        
        # From JSON payload
        knowrithm agent create --payload '{"name": "Sales Bot", "description": "Sales assistant"}'
        
        # From file
        knowrithm agent create --payload @agent-config.json
    """
    client = make_client()
    
    # Determine creation mode
    if interactive or (not payload and not name):
        # Interactive mode
        body = _interactive_agent_creation()
    elif payload:
        # Payload mode
        body = load_json_payload(payload)
        if not isinstance(body, dict):
            raise click.ClickException("Agent payload must be a JSON object.")
    else:
        # Quick create mode
        body = {}
        if name:
            body["name"] = name
        if description:
            body["description"] = description
        
        if not body.get("name"):
            raise click.ClickException("Agent name is required. Use --name or --interactive.")
    
    response = client.post("/api/v1/agent", json=body, **auth_kwargs(auth))
    
    if response.get("task_id"):
        if wait:
            click.echo("Creating agent... (this may take a moment)")
        response = client.handle_async_response(response, wait=wait)
    
    # Set as active agent if successful
    if response.get("id"):
        ctx = get_context()
        ctx.set_agent(response["id"], response.get("name"))
        click.echo(f"✓ Agent created and set as active: {response.get('name')}", err=True)
    
    print_json(response)


def _interactive_agent_creation() -> dict:
    """Interactive wizard for agent creation."""
    click.echo("=== Create New Agent ===\n")
    
    name = click.prompt("Agent name", type=str)
    description = click.prompt("Description", default="", show_default=False)
    
    # Optional fields
    if click.confirm("Configure advanced settings?", default=False):
        status = click.prompt(
            "Status",
            type=click.Choice(["active", "inactive", "training"], case_sensitive=False),
            default="active",
        )
        
        # Personality traits
        if click.confirm("Add personality traits?", default=False):
            traits = click.prompt("Personality traits (comma-separated)", default="")
            personality_traits = [t.strip() for t in traits.split(",") if t.strip()]
        else:
            personality_traits = None
        
        # Capabilities
        if click.confirm("Add capabilities?", default=False):
            caps = click.prompt("Capabilities (comma-separated)", default="")
            capabilities = [c.strip() for c in caps.split(",") if c.strip()]
        else:
            capabilities = None
        
        body = {
            "name": name,
            "description": description,
            "status": status,
        }
        
        if personality_traits:
            body["personality_traits"] = personality_traits
        if capabilities:
            body["capabilities"] = capabilities
    else:
        body = {
            "name": name,
            "description": description,
        }
    
    return body


@cmd.command("update")
@auth_option()
@click.argument("agent_name_or_id")
@click.option("--payload", help="JSON string or @path with update fields.")
@click.option("--name", help="New agent name")
@click.option("--description", help="New description")
@click.option("--status", type=click.Choice(["active", "inactive", "training"]), help="New status")
@click.option("--wait/--no-wait", default=True, show_default=True)
def update_agent(
    auth: str,
    agent_name_or_id: str,
    payload: Optional[str],
    name: Optional[str],
    description: Optional[str],
    status: Optional[str],
    wait: bool,
) -> None:
    """Update an agent by name or ID.
    
    Examples:
        # Update name
        knowrithm agent update "Support Bot" --name "Customer Support Bot"
        
        # Update status
        knowrithm agent update "Support Bot" --status inactive
        
        # Update from JSON
        knowrithm agent update "Support Bot" --payload '{"description": "New description"}'
    """
    client = make_client()
    resolver = NameResolver(client)
    
    try:
        agent_id = resolver.resolve_agent(agent_name_or_id)
    except click.ClickException as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    
    # Build update payload
    if payload:
        body = load_json_payload(payload)
    else:
        body = {}
        if name:
            body["name"] = name
        if description:
            body["description"] = description
        if status:
            body["status"] = status
        
        if not body:
            raise click.ClickException("No updates specified. Use --name, --description, --status, or --payload.")
    
    response = client.put(f"/api/v1/agent/{agent_id}", json=body, **auth_kwargs(auth))
    
    if response.get("task_id"):
        if wait:
            click.echo("Updating agent...")
        response = client.handle_async_response(response, wait=wait)
    
    click.echo("✓ Agent updated successfully", err=True)
    print_json(response)


@cmd.command("delete")
@auth_option()
@click.argument("agent_name_or_id")
@click.option("--wait/--no-wait", default=False, show_default=True)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def delete_agent(auth: str, agent_name_or_id: str, wait: bool, yes: bool) -> None:
    """Soft delete an agent by name or ID."""
    client = make_client()
    resolver = NameResolver(client)
    
    try:
        agent_id = resolver.resolve_agent(agent_name_or_id)
    except click.ClickException as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    
    if not yes:
        if not click.confirm(f"Are you sure you want to delete agent '{agent_name_or_id}'?"):
            click.echo("Cancelled.")
            return
    
    response = client.delete(f"/api/v1/agent/{agent_id}", **auth_kwargs(auth))
    
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    
    click.echo(f"✓ Agent '{agent_name_or_id}' deleted successfully", err=True)
    print_json(response)


@cmd.command("restore")
@auth_option()
@click.argument("agent_name_or_id")
@click.option("--wait/--no-wait", default=False, show_default=True)
def restore_agent(auth: str, agent_name_or_id: str, wait: bool) -> None:
    """Restore a soft-deleted agent by name or ID."""
    client = make_client()
    resolver = NameResolver(client)
    
    try:
        agent_id = resolver.resolve_agent(agent_name_or_id, fuzzy=False)
    except click.ClickException as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    
    response = client.patch(f"/api/v1/agent/{agent_id}/restore", **auth_kwargs(auth))
    
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    
    click.echo(f"✓ Agent '{agent_name_or_id}' restored successfully", err=True)
    print_json(response)


@cmd.command("stats")
@auth_option()
@click.argument("agent_name_or_id", required=False)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "table", "tree"], case_sensitive=False),
    default="tree",
    show_default=True,
    help="Output format",
)
def agent_stats(auth: str, agent_name_or_id: Optional[str], output_format: str) -> None:
    """Retrieve statistics for an agent.
    
    If no agent is specified, uses the active agent from context.
    """
    client = make_client()
    resolver = NameResolver(client)
    ctx = get_context()
    
    # Use context if no agent specified
    if not agent_name_or_id:
        if not ctx.agent_id:
            raise click.ClickException(
                "No agent specified and no active agent in context. "
                "Use 'knowrithm context set agent <name>' or provide an agent name."
            )
        agent_id = ctx.agent_id
        agent_name_or_id = ctx.agent_name or agent_id
    else:
        try:
            agent_id = resolver.resolve_agent(agent_name_or_id)
        except click.ClickException as e:
            click.echo(str(e), err=True)
            raise SystemExit(1)
    
    response = client.get(f"/api/v1/agent/{agent_id}/stats", **auth_kwargs(auth))
    
    # Format output
    if output_format == "tree":
        output = format_output(response, output_format, title=f"Stats: {agent_name_or_id}")
    else:
        output = format_output(response, output_format)
    click.echo(output)


@cmd.command("test")
@auth_option()
@click.argument("agent_name_or_id", required=False)
@click.option("--query", "-q", help="Test query to send to the agent")
@click.option("--payload", help="Optional JSON test payload")
@click.option("--wait/--no-wait", default=True, show_default=True)
def test_agent(
    auth: str,
    agent_name_or_id: Optional[str],
    query: Optional[str],
    payload: Optional[str],
    wait: bool,
) -> None:
    """Run a test query against an agent.
    
    If no agent is specified, uses the active agent from context.
    
    Examples:
        # Test with active agent
        knowrithm agent test --query "What is your refund policy?"
        
        # Test specific agent
        knowrithm agent test "Support Bot" --query "Hello"
    """
    client = make_client()
    resolver = NameResolver(client)
    ctx = get_context()
    
    # Use context if no agent specified
    if not agent_name_or_id:
        if not ctx.agent_id:
            raise click.ClickException(
                "No agent specified and no active agent in context. "
                "Use 'knowrithm context set agent <name>' or provide an agent name."
            )
        agent_id = ctx.agent_id
        agent_name_or_id = ctx.agent_name or agent_id
    else:
        try:
            agent_id = resolver.resolve_agent(agent_name_or_id)
        except click.ClickException as e:
            click.echo(str(e), err=True)
            raise SystemExit(1)
    
    # Build test payload
    if payload:
        body = load_json_payload(payload)
    elif query:
        body = {"query": query}
    else:
        body = None
    
    click.echo(f"Testing agent '{agent_name_or_id}'...", err=True)
    
    response = client.post(
        f"/api/v1/agent/{agent_id}/test",
        json=body,
        **auth_kwargs(auth),
    )
    
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    
    print_json(response)


@cmd.command("clone")
@auth_option()
@click.argument("agent_name_or_id")
@click.option("--new-name", help="Name for the cloned agent")
@click.option("--payload", help="Optional JSON overrides for the cloned agent")
@click.option("--wait/--no-wait", default=True, show_default=True)
def clone_agent(
    auth: str,
    agent_name_or_id: str,
    new_name: Optional[str],
    payload: Optional[str],
    wait: bool,
) -> None:
    """Clone an existing agent by name or ID.
    
    Examples:
        # Clone with new name
        knowrithm agent clone "Support Bot" --new-name "Support Bot Copy"
        
        # Clone with overrides
        knowrithm agent clone "Support Bot" --payload '{"name": "New Bot", "description": "Cloned"}'
    """
    client = make_client()
    resolver = NameResolver(client)
    
    try:
        agent_id = resolver.resolve_agent(agent_name_or_id)
    except click.ClickException as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    
    # Build clone payload
    if payload:
        body = load_json_payload(payload)
    elif new_name:
        body = {"name": new_name}
    else:
        body = None
    
    response = client.post(f"/api/v1/agent/{agent_id}/clone", json=body, **auth_kwargs(auth))
    
    if response.get("task_id"):
        if wait:
            click.echo("Cloning agent...")
        response = client.handle_async_response(response, wait=wait)
    
    click.echo(f"✓ Agent cloned successfully", err=True)
    print_json(response)


@cmd.command("embed-code")
@auth_option()
@click.argument("agent_name_or_id", required=False)
def embed_code(auth: str, agent_name_or_id: Optional[str]) -> None:
    """Fetch widget embed code for an agent.
    
    If no agent is specified, uses the active agent from context.
    """
    client = make_client()
    resolver = NameResolver(client)
    ctx = get_context()
    
    # Use context if no agent specified
    if not agent_name_or_id:
        if not ctx.agent_id:
            raise click.ClickException(
                "No agent specified and no active agent in context. "
                "Use 'knowrithm context set agent <name>' or provide an agent name."
            )
        agent_id = ctx.agent_id
    else:
        try:
            agent_id = resolver.resolve_agent(agent_name_or_id)
        except click.ClickException as e:
            click.echo(str(e), err=True)
            raise SystemExit(1)
    
    response = client.get(f"/api/v1/agent/{agent_id}/embed-code", **auth_kwargs(auth))
    
    # Display embed code prominently
    if "embed_code" in response:
        click.echo("\n=== Widget Embed Code ===\n")
        click.echo(response["embed_code"])
        click.echo("\n=========================\n")
    
    print_json(response)
