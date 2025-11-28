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

from core.agent import BaseAgent, SimpleAgent, StreamingAgent, AgentState
from core.conversation import ConversationManager
from core.exceptions import (
    AgentExecutionError,
    AgentTimeoutError,
    ConfigurationError,
    InvalidModelError,
    OllamaConnectionError,
    OllamaException,
    VisionProcessingError,
)
from core.ollama_client import OllamaClient
from core.orchestrator import (
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
