"""DearPyGui node editor wrapper"""
import dearpygui.dearpygui as dpg

class NodeEditor:
    """A wrapper for the DearPyGui node editor."""

    def __init__(self):
        """Initializes the NodeEditor."""
        self.tag = dpg.generate_uuid()

    def create(self):
        """Creates the node editor window and adds initial nodes."""
        with dpg.node_editor(tag=self.tag, label="Node Editor"):
            with dpg.node(label="Node 1"):
                with dpg.node_attribute(label="Input"):
                    dpg.add_input_float(label="Value", width=150)
                with dpg.node_attribute(label="Output", attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_text("Output")

            with dpg.node(label="Node 2"):
                with dpg.node_attribute(label="Input"):
                    dpg.add_input_float(label="Value", width=150)
                with dpg.node_attribute(label="Output", attribute_type=dpg.mvNode_Attr_Output):
                    dpg.add_text("Output")