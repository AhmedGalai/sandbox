"""VSE_PY Main Application Entry Point"""
import dearpygui.dearpygui as dpg
from vse_py.gui.node_editor import NodeEditor

def main():
    """Initializes and runs the VSE_PY application."""
    dpg.create_context()

    node_editor = NodeEditor()

    dpg.create_viewport(title="VSE_PY - Visual Scripting Environment", width=1280, height=720)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    # Create the main window
    with dpg.window(label="VSE PY", tag="Primary Window"):
        node_editor.create()


    dpg.set_primary_window("Primary Window", True)

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

    dpg.destroy_context()

if __name__ == "__main__":
    main()