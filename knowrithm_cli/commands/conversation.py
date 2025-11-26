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
    
    # Extract messages from response
    messages_data = None
    if "data" in response:
        data_field = response["data"]
        if isinstance(data_field, str):
            try:
                import json
                parsed_data = json.loads(data_field)
                messages_data = parsed_data.get("messages", [])
            except (json.JSONDecodeError, AttributeError):
                pass
        elif isinstance(data_field, dict):
            messages_data = data_field.get("messages", [])
        elif isinstance(data_field, list):
            messages_data = data_field
    
    if not messages_data:
        messages_data = response.get("messages", [])
    
    # Display in a chat-like format for better readability
    if messages_data and isinstance(messages_data, list) and format == "table":
        click.echo(f"\n💬 Conversation Messages ({len(messages_data)} messages)\n")
        click.echo("=" * 80)
        
        for msg in messages_data:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            created_at = msg.get("created_at", "")
            model = msg.get("model_used", "")
            processing_time = msg.get("processing_time", "")
            
            # Role indicator
            if role == "user":
                role_emoji = "👤"
                role_label = "User"
            elif role == "assistant":
                role_emoji = "🤖"
                role_label = "Assistant"
            else:
                role_emoji = "ℹ️"
                role_label = role.title()
            
            click.echo(f"\n{role_emoji} {role_label}")
            if created_at:
                click.echo(f"   📅 {created_at}")
            
            # Content
            click.echo(f"   💬 {content}")
            
            # Additional info for assistant messages
            if role == "assistant":
                if model:
                    click.echo(f"   🤖 Model: {model}")
                if processing_time:
                    click.echo(f"   ⏱️  Processing: {processing_time}s")
                
                # Show sources if available
                metadata = msg.get("metadata", {})
                if isinstance(metadata, dict):
                    cited_sources = metadata.get("cited_sources", [])
                    if cited_sources:
                        click.echo(f"   📚 Sources: {len(cited_sources)} citations")
            
            click.echo("-" * 80)
    else:
        # Fallback to standard formatting
        click.echo(format_output(response, format))


def run_interactive_chat(client, conversation_id, auth_kwargs, wait=True):
    """Run an interactive chat session."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.markdown import Markdown
    import re
    
    console = Console()
    
    console.print(Panel(
        f"[bold cyan]Interactive Chat[/bold cyan]\n[dim]Conversation ID: {conversation_id}[/dim]",
        border_style="cyan"
    ))
    console.print("[dim]Type your messages below. Press Ctrl+C to exit.[/dim]\n")
    
    try:
        while True:
            user_message = console.input("[bold green]You:[/bold green] ")
            
            if not user_message.strip():
                continue
            
            body = {"message": user_message}
            response = client.post(
                f"/api/v1/conversation/{conversation_id}/chat",
                json=body,
                **auth_kwargs,
            )
            
            # Handle async response (wait for task completion)
            if response.get("task_id"):
                task_result = client.handle_async_response(response, wait=wait)
                
                # After task completes, fetch the latest messages
                messages_response = client.get(
                    f"/api/v1/conversation/{conversation_id}/messages",
                    params={"per_page": 10},  # Get last 10 messages
                    **auth_kwargs,
                )
                
                # Extract messages from response
                messages = []
                if "messages" in messages_response:
                    messages = messages_response["messages"]
                elif "data" in messages_response and isinstance(messages_response["data"], dict):
                    messages = messages_response["data"].get("messages", [])
                elif "data" in messages_response and isinstance(messages_response["data"], list):
                    messages = messages_response["data"]
                
                # Use the messages from the fetch
                response = {"messages": messages}
            
            # Extract assistant response from messages array
            assistant_response = None
            sources = []
            model_used = None
            processing_time = None
            
            # Check if response has messages array
            if "messages" in response and isinstance(response["messages"], list):
                # Get the last message (should be the assistant's response)
                for msg in reversed(response["messages"]):
                    if msg.get("role") == "assistant":
                        assistant_response = msg.get("content")
                        model_used = msg.get("model_used")
                        processing_time = msg.get("processing_time")
                        
                        # Extract sources from metadata
                        metadata = msg.get("metadata", {})
                        if isinstance(metadata, dict):
                            cited_sources = metadata.get("cited_sources", [])
                            all_sources = metadata.get("all_sources", [])
                            sources = cited_sources if cited_sources else all_sources
                        break
            
            # Fallback to old response structure
            if not assistant_response:
                assistant_response = response.get("response") or response.get("message") or response.get("content")
                # Try to get sources from top level
                sources = response.get("cited_sources", []) or response.get("all_sources", [])
            
            # Display assistant response
            if assistant_response:
                # Clean up inline source citations like [Source 1, 2, 3]
                cleaned_response = re.sub(r'\[Source[^\]]+\]', '', assistant_response)
                # Remove multiple consecutive newlines
                cleaned_response = re.sub(r'\n{3,}', '\n\n', cleaned_response)
                
                console.print(f"\n[bold blue]Assistant:[/bold blue]\n")
                
                # Render as markdown for proper formatting
                md = Markdown(cleaned_response)
                console.print(md)
                console.print()
                
                # Display metadata if available
                metadata_parts = []
                if model_used:
                    metadata_parts.append(f"🤖 Model: {model_used}")
                if processing_time:
                    metadata_parts.append(f"⏱️  {processing_time:.2f}s")
                
                if metadata_parts:
                    console.print(f"[dim]{' | '.join(metadata_parts)}[/dim]")
                
                # Display sources if available
                if sources:
                    console.print(f"\n[bold cyan]📚 Sources ({len(sources)}):[/bold cyan]")
                    # Parse and clean up source entries
                    for idx, source in enumerate(sources[:5], 1):  # Show first 5
                        # Convert to string if not already
                        if not isinstance(source, str):
                            source = str(source)
                        
                        # Extract filename and URL if present
                        # Format: "Source X: filename (URL)"
                        source_match = re.match(r'Source \d+:\s*(.+?)\s*\((.+?)\)', source)
                        if source_match:
                            filename = source_match.group(1)
                            url = source_match.group(2)
                            console.print(f"  [dim]{idx}.[/dim] [link={url}]{filename}[/link]")
                        else:
                            console.print(f"  [dim]{idx}.[/dim] {source}")
                    if len(sources) > 5:
                        console.print(f"  [dim]... and {len(sources) - 5} more[/dim]")
                
                # Add separator line
                console.print(f"\n[dim]{'─' * console.width}[/dim]\n")
            else:
                # No response text found - show raw response
                console.print("[yellow]⚠️  Unexpected response format:[/yellow]")
                print_json(response)
                console.print()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Exiting chat...[/dim]")
        return


@cmd.command("chat")
@auth_option()
@format_option()
@click.argument("conversation_id")
@click.option("--payload", help="JSON string or @path containing the message body.")
@click.option("--message", "-m", help="Quick message text (alternative to --payload)")
@click.option("--interactive", "-i", is_flag=True, help="Interactive chat mode")
@click.option("--wait/--no-wait", default=True, show_default=True)
def chat(
    auth: str,
    format: str,
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
        run_interactive_chat(client, conversation_id, auth_kwargs(auth), wait=wait)
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
        
        # Display in a user-friendly format
        if format == "table":
            # Extract the response message
            response_text = None
            response_data = None
            
            # Try to extract from various response structures
            if "data" in response:
                data_field = response["data"]
                if isinstance(data_field, str):
                    try:
                        import json
                        parsed_data = json.loads(data_field)
                        response_data = parsed_data
                        response_text = parsed_data.get("response") or parsed_data.get("message") or parsed_data.get("content")
                    except (json.JSONDecodeError, AttributeError):
                        response_text = data_field
                elif isinstance(data_field, dict):
                    response_data = data_field
                    response_text = data_field.get("response") or data_field.get("message") or data_field.get("content")
            
            if not response_text:
                response_text = response.get("response") or response.get("message") or response.get("content")
                response_data = response
            
            if response_text:
                click.echo("\n✅ Message sent successfully!\n")
                click.echo("🤖 Assistant Response:")
                click.echo("=" * 80)
                click.echo(f"\n{response_text}\n")
                click.echo("=" * 80)
                
                # Show additional info if available
                if response_data and isinstance(response_data, dict):
                    if response_data.get("model_used"):
                        click.echo(f"\n   🤖 Model: {response_data.get('model_used')}")
                    if response_data.get("processing_time"):
                        click.echo(f"   ⏱️  Processing: {response_data.get('processing_time')}s")
                    
                    # Show sources if available
                    metadata = response_data.get("metadata", {})
                    if isinstance(metadata, dict):
                        cited_sources = metadata.get("cited_sources", [])
                        if cited_sources:
                            click.echo(f"   📚 Sources: {len(cited_sources)} citations")
            else:
                # No response text found - show what we have
                click.echo("\n✅ Message sent successfully!\n")
                
                if response_data and isinstance(response_data, dict):
                    # Show status
                    status = response_data.get("status")
                    if status:
                        click.echo(f"   ℹ️  Status: {status}")
                    
                    # Show processing time
                    processing_time = response_data.get("processing_time")
                    if processing_time:
                        click.echo(f"   ⏱️  Processing: {processing_time}s")
                    
                    # Show message ID
                    message_id = response_data.get("message_id")
                    if message_id:
                        click.echo(f"   🆔 Message ID: {message_id}")
                    
                    # Show sources
                    all_sources = response_data.get("all_sources", [])
                    cited_sources = response_data.get("cited_sources", [])
                    
                    if cited_sources:
                        click.echo(f"\n   📚 Cited Sources ({len(cited_sources)}):")
                        for source in cited_sources[:5]:  # Show first 5
                            click.echo(f"      • {source}")
                    elif all_sources:
                        click.echo(f"\n   📚 Available Sources ({len(all_sources)}):")
                        for source in all_sources[:5]:  # Show first 5
                            click.echo(f"      • {source}")
                    
                    click.echo("\n   ℹ️  Note: Response text not available in API response")
                    click.echo("   💡 Try checking the conversation messages to see the full response")
                else:
                    # Fallback to standard formatting
                    click.echo(format_output(response, format))
        else:
            # Use standard formatting for non-table formats
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

