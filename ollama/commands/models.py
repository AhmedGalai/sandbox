"""
Model management commands - list, use, and pull Ollama models.
"""

import logging
from typing import Any, Dict, List, Tuple

from rich.panel import Panel
from rich.table import Table

from .base import BaseCommand

logger = logging.getLogger(__name__)


class ModelsCommand(BaseCommand):
    """List all available Ollama models installed locally."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the models list command.

        Args:
            args: Command arguments
            context: Shared context with OllamaClient

        Returns:
            Tuple of (success, output_message)
        """
        client = context.get("ollama_client")
        if not client:
            return False, "Ollama client not available"

        try:
            # Get available models
            models = await client.list_models()

            if not models:
                self.console.print(
                    "[yellow]No models found. Use /pull <model> to download one.[/yellow]"
                )
                return True, ""

            # Create table
            table = Table(
                title="Available Models",
                show_header=True,
                header_style="bold cyan",
            )
            table.add_column("Model Name", style="green")
            table.add_column("Size", style="yellow")
            table.add_column("Modified", style="white")

            for model in models:
                name = model.get("name", "unknown")
                size = model.get("size", "unknown")
                modified = model.get("modified_at", "unknown")

                # Format size
                if isinstance(size, (int, float)):
                    if size > 1e9:
                        size_str = f"{size / 1e9:.2f} GB"
                    elif size > 1e6:
                        size_str = f"{size / 1e6:.2f} MB"
                    else:
                        size_str = f"{size / 1e3:.2f} KB"
                else:
                    size_str = str(size)

                table.add_row(name, size_str, str(modified)[:10])

            self.console.print(Panel(table, title="[bold]Models[/bold]"))
            return True, ""

        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return False, f"Failed to list models: {e}"

    def get_help_text(self) -> str:
        """Return help text for the models command."""
        return """[bold cyan]/models[/bold cyan]

List all Ollama models installed locally.

Usage:
  /models            - Show all installed models

Related Commands:
  /use MODEL         - Switch the default model
  /pull MODEL        - Download a new model

The /models command connects to your local Ollama instance
and lists all models that have been downloaded.
"""


class UseCommand(BaseCommand):
    """Switch the default model used by agents."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the use model command.

        Args:
            args: Command arguments [model_name]
            context: Shared context

        Returns:
            Tuple of (success, output_message)
        """
        if not args:
            return False, "Please specify a model name"

        try:
            model_name = args[0]

            # Get settings and update
            settings = context.get("settings")
            if not settings:
                return False, "Settings not available"

            # Update default model
            old_model = settings.default_model
            settings.default_model = model_name

            # Also update in context if available
            context["current_model"] = model_name

            output = (
                f"[green]Default model switched from "
                f"[yellow]{old_model}[/yellow] to "
                f"[yellow]{model_name}[/yellow][/green]"
            )
            self.console.print(f"\n{output}\n")

            return True, ""

        except Exception as e:
            logger.error(f"Error switching model: {e}")
            return False, f"Failed to switch model: {e}"

    def get_help_text(self) -> str:
        """Return help text for the use command."""
        return """[bold cyan]/use[/bold cyan] <model_name>

Switch the default model used by agents.

Usage:
  /use llama3.2:3b
  /use qwen2.5:7b
  /use mistral:latest

Run /models to see available options.

The model you specify will be used as the default for all
agents until you switch to a different model.
"""


class PullCommand(BaseCommand):
    """Download a new model from Ollama repository."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the pull model command.

        Args:
            args: Command arguments [model_name]
            context: Shared context with OllamaClient

        Returns:
            Tuple of (success, output_message)
        """
        if not args:
            return False, "Please specify a model name"

        client = context.get("ollama_client")
        if not client:
            return False, "Ollama client not available"

        try:
            model_name = args[0]

            self.console.print(
                f"\n[cyan]Pulling model: {model_name}[/cyan]\n"
            )

            # Pull the model
            result = await client.pull_model(model_name)

            if result:
                self.console.print(
                    f"[green]Successfully pulled model: {model_name}[/green]\n"
                )
                return True, ""
            else:
                return False, f"Failed to pull model: {model_name}"

        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False, f"Failed to pull model: {e}"

    def get_help_text(self) -> str:
        """Return help text for the pull command."""
        return """[bold cyan]/pull[/bold cyan] <model_name>

Download a new model from the Ollama repository.

Usage:
  /pull llama3.2:3b
  /pull qwen2.5:7b
  /pull mistral:latest
  /pull neural-chat:latest

Popular Models:
  llama3.2:3b        - Small, fast Llama model
  qwen2.5:7b         - Qwen 2.5 7B model
  mistral:latest     - Mistral instruction-tuned model
  neural-chat:latest - Neural Chat model
  llava:7b           - Vision model for image analysis

Note: Models can be large (500MB to 10GB+). Download time
depends on your internet speed.
"""
