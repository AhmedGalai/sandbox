"""
Tests for BaseAgent and agent implementations.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from core.agent import BaseAgent, SimpleAgent, StreamingAgent, AgentState
from core.exceptions import AgentExecutionError
from core.ollama_client import OllamaClient


@pytest.fixture
def mock_client():
    """Create mock OllamaClient."""
    return AsyncMock(spec=OllamaClient)


@pytest.fixture
def simple_agent(mock_client):
    """Create SimpleAgent for testing."""
    return SimpleAgent(
        name="test_agent",
        model="llama3.2:3b",
        client=mock_client,
    )


@pytest.mark.asyncio
async def test_agent_initialization(mock_client):
    """Test BaseAgent subclass initialization."""
    agent = SimpleAgent(
        name="test_agent",
        model="llama3.2:3b",
        client=mock_client,
    )

    assert agent.name == "test_agent"
    assert agent.model == "llama3.2:3b"
    assert agent.state == AgentState.IDLE
    assert agent.last_error is None


@pytest.mark.asyncio
async def test_agent_state_tracking(simple_agent):
    """Test agent state transitions during execution."""
    simple_agent.client.generate = AsyncMock(return_value="Test response")

    # Create minimal context and mock prompt loading
    with patch.object(simple_agent, "load_prompt", return_value="Test prompt"):
        initial_state = simple_agent.get_state()
        assert initial_state == AgentState.IDLE

        response = await simple_agent.execute({"prompt_name": "test"})

        assert response == "Test response"
        assert simple_agent.last_error is None


@pytest.mark.asyncio
async def test_agent_error_handling(simple_agent):
    """Test agent error handling and state management."""
    simple_agent.client.generate = AsyncMock(
        side_effect=Exception("Test error")
    )

    with patch.object(simple_agent, "load_prompt", return_value="Test prompt"):
        with pytest.raises(AgentExecutionError):
            await simple_agent.execute({"prompt_name": "test"})

        assert simple_agent.state == AgentState.IDLE
        assert simple_agent.last_error is not None


@pytest.mark.asyncio
async def test_format_context(simple_agent):
    """Test context placeholder replacement."""
    template = "Question: ___question___\nLanguage: ___language___"
    context = {
        "question": "What is AI?",
        "language": "Python",
        "unused": "value"
    }

    result = simple_agent.format_context(template, context)

    assert "What is AI?" in result
    assert "Python" in result
    assert "___question___" not in result
    assert "___language___" not in result


@pytest.mark.asyncio
async def test_format_context_missing_placeholder(simple_agent):
    """Test format_context with missing values."""
    template = "Value: ___missing___"
    context = {"other": "value"}

    result = simple_agent.format_context(template, context)
    assert "___missing___" in result


@pytest.mark.asyncio
async def test_get_status(simple_agent):
    """Test agent status reporting."""
    status = simple_agent.get_status()

    assert status["name"] == "test_agent"
    assert status["model"] == "llama3.2:3b"
    assert status["state"] == "idle"
    assert status["last_error"] is None


@pytest.mark.asyncio
async def test_streaming_agent(mock_client):
    """Test StreamingAgent execution."""
    agent = StreamingAgent(
        name="streaming_agent",
        model="llama3.2:3b",
        client=mock_client,
    )

    async def mock_stream():
        for chunk in ["Hello ", "world", "!"]:
            yield chunk

    agent.client.generate_stream = AsyncMock(return_value=mock_stream())

    with patch.object(agent, "load_prompt", return_value="Test prompt"):
        result = await agent.execute({"prompt_name": "test"})
        assert result == "Hello world!"


@pytest.mark.asyncio
async def test_load_prompt_missing_file(simple_agent):
    """Test load_prompt with missing file."""
    with pytest.raises(FileNotFoundError):
        simple_agent.load_prompt("nonexistent")


@pytest.mark.asyncio
async def test_concurrent_execution(mock_client):
    """Test agent handles concurrent execution requests."""
    agent = SimpleAgent(
        name="test_agent",
        model="llama3.2:3b",
        client=mock_client,
    )

    agent.client.generate = AsyncMock(return_value="Response")

    with patch.object(agent, "load_prompt", return_value="Prompt"):
        # First execution should work
        result1 = await agent.execute({"prompt_name": "test"})
        assert result1 == "Response"

        # Second execution should also work
        result2 = await agent.execute({"prompt_name": "test"})
        assert result2 == "Response"
