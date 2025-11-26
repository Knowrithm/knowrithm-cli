"""Interactive dashboard command."""

from __future__ import annotations

import os
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

console = Console()


KNOWRITHM_LOGO = """
██╗  ██╗███╗   ██╗ ██████╗ ██╗    ██╗██████╗ ██╗████████╗██╗  ██╗███╗   ███╗
██║ ██╔╝████╗  ██║██╔═══██╗██║    ██║██╔══██╗██║╚══██╔══╝██║  ██║████╗ ████║
█████╔╝ ██╔██╗ ██║██║   ██║██║ █╗ ██║██████╔╝██║   ██║   ███████║██╔████╔██║
██╔═██╗ ██║╚██╗██║██║   ██║██║███╗██║██╔══██╗██║   ██║   ██╔══██║██║╚██╔╝██║
██║  ██╗██║ ╚████║╚██████╔╝╚███╔███╔╝██║  ██║██║   ██║   ██║  ██║██║ ╚═╝ ██║
╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝
"""


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def create_commands_table() -> Table:
    """Create a table with main commands."""
    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="cyan",
        title="📋 Main Commands",
        title_style="bold magenta"
    )
    
    table.add_column("Command", style="cyan", width=20)
    table.add_column("Description", style="white")
    table.add_column("Example", style="green")
    
    commands = [
        ("🤖 agent", "Manage AI agents", "knowrithm agent list"),
        ("💬 conversation", "Manage conversations", "knowrithm conversation list"),
        ("📄 document", "Manage documents", "knowrithm document list"),
        ("👥 lead", "Manage leads", "knowrithm lead list"),
        ("🏢 company", "Manage companies", "knowrithm company current"),
        ("🔐 auth", "Authentication", "knowrithm auth login"),
        ("📊 analytics", "View analytics", "knowrithm analytics dashboard"),
        ("⚙️  settings", "LLM settings", "knowrithm settings list"),
        ("🌐 website", "Website sources", "knowrithm website list"),
        ("🗄️  database", "Database connections", "knowrithm database list"),
        ("👨‍💼 admin", "Admin commands", "knowrithm admin users list"),
        ("🔧 system", "System utilities", "knowrithm system health"),
    ]
    
    for cmd, desc, example in commands:
        table.add_row(cmd, desc, example)
    
    return table


def create_quick_actions_panel() -> Panel:
    """Create a panel with quick actions."""
    quick_actions = Text()
    quick_actions.append("🚀 Quick Actions:\n\n", style="bold yellow")
    quick_actions.append("  • Setup wizard: ", style="white")
    quick_actions.append("knowrithm config init\n", style="cyan")
    quick_actions.append("  • Login: ", style="white")
    quick_actions.append("knowrithm auth login\n", style="cyan")
    quick_actions.append("  • Create agent: ", style="white")
    quick_actions.append("knowrithm agent create\n", style="cyan")
    quick_actions.append("  • Interactive chat: ", style="white")
    quick_actions.append("knowrithm conversation chat <id> -i\n", style="cyan")
    quick_actions.append("  • View help: ", style="white")
    quick_actions.append("knowrithm --help\n", style="cyan")
    
    return Panel(
        quick_actions,
        border_style="yellow",
        padding=(1, 2)
    )


def create_info_panel() -> Panel:
    """Create an info panel."""
    info = Text()
    info.append("ℹ️  Information:\n\n", style="bold blue")
    info.append("  • Documentation: ", style="white")
    info.append("https://docs.knowrithm.org\n", style="blue underline")
    info.append("  • Support: ", style="white")
    info.append("agentx@notifications.knowrithm.org\n", style="blue")
    info.append("  • Version: ", style="white")
    info.append("1.0.0\n", style="green")
    
    return Panel(
        info,
        border_style="blue",
        padding=(1, 2)
    )


@click.command(name="dashboard")
def cmd() -> None:
    """Launch the interactive Knowrithm dashboard.
    
    This command clears the screen and displays a beautiful dashboard
    with the Knowrithm logo, main commands, and quick actions.
    """
    # Clear screen
    clear_screen()
    
    # Print logo with gradient effect
    console.print()
    logo_text = Text(KNOWRITHM_LOGO)
    logo_text.stylize("bold cyan")
    console.print(Align.center(logo_text))
    
    # Tagline
    tagline = Text("🚀 AI-Powered Platform CLI", style="bold white")
    console.print(Align.center(tagline))
    console.print(Align.center(Text("One Platform. Unlimited AI Agents.", style="italic cyan")))
    console.print()
    
    # Separator
    console.print("═" * console.width, style="cyan")
    console.print()
    
    # Main commands table
    commands_table = create_commands_table()
    console.print(Align.center(commands_table))
    console.print()
    
    # Create grid for quick actions and info
    grid = Table.grid(expand=True, padding=1)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_row(create_quick_actions_panel(), create_info_panel())
    console.print(grid)
    console.print()
    
    # Footer
    footer = Text()
    footer.append("💡 Tip: ", style="bold yellow")
    footer.append("Type ", style="white")
    footer.append("knowrithm <command> --help", style="cyan")
    footer.append(" for detailed information about any command", style="white")
    console.print(Align.center(footer))
    console.print()
    console.print("═" * console.width, style="cyan")
    console.print()
