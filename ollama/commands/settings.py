"""
Settings command - view and modify configuration.
"""

import logging
from typing import Any, Dict, List, Tuple

from rich.panel import Panel
from rich.table import Table

from .base import BaseCommand

logger = logging.getLogger(__name__)


class SettingsCommand(BaseCommand):
    """View and modify application settings interactively."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the settings command.

        Args:
            args: Command arguments [--view, --set, etc.]
            context: Shared context with settings

        Returns:
            Tuple of (success, output_message)
        """
        try:
            settings = context.get("settings")
            if not settings:
                return False, "Settings not available"

            if not args or args[0] == "view":
                # Show current settings
                self._show_settings(settings, context)
                return True, ""
            elif args[0] == "agents":
                # Show agent assignments
                self._show_agent_settings(settings, context)
                return True, ""
            else:
                return False, "Unknown settings option"

        except Exception as e:
            logger.error(f"Error in settings command: {e}")
            return False, f"Settings error: {e}"

    def _show_settings(
        self, settings: Any, context: Dict[str, Any]
    ) -> None:
        """Display current application settings."""
        table = Table(
            title="Application Settings",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Setting", style="green")
        table.add_column("Value", style="yellow")

        # Ollama settings
        table.add_row("Ollama Host", settings.ollama_host)
        table.add_row("Request Timeout", f"{settings.timeout}s")

        # Concurrency settings
        table.add_row(
            "Max Concurrent Agents", str(settings.max_concurrent_agents)
        )

        # Model settings
        table.add_row("Default Model", settings.default_model)

        # Logging settings
        table.add_row("Log Level", settings.log_level)

        self.console.print(Panel(table, title="[bold]Settings[/bold]"))

    def _show_agent_settings(
        self, settings: Any, context: Dict[str, Any]
    ) -> None:
        """Display agent-specific settings."""
        model_mappings = settings.model_mappings

        table = Table(
            title="Agent Model Assignments",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Agent", style="green")
        table.add_column("Assigned Model", style="yellow")

        agents = ["researcher", "developer", "planner", "vision"]
        for agent in agents:
            model = model_mappings.get(agent, "default")
            table.add_row(agent, model)

        self.console.print(Panel(table, title="[bold]Agent Settings[/bold]"))

    def get_help_text(self) -> str:
        """Return help text for the settings command."""
        return """[bold cyan]/settings[/bold cyan] [option]

View and modify application settings.

Usage:
  /settings              - Show all settings
  /settings view         - Show all settings
  /settings agents       - Show agent-specific settings

Available Options:
  (no option)            - Display current settings
  view                   - Display current settings
  agents                 - Show agent model assignments

Settings Categories:
  - Ollama Configuration (host, timeout)
  - Concurrency Settings (max concurrent agents)
  - Model Configuration (default model, agent assignments)
  - Logging Settings (log level)

To modify settings, edit the .env file or set environment variables.
"""
