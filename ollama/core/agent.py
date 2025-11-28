"""
Base agent class for multi-agent system with async execution support,
prompt loading, context formatting, and state tracking.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Optional

from core.exceptions import AgentExecutionError
from core.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class AgentState(str, Enum):
    """Agent execution state enumeration."""

    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    COMPLETED = "completed"


class BaseAgent(ABC):
    """
    Abstract base class for agents in the multi-agent system.

    Provides:
    - Async execution framework
    - Prompt loading from markdown files
    - Context placeholder replacement
    - State tracking
    - Streaming support
    - Error handling
    """

    def __init__(
        self,
        name: str,
        model: str,
        prompts_dir: Optional[Path] = None,
        client: Optional[OllamaClient] = None,
    ):
        """
        Initialize a base agent.

        Args:
            name: Agent name (used for identification and logging)
            model: Ollama model to use for this agent
            prompts_dir: Directory containing prompt templates (markdown files)
            client: OllamaClient instance (creates new one if not provided)
        """
        self.name = name
        self.model = model
        self.prompts_dir = prompts_dir or Path(__file__).parent.parent / "prompts"
        self.client = client or OllamaClient()
        self.state = AgentState.IDLE
        self.last_error: Optional[str] = None
        self._lock = asyncio.Lock()

        logger.info(
            f"Initialized agent '{self.name}' with model '{self.model}'"
        )

    async def execute(self, context: Dict[str, Any]) -> str:
        """
        Execute the agent with the given context.

        This is the main entry point for agent execution. Subclasses should
        override this method or the _execute_internal method.

        Args:
            context: Dictionary containing execution context and parameters

        Returns:
            Agent's response/output

        Raises:
            AgentExecutionError: If execution fails
        """
        async with self._lock:
            try:
                self.state = AgentState.BUSY
                self.last_error = None
                logger.info(f"Agent '{self.name}' starting execution")

                result = await self._execute_internal(context)

                self.state = AgentState.COMPLETED
                logger.info(f"Agent '{self.name}' completed successfully")
                return result

            except Exception as e:
                self.state = AgentState.ERROR
                self.last_error = str(e)
                logger.error(
                    f"Agent '{self.name}' execution failed: {e}", exc_info=True
                )
                raise AgentExecutionError(
                    f"Agent '{self.name}' failed: {e}"
                ) from e

            finally:
                if self.state == AgentState.BUSY:
                    self.state = AgentState.IDLE

    @abstractmethod
    async def _execute_internal(self, context: Dict[str, Any]) -> str:
        """
        Internal execution logic - must be implemented by subclasses.

        Args:
            context: Dictionary containing execution context

        Returns:
            Agent's response/output
        """
        pass

    async def handle_streaming(
        self, context: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        Handle streaming response from the model.

        Subclasses can override this to implement streaming behavior.

        Args:
            context: Dictionary containing execution context

        Yields:
            Text chunks as they are generated
        """
        prompt = self.format_context(self.load_prompt("default"), context)

        async for chunk in self.client.generate_stream(
            model=self.model, prompt=prompt
        ):
            yield chunk

    def load_prompt(self, prompt_name: str) -> str:
        """
        Load a prompt template from a markdown file.

        Looks for files in prompts_dir/{agent_name}/{prompt_name}.md

        Args:
            prompt_name: Name of the prompt (filename without .md extension)

        Returns:
            Prompt template content

        Raises:
            FileNotFoundError: If prompt file is not found
        """
        prompt_path = self.prompts_dir / self.name / f"{prompt_name}.md"

        if not prompt_path.exists():
            logger.warning(f"Prompt file not found: {prompt_path}")
            raise FileNotFoundError(f"Prompt not found: {prompt_path}")

        try:
            content = prompt_path.read_text(encoding="utf-8")
            logger.debug(f"Loaded prompt '{prompt_name}' from {prompt_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read prompt file {prompt_path}: {e}")
            raise

    def format_context(self, template: str, placeholders: Dict[str, Any]) -> str:
        """
        Replace context placeholders in a template.

        Replaces `___` markers and named placeholders like `___key___`.

        Args:
            template: Template string with placeholders
            placeholders: Dictionary of values to replace

        Returns:
            Formatted string with placeholders replaced

        Raises:
            ValueError: If required placeholder is missing
        """
        result = template

        # Handle named placeholders like ___key___
        for key, value in placeholders.items():
            if value is None:
                continue

            placeholder = f"___{key}___"
            str_value = str(value)

            if placeholder in result:
                result = result.replace(placeholder, str_value)
                logger.debug(f"Replaced placeholder {placeholder}")

        # Warn about unused placeholders
        if "___" in result:
            import re

            unused = re.findall(r"___(\w+)___", result)
            if unused:
                logger.warning(f"Unused placeholders in template: {unused}")

        return result

    def get_state(self) -> AgentState:
        """
        Get the current agent state.

        Returns:
            Current AgentState
        """
        return self.state

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive agent status.

        Returns:
            Dictionary with agent status information
        """
        return {
            "name": self.name,
            "model": self.model,
            "state": self.state.value,
            "last_error": self.last_error,
        }

    async def close(self) -> None:
        """Close the agent and cleanup resources."""
        if self.client:
            await self.client.close()
        logger.info(f"Agent '{self.name}' closed")


class SimpleAgent(BaseAgent):
    """
    Simple agent implementation for basic text generation.

    Loads prompts and generates responses using the configured model.
    """

    async def _execute_internal(self, context: Dict[str, Any]) -> str:
        """
        Generate text based on a prompt template and context.

        Expects context to contain:
        - prompt_name: Name of the prompt template (default: 'default')
        - Any additional placeholders to be substituted

        Args:
            context: Execution context with prompt and placeholders

        Returns:
            Generated response
        """
        prompt_name = context.get("prompt_name", "default")

        try:
            template = self.load_prompt(prompt_name)
            prompt = self.format_context(template, context)

            logger.debug(
                f"Agent '{self.name}' generating with prompt: {prompt[:100]}..."
            )

            response = await self.client.generate(
                model=self.model,
                prompt=prompt,
                temperature=context.get("temperature", 0.7),
            )

            return response

        except FileNotFoundError as e:
            logger.error(f"Prompt file not found: {e}")
            raise AgentExecutionError(f"Prompt not found: {e}") from e
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise


class StreamingAgent(BaseAgent):
    """
    Agent that supports streaming responses for real-time output.
    """

    async def _execute_internal(self, context: Dict[str, Any]) -> str:
        """
        Generate text with streaming and collect full response.

        Args:
            context: Execution context

        Returns:
            Complete generated response
        """
        prompt_name = context.get("prompt_name", "default")

        try:
            template = self.load_prompt(prompt_name)
            prompt = self.format_context(template, context)

            full_response = ""

            async for chunk in self.client.generate_stream(
                model=self.model,
                prompt=prompt,
                temperature=context.get("temperature", 0.7),
            ):
                full_response += chunk

            return full_response

        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            raise AgentExecutionError(f"Streaming generation failed: {e}") from e
