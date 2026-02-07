"""AND gate logic component for VSE_PY"""

from typing import Optional

from ...core.component_base import ComponentBase
from ...core.data_types import DataType, DataVariant
from ...components.processor import ProcessorComponent
from ...registry.component_registry import register_component


@register_component(
    type_name="logic.and",
    display_name="AND Gate",
    category="Logic",
    description="Logical AND operation: returns True only if both inputs are True",
    tags=["logic", "gate", "boolean"],
)
class AndGateComponent(ProcessorComponent):
    """AND gate logic component.

    This component implements a logical AND operation with two boolean inputs.
    The output is True only when both input A and input B are True.

    Pins:
        Inputs:
            - A (boolean): First input
            - B (boolean): Second input
        Outputs:
            - Result (boolean): A AND B

    Examples:
        >>> and_gate = AndGateComponent()
        >>> and_gate.get_input_pin("A").set_data(DataVariant(True))
        >>> and_gate.get_input_pin("B").set_data(DataVariant(True))
        >>> and_gate.execute()
        >>> and_gate.get_output_pin("Result").data.to_bool()
        True
    """

    def get_name(self) -> str:
        """Get the component name.

        Returns:
            str: "AND Gate"
        """
        return "AND Gate"

    def initialize(self) -> None:
        """Initialize the AND gate component with input and output pins.

        Creates:
            - Input pin A (boolean)
            - Input pin B (boolean)
            - Output pin Result (boolean)
        """
        self.add_input_pin("A", DataType.BOOLEAN)
        self.add_input_pin("B", DataType.BOOLEAN)
        self.add_output_pin("Result", DataType.BOOLEAN)

    def process(self) -> None:
        """Process the AND operation.

        Retrieves boolean values from inputs A and B, performs logical AND,
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

            # Perform AND operation
            result = a_value and b_value

            # Transmit result
            result_pin.transmit_data(DataVariant(result))

        except Exception as e:
            self.report_error(f"Error in AND gate processing: {str(e)}")
