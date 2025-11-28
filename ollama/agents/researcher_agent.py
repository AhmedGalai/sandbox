"""
Researcher agent specialized for information synthesis and research tasks.
Uses qwen2.5:7b model for comprehensive research capabilities.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from core.agent import BaseAgent
from core.exceptions import AgentExecutionError
from core.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """
    Specialized agent for research tasks.

    Handles information synthesis, source evaluation, and comprehensive
    research output generation using the Qwen2.5 7B model.
    """

    REQUIRED_CONTEXT_FIELDS = [
        "Topic",
        "Key Questions",
        "Known Information",
        "Sources to Prioritize",
        "Desired Output Format",
    ]

    def __init__(
        self,
        name: str = "researcher",
        model: str = "qwen2.5:7b",
        prompts_dir: Optional[Path] = None,
        client: Optional[OllamaClient] = None,
    ):
        """
        Initialize the Researcher agent.

        Args:
            name: Agent name for identification
            model: Ollama model to use (default: qwen2.5:7b)
            prompts_dir: Directory containing prompt templates
            client: OllamaClient instance
        """
        super().__init__(name, model, prompts_dir, client)
        logger.info(f"Initialized ResearcherAgent with model '{model}'")

    async def _execute_internal(self, context: Dict[str, Any]) -> str:
        """
        Execute research task with given context.

        Expected context keys:
        - Topic: Research topic
        - Key Questions: Questions to answer
        - Known Information: Background information
        - Sources to Prioritize: Preferred information sources
        - Desired Output Format: Expected output format
        - task: The research task/instruction

        Args:
            context: Research context and parameters

        Returns:
            Research findings and synthesis

        Raises:
            AgentExecutionError: If research execution fails
        """
        try:
            # Load the researcher prompt template
            template = self._load_builtin_prompt("agent_builtin_researcher.md")

            # Validate context has required fields
            self._validate_context_fields(context)

            # Format the context with placeholders
            prompt = self.format_context(template, context)

            logger.debug(
                f"Executing research task with context: "
                f"{list(context.keys())}"
            )

            # Generate research response
            response = await self.client.generate(
                model=self.model,
                prompt=prompt,
                temperature=context.get("temperature", 0.6),
                top_k=context.get("top_k", 40),
                top_p=context.get("top_p", 0.9),
            )

            logger.info("Research task completed successfully")
            return response

        except FileNotFoundError as e:
            logger.error(f"Prompt file not found: {e}")
            raise AgentExecutionError(f"Prompt template not found: {e}") from e
        except ValueError as e:
            logger.error(f"Context validation failed: {e}")
            raise AgentExecutionError(f"Invalid context: {e}") from e
        except Exception as e:
            logger.error(f"Research execution failed: {e}", exc_info=True)
            raise AgentExecutionError(f"Research failed: {e}") from e

    async def handle_streaming(
        self, context: Dict[str, Any]
    ):
        """
        Handle streaming research response.

        Args:
            context: Research context

        Yields:
            Text chunks from the model
        """
        try:
            template = self._load_builtin_prompt("agent_builtin_researcher.md")
            self._validate_context_fields(context)
            prompt = self.format_context(template, context)

            async for chunk in self.client.generate_stream(
                model=self.model,
                prompt=prompt,
                temperature=context.get("temperature", 0.6),
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Streaming research failed: {e}")
            raise AgentExecutionError(f"Streaming failed: {e}") from e

    def _load_builtin_prompt(self, filename: str) -> str:
        """
        Load a built-in prompt from the agents directory.

        Args:
            filename: Name of the prompt file

        Returns:
            Prompt content

        Raises:
            FileNotFoundError: If prompt file not found
        """
        # Try to load from agents directory first
        agents_dir = Path(__file__).parent
        prompt_path = agents_dir / filename

        if prompt_path.exists():
            try:
                content = prompt_path.read_text(encoding="utf-8")
                logger.debug(f"Loaded built-in prompt from {prompt_path}")
                return content
            except Exception as e:
                logger.error(f"Failed to read prompt file {prompt_path}: {e}")
                raise FileNotFoundError(f"Failed to read prompt: {prompt_path}") from e

        # Fallback to using the standard load_prompt method
        try:
            return self.load_prompt("builtin_researcher")
        except Exception as e:
            raise FileNotFoundError(
                f"Prompt file not found: {filename}"
            ) from e

    def _validate_context_fields(self, context: Dict[str, Any]) -> None:
        """
        Validate that context contains required fields.

        Args:
            context: Context dictionary to validate

        Raises:
            ValueError: If required fields are missing
        """
        # Map context keys to required template placeholders
        required_keys = {
            "Topic",
            "Key Questions",
            "Known Information",
            "Sources to Prioritize",
            "Desired Output Format",
        }

        # Check for at least the primary task
        if "task" not in context:
            logger.warning("Context missing 'task' field")

        # Optional validation - log which fields are missing
        missing = required_keys - set(context.keys())
        if missing:
            logger.debug(f"Optional context fields missing: {missing}")
