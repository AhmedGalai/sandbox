"""Node Library / Component Palette for VSE_1

This module provides a comprehensive UI for browsing and adding components
to the node editor. It organizes components by category and provides
search and filtering capabilities.
"""

import dearpygui.dearpygui as dpg
from typing import Dict, List, Optional, Callable
from ..registry.component_registry import ComponentRegistry, ComponentMetadata


class NodeLibrary:
    """Component library UI for browsing and adding nodes."""

    def __init__(self, on_component_selected: Optional[Callable[[str], None]] = None):
        """Initialize the node library.

        Args:
            on_component_selected: Callback when a component is selected
                                 Called with the component type_name
        """
        self.registry = ComponentRegistry.instance()
        self.on_component_selected = on_component_selected
        self.tag = dpg.generate_uuid()
        self.search_tag = dpg.generate_uuid()
        self.categories_tag = dpg.generate_uuid()
        self.search_text = ""
        self.selected_category = "All"

    def create(self, parent: Optional[int] = None) -> int:
        """Create the node library UI.

        Args:
            parent: Optional parent window ID

        Returns:
            int: The UI element tag
        """
        group_kwargs = {"tag": self.tag}
        if parent is not None:
            group_kwargs["parent"] = parent

        with dpg.group(**group_kwargs):
            # Search box
            dpg.add_input_text(
                tag=self.search_tag,
                hint="Search components...",
                callback=self._on_search_changed,
                width=-1
            )

            dpg.add_separator()

            # Category filter buttons
            with dpg.group():
                dpg.add_text("Categories:", color=(200, 200, 200))

                # Get all categories
                categories = ["All"] + self.registry.get_all_categories()

                for category in categories:
                    dpg.add_button(
                        label=category,
                        callback=lambda s, a, u: self._on_category_selected(u),
                        user_data=category,
                        width=-1
                    )

            dpg.add_separator()

            # Components list
            with dpg.child_window(tag=self.categories_tag, height=-1, width=-1):
                self._refresh_component_list()

        return self.tag

    def _on_search_changed(self, sender, app_data):
        """Handle search text changes."""
        self.search_text = app_data.lower()
        self._refresh_component_list()

    def _on_category_selected(self, category: str):
        """Handle category selection."""
        self.selected_category = category
        self._refresh_component_list()

    def _refresh_component_list(self):
        """Refresh the displayed component list based on filters."""
        # Clear existing items
        dpg.delete_item(self.categories_tag, children_only=True)

        # Get filtered components
        if self.selected_category == "All":
            components = self.registry.get_all_components()
        else:
            components = self.registry.get_components_by_category(self.selected_category)

        # Apply search filter
        if self.search_text:
            components = [
                c for c in components
                if (self.search_text in c.display_name.lower() or
                    self.search_text in c.description.lower() or
                    any(self.search_text in tag.lower() for tag in c.tags))
            ]

        # Display components grouped by category
        current_category = None
        for metadata in components:
            # Add category header if needed
            if metadata.category != current_category:
                current_category = metadata.category
                dpg.add_text(
                    f"  {current_category}  ",
                    parent=self.categories_tag,
                    color=(150, 200, 255)
                )
                dpg.add_separator(parent=self.categories_tag)

            # Add component button
            with dpg.group(horizontal=True, parent=self.categories_tag):
                dpg.add_button(
                    label=metadata.display_name,
                    callback=lambda s, a, u: self._on_component_clicked(u),
                    user_data=metadata.type_name,
                    width=150
                )
                dpg.add_text(
                    metadata.description[:30] + "..." if len(metadata.description) > 30 else metadata.description,
                    color=(180, 180, 180)
                )

    def _on_component_clicked(self, type_name: str):
        """Handle component button click."""
        if self.on_component_selected:
            self.on_component_selected(type_name)
