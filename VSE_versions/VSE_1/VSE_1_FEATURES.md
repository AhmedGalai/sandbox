# VSE_1 - Enhanced Visual Scripting Environment

VSE_1 is the enhanced version of VSE_PY with a complete UI overhaul and advanced features for visual programming.

## New Features

### 1. **Comprehensive Node Library**
   - **Location:** Left sidebar
   - **File:** `vse_py/gui/node_library.py`
   - **Features:**
     - Browse all available components organized by category
     - Search components by name, description, or tags
     - Filter components by category (Math, Logic, Interface, Container)
     - Click to add components to the graph
   - **Categories:**
     - **Math:** Add, Subtract, Multiply, Compare
     - **Logic:** AND, OR, XOR, NOT gates
     - **Interface:** Input/Output interfaces, Pass Through
     - **Container:** Composite components (subsystems)

### 2. **Enhanced Node Editor**
   - **File:** `vse_py/gui/enhanced_node_editor.py`
   - **Features:**
     - Visual representation of component nodes
     - Drag-and-drop node positioning
     - Pin-based visual connections
     - Integrated with topic-based pub/sub system
     - Built-in minimap (top-right corner)
     - Node selection and highlighting

### 3. **Sidebar with Three Sections**

   #### a) **Minimap** (Top-right)
   - **File:** `vse_py/gui/minimap.py`
   - **Features:**
     - Bird's-eye view of the entire graph
     - Shows all nodes as dots
     - Shows connections as lines
     - Displays viewport rectangle (visible area)
     - Automatically scales to fit all nodes

   #### b) **Nodes Tree** (Middle-right)
   - **File:** `vse_py/gui/nodes_tree.py`
   - **Features:**
     - Hierarchical view of all nodes
     - Organized by category with expandable sections
     - Shows node count per category
     - Color-coded status indicators:
       - 🟢 Green: IDLE
       - 🔵 Blue: RUNNING
       - 🔴 Red: ERROR
       - ⚪ Gray: DISABLED
     - Click to select and inspect nodes

   #### c) **Node Inspector** (Bottom-right)
   - **File:** `vse_py/gui/node_inspector.py`
   - **Features:**
     - View and edit properties of selected node
     - Displays node information (name, category, ID, state)
     - Shows all input and output pins with types
     - Interactive parameter editing:
       - Integer parameters: spinbox
       - Float parameters: float input
       - String parameters: text input
       - Boolean parameters: checkbox
     - Error message display when node is in ERROR state

### 4. **Topic-Based Pub/Sub Connections**
   - **Integration:** Enhanced in `vse_py/core/pin.py`
   - **Features:**
     - Connections use topics for data transfer
     - Support for many-to-many data distribution
     - Type-safe data transfer with DataVariant
     - Automatic topic creation and management
     - Callbacks for data reception
   - **New Pin Methods:**
     - `OutputPin.connect_to_topic(topic_name)` - Connect output to topic
     - `OutputPin.transmit_data(data)` - Publishes to both pins and topics
     - `InputPin.receive_data(data)` - Receives data from topic subscriptions
     - `InputPin.has_data()` - Check if pin has received data

### 5. **Composite Components (Subsystems)**
   - **File:** `vse_py/components/composite.py`
   - **Features:**
     - Create reusable subgraphs (like Simulink subsystems)
     - Contains multiple internal components
     - Internal connections between components
     - Map external inputs to internal component inputs
     - Map internal component outputs to external outputs
     - Serialization support for saving/loading
   - **Methods:**
     - `add_internal_component(component)` - Add component to subgraph
     - `connect_internal(from_id, from_pin, to_id, to_pin)` - Connect internal components
     - `map_input(external_pin, internal_id, internal_pin)` - Map external input
     - `map_output(external_pin, internal_id, internal_pin)` - Map external output

### 6. **Interface Components**
   - **File:** `vse_py/components/interface.py`
   - **Purpose:** Define boundaries of composite components

   #### **InputInterface Component**
   - Creates an external input on a composite component
   - Routes data from outside into the subgraph
   - Similar to Simulink Inport blocks
   - Color: Cyan (0, 188, 212)

   #### **OutputInterface Component**
   - Creates an external output on a composite component
   - Routes data from inside the subgraph to outside
   - Similar to Simulink Outport blocks
   - Color: Orange (255, 152, 0)

   #### **PassThrough Component**
   - Simple utility component for routing
   - Passes data from input to output unchanged
   - Useful for testing and debugging connections
   - Color: Gray (158, 158, 158)

## Architecture

### File Structure
```
VSE_1/
├── main.py                          # Enhanced entry point
├── vse_py/
│   ├── components/
│   │   ├── composite.py             # Composite component (subsystems)
│   │   ├── interface.py             # Interface components
│   │   ├── math/                    # Math components
│   │   └── logic/                   # Logic components
│   ├── core/
│   │   ├── component_base.py        # Base component class
│   │   ├── pin.py                   # Enhanced pin system with topics
│   │   ├── topic_registry.py        # Pub/sub topic system
│   │   ├── data_types.py            # Data type system
│   │   └── parameter.py             # Parameter system
│   ├── gui/
│   │   ├── main_window_enhanced.py  # Main window with sidebars
│   │   ├── node_library.py          # Component library/palette
│   │   ├── enhanced_node_editor.py  # Enhanced node editor
│   │   ├── minimap.py               # Graph minimap
│   │   ├── nodes_tree.py            # Hierarchical nodes view
│   │   └── node_inspector.py        # Property inspector
│   └── registry/
│       └── component_registry.py    # Component registration system
```

### Data Flow
1. **Component Selection:** User selects component from Node Library
2. **Node Creation:** Component instantiated and added to editor
3. **Connection:** User drags from output pin to input pin
4. **Topic Creation:** System creates topic for the connection
5. **Subscription:** Input pin subscribes to topic
6. **Data Transfer:** Output pin publishes data to topic
7. **Reception:** Input pin receives data via topic callback

## Usage

### Running VSE_1
```bash
cd VSE_1
python3 main.py
```

### Creating a Graph
1. **Add Nodes:** Click components in the Node Library to add them
2. **Position Nodes:** Drag nodes to arrange them
3. **Connect Nodes:** Drag from output pins to input pins
4. **Inspect Nodes:** Click nodes to view/edit properties in Inspector
5. **View Graph:** Use Minimap to see overall structure
6. **Navigate:** Use Nodes Tree to quickly find and select nodes

### Creating a Composite Component (Subsystem)
1. Add a Composite component from the Container category
2. Define inputs using InputInterface components
3. Add internal logic components (math, logic, etc.)
4. Connect internal components
5. Define outputs using OutputInterface components
6. Map external inputs/outputs to internal component pins

## Component Summary

### Registered Components (12 total)

| Component | Category | Description |
|-----------|----------|-------------|
| Add | Math | Adds two float values (A + B) |
| Subtract | Math | Subtracts two float values (A - B) |
| Multiply | Math | Multiplies two float values (A * B) |
| Compare | Math | Compares two float values using configurable operations |
| AND Gate | Logic | Logical AND operation |
| OR Gate | Logic | Logical OR operation |
| XOR Gate | Logic | Logical XOR operation |
| NOT Gate | Logic | Logical NOT operation (inverts input) |
| Input Interface | Interface | Defines input to composite component |
| Output Interface | Interface | Defines output from composite component |
| Pass Through | Interface | Passes data unchanged from input to output |
| Composite (Subsystem) | Container | Container for reusable subgraphs |

## Technical Details

### Topic-Based Connections
- Each connection creates a unique topic: `{from_node_id}_{from_pin}_to_{to_node_id}_{to_pin}`
- Topics enforce type compatibility
- Support for thread-safe pub/sub
- Automatic cleanup on connection deletion

### Pin System Enhancements
- **InputPin** now supports:
  - `has_data()` - Check if data has been received
  - `status` property - Connection status
  - Topic-based data reception

- **OutputPin** now supports:
  - `connect_to_topic(topic_name)` - Connect to topic
  - Automatic topic publishing on `transmit_data()`
  - Multiple topic connections

### UI Layout
- **Left Sidebar (250px):** Node Library
- **Center Area (flexible):** Enhanced Node Editor
- **Right Sidebar (250px):**
  - Minimap (200px height)
  - Nodes Tree (200px height)
  - Inspector (remaining height)

## Future Enhancements

Potential future improvements:
- Graph serialization/deserialization (save/load)
- Execution engine for running graphs
- Debugging tools (breakpoints, step through)
- Custom component creation from UI
- Graph templates and examples
- Performance profiling and optimization
- Multi-graph support (tabs)
- Undo/redo functionality
- Copy/paste nodes
- Graph validation and error checking

## Dependencies

- **Python 3.8+**
- **DearPyGui 2.1.1+** - GUI framework
- **Standard library:** uuid, threading, dataclasses, abc, enum, typing

## License

Same as VSE_PY base project.
