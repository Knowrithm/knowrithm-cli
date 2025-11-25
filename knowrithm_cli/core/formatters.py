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

        # Handle single dict
        if isinstance(data, dict):
            # Check if it contains a list under 'data' key
            if "data" in data and isinstance(data["data"], list):
                data = data["data"]
            else:
                # Convert single dict to list
                data = [data]

        if not isinstance(data, list) or not data:
            return "No data to display"

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

        # Get all unique keys
        keys = []
        for item in data:
            for key in item.keys():
                if key not in keys:
                    keys.append(key)

        # Create table
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")

        # Add columns
        for key in keys:
            table.add_column(self._format_header(key), overflow="fold")

        # Add rows
        for item in data:
            row = []
            for key in keys:
                value = item.get(key, "")
                row.append(self._format_value(value))
            table.add_row(*row)

        # Render to string
        from io import StringIO
        string_io = StringIO()
        console = Console(file=string_io, force_terminal=False)
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
