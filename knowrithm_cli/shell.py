"""Interactive shell mode for Knowrithm CLI."""

import os
import shlex
import subprocess
import sys
import click
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

LOGO = r"""
██╗  ██╗███╗   ██╗ ██████╗ ██╗    ██╗██████╗ ██╗████████╗██╗  ██╗███╗   ███╗
██║ ██╔╝████╗  ██║██╔═══██╗██║    ██║██╔══██╗██║╚══██╔══╝██║  ██║████╗ ████║
█████╔╝ ██╔██╗ ██║██║   ██║██║ █╗ ██║██████╔╝██║   ██║   ███████║██╔████╔██║
██╔═██╗ ██║╚██╗██║██║   ██║██║███╗██║██╔══██╗██║   ██║   ██╔══██║██║╚██╔╝██║
██║  ██╗██║ ╚████║╚██████╔╝╚███╔███╔╝██║  ██║██║   ██║   ██║  ██║██║ ╚═╝ ██║
╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝
"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    console.print(Panel(Align.center(Text(LOGO, style="bold cyan")), title="Knowrithm CLI", subtitle="Interactive Mode"))

def run_interactive_mode(ctx: click.Context):
    """Run the interactive shell loop."""
    # Initial clear and header
    clear_screen()
    print_header()

    while True:
        try:
            # Show prompt
            command_input = console.input("[bold green]knowrithm>[/bold green] ")
        except (EOFError, KeyboardInterrupt):
            console.print("\nGoodbye!")
            break

        if not command_input.strip():
            continue

        if command_input.strip().lower() in ('exit', 'quit'):
            break

        # Clear screen and show header before executing command
        clear_screen()
        print_header()
        
        # Show what command was run (optional, but good for context)
        console.print(f"[dim]> {command_input}[/dim]")
        console.print()

        parts = shlex.split(command_input)
        cmd_name = parts[0]
        args = parts[1:]

        # Handle built-in shell commands
        if cmd_name == 'cd':
            try:
                path = args[0] if args else os.path.expanduser('~')
                os.chdir(path)
                console.print(f"Changed directory to: {os.getcwd()}")
            except Exception as e:
                console.print(f"[red]Error changing directory: {e}[/red]")
            continue
        
        # Handle clear command manually if needed (though we clear automatically)
        if cmd_name == 'clear' or cmd_name == 'cls':
            continue

        # Check if it's a known CLI command
        # ctx.command is the root Group
        if cmd_name in ctx.command.commands:
            try:
                # We need to invoke the command. 
                # Using cli.main() might be risky as it handles system exit.
                # We can construct a new context or use the existing one?
                # The issue is that click commands expect to be run within a context.
                
                # We can try to use the root command to invoke the subcommand.
                # But we need to pass the arguments.
                
                # Let's try to find the command object and invoke it.
                cmd_obj = ctx.command.commands[cmd_name]
                
                # We need to parse args for this command.
                # This is complex because of nested commands.
                # The easiest way is to call the root CLI again but catch SystemExit.
                
                # However, calling the root CLI (ctx.command) with 'parts' might work.
                # We need to make sure we don't recurse into interactive mode if we pass no args (which shouldn't happen here as we have cmd_name).
                
                try:
                    with ctx.scope(cleanup=False):
                        ctx.command.main(args=parts, prog_name="knowrithm", standalone_mode=False)
                except SystemExit as e:
                    if e.code != 0:
                        console.print(f"[red]Command exited with code {e.code}[/red]")
                except Exception as e:
                    console.print(f"[red]Error executing command: {e}[/red]")

            except Exception as e:
                console.print(f"[red]Unexpected error: {e}[/red]")
        else:
            # Pass through to system shell
            try:
                subprocess.run(command_input, shell=True)
            except Exception as e:
                console.print(f"[red]Error executing system command: {e}[/red]")
