"""SubscriberComponent base class for data consuming components.

This module provides the abstract base class for components that consume
or subscribe to data from other components. Subscribers are typically used
as sinks in VSE_PY graphs to process or display final results.

Features:
- Blue color designation for visual identification
- Auto-execute support for event-driven processing
- Abstract process_inputs() method for subclass customization
- Input handling with optional automatic processing
"""

from abc import abstractmethod

from ..core.component_base import ComponentBase, ComponentState
from ..core.data_types import DataType, DataVariant


class SubscriberComponent(ComponentBase):
    """Abstract base class for components that subscribe to data.

    SubscriberComponent extends ComponentBase to provide a framework for components
    that consume data from other components. Subscribers are typically used as
    final processing nodes (sinks) in VSE_PY graphs.

    Key features:
    - Blue color (33, 150, 243) for visual identification in graphs
    - "Subscriber" category classification
    - Optional auto-execute mode for automatic processing when data arrives
    - Abstract process_inputs() method for subclass implementation
    - No output pins (subscribers are terminal nodes)

    Attributes:
        auto_execute: Whether component executes when input data arrives

    Examples:
        >>> class LoggerSubscriber(SubscriberComponent):
        ...     def get_name(self):
        ...         return "Logger"
        ...     def initialize(self):
        ...         self.add_input_pin("Data", DataType.ANY)
        ...     def process_inputs(self):
        ...         data_pin = self.get_input_pin("Data")
        ...         print(f"Received: {data_pin.data.to_string()}")
        >>> subscriber = LoggerSubscriber()
        >>> subscriber.set_auto_execute(True)
    """

    def __init__(self) -> None:
        """Initialize a SubscriberComponent.

        Sets up auto-execute mode for event-driven processing.
        """
        self._auto_execute: bool = False

        super().__init__()

    def get_category(self) -> str:
        """Get the component category.

        Returns:
            str: "Subscriber"
        """
        return "Subscriber"

    def get_color(self) -> tuple:
        """Get the component display color.

        Returns:
            tuple: Blue color (33, 150, 243)
        """
        return (33, 150, 243)

    def set_auto_execute(self, enabled: bool) -> None:
        """Enable or disable automatic execution.

        When enabled, the component will automatically execute whenever input
        data arrives (via callbacks). When disabled, execution only occurs on
        explicit calls to execute().

        For subscribers, auto-execute is particularly useful as it allows
        real-time processing of incoming data from publishers or processors.

        Args:
            enabled: True to enable auto-execute, False to disable

        Raises:
            TypeError: If enabled is not a boolean

        Examples:
            >>> subscriber.set_auto_execute(True)
            >>> subscriber.set_auto_execute(False)
        """
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a boolean")

        self._auto_execute = enabled

    @property
    def auto_execute(self) -> bool:
        """Get auto-execute status.

        Returns:
            bool: True if auto-execute is enabled
        """
        return self._auto_execute

    @abstractmethod
    def process_inputs(self) -> None:
        """Process input data from connected sources.

        Must be implemented by subclasses. This method should:
        1. Retrieve input data from input pins
        2. Process or consume the data
        3. Store results, write to disk, display, etc.

        Unlike processors, subscribers do not produce output. They are
        terminal nodes that consume data from the graph.

        Subclasses should handle their own error checking and reporting.
        The base execute() method handles state management.

        Examples:
            >>> def process_inputs(self):
            ...     input_pin = self.get_input_pin("Value")
            ...     value = input_pin.data.to_float()
            ...     self.log_value(value)
        """
        pass

    def execute(self) -> None:
        """Execute the component's main logic.

        This method calls the abstract process_inputs() method to consume
        and process input data. It also manages component state.

        Workflow:
        1. If disabled, return without processing
        2. Call process_inputs() to consume data
        3. Handle any exceptions and report errors

        Examples:
            >>> subscriber.execute()
        """
        # Don't execute if disabled
        if self._state == ComponentState.DISABLED:
            return

        try:
            self.set_state(ComponentState.RUNNING)

            # Call the process_inputs method
            self.process_inputs()

            self.set_state(ComponentState.IDLE)

        except Exception as e:
            self.report_error(f"Error during input processing: {str(e)}")

    def __repr__(self) -> str:
        """Return string representation of this component.

        Returns:
            str: Representation showing auto-execute status
        """
        return (f"{self.__class__.__name__}("
                f"id={self._id[:8]}..., "
                f"auto_execute={self._auto_execute}, "
                f"inputs={len(self._input_pins)})")
