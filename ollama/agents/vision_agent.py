"""
Vision agent specialized for image analysis using multimodal vision models.
Uses llava:7b vision model for comprehensive image understanding.
"""

import asyncio
import base64
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from ..core.agent import BaseAgent
from ..core.exceptions import AgentExecutionError, VisionProcessingError
from ..core.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

# Supported image formats
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB


class VisionAgent(BaseAgent):
    """
    Specialized agent for image analysis and visual understanding.

    Handles image loading, preprocessing, and analysis using the Llava 7B
    vision model for comprehensive visual understanding tasks.
    """

    REQUIRED_CONTEXT_FIELDS = [
        "Image Path",
        "Analysis Focus",
        "Specific Questions",
        "Expected Output",
        "Detail Level",
    ]

    def __init__(
        self,
        name: str = "vision",
        model: str = "llava:7b",
        prompts_dir: Optional[Path] = None,
        client: Optional[OllamaClient] = None,
    ):
        """
        Initialize the Vision agent.

        Args:
            name: Agent name for identification
            model: Ollama vision model to use (default: llava:7b)
            prompts_dir: Directory containing prompt templates
            client: OllamaClient instance
        """
        super().__init__(name, model, prompts_dir, client)
        logger.info(f"Initialized VisionAgent with model '{model}'")

    async def _execute_internal(self, context: Dict[str, Any]) -> str:
        """
        Execute image analysis task with given context.

        Expected context keys:
        - Image Path: Path to the image file
        - Analysis Focus: What to focus on in the analysis
        - Specific Questions: Questions about the image
        - Expected Output: Expected format/content
        - Detail Level: Level of detail required (low/medium/high)
        - task: The analysis task/instruction

        Args:
            context: Analysis context and parameters

        Returns:
            Image analysis results

        Raises:
            AgentExecutionError: If analysis execution fails
            VisionProcessingError: If image processing fails
        """
        try:
            # Validate context has required fields
            self._validate_context_fields(context)

            # Get and validate image path
            image_path = context.get("Image Path")
            if not image_path:
                raise VisionProcessingError("Image Path is required in context")

            # Preprocess and validate image
            await self.preprocess_image(image_path)

            # Load the vision prompt template
            template = self._load_builtin_prompt("agent_builtin_vision.md")

            # Format the context with placeholders
            prompt = self.format_context(template, context)

            logger.debug(
                f"Executing vision analysis task with image: {image_path}"
            )

            # Generate vision response using OllamaClient's vision_generate
            response = await self.client.vision_generate(
                model=self.model,
                image_path=image_path,
                prompt=prompt,
            )

            logger.info("Vision analysis task completed successfully")
            return response

        except VisionProcessingError as e:
            logger.error(f"Image processing failed: {e}")
            raise
        except FileNotFoundError as e:
            logger.error(f"Prompt file not found: {e}")
            raise AgentExecutionError(f"Prompt template not found: {e}") from e
        except ValueError as e:
            logger.error(f"Context validation failed: {e}")
            raise AgentExecutionError(f"Invalid context: {e}") from e
        except Exception as e:
            logger.error(f"Vision analysis execution failed: {e}", exc_info=True)
            raise AgentExecutionError(f"Vision analysis failed: {e}") from e

    async def analyze_image(
        self, image_path: str, question: str
    ) -> str:
        """
        Analyze an image with a specific question.

        Convenience method for simple image analysis without full context.

        Args:
            image_path: Path to the image file
            question: Question or instruction about the image

        Returns:
            Analysis results

        Raises:
            VisionProcessingError: If image processing fails
            AgentExecutionError: If analysis fails
        """
        try:
            # Preprocess image
            await self.preprocess_image(image_path)

            logger.debug(f"Analyzing image: {image_path}")

            # Generate vision response
            response = await self.client.vision_generate(
                model=self.model,
                image_path=image_path,
                prompt=question,
            )

            logger.info("Image analysis completed")
            return response

        except VisionProcessingError as e:
            logger.error(f"Image processing failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Image analysis failed: {e}", exc_info=True)
            raise AgentExecutionError(f"Image analysis failed: {e}") from e

    async def preprocess_image(self, image_path: str) -> None:
        """
        Preprocess and validate an image file.

        Checks:
        - File exists
        - File format is supported
        - File size is reasonable (resizes if > 2MB)

        Args:
            image_path: Path to the image file

        Raises:
            VisionProcessingError: If image validation or processing fails
        """
        image_path_obj = Path(image_path)

        # Check if file exists
        if not image_path_obj.exists():
            raise VisionProcessingError(f"Image file not found: {image_path}")

        # Check file format
        if image_path_obj.suffix.lower() not in SUPPORTED_FORMATS:
            raise VisionProcessingError(
                f"Unsupported image format: {image_path_obj.suffix}. "
                f"Supported formats: {', '.join(SUPPORTED_FORMATS)}"
            )

        # Check file size
        file_size = image_path_obj.stat().st_size
        if file_size == 0:
            raise VisionProcessingError(f"Image file is empty: {image_path}")

        if file_size > MAX_IMAGE_SIZE:
            logger.warning(
                f"Image file size ({file_size} bytes) exceeds recommended "
                f"size ({MAX_IMAGE_SIZE} bytes). Attempting to resize..."
            )
            await self._resize_image(image_path)

        logger.debug(
            f"Image validation passed: {image_path} "
            f"(size: {file_size} bytes)"
        )

    async def _resize_image(self, image_path: str) -> None:
        """
        Resize an image that exceeds the size limit.

        Uses PIL/Pillow if available, otherwise logs a warning.

        Args:
            image_path: Path to the image file

        Raises:
            VisionProcessingError: If resizing fails
        """
        try:
            from PIL import Image

            logger.info(f"Resizing image: {image_path}")

            image_path_obj = Path(image_path)
            image = Image.open(image_path_obj)

            # Calculate new dimensions (resize to 50% if over limit)
            new_width = int(image.width * 0.7)
            new_height = int(image.height * 0.7)

            resized_image = image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )

            # Save the resized image back
            resized_image.save(image_path_obj, quality=85, optimize=True)

            new_size = image_path_obj.stat().st_size
            logger.info(
                f"Image resized successfully. New size: {new_size} bytes"
            )

        except ImportError:
            logger.warning(
                "PIL/Pillow not available for image resizing. "
                "Please install pillow: pip install pillow"
            )
            logger.warning(
                "Image will be processed as-is, but may cause issues "
                "if it exceeds model limits."
            )
        except Exception as e:
            raise VisionProcessingError(f"Failed to resize image: {e}") from e

    async def handle_streaming(
        self, context: Dict[str, Any]
    ):
        """
        Handle streaming vision analysis response.

        Note: Streaming may not be available for vision models in all
        Ollama configurations.

        Args:
            context: Analysis context

        Yields:
            Text chunks from the model
        """
        try:
            # Validate and preprocess image
            image_path = context.get("Image Path")
            if not image_path:
                raise VisionProcessingError("Image Path is required")

            await self.preprocess_image(image_path)

            template = self._load_builtin_prompt("agent_builtin_vision.md")
            self._validate_context_fields(context)
            prompt = self.format_context(template, context)

            logger.debug("Attempting streaming vision analysis")

            # Try streaming if supported
            async for chunk in self.client.generate_stream(
                model=self.model,
                prompt=prompt,
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Streaming vision analysis failed: {e}")
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
            return self.load_prompt("builtin_vision")
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
            "Image Path",
            "Analysis Focus",
            "Specific Questions",
            "Expected Output",
            "Detail Level",
        }

        # Check for at least the primary task or image path
        if "task" not in context and "Image Path" not in context:
            logger.warning("Context missing both 'task' and 'Image Path' fields")

        # Optional validation - log which fields are missing
        missing = required_keys - set(context.keys())
        if missing:
            logger.debug(f"Optional context fields missing: {missing}")
