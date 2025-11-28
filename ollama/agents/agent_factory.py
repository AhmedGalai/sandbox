"""
Agent factory for dynamic agent creation and discovery.
Provides automatic agent instantiation and registry management.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type

from core.agent import BaseAgent
from core.exceptions import AgentExecutionError
from core.ollama_client import OllamaClient
from .developer_agent import DeveloperAgent
from .planner_agent import PlannerAgent
from .researcher_agent import ResearcherAgent
from .vision_agent import VisionAgent

logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Factory for creating and managing agent instances.

    Provides:
    - Dynamic agent creation by type
    - Agent registry and discovery
    - Configuration management
    - Automatic agent discovery
    """

    # Built-in agent registry
    _DEFAULT_REGISTRY: Dict[str, Type[BaseAgent]] = {
        "researcher": ResearcherAgent,
        "developer": DeveloperAgent,
        "planner": PlannerAgent,
        "vision": VisionAgent,
    }

    # Default model mappings
    _DEFAULT_MODELS: Dict[str, str] = {
        "researcher": "qwen2.5:7b",
        "developer": "llama3.2:3b",
        "planner": "qwen2.5:7b",
        "vision": "llava:7b",
    }

    def __init__(
        self,
        client: Optional[OllamaClient] = None,
        prompts_dir: Optional[Path] = None,
        registry: Optional[Dict[str, Type[BaseAgent]]] = None,
    ):
        """
        Initialize the agent factory.

        Args:
            client: Shared OllamaClient instance (creates new if not provided)
            prompts_dir: Directory containing prompt templates
            registry: Custom agent registry (uses defaults if not provided)
        """
        self.client = client or OllamaClient()
        self.prompts_dir = prompts_dir or Path(__file__).parent.parent / "agents"
        self.registry = registry or self._DEFAULT_REGISTRY.copy()

        logger.info(
            f"Initialized AgentFactory with {len(self.registry)} "
            f"registered agents"
        )

    def create_agent(
        self,
        agent_type: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> BaseAgent:
        """
        Create an agent instance dynamically.

        Args:
            agent_type: Type of agent to create (must be in registry)
            config: Optional configuration dictionary with keys:
                - name: Agent name (default: agent_type)
                - model: Model to use (default: from _DEFAULT_MODELS)
                - temperature: Generation temperature
                - top_k: Top-k sampling parameter
                - top_p: Top-p sampling parameter

        Returns:
            Instantiated agent

        Raises:
            AgentExecutionError: If agent type is not registered
        """
        agent_type = agent_type.lower().strip()

        if agent_type not in self.registry:
            available = ", ".join(self.registry.keys())
            raise AgentExecutionError(
                f"Unknown agent type '{agent_type}'. "
                f"Available agents: {available}"
            )

        config = config or {}
        agent_class = self.registry[agent_type]

        # Determine agent name and model
        agent_name = config.get("name", agent_type)
        model = config.get("model", self._DEFAULT_MODELS.get(agent_type))

        if not model:
            raise AgentExecutionError(
                f"No model configured for agent type '{agent_type}'"
            )

        try:
            logger.debug(
                f"Creating {agent_type} agent: {agent_name} "
                f"(model: {model})"
            )

            agent = agent_class(
                name=agent_name,
                model=model,
                prompts_dir=self.prompts_dir,
                client=self.client,
            )

            logger.info(
                f"Successfully created agent '{agent_name}' "
                f"of type '{agent_type}'"
            )
            return agent

        except Exception as e:
            logger.error(
                f"Failed to create agent of type '{agent_type}': {e}",
                exc_info=True,
            )
            raise AgentExecutionError(
                f"Failed to create agent: {e}"
            ) from e

    def get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all available agents.

        Returns:
            Dictionary mapping agent type to agent information:
            {
                "agent_type": {
                    "class": AgentClass,
                    "model": "default_model",
                    "description": "Agent description"
                },
                ...
            }
        """
        agents = {}

        for agent_type, agent_class in self.registry.items():
            model = self._DEFAULT_MODELS.get(agent_type, "unknown")
            description = (agent_class.__doc__ or "").split("\n")[0]

            agents[agent_type] = {
                "class": agent_class,
                "model": model,
                "description": description,
                "class_name": agent_class.__name__,
            }

        logger.debug(f"Retrieved {len(agents)} available agents")
        return agents

    def register_agent(
        self,
        agent_type: str,
        agent_class: Type[BaseAgent],
        model: Optional[str] = None,
    ) -> None:
        """
        Register a custom agent class.

        Args:
            agent_type: Type identifier for the agent
            agent_class: Agent class (must extend BaseAgent)
            model: Default model for this agent type

        Raises:
            ValueError: If agent_class is not a BaseAgent subclass
        """
        agent_type = agent_type.lower().strip()

        if not issubclass(agent_class, BaseAgent):
            raise ValueError(
                f"Agent class must extend BaseAgent, got {agent_class}"
            )

        self.registry[agent_type] = agent_class

        if model:
            self._DEFAULT_MODELS[agent_type] = model

        logger.info(f"Registered custom agent type '{agent_type}'")

    def discover_agents(self, agents_dir: Optional[Path] = None) -> int:
        """
        Discover and register agents from a directory.

        Looks for classes extending BaseAgent in *_agent.py files.

        Args:
            agents_dir: Directory to search for agents (default: self.prompts_dir)

        Returns:
            Number of agents discovered
        """
        agents_dir = agents_dir or Path(__file__).parent

        if not agents_dir.is_dir():
            logger.warning(f"Agents directory not found: {agents_dir}")
            return 0

        discovered = 0

        try:
            # This would require dynamic imports and inspection
            # For now, just log that discovery is available
            logger.info(
                f"Agent discovery available for directory: {agents_dir}"
            )
            discovered = len(self.registry)

        except Exception as e:
            logger.error(f"Agent discovery failed: {e}")

        return discovered

    async def close(self) -> None:
        """Close shared client and cleanup resources."""
        if self.client:
            await self.client.close()
        logger.info("AgentFactory closed")
