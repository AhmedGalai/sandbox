"""
Multi-agent orchestrator with task queue, concurrency control,
and result aggregation.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .agent import BaseAgent
from .exceptions import AgentExecutionError

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""

    LOW = 3
    NORMAL = 2
    HIGH = 1


@dataclass
class Task:
    """Represents a task to be executed by an agent."""

    agent_name: str
    agent: BaseAgent
    context: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    task_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    result: Optional[str] = None
    error: Optional[str] = None
    completed_at: Optional[datetime] = None

    def __lt__(self, other: "Task") -> bool:
        """Enable priority queue ordering by priority then creation time."""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at

    def get_execution_time(self) -> Optional[float]:
        """Get execution time in seconds if task is completed."""
        if self.completed_at is None:
            return None
        return (self.completed_at - self.created_at).total_seconds()


@dataclass
class ExecutionResult:
    """Result from a single agent execution."""

    task_id: str
    agent_name: str
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentOrchestrator:
    """
    Orchestrates execution of multiple agents with concurrency control.

    Features:
    - Async task queue with priority support
    - Concurrency limiting with configurable max concurrent agents
    - Automatic failure handling and logging
    - Result aggregation from multiple agents
    - Task tracking and execution metrics
    """

    def __init__(self, max_concurrent: int = 3):
        """
        Initialize the orchestrator.

        Args:
            max_concurrent: Maximum number of agents to run concurrently
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.task_queue: asyncio.PriorityQueue[Task] = asyncio.PriorityQueue()
        self.results: Dict[str, ExecutionResult] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self._task_counter = 0
        self._lock = asyncio.Lock()

        logger.info(
            f"Initialized AgentOrchestrator with max_concurrent={max_concurrent}"
        )

    async def dispatch_task(
        self,
        agent: BaseAgent,
        context: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> str:
        """
        Dispatch a task for execution.

        Args:
            agent: Agent to execute
            context: Execution context
            priority: Task priority level

        Returns:
            Task ID for tracking

        Raises:
            ValueError: If agent is None
        """
        if agent is None:
            raise ValueError("Agent cannot be None")

        async with self._lock:
            self._task_counter += 1
            task_id = f"{agent.name}_{self._task_counter}"

        task = Task(
            agent_name=agent.name,
            agent=agent,
            context=context,
            priority=priority,
            task_id=task_id,
        )

        await self.task_queue.put(task)
        logger.info(f"Dispatched task {task_id} for agent '{agent.name}'")

        return task_id

    async def _execute_single_task(self, task: Task) -> ExecutionResult:
        """
        Execute a single task with concurrency control.

        Args:
            task: Task to execute

        Returns:
            ExecutionResult with outcome
        """
        async with self.semaphore:
            try:
                logger.info(f"Executing task {task.task_id} (agent: {task.agent_name})")

                result = await task.agent.execute(task.context)

                task.result = result
                task.completed_at = datetime.now()
                execution_time = task.get_execution_time()

                logger.info(
                    f"Task {task.task_id} completed in {execution_time:.2f}s"
                )

                return ExecutionResult(
                    task_id=task.task_id,
                    agent_name=task.agent_name,
                    success=True,
                    result=result,
                    execution_time=execution_time,
                )

            except AgentExecutionError as e:
                task.error = str(e)
                task.completed_at = datetime.now()
                execution_time = task.get_execution_time()

                logger.error(
                    f"Task {task.task_id} failed: {e} "
                    f"(execution time: {execution_time:.2f}s)"
                )

                return ExecutionResult(
                    task_id=task.task_id,
                    agent_name=task.agent_name,
                    success=False,
                    error=str(e),
                    execution_time=execution_time,
                )

            except Exception as e:
                task.error = str(e)
                task.completed_at = datetime.now()
                execution_time = task.get_execution_time()

                logger.error(
                    f"Task {task.task_id} encountered unexpected error: {e}",
                    exc_info=True,
                )

                return ExecutionResult(
                    task_id=task.task_id,
                    agent_name=task.agent_name,
                    success=False,
                    error=f"Unexpected error: {e}",
                    execution_time=execution_time,
                )

    async def _worker(self) -> None:
        """
        Worker coroutine that continuously processes tasks from the queue.

        This is designed to run in the background and process tasks as they
        arrive or are dispatched.
        """
        while True:
            try:
                # Non-blocking get with timeout to allow graceful shutdown
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)

                # Execute task and store result
                result = await self._execute_single_task(task)
                self.results[result.task_id] = result

            except asyncio.TimeoutError:
                # No task available, continue waiting
                continue
            except asyncio.CancelledError:
                logger.debug("Worker task cancelled, shutting down")
                break
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)

    async def run_agents_parallel(
        self,
        agent_tasks: List[tuple[BaseAgent, Dict[str, Any]]],
        timeout: Optional[float] = None,
    ) -> List[ExecutionResult]:
        """
        Run multiple agents in parallel with concurrency control.

        Args:
            agent_tasks: List of (agent, context) tuples to execute
            timeout: Overall timeout for all tasks in seconds

        Returns:
            List of ExecutionResult objects with outcomes

        Raises:
            asyncio.TimeoutError: If timeout is exceeded
            ValueError: If agent_tasks is empty
        """
        if not agent_tasks:
            raise ValueError("agent_tasks cannot be empty")

        logger.info(f"Starting parallel execution of {len(agent_tasks)} tasks")

        # Dispatch all tasks
        task_ids = []
        for agent, context in agent_tasks:
            task_id = await self.dispatch_task(agent, context)
            task_ids.append(task_id)

        # Start worker coroutines
        worker_tasks = [
            asyncio.create_task(self._worker()) for _ in range(self.max_concurrent)
        ]

        try:
            # Wait for all tasks to be dispatched and processed
            async def _wait_for_completion():
                while len(self.results) < len(task_ids):
                    await asyncio.sleep(0.1)

            if timeout:
                await asyncio.wait_for(_wait_for_completion(), timeout=timeout)
            else:
                await _wait_for_completion()

        except asyncio.TimeoutError:
            logger.error(f"Parallel execution timed out after {timeout}s")
            raise

        finally:
            # Cancel all worker tasks
            for task in worker_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Return results in order
        results = [self.results[task_id] for task_id in task_ids]
        logger.info(
            f"Parallel execution completed: {sum(1 for r in results if r.success)} "
            f"succeeded, {sum(1 for r in results if not r.success)} failed"
        )

        return results

    async def run_sequential(
        self,
        agent_tasks: List[tuple[BaseAgent, Dict[str, Any]]],
        stop_on_failure: bool = False,
    ) -> List[ExecutionResult]:
        """
        Run agents sequentially (one at a time).

        Args:
            agent_tasks: List of (agent, context) tuples to execute
            stop_on_failure: If True, stop execution on first failure

        Returns:
            List of ExecutionResult objects with outcomes
        """
        results = []

        logger.info(
            f"Starting sequential execution of {len(agent_tasks)} tasks "
            f"(stop_on_failure={stop_on_failure})"
        )

        for agent, context in agent_tasks:
            try:
                task = Task(
                    agent_name=agent.name,
                    agent=agent,
                    context=context,
                )

                result = await self._execute_single_task(task)
                results.append(result)

                if not result.success and stop_on_failure:
                    logger.warning(
                        f"Stopping sequential execution due to failure in "
                        f"{result.agent_name}"
                    )
                    break

            except Exception as e:
                logger.error(f"Sequential execution error: {e}", exc_info=True)
                results.append(
                    ExecutionResult(
                        task_id="unknown",
                        agent_name=agent.name,
                        success=False,
                        error=str(e),
                    )
                )

                if stop_on_failure:
                    break

        return results

    def handle_agent_failure(
        self,
        task_id: str,
        error_callback: Optional[Callable[[str, str], None]] = None,
    ) -> Optional[ExecutionResult]:
        """
        Handle failure of a specific task.

        Args:
            task_id: ID of the failed task
            error_callback: Optional callback function(task_id, error) to invoke

        Returns:
            ExecutionResult for the failed task or None if not found
        """
        result = self.results.get(task_id)

        if result is None:
            logger.warning(f"Task {task_id} not found in results")
            return None

        if result.success:
            logger.warning(f"Task {task_id} did not fail")
            return result

        logger.info(f"Handling failure for task {task_id}: {result.error}")

        if error_callback:
            try:
                error_callback(task_id, result.error or "Unknown error")
            except Exception as e:
                logger.error(f"Error callback failed: {e}", exc_info=True)

        return result

    def get_result(self, task_id: str) -> Optional[ExecutionResult]:
        """
        Get the result of a specific task.

        Args:
            task_id: Task ID to retrieve

        Returns:
            ExecutionResult or None if not found
        """
        return self.results.get(task_id)

    def get_all_results(self) -> Dict[str, ExecutionResult]:
        """Get all execution results."""
        return dict(self.results)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all execution results.

        Returns:
            Dictionary with execution summary statistics
        """
        results_list = list(self.results.values())
        successful = [r for r in results_list if r.success]
        failed = [r for r in results_list if not r.success]
        execution_times = [
            r.execution_time for r in results_list if r.execution_time is not None
        ]

        return {
            "total_tasks": len(results_list),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": (
                len(successful) / len(results_list) if results_list else 0
            ),
            "avg_execution_time": (
                sum(execution_times) / len(execution_times)
                if execution_times
                else 0
            ),
            "min_execution_time": min(execution_times) if execution_times else 0,
            "max_execution_time": max(execution_times) if execution_times else 0,
        }

    def reset(self) -> None:
        """Reset all state and results."""
        self.results.clear()
        self.running_tasks.clear()
        self._task_counter = 0
        logger.info("Orchestrator reset")
