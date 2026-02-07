"""Add component for arithmetic addition operations.

This module implements a simple addition processor component that adds two float
values together and outputs the result.

Example:
    >>> add_comp = AddComponent()
    >>> add_comp.get_name()
    'Add'
"""

from ...core.component_base import ComponentBase
from ...core.data_types import DataType, DataVariant
from ...components.processor import ProcessorComponent
from ...registry.component_registry import register_component


@register_component(
    type_name="AddComponent",
    display_name="Add",
    category="Math",
    description="Adds two float values together (A + B)"
)
class AddComponent(ProcessorComponent):
    """Component that adds two float inputs together.

    This processor takes two float input pins A and B, and outputs their
    sum on the Result output pin.

    Attributes:
        Inputs:
            A (float): First operand
            B (float): Second operand
        Outputs:
            Result (float): Sum of A and B (A + B)
    """

    def get_name(self) -> str:
        """Get the component name.

        Returns:
            str: "Add"
        """
        return "Add"

    def initialize(self) -> None:
        """Initialize the component by creating pins.

        Adds two float input pins (A, B) and one float output pin (Result).
        """
        self.add_input_pin("A", DataType.FLOAT)
        self.add_input_pin("B", DataType.FLOAT)
        self.add_output_pin("Result", DataType.FLOAT)

    def process(self) -> None:
        """Process the input pins and produce the output.

        Retrieves values from inputs A and B, adds them together, and
        transmits the result through the Result output pin.

        Raises:
            ValueError: If input data cannot be converted to float
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

            # Perform addition
            result = value_a + value_b

            # Get output pin and transmit result
            output_pin = self.get_output_pin("Result")
            if output_pin is not None:
                output_pin.transmit_data(DataVariant(result, DataType.FLOAT))
            else:
                self.report_error("Output pin 'Result' not found")

        except ValueError as e:
            self.report_error(f"Failed to convert input to float: {str(e)}")
        except Exception as e:
            self.report_error(f"Unexpected error in Add component: {str(e)}")
