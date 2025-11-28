"""
Agent-related commands for managing and invoking agents.
"""

import logging
from typing import Any, Dict, List, Tuple

from rich.panel import Panel
from rich.table import Table

from .base import BaseCommand

logger = logging.getLogger(__name__)


class AgentsCommand(BaseCommand):
    """List all available agents with their status and assigned models."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the agents list command.

        Args:
            args: Command arguments
            context: Shared context with agent factory

        Returns:
            Tuple of (success, output_message)
        """
        factory = context.get("agent_factory")
        if not factory:
            return False, "Agent factory not available"

        try:
            agents = factory.get_available_agents()

            # Create table
            table = Table(
                title="Available Agents",
                show_header=True,
                header_style="bold cyan",
            )
            table.add_column("Agent", style="green")
            table.add_column("Model", style="yellow")
            table.add_column("Description", style="white")

            for agent_type, info in agents.items():
                description = info.get("description", "No description")
                table.add_row(agent_type, info.get("model", "unknown"), description)

            self.console.print(Panel(table, title="[bold]Agents[/bold]"))
            return True, ""

        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return False, f"Failed to list agents: {e}"

    def get_help_text(self) -> str:
        """Return help text for the agents command."""
        return """[bold cyan]/agents[/bold cyan]

List all available agents with their assigned models and descriptions.

Usage:
  /agents            - Show all available agents

Related Commands:
  /researcher        - Invoke researcher agent directly
  /developer         - Invoke developer agent directly
  /planner           - Invoke planner agent directly
"""


class ResearcherCommand(BaseCommand):
    """Invoke the researcher agent for information gathering and analysis."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the researcher agent.

        Args:
            args: Command arguments (query and optional parameters)
            context: Shared context with orchestrator

        Returns:
            Tuple of (success, output_message)
        """
        if not args:
            return False, "Please provide a query for the researcher agent"

        factory = context.get("agent_factory")
        orchestrator = context.get("orchestrator")
        if not factory or not orchestrator:
            return False, "Agent factory or orchestrator not available"

        try:
            # Parse arguments
            positional, named = self.parse_arguments(
                args, named_params=["model", "context"]
            )

            query = " ".join(positional)
            model = named.get("model")

            # Create agent
            agent_config = {"name": "researcher"}
            if model:
                agent_config["model"] = model

            agent = factory.create_agent("researcher", agent_config)

            # Prepare context
            execution_context = {
                "task": query,
                "context": named.get("context", "general research"),
                "expected_output": "comprehensive research findings",
            }

            # Show status
            self.console.print(
                f"\n[cyan]Invoking researcher agent...[/cyan]\n"
            )

            # Execute with orchestrator
            from ..core.orchestrator import TaskPriority

            task_id = await orchestrator.dispatch_task(
                agent, execution_context, priority=TaskPriority.NORMAL
            )

            return True, f"Task {task_id} dispatched to researcher"

        except Exception as e:
            logger.error(f"Error invoking researcher: {e}")
            return False, f"Failed to invoke researcher: {e}"

    def get_help_text(self) -> str:
        """Return help text for the researcher command."""
        return """[bold cyan]/researcher[/bold cyan] <query> [options]

Invoke the researcher agent to gather and analyze information.

Usage:
  /researcher "how does photosynthesis work"
  /researcher "latest AI trends" --context "technology"
  /researcher "climate change impacts" --model llama3.2:3b

Options:
  --model MODEL      - Specify a different model to use
  --context TEXT     - Provide additional context for the research

The researcher agent uses a language model to gather, analyze, and
synthesize information about your query.
"""


class DeveloperCommand(BaseCommand):
    """Invoke the developer agent for code generation and technical tasks."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the developer agent.

        Args:
            args: Command arguments (task and optional parameters)
            context: Shared context with orchestrator

        Returns:
            Tuple of (success, output_message)
        """
        if not args:
            return False, "Please provide a task for the developer agent"

        factory = context.get("agent_factory")
        orchestrator = context.get("orchestrator")
        if not factory or not orchestrator:
            return False, "Agent factory or orchestrator not available"

        try:
            # Parse arguments
            positional, named = self.parse_arguments(
                args, named_params=["model", "language"]
            )

            task = " ".join(positional)
            model = named.get("model")

            # Create agent
            agent_config = {"name": "developer"}
            if model:
                agent_config["model"] = model

            agent = factory.create_agent("developer", agent_config)

            # Prepare context
            execution_context = {
                "task": task,
                "language": named.get("language", "python"),
                "expected_output": "working code implementation",
            }

            # Show status
            self.console.print(
                f"\n[cyan]Invoking developer agent...[/cyan]\n"
            )

            # Execute with orchestrator
            from ..core.orchestrator import TaskPriority

            task_id = await orchestrator.dispatch_task(
                agent, execution_context, priority=TaskPriority.NORMAL
            )

            return True, f"Task {task_id} dispatched to developer"

        except Exception as e:
            logger.error(f"Error invoking developer: {e}")
            return False, f"Failed to invoke developer: {e}"

    def get_help_text(self) -> str:
        """Return help text for the developer command."""
        return """[bold cyan]/developer[/bold cyan] <task> [options]

Invoke the developer agent for code generation and technical tasks.

Usage:
  /developer "create a REST API endpoint"
  /developer "fix this bug in my code" --language javascript
  /developer "write unit tests" --model llama3.2:3b

Options:
  --model MODEL      - Specify a different model to use
  --language LANG    - Programming language (default: python)

The developer agent specializes in code generation, debugging,
and technical implementation tasks.
"""


class PlannerCommand(BaseCommand):
    """Invoke the planner agent for planning and strategy tasks."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the planner agent.

        Args:
            args: Command arguments (task and optional parameters)
            context: Shared context with orchestrator

        Returns:
            Tuple of (success, output_message)
        """
        if not args:
            return False, "Please provide a planning task for the planner agent"

        factory = context.get("agent_factory")
        orchestrator = context.get("orchestrator")
        if not factory or not orchestrator:
            return False, "Agent factory or orchestrator not available"

        try:
            # Parse arguments
            positional, named = self.parse_arguments(
                args, named_params=["model", "scope"]
            )

            task = " ".join(positional)
            model = named.get("model")

            # Create agent
            agent_config = {"name": "planner"}
            if model:
                agent_config["model"] = model

            agent = factory.create_agent("planner", agent_config)

            # Prepare context
            execution_context = {
                "task": task,
                "scope": named.get("scope", "project"),
                "expected_output": "detailed plan with steps and timeline",
            }

            # Show status
            self.console.print(
                f"\n[cyan]Invoking planner agent...[/cyan]\n"
            )

            # Execute with orchestrator
            from ..core.orchestrator import TaskPriority

            task_id = await orchestrator.dispatch_task(
                agent, execution_context, priority=TaskPriority.NORMAL
            )

            return True, f"Task {task_id} dispatched to planner"

        except Exception as e:
            logger.error(f"Error invoking planner: {e}")
            return False, f"Failed to invoke planner: {e}"

    def get_help_text(self) -> str:
        """Return help text for the planner command."""
        return """[bold cyan]/planner[/bold cyan] <task> [options]

Invoke the planner agent for planning and strategy tasks.

Usage:
  /planner "create a project roadmap for next quarter"
  /planner "plan a website redesign" --scope "full-site"
  /planner "organize team workflow" --model qwen2.5:7b

Options:
  --model MODEL      - Specify a different model to use
  --scope SCOPE      - Scope of planning (default: project)

The planner agent specializes in creating detailed plans,
strategies, and actionable steps for various projects.
"""
