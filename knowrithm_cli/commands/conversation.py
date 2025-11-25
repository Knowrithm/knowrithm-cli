"""Conversation management commands."""

from __future__ import annotations

from typing import Optional

import click

from ..core.formatters import format_output
from ..core.name_resolver import NameResolver
from ..utils import load_json_payload, print_json
from .common import auth_kwargs, auth_option, format_option, make_client


@click.group(name="conversation")
def cmd() -> None:
    """Manage conversations and messages."""


@cmd.command("list")
@auth_option()
@format_option()
@click.option("--page", default=1, show_default=True, type=int)
@click.option("--per-page", default=20, show_default=True, type=int)
def list_conversations(auth: str, format: str, page: int, per_page: int) -> None:
    """List company conversations."""
    client = make_client()
    response = client.get(
        "/api/v1/conversation",
        params={"page": page, "per_page": per_page},
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("entity")
@auth_option()
@format_option()
@click.option("--entity-id", help="Specific entity ID to inspect.")
@click.option("--entity-type", help="Filter by entity type (lead/user).")
@click.option("--status", help="Conversation status filter.")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
def entity_conversations(
    auth: str,
    format: str,
    entity_id: Optional[str],
    entity_type: Optional[str],
    status: Optional[str],
    page: int,
    per_page: int,
) -> None:
    """List conversations scoped to the current entity or a provided ID."""
    client = make_client()
    params = {"page": page, "per_page": per_page}
    if status:
        params["status"] = status
    if entity_id:
        if entity_type:
            params["entity_type"] = entity_type
        response = client.get(
            f"/api/v1/conversation/entity/{entity_id}",
            params=params,
            **auth_kwargs(auth),
        )
    else:
        if entity_type:
            params["entity_type"] = entity_type
        response = client.get(
            "/api/v1/conversation/entity",
            params=params,
            **auth_kwargs(auth),
        )
    click.echo(format_output(response, format))


@cmd.command("agent")
@auth_option()
@format_option()
@click.argument("agent_id_or_name")
@click.option("--status", help="Filter by conversation status.")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
def agent_conversations(
    auth: str,
    format: str,
    agent_id_or_name: str,
    status: Optional[str],
    page: int,
    per_page: int,
) -> None:
    """List conversations for a specific agent (by name or ID)."""
    client = make_client()
    resolver = NameResolver(client)
    
    # Resolve agent name to ID
    agent_id = resolver.resolve_agent(agent_id_or_name)
    
    params = {"page": page, "per_page": per_page}
    if status:
        params["status"] = status
    response = client.get(
        f"/api/v1/conversation/agent/{agent_id}",
        params=params,
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("create")
@auth_option()
@format_option()
@click.option("--payload", required=True, help="JSON string or @path for the conversation body.")
@click.option("--wait/--no-wait", default=False, show_default=True)
def create_conversation(auth: str, payload: str, wait: bool) -> None:
    """Create a new conversation."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post("/api/v1/conversation", json=body, **auth_kwargs(auth))
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    click.echo(format_output(response, format))


@cmd.command("messages")
@auth_option()
@format_option()
@click.argument("conversation_id")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=50, type=int)
def messages(auth: str, format: str, conversation_id: str, page: int, per_page: int) -> None:
    """Retrieve messages for a conversation."""
    client = make_client()
    response = client.get(
        f"/api/v1/conversation/{conversation_id}/messages",
        params={"page": page, "per_page": per_page},
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("chat")
@auth_option()
@click.argument("conversation_id")
@click.option("--payload", help="JSON string or @path containing the message body.")
@click.option("--message", "-m", help="Quick message text (alternative to --payload)")
@click.option("--interactive", "-i", is_flag=True, help="Interactive chat mode")
@click.option("--wait/--no-wait", default=True, show_default=True)
def chat(
    auth: str,
    conversation_id: str,
    payload: Optional[str],
    message: Optional[str],
    interactive: bool,
    wait: bool
) -> None:
    """Send a chat message into a conversation.
    
    Examples:
        # Quick message
        knowrithm conversation chat <id> --message "Hello"
        
        # From JSON payload
        knowrithm conversation chat <id> --payload '{"message": "Hello"}'
        
        # Interactive mode
        knowrithm conversation chat <id> --interactive
    """
    client = make_client()
    
    if interactive:
        # Interactive chat mode
        click.echo(f"=== Interactive Chat (Conversation: {conversation_id}) ===")
        click.echo("Type your messages below. Press Ctrl+C to exit.\n")
        
        try:
            while True:
                user_message = click.prompt("You", type=str)
                
                if not user_message.strip():
                    continue
                
                body = {"message": user_message}
                response = client.post(
                    f"/api/v1/conversation/{conversation_id}/chat",
                    json=body,
                    **auth_kwargs(auth),
                )
                
                if response.get("task_id"):
                    response = client.handle_async_response(response, wait=wait)
                
                # Extract and display assistant response
                if "response" in response:
                    click.echo(f"\nAssistant: {response['response']}\n")
                elif "message" in response:
                    click.echo(f"\nAssistant: {response['message']}\n")
                else:
                    print_json(response)
                    click.echo()
        except (KeyboardInterrupt, EOFError):
            click.echo("\n\nExiting chat...")
            return
    
    elif message:
        # Quick message mode
        body = {"message": message}
    elif payload:
        # Payload mode
        body = load_json_payload(payload)
    else:
        raise click.ClickException(
            "Either --message, --payload, or --interactive is required"
        )
    
    if not interactive:
        response = client.post(
            f"/api/v1/conversation/{conversation_id}/chat",
            json=body,
            **auth_kwargs(auth),
        )
        if response.get("task_id"):
            response = client.handle_async_response(response, wait=wait)
        click.echo(format_output(response, format))


@cmd.command("delete")
@auth_option()
@format_option()
@click.argument("conversation_id")
def delete_conversation(auth: str, conversation_id: str) -> None:
    """Soft delete a conversation."""
    client = make_client()
    response = client.delete(f"/api/v1/conversation/{conversation_id}", **auth_kwargs(auth))
    click.echo(format_output(response, format))


@cmd.command("restore")
@auth_option()
@format_option()
@click.argument("conversation_id")
def restore_conversation(auth: str, conversation_id: str) -> None:
    """Restore a soft-deleted conversation."""
    client = make_client()
    response = client.patch(
        f"/api/v1/conversation/{conversation_id}/restore",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("delete-messages")
@auth_option()
@format_option()
@click.argument("conversation_id")
def delete_messages(auth: str, conversation_id: str) -> None:
    """Delete all messages for a conversation."""
    client = make_client()
    response = client.delete(
        f"/api/v1/conversation/{conversation_id}/messages",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("restore-messages")
@auth_option()
@format_option()
@click.argument("conversation_id")
def restore_messages(auth: str, conversation_id: str) -> None:
    """Restore all messages for a conversation."""
    client = make_client()
    response = client.patch(
        f"/api/v1/conversation/{conversation_id}/message/restore-all",
        **auth_kwargs(auth),
    )
    click.echo(format_output(response, format))


@cmd.command("deleted")
@auth_option()
@format_option()
def deleted_conversations(auth: str, format: str) -> None:
    """List soft-deleted conversations."""
    client = make_client()
    response = client.get("/api/v1/conversation/deleted", **auth_kwargs(auth))
    click.echo(format_output(response, format))

