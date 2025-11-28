"""Interactive utilities for CLI menus and selections."""

from typing import List, Optional, Dict, Any
import questionary
from questionary import Style


# Custom style for interactive prompts
custom_style = Style([
    ('qmark', 'fg:#00d4aa bold'),           # Question mark
    ('question', 'bold'),                    # Question text
    ('answer', 'fg:#00d4aa bold'),          # Selected answer
    ('pointer', 'fg:#00d4aa bold'),         # Pointer (arrow)
    ('highlighted', 'fg:#00d4aa bold'),     # Highlighted choice
    ('selected', 'fg:#00d4aa'),             # Selected choice
    ('separator', 'fg:#6C6C6C'),            # Separator
    ('instruction', ''),                     # Instruction text
    ('text', ''),                            # Plain text
    ('disabled', 'fg:#858585 italic')       # Disabled choices
])


def select_from_list(
    message: str,
    choices: List[str],
    default: Optional[str] = None,
    instruction: str = "(Use arrow keys)"
) -> str:
    """
    Display an interactive list selection menu.
    
    Args:
        message: The question/prompt to display
        choices: List of choices to select from
        default: Default choice (optional)
        instruction: Instruction text shown below the question
        
    Returns:
        The selected choice as a string
    """
    enable_shortcuts = len(choices) <= 36  # questionary shortcut limit
    return questionary.select(
        message,
        choices=choices,
        default=default,
        instruction=instruction,
        style=custom_style,
        use_shortcuts=enable_shortcuts,
        use_arrow_keys=True,
        use_indicator=True,
    ).ask()


def select_from_dict(
    message: str,
    choices: List[Dict[str, Any]],
    display_key: str = "name",
    value_key: str = "id",
    default_value: Optional[Any] = None,
    instruction: str = "(Use arrow keys)",
    format_choice: Optional[callable] = None
) -> tuple[Any, Dict[str, Any]]:
    """
    Display an interactive list selection menu from a list of dictionaries.
    
    Args:
        message: The question/prompt to display
        choices: List of dictionaries to select from
        display_key: Key to use for display text
        value_key: Key to use for return value
        default_value: Default value to pre-select (matches against value_key)
        instruction: Instruction text shown below the question
        format_choice: Optional function to format each choice for display
        
    Returns:
        Tuple of (selected_value, selected_dict)
    """
    if not choices:
        raise ValueError("No choices provided")
    
    # Create display choices
    if format_choice:
        display_choices = [format_choice(choice) for choice in choices]
    else:
        display_choices = [str(choice.get(display_key, "Unknown")) for choice in choices]
    
    # Find default index if default_value provided
    default_choice = None
    if default_value is not None:
        for i, choice in enumerate(choices):
            if choice.get(value_key) == default_value:
                default_choice = display_choices[i]
                break
    
    # Show selection menu
    enable_shortcuts = len(display_choices) <= 36  # questionary shortcut limit
    selected_display = questionary.select(
        message,
        choices=display_choices,
        default=default_choice,
        instruction=instruction,
        style=custom_style,
        use_shortcuts=enable_shortcuts,
        use_arrow_keys=True,
        use_indicator=True,
    ).ask()
    
    # Find the selected item
    selected_index = display_choices.index(selected_display)
    selected_dict = choices[selected_index]
    selected_value = selected_dict.get(value_key)
    
    return selected_value, selected_dict


def confirm(
    message: str,
    default: bool = False,
    auto_enter: bool = True
) -> bool:
    """
    Display a yes/no confirmation prompt.
    
    Args:
        message: The question to ask
        default: Default answer (True for yes, False for no)
        auto_enter: Whether to auto-submit on selection
        
    Returns:
        True if yes, False if no
    """
    return questionary.confirm(
        message,
        default=default,
        auto_enter=auto_enter,
        style=custom_style
    ).ask()


def text_input(
    message: str,
    default: str = "",
    validate: Optional[callable] = None,
    multiline: bool = False
) -> str:
    """
    Display a text input prompt.
    
    Args:
        message: The question/prompt to display
        default: Default value
        validate: Optional validation function
        multiline: Whether to allow multiline input
        
    Returns:
        The entered text
    """
    return questionary.text(
        message,
        default=default,
        validate=validate,
        multiline=multiline,
        style=custom_style
    ).ask()


def password_input(
    message: str,
    validate: Optional[callable] = None
) -> str:
    """
    Display a password input prompt (hidden input).
    
    Args:
        message: The question/prompt to display
        validate: Optional validation function
        
    Returns:
        The entered password
    """
    return questionary.password(
        message,
        validate=validate,
        style=custom_style
    ).ask()


def checkbox_select(
    message: str,
    choices: List[str],
    default: Optional[List[str]] = None,
    instruction: str = "(Use arrow keys, space to select, enter to confirm)"
) -> List[str]:
    """
    Display a multi-select checkbox menu.
    
    Args:
        message: The question/prompt to display
        choices: List of choices to select from
        default: List of default selected choices
        instruction: Instruction text shown below the question
        
    Returns:
        List of selected choices
    """
    return questionary.checkbox(
        message,
        choices=choices,
        default=default,
        instruction=instruction,
        style=custom_style,
        use_arrow_keys=True,
        use_jk_keys=False
    ).ask()


# Resource Selection Helpers

def select_agent(client, message: str = "Select an agent", show_status: bool = True):
    """
    Fetch agents and present an interactive selection menu.
    
    Args:
        client: KnowrithmClient instance
        message: The prompt message
        show_status: Whether to show agent status in the display
        
    Returns:
        Tuple of (agent_id, agent_dict)
    """
    import click
    
    # Fetch agents
    try:
        response = client.get("/api/v1/agent", params={"per_page": 100}, require_auth=True)
        agents = response.get("agents", [])
        
        if not agents:
            click.echo("❌ No agents found. Create an agent first.")
            raise click.Abort()
        
        # Format agent choices
        def format_agent(agent):
            name = agent.get("name", "Unknown")
            if show_status:
                status = agent.get("status", "unknown")
                model = agent.get("model_name", "N/A")
                return f"{name} (Status: {status}, Model: {model})"
            return name
        
        return select_from_dict(
            message,
            agents,
            display_key="name",
            value_key="id",
            format_choice=format_agent
        )
    except Exception as e:
        click.echo(f"❌ Error fetching agents: {e}")
        raise click.Abort()


def select_document(client, agent_id: Optional[str] = None, message: str = "Select a document"):
    """
    Fetch documents and present an interactive selection menu.
    
    Args:
        client: KnowrithmClient instance
        agent_id: Optional agent ID to filter documents
        message: The prompt message
        
    Returns:
        Tuple of (document_id, document_dict)
    """
    import click
    
    # Fetch documents
    try:
        if agent_id:
            response = client.get(f"/api/v1/document/agent/{agent_id}", params={"per_page": 100}, require_auth=True)
        else:
            response = client.get("/api/v1/document", params={"per_page": 100}, require_auth=True)
        
        documents = response.get("documents", [])
        
        if not documents:
            click.echo("❌ No documents found.")
            raise click.Abort()
        
        # Format document choices
        def format_document(doc):
            title = doc.get("title", doc.get("filename", "Unknown"))
            doc_type = doc.get("type", "N/A")
            created = doc.get("created_at", "")[:10] if doc.get("created_at") else "N/A"
            return f"{title} (Type: {doc_type}, Created: {created})"
        
        return select_from_dict(
            message,
            documents,
            display_key="title",
            value_key="id",
            format_choice=format_document
        )
    except Exception as e:
        click.echo(f"❌ Error fetching documents: {e}")
        raise click.Abort()


def select_conversation(client, agent_id: Optional[str] = None, message: str = "Select a conversation"):
    """
    Fetch conversations and present an interactive selection menu.
    
    Args:
        client: KnowrithmClient instance
        agent_id: Optional agent ID to filter conversations
        message: The prompt message
        
    Returns:
        Tuple of (conversation_id, conversation_dict)
    """
    import click
    
    # Fetch conversations
    try:
        if agent_id:
            response = client.get(f"/api/v1/conversation/agent/{agent_id}", params={"per_page": 100}, require_auth=True)
        else:
            response = client.get("/api/v1/conversation", params={"per_page": 100}, require_auth=True)
        
        conversations = response.get("conversations", [])
        
        if not conversations:
            click.echo("❌ No conversations found.")
            raise click.Abort()
        
        # Format conversation choices
        def format_conversation(conv):
            conv_id = conv.get("id", "Unknown")[:8]
            status = conv.get("status", "N/A")
            created = conv.get("created_at", "")[:10] if conv.get("created_at") else "N/A"
            msg_count = conv.get("message_count", 0)
            return f"ID: {conv_id}... (Status: {status}, Messages: {msg_count}, Created: {created})"
        
        return select_from_dict(
            message,
            conversations,
            display_key="id",
            value_key="id",
            format_choice=format_conversation
        )
    except Exception as e:
        click.echo(f"❌ Error fetching conversations: {e}")
        raise click.Abort()


def select_database(client, message: str = "Select a database connection"):
    """
    Fetch database connections and present an interactive selection menu.
    
    Args:
        client: KnowrithmClient instance
        message: The prompt message
        
    Returns:
        Tuple of (connection_id, connection_dict)
    """
    import click
    
    # Fetch database connections
    try:
        response = client.get("/api/v1/database", require_auth=True)
        connections = response.get("connections", [])
        
        if not connections:
            click.echo("❌ No database connections found.")
            raise click.Abort()
        
        # Format connection choices
        def format_connection(conn):
            name = conn.get("name", "Unknown")
            db_type = conn.get("type", "N/A")
            host = conn.get("host", "N/A")
            return f"{name} (Type: {db_type}, Host: {host})"
        
        return select_from_dict(
            message,
            connections,
            display_key="name",
            value_key="id",
            format_choice=format_connection
        )
    except Exception as e:
        click.echo(f"❌ Error fetching database connections: {e}")
        raise click.Abort()


def select_company(client, message: str = "Select a company"):
    """
    Fetch companies and present an interactive selection menu.
    
    Args:
        client: KnowrithmClient instance
        message: The prompt message
        
    Returns:
        Tuple of (company_id, company_dict)
    """
    import click
    
    # Fetch companies
    try:
        response = client.get("/api/v1/company", params={"per_page": 100}, require_auth=True)
        companies = response.get("companies", [])
        
        if not companies:
            click.echo("❌ No companies found.")
            raise click.Abort()
        
        # Format company choices
        def format_company(comp):
            name = comp.get("name", "Unknown")
            status = comp.get("status", "N/A")
            return f"{name} (Status: {status})"
        
        return select_from_dict(
            message,
            companies,
            display_key="name",
            value_key="id",
            format_choice=format_company
        )
    except Exception as e:
        click.echo(f"❌ Error fetching companies: {e}")
        raise click.Abort()


def select_lead(client, message: str = "Select a lead"):
    """
    Fetch leads and present an interactive selection menu.
    
    Args:
        client: KnowrithmClient instance
        message: The prompt message
        
    Returns:
        Tuple of (lead_id, lead_dict)
    """
    import click
    
    # Fetch leads
    try:
        response = client.get("/api/v1/lead/company", params={"per_page": 100}, require_auth=True)
        leads = response.get("leads")
        if leads is None:
            # Check for Data envelope
            data = response.get("Data") or response.get("data")
            if isinstance(data, dict):
                leads = data.get("leads")
        
        leads = leads or []
        
        if not leads:
            click.echo("❌ No leads found.")
            raise click.Abort()
        
        # Format lead choices
        def format_lead(lead):
            name = f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip() or "Unknown"
            email = lead.get("email", "N/A")
            status = lead.get("status", "N/A")
            return f"{name} ({email}, Status: {status})"
        
        return select_from_dict(
            message,
            leads,
            display_key="email",
            value_key="id",
            format_choice=format_lead
        )
    except Exception as e:
        click.echo(f"❌ Error fetching leads: {e}")
        raise click.Abort()


def select_settings(client, message: str = "Select settings"):
    """
    Fetch settings and present an interactive selection menu.
    
    Args:
        client: KnowrithmClient instance
        message: The prompt message
        
    Returns:
        Tuple of (settings_id, settings_dict)
    """
    import click
    
    # Fetch settings
    try:
        # First get current company to list its settings
        company_resp = client.get("/api/v1/company", require_auth=True)
        company_id = company_resp.get("id")
        
        if not company_id:
             click.echo("❌ Could not determine current company context.")
             raise click.Abort()

        response = client.get(f"/api/v1/settings/company/{company_id}", require_auth=True)
        settings_list = response.get("settings", [])
        
        if not settings_list:
            click.echo("❌ No settings found for current company.")
            raise click.Abort()
        
        # Format settings choices
        def format_setting(setting):
            provider = setting.get("provider", "Unknown")
            model = setting.get("model", "Unknown")
            return f"{provider} / {model}"
        
        return select_from_dict(
            message,
            settings_list,
            display_key="id",
            value_key="id",
            format_choice=format_setting
        )
    except Exception as e:
        click.echo(f"❌ Error fetching settings: {e}")
        raise click.Abort()


def select_website_source(client, message: str = "Select website source"):
    """
    Fetch website sources and present an interactive selection menu.
    
    Args:
        client: KnowrithmClient instance
        message: The prompt message
        
    Returns:
        Tuple of (source_id, source_dict)
    """
    import click
    
    # Fetch sources
    try:
        response = client.get("/api/v1/website/source", params={"per_page": 100}, require_auth=True)
        sources = response.get("sources", [])
        
        if not sources:
            click.echo("❌ No website sources found.")
            raise click.Abort()
        
        # Format source choices
        def format_source(source):
            url = source.get("url", "Unknown URL")
            status = source.get("status", "N/A")
            return f"{url} (Status: {status})"
        
        return select_from_dict(
            message,
            sources,
            display_key="url",
            value_key="id",
            format_choice=format_source
        )
    except Exception as e:
        click.echo(f"❌ Error fetching website sources: {e}")
        raise click.Abort()
