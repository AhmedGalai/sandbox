"""
Help command - display available commands and their descriptions.
"""

from typing import Any, Dict, List, Tuple

from rich.table import Table

from .base import BaseCommand


class HelpCommand(BaseCommand):
    """Display all available commands with descriptions and usage."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the help command.

        Args:
            args: Command arguments
            context: Shared context

        Returns:
            Tuple of (success, output_message)
        """
        if args and len(args) > 0:
            # Help for specific command
            command_name = args[0].lower()
            return await self._show_command_help(command_name, context)
        else:
            # Show all commands
            self._show_all_commands(context)
            return True, ""

    def _show_all_commands(self, context: Dict[str, Any]) -> None:
        """Display all available commands grouped by category."""
        # Create command registry from context
        registry = context.get("command_registry", {})

        # Group commands by category
        categories = {
            "System": ["help", "clear", "exit"],
            "Agents": ["agents", "researcher", "developer", "planner"],
            "Vision": ["vision"],
            "Models": ["models", "use", "pull"],
            "Utilities": ["history", "export"],
            "Settings": ["settings"],
        }

        self.console.print("\n[bold cyan]Available Commands[/bold cyan]\n")

        for category, commands in categories.items():
            # Filter to only existing commands
            available_in_category = [
                cmd for cmd in commands if cmd in registry or cmd in ["exit"]
            ]

            if available_in_category:
                self.console.print(f"[bold yellow]{category}:[/bold yellow]")

                for cmd in available_in_category:
                    if cmd == "exit":
                        self.console.print(
                            f"  [cyan]/exit, /quit, /q[/cyan] - Exit the CLI"
                        )
                    elif cmd in registry:
                        cmd_class = registry[cmd]
                        cmd_instance = cmd_class(self.console)
                        desc = cmd_instance.description.split("\n")[0]
                        self.console.print(f"  [cyan]/{cmd}[/cyan] - {desc}")

                self.console.print()

        # Show aliases
        self.console.print("[bold yellow]Aliases:[/bold yellow]")
        self.console.print("  [cyan]/?[/cyan] - Help")
        self.console.print("  [cyan]/h[/cyan] - Help")
        self.console.print("  [cyan]/cls[/cyan] - Clear screen")
        self.console.print()

        # Show tips
        self.console.print("[bold cyan]Tips:[/bold cyan]")
        self.console.print("  - Type [cyan]/help <command>[/cyan] for command details")
        self.console.print("  - Use [cyan]/history[/cyan] to view past interactions")
        self.console.print("  - Use [cyan]/export[/cyan] to save conversations")
        self.console.print()

    async def _show_command_help(
        self, command_name: str, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Display detailed help for a specific command.

        Args:
            command_name: Name of command to get help for
            context: Shared context

        Returns:
            Tuple of (success, output_message)
        """
        registry = context.get("command_registry", {})

        if command_name in registry:
            cmd_class = registry[command_name]
            cmd_instance = cmd_class(self.console)
            help_text = cmd_instance.get_help_text()
            self.console.print(f"\n{help_text}\n")
            return True, ""
        elif command_name == "exit":
            self.console.print("\n[bold cyan]/exit, /quit[/bold cyan]")
            self.console.print("Exit the CLI application.\n")
            return True, ""
        else:
            return False, f"Command '{command_name}' not found"

    def get_help_text(self) -> str:
        """Return help text for the help command."""
        return """[bold cyan]/help[/bold cyan] [command]

Display available commands or get detailed help for a specific command.

Usage:
  /help              - Show all available commands
  /help agents       - Show detailed help for /agents command
  /help vision       - Show detailed help for /vision command
  /help models       - Show detailed help for /models command

Aliases:
  /?                 - Same as /help
  /h                 - Same as /help
"""
