"""
Vision command for image analysis using the VisionAgent.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from rich.panel import Panel

from .base import BaseCommand

logger = logging.getLogger(__name__)

# Supported image formats
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


class VisionCommand(BaseCommand):
    """Analyze images using the vision agent with optional custom questions."""

    async def execute(
        self, args: List[str], context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Execute the vision command.

        Args:
            args: Command arguments [image_path] [question]
            context: Shared context with agent factory and orchestrator

        Returns:
            Tuple of (success, output_message)
        """
        if not args:
            return False, "Please provide an image path"

        factory = context.get("agent_factory")
        orchestrator = context.get("orchestrator")
        if not factory or not orchestrator:
            return False, "Agent factory or orchestrator not available"

        try:
            # Parse arguments
            positional, named = self.parse_arguments(
                args, named_params=["question", "model"]
            )

            if not positional:
                return False, "Image path is required"

            image_path = positional[0]

            # Validate image path
            path_obj = Path(image_path)
            if not path_obj.exists():
                return False, f"Image file not found: {image_path}"

            if path_obj.suffix.lower() not in SUPPORTED_FORMATS:
                return False, (
                    f"Unsupported image format: {path_obj.suffix}. "
                    f"Supported: {', '.join(SUPPORTED_FORMATS)}"
                )

            # Get question if provided
            if len(positional) > 1:
                question = " ".join(positional[1:])
            else:
                question = named.get(
                    "question",
                    "Describe what you see in this image in detail.",
                )

            # Create agent
            agent_config = {"name": "vision"}
            model = named.get("model")
            if model:
                agent_config["model"] = model

            agent = factory.create_agent("vision", agent_config)

            # Prepare context
            file_size = path_obj.stat().st_size
            execution_context = {
                "Image Path": image_path,
                "Analysis Focus": "comprehensive visual analysis",
                "Specific Questions": question,
                "Expected Output": "detailed image analysis",
                "Detail Level": "high",
                "task": question,
                "file_size": file_size,
            }

            # Show status
            self.console.print(f"\n[cyan]Analyzing image: {image_path}[/cyan]")
            self.console.print(f"[cyan]Question: {question}[/cyan]\n")

            # Execute with orchestrator
            from ..core.orchestrator import TaskPriority

            task_id = await orchestrator.dispatch_task(
                agent, execution_context, priority=TaskPriority.HIGH
            )

            return True, f"Vision analysis task {task_id} dispatched"

        except FileNotFoundError as e:
            logger.error(f"Image file error: {e}")
            return False, f"Image file error: {e}"
        except Exception as e:
            logger.error(f"Error invoking vision agent: {e}")
            return False, f"Failed to invoke vision agent: {e}"

    def get_help_text(self) -> str:
        """Return help text for the vision command."""
        return """[bold cyan]/vision[/bold cyan] <image_path> [question] [options]

Analyze images using the vision agent with optional custom questions.

Usage:
  /vision /path/to/image.jpg
  /vision /path/to/image.png "What's in this image?"
  /vision image.jpg "Identify objects" --model llava:7b

Arguments:
  image_path         - Path to the image file (required)
  question           - Question or instruction about the image (optional)

Options:
  --question TEXT    - Question to ask about the image
  --model MODEL      - Specify a different vision model to use

Supported Formats:
  .png, .jpg, .jpeg, .gif, .webp

The vision agent uses a multimodal model (Llava) to analyze images
and answer questions about their content.
"""
