# VSE Architecture Documentation

## System Overview

The Visual Scripting Environment (VSE) is built using a component-based architecture with a topic/data bus communication system. This design provides flexibility, modularity, and extensibility while maintaining clean separation of concerns.

## Design Principles

1. **Component-Based Design**: Everything is a component with well-defined interfaces
2. **Loose Coupling**: Components communicate through a publish-subscribe pattern
3. **Type Safety**: Strong typing with C++17 features and Qt's meta-object system
4. **Separation of Concerns**: Clear boundaries between logic, presentation, and data
5. **Extensibility**: Easy to add new components without modifying core system

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                   Presentation Layer                     │
│  (GUI: MainWindow, NodeView, NodeScene, PropertyPanel)  │
└────────────────────┬────────────────────────────────────┘
                     │ Qt Signals/Slots
┌────────────────────▼────────────────────────────────────┐
│                   Business Logic Layer                   │
│      (Node, Edge, Graph, ExecutionEngine)               │
└────────────────────┬────────────────────────────────────┘
                     │ Component Interface
┌────────────────────▼────────────────────────────────────┐
│                   Component Layer                        │
│    (LogicComponent, MathComponent, NetworkComponent)    │
└────────────────────┬────────────────────────────────────┘
                     │ Topic/Data Bus
┌────────────────────▼────────────────────────────────────┐
│                Communication Layer                       │
│          (Topic, DataBus, Message Queue)                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   Persistence Layer                      │
│        (JSONSerializer, FileManager)                     │
└─────────────────────────────────────────────────────────┘
```

## Core Modules

### 1. Core Module (`src/core/`, `include/core/`)

The foundation of the VSE system, providing base classes and fundamental data structures.

#### Key Classes

**Node**
- Base class for all nodes in the visual graph
- Manages input/output pins and their connections
- Handles execution logic and state
- Properties: ID, name, position, enabled state
- Methods: `execute()`, `addInput()`, `addOutput()`, `validate()`

**Edge**
- Represents connections between nodes
- Validates type compatibility
- Manages data flow direction
- Properties: source pin, destination pin, data type
- Methods: `isValid()`, `getSourceNode()`, `getDestinationNode()`

**Pin**
- Represents input/output connection points on nodes
- Type-safe data handling
- Supports multiple data types (int, float, string, bool, custom)
- Properties: name, type, direction (input/output), value
- Methods: `getValue()`, `setValue()`, `getType()`, `isConnected()`

**Graph**
- Container for nodes and edges
- Manages graph topology and execution order
- Provides graph traversal and validation
- Properties: nodes list, edges list, metadata
- Methods: `addNode()`, `removeNode()`, `addEdge()`, `validate()`, `execute()`

**Topic**
- Named communication channel for publish-subscribe pattern
- Type-erased value container using `std::any`
- Thread-safe access
- Properties: name, value, subscriber list
- Methods: `publish()`, `subscribe()`, `getValue()`, `hasSubscribers()`

**DataBus**
- Central message broker for inter-component communication
- Manages all topics
- Singleton pattern for global access
- Properties: topic registry, message queue
- Methods: `registerTopic()`, `publish()`, `subscribe()`, `unsubscribe()`

### 2. GUI Module (`src/gui/`, `include/gui/`)

Provides the visual interface built on Qt6 Widgets.

#### Key Classes

**MainWindow**
- Primary application window (QMainWindow)
- Contains menu bar, toolbar, dock panels
- Manages application-level actions
- Components: NodeView, PropertyPanel, ComponentLibrary, ConsolePanel
- Methods: `createActions()`, `createMenus()`, `loadGraph()`, `saveGraph()`

**NodeView**
- Custom QGraphicsView for displaying the node graph
- Handles user interactions (pan, zoom, selection)
- Manages visual feedback
- Methods: `addNodeVisual()`, `removeNodeVisual()`, `zoomIn()`, `zoomOut()`

**NodeScene**
- Custom QGraphicsScene managing visual node representations
- Handles node placement and edge routing
- Collision detection and snap-to-grid
- Methods: `drawBackground()`, `handleNodeMove()`, `handleEdgeCreation()`

**NodeWidget**
- QGraphicsItem representing a single node
- Custom painting for node appearance
- Interactive pins and title bar
- Methods: `paint()`, `boundingRect()`, `mousePressEvent()`, `contextMenuEvent()`

**EdgeWidget**
- QGraphicsItem for visual edge representation
- Bezier curve rendering between pins
- Animated data flow visualization
- Methods: `paint()`, `updatePath()`, `animate()`

**PropertyPanel**
- QDockWidget for editing node properties
- Dynamic form generation based on node type
- Real-time property updates
- Methods: `displayProperties()`, `updateProperty()`, `resetToDefaults()`

**ComponentLibrary**
- QDockWidget showing available components
- Drag-and-drop interface for adding nodes
- Component search and filtering
- Methods: `populateLibrary()`, `filterComponents()`, `createNode()`

### 3. Component Module (`src/components/`, `include/components/`)

Implements actual functionality as reusable components.

#### Base Class: Component

```cpp
class Component : public Node {
public:
    virtual void execute() = 0;
    virtual void initialize() = 0;
    virtual void cleanup() = 0;
    virtual QString getCategory() const = 0;
    virtual QString getDescription() const = 0;
};
```

#### Component Categories

**Logic Components** (`components/logic/`)
- `ANDGate`: Logical AND operation
- `ORGate`: Logical OR operation
- `NOTGate`: Logical NOT operation
- `XORGate`: Logical XOR operation
- `ConditionalGate`: If-then-else logic
- `CompareGate`: Comparison operations (==, !=, <, >, <=, >=)
- `FlipFlop`: State memory element
- `Timer`: Time-based triggers

**Math Components** (`components/math/`)
- `AddNode`: Addition
- `SubtractNode`: Subtraction
- `MultiplyNode`: Multiplication
- `DivideNode`: Division
- `ModuloNode`: Modulo operation
- `SinNode`: Sine function
- `CosNode`: Cosine function
- `TanNode`: Tangent function
- `PowerNode`: Exponentiation
- `SquareRootNode`: Square root
- `AbsoluteNode`: Absolute value
- `ClampNode`: Value clamping
- `MapRangeNode`: Linear interpolation between ranges

**Network Components** (`components/network/`)
- `TCPClientNode`: TCP client socket
- `TCPServerNode`: TCP server socket
- `UDPSendNode`: UDP datagram sender
- `UDPReceiveNode`: UDP datagram receiver
- `HTTPGetNode`: HTTP GET request
- `HTTPPostNode`: HTTP POST request
- `WebSocketNode`: WebSocket client

**I/O Components** (`components/io/`)
- `FileReadNode`: Read file contents
- `FileWriteNode`: Write to file
- `ConsoleOutNode`: Print to console
- `ConsoleInNode`: Read from console
- `EnvironmentVarNode`: Read environment variables
- `CommandExecuteNode`: Execute system commands
- `GPIONode`: GPIO pin control (platform-specific)

### 4. Serialization Module (`src/serialization/`, `include/serialization/`)

Handles saving and loading graphs to/from JSON format using nlohmann/json.

#### Key Classes

**JSONSerializer**
- Converts graph to JSON and vice versa
- Handles versioning and backward compatibility
- Methods: `serialize()`, `deserialize()`, `getVersion()`

**FileManager**
- File I/O operations
- Path validation and error handling
- Recent files management
- Methods: `saveGraph()`, `loadGraph()`, `getRecentFiles()`

#### JSON Format

```json
{
  "version": "1.0.0",
  "metadata": {
    "name": "Example Graph",
    "description": "A sample visual script",
    "created": "2025-11-26T12:00:00Z",
    "modified": "2025-11-26T12:30:00Z"
  },
  "nodes": [
    {
      "id": "node_001",
      "type": "AddNode",
      "position": {"x": 100, "y": 200},
      "properties": {
        "name": "Add Numbers"
      },
      "inputs": [
        {"name": "A", "type": "float", "value": 5.0},
        {"name": "B", "type": "float", "value": 3.0}
      ],
      "outputs": [
        {"name": "Result", "type": "float"}
      ]
    }
  ],
  "edges": [
    {
      "id": "edge_001",
      "source": {"node": "node_001", "pin": "Result"},
      "destination": {"node": "node_002", "pin": "Input"}
    }
  ]
}
```

### 5. Registry Module (`src/registry/`, `include/registry/`)

Manages component registration and factory pattern for creating components.

#### Key Classes

**ComponentRegistry**
- Singleton registry of all available components
- Factory pattern for component creation
- Plugin system support
- Methods: `registerComponent()`, `createComponent()`, `getCategories()`, `getComponentsInCategory()`

**ComponentMetadata**
- Stores component information for UI display
- Properties: name, category, description, icon, version
- Methods: `getName()`, `getCategory()`, `getIcon()`

## Topic/Data Bus Architecture

### Communication Pattern

The VSE uses a publish-subscribe pattern for loose coupling between components.

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Component  │──Publish─▶│   DataBus    │◀─Subscribe─│  Component  │
│      A      │         │              │         │      B      │
└─────────────┘         │   Topics:    │         └─────────────┘
                        │   - "temp"   │
                        │   - "speed"  │
                        │   - "status" │
                        └──────────────┘
```

### Usage Example

```cpp
// Component A publishes data
DataBus::instance().publish("temperature", 25.5f);

// Component B subscribes to data
DataBus::instance().subscribe("temperature", [](const std::any& value) {
    float temp = std::any_cast<float>(value);
    qDebug() << "Temperature updated:" << temp;
});
```

### Benefits

1. **Decoupling**: Components don't need to know about each other
2. **Flexibility**: Easy to add/remove subscribers
3. **Scalability**: Supports many-to-many communication
4. **Testability**: Easy to mock and test components in isolation

## Execution Model

### Graph Execution Flow

1. **Validation**: Check for cycles, type mismatches, disconnected nodes
2. **Topological Sort**: Determine execution order
3. **Initialization**: Call `initialize()` on all nodes
4. **Execution Loop**:
   - Execute nodes in topological order
   - Propagate data through edges
   - Handle errors and exceptions
5. **Cleanup**: Call `cleanup()` on all nodes

### Execution Modes

**Single-Step Mode**
- Execute one node at a time
- Useful for debugging
- Visual highlighting of current node

**Continuous Mode**
- Execute entire graph repeatedly
- Configurable execution rate
- Useful for simulations and real-time systems

**Event-Driven Mode**
- Execute only when inputs change
- Efficient for reactive systems
- Propagates changes through graph

## Class Hierarchy

```
QObject
├── Node (abstract)
│   ├── Component (abstract)
│   │   ├── LogicComponent (abstract)
│   │   │   ├── ANDGate
│   │   │   ├── ORGate
│   │   │   └── NOTGate
│   │   ├── MathComponent (abstract)
│   │   │   ├── AddNode
│   │   │   ├── SubtractNode
│   │   │   └── MultiplyNode
│   │   ├── NetworkComponent (abstract)
│   │   │   ├── TCPClientNode
│   │   │   └── TCPServerNode
│   │   └── IOComponent (abstract)
│   │       ├── FileReadNode
│   │       └── FileWriteNode
│   └── ControlFlowNode (abstract)
│       ├── SequenceNode
│       └── BranchNode
├── Edge
├── Graph
├── Topic
├── DataBus (singleton)
└── ComponentRegistry (singleton)

QGraphicsItem
├── NodeWidget
├── EdgeWidget
└── PinWidget

QMainWindow
└── MainWindow

QGraphicsView
└── NodeView

QGraphicsScene
└── NodeScene

QDockWidget
├── PropertyPanel
└── ComponentLibrary
```

## Thread Safety

### Strategy

- **GUI Thread**: All Qt widgets and graphics operations
- **Execution Thread**: Graph execution in separate QThread
- **Network Thread Pool**: Network operations in QThreadPool
- **Synchronization**: QMutex for DataBus topic access

### Critical Sections

- Topic value updates (DataBus)
- Graph topology modifications
- Component property changes during execution

## Error Handling

### Error Types

1. **Validation Errors**: Invalid graph structure, type mismatches
2. **Execution Errors**: Runtime errors in component logic
3. **I/O Errors**: File and network operation failures
4. **System Errors**: Resource allocation failures

### Error Propagation

- Exceptions converted to error signals
- Error nodes marked visually in red
- Error messages logged to console panel
- Execution halts on critical errors

## Extension Points

### Adding Custom Components

1. Inherit from appropriate base class (LogicComponent, MathComponent, etc.)
2. Implement required virtual methods
3. Register in ComponentRegistry
4. Optionally provide custom widget for specialized UI

### Adding Custom Data Types

1. Define type with Q_DECLARE_METATYPE
2. Implement serialization/deserialization
3. Register with type system
4. Update Pin to handle new type

### Plugin System (Future)

- Dynamic library loading
- Component discovery at runtime
- Versioning and dependency management
- Sandboxing for safety

## Performance Considerations

### Optimization Strategies

1. **Lazy Evaluation**: Execute only when inputs change
2. **Caching**: Cache computed values when possible
3. **Parallel Execution**: Execute independent branches in parallel
4. **Memory Pooling**: Reuse objects to reduce allocation overhead
5. **Dirty Flagging**: Track which nodes need re-execution

### Profiling Points

- Graph execution time
- Individual node execution time
- Memory usage per node
- Edge data transfer overhead

## Security Considerations

### Sandboxing

- Restrict file system access
- Limit network operations
- Validate all user inputs
- Prevent code injection in serialized graphs

### Best Practices

- Validate all external data
- Use safe parsing (nlohmann/json handles this)
- Sanitize file paths
- Limit execution time to prevent infinite loops
- Rate limiting for network operations

## Future Enhancements

1. **Visual Debugger**: Step-through debugging with breakpoints
2. **Performance Profiler**: Real-time performance analysis
3. **Version Control Integration**: Git integration for graphs
4. **Collaborative Editing**: Multi-user editing support
5. **Cloud Execution**: Remote graph execution
6. **Mobile Support**: Qt Quick/QML interface for tablets
7. **AI Integration**: Machine learning components
8. ** 3D Visualization**: 3D graph layout and visualization

## References

- Qt6 Documentation: https://doc.qt.io/qt-6/
- nlohmann/json: https://github.com/nlohmann/json
- Visual Scripting Best Practices: Industry standards and patterns
- Node-Based UI Patterns: Common UX patterns for node editors
