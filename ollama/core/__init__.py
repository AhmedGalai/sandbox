"""
Core module for the Ollama multi-agent system.

Provides:
- OllamaClient: Async HTTP client for Ollama API
- BaseAgent: Abstract base class for agents
- SimpleAgent: Simple text generation agent
- StreamingAgent: Agent with streaming support
- AgentOrchestrator: Multi-agent orchestration and concurrency control
- ConversationManager: Conversation history tracking and persistence
"""

from .agent import BaseAgent, SimpleAgent, StreamingAgent, AgentState
from .conversation import ConversationManager
from .exceptions import (
    AgentExecutionError,
    AgentTimeoutError,
    ConfigurationError,
    InvalidModelError,
    OllamaConnectionError,
    OllamaException,
    VisionProcessingError,
)
from .ollama_client import OllamaClient
from .orchestrator import (
    AgentOrchestrator,
    ExecutionResult,
    Task,
    TaskPriority,
)

__all__ = [
    "OllamaClient",
    "BaseAgent",
    "SimpleAgent",
    "StreamingAgent",
    "AgentState",
    "AgentOrchestrator",
    "ExecutionResult",
    "Task",
    "TaskPriority",
    "ConversationManager",
    "OllamaException",
    "OllamaConnectionError",
    "AgentExecutionError",
    "AgentTimeoutError",
    "InvalidModelError",
    "VisionProcessingError",
    "ConfigurationError",
]
