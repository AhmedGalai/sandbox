"""ProcessorComponent base class for data processing components.

This module provides the abstract base class for components that transform
or process input data and produce output. Processors are the core computational
nodes in VSE_PY graphs, handling data transformations and calculations.

Features:
- Orange color designation for visual identification
- Input validation to ensure all inputs are connected
- Optional pass-through mode for testing
- Abstract process() method for subclass customization
- Auto-execute support for event-driven processing
"""

from abc import abstractmethod
from typing import Optional

from ..core.component_base import ComponentBase, ComponentState
from ..core.data_types import DataType, DataVariant


class ProcessorComponent(ComponentBase):
    """Abstract base class for components that process data.

    ProcessorComponent extends ComponentBase to provide a framework for components
    that transform or process input data and produce output. This is the primary
    type of component for computational operations in VSE_PY graphs.

    Key features:
    - Orange color (255, 152, 0) for visual identification in graphs
    - "Processor" category classification
    - Input validation ensuring all inputs are connected before processing
    - Optional auto-execute mode for event-driven execution
    - Optional pass-through mode for bypassing processing
    - Abstract process() method for subclass implementation

    Attributes:
        auto_execute: Whether component executes on input data arrival
        pass_through: Whether to skip processing and pass input to output directly

    Examples:
        >>> class AddProcessor(ProcessorComponent):
        ...     def get_name(self):
        ...         return "Add"
        ...     def initialize(self):
        ...         self.add_input_pin("A", DataType.INTEGER)
        ...         self.add_input_pin("B", DataType.INTEGER)
        ...         self.add_output_pin("Sum", DataType.INTEGER)
        ...     def process(self):
        ...         a_pin = self.get_input_pin("A")
        ...         b_pin = self.get_input_pin("B")
        ...         sum_val = a_pin.data.to_int() + b_pin.data.to_int()
        ...         self.get_output_pin("Sum").transmit_data(DataVariant(sum_val))
        >>> processor = AddProcessor()
        >>> processor.set_auto_execute(True)
    """

    def __init__(self) -> None:
        """Initialize a ProcessorComponent.

        Sets up auto-execute and pass-through modes.
        """
        self._auto_execute: bool = False
        self._pass_through: bool = False

        super().__init__()

    def get_category(self) -> str:
        """Get the component category.

        Returns:
            str: "Processor"
        """
        return "Processor"

    def get_color(self) -> tuple:
        """Get the component display color.

        Returns:
            tuple: Orange color (255, 152, 0)
        """
        return (255, 152, 0)

    def set_auto_execute(self, enabled: bool) -> None:
        """Enable or disable automatic execution.

        When enabled, the component will automatically execute whenever input
        data arrives (via callbacks). When disabled, execution only occurs on
        explicit calls to execute().

        Args:
            enabled: True to enable auto-execute, False to disable

        Raises:
            TypeError: If enabled is not a boolean

        Examples:
            >>> processor.set_auto_execute(True)
            >>> processor.set_auto_execute(False)
        """
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a boolean")

        self._auto_execute = enabled

    def set_pass_through(self, enabled: bool) -> None:
        """Enable or disable pass-through mode.

        When enabled, input data is passed directly to output pins without
        processing. This is useful for testing or temporarily disabling
        a processor without removing it from the graph.

        Args:
            enabled: True to enable pass-through, False to disable

        Raises:
            TypeError: If enabled is not a boolean

        Examples:
            >>> processor.set_pass_through(True)
            >>> processor.set_pass_through(False)
        """
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a boolean")

        self._pass_through = enabled

    @property
    def auto_execute(self) -> bool:
        """Get auto-execute status.

        Returns:
            bool: True if auto-execute is enabled
        """
        return self._auto_execute

    @property
    def pass_through(self) -> bool:
        """Get pass-through mode status.

        Returns:
            bool: True if pass-through mode is enabled
        """
        return self._pass_through

    def validate_inputs(self) -> bool:
        """Validate that all input pins are connected.

        Checks that every input pin has an active connection. This ensures
        that all required data is available before processing.

        Returns:
            bool: True if all input pins are connected, False otherwise

        Examples:
            >>> if processor.validate_inputs():
            ...     processor.process()
            ... else:
            ...     processor.report_error("Missing input connections")
        """
        for pin_name, pin in self._input_pins.items():
            if not pin.is_connected():
                return False
        return True

    @abstractmethod
    def process(self) -> None:
        """Process input data and produce output.

        Must be implemented by subclasses. This method should:
        1. Retrieve input data from input pins
        2. Perform processing or transformation
        3. Transmit results via output pins

        Subclasses should handle their own error checking and reporting.
        The base execute() method handles validation and state management.

        Examples:
            >>> def process(self):
            ...     input_pin = self.get_input_pin("Value")
            ...     output_pin = self.get_output_pin("Result")
            ...     value = input_pin.data.to_float()
            ...     result = value * 2.0
            ...     output_pin.transmit_data(DataVariant(result))
        """
        pass

    def execute(self) -> None:
        """Execute the component's main logic.

        This method validates inputs, handles pass-through mode, and calls
        the abstract process() method. It also manages component state.

        Workflow:
        1. If disabled, return without processing
        2. If pass-through enabled, copy inputs to outputs
        3. Otherwise, validate inputs and call process()
        4. Handle any exceptions and report errors

        Examples:
            >>> processor.execute()
        """
        # Don't execute if disabled
        if self._state == ComponentState.DISABLED:
            return

        try:
            self.set_state(ComponentState.RUNNING)

            # Handle pass-through mode
            if self._pass_through:
                # Copy input pins to output pins with matching names
                for input_name, input_pin in self._input_pins.items():
                    output_pin = self.get_output_pin(input_name)
                    if output_pin is not None:
                        output_pin.transmit_data(input_pin.data)
            else:
                # Validate that all inputs are connected
                if not self.validate_inputs():
                    self.report_error("Not all input pins are connected")
                    return

                # Call the process method
                self.process()

            self.set_state(ComponentState.IDLE)

        except Exception as e:
            self.report_error(f"Error during processing: {str(e)}")

    def __repr__(self) -> str:
        """Return string representation of this component.

        Returns:
            str: Representation showing auto-execute and pass-through status
        """
        return (f"{self.__class__.__name__}("
                f"id={self._id[:8]}..., "
                f"auto_execute={self._auto_execute}, "
                f"pass_through={self._pass_through}, "
                f"inputs={len(self._input_pins)}, "
                f"outputs={len(self._output_pins)})")
