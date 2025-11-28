"""
Tests for AgentOrchestrator.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from core.orchestrator import (
    AgentOrchestrator,
    Task,
    TaskPriority,
    ExecutionResult,
)
from core.agent import SimpleAgent
from core.exceptions import AgentExecutionError


@pytest.fixture
def orchestrator():
    """Create orchestrator for testing."""
    return AgentOrchestrator(max_concurrent=2)


@pytest.fixture
def mock_agent():
    """Create mock agent."""
    agent = MagicMock(spec=SimpleAgent)
    agent.name = "test_agent"
    agent.execute = AsyncMock(return_value="Test response")
    return agent


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test orchestrator initialization."""
    orch = AgentOrchestrator(max_concurrent=5)
    assert orch.max_concurrent == 5
    assert orch.semaphore._value == 5
    assert len(orch.results) == 0


@pytest.mark.asyncio
async def test_dispatch_task(orchestrator, mock_agent):
    """Test task dispatch."""
    context = {"key": "value"}

    task_id = await orchestrator.dispatch_task(mock_agent, context)

    assert task_id is not None
    assert task_id.startswith("test_agent_")
    assert not orchestrator.task_queue.empty()


@pytest.mark.asyncio
async def test_dispatch_task_invalid_agent(orchestrator):
    """Test dispatch with invalid agent."""
    with pytest.raises(ValueError):
        await orchestrator.dispatch_task(None, {})


@pytest.mark.asyncio
async def test_task_priority_ordering():
    """Test task priority queue ordering."""
    task_low = Task("agent1", MagicMock(), {}, priority=TaskPriority.LOW)
    task_high = Task("agent2", MagicMock(), {}, priority=TaskPriority.HIGH)
    task_normal = Task("agent3", MagicMock(), {}, priority=TaskPriority.NORMAL)

    # High priority should be less than others
    assert task_high < task_normal
    assert task_normal < task_low


@pytest.mark.asyncio
async def test_execute_single_task(orchestrator, mock_agent):
    """Test single task execution."""
    task = Task("test_agent", mock_agent, {"key": "value"})

    result = await orchestrator._execute_single_task(task)

    assert result.success is True
    assert result.agent_name == "test_agent"
    assert result.result == "Test response"
    assert result.error is None
    assert result.execution_time is not None


@pytest.mark.asyncio
async def test_execute_single_task_failure(orchestrator):
    """Test task execution with failure."""
    mock_agent = MagicMock(spec=SimpleAgent)
    mock_agent.name = "failing_agent"
    mock_agent.execute = AsyncMock(
        side_effect=AgentExecutionError("Test error")
    )

    task = Task("failing_agent", mock_agent, {})

    result = await orchestrator._execute_single_task(task)

    assert result.success is False
    assert result.error is not None
    assert "Test error" in result.error


@pytest.mark.asyncio
async def test_get_result(orchestrator, mock_agent):
    """Test getting execution result."""
    context = {"key": "value"}
    task_id = await orchestrator.dispatch_task(mock_agent, context)

    # Create and store a result
    result = ExecutionResult(
        task_id=task_id,
        agent_name="test_agent",
        success=True,
        result="Test response",
    )
    orchestrator.results[task_id] = result

    retrieved = orchestrator.get_result(task_id)
    assert retrieved is result


@pytest.mark.asyncio
async def test_get_all_results(orchestrator, mock_agent):
    """Test getting all results."""
    context1 = {"test": "1"}
    context2 = {"test": "2"}

    task_id1 = await orchestrator.dispatch_task(mock_agent, context1)
    task_id2 = await orchestrator.dispatch_task(mock_agent, context2)

    result1 = ExecutionResult(task_id1, "agent1", True, "response1")
    result2 = ExecutionResult(task_id2, "agent2", True, "response2")

    orchestrator.results[task_id1] = result1
    orchestrator.results[task_id2] = result2

    all_results = orchestrator.get_all_results()
    assert len(all_results) == 2


@pytest.mark.asyncio
async def test_get_summary(orchestrator, mock_agent):
    """Test execution summary."""
    # Add some results
    result1 = ExecutionResult(
        task_id="task1",
        agent_name="agent1",
        success=True,
        result="response1",
        execution_time=1.5,
    )
    result2 = ExecutionResult(
        task_id="task2",
        agent_name="agent2",
        success=False,
        error="Test error",
        execution_time=0.5,
    )

    orchestrator.results["task1"] = result1
    orchestrator.results["task2"] = result2

    summary = orchestrator.get_summary()

    assert summary["total_tasks"] == 2
    assert summary["successful"] == 1
    assert summary["failed"] == 1
    assert summary["success_rate"] == 0.5
    assert summary["avg_execution_time"] == 1.0


@pytest.mark.asyncio
async def test_handle_agent_failure(orchestrator):
    """Test failure handling."""
    result = ExecutionResult(
        task_id="task1",
        agent_name="agent1",
        success=False,
        error="Test error",
    )
    orchestrator.results["task1"] = result

    # Test without callback
    handled = orchestrator.handle_agent_failure("task1")
    assert handled is result

    # Test with callback
    callback_called = False
    callback_args = None

    def error_callback(task_id, error):
        nonlocal callback_called, callback_args
        callback_called = True
        callback_args = (task_id, error)

    handled = orchestrator.handle_agent_failure("task1", error_callback)
    assert callback_called is True
    assert callback_args == ("task1", "Test error")


@pytest.mark.asyncio
async def test_handle_agent_failure_success_task(orchestrator):
    """Test failure handling on successful task."""
    result = ExecutionResult(
        task_id="task1",
        agent_name="agent1",
        success=True,
        result="response",
    )
    orchestrator.results["task1"] = result

    handled = orchestrator.handle_agent_failure("task1")
    assert handled.success is True


@pytest.mark.asyncio
async def test_reset(orchestrator, mock_agent):
    """Test orchestrator reset."""
    await orchestrator.dispatch_task(mock_agent, {})

    result = ExecutionResult("task1", "agent1", True, "response")
    orchestrator.results["task1"] = result

    orchestrator.reset()

    assert len(orchestrator.results) == 0
    assert orchestrator._task_counter == 0


@pytest.mark.asyncio
async def test_run_sequential(orchestrator):
    """Test sequential execution."""
    mock_agent1 = MagicMock(spec=SimpleAgent)
    mock_agent1.name = "agent1"
    mock_agent1.execute = AsyncMock(return_value="response1")

    mock_agent2 = MagicMock(spec=SimpleAgent)
    mock_agent2.name = "agent2"
    mock_agent2.execute = AsyncMock(return_value="response2")

    agent_tasks = [
        (mock_agent1, {"test": "1"}),
        (mock_agent2, {"test": "2"}),
    ]

    results = await orchestrator.run_sequential(agent_tasks)

    assert len(results) == 2
    assert results[0].success is True
    assert results[1].success is True


@pytest.mark.asyncio
async def test_run_sequential_stop_on_failure(orchestrator):
    """Test sequential execution with stop_on_failure."""
    mock_agent1 = MagicMock(spec=SimpleAgent)
    mock_agent1.name = "agent1"
    mock_agent1.execute = AsyncMock(
        side_effect=AgentExecutionError("Error")
    )

    mock_agent2 = MagicMock(spec=SimpleAgent)
    mock_agent2.name = "agent2"
    mock_agent2.execute = AsyncMock(return_value="response2")

    agent_tasks = [
        (mock_agent1, {}),
        (mock_agent2, {}),
    ]

    results = await orchestrator.run_sequential(agent_tasks, stop_on_failure=True)

    # Should only have first result (failure)
    assert len(results) == 1
    assert results[0].success is False
