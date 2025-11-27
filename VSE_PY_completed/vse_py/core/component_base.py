"""ComponentBase abstract class for all VSE_PY components.

This module provides the abstract base class that all components must inherit from.
It defines the contract for component behavior including:
- Component identification (name, category, color)
- Pin management (inputs and outputs)
- Parameter configuration
- State management
- Execution flow
- Error handling
- Serialization/deserialization
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Any
import uuid

from .pin import Pin, InputPin, OutputPin
from .parameter import Parameter
from .data_types import DataType, DataVariant


class ComponentState(Enum):
    """Component execution state enumeration.

    Attributes:
        IDLE: Component is waiting, not currently executing
        RUNNING: Component is currently executing
        ERROR: Component encountered an error during execution
        DISABLED: Component is disabled and will not execute
    """
    IDLE = auto()
    RUNNING = auto()
    ERROR = auto()
    DISABLED = auto()


class ComponentBase(ABC):
    """Abstract base class for all VSE_PY components.

    This class provides the core interface and functionality that all components
    must implement. Components are the building blocks of VSE_PY graphs, representing
    distinct computational or data-flow units.

    Attributes:
        id: Unique identifier for this component (UUID-based)
        state: Current execution state of the component

    Subclasses must implement:
        - get_name(): Return the component's name
        - get_category(): Return the component's category
        - get_color(): Return the component's color as (R, G, B) tuple
        - execute(): Define the component's main execution logic
    """

    def __init__(self) -> None:
        """Initialize a ComponentBase instance.

        Sets up the component with default state and empty pin/parameter collections.
        The initialize() method is called at the end to allow subclasses to perform
        custom setup.
        """
        self._id: str = str(uuid.uuid4())
        self._state: ComponentState = ComponentState.IDLE
        self._input_pins: Dict[str, InputPin] = {}
        self._output_pins: Dict[str, OutputPin] = {}
        self._parameters: Dict[str, Parameter] = {}
        self._state_changed_callbacks: List[Callable[[ComponentState], None]] = []
        self._error_callbacks: List[Callable[[str], None]] = []
        self._error_message: str = ""

        # Call initialize for subclass setup
        self.initialize()

    # ========================= Identification Methods =========================

    @property
    def id(self) -> str:
        """Get the unique identifier of this component.

        Returns:
            str: UUID string uniquely identifying this component
        """
        return self._id

    def set_id(self, component_id: str) -> None:
        """Set the component ID (used during deserialization).

        This method allows restoring a component's ID when deserializing from storage.
        Should not be used in normal operation as IDs are auto-generated.

        Args:
            component_id: The new UUID to assign to this component

        Raises:
            ValueError: If component_id is empty
        """
        if not component_id or not isinstance(component_id, str):
            raise ValueError("component_id must be a non-empty string")
        self._id = component_id

    @abstractmethod
    def get_name(self) -> str:
        """Get the human-readable name of this component.

        Must be implemented by subclasses. Examples: "Add", "Multiply", "Logger"

        Returns:
            str: The component's name
        """
        pass

    @abstractmethod
    def get_category(self) -> str:
        """Get the category/type of this component.

        Must be implemented by subclasses. Examples: "Math", "Logic", "Publisher"

        Returns:
            str: The component's category
        """
        pass

    @abstractmethod
    def get_color(self) -> tuple:
        """Get the display color for this component.

        Must be implemented by subclasses. The color is used in UI representations.

        Returns:
            tuple: RGB color as (R, G, B) where each component is 0-255
        """
        pass

    # ========================= Pin Management Methods =========================

    def add_input_pin(self, name: str, dtype: DataType) -> InputPin:
        """Add an input pin to this component.

        Creates a new InputPin and registers it with this component. The pin name
        must be unique among input pins for this component.

        Args:
            name: Unique name for the input pin
            dtype: DataType for the pin

        Returns:
            InputPin: The newly created input pin

        Raises:
            ValueError: If a pin with this name already exists
            TypeError: If dtype is not a DataType

        Examples:
            >>> component.add_input_pin("X", DataType.INTEGER)
            InputPin(id=..., name='X', dtype=integer, status=disconnected)
        """
        if name in self._input_pins:
            raise ValueError(f"Input pin '{name}' already exists")

        pin = InputPin(name, dtype)
        self._input_pins[name] = pin
        return pin

    def add_output_pin(self, name: str, dtype: DataType) -> OutputPin:
        """Add an output pin to this component.

        Creates a new OutputPin and registers it with this component. The pin name
        must be unique among output pins for this component.

        Args:
            name: Unique name for the output pin
            dtype: DataType for the pin

        Returns:
            OutputPin: The newly created output pin

        Raises:
            ValueError: If a pin with this name already exists
            TypeError: If dtype is not a DataType

        Examples:
            >>> component.add_output_pin("Sum", DataType.INTEGER)
            OutputPin(id=..., name='Sum', dtype=integer, connections=0)
        """
        if name in self._output_pins:
            raise ValueError(f"Output pin '{name}' already exists")

        pin = OutputPin(name, dtype)
        self._output_pins[name] = pin
        return pin

    def get_input_pin(self, name: str) -> Optional[InputPin]:
        """Get an input pin by name.

        Args:
            name: The name of the input pin

        Returns:
            InputPin: The requested input pin, or None if not found
        """
        return self._input_pins.get(name)

    def get_output_pin(self, name: str) -> Optional[OutputPin]:
        """Get an output pin by name.

        Args:
            name: The name of the output pin

        Returns:
            OutputPin: The requested output pin, or None if not found
        """
        return self._output_pins.get(name)

    @property
    def input_pins(self) -> Dict[str, InputPin]:
        """Get all input pins as a dictionary.

        Returns a copy to prevent external modification of the internal dictionary.

        Returns:
            Dict[str, InputPin]: Dictionary mapping pin names to InputPin objects
        """
        return self._input_pins.copy()

    @property
    def output_pins(self) -> Dict[str, OutputPin]:
        """Get all output pins as a dictionary.

        Returns a copy to prevent external modification of the internal dictionary.

        Returns:
            Dict[str, OutputPin]: Dictionary mapping pin names to OutputPin objects
        """
        return self._output_pins.copy()

    # ========================= Parameter Management Methods =========================

    def add_parameter(self, parameter: Parameter) -> None:
        """Add a parameter to this component.

        Parameters allow configuration of component behavior. The parameter name
        must be unique within this component.

        Args:
            parameter: The Parameter object to add

        Raises:
            ValueError: If a parameter with this name already exists
            TypeError: If parameter is not a Parameter instance

        Examples:
            >>> component.add_parameter(IntParameter("threshold", default=10))
        """
        if not isinstance(parameter, Parameter):
            raise TypeError("parameter must be a Parameter instance")

        if parameter.name in self._parameters:
            raise ValueError(f"Parameter '{parameter.name}' already exists")

        self._parameters[parameter.name] = parameter

    def get_parameter(self, name: str) -> Optional[Parameter]:
        """Get a parameter by name.

        Args:
            name: The name of the parameter

        Returns:
            Parameter: The requested parameter, or None if not found
        """
        return self._parameters.get(name)

    @property
    def parameters(self) -> Dict[str, Parameter]:
        """Get all parameters as a dictionary.

        Returns a copy to prevent external modification of the internal dictionary.

        Returns:
            Dict[str, Parameter]: Dictionary mapping parameter names to Parameter objects
        """
        return self._parameters.copy()

    # ========================= State Management Methods =========================

    @property
    def state(self) -> ComponentState:
        """Get the current execution state of this component.

        Returns:
            ComponentState: The current state (IDLE, RUNNING, ERROR, or DISABLED)
        """
        return self._state

    def set_state(self, new_state: ComponentState) -> None:
        """Set the component state and invoke callbacks.

        When the state changes, all registered state change callbacks are invoked.

        Args:
            new_state: The new ComponentState to set

        Raises:
            TypeError: If new_state is not a ComponentState

        Examples:
            >>> component.set_state(ComponentState.RUNNING)
            >>> component.state
            <ComponentState.RUNNING: 2>
        """
        if not isinstance(new_state, ComponentState):
            raise TypeError("new_state must be a ComponentState enum value")

        if self._state != new_state:
            self._state = new_state
            self._invoke_state_changed_callbacks(new_state)

    # ========================= Callback Management Methods =========================

    def on_state_changed(self, callback: Callable[[ComponentState], None]) -> None:
        """Register a callback for state change events.

        The callback will be invoked whenever the component's state changes.

        Args:
            callback: Function taking a ComponentState and returning None

        Raises:
            TypeError: If callback is not callable

        Examples:
            >>> def on_state(state):
            ...     print(f"State changed to {state}")
            >>> component.on_state_changed(on_state)
        """
        if not callable(callback):
            raise TypeError("callback must be callable")

        if callback not in self._state_changed_callbacks:
            self._state_changed_callbacks.append(callback)

    def on_error(self, callback: Callable[[str], None]) -> None:
        """Register a callback for error events.

        The callback will be invoked whenever an error is reported.

        Args:
            callback: Function taking an error message string and returning None

        Raises:
            TypeError: If callback is not callable

        Examples:
            >>> def on_err(msg):
            ...     print(f"Error: {msg}")
            >>> component.on_error(on_err)
        """
        if not callable(callback):
            raise TypeError("callback must be callable")

        if callback not in self._error_callbacks:
            self._error_callbacks.append(callback)

    def _invoke_state_changed_callbacks(self, state: ComponentState) -> None:
        """Invoke all registered state change callbacks.

        Called internally when the component state changes.

        Args:
            state: The new ComponentState
        """
        for callback in self._state_changed_callbacks:
            try:
                callback(state)
            except Exception as e:
                print(f"Error in state changed callback: {e}")

    def _invoke_error_callbacks(self, message: str) -> None:
        """Invoke all registered error callbacks.

        Called internally when an error is reported.

        Args:
            message: The error message string
        """
        for callback in self._error_callbacks:
            try:
                callback(message)
            except Exception as e:
                print(f"Error in error callback: {e}")

    # ========================= Error Reporting Methods =========================

    def report_error(self, message: str) -> None:
        """Report an error in this component.

        Sets the component state to ERROR and invokes error callbacks.

        Args:
            message: Description of the error

        Raises:
            ValueError: If message is empty

        Examples:
            >>> component.report_error("Invalid input value")
        """
        if not message or not isinstance(message, str):
            raise ValueError("message must be a non-empty string")

        self._error_message = message
        self.set_state(ComponentState.ERROR)
        self._invoke_error_callbacks(message)

    @property
    def error_message(self) -> str:
        """Get the last error message.

        Returns:
            str: The error message, or empty string if no error
        """
        return self._error_message

    # ========================= Execution Methods =========================

    @abstractmethod
    def execute(self) -> None:
        """Execute the component's main logic.

        Must be implemented by subclasses. This method is called by the execution
        engine to perform the component's primary function.

        Subclasses should:
        1. Check if component is enabled
        2. Set state to RUNNING
        3. Perform computation
        4. Transmit output via output pins
        5. Set state back to IDLE
        6. Handle exceptions and call report_error() as needed
        """
        pass

    # ========================= Initialization Hook =========================

    def initialize(self) -> None:
        """Initialize component-specific setup.

        Called automatically at the end of __init__. Subclasses can override this
        to perform custom initialization like adding pins and parameters.

        This is called after all base class initialization is complete, so it's
        safe to call add_input_pin(), add_output_pin(), add_parameter(), etc.

        Examples:
            >>> class MyComponent(ComponentBase):
            ...     def initialize(self):
            ...         self.add_input_pin("Input", DataType.INTEGER)
            ...         self.add_output_pin("Output", DataType.INTEGER)
        """
        pass

    # ========================= Serialization Methods =========================

    def serialize(self) -> dict:
        """Serialize the component to a dictionary.

        Returns a complete representation of the component that can be saved
        and later restored via deserialize(). This includes:
        - Component ID
        - Component state
        - All parameter values

        Returns:
            dict: Serialized component data with keys:
                  - id: Component ID string
                  - type: Component class name
                  - state: Component state as string
                  - parameters: Dict of parameter names to JSON data

        Examples:
            >>> data = component.serialize()
            >>> json.dumps(data)  # Can be saved to file
        """
        return {
            "id": self._id,
            "type": self.__class__.__name__,
            "state": self._state.name,
            "parameters": {
                name: param.to_json()
                for name, param in self._parameters.items()
            }
        }

    def deserialize(self, data: dict) -> None:
        """Deserialize component state from a dictionary.

        Restores component state from a previously serialized dictionary. This
        includes ID and parameter values, but not pin connections (which are
        managed at the graph level).

        Args:
            data: Dictionary produced by serialize()

        Raises:
            KeyError: If required keys are missing from data
            ValueError: If state name is invalid

        Examples:
            >>> component = MyComponent()
            >>> component.deserialize(saved_data)
        """
        if "id" not in data:
            raise KeyError("Missing 'id' in serialized data")

        self._id = data["id"]

        if "state" in data:
            state_name = data["state"]
            try:
                self._state = ComponentState[state_name]
            except KeyError:
                raise ValueError(f"Invalid component state: {state_name}")

        if "parameters" in data:
            params_data = data["parameters"]
            for param_name, param_json in params_data.items():
                param = self._parameters.get(param_name)
                if param is not None:
                    try:
                        param.from_json(param_json)
                    except Exception as e:
                        print(f"Error deserializing parameter '{param_name}': {e}")

    def __repr__(self) -> str:
        """Return string representation of this component.

        Returns:
            str: Representation showing class name, ID, and state
        """
        return (f"{self.__class__.__name__}("
                f"id={self._id[:8]}..., "
                f"state={self._state.name}, "
                f"inputs={len(self._input_pins)}, "
                f"outputs={len(self._output_pins)})")
