"""XOR gate logic component for VSE_PY"""

from typing import Optional

from ...core.component_base import ComponentBase
from ...core.data_types import DataType, DataVariant
from ...components.processor import ProcessorComponent
from ...registry.component_registry import register_component


@register_component(
    type_name="logic.xor",
    display_name="XOR Gate",
    category="Logic",
    description="Logical XOR operation: returns True if inputs are different",
    tags=["logic", "gate", "boolean", "exclusive"],
)
class XorGateComponent(ProcessorComponent):
    """XOR gate logic component.

    This component implements a logical XOR (exclusive OR) operation with two boolean inputs.
    The output is True when the inputs are different (one True and one False),
    and False when the inputs are the same (both True or both False).

    Pins:
        Inputs:
            - A (boolean): First input
            - B (boolean): Second input
        Outputs:
            - Result (boolean): A XOR B

    Examples:
        >>> xor_gate = XorGateComponent()
        >>> xor_gate.get_input_pin("A").set_data(DataVariant(True))
        >>> xor_gate.get_input_pin("B").set_data(DataVariant(False))
        >>> xor_gate.execute()
        >>> xor_gate.get_output_pin("Result").data.to_bool()
        True
    """

    def get_name(self) -> str:
        """Get the component name.

        Returns:
            str: "XOR Gate"
        """
        return "XOR Gate"

    def initialize(self) -> None:
        """Initialize the XOR gate component with input and output pins.

        Creates:
            - Input pin A (boolean)
            - Input pin B (boolean)
            - Output pin Result (boolean)
        """
        self.add_input_pin("A", DataType.BOOLEAN)
        self.add_input_pin("B", DataType.BOOLEAN)
        self.add_output_pin("Result", DataType.BOOLEAN)

    def process(self) -> None:
        """Process the XOR operation.

        Retrieves boolean values from inputs A and B, performs logical XOR,
        and transmits the result.

        Error Handling:
            - Reports error if inputs are missing or invalid
            - Gracefully handles missing data by treating as False
        """
        try:
            # Get input pins
            a_pin = self.get_input_pin("A")
            b_pin = self.get_input_pin("B")
            result_pin = self.get_output_pin("Result")

            # Handle missing data gracefully
            if a_pin is None or b_pin is None or result_pin is None:
                self.report_error("Missing input or output pins")
                return

            # Get boolean values, defaulting to False if data is invalid
            try:
                a_value = a_pin.data.to_bool() if a_pin.data is not None else False
            except (ValueError, TypeError, AttributeError):
                a_value = False

            try:
                b_value = b_pin.data.to_bool() if b_pin.data is not None else False
            except (ValueError, TypeError, AttributeError):
                b_value = False

            # Perform XOR operation
            result = a_value != b_value

            # Transmit result
            result_pin.transmit_data(DataVariant(result))

        except Exception as e:
            self.report_error(f"Error in XOR gate processing: {str(e)}")
