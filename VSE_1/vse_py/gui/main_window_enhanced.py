"""Enhanced Main Window with sidebar and all UI components

Integrates:
- Node library/palette
- Enhanced node editor
- Sidebar with minimap, nodes tree, and inspector
"""

import dearpygui.dearpygui as dpg
from .node_library import NodeLibrary
from .enhanced_node_editor import EnhancedNodeEditor
from .minimap import Minimap
from .nodes_tree import NodesTree
from .node_inspector import NodeInspector


class MainWindowEnhanced:
    """Main application window with full UI layout."""

    def __init__(self):
        """Initialize the main window."""
        self.window_tag = dpg.generate_uuid()

        # Create UI components
        self.node_library = NodeLibrary(on_component_selected=self._on_component_selected)
        self.node_editor = EnhancedNodeEditor(
            on_node_selected=self._on_node_selected,
            on_nodes_changed=self._on_nodes_changed
        )
        self.minimap = Minimap(width=250, height=200)
        self.nodes_tree = NodesTree(on_node_selected=self._on_tree_node_selected)
        self.node_inspector = NodeInspector()

    def create(self) -> int:
        """Create the main window UI.

        Returns:
            int: The window tag
        """
        with dpg.window(
            tag=self.window_tag,
            label="VSE_1 - Visual Scripting Environment",
            width=-1,
            height=-1,
            no_close=True,
            no_collapse=True,
            menubar=True
        ):
            # Menu bar
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="New", callback=self._on_new)
                    dpg.add_menu_item(label="Open...", callback=self._on_open)
                    dpg.add_menu_item(label="Save", callback=self._on_save)
                    dpg.add_menu_item(label="Save As...", callback=self._on_save_as)
                    dpg.add_separator()
                    dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())

                with dpg.menu(label="Edit"):
                    dpg.add_menu_item(label="Clear All Nodes", callback=self._on_clear_all)

                with dpg.menu(label="View"):
                    dpg.add_menu_item(label="Reset Zoom", callback=self._on_reset_zoom)

                with dpg.menu(label="Help"):
                    dpg.add_menu_item(label="About", callback=self._on_about)

            # Main layout with splitters
            with dpg.group(horizontal=True):
                # Left sidebar - Node Library (250px wide)
                with dpg.child_window(width=250, height=-1):
                    self.node_library.create()

                # Center - Node Editor
                with dpg.child_window(width=-250, height=-1):
                    dpg.add_text("Node Editor", color=(200, 220, 255))
                    dpg.add_separator()
                    self.node_editor.create()

                # Right sidebar - Minimap, Tree, Inspector (250px wide)
                with dpg.child_window(width=250, height=-1):
                    # Minimap section
                    self.minimap.create()

                    dpg.add_spacer(height=10)

                    # Nodes tree section
                    with dpg.child_window(height=200):
                        self.nodes_tree.create()

                    dpg.add_spacer(height=10)

                    # Inspector section
                    with dpg.child_window(height=-1):
                        self.node_inspector.create()

        return self.window_tag

    def _on_component_selected(self, type_name: str):
        """Handle component selection from library.

        Args:
            type_name: Component type to add
        """
        # Add component at center of view
        # TODO: Get actual view center, for now use a default position
        import random
        pos = (random.randint(100, 400), random.randint(100, 400))
        self.node_editor.add_component(type_name, pos)

    def _on_node_selected(self, node_id: str, component):
        """Handle node selection in editor.

        Args:
            node_id: Selected node ID
            component: ComponentBase instance
        """
        self.node_inspector.inspect_node(node_id, component)

    def _on_tree_node_selected(self, node_id: str):
        """Handle node selection from tree.

        Args:
            node_id: Selected node ID
        """
        nodes = self.node_editor.get_all_nodes()
        if node_id in nodes:
            self.node_inspector.inspect_node(node_id, nodes[node_id])

    def _on_nodes_changed(self):
        """Handle nodes being added/removed/changed."""
        # Update nodes tree
        nodes = self.node_editor.get_all_nodes()
        self.nodes_tree.update_nodes(nodes)

        # Update minimap
        positions = self.node_editor.get_node_positions()
        self.minimap.update_nodes(positions)

    def _on_new(self):
        """Handle File > New."""
        self.node_editor.clear()
        self.node_inspector.clear()
        print("New graph created")

    def _on_open(self):
        """Handle File > Open."""
        print("Open not yet implemented")
        # TODO: Implement graph loading

    def _on_save(self):
        """Handle File > Save."""
        print("Save not yet implemented")
        # TODO: Implement graph saving

    def _on_save_as(self):
        """Handle File > Save As."""
        print("Save As not yet implemented")
        # TODO: Implement graph saving with file dialog

    def _on_clear_all(self):
        """Handle Edit > Clear All Nodes."""
        self.node_editor.clear()
        self.node_inspector.clear()
        print("All nodes cleared")

    def _on_reset_zoom(self):
        """Handle View > Reset Zoom."""
        print("Reset zoom not yet implemented")

    def _on_about(self):
        """Handle Help > About."""
        with dpg.window(label="About VSE_1", modal=True, show=True, width=400, height=200):
            dpg.add_text("VSE_1 - Visual Scripting Environment")
            dpg.add_text("Version 1.0")
            dpg.add_separator()
            dpg.add_text("A Python-based visual scripting system")
            dpg.add_text("with topic-based pub/sub architecture.")
            dpg.add_spacer(height=10)
            dpg.add_button(label="Close", callback=lambda: dpg.delete_item(dpg.get_active_window()))
