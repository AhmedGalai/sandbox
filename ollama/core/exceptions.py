"""
Custom exceptions for the Ollama multi-agent system.
"""


class OllamaException(Exception):
    """Base exception for all Ollama-related errors."""

    pass


class OllamaConnectionError(OllamaException):
    """Raised when connection to Ollama API fails."""

    pass


class AgentTimeoutError(OllamaException):
    """Raised when an agent execution times out."""

    pass


class InvalidModelError(OllamaException):
    """Raised when an invalid or unavailable model is requested."""

    pass


class VisionProcessingError(OllamaException):
    """Raised when vision model processing fails."""

    pass


class ConfigurationError(OllamaException):
    """Raised when configuration is invalid."""

    pass


class AgentExecutionError(OllamaException):
    """Raised when agent execution encounters an error."""

    pass
