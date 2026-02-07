"""Compare component for float value comparison.

This module implements a comparison processor component that compares two float
values using a configurable comparison operation and outputs a boolean result.

Example:
    >>> comp = CompareComponent()
    >>> comp.get_name()
    'Compare'
"""

from ...core.component_base import ComponentBase
from ...core.data_types import DataType, DataVariant
from ...core.parameter import StringParameter
from ...components.processor import ProcessorComponent
from ...registry.component_registry import register_component


@register_component(
    type_name="CompareComponent",
    display_name="Compare",
    category="Math",
    description="Compares two float values using configurable operations"
)
class CompareComponent(ProcessorComponent):
    """Component that compares two float inputs using a configurable operation.

    This processor takes two float input pins A and B, compares them using the
    operation specified by the operation parameter, and outputs a boolean result.

    Attributes:
        Inputs:
            A (float): First value to compare
            B (float): Second value to compare
        Parameters:
            operation (string): Comparison operation to perform
                Options: "equal", "not_equal", "greater", "less",
                         "greater_equal", "less_equal"
                Default: "equal"
        Outputs:
            Result (bool): Boolean result of the comparison
    """

    def get_name(self) -> str:
        """Get the component name.

        Returns:
            str: "Compare"
        """
        return "Compare"

    def initialize(self) -> None:
        """Initialize the component by creating pins and parameters.

        Adds two float input pins (A, B), one boolean output pin (Result),
        and one string parameter for the operation type.
        """
        self.add_input_pin("A", DataType.FLOAT)
        self.add_input_pin("B", DataType.FLOAT)
        self.add_output_pin("Result", DataType.BOOLEAN)

        # Add operation parameter
        self.add_parameter(StringParameter(
            name="operation",
            default="equal",
            description="Comparison operation: equal, not_equal, greater, less, greater_equal, less_equal"
        ))

    def process(self) -> None:
        """Process the input pins and produce the output.

        Retrieves values from inputs A and B, performs the comparison using
        the operation parameter, and transmits the boolean result through the
        Result output pin.

        Raises:
            ValueError: If input data cannot be converted to float or operation is invalid
            RuntimeError: If input pins are not accessible
        """
        try:
            # Get input pins
            pin_a = self.get_input_pin("A")
            pin_b = self.get_input_pin("B")

            if pin_a is None or pin_b is None:
                self.report_error("Missing input pins A or B")
                return

            # Convert input data to floats
            value_a = pin_a.data.to_float()
            value_b = pin_b.data.to_float()

            # Get the operation parameter
            operation_param = self.get_parameter("operation")
            if operation_param is None:
                self.report_error("Operation parameter not found")
                return

            operation = operation_param.get_value().lower().strip()

            # Perform comparison based on operation
            result = False
            if operation == "equal":
                result = value_a == value_b
            elif operation == "not_equal":
                result = value_a != value_b
            elif operation == "greater":
                result = value_a > value_b
            elif operation == "less":
                result = value_a < value_b
            elif operation == "greater_equal":
                result = value_a >= value_b
            elif operation == "less_equal":
                result = value_a <= value_b
            else:
                self.report_error(
                    f"Invalid operation '{operation}'. Valid operations are: "
                    "equal, not_equal, greater, less, greater_equal, less_equal"
                )
                return

            # Get output pin and transmit result
            output_pin = self.get_output_pin("Result")
            if output_pin is not None:
                output_pin.transmit_data(DataVariant(result, DataType.BOOLEAN))
            else:
                self.report_error("Output pin 'Result' not found")

        except ValueError as e:
            self.report_error(f"Failed to convert input to float: {str(e)}")
        except Exception as e:
            self.report_error(f"Unexpected error in Compare component: {str(e)}")
