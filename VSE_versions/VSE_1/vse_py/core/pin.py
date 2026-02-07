"""Pin classes for component connections.

This module provides the pin system for VSE_PY, which handles data flow between
components. It includes:
- Pin: Abstract base class for all pin types
- InputPin: Single-connection pin for receiving data
- OutputPin: Multi-connection pin for transmitting data
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable, List
import uuid

from .data_types import DataType, DataVariant, is_type_compatible


class Pin(ABC):
    """Abstract base class for component pins.

    Pins are the connection points for data flow between components. Each pin
    has a unique ID, name, and data type. Pins can be either input (receiving
    data) or output (transmitting data).

    This class should not be instantiated directly; use InputPin or OutputPin
    instead.

    Attributes:
        id: Unique identifier for this pin (UUID-based)
        name: Human-readable name of the pin
        dtype: DataType of data flowing through this pin
    """

    def __init__(self, name: str, dtype: DataType) -> None:
        """Initialize a Pin.

        Args:
            name: Human-readable name for this pin (e.g., "Input A", "Result")
            dtype: DataType specifying what type of data this pin carries

        Raises:
            ValueError: If name is empty
            TypeError: If dtype is not a DataType
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Pin name must be a non-empty string")
        if not isinstance(dtype, DataType):
            raise TypeError("dtype must be a DataType enum value")

        self._id: str = str(uuid.uuid4())
        self._name: str = name
        self._dtype: DataType = dtype

    @property
    def id(self) -> str:
        """Get the unique ID of this pin.

        Returns:
            str: UUID string uniquely identifying this pin
        """
        return self._id

    @property
    def name(self) -> str:
        """Get the name of this pin.

        Returns:
            str: Human-readable name of the pin
        """
        return self._name

    @property
    def dtype(self) -> DataType:
        """Get the data type of this pin.

        Returns:
            DataType: The type of data this pin carries
        """
        return self._dtype

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if this pin has any active connections.

        Returns:
            bool: True if the pin is connected, False otherwise

        Note:
            - For InputPin: True if connected to an OutputPin
            - For OutputPin: True if connected to any InputPins
        """
        pass

    def __repr__(self) -> str:
        """Return string representation of this pin.

        Returns:
            str: Representation showing class name, ID, name, and type
        """
        return (f"{self.__class__.__name__}("
                f"id={self._id[:8]}..., "
                f"name='{self._name}', "
                f"dtype={self._dtype.name})")

    def __eq__(self, other: any) -> bool:
        """Check equality based on pin ID.

        Args:
            other: Another Pin or other object

        Returns:
            bool: True if pins have the same ID
        """
        if isinstance(other, Pin):
            return self._id == other._id
        return False

    def __hash__(self) -> int:
        """Return hash of this pin based on its ID.

        Returns:
            int: Hash of the pin's UUID
        """
        return hash(self._id)


class InputPin(Pin):
    """Input pin that receives data from a single output pin.

    An InputPin can be connected to at most one OutputPin. When the connected
    OutputPin transmits data, the InputPin receives it and optionally triggers
    a callback function. This allows components to react to incoming data.

    Attributes:
        data: Current data value stored in this pin
        callback: Optional callback function invoked when data is received

    Examples:
        >>> pin_in = InputPin("Value", DataType.INTEGER)
        >>> pin_out = OutputPin("Sum", DataType.INTEGER)
        >>> pin_in.connect_to(pin_out)
        True
        >>> pin_out.transmit_data(DataVariant(42))
        >>> pin_in.data.value
        42
    """

    def __init__(self, name: str, dtype: DataType) -> None:
        """Initialize an InputPin.

        Args:
            name: Human-readable name for this input pin
            dtype: DataType of data this pin receives

        Raises:
            ValueError: If name is empty
            TypeError: If dtype is not a DataType
        """
        super().__init__(name, dtype)
        self._connected_pin: Optional[OutputPin] = None
        self._data: DataVariant = DataVariant(None, DataType.NULL)
        self._callback: Optional[Callable[[DataVariant], None]] = None

    def is_connected(self) -> bool:
        """Check if this input pin is connected to an output pin.

        Returns:
            bool: True if connected to an OutputPin, False otherwise
        """
        return self._connected_pin is not None

    def connect_to(self, output_pin: "OutputPin") -> bool:
        """Connect this input pin to an output pin.

        Establishes a connection from the specified output pin to this input pin.
        Type compatibility is checked before connection. This method is typically
        called by the connection manager rather than directly.

        Args:
            output_pin: The OutputPin to connect to

        Returns:
            bool: True if connection succeeded, False if types are incompatible

        Raises:
            TypeError: If output_pin is not an OutputPin
            ValueError: If trying to connect to same pin or creating circular reference

        Examples:
            >>> input_pin = InputPin("Result", DataType.INTEGER)
            >>> output_pin = OutputPin("Sum", DataType.INTEGER)
            >>> input_pin.connect_to(output_pin)
            True
            >>> input_pin.is_connected()
            True

            >>> # Type mismatch
            >>> input_pin2 = InputPin("Flag", DataType.BOOLEAN)
            >>> input_pin2.connect_to(output_pin)
            False
        """
        if not isinstance(output_pin, OutputPin):
            raise TypeError("output_pin must be an OutputPin instance")

        # Check type compatibility
        if not is_type_compatible(output_pin.dtype, self._dtype):
            return False

        # Check for self-connection
        if output_pin is self:
            raise ValueError("Cannot connect a pin to itself")

        self._connected_pin = output_pin
        # Also register on the output pin's side to maintain bidirectional connection
        if self not in output_pin._connected_pins:
            output_pin._connected_pins.append(self)
        return True

    def disconnect(self) -> None:
        """Disconnect this input pin from its connected output pin.

        After disconnection, this pin will no longer receive data from the
        previously connected output pin. The data value is retained but will
        no longer be updated.

        Examples:
            >>> input_pin = InputPin("Value", DataType.FLOAT)
            >>> output_pin = OutputPin("Result", DataType.FLOAT)
            >>> input_pin.connect_to(output_pin)
            True
            >>> input_pin.disconnect()
            >>> input_pin.is_connected()
            False
        """
        if self._connected_pin is not None:
            # Remove from output pin's connected list
            if self in self._connected_pin._connected_pins:
                self._connected_pin._connected_pins.remove(self)
        self._connected_pin = None

    def receive_data(self, data: DataVariant) -> None:
        """Receive data on this pin.

        This method is called by the connected OutputPin when transmitting data.
        The data is stored and any registered callback is invoked.

        Args:
            data: The DataVariant to receive

        Raises:
            TypeError: If data is not a DataVariant

        Examples:
            >>> pin = InputPin("Voltage", DataType.FLOAT)
            >>> pin.receive_data(DataVariant(5.0))
            >>> pin.data.value
            5.0
        """
        if not isinstance(data, DataVariant):
            raise TypeError("data must be a DataVariant instance")

        self._data = data

        # Invoke callback if registered
        if self._callback is not None:
            try:
                self._callback(data)
            except Exception as e:
                # Log callback errors but don't propagate them
                print(f"Error in InputPin callback for '{self._name}': {e}")

    @property
    def data(self) -> DataVariant:
        """Get the current data value on this pin.

        Returns:
            DataVariant: The most recent data received on this pin,
                        or a NULL DataVariant if no data has been received

        Examples:
            >>> pin = InputPin("Count", DataType.INTEGER)
            >>> pin.receive_data(DataVariant(10))
            >>> pin.data.value
            10
            >>> pin.data.dtype
            <DataType.INTEGER: 3>
        """
        return self._data

    def set_callback(self, callback: Optional[Callable[[DataVariant], None]]) -> None:
        """Set or clear the data reception callback.

        When a callback is registered, it will be invoked whenever this pin
        receives data. Pass None to clear the callback.

        Args:
            callback: Function taking a DataVariant and returning None,
                     or None to clear the callback

        Raises:
            TypeError: If callback is not callable or None

        Examples:
            >>> def on_data(data):
            ...     print(f"Received: {data.value}")
            >>> pin = InputPin("Value", DataType.INTEGER)
            >>> pin.set_callback(on_data)
            >>> pin.receive_data(DataVariant(42))
            Received: 42
        """
        if callback is not None and not callable(callback):
            raise TypeError("callback must be callable or None")
        self._callback = callback

    def clear_callback(self) -> None:
        """Clear the data reception callback.

        Examples:
            >>> pin = InputPin("Value", DataType.INTEGER)
            >>> pin.set_callback(lambda x: print(x))
            >>> pin.clear_callback()
        """
        self._callback = None

    def has_data(self) -> bool:
        """Check if this pin has received data.

        Returns:
            bool: True if data has been received (dtype is not NULL)

        Examples:
            >>> pin = InputPin("Value", DataType.INTEGER)
            >>> pin.has_data()
            False
            >>> pin.receive_data(DataVariant(42))
            >>> pin.has_data()
            True
        """
        return self._data.dtype != DataType.NULL

    @property
    def status(self):
        """Get the connection status of this pin.

        Returns:
            str: Connection status as an enum-like object
        """
        class PinStatus:
            def __init__(self, connected):
                self.name = "CONNECTED" if connected else "DISCONNECTED"

        return PinStatus(self.is_connected())

    def __repr__(self) -> str:
        """Return string representation of this input pin.

        Returns:
            str: Representation showing connection status
        """
        status = "connected" if self.is_connected() else "disconnected"
        return (f"InputPin("
                f"id={self._id[:8]}..., "
                f"name='{self._name}', "
                f"dtype={self._dtype.name}, "
                f"status={status})")


class OutputPin(Pin):
    """Output pin that transmits data to multiple input pins.

    An OutputPin can be connected to multiple InputPins. When transmit_data()
    is called, the data is broadcast to all connected InputPins. This supports
    one-to-many data distribution patterns.

    Attributes:
        data: Current data value stored in this pin
        connected_pins: List of connected InputPins (read-only copy)

    Examples:
        >>> out_pin = OutputPin("Result", DataType.FLOAT)
        >>> in_pin1 = InputPin("Display", DataType.FLOAT)
        >>> in_pin2 = InputPin("Logger", DataType.FLOAT)
        >>> out_pin.add_connection(in_pin1)
        True
        >>> out_pin.add_connection(in_pin2)
        True
        >>> out_pin.transmit_data(DataVariant(3.14))
        >>> in_pin1.data.value
        3.14
        >>> in_pin2.data.value
        3.14
    """

    def __init__(self, name: str, dtype: DataType) -> None:
        """Initialize an OutputPin.

        Args:
            name: Human-readable name for this output pin
            dtype: DataType of data this pin transmits

        Raises:
            ValueError: If name is empty
            TypeError: If dtype is not a DataType
        """
        super().__init__(name, dtype)
        self._connected_pins: List[InputPin] = []
        self._data: DataVariant = DataVariant(None, DataType.NULL)

    def is_connected(self) -> bool:
        """Check if this output pin is connected to any input pins.

        Returns:
            bool: True if at least one InputPin is connected, False otherwise
        """
        return len(self._connected_pins) > 0

    def add_connection(self, input_pin: InputPin) -> bool:
        """Add a connection to an input pin.

        Creates a unidirectional data flow from this output pin to the specified
        input pin. Type compatibility is checked before connection. If the input
        pin is already connected to this output, no duplicate is added.

        Args:
            input_pin: The InputPin to connect to

        Returns:
            bool: True if connection succeeded, False if types are incompatible

        Raises:
            TypeError: If input_pin is not an InputPin
            ValueError: If trying to connect to same pin

        Examples:
            >>> out_pin = OutputPin("Sum", DataType.INTEGER)
            >>> in_pin = InputPin("Display", DataType.INTEGER)
            >>> out_pin.add_connection(in_pin)
            True
            >>> out_pin.is_connected()
            True

            >>> # Type mismatch
            >>> in_pin2 = InputPin("Flag", DataType.BOOLEAN)
            >>> out_pin.add_connection(in_pin2)
            False
        """
        if not isinstance(input_pin, InputPin):
            raise TypeError("input_pin must be an InputPin instance")

        # Check type compatibility
        if not is_type_compatible(self._dtype, input_pin.dtype):
            return False

        # Check for self-connection
        if input_pin is self:
            raise ValueError("Cannot connect a pin to itself")

        # Avoid duplicate connections
        if input_pin not in self._connected_pins:
            self._connected_pins.append(input_pin)

        return True

    def remove_connection(self, input_pin: InputPin) -> None:
        """Remove a connection to an input pin.

        If the input pin is not in the connections list, this method does nothing
        (no error is raised).

        Args:
            input_pin: The InputPin to disconnect from

        Examples:
            >>> out_pin = OutputPin("Value", DataType.FLOAT)
            >>> in_pin = InputPin("Display", DataType.FLOAT)
            >>> out_pin.add_connection(in_pin)
            True
            >>> out_pin.remove_connection(in_pin)
            >>> out_pin.is_connected()
            False
        """
        if input_pin in self._connected_pins:
            self._connected_pins.remove(input_pin)

    def disconnect_all(self) -> None:
        """Disconnect all input pins from this output pin.

        Clears all connections, effectively stopping data distribution to any
        connected inputs.

        Examples:
            >>> out_pin = OutputPin("Data", DataType.STRING)
            >>> in_pin1 = InputPin("A", DataType.STRING)
            >>> in_pin2 = InputPin("B", DataType.STRING)
            >>> out_pin.add_connection(in_pin1)
            True
            >>> out_pin.add_connection(in_pin2)
            True
            >>> out_pin.is_connected()
            True
            >>> out_pin.disconnect_all()
            >>> out_pin.is_connected()
            False
        """
        self._connected_pins.clear()

    def connect_to_topic(self, topic_name: str) -> None:
        """Connect this output pin to a topic for pub/sub communication.

        When this output pin transmits data, it will also publish to the topic.
        This enables topic-based data distribution in addition to direct pin connections.

        Args:
            topic_name: Name of the topic to publish to

        Examples:
            >>> from .topic_registry import TopicRegistry
            >>> registry = TopicRegistry.instance()
            >>> registry.create_topic("sensor_data", DataType.FLOAT)
            True
            >>> out_pin = OutputPin("Sensor", DataType.FLOAT)
            >>> out_pin.connect_to_topic("sensor_data")
        """
        # Store topic name for publishing
        if not hasattr(self, '_topics'):
            self._topics = []
        if topic_name not in self._topics:
            self._topics.append(topic_name)

    def transmit_data(self, data: DataVariant) -> None:
        """Transmit data to all connected input pins.

        Broadcasts the data to all connected InputPins, triggering their
        receive_data() methods and any associated callbacks. The data is
        stored in this pin and is available via the data property.

        If connected to topics, also publishes to those topics.

        Args:
            data: The DataVariant to transmit

        Raises:
            TypeError: If data is not a DataVariant

        Examples:
            >>> out_pin = OutputPin("Sum", DataType.INTEGER)
            >>> in_pin = InputPin("Result", DataType.INTEGER)
            >>> out_pin.add_connection(in_pin)
            True
            >>> out_pin.transmit_data(DataVariant(100))
            >>> out_pin.data.value
            100
            >>> in_pin.data.value
            100
        """
        if not isinstance(data, DataVariant):
            raise TypeError("data must be a DataVariant instance")

        # Store data in this pin
        self._data = data

        # Broadcast to all connected input pins
        for pin in self._connected_pins:
            pin.receive_data(data)

        # Publish to topics if connected
        if hasattr(self, '_topics'):
            from .topic_registry import TopicRegistry
            registry = TopicRegistry.instance()
            for topic_name in self._topics:
                registry.publish(topic_name, data)

    @property
    def data(self) -> DataVariant:
        """Get the current data value on this pin.

        Returns:
            DataVariant: The most recently transmitted data on this pin,
                        or a NULL DataVariant if no data has been transmitted

        Examples:
            >>> pin = OutputPin("Count", DataType.INTEGER)
            >>> pin.transmit_data(DataVariant(5))
            >>> pin.data.value
            5
            >>> pin.data.dtype
            <DataType.INTEGER: 3>
        """
        return self._data

    @property
    def connected_pins(self) -> List[InputPin]:
        """Get a copy of the list of connected input pins.

        Returns a copy to prevent external modification of the internal
        connections list.

        Returns:
            List[InputPin]: Copy of the list of connected InputPins

        Examples:
            >>> out_pin = OutputPin("Data", DataType.STRING)
            >>> in_pin1 = InputPin("A", DataType.STRING)
            >>> in_pin2 = InputPin("B", DataType.STRING)
            >>> out_pin.add_connection(in_pin1)
            True
            >>> out_pin.add_connection(in_pin2)
            True
            >>> len(out_pin.connected_pins)
            2
        """
        return self._connected_pins.copy()

    def __repr__(self) -> str:
        """Return string representation of this output pin.

        Returns:
            str: Representation showing connection count
        """
        return (f"OutputPin("
                f"id={self._id[:8]}..., "
                f"name='{self._name}', "
                f"dtype={self._dtype.name}, "
                f"connections={len(self._connected_pins)})")
