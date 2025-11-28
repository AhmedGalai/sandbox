"""
Async HTTP client for Ollama API with connection pooling,
timeout handling, and exponential backoff retry logic.
"""

import asyncio
import logging
from typing import AsyncGenerator, Optional

import httpx

from ..config.settings import get_settings
from .exceptions import (
    InvalidModelError,
    OllamaConnectionError,
    VisionProcessingError,
)

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Async client for interacting with Ollama API.

    Features:
    - HTTP/2 connection pooling via httpx
    - Configurable timeout handling
    - Exponential backoff retry logic
    - Streaming response support
    - Vision model support
    """

    def __init__(
        self,
        host: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        initial_backoff: float = 1.0,
    ):
        """
        Initialize the Ollama client.

        Args:
            host: Ollama API endpoint (default: from settings)
            timeout: Request timeout in seconds (default: from settings)
            max_retries: Maximum number of retry attempts
            initial_backoff: Initial backoff delay in seconds for exponential backoff
        """
        settings = get_settings()
        self.host = host or settings.ollama_host
        self.timeout = timeout or settings.timeout
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff

        # Create async client with connection pooling
        self._client: Optional[httpx.AsyncClient] = None
        logger.info(f"Initialized OllamaClient for {self.host}")

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Get or create the async HTTP client.

        Returns:
            httpx.AsyncClient instance with connection pooling
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.host,
                timeout=self.timeout,
                http2=True,
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            )
            logger.debug("Created new HTTP client with connection pooling")
        return self._client

    async def close(self) -> None:
        """Close the async HTTP client and cleanup resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.debug("Closed HTTP client")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        await self.close()

    async def _retry_with_backoff(
        self,
        coro,
        operation_name: str,
    ):
        """
        Execute a coroutine with exponential backoff retry logic.

        Args:
            coro: Coroutine to execute
            operation_name: Name of the operation for logging

        Returns:
            Result from the coroutine

        Raises:
            OllamaConnectionError: If all retries are exhausted
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await coro()
            except httpx.ConnectError as e:
                last_exception = e
                if attempt < self.max_retries:
                    backoff = self.initial_backoff * (2 ** attempt)
                    logger.warning(
                        f"{operation_name} attempt {attempt + 1} failed, "
                        f"retrying in {backoff}s: {e}"
                    )
                    await asyncio.sleep(backoff)
                else:
                    logger.error(
                        f"{operation_name} failed after {self.max_retries + 1} attempts"
                    )
            except httpx.HTTPError as e:
                raise OllamaConnectionError(f"{operation_name} failed: {e}")

        raise OllamaConnectionError(
            f"{operation_name} failed after {self.max_retries + 1} attempts: "
            f"{last_exception}"
        )

    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        top_k: int = 40,
        top_p: float = 0.9,
    ) -> str:
        """
        Generate text completion for a prompt.

        Args:
            model: Model name (must be available in Ollama)
            prompt: Input prompt
            system: System message for model behavior
            temperature: Sampling temperature (0.0-1.0)
            top_k: Top-k sampling parameter
            top_p: Top-p (nucleus) sampling parameter

        Returns:
            Generated text response

        Raises:
            OllamaConnectionError: If connection fails
            InvalidModelError: If model is not available
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
        }

        if system:
            payload["system"] = system

        async def _generate():
            client = await self._get_client()
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            return response.json()

        try:
            result = await self._retry_with_backoff(_generate, f"generate({model})")
            logger.debug(f"Generated text using model {model}")
            return result.get("response", "")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise InvalidModelError(
                    f"Model '{model}' not found. Ensure it's pulled in Ollama."
                )
            raise OllamaConnectionError(f"HTTP error {e.response.status_code}: {e}")

    async def generate_stream(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        top_k: int = 40,
        top_p: float = 0.9,
    ) -> AsyncGenerator[str, None]:
        """
        Generate text completion with streaming response.

        Yields chunks of text as they are generated, allowing for
        real-time processing of model outputs.

        Args:
            model: Model name (must be available in Ollama)
            prompt: Input prompt
            system: System message for model behavior
            temperature: Sampling temperature (0.0-1.0)
            top_k: Top-k sampling parameter
            top_p: Top-p (nucleus) sampling parameter

        Yields:
            Text chunks as they are generated

        Raises:
            OllamaConnectionError: If connection fails
            InvalidModelError: If model is not available
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
        }

        if system:
            payload["system"] = system

        async def _stream():
            client = await self._get_client()
            return await client.post("/api/generate", json=payload)

        try:
            response = await self._retry_with_backoff(
                _stream, f"generate_stream({model})"
            )
            response.raise_for_status()

            async for line in response.aiter_lines():
                if line:
                    chunk = response.json() if isinstance(response, dict) else line
                    if isinstance(chunk, str):
                        # Parse JSON from line
                        import json

                        try:
                            chunk = json.loads(chunk)
                        except ValueError:
                            continue

                    if isinstance(chunk, dict) and "response" in chunk:
                        yield chunk["response"]

            logger.debug(f"Streamed generation completed for model {model}")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise InvalidModelError(
                    f"Model '{model}' not found. Ensure it's pulled in Ollama."
                )
            raise OllamaConnectionError(f"HTTP error {e.response.status_code}: {e}")

    async def vision_generate(
        self,
        model: str,
        image_path: str,
        prompt: str,
        system: Optional[str] = None,
    ) -> str:
        """
        Process an image using a vision model.

        Args:
            model: Vision model name (e.g., llava)
            image_path: Path to the image file
            prompt: Question or instruction about the image
            system: System message for model behavior

        Returns:
            Vision model's analysis of the image

        Raises:
            VisionProcessingError: If image processing fails
            InvalidModelError: If model is not available
        """
        import base64
        from pathlib import Path

        image_path_obj = Path(image_path)

        if not image_path_obj.exists():
            raise VisionProcessingError(f"Image file not found: {image_path}")

        try:
            with open(image_path_obj, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            raise VisionProcessingError(f"Failed to read image file: {e}")

        payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
        }

        if system:
            payload["system"] = system

        async def _vision():
            client = await self._get_client()
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            return response.json()

        try:
            result = await self._retry_with_backoff(
                _vision, f"vision_generate({model})"
            )
            logger.debug(f"Vision generation completed using model {model}")
            return result.get("response", "")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise InvalidModelError(
                    f"Vision model '{model}' not found. Ensure it's pulled in Ollama."
                )
            raise VisionProcessingError(f"Vision processing failed: {e}")

    async def get_model_info(self, model: str) -> dict:
        """
        Get information about a specific model.

        Args:
            model: Model name

        Returns:
            Model information dictionary

        Raises:
            InvalidModelError: If model is not found
        """

        async def _get_info():
            client = await self._get_client()
            response = await client.get(f"/api/show?name={model}")
            response.raise_for_status()
            return response.json()

        try:
            return await self._retry_with_backoff(
                _get_info, f"get_model_info({model})"
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise InvalidModelError(f"Model '{model}' not found")
            raise OllamaConnectionError(f"Failed to get model info: {e}")

    async def list_models(self) -> list:
        """
        List all available models in Ollama.

        Returns:
            List of available model information

        Raises:
            OllamaConnectionError: If request fails
        """

        async def _list():
            client = await self._get_client()
            response = await client.get("/api/tags")
            response.raise_for_status()
            return response.json()

        try:
            result = await self._retry_with_backoff(_list, "list_models")
            models = result.get("models", [])
            logger.debug(f"Retrieved list of {len(models)} available models")
            return models
        except OllamaConnectionError:
            logger.error("Failed to list models from Ollama")
            raise
