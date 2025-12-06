"""Node Inspector panel for viewing and editing node properties

Allows users to inspect and modify parameters of selected nodes.
"""

import dearpygui.dearpygui as dpg
from typing import Optional, Dict, Any
from ..core.component_base import ComponentBase
from ..core.parameter import Parameter, IntParameter, FloatParameter, StringParameter, BoolParameter


class NodeInspector:
    """Inspector panel for viewing and editing node properties."""

    def __init__(self):
        """Initialize the node inspector."""
        self.tag = dpg.generate_uuid()
        self.content_tag = dpg.generate_uuid()
        self.current_node_id: Optional[str] = None
        self.current_component: Optional[ComponentBase] = None

    def create(self, parent: Optional[int] = None) -> int:
        """Create the inspector UI.

        Args:
            parent: Optional parent window ID

        Returns:
            int: The UI element tag
        """
        group_kwargs = {"tag": self.tag}
        if parent is not None:
            group_kwargs["parent"] = parent

        with dpg.group(**group_kwargs):
            with dpg.child_window(tag=self.content_tag, height=-1, width=-1):
                dpg.add_text("No node selected", color=(150, 150, 150))

        return self.tag

    def inspect_node(self, node_id: str, component: ComponentBase):
        """Display properties of a node for inspection/editing.

        Args:
            node_id: Unique identifier for the node
            component: ComponentBase instance to inspect
        """
        self.current_node_id = node_id
        self.current_component = component
        self._refresh_inspector()

    def clear(self):
        """Clear the inspector (no node selected)."""
        self.current_node_id = None
        self.current_component = None
        self._refresh_inspector()

    def _refresh_inspector(self):
        """Refresh the inspector display."""
        # Clear existing content
        dpg.delete_item(self.content_tag, children_only=True)

        if not self.current_component:
            dpg.add_text(
                "No node selected",
                color=(150, 150, 150),
                parent=self.content_tag
            )
            return

        component = self.current_component

        # Node identification
        with dpg.group(parent=self.content_tag):
            dpg.add_text("Node Information", color=(200, 220, 255))
            dpg.add_separator()

            with dpg.table(header_row=False, borders_innerV=True, parent=self.content_tag):
                dpg.add_table_column()
                dpg.add_table_column()

                with dpg.table_row():
                    dpg.add_text("Name:")
                    dpg.add_text(component.get_name())

                with dpg.table_row():
                    dpg.add_text("Category:")
                    dpg.add_text(component.get_category())

                with dpg.table_row():
                    dpg.add_text("ID:")
                    dpg.add_text(self.current_node_id[:8] + "...")

                with dpg.table_row():
                    dpg.add_text("State:")
                    state = component.state
                    state_colors = {
                        "IDLE": (100, 200, 100),
                        "RUNNING": (100, 150, 255),
                        "ERROR": (255, 100, 100),
                        "DISABLED": (150, 150, 150)
                    }
                    dpg.add_text(state.name, color=state_colors.get(state.name, (200, 200, 200)))

        dpg.add_spacer(height=10, parent=self.content_tag)

        # Input pins
        input_pins = component.input_pins
        if input_pins:
            dpg.add_text("Input Pins", color=(200, 220, 255), parent=self.content_tag)
            dpg.add_separator(parent=self.content_tag)

            for pin_name, pin in input_pins.items():
                with dpg.group(horizontal=True, parent=self.content_tag):
                    dpg.add_text(f"  {pin_name}:")
                    dpg.add_text(
                        f"{pin.dtype.name} [{pin.status.name}]",
                        color=(150, 180, 200)
                    )

            dpg.add_spacer(height=10, parent=self.content_tag)

        # Output pins
        output_pins = component.output_pins
        if output_pins:
            dpg.add_text("Output Pins", color=(200, 220, 255), parent=self.content_tag)
            dpg.add_separator(parent=self.content_tag)

            for pin_name, pin in output_pins.items():
                with dpg.group(horizontal=True, parent=self.content_tag):
                    dpg.add_text(f"  {pin_name}:")
                    dpg.add_text(
                        f"{pin.dtype.name} ({len(pin._connections)} conn.)",
                        color=(150, 180, 200)
                    )

            dpg.add_spacer(height=10, parent=self.content_tag)

        # Parameters
        parameters = component.parameters
        if parameters:
            dpg.add_text("Parameters", color=(200, 220, 255), parent=self.content_tag)
            dpg.add_separator(parent=self.content_tag)

            for param_name, param in parameters.items():
                self._create_parameter_widget(param)

            dpg.add_spacer(height=10, parent=self.content_tag)
        else:
            dpg.add_text("No parameters", color=(150, 150, 150), parent=self.content_tag)

        # Error message if in error state
        if component.state.name == "ERROR":
            dpg.add_spacer(height=10, parent=self.content_tag)
            dpg.add_text("Error:", color=(255, 100, 100), parent=self.content_tag)
            dpg.add_text(
                component.error_message,
                color=(255, 150, 150),
                wrap=0,
                parent=self.content_tag
            )

    def _create_parameter_widget(self, param: Parameter):
        """Create appropriate widget for a parameter.

        Args:
            param: Parameter instance to create widget for
        """
        if isinstance(param, IntParameter):
            dpg.add_input_int(
                label=param.name,
                default_value=param.value,
                callback=lambda s, a, u: u.set_value(a),
                user_data=param,
                parent=self.content_tag
            )
        elif isinstance(param, FloatParameter):
            dpg.add_input_float(
                label=param.name,
                default_value=param.value,
                callback=lambda s, a, u: u.set_value(a),
                user_data=param,
                parent=self.content_tag
            )
        elif isinstance(param, StringParameter):
            dpg.add_input_text(
                label=param.name,
                default_value=param.value,
                callback=lambda s, a, u: u.set_value(a),
                user_data=param,
                parent=self.content_tag
            )
        elif isinstance(param, BoolParameter):
            dpg.add_checkbox(
                label=param.name,
                default_value=param.value,
                callback=lambda s, a, u: u.set_value(a),
                user_data=param,
                parent=self.content_tag
            )
        else:
            # Generic parameter display
            with dpg.group(horizontal=True, parent=self.content_tag):
                dpg.add_text(f"{param.name}:")
                dpg.add_text(str(param.value), color=(150, 180, 200))
