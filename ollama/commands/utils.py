"""
Utility commands - clear, history, and export.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from rich.panel import Panel
from rich.table import Table

from .base import BaseCommand

logger = logging.getLogger(__name__)


class ClearCommand(BaseCommand):
    """Clear the console screen and conversation history."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the clear command.

        Args:
            args: Command arguments
            context: Shared context with conversation manager

        Returns:
            Tuple of (success, output_message)
        """
        try:
            # Clear the console
            self.console.clear()

            # Clear conversation history if available
            conversation_manager = context.get("conversation_manager")
            if conversation_manager:
                await conversation_manager.clear()

            return True, ""

        except Exception as e:
            logger.error(f"Error clearing: {e}")
            return False, f"Failed to clear: {e}"

    def get_help_text(self) -> str:
        """Return help text for the clear command."""
        return """[bold cyan]/clear[/bold cyan]

Clear the console screen and conversation history.

Usage:
  /clear             - Clear screen and history

Aliases:
  /cls               - Same as /clear

This command removes all text from the screen and clears the
conversation history stored in memory.
"""


class HistoryCommand(BaseCommand):
    """Display recent conversation history."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the history command.

        Args:
            args: Command arguments [--limit N]
            context: Shared context with conversation manager

        Returns:
            Tuple of (success, output_message)
        """
        try:
            # Parse arguments
            limit = 20
            if args:
                if args[0].isdigit():
                    limit = int(args[0])

            conversation_manager = context.get("conversation_manager")
            if not conversation_manager:
                return False, "Conversation manager not available"

            # Get history
            history = await conversation_manager.get_history(limit=limit)

            if not history:
                self.console.print(
                    "[yellow]No conversation history available.[/yellow]"
                )
                return True, ""

            # Create table
            table = Table(
                title=f"Conversation History (last {limit})",
                show_header=True,
                header_style="bold cyan",
            )
            table.add_column("Time", style="cyan")
            table.add_column("Role", style="yellow")
            table.add_column("Message", style="white", width=50)

            for entry in history:
                timestamp = entry.get("timestamp", "unknown")
                role = entry.get("role", "unknown")
                message = entry.get("content", "")

                # Truncate long messages
                if len(message) > 50:
                    message = message[:47] + "..."

                table.add_row(str(timestamp)[:19], role, message)

            self.console.print(Panel(table, title="[bold]History[/bold]"))
            return True, ""

        except Exception as e:
            logger.error(f"Error retrieving history: {e}")
            return False, f"Failed to retrieve history: {e}"

    def get_help_text(self) -> str:
        """Return help text for the history command."""
        return """[bold cyan]/history[/bold cyan] [limit]

Display recent conversation history.

Usage:
  /history           - Show last 20 messages
  /history 50        - Show last 50 messages
  /history 100       - Show last 100 messages

History is automatically saved and persists across sessions.
See /export to save conversations to a file.
"""


class ExportCommand(BaseCommand):
    """Export conversation history to a file (markdown or JSON)."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the export command.

        Args:
            args: Command arguments [filename] [--format FORMAT]
            context: Shared context with conversation manager

        Returns:
            Tuple of (success, output_message)
        """
        try:
            # Parse arguments
            positional, named = self.parse_arguments(
                args, named_params=["format"]
            )

            # Get filename
            if positional:
                filename = positional[0]
            else:
                filename = (
                    f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )

            # Get format
            file_format = named.get("format", "markdown")
            if file_format not in ["markdown", "json"]:
                return False, "Format must be 'markdown' or 'json'"

            conversation_manager = context.get("conversation_manager")
            if not conversation_manager:
                return False, "Conversation manager not available"

            # Get all history
            history = await conversation_manager.get_history(limit=None)

            if not history:
                return False, "No conversation history to export"

            # Create output path
            if not filename.endswith(f".{file_format}"):
                filename = f"{filename}.{file_format}"

            output_path = (
                Path.home() / ".ollama_agents" / "exports" / filename
            )
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Export based on format
            if file_format == "json":
                with open(output_path, "w") as f:
                    json.dump(history, f, indent=2, default=str)
            else:  # markdown
                with open(output_path, "w") as f:
                    f.write("# Conversation Export\n\n")
                    f.write(
                        f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    )

                    for entry in history:
                        role = entry.get("role", "Unknown")
                        content = entry.get("content", "")
                        timestamp = entry.get("timestamp", "")

                        f.write(f"**{role}** ({timestamp})\n")
                        f.write(f"{content}\n\n")

            self.console.print(
                f"[green]Conversation exported to: {output_path}[/green]\n"
            )
            return True, ""

        except Exception as e:
            logger.error(f"Error exporting conversation: {e}")
            return False, f"Failed to export conversation: {e}"

    def get_help_text(self) -> str:
        """Return help text for the export command."""
        return """[bold cyan]/export[/bold cyan] [filename] [options]

Export conversation history to a file.

Usage:
  /export                    - Export to timestamped file
  /export my_conversation    - Export to my_conversation.markdown
  /export data --format json - Export as JSON format

Options:
  --format FORMAT            - Output format: markdown or json (default: markdown)

Exports are saved to ~/.ollama_agents/exports/

Formats:
  markdown               - Human-readable markdown format
  json                   - Machine-readable JSON format
"""
