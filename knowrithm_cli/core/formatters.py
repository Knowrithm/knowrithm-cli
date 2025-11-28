"""Output formatting utilities for the Knowrithm CLI."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import click

try:
    from rich.console import Console
    from rich.table import Table
    from rich.tree import Tree
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class Formatter:
    """Formats CLI output in various formats."""

    def __init__(self, format_type: str = "json") -> None:
        """Initialize formatter.

        Args:
            format_type: Output format (json, table, yaml, csv, tree)
        """
        self.format_type = format_type.lower()
        self.console = Console() if RICH_AVAILABLE else None

    def format(self, data: Any) -> str:
        """Format data according to the configured format type.

        Args:
            data: Data to format

        Returns:
            Formatted string
        """
        if self.format_type == "json":
            return self.format_json(data)
        elif self.format_type == "table":
            return self.format_table(data)
        elif self.format_type == "yaml":
            return self.format_yaml(data)
        elif self.format_type == "csv":
            return self.format_csv(data)
        elif self.format_type == "tree":
            return self.format_tree(data)
        else:
            return self.format_json(data)

    def format_json(self, data: Any, *, indent: int = 2) -> str:
        """Format data as pretty JSON.

        Args:
            data: Data to format
            indent: Indentation level

        Returns:
            JSON string
        """
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)

    def format_yaml(self, data: Any) -> str:
        """Format data as YAML.

        Args:
            data: Data to format

        Returns:
            YAML string
        """
        try:
            import yaml
            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        except ImportError:
            click.echo("YAML output requires PyYAML. Install with: pip install pyyaml", err=True)
            return self.format_json(data)

    def format_table(self, data: Union[List[Dict], Dict]) -> str:
        """Format data as a table.

        Args:
            data: List of dictionaries or single dictionary

        Returns:
            Table string
        """
        if not data:
            return "No data to display"

        # Handle single dict - extract list data from various response structures
        if isinstance(data, dict):
            # Common list keys in API responses
            list_keys = ["data", "agents", "documents", "connection", "databases", 
                        "conversations", "leads", "companies", "users", "website_sources"]
            
            # Common single-entity keys (for get commands)
            single_entity_keys = ["agent", "document", "conversation", "lead", 
                                 "company", "user", "database_connection", "website_source"]
            
            # Try known list keys first
            for key in list_keys:
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
            else:
                # Check for single entity wrapped in a key
                for key in single_entity_keys:
                    if key in data and isinstance(data[key], dict):
                        # Convert single entity to list for table display
                        data = [data[key]]
                        break
                else:
                    # If no known key found, find first key with a list value
                    for key, value in data.items():
                        if isinstance(value, list) and key != "pagination":
                            data = value
                            break
                    else:
                        # No list found, convert single dict to list
                        data = [data]

        if not isinstance(data, list) or not data:
            return "No data to display"

        # Filter to essential columns for better readability
        data = self._filter_essential_columns(data)

        if RICH_AVAILABLE and self.console:
            return self._format_rich_table(data)
        else:
            return self._format_simple_table(data)

    def _format_rich_table(self, data: List[Dict]) -> str:
        """Format data as a rich table.

        Args:
            data: List of dictionaries

        Returns:
            Formatted table
        """
        if not data:
            return "No data to display"

        # Get all unique keys (only from dict items)
        keys = []
        for item in data:
            if isinstance(item, dict):
                for key in item.keys():
                    if key not in keys:
                        keys.append(key)

        # If no keys found (all items are non-dict), fall back to simple display
        if not keys:
            return "\\n".join(str(item) for item in data)

        # Create table
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")

        # Add columns
        for key in keys:
            table.add_column(self._format_header(key), overflow="fold")

        # Add rows
        for item in data:
            if isinstance(item, dict):
                row = []
                for key in keys:
                    value = item.get(key, "")
                    row.append(self._format_value(value))
                table.add_row(*row)

        # Render to string
        from io import StringIO
        string_io = StringIO()
        # Force terminal to ensure colors/styles are rendered, and set width to avoid wrapping issues in captured output
        console = Console(file=string_io, force_terminal=True, width=120)
        console.print(table)
        return string_io.getvalue()

    def _format_simple_table(self, data: List[Dict]) -> str:
        """Format data as a simple ASCII table.

        Args:
            data: List of dictionaries

        Returns:
            ASCII table string
        """
        if not data:
            return "No data to display"

        # Get all unique keys
        keys = []
        for item in data:
            for key in item.keys():
                if key not in keys:
                    keys.append(key)

        # Calculate column widths
        widths = {key: len(self._format_header(key)) for key in keys}
        for item in data:
            for key in keys:
                value_str = str(item.get(key, ""))
                widths[key] = max(widths[key], len(value_str))

        # Build table
        lines = []

        # Header
        header = " | ".join(self._format_header(key).ljust(widths[key]) for key in keys)
        lines.append(header)
        lines.append("-" * len(header))

        # Rows
        for item in data:
            row = " | ".join(
                str(item.get(key, "")).ljust(widths[key]) for key in keys
            )
            lines.append(row)

        return "\n".join(lines)

    def format_csv(self, data: Union[List[Dict], Dict]) -> str:
        """Format data as CSV.

        Args:
            data: List of dictionaries or single dictionary

        Returns:
            CSV string
        """
        import csv
        from io import StringIO

        if isinstance(data, dict):
            if "data" in data and isinstance(data["data"], list):
                data = data["data"]
            else:
                data = [data]

        if not data:
            return ""

        output = StringIO()
        keys = []
        for item in data:
            for key in item.keys():
                if key not in keys:
                    keys.append(key)

        writer = csv.DictWriter(output, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

        return output.getvalue()

    def format_tree(self, data: Dict, *, title: str = "Data") -> str:
        """Format data as a tree structure.

        Args:
            data: Dictionary to format
            title: Tree title

        Returns:
            Tree string
        """
        if RICH_AVAILABLE and self.console:
            return self._format_rich_tree(data, title=title)
        else:
            return self._format_simple_tree(data, title=title)

    def _format_rich_tree(self, data: Dict, *, title: str = "Data") -> str:
        """Format data as a rich tree.

        Args:
            data: Dictionary to format
            title: Tree title

        Returns:
            Formatted tree
        """
        tree = Tree(f"[bold cyan]{title}[/bold cyan]")
        self._add_tree_nodes(tree, data)

        from io import StringIO
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=False)
        console.print(tree)
        return string_io.getvalue()

    def _add_tree_nodes(self, parent: Any, data: Any) -> None:
        """Recursively add nodes to a tree.

        Args:
            parent: Parent tree node
            data: Data to add
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    branch = parent.add(f"[yellow]{key}[/yellow]")
                    self._add_tree_nodes(branch, value)
                else:
                    parent.add(f"[yellow]{key}[/yellow]: {self._format_value(value)}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    branch = parent.add(f"[yellow][{i}][/yellow]")
                    self._add_tree_nodes(branch, item)
                else:
                    parent.add(f"[yellow][{i}][/yellow]: {self._format_value(item)}")

    def _format_simple_tree(
        self, data: Dict, *, title: str = "Data", indent: int = 0
    ) -> str:
        """Format data as a simple ASCII tree.

        Args:
            data: Dictionary to format
            title: Tree title
            indent: Current indentation level

        Returns:
            ASCII tree string
        """
        lines = []
        if indent == 0:
            lines.append(title)

        prefix = "  " * indent

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{prefix}├─ {key}:")
                    lines.append(
                        self._format_simple_tree(value, title="", indent=indent + 1)
                    )
                else:
                    lines.append(f"{prefix}├─ {key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}├─ [{i}]:")
                    lines.append(
                        self._format_simple_tree(item, title="", indent=indent + 1)
                    )
                else:
                    lines.append(f"{prefix}├─ [{i}]: {item}")

        return "\n".join(lines)

    def _filter_essential_columns(self, data: List[Dict]) -> List[Dict]:
        """Filter data to show only essential columns for better readability.

        Args:
            data: List of dictionaries

        Returns:
            Filtered list with only essential columns
        """
        if not data:
            return data

        # Detect data type based on keys in first item
        first_item = data[0]
        
        # If first item is not a dict, return as-is
        if not isinstance(first_item, dict):
            return data
        
        # Define essential columns for different entity types
        essential_columns = {
            # Agents
            "agent": ["id", "name", "status", "model_name", "total_conversations", "total_messages", "created_at"],
            # Documents
            "document": ["id", "original_filename", "status", "word_count", "document_type", "created_at"],
            # Database connections
            "database": ["id", "name", "database_type", "host", "status", "created_at"],
            # Conversations
            "conversation": ["id", "title", "agent_id", "status", "message_count", "created_at"],
            # Leads
            "lead": ["id", "name", "email", "phone", "status", "source", "created_at"],
            # Companies
            "company": ["id", "name", "status", "subscription_tier", "created_at"],
            # Users
            "user": ["id", "username", "email", "role", "status", "last_login"],
        }

        # Detect entity type
        entity_type = None
        if "model_name" in first_item or "llm_settings_id" in first_item:
            entity_type = "agent"
        elif "original_filename" in first_item or "document_type" in first_item:
            entity_type = "document"
        elif "database_type" in first_item or "host" in first_item:
            entity_type = "database"
        elif "message_count" in first_item or "agent_id" in first_item:
            entity_type = "conversation"
        elif "subscription_tier" in first_item or "company_name" in first_item:
            entity_type = "company"
        elif "username" in first_item and "role" in first_item:
            entity_type = "user"
        elif "source" in first_item and "email" in first_item:
            entity_type = "lead"

        # If entity type detected, filter columns
        if entity_type and entity_type in essential_columns:
            columns = essential_columns[entity_type]
            filtered_data = []
            for item in data:
                if isinstance(item, dict):
                    filtered_item = {k: v for k, v in item.items() if k in columns}
                    filtered_data.append(filtered_item)
            return filtered_data

        # If too many columns (>10), show only first 10
        if len(first_item) > 10:
            keys_to_show = list(first_item.keys())[:10]
            filtered_data = []
            for item in data:
                if isinstance(item, dict):
                    filtered_item = {k: v for k, v in item.items() if k in keys_to_show}
                    filtered_data.append(filtered_item)
            return filtered_data

        return data

    @staticmethod
    def _format_header(key: str) -> str:
        """Format a header key.

        Args:
            key: Header key

        Returns:
            Formatted header
        """
        # Convert snake_case to Title Case
        return key.replace("_", " ").title()

    @staticmethod
    def _format_value(value: Any) -> str:
        """Format a value for display.

        Args:
            value: Value to format

        Returns:
            Formatted value string
        """
        if value is None:
            return ""
        if isinstance(value, bool):
            return "✓" if value else "✗"
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(value, (dict, list)):
            return json.dumps(value, default=str)
        return str(value)


def format_output(
    data: Any, format_type: str = "json", *, title: Optional[str] = None
) -> str:
    """Convenience function to format output.

    Args:
        data: Data to format
        format_type: Output format
        title: Optional title for tree format

    Returns:
        Formatted string
    """
    formatter = Formatter(format_type)
    if format_type == "tree" and title:
        return formatter.format_tree(data, title=title)
    return formatter.format(data)
