"""Nodes tree view component

Displays a hierarchical tree view of all nodes in the graph,
organized by category or type.
"""

import dearpygui.dearpygui as dpg
from typing import Dict, List, Optional, Callable
from ..core.component_base import ComponentBase


class NodesTree:
    """Tree view showing all nodes in the graph."""

    def __init__(self, on_node_selected: Optional[Callable[[str], None]] = None):
        """Initialize the nodes tree.

        Args:
            on_node_selected: Callback when a node is selected in the tree
                            Called with the node ID
        """
        self.tag = dpg.generate_uuid()
        self.tree_tag = dpg.generate_uuid()
        self.on_node_selected = on_node_selected
        self.nodes: Dict[str, ComponentBase] = {}

    def create(self, parent: Optional[int] = None) -> int:
        """Create the nodes tree UI.

        Args:
            parent: Optional parent window ID

        Returns:
            int: The UI element tag
        """
        group_kwargs = {"tag": self.tag}
        if parent is not None:
            group_kwargs["parent"] = parent

        with dpg.group(**group_kwargs):
            with dpg.child_window(tag=self.tree_tag, height=200, width=-1):
                dpg.add_text("No nodes in graph", color=(150, 150, 150))

        return self.tag

    def update_nodes(self, nodes: Dict[str, ComponentBase]):
        """Update the tree with current nodes.

        Args:
            nodes: Dictionary mapping node_id to ComponentBase instance
        """
        self.nodes = nodes
        self._refresh_tree()

    def add_node(self, node_id: str, component: ComponentBase):
        """Add a single node to the tree.

        Args:
            node_id: Unique identifier for the node
            component: ComponentBase instance
        """
        self.nodes[node_id] = component
        self._refresh_tree()

    def remove_node(self, node_id: str):
        """Remove a node from the tree.

        Args:
            node_id: ID of the node to remove
        """
        if node_id in self.nodes:
            del self.nodes[node_id]
            self._refresh_tree()

    def _refresh_tree(self):
        """Refresh the tree view with current nodes."""
        # Clear existing tree
        dpg.delete_item(self.tree_tag, children_only=True)

        if not self.nodes:
            dpg.add_text(
                "No nodes in graph",
                color=(150, 150, 150),
                parent=self.tree_tag
            )
            return

        # Group nodes by category
        categories: Dict[str, List[tuple[str, ComponentBase]]] = {}
        for node_id, component in self.nodes.items():
            category = component.get_category()
            if category not in categories:
                categories[category] = []
            categories[category].append((node_id, component))

        # Create tree structure
        for category, nodes_list in sorted(categories.items()):
            with dpg.tree_node(
                label=f"{category} ({len(nodes_list)})",
                parent=self.tree_tag,
                default_open=True
            ):
                for node_id, component in sorted(nodes_list, key=lambda x: x[1].get_name()):
                    # Create node entry
                    with dpg.group(horizontal=True):
                        # Node icon based on state
                        state = component.state
                        if state.name == "IDLE":
                            icon_color = (100, 200, 100)
                        elif state.name == "RUNNING":
                            icon_color = (100, 150, 255)
                        elif state.name == "ERROR":
                            icon_color = (255, 100, 100)
                        else:
                            icon_color = (150, 150, 150)

                        dpg.add_text("●", color=icon_color)

                        # Node button
                        dpg.add_button(
                            label=f"{component.get_name()} [{node_id[:8]}]",
                            callback=lambda s, a, u: self._on_node_clicked(u),
                            user_data=node_id,
                            width=-1
                        )

    def _on_node_clicked(self, node_id: str):
        """Handle node selection in tree."""
        if self.on_node_selected:
            self.on_node_selected(node_id)
