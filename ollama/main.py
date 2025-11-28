"""
Enhanced Ollama Multi-Agent CLI with async support and command system.

Full-featured async CLI with:
- Command routing and execution
- Conversation management and history
- Agent orchestration with streaming responses
- Rich formatted output with panels and tables
- Graceful error handling and Ctrl+C support
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from agents.agent_factory import AgentFactory
from commands import COMMAND_ALIASES, COMMAND_REGISTRY
from config.settings import get_settings
from core.conversation import ConversationManager
from core.exceptions import AgentExecutionError
from core.ollama_client import OllamaClient
from core.orchestrator import AgentOrchestrator

# Setup logging
logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Console for rich output
console = Console()


class OllamaAgentCLI:
    """Main CLI application for the Ollama multi-agent system."""

    def __init__(self):
        """Initialize the CLI application."""
        self.console = console
        self.running = False

        # Load configuration
        self.settings = get_settings()
        logger.info(f"Loaded settings from {self.settings}")

        # Initialize core components
        self.ollama_client = OllamaClient(host=self.settings.ollama_host)
        self.agent_factory = AgentFactory(client=self.ollama_client)
        self.orchestrator = AgentOrchestrator(
            max_concurrent=self.settings.max_concurrent_agents
        )

        # Initialize conversation manager
        self.conversation_manager = ConversationManager()

        # Context available to all commands
        self.context: Dict[str, Any] = {
            "settings": self.settings,
            "ollama_client": self.ollama_client,
            "agent_factory": self.agent_factory,
            "orchestrator": self.orchestrator,
            "conversation_manager": self.conversation_manager,
            "command_registry": COMMAND_REGISTRY,
            "cli": self,
        }

        logger.info("Initialized OllamaAgentCLI")

    async def initialize(self) -> None:
        """Initialize async resources."""
        try:
            # Load conversation history
            await self.conversation_manager.load_from_disk()

            # Validate Ollama connection
            try:
                models = await self.ollama_client.list_models()
                logger.info(
                    f"Connected to Ollama with {len(models)} models available"
                )
            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Could not connect to Ollama: {e}[/yellow]"
                )

        except Exception as e:
            logger.error(f"Initialization error: {e}")
            raise

    async def show_welcome_banner(self) -> None:
        """Display welcome banner and initial instructions."""
        self.console.clear()

        banner = """
        [bold cyan]╔══════════════════════════════════════════════════════════╗[/bold cyan]
        [bold cyan]║[/bold cyan]    [bold green]Ollama Multi-Agent AI System[/bold green]
        [bold cyan]║[/bold cyan]    Powered by Llama, Qwen, Mistral, and Llava
        [bold cyan]╚══════════════════════════════════════════════════════════╝[/bold cyan]

        [yellow]Type /help for available commands[/yellow]
        [yellow]Type /exit to quit[/yellow]

        [cyan]Current Model:[/cyan] {model}
        [cyan]Max Concurrent Agents:[/cyan] {max_concurrent}
        """

        self.console.print(
            banner.format(
                model=self.settings.default_model,
                max_concurrent=self.settings.max_concurrent_agents,
            )
        )

    async def run(self) -> None:
        """Run the CLI application main loop."""
        self.running = True

        # Setup signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig, lambda: asyncio.create_task(self.shutdown())
            )

        try:
            await self.initialize()
            await self.show_welcome_banner()

            while self.running:
                try:
                    # Get user input
                    user_input = await self._async_input("[bold cyan]You:[/bold cyan] ")

                    if not user_input.strip():
                        continue

                    # Process input
                    await self.process_input(user_input)

                except EOFError:
                    # Handle Ctrl+D
                    await self.shutdown()
                    break
                except KeyboardInterrupt:
                    # Handle Ctrl+C
                    self.console.print("\n[yellow]Use /exit to quit[/yellow]")
                    continue
                except Exception as e:
                    logger.error(f"Error processing input: {e}")
                    self.console.print(
                        f"[red]Error: {e}[/red]"
                    )

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            self.console.print(f"[red]Fatal error: {e}[/red]")
        finally:
            await self.shutdown()

    async def process_input(self, user_input: str) -> None:
        """
        Process user input and route to appropriate command.

        Args:
            user_input: Raw user input string
        """
        # Save to conversation history
        await self.conversation_manager.add_message("user", user_input)

        # Parse command and arguments
        if user_input.startswith("/"):
            await self._handle_command(user_input)
        else:
            await self._handle_message(user_input)

    async def _handle_command(self, user_input: str) -> None:
        """
        Handle a command (starts with /).

        Args:
            user_input: Raw user input string
        """
        # Extract command and arguments
        command_line = user_input[1:].strip()

        if not command_line:
            return

        parts = command_line.split(None, 1)
        command_name = parts[0].lower()
        args_str = parts[1] if len(parts) > 1 else ""

        # Handle aliases
        if command_name in COMMAND_ALIASES:
            command_name = COMMAND_ALIASES[command_name]

        # Handle special commands
        if command_name in ["exit", "quit", "q"]:
            await self.shutdown()
            return

        # Get command class
        if command_name not in COMMAND_REGISTRY:
            self.console.print(
                f"[red]Unknown command: /{command_name}[/red]"
            )
            self.console.print("[cyan]Type /help for available commands[/cyan]")
            return

        try:
            # Create command instance
            command_class = COMMAND_REGISTRY[command_name]
            command = command_class(self.console)

            # Parse arguments
            args = command._parse_quoted_args(args_str) if args_str else []

            # Execute command with progress indicator
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True,
            ) as progress:
                progress.add_task(
                    description=f"Executing {command_name}...", total=None
                )

                success, output = await command.execute(args, self.context)

            # Handle response
            if success:
                if output:
                    await self.conversation_manager.add_message(
                        "system",
                        output,
                        {"command": command_name},
                    )
                    self.console.print(f"\n{output}\n")
            else:
                error_msg = output or f"Command {command_name} failed"
                await self.conversation_manager.add_message(
                    "system",
                    error_msg,
                    {"command": command_name, "error": True},
                )
                self.console.print(f"[red]{error_msg}[/red]\n")

        except Exception as e:
            logger.error(f"Command execution error: {e}")
            self.console.print(f"[red]Error executing command: {e}[/red]\n")
            await self.conversation_manager.add_message(
                "system",
                f"Command error: {e}",
                {"error": True},
            )

    async def _handle_message(self, message: str) -> None:
        """
        Handle a regular message (non-command).

        Args:
            message: User message text
        """
        self.console.print("[cyan]Feature coming soon...[/cyan]\n")

    async def _async_input(self, prompt: str = "") -> str:
        """
        Get user input asynchronously.

        Args:
            prompt: Input prompt string

        Returns:
            User input string
        """
        # Run input in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.console.input(prompt)
        )

    async def shutdown(self) -> None:
        """Gracefully shutdown the CLI."""
        if not self.running:
            return

        self.running = False

        self.console.print("\n[yellow]Shutting down...[/yellow]")

        try:
            # Close agent factory
            await self.agent_factory.close()

            # Close Ollama client
            await self.ollama_client.close()

            # Save conversation
            await self.conversation_manager._save_to_disk()

            self.console.print("[green]Goodbye![/green]\n")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            sys.exit(0)


async def main() -> None:
    """Main entry point."""
    cli = OllamaAgentCLI()
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[red]Interrupted[/red]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)
