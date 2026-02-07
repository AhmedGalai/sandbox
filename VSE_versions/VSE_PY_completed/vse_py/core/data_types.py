"""Data type definitions and variants for VSE_PY

This module provides the core data typing system for VSE_PY, including:
- DataType enum for pin type definitions
- Type conversion and compatibility checking functions
- DataVariant class for type-safe value storage and conversion
"""

from enum import Enum, auto
from typing import Any, Optional, Dict, Union
import json


class DataType(Enum):
    """Pin data type enumeration.

    Defines all supported data types for VSE_PY pins and connections.

    Attributes:
        NULL: Represents no value or undefined state
        BOOLEAN: Boolean value (True/False)
        INTEGER: 32/64-bit signed integer
        FLOAT: Single or double precision floating-point number
        STRING: Unicode text string
        JSON: JSON-serializable object (dict, list, etc.)
        ANY: Wildcard type that matches any other type
    """
    NULL = auto()
    BOOLEAN = auto()
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    JSON = auto()
    ANY = auto()


def data_type_to_string(dtype: DataType) -> str:
    """Convert DataType enum to its string representation.

    Args:
        dtype: The DataType enum value to convert.

    Returns:
        Lowercase string representation of the data type name.

    Examples:
        >>> data_type_to_string(DataType.INTEGER)
        'integer'
        >>> data_type_to_string(DataType.BOOLEAN)
        'boolean'
    """
    return dtype.name.lower()


def string_to_data_type(s: str) -> DataType:
    """Convert string to DataType enum.

    Args:
        s: String representation of the data type (case-insensitive).

    Returns:
        The corresponding DataType enum value.

    Raises:
        KeyError: If the string does not match any DataType name.

    Examples:
        >>> string_to_data_type('integer')
        <DataType.INTEGER: 3>
        >>> string_to_data_type('FLOAT')
        <DataType.FLOAT: 4>
    """
    return DataType[s.upper()]


def is_type_compatible(source: DataType, dest: DataType) -> bool:
    """Check if a source data type can connect to a destination data type.

    Type compatibility rules:
    - DataType.ANY is compatible with any type (both as source and destination)
    - Identical types are compatible
    - All other combinations are incompatible

    Args:
        source: The source pin's data type.
        dest: The destination pin's data type.

    Returns:
        True if the source can connect to the destination, False otherwise.

    Examples:
        >>> is_type_compatible(DataType.INTEGER, DataType.INTEGER)
        True
        >>> is_type_compatible(DataType.INTEGER, DataType.ANY)
        True
        >>> is_type_compatible(DataType.ANY, DataType.STRING)
        True
        >>> is_type_compatible(DataType.INTEGER, DataType.STRING)
        False
    """
    if dest == DataType.ANY:
        return True
    if source == DataType.ANY:
        return True
    return source == dest


class DataVariant:
    """Type-safe data container for pin values.

    DataVariant wraps values with their associated data type information,
    providing type inference, validation, and conversion methods. It supports
    conversion between compatible types and JSON serialization.

    Attributes:
        value: The wrapped value.
        dtype: The DataType of the value.

    Examples:
        >>> # Create from value with automatic type inference
        >>> v1 = DataVariant(42)
        >>> v1.dtype
        <DataType.INTEGER: 3>
        >>> v1.to_string()
        '42'

        >>> # Create with explicit type
        >>> v2 = DataVariant("3.14", DataType.STRING)
        >>> v2.to_float()
        3.14

        >>> # JSON serialization
        >>> v3 = DataVariant([1, 2, 3])
        >>> json_str = v3.to_json()
        >>> v4 = DataVariant.from_json(json_str)
    """

    def __init__(self, value: Any, dtype: Optional[DataType] = None) -> None:
        """Initialize a DataVariant.

        Args:
            value: The value to wrap. If dtype is not provided, the type will
                   be inferred from the Python type of the value.
            dtype: Optional explicit DataType. If provided, it overrides type
                   inference. If not provided, the type is automatically inferred.

        Examples:
            >>> v1 = DataVariant(True)  # Automatic type inference
            >>> v2 = DataVariant("123", DataType.STRING)  # Explicit type
        """
        self._value = value

        if dtype is not None:
            self._dtype = dtype
        else:
            self._dtype = self._infer_type(value)

    @staticmethod
    def _infer_type(value: Any) -> DataType:
        """Infer the DataType from a Python value.

        Type inference mapping:
        - None -> DataType.NULL
        - bool -> DataType.BOOLEAN
        - int -> DataType.INTEGER
        - float -> DataType.FLOAT
        - str -> DataType.STRING
        - dict, list, tuple -> DataType.JSON
        - other -> DataType.JSON

        Args:
            value: The Python value to infer type from.

        Returns:
            The inferred DataType.
        """
        if value is None:
            return DataType.NULL
        elif isinstance(value, bool):
            # Check bool before int, as bool is a subclass of int in Python
            return DataType.BOOLEAN
        elif isinstance(value, int):
            return DataType.INTEGER
        elif isinstance(value, float):
            return DataType.FLOAT
        elif isinstance(value, str):
            return DataType.STRING
        elif isinstance(value, (dict, list, tuple)):
            return DataType.JSON
        else:
            # Default to JSON for other types (objects, custom classes, etc.)
            return DataType.JSON

    @property
    def value(self) -> Any:
        """Get the wrapped value.

        Returns:
            The underlying value stored in this variant.
        """
        return self._value

    @property
    def dtype(self) -> DataType:
        """Get the data type of this variant.

        Returns:
            The DataType of the wrapped value.
        """
        return self._dtype

    def to_bool(self) -> bool:
        """Convert the value to a boolean.

        Conversion rules:
        - NULL, False, 0, 0.0, empty string -> False
        - True, non-zero numbers, non-empty strings -> True
        - JSON objects/arrays -> True if non-empty

        Returns:
            The boolean representation of the value.

        Raises:
            ValueError: If the conversion is not possible or not meaningful.

        Examples:
            >>> DataVariant(1).to_bool()
            True
            >>> DataVariant("").to_bool()
            False
            >>> DataVariant("hello").to_bool()
            True
        """
        if self._value is None:
            return False
        elif isinstance(self._value, bool):
            return self._value
        elif isinstance(self._value, (int, float)):
            return bool(self._value)
        elif isinstance(self._value, str):
            return len(self._value) > 0
        elif isinstance(self._value, (dict, list, tuple)):
            return len(self._value) > 0
        else:
            return bool(self._value)

    def to_int(self) -> int:
        """Convert the value to an integer.

        Conversion rules:
        - NULL -> 0
        - Boolean -> 1 (True) or 0 (False)
        - Integer -> unchanged
        - Float -> truncated to integer
        - String -> parsed as integer (raises ValueError if not numeric)
        - JSON -> not supported (raises ValueError)

        Returns:
            The integer representation of the value.

        Raises:
            ValueError: If the value cannot be converted to an integer.

        Examples:
            >>> DataVariant(3.7).to_int()
            3
            >>> DataVariant("42").to_int()
            42
            >>> DataVariant(True).to_int()
            1
        """
        if self._value is None:
            return 0
        elif isinstance(self._value, bool):
            return 1 if self._value else 0
        elif isinstance(self._value, int):
            return self._value
        elif isinstance(self._value, float):
            return int(self._value)
        elif isinstance(self._value, str):
            try:
                # Try parsing as float first to handle "3.14" style strings
                return int(float(self._value))
            except ValueError:
                raise ValueError(
                    f"Cannot convert string '{self._value}' to integer"
                )
        elif isinstance(self._value, (dict, list, tuple)):
            raise ValueError(
                f"Cannot convert {type(self._value).__name__} to integer"
            )
        else:
            raise ValueError(
                f"Cannot convert {type(self._value).__name__} to integer"
            )

    def to_float(self) -> float:
        """Convert the value to a float.

        Conversion rules:
        - NULL -> 0.0
        - Boolean -> 1.0 (True) or 0.0 (False)
        - Integer -> converted to float
        - Float -> unchanged
        - String -> parsed as float (raises ValueError if not numeric)
        - JSON -> not supported (raises ValueError)

        Returns:
            The float representation of the value.

        Raises:
            ValueError: If the value cannot be converted to a float.

        Examples:
            >>> DataVariant(42).to_float()
            42.0
            >>> DataVariant("3.14").to_float()
            3.14
            >>> DataVariant(False).to_float()
            0.0
        """
        if self._value is None:
            return 0.0
        elif isinstance(self._value, bool):
            return 1.0 if self._value else 0.0
        elif isinstance(self._value, (int, float)):
            return float(self._value)
        elif isinstance(self._value, str):
            try:
                return float(self._value)
            except ValueError:
                raise ValueError(
                    f"Cannot convert string '{self._value}' to float"
                )
        elif isinstance(self._value, (dict, list, tuple)):
            raise ValueError(
                f"Cannot convert {type(self._value).__name__} to float"
            )
        else:
            raise ValueError(
                f"Cannot convert {type(self._value).__name__} to float"
            )

    def to_string(self) -> str:
        """Convert the value to a string.

        Conversion rules:
        - NULL -> "null"
        - Boolean -> "true" or "false"
        - Integer -> decimal string representation
        - Float -> decimal string representation
        - String -> unchanged
        - JSON -> JSON serialized string

        Returns:
            The string representation of the value.

        Examples:
            >>> DataVariant(42).to_string()
            '42'
            >>> DataVariant(True).to_string()
            'true'
            >>> DataVariant([1, 2, 3]).to_string()
            '[1, 2, 3]'
        """
        if self._value is None:
            return "null"
        elif isinstance(self._value, bool):
            return "true" if self._value else "false"
        elif isinstance(self._value, (int, float)):
            return str(self._value)
        elif isinstance(self._value, str):
            return self._value
        elif isinstance(self._value, (dict, list, tuple)):
            return json.dumps(self._value)
        else:
            return str(self._value)

    def to_json(self) -> str:
        """Serialize the DataVariant to a JSON string.

        The JSON structure contains both the value and its type information:
        {
            "value": <the_value>,
            "type": "<type_name>"
        }

        Returns:
            A JSON string representation of this DataVariant.

        Raises:
            TypeError: If the value contains non-JSON-serializable objects.

        Examples:
            >>> v = DataVariant(42, DataType.INTEGER)
            >>> v.to_json()
            '{"value": 42, "type": "integer"}'

            >>> v = DataVariant([1, 2, 3])
            >>> v.to_json()
            '{"value": [1, 2, 3], "type": "json"}'
        """
        try:
            data = {
                "value": self._value,
                "type": data_type_to_string(self._dtype)
            }
            return json.dumps(data)
        except TypeError as e:
            raise TypeError(
                f"Cannot serialize DataVariant value to JSON: {e}"
            )

    @classmethod
    def from_json(cls, json_str: str) -> "DataVariant":
        """Deserialize a DataVariant from a JSON string.

        The JSON string must contain a "value" and "type" field.
        The type information is used to properly interpret the value.

        Args:
            json_str: A JSON string produced by to_json().

        Returns:
            A new DataVariant instance with the deserialized value and type.

        Raises:
            json.JSONDecodeError: If the JSON string is invalid.
            KeyError: If required fields are missing from the JSON.
            ValueError: If the type name is not a valid DataType.

        Examples:
            >>> json_str = '{"value": 42, "type": "integer"}'
            >>> v = DataVariant.from_json(json_str)
            >>> v.value
            42
            >>> v.dtype
            <DataType.INTEGER: 3>
        """
        try:
            data = json.loads(json_str)
            value = data["value"]
            dtype = string_to_data_type(data["type"])
            return cls(value, dtype)
        except KeyError as e:
            raise KeyError(
                f"Missing required field in JSON: {e}"
            )
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON format: {e.msg}",
                e.doc,
                e.pos
            )

    def __repr__(self) -> str:
        """Return a detailed string representation of this DataVariant.

        Returns:
            A string representation showing the value and type.

        Examples:
            >>> repr(DataVariant(42))
            'DataVariant(value=42, dtype=<DataType.INTEGER: 3>)'
        """
        return f"DataVariant(value={self._value!r}, dtype={self._dtype})"

    def __str__(self) -> str:
        """Return a user-friendly string representation.

        Returns:
            The string representation of the value.
        """
        return self.to_string()

    def __eq__(self, other: Any) -> bool:
        """Check equality with another DataVariant or value.

        Args:
            other: Another DataVariant or a raw value.

        Returns:
            True if values and types match (for DataVariant comparison),
            or if raw values match (for raw value comparison).

        Examples:
            >>> DataVariant(42) == DataVariant(42)
            True
            >>> DataVariant(42, DataType.INTEGER) == DataVariant(42, DataType.STRING)
            False
            >>> DataVariant(42) == 42
            True
        """
        if isinstance(other, DataVariant):
            return self._value == other._value and self._dtype == other._dtype
        else:
            return self._value == other

    def __hash__(self) -> int:
        """Return hash of this DataVariant.

        This allows DataVariant instances to be used as dictionary keys
        or in sets. Note: only hashable values are supported.

        Returns:
            Hash of the (value, dtype) tuple.

        Raises:
            TypeError: If the value is not hashable.
        """
        try:
            return hash((self._value, self._dtype))
        except TypeError:
            raise TypeError(
                f"unhashable type: '{type(self._value).__name__}'"
            )
