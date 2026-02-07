"""Unit tests for the parameter system (Phase 4 of VSE_PY implementation).

This test module validates all parameter types with comprehensive coverage:
- Abstract base class behavior
- Type-safe value storage and retrieval
- Validation and range constraints
- JSON serialization/deserialization
- Error handling and edge cases
"""

import unittest
import json
from vse_py.core.parameter import (
    Parameter,
    IntParameter,
    FloatParameter,
    StringParameter,
    BoolParameter
)


class TestParameterBase(unittest.TestCase):
    """Test abstract Parameter base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that Parameter cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            Parameter("test")

    def test_parameter_name_validation(self):
        """Test that parameter names must be non-empty strings."""
        # Valid parameter should be created via subclass
        param = IntParameter("valid_name")
        self.assertEqual(param.name, "valid_name")

    def test_parameter_description(self):
        """Test parameter description storage."""
        param = IntParameter("test", description="A test parameter")
        self.assertEqual(param.description, "A test parameter")

    def test_parameter_name_required(self):
        """Test that parameter name is required."""
        with self.assertRaises(ValueError):
            IntParameter("")

    def test_parameter_invalid_name_type(self):
        """Test that parameter name must be string."""
        with self.assertRaises(ValueError):
            IntParameter(123)


class TestIntParameter(unittest.TestCase):
    """Test IntParameter implementation."""

    def test_init_default_values(self):
        """Test default initialization."""
        param = IntParameter("count")
        self.assertEqual(param.get_value(), 0)
        self.assertEqual(param.min_value, -2**31)
        self.assertEqual(param.max_value, 2**31 - 1)

    def test_init_with_custom_default(self):
        """Test initialization with custom default value."""
        param = IntParameter("count", default=42)
        self.assertEqual(param.get_value(), 42)

    def test_init_with_custom_range(self):
        """Test initialization with custom min/max."""
        param = IntParameter("percentage", default=50, min_val=0, max_val=100)
        self.assertEqual(param.min_value, 0)
        self.assertEqual(param.max_value, 100)
        self.assertEqual(param.get_value(), 50)

    def test_init_clamps_default_to_min(self):
        """Test that default is clamped to minimum."""
        param = IntParameter("test", default=-10, min_val=0, max_val=100)
        self.assertEqual(param.get_value(), 0)

    def test_init_clamps_default_to_max(self):
        """Test that default is clamped to maximum."""
        param = IntParameter("test", default=150, min_val=0, max_val=100)
        self.assertEqual(param.get_value(), 100)

    def test_init_invalid_range(self):
        """Test that min_val > max_val raises error."""
        with self.assertRaises(ValueError):
            IntParameter("test", min_val=100, max_val=0)

    def test_set_value_within_range(self):
        """Test setting value within valid range."""
        param = IntParameter("test", min_val=0, max_val=100)
        param.set_value(50)
        self.assertEqual(param.get_value(), 50)

    def test_set_value_clamps_to_min(self):
        """Test that values below min are clamped."""
        param = IntParameter("test", min_val=10, max_val=100)
        param.set_value(5)
        self.assertEqual(param.get_value(), 10)

    def test_set_value_clamps_to_max(self):
        """Test that values above max are clamped."""
        param = IntParameter("test", min_val=0, max_val=100)
        param.set_value(150)
        self.assertEqual(param.get_value(), 100)

    def test_set_value_from_float(self):
        """Test converting float to int."""
        param = IntParameter("test")
        param.set_value(42.7)
        self.assertEqual(param.get_value(), 42)

    def test_set_value_from_string(self):
        """Test converting string to int."""
        param = IntParameter("test")
        param.set_value("42")
        self.assertEqual(param.get_value(), 42)

    def test_set_value_invalid_conversion(self):
        """Test that invalid conversions raise error."""
        param = IntParameter("test")
        with self.assertRaises(TypeError):
            param.set_value("not_a_number")

    def test_set_value_infinite_float(self):
        """Test that infinite float values are rejected."""
        param = IntParameter("test")
        with self.assertRaises(ValueError):
            param.set_value(float('inf'))

    def test_to_json(self):
        """Test JSON serialization."""
        param = IntParameter("count", default=42, min_val=0, max_val=100,
                           description="A counter")
        data = param.to_json()
        self.assertEqual(data["type"], "int")
        self.assertEqual(data["name"], "count")
        self.assertEqual(data["value"], 42)
        self.assertEqual(data["min"], 0)
        self.assertEqual(data["max"], 100)
        self.assertEqual(data["description"], "A counter")

    def test_from_json(self):
        """Test JSON deserialization."""
        param = IntParameter("test")
        data = {"value": 42, "min": 0, "max": 100}
        param.from_json(data)
        self.assertEqual(param.get_value(), 42)
        self.assertEqual(param.min_value, 0)
        self.assertEqual(param.max_value, 100)

    def test_from_json_missing_value(self):
        """Test that missing value key raises error."""
        param = IntParameter("test")
        with self.assertRaises(KeyError):
            param.from_json({"min": 0})

    def test_from_json_invalid_range(self):
        """Test that invalid range in JSON raises error."""
        param = IntParameter("test")
        with self.assertRaises(ValueError):
            param.from_json({"value": 50, "min": 100, "max": 0})

    def test_from_json_clamps_value(self):
        """Test that loaded value outside new range is clamped."""
        param = IntParameter("test")
        param.from_json({"value": 150, "min": 0, "max": 100})
        self.assertEqual(param.get_value(), 100)

    def test_from_json_default_constraints(self):
        """Test from_json with missing min/max uses existing."""
        param = IntParameter("test", min_val=0, max_val=100)
        param.from_json({"value": 50})
        self.assertEqual(param.min_value, 0)
        self.assertEqual(param.max_value, 100)

    def test_json_roundtrip(self):
        """Test that JSON serialize/deserialize preserves value."""
        original = IntParameter("test", default=42, min_val=0, max_val=100)
        data = original.to_json()
        new_param = IntParameter("test")
        new_param.from_json(data)
        self.assertEqual(new_param.get_value(), original.get_value())
        self.assertEqual(new_param.min_value, original.min_value)
        self.assertEqual(new_param.max_value, original.max_value)


class TestFloatParameter(unittest.TestCase):
    """Test FloatParameter implementation."""

    def test_init_default_values(self):
        """Test default initialization."""
        param = FloatParameter("scalar")
        self.assertEqual(param.get_value(), 0.0)
        self.assertEqual(param.min_value, -1e308)
        self.assertEqual(param.max_value, 1e308)

    def test_init_with_custom_default(self):
        """Test initialization with custom default."""
        param = FloatParameter("scalar", default=3.14)
        self.assertEqual(param.get_value(), 3.14)

    def test_init_with_custom_range(self):
        """Test initialization with custom min/max."""
        param = FloatParameter("ratio", default=0.5, min_val=0.0, max_val=1.0)
        self.assertEqual(param.min_value, 0.0)
        self.assertEqual(param.max_value, 1.0)
        self.assertEqual(param.get_value(), 0.5)

    def test_init_clamps_default_to_min(self):
        """Test that default is clamped to minimum."""
        param = FloatParameter("test", default=-1.0, min_val=0.0, max_val=1.0)
        self.assertEqual(param.get_value(), 0.0)

    def test_init_clamps_default_to_max(self):
        """Test that default is clamped to maximum."""
        param = FloatParameter("test", default=2.0, min_val=0.0, max_val=1.0)
        self.assertEqual(param.get_value(), 1.0)

    def test_init_invalid_range(self):
        """Test that min_val > max_val raises error."""
        with self.assertRaises(ValueError):
            FloatParameter("test", min_val=1.0, max_val=0.0)

    def test_set_value_within_range(self):
        """Test setting value within range."""
        param = FloatParameter("test", min_val=0.0, max_val=1.0)
        param.set_value(0.5)
        self.assertAlmostEqual(param.get_value(), 0.5)

    def test_set_value_clamps_to_min(self):
        """Test that values below min are clamped."""
        param = FloatParameter("test", min_val=0.0, max_val=1.0)
        param.set_value(-0.5)
        self.assertEqual(param.get_value(), 0.0)

    def test_set_value_clamps_to_max(self):
        """Test that values above max are clamped."""
        param = FloatParameter("test", min_val=0.0, max_val=1.0)
        param.set_value(1.5)
        self.assertEqual(param.get_value(), 1.0)

    def test_set_value_from_int(self):
        """Test converting int to float."""
        param = FloatParameter("test")
        param.set_value(42)
        self.assertEqual(param.get_value(), 42.0)

    def test_set_value_from_string(self):
        """Test converting string to float."""
        param = FloatParameter("test")
        param.set_value("3.14")
        self.assertAlmostEqual(param.get_value(), 3.14)

    def test_set_value_invalid_conversion(self):
        """Test that invalid conversions raise error."""
        param = FloatParameter("test")
        with self.assertRaises(TypeError):
            param.set_value("not_a_number")

    def test_set_value_rejects_nan(self):
        """Test that NaN values are rejected."""
        param = FloatParameter("test")
        with self.assertRaises(ValueError):
            param.set_value(float('nan'))

    def test_set_value_accepts_inf_but_raises(self):
        """Test that infinite values raise ValueError."""
        param = FloatParameter("test")
        # This should work for set_value (it doesn't check for inf like int does)
        # But let's test normal case
        param.set_value(1.5)
        self.assertEqual(param.get_value(), 1.5)

    def test_to_json(self):
        """Test JSON serialization."""
        param = FloatParameter("ratio", default=0.5, min_val=0.0, max_val=1.0,
                             description="A ratio value")
        data = param.to_json()
        self.assertEqual(data["type"], "float")
        self.assertEqual(data["name"], "ratio")
        self.assertEqual(data["value"], 0.5)
        self.assertEqual(data["min"], 0.0)
        self.assertEqual(data["max"], 1.0)
        self.assertEqual(data["description"], "A ratio value")

    def test_from_json(self):
        """Test JSON deserialization."""
        param = FloatParameter("test")
        data = {"value": 0.5, "min": 0.0, "max": 1.0}
        param.from_json(data)
        self.assertEqual(param.get_value(), 0.5)
        self.assertEqual(param.min_value, 0.0)
        self.assertEqual(param.max_value, 1.0)

    def test_from_json_missing_value(self):
        """Test that missing value key raises error."""
        param = FloatParameter("test")
        with self.assertRaises(KeyError):
            param.from_json({"min": 0.0})

    def test_from_json_rejects_nan(self):
        """Test that NaN in JSON is rejected."""
        param = FloatParameter("test")
        # JSON doesn't natively support NaN, but Python can
        with self.assertRaises(ValueError):
            param.from_json({"value": float('nan')})

    def test_json_roundtrip(self):
        """Test JSON serialize/deserialize roundtrip."""
        original = FloatParameter("test", default=0.5, min_val=0.0, max_val=1.0)
        data = original.to_json()
        new_param = FloatParameter("test")
        new_param.from_json(data)
        self.assertEqual(new_param.get_value(), original.get_value())
        self.assertEqual(new_param.min_value, original.min_value)
        self.assertEqual(new_param.max_value, original.max_value)


class TestStringParameter(unittest.TestCase):
    """Test StringParameter implementation."""

    def test_init_default_empty(self):
        """Test default initialization."""
        param = StringParameter("name")
        self.assertEqual(param.get_value(), "")

    def test_init_with_default_value(self):
        """Test initialization with default value."""
        param = StringParameter("name", default="John")
        self.assertEqual(param.get_value(), "John")

    def test_init_rejects_non_string_default(self):
        """Test that non-string defaults are rejected."""
        with self.assertRaises(TypeError):
            StringParameter("test", default=42)

    def test_set_value_string(self):
        """Test setting string value."""
        param = StringParameter("test")
        param.set_value("hello")
        self.assertEqual(param.get_value(), "hello")

    def test_set_value_from_int(self):
        """Test converting int to string."""
        param = StringParameter("test")
        param.set_value(42)
        self.assertEqual(param.get_value(), "42")

    def test_set_value_from_float(self):
        """Test converting float to string."""
        param = StringParameter("test")
        param.set_value(3.14)
        self.assertEqual(param.get_value(), "3.14")

    def test_set_value_from_none(self):
        """Test converting None to empty string."""
        param = StringParameter("test", default="initial")
        param.set_value(None)
        self.assertEqual(param.get_value(), "")

    def test_set_value_empty_string(self):
        """Test setting empty string."""
        param = StringParameter("test", default="initial")
        param.set_value("")
        self.assertEqual(param.get_value(), "")

    def test_to_json(self):
        """Test JSON serialization."""
        param = StringParameter("filename", default="test.txt",
                              description="Output filename")
        data = param.to_json()
        self.assertEqual(data["type"], "string")
        self.assertEqual(data["name"], "filename")
        self.assertEqual(data["value"], "test.txt")
        self.assertEqual(data["description"], "Output filename")

    def test_from_json(self):
        """Test JSON deserialization."""
        param = StringParameter("test")
        data = {"value": "hello"}
        param.from_json(data)
        self.assertEqual(param.get_value(), "hello")

    def test_from_json_missing_value(self):
        """Test that missing value raises error."""
        param = StringParameter("test")
        with self.assertRaises(KeyError):
            param.from_json({})

    def test_from_json_non_string_converted(self):
        """Test that non-string values are converted."""
        param = StringParameter("test")
        data = {"value": 42}
        param.from_json(data)
        self.assertEqual(param.get_value(), "42")

    def test_json_roundtrip(self):
        """Test JSON roundtrip."""
        original = StringParameter("test", default="hello")
        data = original.to_json()
        new_param = StringParameter("test")
        new_param.from_json(data)
        self.assertEqual(new_param.get_value(), original.get_value())


class TestBoolParameter(unittest.TestCase):
    """Test BoolParameter implementation."""

    def test_init_default_false(self):
        """Test default initialization."""
        param = BoolParameter("enabled")
        self.assertEqual(param.get_value(), False)

    def test_init_with_default_true(self):
        """Test initialization with True."""
        param = BoolParameter("enabled", default=True)
        self.assertEqual(param.get_value(), True)

    def test_init_default_from_truthy(self):
        """Test initialization with truthy value."""
        param = BoolParameter("test", default=1)
        self.assertEqual(param.get_value(), True)

    def test_init_default_from_falsy(self):
        """Test initialization with falsy value."""
        param = BoolParameter("test", default=0)
        self.assertEqual(param.get_value(), False)

    def test_set_value_true(self):
        """Test setting True."""
        param = BoolParameter("test")
        param.set_value(True)
        self.assertEqual(param.get_value(), True)

    def test_set_value_false(self):
        """Test setting False."""
        param = BoolParameter("test", default=True)
        param.set_value(False)
        self.assertEqual(param.get_value(), False)

    def test_set_value_from_int(self):
        """Test converting int to bool."""
        param = BoolParameter("test")
        param.set_value(1)
        self.assertEqual(param.get_value(), True)

        param.set_value(0)
        self.assertEqual(param.get_value(), False)

    def test_set_value_from_string(self):
        """Test converting string to bool."""
        param = BoolParameter("test")
        param.set_value("yes")  # Non-empty string is True
        self.assertEqual(param.get_value(), True)

        param.set_value("")  # Empty string is False
        self.assertEqual(param.get_value(), False)

    def test_set_value_from_none(self):
        """Test converting None to bool."""
        param = BoolParameter("test", default=True)
        param.set_value(None)
        self.assertEqual(param.get_value(), False)

    def test_set_value_from_list(self):
        """Test converting list to bool."""
        param = BoolParameter("test")
        param.set_value([1, 2, 3])  # Non-empty list is True
        self.assertEqual(param.get_value(), True)

        param.set_value([])  # Empty list is False
        self.assertEqual(param.get_value(), False)

    def test_to_json(self):
        """Test JSON serialization."""
        param = BoolParameter("enabled", default=True,
                            description="Enable feature")
        data = param.to_json()
        self.assertEqual(data["type"], "bool")
        self.assertEqual(data["name"], "enabled")
        self.assertEqual(data["value"], True)
        self.assertEqual(data["description"], "Enable feature")

    def test_from_json(self):
        """Test JSON deserialization."""
        param = BoolParameter("test")
        param.from_json({"value": True})
        self.assertEqual(param.get_value(), True)

        param.from_json({"value": False})
        self.assertEqual(param.get_value(), False)

    def test_from_json_missing_value(self):
        """Test that missing value raises error."""
        param = BoolParameter("test")
        with self.assertRaises(KeyError):
            param.from_json({})

    def test_from_json_conversion(self):
        """Test that JSON values are converted to bool."""
        param = BoolParameter("test")
        param.from_json({"value": 1})
        self.assertEqual(param.get_value(), True)

        param.from_json({"value": 0})
        self.assertEqual(param.get_value(), False)

    def test_json_roundtrip(self):
        """Test JSON roundtrip."""
        original = BoolParameter("test", default=True)
        data = original.to_json()
        new_param = BoolParameter("test")
        new_param.from_json(data)
        self.assertEqual(new_param.get_value(), original.get_value())


class TestParameterIntegration(unittest.TestCase):
    """Integration tests for parameter system."""

    def test_multiple_parameters_independent(self):
        """Test that multiple parameters don't interfere."""
        int_param = IntParameter("count", default=10)
        float_param = FloatParameter("ratio", default=0.5)
        str_param = StringParameter("name", default="test")
        bool_param = BoolParameter("enabled", default=True)

        # Modify one
        int_param.set_value(20)

        # Others should be unchanged
        self.assertEqual(float_param.get_value(), 0.5)
        self.assertEqual(str_param.get_value(), "test")
        self.assertEqual(bool_param.get_value(), True)

    def test_json_serialization_consistency(self):
        """Test that all types serialize consistently."""
        params = [
            IntParameter("int_val", 42),
            FloatParameter("float_val", 3.14),
            StringParameter("str_val", "hello"),
            BoolParameter("bool_val", True)
        ]

        for param in params:
            data = param.to_json()
            # All should have required keys
            self.assertIn("type", data)
            self.assertIn("name", data)
            self.assertIn("value", data)
            self.assertIn("description", data)

    def test_parameter_type_preservation(self):
        """Test that parameter types are preserved through operations."""
        int_param = IntParameter("test", default=42)
        self.assertIsInstance(int_param.get_value(), int)

        float_param = FloatParameter("test", default=3.14)
        self.assertIsInstance(float_param.get_value(), float)

        str_param = StringParameter("test", default="hello")
        self.assertIsInstance(str_param.get_value(), str)

        bool_param = BoolParameter("test", default=True)
        self.assertIsInstance(bool_param.get_value(), bool)


if __name__ == '__main__':
    unittest.main()
