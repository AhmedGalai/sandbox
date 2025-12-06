"""Comprehensive test of all VSE_1 components UI creation

Tests that all 12 components can be created in the node editor without errors.
"""

import dearpygui.dearpygui as dpg
from vse_py.registry.component_registry import ComponentRegistry
from vse_py.gui.enhanced_node_editor import EnhancedNodeEditor

# Import all components to trigger registration
from vse_py.components.math.add import AddComponent
from vse_py.components.math.subtract import SubtractComponent
from vse_py.components.math.multiply import MultiplyComponent
from vse_py.components.math.compare import CompareComponent
from vse_py.components.logic.and_gate import AndGateComponent
from vse_py.components.logic.or_gate import OrGateComponent
from vse_py.components.logic.xor_gate import XorGateComponent
from vse_py.components.logic.not_gate import NotGateComponent
from vse_py.components.composite import CompositeComponentRegistered
from vse_py.components.interface import InputInterface, OutputInterface, PassThrough

print("=" * 70)
print("VSE_1 Component UI Creation Test")
print("=" * 70)

# Create DearPyGui context
dpg.create_context()

# Create node editor
editor = EnhancedNodeEditor()

# Create a test window
with dpg.window(label="Test Window"):
    editor.create()

# Get all registered components
registry = ComponentRegistry.instance()
all_components = registry.get_all_components()

print(f"\nTesting {len(all_components)} components...")
print()

# Test each component
success_count = 0
fail_count = 0
errors = []

for i, comp_meta in enumerate(sorted(all_components, key=lambda c: c.display_name), 1):
    try:
        # Calculate position (grid layout)
        col = (i - 1) % 4
        row = (i - 1) // 4
        pos = (col * 200 + 100, row * 150 + 100)

        # Try to create component
        node_id = editor.add_component(comp_meta.type_name, pos)

        if node_id:
            print(f"✅ [{i:2d}/12] {comp_meta.display_name:25} - Created successfully")
            success_count += 1
        else:
            print(f"❌ [{i:2d}/12] {comp_meta.display_name:25} - Failed (returned None)")
            fail_count += 1
            errors.append(f"{comp_meta.display_name}: Returned None")

    except Exception as e:
        print(f"❌ [{i:2d}/12] {comp_meta.display_name:25} - Error: {e}")
        fail_count += 1
        errors.append(f"{comp_meta.display_name}: {e}")

# Cleanup
dpg.destroy_context()

# Print summary
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total components tested: {len(all_components)}")
print(f"✅ Successful: {success_count}")
print(f"❌ Failed: {fail_count}")

if errors:
    print("\nErrors encountered:")
    for error in errors:
        print(f"  - {error}")
else:
    print("\n🎉 All components created successfully!")

print("=" * 70)

if fail_count == 0:
    print("\n✅ ALL TESTS PASSED - VSE_1 UI is fully functional!")
else:
    print(f"\n⚠️  {fail_count} components failed to create")
    exit(1)
