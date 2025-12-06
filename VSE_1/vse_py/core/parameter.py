"""Parameter hierarchy for component configuration

This module implements the parameter system for VSE_PY components. Parameters allow
user configuration of component behavior through a type-safe interface with JSON
serialization support.

Classes:
    Parameter: Abstract base class for all parameter types
    IntParameter: Integer parameter with min/max validation
    FloatParameter: Float parameter with min/max validation
    StringParameter: String parameter with optional default
    BoolParameter: Boolean parameter

Each parameter type provides:
    - Type-safe value storage and retrieval
    - Full validation and range constraints
    - Complete JSON serialization/deserialization
    - Pythonic property-based API
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Union


class Parameter(ABC):
    """Abstract base class for component parameters.

    Parameters are configuration values that control component behavior.
    Each parameter has a name, description, and a type-specific value.

    All parameters support JSON serialization for saving and loading.

    Attributes:
        name: Unique identifier for the parameter
        description: Human-readable description of the parameter's purpose
    """

    def __init__(self, name: str, description: str = "") -> None:
        """Initialize a parameter.

        Args:
            name: Parameter identifier (must be unique within a component)
            description: Optional description of the parameter's purpose

        Raises:
            ValueError: If name is empty or contains invalid characters
        """
        if not name or not isinstance(name, str):
            raise ValueError("Parameter name must be a non-empty string")

        self._name: str = name
        self._description: str = description

    @property
    def name(self) -> str:
        """Get the parameter name."""
        return self._name

    @property
    def description(self) -> str:
        """Get the parameter description."""
        return self._description

    @abstractmethod
    def get_value(self) -> Any:
        """Get the current parameter value.

        Returns:
            The current value with the appropriate type
        """
        pass

    @abstractmethod
    def set_value(self, value: Any) -> None:
        """Set the parameter value with validation.

        Args:
            value: New value for the parameter. Type conversion is attempted
                   if the value is not already of the correct type.

        Raises:
            TypeError: If value cannot be converted to the appropriate type
            ValueError: If value fails validation (e.g., outside min/max range)
        """
        pass

    @abstractmethod
    def to_json(self) -> dict:
        """Serialize parameter to JSON-compatible dictionary.

        Returns:
            Dictionary containing all parameter state needed for serialization.
            Must include "type" and "name" keys.
        """
        pass

    @abstractmethod
    def from_json(self, data: dict) -> None:
        """Deserialize parameter from JSON dictionary.

        Args:
            data: Dictionary with serialized parameter state

        Raises:
            KeyError: If required keys are missing from data
            ValueError: If data values are invalid for this parameter type
        """
        pass


class IntParameter(Parameter):
    """Integer parameter with optional min/max validation.

    Stores a 32-bit signed integer value with optional range constraints.
    Values outside the range are clamped to valid bounds.

    Attributes:
        min_value: Minimum valid value (default: -2^31)
        max_value: Maximum valid value (default: 2^31-1)
    """

    def __init__(
        self,
        name: str,
        default: int = 0,
        min_val: int = -2**31,
        max_val: int = 2**31 - 1,
        description: str = ""
    ) -> None:
        """Initialize an integer parameter.

        Args:
            name: Parameter identifier
            default: Initial value (will be clamped to min/max)
            min_val: Minimum valid value (inclusive)
            max_val: Maximum valid value (inclusive)
            description: Optional description

        Raises:
            ValueError: If name is empty, min_val > max_val, or default outside range
        """
        super().__init__(name, description)

        if min_val > max_val:
            raise ValueError(f"min_val ({min_val}) cannot exceed max_val ({max_val})")

        self._min: int = min_val
        self._max: int = max_val
        # Clamp default to valid range
        self._value: int = max(self._min, min(self._max, int(default)))

    @property
    def min_value(self) -> int:
        """Get the minimum valid value."""
        return self._min

    @property
    def max_value(self) -> int:
        """Get the maximum valid value."""
        return self._max

    def get_value(self) -> int:
        """Get the current integer value."""
        return self._value

    def set_value(self, value: Any) -> None:
        """Set the integer value with range clamping.

        Args:
            value: Value to set. Will be converted to int if possible.
                   Values outside min/max range are clamped to boundaries.

        Raises:
            TypeError: If value cannot be converted to int
            ValueError: If value is NaN or infinite (for numeric types)
        """
        try:
            # Handle float -> int conversion with special cases
            if isinstance(value, float):
                if not (-float('inf') < value < float('inf')):
                    raise ValueError(f"Cannot convert infinite value to int: {value}")
                int_val = int(value)
            else:
                int_val = int(value)

            # Clamp to valid range
            self._value = max(self._min, min(self._max, int_val))
        except (TypeError, ValueError) as e:
            if "cannot convert" not in str(e).lower():
                raise TypeError(f"Cannot convert {type(value).__name__} to int: {value}") from e
            raise

    def to_json(self) -> dict:
        """Serialize to JSON dictionary.

        Returns:
            Dictionary with keys: type, name, value, min, max, description
        """
        return {
            "type": "int",
            "name": self._name,
            "value": self._value,
            "min": self._min,
            "max": self._max,
            "description": self._description
        }

    def from_json(self, data: dict) -> None:
        """Deserialize from JSON dictionary.

        Args:
            data: Dictionary with keys: value, min, max

        Raises:
            KeyError: If required keys are missing
            ValueError: If values are invalid
        """
        if "value" not in data:
            raise KeyError("Missing 'value' key in JSON data")

        self._value = data["value"]
        self._min = data.get("min", self._min)
        self._max = data.get("max", self._max)

        # Validate loaded data
        if self._min > self._max:
            raise ValueError(f"Loaded min ({self._min}) exceeds max ({self._max})")
        if not (self._min <= self._value <= self._max):
            # Clamp loaded value to new range
            self._value = max(self._min, min(self._max, self._value))


class FloatParameter(Parameter):
    """Float parameter with optional min/max validation.

    Stores a double-precision floating point value with optional range constraints.
    Values outside the range are clamped to valid bounds.

    Attributes:
        min_value: Minimum valid value (default: -1e308)
        max_value: Maximum valid value (default: 1e308)
    """

    def __init__(
        self,
        name: str,
        default: float = 0.0,
        min_val: float = -1e308,
        max_val: float = 1e308,
        description: str = ""
    ) -> None:
        """Initialize a float parameter.

        Args:
            name: Parameter identifier
            default: Initial value (will be clamped to min/max)
            min_val: Minimum valid value (inclusive)
            max_val: Maximum valid value (inclusive)
            description: Optional description

        Raises:
            ValueError: If name is empty, min_val > max_val, or default invalid
        """
        super().__init__(name, description)

        if min_val > max_val:
            raise ValueError(f"min_val ({min_val}) cannot exceed max_val ({max_val})")

        self._min: float = float(min_val)
        self._max: float = float(max_val)
        # Clamp default to valid range
        self._value: float = max(self._min, min(self._max, float(default)))

    @property
    def min_value(self) -> float:
        """Get the minimum valid value."""
        return self._min

    @property
    def max_value(self) -> float:
        """Get the maximum valid value."""
        return self._max

    def get_value(self) -> float:
        """Get the current float value."""
        return self._value

    def set_value(self, value: Any) -> None:
        """Set the float value with range clamping.

        Args:
            value: Value to set. Will be converted to float if possible.
                   Values outside min/max range are clamped to boundaries.

        Raises:
            TypeError: If value cannot be converted to float
            ValueError: If value is NaN (NaN is not allowed)
        """
        try:
            float_val = float(value)

            # Reject NaN values
            if float_val != float_val:  # NaN check (NaN != NaN)
                raise ValueError(f"NaN values are not allowed: {value}")

            # Clamp to valid range
            self._value = max(self._min, min(self._max, float_val))
        except (TypeError, ValueError) as e:
            if "NaN" in str(e):
                raise
            raise TypeError(f"Cannot convert {type(value).__name__} to float: {value}") from e

    def to_json(self) -> dict:
        """Serialize to JSON dictionary.

        Returns:
            Dictionary with keys: type, name, value, min, max, description
        """
        return {
            "type": "float",
            "name": self._name,
            "value": self._value,
            "min": self._min,
            "max": self._max,
            "description": self._description
        }

    def from_json(self, data: dict) -> None:
        """Deserialize from JSON dictionary.

        Args:
            data: Dictionary with keys: value, min, max

        Raises:
            KeyError: If required keys are missing
            ValueError: If values are invalid (NaN or min > max)
        """
        if "value" not in data:
            raise KeyError("Missing 'value' key in JSON data")

        self._value = data["value"]
        self._min = data.get("min", self._min)
        self._max = data.get("max", self._max)

        # Validate loaded data
        if self._min > self._max:
            raise ValueError(f"Loaded min ({self._min}) exceeds max ({self._max})")

        # Check for NaN
        if self._value != self._value:  # NaN check
            raise ValueError("Cannot load NaN value")

        if not (self._min <= self._value <= self._max):
            # Clamp loaded value to new range
            self._value = max(self._min, min(self._max, self._value))


class StringParameter(Parameter):
    """String parameter with optional default value.

    Stores a string value. No validation is performed beyond type checking.
    Empty strings are allowed.
    """

    def __init__(
        self,
        name: str,
        default: str = "",
        description: str = ""
    ) -> None:
        """Initialize a string parameter.

        Args:
            name: Parameter identifier
            default: Initial string value
            description: Optional description

        Raises:
            ValueError: If name is empty
            TypeError: If default is not a string
        """
        super().__init__(name, description)

        if not isinstance(default, str):
            raise TypeError(f"default must be a string, got {type(default).__name__}")

        self._value: str = default

    def get_value(self) -> str:
        """Get the current string value."""
        return self._value

    def set_value(self, value: Any) -> None:
        """Set the string value.

        Args:
            value: Value to set. Will be converted to string if necessary.

        Raises:
            TypeError: Only if value is None and that's not desired
        """
        if value is None:
            self._value = ""
        else:
            self._value = str(value)

    def to_json(self) -> dict:
        """Serialize to JSON dictionary.

        Returns:
            Dictionary with keys: type, name, value, description
        """
        return {
            "type": "string",
            "name": self._name,
            "value": self._value,
            "description": self._description
        }

    def from_json(self, data: dict) -> None:
        """Deserialize from JSON dictionary.

        Args:
            data: Dictionary with key: value

        Raises:
            KeyError: If 'value' key is missing
        """
        if "value" not in data:
            raise KeyError("Missing 'value' key in JSON data")

        self._value = data["value"]

        # Ensure value is string
        if not isinstance(self._value, str):
            self._value = str(self._value)


class BoolParameter(Parameter):
    """Boolean parameter with true/false value.

    Stores a boolean value. Any Python value can be converted to bool.
    """

    def __init__(
        self,
        name: str,
        default: bool = False,
        description: str = ""
    ) -> None:
        """Initialize a boolean parameter.

        Args:
            name: Parameter identifier
            default: Initial boolean value
            description: Optional description

        Raises:
            ValueError: If name is empty
        """
        super().__init__(name, description)
        self._value: bool = bool(default)

    def get_value(self) -> bool:
        """Get the current boolean value."""
        return self._value

    def set_value(self, value: Any) -> None:
        """Set the boolean value.

        Args:
            value: Value to convert to boolean. Python's truthiness rules apply.
                   - 0, 0.0, "", None, [], {} etc. are False
                   - Non-zero numbers, non-empty strings, non-empty collections are True
        """
        self._value = bool(value)

    def to_json(self) -> dict:
        """Serialize to JSON dictionary.

        Returns:
            Dictionary with keys: type, name, value, description
        """
        return {
            "type": "bool",
            "name": self._name,
            "value": self._value,
            "description": self._description
        }

    def from_json(self, data: dict) -> None:
        """Deserialize from JSON dictionary.

        Args:
            data: Dictionary with key: value

        Raises:
            KeyError: If 'value' key is missing
        """
        if "value" not in data:
            raise KeyError("Missing 'value' key in JSON data")

        self._value = bool(data["value"])
