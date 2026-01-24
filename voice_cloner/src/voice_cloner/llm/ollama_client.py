"""Ollama LLM client for text generation."""

import json
import logging
from typing import Generator, Optional, Union

import requests

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 300):
        """
        Initialize the Ollama client.

        Args:
            base_url: Base URL of the Ollama API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def is_running(self) -> bool:
        """
        Check if Ollama is running and accessible.

        Returns:
            True if Ollama is accessible, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not accessible: {e}")
            return False

    def list_models(self) -> list[str]:
        """
        List available models in Ollama.

        Returns:
            List of model names
        """
        try:
            if not self.is_running():
                raise RuntimeError("Ollama is not running")

            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()

            data = response.json()
            models = [model["name"] for model in data.get("models", [])]

            logger.info(f"Found {len(models)} models")
            return models

        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            raise RuntimeError(f"Could not list Ollama models: {e}") from e

    def generate(
        self,
        prompt: str,
        model: str = "qwen3",
        temperature: float = 0.7,
        top_p: float = 0.9,
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        """
        Generate text using Ollama.

        Args:
            prompt: The prompt for generation
            model: Model name to use
            temperature: Temperature for generation (0.0 to 1.0)
            top_p: Top-p sampling parameter
            stream: Whether to stream the response

        Returns:
            Generated text as string if stream=False, or generator of text chunks if stream=True
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if temperature < 0 or temperature > 1.0:
            raise ValueError("Temperature must be between 0 and 1.0")

        try:
            if not self.is_running():
                raise RuntimeError("Ollama is not running. Start it with: ollama serve")

            # Verify model exists
            available_models = self.list_models()
            if model not in available_models:
                available_str = ", ".join(available_models) if available_models else "none"
                raise ValueError(f"Model '{model}' not found. Available: {available_str}")

            payload = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "top_p": top_p,
                "stream": stream,
            }

            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=stream,
                timeout=self.timeout,
            )
            response.raise_for_status()

            if stream:
                return self._stream_response(response)
            else:
                data = response.json()
                return data.get("response", "").strip()

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise RuntimeError(f"Could not generate text: {e}") from e

    def _stream_response(self, response) -> Generator[str, None, None]:
        """
        Stream response from Ollama.

        Args:
            response: HTTP response object

        Yields:
            Text chunks from the response
        """
        try:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    if chunk:
                        yield chunk
        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            raise

    def chat(
        self,
        messages: list[dict],
        model: str = "qwen3",
        temperature: float = 0.7,
        stream: bool = False,
    ) -> Union[str, Generator[str, None, None]]:
        """
        Chat with Ollama using message history.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name to use
            temperature: Temperature for generation (0.0 to 1.0)
            stream: Whether to stream the response

        Returns:
            Generated response as string if stream=False, or generator if stream=True
        """
        if not messages or len(messages) == 0:
            raise ValueError("Messages list cannot be empty")

        try:
            if not self.is_running():
                raise RuntimeError("Ollama is not running. Start it with: ollama serve")

            # Verify model exists
            available_models = self.list_models()
            if model not in available_models:
                available_str = ", ".join(available_models) if available_models else "none"
                raise ValueError(f"Model '{model}' not found. Available: {available_str}")

            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream,
            }

            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=stream,
                timeout=self.timeout,
            )
            response.raise_for_status()

            if stream:
                return self._stream_chat_response(response)
            else:
                data = response.json()
                return data.get("message", {}).get("content", "").strip()

        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise RuntimeError(f"Could not chat: {e}") from e

    def _stream_chat_response(self, response) -> Generator[str, None, None]:
        """
        Stream chat response from Ollama.

        Args:
            response: HTTP response object

        Yields:
            Text chunks from the response
        """
        try:
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        yield chunk
        except Exception as e:
            logger.error(f"Error streaming chat response: {e}")
            raise

    def close(self) -> None:
        """Close the session."""
        try:
            self.session.close()
            logger.info("Ollama client session closed")
        except Exception as e:
            logger.warning(f"Error closing session: {e}")
