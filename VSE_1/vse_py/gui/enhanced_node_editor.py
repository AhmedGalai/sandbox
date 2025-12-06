"""Enhanced Node Editor with full connection support

This module provides a comprehensive node editor with:
- Visual node representation
- Pin-based connections using topic pub/sub
- Component instantiation from the registry
- Integration with sidebar components
"""

import dearpygui.dearpygui as dpg
from typing import Dict, List, Optional, Tuple, Callable
from ..core.component_base import ComponentBase
from ..core.topic_registry import TopicRegistry
from ..core.data_types import DataType, DataVariant
from ..registry.component_registry import ComponentRegistry


class NodeEditorConnection:
    """Represents a visual connection between two pins."""

    def __init__(self, from_node_id: str, from_pin: str, to_node_id: str, to_pin: str, topic_name: str):
        """Initialize a connection.

        Args:
            from_node_id: Source node ID
            from_pin: Source output pin name
            to_node_id: Destination node ID
            to_pin: Destination input pin name
            topic_name: Topic used for data transfer
        """
        self.from_node_id = from_node_id
        self.from_pin = from_pin
        self.to_node_id = to_node_id
        self.to_pin = to_pin
        self.topic_name = topic_name
        self.subscription_id: Optional[str] = None


class EnhancedNodeEditor:
    """Enhanced node editor with full VSE functionality."""

    def __init__(
        self,
        on_node_selected: Optional[Callable[[str, ComponentBase], None]] = None,
        on_nodes_changed: Optional[Callable[[], None]] = None
    ):
        """Initialize the enhanced node editor.

        Args:
            on_node_selected: Callback when a node is selected (node_id, component)
            on_nodes_changed: Callback when nodes are added/removed/changed
        """
        self.tag = dpg.generate_uuid()
        self.component_registry = ComponentRegistry.instance()
        self.topic_registry = TopicRegistry.instance()

        self.nodes: Dict[str, ComponentBase] = {}  # node_id -> component
        self.node_ui_tags: Dict[str, int] = {}  # node_id -> dpg tag
        self.connections: List[NodeEditorConnection] = []
        self.connection_tags: List[int] = []  # dpg tags for connection links

        self.on_node_selected = on_node_selected
        self.on_nodes_changed = on_nodes_changed

        self.selected_node_id: Optional[str] = None

    def create(self, parent: Optional[int] = None) -> int:
        """Create the node editor UI.

        Args:
            parent: Optional parent window ID

        Returns:
            int: The UI element tag
        """
        editor_kwargs = {
            "tag": self.tag,
            "callback": self._on_link_created,
            "delink_callback": self._on_link_deleted,
            "minimap": True,
            "minimap_location": dpg.mvNodeMiniMap_Location_BottomRight
        }
        if parent is not None:
            editor_kwargs["parent"] = parent

        with dpg.node_editor(**editor_kwargs):
            pass  # Nodes will be added dynamically

        return self.tag

    def add_component(self, type_name: str, pos: Tuple[float, float] = (0, 0)) -> Optional[str]:
        """Add a new component node to the editor.

        Args:
            type_name: Component type from the registry
            pos: Initial position (x, y) for the node

        Returns:
            Optional[str]: Node ID if successful, None otherwise
        """
        try:
            # Create component instance
            component = self.component_registry.create_component(type_name)
            node_id = component.id

            # Store component
            self.nodes[node_id] = component

            # Create UI node
            self._create_node_ui(node_id, component, pos)

            # Notify listeners
            if self.on_nodes_changed:
                self.on_nodes_changed()

            return node_id

        except Exception as e:
            print(f"Error adding component {type_name}: {e}")
            return None

    def remove_node(self, node_id: str):
        """Remove a node from the editor.

        Args:
            node_id: ID of the node to remove
        """
        if node_id not in self.nodes:
            return

        # Remove all connections involving this node
        self.connections = [
            conn for conn in self.connections
            if conn.from_node_id != node_id and conn.to_node_id != node_id
        ]

        # Remove UI
        if node_id in self.node_ui_tags:
            dpg.delete_item(self.node_ui_tags[node_id])
            del self.node_ui_tags[node_id]

        # Remove component
        del self.nodes[node_id]

        # Notify listeners
        if self.on_nodes_changed:
            self.on_nodes_changed()

    def _create_node_ui(self, node_id: str, component: ComponentBase, pos: Tuple[float, float]):
        """Create the UI representation of a node.

        Args:
            node_id: Unique node identifier
            component: Component instance
            pos: Position (x, y) for the node
        """
        node_tag = dpg.generate_uuid()
        self.node_ui_tags[node_id] = node_tag

        with dpg.node(
            tag=node_tag,
            label=f"{component.get_name()} [{node_id[:8]}]",
            parent=self.tag,
            pos=pos
        ):
            # Input pins
            for pin_name, pin in component.input_pins.items():
                pin_tag = dpg.generate_uuid()
                with dpg.node_attribute(
                    tag=pin_tag,
                    attribute_type=dpg.mvNode_Attr_Input,
                    user_data={"node_id": node_id, "pin_name": pin_name, "is_output": False}
                ):
                    dpg.add_text(f"{pin_name} ({pin.dtype.name})")

            # Add spacing between inputs and outputs
            if component.input_pins and component.output_pins:
                dpg.add_spacer(height=10)

            # Output pins
            for pin_name, pin in component.output_pins.items():
                pin_tag = dpg.generate_uuid()
                with dpg.node_attribute(
                    tag=pin_tag,
                    attribute_type=dpg.mvNode_Attr_Output,
                    user_data={"node_id": node_id, "pin_name": pin_name, "is_output": True}
                ):
                    dpg.add_text(f"{pin_name} ({pin.dtype.name})")

        # Make node selectable
        dpg.set_item_callback(node_tag, lambda s, a: self._on_node_clicked(node_id))

    def _on_node_clicked(self, node_id: str):
        """Handle node selection.

        Args:
            node_id: ID of the clicked node
        """
        self.selected_node_id = node_id
        if self.on_node_selected and node_id in self.nodes:
            self.on_node_selected(node_id, self.nodes[node_id])

    def _on_link_created(self, sender, app_data):
        """Handle new connection created by user.

        Args:
            sender: DPG sender
            app_data: (from_pin_tag, to_pin_tag) tuple
        """
        from_pin_tag, to_pin_tag = app_data

        # Get pin information
        from_data = dpg.get_item_user_data(from_pin_tag)
        to_data = dpg.get_item_user_data(to_pin_tag)

        if not from_data or not to_data:
            return

        # Ensure from is output and to is input
        if not from_data.get("is_output") or to_data.get("is_output"):
            print("Invalid connection: must connect output to input")
            return

        from_node_id = from_data["node_id"]
        from_pin = from_data["pin_name"]
        to_node_id = to_data["node_id"]
        to_pin = to_data["pin_name"]

        # Create connection
        self._create_connection(from_node_id, from_pin, to_node_id, to_pin)

    def _create_connection(
        self,
        from_node_id: str,
        from_pin: str,
        to_node_id: str,
        to_pin: str
    ) -> bool:
        """Create a pub/sub connection between two pins.

        Args:
            from_node_id: Source node ID
            from_pin: Source output pin name
            to_node_id: Destination node ID
            to_pin: Destination input pin name

        Returns:
            bool: True if connection successful
        """
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            return False

        from_component = self.nodes[from_node_id]
        to_component = self.nodes[to_node_id]

        from_pin_obj = from_component.get_output_pin(from_pin)
        to_pin_obj = to_component.get_input_pin(to_pin)

        if not from_pin_obj or not to_pin_obj:
            print(f"Pins not found: {from_pin} or {to_pin}")
            return False

        # Create unique topic name
        topic_name = f"{from_node_id}_{from_pin}_to_{to_node_id}_{to_pin}"

        # Create topic with the output pin's data type
        if not self.topic_registry.has_topic(topic_name):
            self.topic_registry.create_topic(topic_name, from_pin_obj.dtype)

        # Subscribe input pin to the topic
        def on_data_received(topic_name: str, data: DataVariant):
            """Callback when data is published to the topic."""
            to_pin_obj.receive_data(data)

        subscription_id = self.topic_registry.subscribe(topic_name, on_data_received)

        # Connect output pin to publish to this topic
        from_pin_obj.connect_to_topic(topic_name)

        # Create connection record
        connection = NodeEditorConnection(
            from_node_id, from_pin, to_node_id, to_pin, topic_name
        )
        connection.subscription_id = subscription_id
        self.connections.append(connection)

        print(f"Connected {from_node_id}.{from_pin} -> {to_node_id}.{to_pin} via topic {topic_name}")
        return True

    def _on_link_deleted(self, sender, link_id):
        """Handle connection deletion.

        Args:
            sender: DPG sender
            link_id: ID of the deleted link
        """
        # Find and remove the connection
        # Note: DearPyGui handles the visual link deletion
        # We need to clean up the topic subscription
        # This is a simplified implementation
        pass

    def get_all_nodes(self) -> Dict[str, ComponentBase]:
        """Get all nodes in the editor.

        Returns:
            Dict[str, ComponentBase]: Dictionary of node_id -> component
        """
        return self.nodes.copy()

    def get_node_positions(self) -> Dict[str, Tuple[float, float]]:
        """Get positions of all nodes.

        Returns:
            Dict[str, Tuple[float, float]]: Dictionary of node_id -> (x, y)
        """
        positions = {}
        for node_id, ui_tag in self.node_ui_tags.items():
            if dpg.does_item_exist(ui_tag):
                pos = dpg.get_item_pos(ui_tag)
                positions[node_id] = pos
        return positions

    def clear(self):
        """Clear all nodes from the editor."""
        for node_id in list(self.nodes.keys()):
            self.remove_node(node_id)

        self.connections.clear()
        self.selected_node_id = None

        if self.on_nodes_changed:
            self.on_nodes_changed()
