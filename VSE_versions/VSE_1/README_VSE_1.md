# VSE_1 - Visual Scripting Environment

**Enhanced visual programming system with comprehensive UI and Simulink-like subsystems**

![Status](https://img.shields.io/badge/status-ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Components](https://img.shields.io/badge/components-12-orange)

## Overview

VSE_1 is an enhanced version of VSE_PY featuring a complete UI overhaul with:
- **Node Library** - Browse and add components with search/filtering
- **3-Panel Sidebar** - Minimap, nodes tree, and property inspector
- **Visual Node Editor** - Drag-and-drop node connections
- **Topic-Based Pub/Sub** - Robust data transfer architecture
- **Composite Components** - Create reusable subgraphs (like Simulink subsystems)
- **Interface Components** - Define subsystem boundaries

## Quick Start

```bash
cd VSE_1
pip3 install dearpygui
python3 main.py
```

## Features at a Glance

### Node Library (Left Panel)
- 📚 12 built-in components across 4 categories
- 🔍 Search by name, description, or tags
- 🏷️ Filter by category (Math, Logic, Interface, Container)
- ➕ Click to add components to graph

### Node Editor (Center Panel)
- 🎨 Visual node representation with color-coded categories
- 🔗 Drag from output pins to input pins to connect
- 📍 Drag nodes to position them
- 🗺️ Built-in minimap in bottom-right corner

### Sidebar (Right Panel)

**Minimap** _(Top)_
- Bird's-eye view of entire graph
- Auto-scales to fit all nodes
- Shows connections and viewport

**Nodes Tree** _(Middle)_
- Hierarchical view organized by category
- Color-coded status: 🟢 IDLE, 🔵 RUNNING, 🔴 ERROR, ⚪ DISABLED
- Click to select nodes

**Node Inspector** _(Bottom)_
- View/edit node properties
- All input/output pins displayed
- Interactive parameter editing
- Error messages when applicable

## Components Library

| Category | Components | Description |
|----------|-----------|-------------|
| **Math** | Add, Subtract, Multiply, Compare | Arithmetic and comparison operations |
| **Logic** | AND, OR, XOR, NOT | Boolean logic gates |
| **Interface** | Input, Output, PassThrough | Define subsystem boundaries |
| **Container** | Composite | Create reusable subgraphs |

## Advanced Features

### Topic-Based Pub/Sub
Every connection uses a dedicated topic for data transfer:
- Type-safe data validation
- Many-to-many connections supported
- Thread-safe operations
- Automatic subscription management

### Composite Components (Subsystems)
Create reusable subgraphs similar to Simulink subsystems:
```python
composite = CompositeComponent()
composite.add_internal_component(add_comp)
composite.add_internal_component(multiply_comp)
composite.connect_internal(add_comp.id, "Result", multiply_comp.id, "A")
composite.map_input("X", add_comp.id, "A")
composite.map_output("Z", multiply_comp.id, "Result")
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Main Window                            │
├──────────┬───────────────────────────┬──────────────────────┤
│  Node    │    Node Editor            │  Sidebar             │
│  Library │  ┌──────────────────┐     │  ┌───────────────┐   │
│          │  │                  │     │  │   Minimap     │   │
│  Search  │  │   [Node] [Node]  │     │  └───────────────┘   │
│  ─────   │  │      │       │   │     │  ┌───────────────┐   │
│          │  │   [Node]────┘    │     │  │  Nodes Tree   │   │
│  ┌───┐   │  │                  │     │  │  • Math (4)   │   │
│  │Add│   │  └──────────────────┘     │  │  • Logic (4)  │   │
│  └───┘   │                           │  └───────────────┘   │
│  ┌───┐   │                           │  ┌───────────────┐   │
│  │AND│   │                           │  │  Inspector    │   │
│  └───┘   │                           │  │  Name: Add    │   │
│    ...   │                           │  │  Pins: A, B   │   │
└──────────┴───────────────────────────┴──────────────────────┘
```

## System Requirements

- **Python:** 3.8 or later
- **Dependencies:** DearPyGui 2.1.1+
- **OS:** Linux, macOS, or Windows
- **Display:** Required for GUI (X11 for Linux/WSL)

## Testing

### Headless Test (No Display Required)
```bash
python3 test_components_only.py
```

Verifies all 12 components are registered and functional.

### Full Application Test
```bash
python3 main.py
```

Launches the complete GUI application.

## Documentation

- **[VSE_1_FEATURES.md](VSE_1_FEATURES.md)** - Detailed feature documentation
- **[INSTALLATION_AND_TESTING.md](INSTALLATION_AND_TESTING.md)** - Setup and testing guide

## Key Files

```
vse_py/
├── components/          # All component implementations
│   ├── math/           # Math operations
│   ├── logic/          # Logic gates
│   ├── composite.py    # Subsystem container
│   └── interface.py    # I/O interfaces
├── core/               # Core system classes
│   ├── component_base.py
│   ├── pin.py          # Enhanced with topic support
│   ├── topic_registry.py
│   ├── data_types.py
│   └── parameter.py
├── gui/                # All UI components
│   ├── main_window_enhanced.py
│   ├── node_library.py
│   ├── enhanced_node_editor.py
│   ├── minimap.py
│   ├── nodes_tree.py
│   └── node_inspector.py
└── registry/
    └── component_registry.py
```

## Usage Example

```python
# Import components
from vse_py.registry.component_registry import ComponentRegistry

# Get registry
registry = ComponentRegistry.instance()

# Create components
add = registry.create_component("AddComponent")
multiply = registry.create_component("MultiplyComponent")

# Components are automatically added to the node editor
# when selected from the UI library
```

## Development

### Adding New Components

1. Create component class inheriting from `ComponentBase`
2. Use `@register_component` decorator
3. Implement required methods:
   - `get_name()` - Component name
   - `get_category()` - Category
   - `get_color()` - RGB color tuple
   - `initialize()` - Add pins and parameters
   - `execute()` - Component logic

Example:
```python
from vse_py.registry.component_registry import register_component
from vse_py.core.component_base import ComponentBase

@register_component(
    type_name="MyComponent",
    display_name="My Custom Component",
    category="Custom",
    description="Does something awesome"
)
class MyComponent(ComponentBase):
    def get_name(self):
        return "My Component"

    def get_category(self):
        return "Custom"

    def get_color(self):
        return (100, 150, 200)  # RGB

    def initialize(self):
        self.add_input_pin("Input", DataType.FLOAT)
        self.add_output_pin("Output", DataType.FLOAT)

    def execute(self):
        # Component logic here
        pass
```

## Roadmap

Future enhancements:
- [ ] Graph serialization/deserialization (save/load)
- [ ] Execution engine with step-through debugging
- [ ] Undo/redo functionality
- [ ] Copy/paste nodes
- [ ] Multi-graph support (tabs)
- [ ] Performance profiling tools
- [ ] Custom component creation from UI
- [ ] Graph validation and error checking

## License

Same as VSE_PY base project.

## Acknowledgments

Built on top of VSE_PY with significant enhancements:
- Complete UI redesign with DearPyGui
- Topic-based pub/sub architecture
- Composite component system
- Enhanced pin system with topic integration

---

**Ready to use!** All features implemented and tested.

For questions or issues, see [INSTALLATION_AND_TESTING.md](INSTALLATION_AND_TESTING.md).
