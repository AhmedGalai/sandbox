"""ExecutionEngine for executing component networks

This module provides the ExecutionEngine class, which orchestrates the execution
of component graphs. It manages:

- Execution state (IDLE, RUNNING, PAUSED, ERROR)
- Execution mode (CONTINUOUS or SINGLE_STEP)
- Execution rate control (default 60 Hz)
- Topological sorting of components using Kahn's algorithm
- Background thread execution with proper cleanup
- Execution statistics (iteration count, error count, last error)
- Callback support for state changes, iteration completion, and errors

The ExecutionEngine uses a background thread to run the component graph
in a non-blocking manner, maintaining the specified execution rate.
"""

from enum import Enum, auto
from typing import List, Optional, Callable, Dict, Set
import threading
import time


class ExecutionState(Enum):
    """Execution state enumeration.

    Represents the current state of the execution engine.

    Attributes:
        IDLE: Engine is not running
        RUNNING: Engine is actively executing components
        PAUSED: Engine is paused, can be resumed
        ERROR: Engine encountered an error and stopped
    """
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    ERROR = auto()


class ExecutionMode(Enum):
    """Execution mode enumeration.

    Determines how the execution engine runs.

    Attributes:
        CONTINUOUS: Run continuously at the specified rate
        SINGLE_STEP: Execute one iteration per step() call
    """
    CONTINUOUS = auto()
    SINGLE_STEP = auto()


class ExecutionEngine:
    """Orchestrates execution of component graphs.

    The ExecutionEngine manages the execution of a component graph by:
    1. Performing topological sort to determine execution order
    2. Running the components in a background thread
    3. Maintaining execution statistics
    4. Providing callbacks for state changes and errors
    5. Supporting both continuous and single-step execution modes

    The engine uses Kahn's algorithm for topological sorting and detects
    cycles in the component graph.

    Thread-safe for all operations.

    Attributes:
        _state: Current execution state (IDLE, RUNNING, PAUSED, ERROR)
        _mode: Execution mode (CONTINUOUS, SINGLE_STEP)
        _context: ExecutionContext containing components and connections
        _execution_rate: Execution rate in Hz (default 60)
        _execution_order: Topologically sorted list of components
        _iteration_count: Number of completed iterations
        _error_count: Number of errors encountered
        _last_error: Description of the last error
        _running: Internal flag for execution loop
        _thread: Background execution thread
        _stop_event: Event to signal thread shutdown
        _pause_event: Event to signal pause/resume
        _lock: Lock for thread-safe access to state
        _on_state_changed: State change callback
        _on_iteration_completed: Iteration completion callback
        _on_error: Error callback
    """

    def __init__(self) -> None:
        """Initialize the ExecutionEngine.

        Creates a new engine in IDLE state with CONTINUOUS mode, 60 Hz
        execution rate, and no context.
        """
        self._state: ExecutionState = ExecutionState.IDLE
        self._mode: ExecutionMode = ExecutionMode.CONTINUOUS
        self._context: Optional['ExecutionContext'] = None
        self._execution_rate: float = 60.0  # Hz
        self._execution_order: List['ComponentBase'] = []
        self._iteration_count: int = 0
        self._error_count: int = 0
        self._last_error: str = ""
        self._running: bool = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event: threading.Event = threading.Event()
        self._pause_event: threading.Event = threading.Event()
        self._lock: threading.Lock = threading.Lock()

        # Callbacks
        self._on_state_changed: Optional[Callable[[ExecutionState], None]] = None
        self._on_iteration_completed: Optional[Callable[[], None]] = None
        self._on_error: Optional[Callable[[str], None]] = None

    @property
    def state(self) -> ExecutionState:
        """Get the current execution state.

        Returns:
            ExecutionState: The current state (IDLE, RUNNING, PAUSED, ERROR)

        Examples:
            >>> engine = ExecutionEngine()
            >>> engine.state == ExecutionState.IDLE
            True
        """
        with self._lock:
            return self._state

    def _set_state(self, state: ExecutionState) -> None:
        """Internal method to set execution state with callback notification.

        Args:
            state: The new ExecutionState

        This is an internal method used to update state atomically with
        callback notification.
        """
        with self._lock:
            self._state = state

        # Invoke callback outside lock to prevent deadlock
        if self._on_state_changed is not None:
            try:
                self._on_state_changed(state)
            except Exception as e:
                # Log callback errors but don't propagate
                print(f"Error in state_changed callback: {e}")

    @property
    def mode(self) -> ExecutionMode:
        """Get the current execution mode.

        Returns:
            ExecutionMode: The current mode (CONTINUOUS or SINGLE_STEP)

        Examples:
            >>> engine = ExecutionEngine()
            >>> engine.mode == ExecutionMode.CONTINUOUS
            True
        """
        with self._lock:
            return self._mode

    @mode.setter
    def mode(self, new_mode: ExecutionMode) -> None:
        """Set the execution mode.

        Args:
            new_mode: The new ExecutionMode (CONTINUOUS or SINGLE_STEP)

        Raises:
            TypeError: If new_mode is not an ExecutionMode

        Examples:
            >>> engine = ExecutionEngine()
            >>> engine.mode = ExecutionMode.SINGLE_STEP
            >>> engine.mode == ExecutionMode.SINGLE_STEP
            True
        """
        if not isinstance(new_mode, ExecutionMode):
            raise TypeError("new_mode must be an ExecutionMode enum value")

        with self._lock:
            self._mode = new_mode

    @property
    def execution_rate(self) -> float:
        """Get the execution rate in Hz.

        Returns:
            float: Execution rate in hertz (cycles per second)

        Examples:
            >>> engine = ExecutionEngine()
            >>> engine.execution_rate
            60.0
        """
        with self._lock:
            return self._execution_rate

    @execution_rate.setter
    def execution_rate(self, rate_hz: float) -> None:
        """Set the execution rate in Hz.

        Args:
            rate_hz: Execution rate in hertz

        Raises:
            ValueError: If rate_hz is not positive

        Examples:
            >>> engine = ExecutionEngine()
            >>> engine.execution_rate = 30.0
            >>> engine.execution_rate
            30.0
        """
        if rate_hz <= 0:
            raise ValueError("execution_rate must be positive")

        with self._lock:
            self._execution_rate = rate_hz

    @property
    def iteration_count(self) -> int:
        """Get the number of completed iterations.

        Returns:
            int: Total number of iterations executed

        Examples:
            >>> engine = ExecutionEngine()
            >>> engine.iteration_count
            0
        """
        with self._lock:
            return self._iteration_count

    @property
    def error_count(self) -> int:
        """Get the number of errors encountered.

        Returns:
            int: Total number of errors during execution

        Examples:
            >>> engine = ExecutionEngine()
            >>> engine.error_count
            0
        """
        with self._lock:
            return self._error_count

    @property
    def last_error(self) -> str:
        """Get the description of the last error.

        Returns:
            str: Last error message, or empty string if no error

        Examples:
            >>> engine = ExecutionEngine()
            >>> engine.last_error
            ''
        """
        with self._lock:
            return self._last_error

    def set_execution_context(self, context: 'ExecutionContext') -> bool:
        """Set the execution context containing components and connections.

        Performs topological sort on the component graph. Returns False if
        a cycle is detected.

        Args:
            context: ExecutionContext with components and connections

        Returns:
            bool: True if context was set and topological sort succeeded,
                  False if a cycle was detected

        Examples:
            >>> from vse_py.core.execution_context import ExecutionContext
            >>> engine = ExecutionEngine()
            >>> context = ExecutionContext()
            >>> engine.set_execution_context(context)
            True
        """
        if context is None:
            raise TypeError("context cannot be None")

        with self._lock:
            self._context = context

        return self._build_execution_order()

    def _build_execution_order(self) -> bool:
        """Build execution order using topological sort (Kahn's algorithm).

        Performs a topological sort on the component graph to determine the
        execution order. Detects cycles and returns False if found.

        Returns:
            bool: True if sort succeeded, False if a cycle was detected

        The algorithm:
        1. Build a dependency graph from connections
        2. Count in-degrees for each component
        3. Start with nodes having zero in-degree (no dependencies)
        4. Process nodes in topological order
        5. Return False if any nodes remain (indicates a cycle)
        """
        if not self._context:
            return False

        try:
            # Build dependency graph
            graph: Dict[str, Set[str]] = {}
            in_degree: Dict[str, int] = {}

            # Initialize graph for all components
            for comp in self._context.components:
                graph[comp.id] = set()
                in_degree[comp.id] = 0

            # Add edges and update in-degrees based on connections
            for conn in self._context.connections:
                # Get source component ID (from source pin's parent component)
                # Get destination component ID (from destination pin's parent component)
                if hasattr(conn.source, 'component_id') and hasattr(conn.destination, 'component_id'):
                    source_comp_id = conn.source.component_id
                    dest_comp_id = conn.destination.component_id

                    # Only add edge if components are different (avoid self-loops)
                    if source_comp_id != dest_comp_id:
                        if dest_comp_id not in graph[source_comp_id]:
                            graph[source_comp_id].add(dest_comp_id)
                            in_degree[dest_comp_id] = in_degree.get(dest_comp_id, 0) + 1

            # Kahn's algorithm: topological sort
            queue: List[str] = [comp_id for comp_id, degree in in_degree.items() if degree == 0]
            result: List[str] = []

            while queue:
                comp_id = queue.pop(0)
                result.append(comp_id)

                # For each neighbor of current node
                for neighbor in graph[comp_id]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)

            # Check for cycles: if we didn't process all components, there's a cycle
            if len(result) != len(self._context.components):
                with self._lock:
                    self._last_error = "Cycle detected in component graph"
                return False

            # Convert component IDs back to component objects
            comp_map = {c.id: c for c in self._context.components}
            with self._lock:
                self._execution_order = [comp_map[comp_id] for comp_id in result]

            return True

        except Exception as e:
            with self._lock:
                self._last_error = f"Error during topological sort: {str(e)}"
            return False

    def start(self) -> None:
        """Start the execution engine.

        Starts the background execution thread. If in CONTINUOUS mode, the
        engine will continuously execute components at the specified rate.
        If in SINGLE_STEP mode, components will only execute when step() is called.

        Does nothing if already running or in ERROR state.

        Examples:
            >>> from vse_py.core.execution_context import ExecutionContext
            >>> engine = ExecutionEngine()
            >>> context = ExecutionContext()
            >>> engine.set_execution_context(context)
            True
            >>> engine.start()
            >>> engine.state == ExecutionState.RUNNING
            True
            >>> time.sleep(0.1)
            >>> engine.stop()
        """
        with self._lock:
            if self._state == ExecutionState.ERROR:
                return
            if self._state == ExecutionState.RUNNING:
                return

        # Rebuild execution order to ensure it's up to date
        if not self._build_execution_order():
            self._set_state(ExecutionState.ERROR)
            return

        self._running = True
        self._stop_event.clear()
        self._pause_event.clear()
        self._set_state(ExecutionState.RUNNING)

        # Start background thread
        self._thread = threading.Thread(target=self._execution_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the execution engine.

        Stops the background execution thread and returns to IDLE state.
        Any pending iterations are completed.

        Examples:
            >>> engine = ExecutionEngine()
            >>> engine.start()
            >>> engine.stop()
            >>> engine.state == ExecutionState.IDLE
            True
        """
        self._running = False
        self._stop_event.set()
        self._pause_event.set()  # Resume if paused

        if self._thread is not None:
            self._thread.join()

        self._set_state(ExecutionState.IDLE)

    def pause(self) -> None:
        """Pause the execution engine.

        Pauses execution without stopping the thread. The engine can be
        resumed by calling start() again.

        Examples:
            >>> engine = ExecutionEngine()
            >>> engine.start()
            >>> engine.pause()
            >>> engine.state == ExecutionState.PAUSED
            True
        """
        self._pause_event.clear()
        self._set_state(ExecutionState.PAUSED)

    def step(self) -> None:
        """Execute a single iteration.

        Executes one complete cycle of all components in topological order.
        Can be called from any state and doesn't change the execution state.

        Useful for debugging and single-step execution mode.

        Examples:
            >>> engine = ExecutionEngine()
            >>> context = ExecutionContext()
            >>> engine.set_execution_context(context)
            True
            >>> engine.step()
            >>> engine.iteration_count
            1
        """
        self._execute_iteration()

    def reset(self) -> None:
        """Reset execution statistics.

        Clears the iteration count, error count, and last error. Useful
        when starting a new execution session.

        Examples:
            >>> engine = ExecutionEngine()
            >>> engine.step()
            >>> engine.iteration_count
            1
            >>> engine.reset()
            >>> engine.iteration_count
            0
        """
        with self._lock:
            self._iteration_count = 0
            self._error_count = 0
            self._last_error = ""

    def _execution_loop(self) -> None:
        """Main execution loop running in background thread.

        Continuously executes iterations at the specified rate. Respects
        pause and stop events.
        """
        interval = 1.0 / self._execution_rate

        while self._running:
            start_time = time.time()

            # Check if paused
            if self._state == ExecutionState.PAUSED:
                self._stop_event.wait(0.01)
                continue

            # Execute one iteration
            self._execute_iteration()

            # Maintain execution rate
            elapsed = time.time() - start_time
            sleep_time = interval - elapsed

            if sleep_time > 0:
                self._stop_event.wait(sleep_time)

    def _execute_iteration(self) -> None:
        """Execute one complete iteration of the component graph.

        Executes all components in topological order, catching and recording
        any errors. Updates statistics and invokes callbacks.
        """
        with self._lock:
            if not self._execution_order:
                return

            execution_order = self._execution_order.copy()

        # Execute all components in order (outside lock to avoid deadlock)
        for component in execution_order:
            try:
                # Skip disabled components
                if hasattr(component, 'state') and hasattr(component.state, 'name'):
                    state_name = component.state.name if hasattr(component.state, 'name') else str(component.state)
                    if state_name == 'DISABLED':
                        continue

                component.execute()

            except Exception as e:
                with self._lock:
                    self._error_count += 1
                    self._last_error = str(e)

                # Report error to component if possible
                if hasattr(component, 'report_error'):
                    try:
                        component.report_error(str(e))
                    except Exception:
                        pass

                # Invoke error callback outside lock
                if self._on_error is not None:
                    try:
                        self._on_error(str(e))
                    except Exception:
                        pass

        # Update iteration count and invoke callback
        with self._lock:
            self._iteration_count += 1

        if self._on_iteration_completed is not None:
            try:
                self._on_iteration_completed()
            except Exception:
                pass

    # Callback registration

    def on_state_changed(self, callback: Callable[[ExecutionState], None]) -> None:
        """Register a callback for state changes.

        The callback will be invoked whenever the execution state changes
        with the new state as an argument.

        Args:
            callback: Function taking ExecutionState and returning None

        Raises:
            TypeError: If callback is not callable or None

        Examples:
            >>> engine = ExecutionEngine()
            >>> def on_state_change(state):
            ...     print(f"State changed to {state.name}")
            >>> engine.on_state_changed(on_state_change)
        """
        if callback is not None and not callable(callback):
            raise TypeError("callback must be callable or None")

        with self._lock:
            self._on_state_changed = callback

    def on_iteration_completed(self, callback: Callable[[], None]) -> None:
        """Register a callback for iteration completion.

        The callback will be invoked after each complete iteration of all
        components.

        Args:
            callback: Function taking no arguments and returning None

        Raises:
            TypeError: If callback is not callable or None

        Examples:
            >>> engine = ExecutionEngine()
            >>> def on_iteration():
            ...     print(f"Iteration {engine.iteration_count} completed")
            >>> engine.on_iteration_completed(on_iteration)
        """
        if callback is not None and not callable(callback):
            raise TypeError("callback must be callable or None")

        with self._lock:
            self._on_iteration_completed = callback

    def on_error(self, callback: Callable[[str], None]) -> None:
        """Register a callback for errors.

        The callback will be invoked whenever an error occurs during
        component execution with the error message as an argument.

        Args:
            callback: Function taking error message string and returning None

        Raises:
            TypeError: If callback is not callable or None

        Examples:
            >>> engine = ExecutionEngine()
            >>> def on_exec_error(msg):
            ...     print(f"Error: {msg}")
            >>> engine.on_error(on_exec_error)
        """
        if callback is not None and not callable(callback):
            raise TypeError("callback must be callable or None")

        with self._lock:
            self._on_error = callback

    def __repr__(self) -> str:
        """Return string representation of this ExecutionEngine.

        Returns:
            str: Representation showing state, mode, and statistics
        """
        with self._lock:
            return (f"ExecutionEngine("
                    f"state={self._state.name}, "
                    f"mode={self._mode.name}, "
                    f"rate={self._execution_rate:.1f} Hz, "
                    f"iterations={self._iteration_count}, "
                    f"errors={self._error_count})")
