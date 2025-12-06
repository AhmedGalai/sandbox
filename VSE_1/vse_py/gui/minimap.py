"""Minimap component for the node editor

Provides a bird's-eye view of the node graph for easier navigation.
"""

import dearpygui.dearpygui as dpg
from typing import Dict, List, Tuple, Optional


class Minimap:
    """Minimap widget showing an overview of the node graph."""

    def __init__(self, width: int = 200, height: int = 150):
        """Initialize the minimap.

        Args:
            width: Width of the minimap in pixels
            height: Height of the minimap in pixels
        """
        self.tag = dpg.generate_uuid()
        self.canvas_tag = dpg.generate_uuid()
        self.width = width
        self.height = height
        self.nodes: Dict[str, Tuple[float, float]] = {}  # node_id -> (x, y)
        self.connections: List[Tuple[str, str]] = []  # (from_node_id, to_node_id)
        self.viewport_rect: Optional[Tuple[float, float, float, float]] = None  # (x, y, w, h)

    def create(self, parent: Optional[int] = None) -> int:
        """Create the minimap UI.

        Args:
            parent: Optional parent window ID

        Returns:
            int: The UI element tag
        """
        group_kwargs = {"tag": self.tag}
        if parent is not None:
            group_kwargs["parent"] = parent

        with dpg.group(**group_kwargs):
            with dpg.drawlist(
                tag=self.canvas_tag,
                width=self.width,
                height=self.height
            ):
                # Draw background
                dpg.draw_rectangle(
                    (0, 0),
                    (self.width, self.height),
                    fill=(20, 20, 30, 255),
                    color=(60, 60, 70, 255)
                )

        return self.tag

    def update_nodes(self, nodes: Dict[str, Tuple[float, float]]):
        """Update the node positions displayed in the minimap.

        Args:
            nodes: Dictionary mapping node_id to (x, y) position
        """
        self.nodes = nodes
        self._redraw()

    def update_connections(self, connections: List[Tuple[str, str]]):
        """Update the connections displayed in the minimap.

        Args:
            connections: List of (from_node_id, to_node_id) tuples
        """
        self.connections = connections
        self._redraw()

    def update_viewport(self, x: float, y: float, w: float, h: float):
        """Update the viewport rectangle showing the visible area.

        Args:
            x: X position of viewport
            y: Y position of viewport
            w: Width of viewport
            h: Height of viewport
        """
        self.viewport_rect = (x, y, w, h)
        self._redraw()

    def _redraw(self):
        """Redraw the minimap with current data."""
        # Clear existing drawings
        dpg.delete_item(self.canvas_tag, children_only=True)

        # Draw background
        dpg.draw_rectangle(
            (0, 0),
            (self.width, self.height),
            fill=(20, 20, 30, 255),
            color=(60, 60, 70, 255),
            parent=self.canvas_tag
        )

        if not self.nodes:
            dpg.draw_text(
                (self.width // 2 - 30, self.height // 2),
                "No nodes",
                color=(100, 100, 100),
                size=12,
                parent=self.canvas_tag
            )
            return

        # Calculate bounds of all nodes
        if self.nodes:
            min_x = min(x for x, y in self.nodes.values())
            max_x = max(x for x, y in self.nodes.values())
            min_y = min(y for x, y in self.nodes.values())
            max_y = max(y for x, y in self.nodes.values())

            # Add padding
            padding = 50
            min_x -= padding
            min_y -= padding
            max_x += padding
            max_y += padding

            # Calculate scale to fit all nodes in minimap
            graph_width = max_x - min_x
            graph_height = max_y - min_y

            if graph_width > 0 and graph_height > 0:
                scale_x = (self.width - 10) / graph_width
                scale_y = (self.height - 10) / graph_height
                scale = min(scale_x, scale_y)

                # Transform function to convert graph coords to minimap coords
                def transform(x, y):
                    return (
                        5 + (x - min_x) * scale,
                        5 + (y - min_y) * scale
                    )

                # Draw connections
                for from_id, to_id in self.connections:
                    if from_id in self.nodes and to_id in self.nodes:
                        from_pos = transform(*self.nodes[from_id])
                        to_pos = transform(*self.nodes[to_id])
                        dpg.draw_line(
                            from_pos,
                            to_pos,
                            color=(100, 150, 200, 200),
                            thickness=1,
                            parent=self.canvas_tag
                        )

                # Draw nodes
                for node_id, (x, y) in self.nodes.items():
                    pos = transform(x, y)
                    dpg.draw_circle(
                        pos,
                        radius=3,
                        fill=(150, 200, 255, 255),
                        color=(200, 220, 255, 255),
                        parent=self.canvas_tag
                    )

                # Draw viewport rectangle if provided
                if self.viewport_rect:
                    vx, vy, vw, vh = self.viewport_rect
                    top_left = transform(vx, vy)
                    bottom_right = transform(vx + vw, vy + vh)
                    dpg.draw_rectangle(
                        top_left,
                        bottom_right,
                        color=(255, 200, 100, 200),
                        thickness=2,
                        parent=self.canvas_tag
                    )
