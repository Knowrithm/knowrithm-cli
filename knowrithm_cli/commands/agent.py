"""Enhanced agent management commands with name resolution and interactive features."""

from __future__ import annotations

from typing import Optional

import click

from ..client import KnowrithmClient
from ..core import get_context, NameResolver, format_output
from ..utils import load_json_payload
from .common import auth_kwargs, auth_option, format_option, make_client


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
@format_option()
def list_agents(
    auth: str,
    company_id: Optional[str],
    status: Optional[str],
    search: Optional[str],
    page: int,
    per_page: int,
    format: str,
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
    output = format_output(response, format)
    click.echo(output)


@cmd.command("get")
@auth_option()
@click.argument("agent_name_or_id")
@format_option(default="json")
def get_agent(auth: str, agent_name_or_id: str, format: str) -> None:
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
    if format == "tree":
        output = format_output(response, format, title=f"Agent: {agent_name_or_id}")
    else:
        output = format_output(response, format)
    click.echo(output)


@cmd.command("create")
@auth_option()
@format_option()
@click.option("--payload", help="JSON string or @path describing the agent.")
@click.option("--name", help="Agent name (interactive mode)")
@click.option("--description", help="Agent description (interactive mode)")
@click.option("--wait/--no-wait", default=True, show_default=True)
@click.option("--interactive", "-i", is_flag=True, help="Interactive creation mode")
def create_agent(
    auth: str,
    format: str,
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
    if response.get("agent"):
        agent = response["agent"]
        agent_id = agent.get("id")
        agent_name = agent.get("name")
        
        if agent_id:
            ctx = get_context()
            ctx.set_agent(agent_id, agent_name)
        
        # Display friendly success message
        click.echo("\n✅ Agent created successfully!\n")
        click.echo(f"  Name: {agent_name}")
        click.echo(f"  ID: {agent_id}")
        click.echo(f"  Status: {agent.get('status', 'N/A')}")
        click.echo(f"  Model: {agent.get('model_name', 'N/A')}")
        
        # Show LLM settings info if available
        if response.get("settings"):
            settings = response["settings"]
            click.echo(f"\n  LLM Provider: {settings.get('llm_provider_label', 'N/A')}")
            click.echo(f"  LLM Model: {settings.get('llm_model_name', 'N/A')}")
            click.echo(f"  Embedding Provider: {settings.get('embedding_provider_label', 'N/A')}")
            click.echo(f"  Embedding Model: {settings.get('embedding_model_name', 'N/A')}")
        
        click.echo(f"\n  🔗 Set as active agent")
        
        # Show full details if format is not table
        if format != "table":
            click.echo(f"\n{'-' * 50}")
            click.echo("Full Details:")
            click.echo(format_output(response, format))
    elif response.get("id"):
        # Fallback for older response format
        agent_id = response.get("id")
        agent_name = response.get("name")
        
        ctx = get_context()
        ctx.set_agent(agent_id, agent_name)
        
        click.echo(f"\n✅ Agent created: {agent_name}")
        click.echo(f"  ID: {agent_id}")
        click.echo(f"  Set as active agent")
        
        if format != "table":
            click.echo(f"\n{format_output(response, format)}")
    else:
        # Show raw response if structure is unexpected
        click.echo(format_output(response, format))


def _interactive_agent_creation() -> dict:
    """Interactive wizard for agent creation."""
    click.echo("=== Create New Agent ===\n")
    
    name = click.prompt("Agent name", type=str)
    description = click.prompt("Description", default="", show_default=False)
    
    # Fetch providers from API
    client = make_client()
    
    # Variables to store IDs
    llm_provider_id = None
    llm_model_id = None
    embedding_provider_id = None
    embedding_model_id = None
    
    try:
        providers_response = client.get("/api/v1/providers", require_auth=True)
        all_providers = providers_response.get("providers", [])
    except Exception as e:
        click.echo(f"❌ Error: Could not fetch providers from API: {e}")
        click.echo("Cannot create agent without provider information.")
        raise click.Abort()
    
    if not all_providers:
        click.echo("❌ Error: No providers found in the system.")
        click.echo("Please configure providers first using the settings API.")
        raise click.Abort()
    
    # Filter providers by provider_type
    llm_providers = [p for p in all_providers if p.get("provider_type") in ["llm", "both"]]
    embedding_providers = [p for p in all_providers if p.get("provider_type") in ["embedding", "both"]]
    
    # LLM Provider Selection
    click.echo("\n📋 Select LLM Provider:")
    if not llm_providers:
        click.echo("❌ Error: No LLM providers found.")
        raise click.Abort()
    
    for idx, provider in enumerate(llm_providers, 1):
        provider_name = provider.get("label", "Unknown")
        provider_type = provider.get("provider_type", "N/A")
        click.echo(f"  {idx}. {provider_name} ({provider_type})")
    
    provider_idx = click.prompt(
        "\nSelect LLM provider (number)",
        type=click.IntRange(1, len(llm_providers)),
        default=1
    )
    
    selected_llm_provider = llm_providers[provider_idx - 1]
    llm_provider = selected_llm_provider.get("label")
    llm_provider_id = selected_llm_provider.get("id")
    
    # Fetch models for selected provider
    try:
        models_response = client.get(
            f"/api/v1/providers/{llm_provider_id}/models",
            require_auth=True
        )
        llm_models = models_response.get("models", [])
        # Filter for LLM models
        llm_models = [m for m in llm_models if m.get("model_type") in ["llm", "chat", "completion"]]
    except Exception as e:
        click.echo(f"❌ Error: Could not fetch models: {e}")
        raise click.Abort()
    
    if not llm_models:
        click.echo(f"❌ Error: No LLM models found for {llm_provider}")
        raise click.Abort()
    
    click.echo(f"\n🤖 Available Models for {llm_provider}:")
    for idx, model in enumerate(llm_models, 1):
        model_name = model.get("name", model.get("label", "Unknown"))
        context = model.get("context_window", "N/A")
        click.echo(f"  {idx}. {model_name} (context: {context})")
    
    model_idx = click.prompt(
        "\nSelect LLM model (number)",
        type=click.IntRange(1, len(llm_models)),
        default=1
    )
    
    selected_llm_model = llm_models[model_idx - 1]
    llm_model = selected_llm_model.get("name", selected_llm_model.get("label", "Unknown"))
    llm_model_id = selected_llm_model.get("id")
    
    click.echo(f"\n✓ LLM: {llm_provider} / {llm_model}")
    
    # Embedding Provider Selection
    click.echo("\n📋 Select Embedding Provider:")
    click.echo("  (You can use the same provider or choose a different one)")
    
    if not embedding_providers:
        click.echo("❌ Error: No embedding providers found.")
        raise click.Abort()
    
    for idx, provider in enumerate(embedding_providers, 1):
        provider_name = provider.get("label", "Unknown")
        provider_type = provider.get("provider_type", "N/A")
        click.echo(f"  {idx}. {provider_name} ({provider_type})")
    
    embedding_provider_idx = click.prompt(
        "\nSelect embedding provider (number)",
        type=click.IntRange(1, len(embedding_providers)),
        default=1
    )
    
    selected_embedding_provider = embedding_providers[embedding_provider_idx - 1]
    embedding_provider = selected_embedding_provider.get("label")
    embedding_provider_id = selected_embedding_provider.get("id")
    
    # Fetch models for selected embedding provider
    try:
        embedding_models_response = client.get(
            f"/api/v1/providers/{embedding_provider_id}/models",
            require_auth=True
        )
        embedding_models = embedding_models_response.get("models", [])
        # Filter for embedding models
        embedding_models = [m for m in embedding_models if m.get("model_type") == "embedding"]
    except Exception as e:
        click.echo(f"❌ Error: Could not fetch embedding models: {e}")
        raise click.Abort()
    
    if not embedding_models:
        click.echo(f"❌ Error: No embedding models found for {embedding_provider}")
        raise click.Abort()
    
    click.echo(f"\n🔤 Available Embedding Models for {embedding_provider}:")
    for idx, model in enumerate(embedding_models, 1):
        model_name = model.get("name", model.get("label", "Unknown"))
        dimension = model.get("embedding_dimension", "N/A")
        click.echo(f"  {idx}. {model_name} (dimension: {dimension})")
    
    embedding_model_idx = click.prompt(
        "\nSelect embedding model (number)",
        type=click.IntRange(1, len(embedding_models)),
        default=1
    )
    
    selected_embedding_model = embedding_models[embedding_model_idx - 1]
    embedding_model = selected_embedding_model.get("name", selected_embedding_model.get("label", "Unknown"))
    embedding_model_id = selected_embedding_model.get("id")
    
    click.echo(f"\n✓ Embeddings: {embedding_provider} / {embedding_model}")
    
    # Optional API keys
    llm_api_key = None
    embedding_api_key = None
    
    if click.confirm("\nDo you want to provide API keys?", default=False):
        llm_api_key = click.prompt(f"Enter API key for {llm_provider} (leave empty to skip)", default="", show_default=False)
        if not llm_api_key:
            llm_api_key = None
        
        if embedding_provider_id != llm_provider_id:
            embedding_api_key = click.prompt(f"Enter API key for {embedding_provider} (leave empty to skip)", default="", show_default=False)
            if not embedding_api_key:
                embedding_api_key = None
        else:
            embedding_api_key = llm_api_key
    
    # Optional fields
    if click.confirm("\nConfigure advanced settings?", default=False):
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
            "status": "active",  # Default status
        }
    
    
    
    # Add provider/model IDs and API keys directly to agent body
    # The agent creation endpoint will handle creating LLM settings internally
    body["llm_provider_id"] = llm_provider_id
    body["llm_model_id"] = llm_model_id
    body["embedding_provider_id"] = embedding_provider_id
    body["embedding_model_id"] = embedding_model_id
    
    if llm_api_key:
        body["llm_api_key"] = llm_api_key
    if embedding_api_key:
        body["embedding_api_key"] = embedding_api_key
    
    return body



@cmd.command("update")
@auth_option()
@format_option()
@click.argument("agent_name_or_id")
@click.option("--payload", help="JSON string or @path with update fields.")
@click.option("--name", help="New agent name")
@click.option("--description", help="New description")
@click.option("--status", type=click.Choice(["active", "inactive", "training"]), help="New status")
@click.option("--wait/--no-wait", default=True, show_default=True)
def update_agent(
    auth: str,
    format: str,
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
    
    
    # Display friendly success message
    click.echo("\n✅ Agent updated successfully!\n")
    
    # Extract agent data from response - handle various response structures
    agent_data = None
    
    # Check if response has a "data" field (common API response format)
    if "data" in response:
        data_field = response["data"]
        if isinstance(data_field, str):
            try:
                parsed_data = json.loads(data_field)
                agent_data = parsed_data.get("agent")
            except (json.JSONDecodeError, AttributeError):
                pass
        elif isinstance(data_field, dict):
            agent_data = data_field.get("agent") or data_field
    
    # Fallback to other common structures
    if not agent_data:
        agent_data = response.get("agent")
    
    # Final fallback - if response itself looks like agent data
    if not agent_data and isinstance(response, dict) and "id" in response and "name" in response:
        agent_data = response
    
    if isinstance(agent_data, dict) and agent_data.get("id"):
        # Display key agent information in a clean format
        click.echo(f"  📝 Name: {agent_data.get('name', 'N/A')}")
        click.echo(f"  🆔 ID: {agent_data.get('id', 'N/A')}")
        
        if agent_data.get("status"):
            status_emoji = "✅" if agent_data.get("status") == "active" else "⏸️"
            click.echo(f"  {status_emoji} Status: {agent_data.get('status')}")
        
        if agent_data.get("description"):
            # Truncate long descriptions
            desc = agent_data.get("description")
            if len(desc) > 100:
                desc = desc[:97] + "..."
            click.echo(f"  📄 Description: {desc}")
        
        if agent_data.get("model_name"):
            click.echo(f"  🤖 Model: {agent_data.get('model_name')}")
        
        # Show timestamps
        if agent_data.get("created_at"):
            click.echo(f"  📅 Created: {agent_data.get('created_at')}")
        if agent_data.get("updated_at"):
            click.echo(f"  🔄 Updated: {agent_data.get('updated_at')}")
        
        # Show statistics if available
        stats_shown = False
        if agent_data.get("total_conversations") is not None:
            if not stats_shown:
                click.echo("")  # Add spacing before stats
                stats_shown = True
            click.echo(f"  💬 Conversations: {agent_data.get('total_conversations', 0)}")
        if agent_data.get("total_messages") is not None:
            if not stats_shown:
                click.echo("")
                stats_shown = True
            click.echo(f"  📨 Messages: {agent_data.get('total_messages', 0)}")
        if agent_data.get("average_rating") is not None and agent_data.get("average_rating") > 0:
            if not stats_shown:
                click.echo("")
                stats_shown = True
            click.echo(f"  ⭐ Rating: {agent_data.get('average_rating', 0):.1f}")
        
        # Show full details if format is json or yaml
        if format in ["json", "yaml"]:
            click.echo(f"\n{'-' * 60}")
            click.echo("📋 Full Response Details:")
            click.echo('-' * 60)
            click.echo(format_output(response, format))
    else:
        # Fallback to standard formatting if we can't parse the structure
        click.echo("  ℹ️  Response received but structure is unexpected")
        click.echo(f"\n{format_output(response, format)}")


@cmd.command("delete")
@auth_option()
@format_option()
@click.argument("agent_name_or_id")
@click.option("--wait/--no-wait", default=False, show_default=True)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def delete_agent(auth: str, format: str, agent_name_or_id: str, wait: bool, yes: bool) -> None:
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
    
    # Display friendly success message
    click.echo(f"\n✅ Agent '{agent_name_or_id}' deleted successfully!\n")
    
    # Show message from response if available
    if response.get("message"):
        click.echo(f"  ℹ️  {response.get('message')}")
    
    # Show full details if format is json or yaml
    if format in ["json", "yaml"]:
        click.echo(f"\n{'-' * 60}")
        click.echo("📋 Full Response Details:")
        click.echo('-' * 60)
        click.echo(format_output(response, format))


@cmd.command("restore")
@auth_option()
@format_option()
@click.argument("agent_name_or_id")
@click.option("--wait/--no-wait", default=False, show_default=True)
def restore_agent(auth: str, format: str, agent_name_or_id: str, wait: bool) -> None:
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
    click.echo(format_output(response, format))


@cmd.command("stats")
@auth_option()
@click.argument("agent_name_or_id", required=False)
@format_option(default="tree")
def agent_stats(auth: str, agent_name_or_id: Optional[str], format: str) -> None:
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
    if format == "tree":
        output = format_output(response, format, title=f"Stats: {agent_name_or_id}")
    else:
        output = format_output(response, format)
    click.echo(output)


@cmd.command("test")
@auth_option()
@format_option()
@click.argument("agent_name_or_id", required=False)
@click.option("--query", "-q", help="Test query to send to the agent")
@click.option("--payload", help="Optional JSON test payload")
@click.option("--wait/--no-wait", default=True, show_default=True)
def test_agent(
    auth: str,
    format: str,
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
    
    click.echo(format_output(response, format))


@cmd.command("clone")
@auth_option()
@format_option()
@click.argument("agent_name_or_id")
@click.option("--new-name", help="Name for the cloned agent")
@click.option("--payload", help="Optional JSON overrides for the cloned agent")
@click.option("--wait/--no-wait", default=True, show_default=True)
def clone_agent(
    auth: str,
    format: str,
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
    
    # Display friendly success message
    click.echo("\n✅ Agent cloned successfully!\n")
    
    # Extract agent data from response
    agent_data = None
    if "data" in response:
        data_field = response["data"]
        if isinstance(data_field, str):
            try:
                parsed_data = json.loads(data_field)
                agent_data = parsed_data.get("agent")
            except (json.JSONDecodeError, AttributeError):
                pass
        elif isinstance(data_field, dict):
            agent_data = data_field.get("agent") or data_field
    
    if not agent_data:
        agent_data = response.get("agent")
    
    if not agent_data and isinstance(response, dict) and "id" in response and "name" in response:
        agent_data = response
    
    if isinstance(agent_data, dict) and agent_data.get("id"):
        # Display key agent information
        click.echo(f"  📝 Name: {agent_data.get('name', 'N/A')}")
        click.echo(f"  🆔 ID: {agent_data.get('id', 'N/A')}")
        
        if agent_data.get("status"):
            status_emoji = "✅" if agent_data.get("status") == "active" else "⏸️"
            click.echo(f"  {status_emoji} Status: {agent_data.get('status')}")
        
        if agent_data.get("description"):
            desc = agent_data.get("description")
            if len(desc) > 100:
                desc = desc[:97] + "..."
            click.echo(f"  📄 Description: {desc}")
        
        if agent_data.get("model_name"):
            click.echo(f"  🤖 Model: {agent_data.get('model_name')}")
        
        click.echo(f"  📅 Created: {agent_data.get('created_at', 'N/A')}")
        
        # Show full details if format is json or yaml
        if format in ["json", "yaml"]:
            click.echo(f"\n{'-' * 60}")
            click.echo("📋 Full Response Details:")
            click.echo('-' * 60)
            click.echo(format_output(response, format))
    else:
        click.echo(f"\n{format_output(response, format)}")


@cmd.command("embed-code")
@auth_option()
@format_option()
@click.argument("agent_name_or_id", required=False)
def embed_code(auth: str, format: str, agent_name_or_id: Optional[str]) -> None:
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
    
    click.echo(format_output(response, format))
