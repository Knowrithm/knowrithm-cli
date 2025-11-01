"""Conversation management commands."""

from __future__ import annotations

from typing import Optional

import click

from ..utils import load_json_payload, print_json
from .common import auth_kwargs, auth_option, make_client


@click.group(name="conversation")
def cmd() -> None:
    """Manage conversations and messages."""


@cmd.command("list")
@auth_option()
@click.option("--page", default=1, show_default=True, type=int)
@click.option("--per-page", default=20, show_default=True, type=int)
def list_conversations(auth: str, page: int, per_page: int) -> None:
    """List company conversations."""
    client = make_client()
    response = client.get(
        "/api/v1/conversation",
        params={"page": page, "per_page": per_page},
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("entity")
@auth_option()
@click.option("--entity-id", help="Specific entity ID to inspect.")
@click.option("--entity-type", help="Filter by entity type (lead/user).")
@click.option("--status", help="Conversation status filter.")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
def entity_conversations(
    auth: str,
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
    print_json(response)


@cmd.command("agent")
@auth_option()
@click.argument("agent_id")
@click.option("--status", help="Filter by conversation status.")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=20, type=int)
def agent_conversations(
    auth: str,
    agent_id: str,
    status: Optional[str],
    page: int,
    per_page: int,
) -> None:
    """List conversations for a specific agent."""
    client = make_client()
    params = {"page": page, "per_page": per_page}
    if status:
        params["status"] = status
    response = client.get(
        f"/api/v1/conversation/agent/{agent_id}",
        params=params,
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("create")
@auth_option()
@click.option("--payload", required=True, help="JSON string or @path for the conversation body.")
@click.option("--wait/--no-wait", default=False, show_default=True)
def create_conversation(auth: str, payload: str, wait: bool) -> None:
    """Create a new conversation."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post("/api/v1/conversation", json=body, **auth_kwargs(auth))
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("messages")
@auth_option()
@click.argument("conversation_id")
@click.option("--page", default=1, type=int)
@click.option("--per-page", default=50, type=int)
def messages(auth: str, conversation_id: str, page: int, per_page: int) -> None:
    """Retrieve messages for a conversation."""
    client = make_client()
    response = client.get(
        f"/api/v1/conversation/{conversation_id}/messages",
        params={"page": page, "per_page": per_page},
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("chat")
@auth_option()
@click.argument("conversation_id")
@click.option("--payload", required=True, help="JSON string or @path containing the message body.")
@click.option("--wait/--no-wait", default=True, show_default=True)
def chat(auth: str, conversation_id: str, payload: str, wait: bool) -> None:
    """Send a chat message into a conversation."""
    body = load_json_payload(payload)
    client = make_client()
    response = client.post(
        f"/api/v1/conversation/{conversation_id}/chat",
        json=body,
        **auth_kwargs(auth),
    )
    if response.get("task_id"):
        response = client.handle_async_response(response, wait=wait)
    print_json(response)


@cmd.command("delete")
@auth_option()
@click.argument("conversation_id")
def delete_conversation(auth: str, conversation_id: str) -> None:
    """Soft delete a conversation."""
    client = make_client()
    response = client.delete(f"/api/v1/conversation/{conversation_id}", **auth_kwargs(auth))
    print_json(response)


@cmd.command("restore")
@auth_option()
@click.argument("conversation_id")
def restore_conversation(auth: str, conversation_id: str) -> None:
    """Restore a soft-deleted conversation."""
    client = make_client()
    response = client.patch(
        f"/api/v1/conversation/{conversation_id}/restore",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("delete-messages")
@auth_option()
@click.argument("conversation_id")
def delete_messages(auth: str, conversation_id: str) -> None:
    """Delete all messages for a conversation."""
    client = make_client()
    response = client.delete(
        f"/api/v1/conversation/{conversation_id}/messages",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("restore-messages")
@auth_option()
@click.argument("conversation_id")
def restore_messages(auth: str, conversation_id: str) -> None:
    """Restore all messages for a conversation."""
    client = make_client()
    response = client.patch(
        f"/api/v1/conversation/{conversation_id}/message/restore-all",
        **auth_kwargs(auth),
    )
    print_json(response)


@cmd.command("deleted")
@auth_option()
def deleted_conversations(auth: str) -> None:
    """List soft-deleted conversations."""
    client = make_client()
    response = client.get("/api/v1/conversation/deleted", **auth_kwargs(auth))
    print_json(response)

