"""VSE_1 Main Application Entry Point

Enhanced version with:
- Comprehensive node library
- Sidebar with minimap, nodes tree, and inspector
- Visual node connections with topic-based pub/sub
- Composite component support (Simulink-like subsystems)
"""

import dearpygui.dearpygui as dpg

# Import all components to trigger registration
from vse_py.components.math.add import AddComponent
from vse_py.components.math.subtract import SubtractComponent
from vse_py.components.math.multiply import MultiplyComponent
from vse_py.components.math.compare import CompareComponent
from vse_py.components.logic.and_gate import AndGateComponent
from vse_py.components.logic.or_gate import OrGateComponent
from vse_py.components.logic.xor_gate import XorGateComponent
from vse_py.components.logic.not_gate import NotGateComponent

# Import composite and interface components
from vse_py.components.composite import CompositeComponentRegistered
from vse_py.components.interface import InputInterface, OutputInterface, PassThrough

# Import enhanced GUI
from vse_py.gui.main_window_enhanced import MainWindowEnhanced


def main():
    """Initialize and run the VSE_1 application."""
    print("Starting VSE_1 - Visual Scripting Environment")
    print("=" * 50)

    # Create DearPyGui context
    dpg.create_context()

    # Create and show viewport
    dpg.create_viewport(
        title="VSE_1 - Visual Scripting Environment",
        width=1600,
        height=900,
        resizable=True
    )

    # Setup DearPyGui
    dpg.setup_dearpygui()

    # Create main window
    main_window = MainWindowEnhanced()
    main_window_tag = main_window.create()

    # Set as primary window
    dpg.set_primary_window(main_window_tag, True)

    # Show viewport
    dpg.show_viewport()

    print("\nVSE_1 is running!")
    print("Features:")
    print("  - Node Library: Browse and add components from the left panel")
    print("  - Node Editor: Create and connect nodes in the center panel")
    print("  - Minimap: View graph overview in the top-right")
    print("  - Nodes Tree: See all nodes organized by category")
    print("  - Inspector: View/edit selected node properties")
    print("  - Connections: Drag from output pins to input pins to connect")
    print("  - Composite Components: Create reusable subgraphs")
    print("\nPress Ctrl+C in terminal to exit")

    # Main render loop
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

    # Cleanup
    dpg.destroy_context()
    print("\nVSE_1 closed successfully")


if __name__ == "__main__":
    main()