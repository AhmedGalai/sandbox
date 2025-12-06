"""Interface components for defining composite component boundaries

InputInterface and OutputInterface components are used inside composite
components to define their external interface, similar to Inport/Outport
blocks in Simulink.
"""

from ..core.component_base import ComponentBase, ComponentState
from ..core.data_types import DataType, DataVariant
from ..core.parameter import StringParameter, IntParameter
from ..registry.component_registry import register_component


@register_component(
    type_name="InputInterface",
    display_name="Input Interface",
    category="Interface",
    description="Defines an input to a composite component (like Simulink Inport)"
)
class InputInterface(ComponentBase):
    """Input interface component for composite components.

    When placed inside a composite component, this creates an external
    input pin on the composite that routes data to this component's output.
    """

    def __init__(self):
        """Initialize the input interface component."""
        super().__init__()

    def get_name(self) -> str:
        """Get component name."""
        return "Input"

    def get_category(self) -> str:
        """Get component category."""
        return "Interface"

    def get_color(self) -> tuple:
        """Get component color - cyan for inputs."""
        return (0, 188, 212)

    def initialize(self) -> None:
        """Initialize the component.

        Adds parameters to configure the interface and an output pin
        for routing data into the subgraph.
        """
        # Parameter: Interface name
        self.add_parameter(StringParameter(
            name="interface_name",
            default="Input1",
            description="Name of the external input pin"
        ))

        # Parameter: Data type
        self.add_parameter(IntParameter(
            name="data_type",
            default=DataType.ANY.value,
            min_val=0,
            max_val=len(DataType) - 1,
            description="Data type for this interface"
        ))

        # Output pin - data flows from the external input through this output
        self.add_output_pin("Out", DataType.ANY)

    def execute(self) -> None:
        """Execute the interface component.

        In a proper implementation, this would receive data from the
        composite's external input and transmit it through the output pin.
        """
        try:
            self.set_state(ComponentState.RUNNING)

            # The composite component's execution logic handles routing
            # data to/from interface components

            self.set_state(ComponentState.IDLE)

        except Exception as e:
            self.report_error(f"Error in InputInterface: {str(e)}")


@register_component(
    type_name="OutputInterface",
    display_name="Output Interface",
    category="Interface",
    description="Defines an output from a composite component (like Simulink Outport)"
)
class OutputInterface(ComponentBase):
    """Output interface component for composite components.

    When placed inside a composite component, this creates an external
    output pin on the composite that receives data from this component's input.
    """

    def __init__(self):
        """Initialize the output interface component."""
        super().__init__()

    def get_name(self) -> str:
        """Get component name."""
        return "Output"

    def get_category(self) -> str:
        """Get component category."""
        return "Interface"

    def get_color(self) -> tuple:
        """Get component color - orange for outputs."""
        return (255, 152, 0)

    def initialize(self) -> None:
        """Initialize the component.

        Adds parameters to configure the interface and an input pin
        for receiving data from the subgraph.
        """
        # Parameter: Interface name
        self.add_parameter(StringParameter(
            name="interface_name",
            default="Output1",
            description="Name of the external output pin"
        ))

        # Parameter: Data type
        self.add_parameter(IntParameter(
            name="data_type",
            default=DataType.ANY.value,
            min_val=0,
            max_val=len(DataType) - 1,
            description="Data type for this interface"
        ))

        # Input pin - data flows into this input and out through the composite's external output
        self.add_input_pin("In", DataType.ANY)

    def execute(self) -> None:
        """Execute the interface component.

        In a proper implementation, this would receive data from the
        input pin and make it available at the composite's external output.
        """
        try:
            self.set_state(ComponentState.RUNNING)

            # The composite component's execution logic handles routing
            # data to/from interface components

            self.set_state(ComponentState.IDLE)

        except Exception as e:
            self.report_error(f"Error in OutputInterface: {str(e)}")


@register_component(
    type_name="PassThrough",
    display_name="Pass Through",
    category="Interface",
    description="Simple component that passes data from input to output unchanged"
)
class PassThrough(ComponentBase):
    """Pass-through component for testing and debugging.

    Simply receives data on input and transmits it unchanged to output.
    Useful for routing and testing connections.
    """

    def get_name(self) -> str:
        """Get component name."""
        return "Pass Through"

    def get_category(self) -> str:
        """Get component category."""
        return "Interface"

    def get_color(self) -> tuple:
        """Get component color - gray for pass-through."""
        return (158, 158, 158)

    def initialize(self) -> None:
        """Initialize the component with input and output pins."""
        self.add_input_pin("In", DataType.ANY)
        self.add_output_pin("Out", DataType.ANY)

    def execute(self) -> None:
        """Execute - pass data through unchanged."""
        try:
            self.set_state(ComponentState.RUNNING)

            input_pin = self.get_input_pin("In")
            output_pin = self.get_output_pin("Out")

            if input_pin and output_pin and input_pin.has_data():
                # Pass data through unchanged
                output_pin.transmit_data(input_pin.data)

            self.set_state(ComponentState.IDLE)

        except Exception as e:
            self.report_error(f"Error in PassThrough: {str(e)}")
