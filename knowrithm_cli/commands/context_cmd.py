"""Context management commands."""

from __future__ import annotations

import click

from ..core import get_context, clear_context as clear_ctx, NameResolver, format_output
from .common import make_client


@click.group(name="context")
def cmd() -> None:
    """Manage CLI context (active agent, conversation, etc.)."""


@cmd.command("show")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "tree", "table"], case_sensitive=False),
    default="tree",
    show_default=True,
    help="Output format",
)
def show_context(output_format: str) -> None:
    """Display the current CLI context."""
    ctx = get_context()
    data = ctx.to_dict()
    
    if not any(data.values()):
        click.echo("No active context set.")
        click.echo("\nUse 'knowrithm context set' to set active agent, conversation, or organization.")
        return
    
    output = format_output(data, output_format, title="Current Context")
    click.echo(output)


@cmd.group("set")
def set_context() -> None:
    """Set active context items."""


@set_context.command("agent")
@click.argument("agent_name_or_id")
def set_agent(agent_name_or_id: str) -> None:
    """Set the active agent by name or ID.
    
    Examples:
        knowrithm context set agent "Support Bot"
        knowrithm context set agent abc123...
    """
    client = make_client()
    resolver = NameResolver(client)
    ctx = get_context()
    
    try:
        agent_id = resolver.resolve_agent(agent_name_or_id)
        
        # Fetch agent details to get the name
        response = client.get(f"/api/v1/agent/{agent_id}", require_auth=True)
        agent_name = response.get("name", agent_name_or_id)
        
        ctx.set_agent(agent_id, agent_name)
        click.echo(f"✓ Active agent set to: {agent_name}")
    except Exception as e:
        click.echo(f"Error setting agent: {e}", err=True)
        raise SystemExit(1)


@set_context.command("conversation")
@click.argument("conversation_name_or_id")
def set_conversation(conversation_name_or_id: str) -> None:
    """Set the active conversation by title or ID.
    
    Examples:
        knowrithm context set conversation "Support Chat"
        knowrithm context set conversation abc123...
    """
    client = make_client()
    resolver = NameResolver(client)
    ctx = get_context()
    
    try:
        conversation_id = resolver.resolve_conversation(conversation_name_or_id)
        
        # Fetch conversation details to get the title
        response = client.get(f"/api/v1/conversation/{conversation_id}/messages", require_auth=True)
        conversation_title = response.get("title", conversation_name_or_id)
        
        ctx.set_conversation(conversation_id, conversation_title)
        click.echo(f"✓ Active conversation set to: {conversation_title}")
    except Exception as e:
        click.echo(f"Error setting conversation: {e}", err=True)
        raise SystemExit(1)


@set_context.command("organization")
@click.argument("organization_name_or_id")
def set_organization(organization_name_or_id: str) -> None:
    """Set the active organization by name or ID (super admin only).
    
    Examples:
        knowrithm context set organization "Acme Corp"
        knowrithm context set organization abc123...
    """
    client = make_client()
    resolver = NameResolver(client)
    ctx = get_context()
    
    try:
        org_id = resolver.resolve_company(organization_name_or_id)
        
        # Fetch company details to get the name
        response = client.get(f"/api/v1/company/{org_id}", require_auth=True, use_jwt=True)
        org_name = response.get("name", organization_name_or_id)
        
        ctx.set_organization(org_id, org_name)
        click.echo(f"✓ Active organization set to: {org_name}")
    except Exception as e:
        click.echo(f"Error setting organization: {e}", err=True)
        raise SystemExit(1)


@cmd.group("clear")
def clear_context_group() -> None:
    """Clear context items."""


@clear_context_group.command("agent")
def clear_agent() -> None:
    """Clear the active agent from context."""
    ctx = get_context()
    ctx.clear_agent()
    click.echo("✓ Active agent cleared")


@clear_context_group.command("conversation")
def clear_conversation() -> None:
    """Clear the active conversation from context."""
    ctx = get_context()
    ctx.clear_conversation()
    click.echo("✓ Active conversation cleared")


@clear_context_group.command("organization")
def clear_organization() -> None:
    """Clear the active organization from context."""
    ctx = get_context()
    ctx.clear_organization()
    click.echo("✓ Active organization cleared")


@clear_context_group.command("all")
def clear_all() -> None:
    """Clear all context."""
    clear_ctx()
    click.echo("✓ All context cleared")
