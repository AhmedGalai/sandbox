"""NOT gate logic component for VSE_PY"""

from typing import Optional

from ...core.component_base import ComponentBase
from ...core.data_types import DataType, DataVariant
from ...components.processor import ProcessorComponent
from ...registry.component_registry import register_component


@register_component(
    type_name="logic.not",
    display_name="NOT Gate",
    category="Logic",
    description="Logical NOT operation: inverts the input boolean value",
    tags=["logic", "gate", "boolean", "inverter"],
)
class NotGateComponent(ProcessorComponent):
    """NOT gate logic component.

    This component implements a logical NOT operation with a single boolean input.
    The output is the inverse of the input: True becomes False, False becomes True.

    Pins:
        Inputs:
            - Input (boolean): The input value to invert
        Outputs:
            - Result (boolean): NOT Input

    Examples:
        >>> not_gate = NotGateComponent()
        >>> not_gate.get_input_pin("Input").set_data(DataVariant(True))
        >>> not_gate.execute()
        >>> not_gate.get_output_pin("Result").data.to_bool()
        False
    """

    def get_name(self) -> str:
        """Get the component name.

        Returns:
            str: "NOT Gate"
        """
        return "NOT Gate"

    def initialize(self) -> None:
        """Initialize the NOT gate component with input and output pins.

        Creates:
            - Input pin Input (boolean)
            - Output pin Result (boolean)
        """
        self.add_input_pin("Input", DataType.BOOLEAN)
        self.add_output_pin("Result", DataType.BOOLEAN)

    def process(self) -> None:
        """Process the NOT operation.

        Retrieves the boolean value from input, performs logical NOT,
        and transmits the result.

        Error Handling:
            - Reports error if input pin is missing or invalid
            - Gracefully handles missing data by treating as False
        """
        try:
            # Get input pins
            input_pin = self.get_input_pin("Input")
            result_pin = self.get_output_pin("Result")

            # Handle missing data gracefully
            if input_pin is None or result_pin is None:
                self.report_error("Missing input or output pins")
                return

            # Get boolean value, defaulting to False if data is invalid
            try:
                input_value = input_pin.data.to_bool() if input_pin.data is not None else False
            except (ValueError, TypeError, AttributeError):
                input_value = False

            # Perform NOT operation
            result = not input_value

            # Transmit result
            result_pin.transmit_data(DataVariant(result))

        except Exception as e:
            self.report_error(f"Error in NOT gate processing: {str(e)}")
