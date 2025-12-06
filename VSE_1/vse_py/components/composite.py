"""Composite Component - Container for subgraphs (like Simulink subsystems)

Allows creating reusable subgraphs by composing multiple components
together with defined input/output interfaces.
"""

from typing import Dict, List, Optional, Tuple
from ..core.component_base import ComponentBase, ComponentState
from ..core.data_types import DataType, DataVariant
from ..core.pin import InputPin, OutputPin
from ..registry.component_registry import register_component


class CompositeComponent(ComponentBase):
    """Component that contains a subgraph of other components.

    This is similar to Simulink subsystems - you can define inputs and outputs
    for the composite, and internally connect multiple components together.

    The composite acts as a single component from the outside, but internally
    executes a full subgraph.
    """

    def __init__(self):
        """Initialize the composite component."""
        self.internal_components: Dict[str, ComponentBase] = {}
        self.internal_connections: List[Tuple[str, str, str, str]] = []  # (from_id, from_pin, to_id, to_pin)
        self.input_mappings: Dict[str, Tuple[str, str]] = {}  # external_pin -> (internal_id, internal_pin)
        self.output_mappings: Dict[str, Tuple[str, str]] = {}  # external_pin -> (internal_id, internal_pin)
        super().__init__()

    def get_name(self) -> str:
        """Get component name."""
        return "Composite"

    def get_category(self) -> str:
        """Get component category."""
        return "Container"

    def get_color(self) -> tuple:
        """Get component color - purple for composites."""
        return (156, 39, 176)

    def add_internal_component(self, component: ComponentBase, component_id: Optional[str] = None) -> str:
        """Add a component to the internal subgraph.

        Args:
            component: ComponentBase instance to add
            component_id: Optional ID to use (generates one if not provided)

        Returns:
            str: The component ID used
        """
        if component_id is None:
            component_id = component.id

        self.internal_components[component_id] = component
        return component_id

    def remove_internal_component(self, component_id: str) -> bool:
        """Remove a component from the internal subgraph.

        Args:
            component_id: ID of component to remove

        Returns:
            bool: True if removed, False if not found
        """
        if component_id in self.internal_components:
            del self.internal_components[component_id]
            # Also remove connections involving this component
            self.internal_connections = [
                conn for conn in self.internal_connections
                if conn[0] != component_id and conn[2] != component_id
            ]
            return True
        return False

    def connect_internal(
        self,
        from_id: str,
        from_pin: str,
        to_id: str,
        to_pin: str
    ) -> bool:
        """Connect two internal components.

        Args:
            from_id: Source component ID
            from_pin: Source output pin name
            to_id: Destination component ID
            to_pin: Destination input pin name

        Returns:
            bool: True if connection successful
        """
        # Validate components exist
        if from_id not in self.internal_components or to_id not in self.internal_components:
            return False

        from_comp = self.internal_components[from_id]
        to_comp = self.internal_components[to_id]

        # Validate pins exist
        if not from_comp.get_output_pin(from_pin) or not to_comp.get_input_pin(to_pin):
            return False

        # Add connection
        connection = (from_id, from_pin, to_id, to_pin)
        if connection not in self.internal_connections:
            self.internal_connections.append(connection)

        return True

    def map_input(self, external_pin_name: str, internal_id: str, internal_pin_name: str):
        """Map an external input pin to an internal component's input.

        This defines how data entering the composite is routed to internal components.

        Args:
            external_pin_name: Name of the composite's input pin
            internal_id: ID of internal component
            internal_pin_name: Name of internal component's input pin
        """
        self.input_mappings[external_pin_name] = (internal_id, internal_pin_name)

    def map_output(self, external_pin_name: str, internal_id: str, internal_pin_name: str):
        """Map an internal component's output to an external output pin.

        This defines how data from internal components is exposed as outputs.

        Args:
            external_pin_name: Name of the composite's output pin
            internal_id: ID of internal component
            internal_pin_name: Name of internal component's output pin
        """
        self.output_mappings[external_pin_name] = (internal_id, internal_pin_name)

    def execute(self) -> None:
        """Execute the composite component.

        Execution flow:
        1. Route external inputs to mapped internal components
        2. Execute internal components in topological order
        3. Propagate data through internal connections
        4. Route mapped internal outputs to external outputs
        """
        try:
            self.set_state(ComponentState.RUNNING)

            # Step 1: Route external inputs to internal components
            for external_pin_name, (internal_id, internal_pin_name) in self.input_mappings.items():
                external_pin = self.get_input_pin(external_pin_name)
                if external_pin and external_pin.has_data():
                    internal_comp = self.internal_components.get(internal_id)
                    if internal_comp:
                        internal_pin = internal_comp.get_input_pin(internal_pin_name)
                        if internal_pin:
                            internal_pin.receive_data(external_pin.data)

            # Step 2 & 3: Execute internal graph
            # For now, execute in order (could implement topological sort for optimization)
            for component in self.internal_components.values():
                component.execute()

                # Propagate outputs through internal connections
                for from_id, from_pin_name, to_id, to_pin_name in self.internal_connections:
                    if from_id == component.id:
                        from_pin = component.get_output_pin(from_pin_name)
                        to_comp = self.internal_components.get(to_id)

                        if from_pin and to_comp:
                            to_pin = to_comp.get_input_pin(to_pin_name)
                            if to_pin:
                                # Transfer data from output to input
                                # This is simplified - in production you'd use the topic system
                                pass

            # Step 4: Route internal outputs to external outputs
            for external_pin_name, (internal_id, internal_pin_name) in self.output_mappings.items():
                internal_comp = self.internal_components.get(internal_id)
                if internal_comp:
                    internal_pin = internal_comp.get_output_pin(internal_pin_name)
                    external_pin = self.get_output_pin(external_pin_name)

                    if internal_pin and external_pin:
                        # Transfer the data (simplified)
                        pass

            self.set_state(ComponentState.IDLE)

        except Exception as e:
            self.report_error(f"Error executing composite: {str(e)}")

    def serialize(self) -> dict:
        """Serialize the composite component including internal structure."""
        base_data = super().serialize()

        base_data.update({
            "internal_components": {
                comp_id: comp.serialize()
                for comp_id, comp in self.internal_components.items()
            },
            "internal_connections": self.internal_connections,
            "input_mappings": self.input_mappings,
            "output_mappings": self.output_mappings
        })

        return base_data

    def deserialize(self, data: dict):
        """Deserialize the composite component."""
        super().deserialize(data)

        # TODO: Deserialize internal components and connections
        # This would require the component registry to recreate components
        pass


# Register the composite component
@register_component(
    type_name="CompositeComponent",
    display_name="Composite (Subsystem)",
    category="Container",
    description="Container for creating reusable subgraphs (like Simulink subsystems)"
)
class CompositeComponentRegistered(CompositeComponent):
    """Registered version of composite component."""
    pass
