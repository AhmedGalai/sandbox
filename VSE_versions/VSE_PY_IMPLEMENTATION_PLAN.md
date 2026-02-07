# VSE_PY Implementation Plan: Python Visual Scripting Environment

## Strategic Plan: Porting VSE from C++/Qt6 to Python/DearPyGui

---

## Problem Summary

Create a Python version of the VSE (Visual Scripting Environment) C++ application using dearpygui instead of Qt6, maintaining the same architecture, design patterns, and functionality while adopting Python-idiomatic implementations.

---

## Current State Assessment

**Analyzed C++ VSE Architecture:**
- Component-based system with 3 component types (Publisher, Subscriber, Processor)
- Pin system with type safety (Boolean, Integer, Float, String, JSON)
- Parameter system for configuration (Int, Float, String, Bool, FilePath, Color)
- ExecutionEngine with topological sorting
- Topic/DataBus publish-subscribe pattern
- Connection system linking pins
- ComponentRegistry with factory pattern
- Qt6-based GUI with node editor
- JSON-based serialization (.vse files)

**Target:** Python implementation using dearpygui's node editor capabilities while maintaining architectural integrity.

---

## Plan Structure

### 1. Project Setup and Foundation
**Rationale**: Establish proper project structure, dependencies, and development environment
**Complexity**: Simple

#### 1.1 Create Project Directory Structure
- **Action**: Create organized folder hierarchy for VSE_PY
- **Success Criteria**: All directories exist and follow Python best practices
- **Effort**: Low
- **Dependencies**: None
- **Considerations**: Use standard Python package layout with proper __init__.py files

**Directory Structure:**
```
VSE_PY/
├── vse_py/                      # Main package
│   ├── __init__.py
│   ├── core/                    # Core system classes
│   │   ├── __init__.py
│   │   ├── component_base.py   # ComponentBase abstract class
│   │   ├── pin.py              # Pin, InputPin, OutputPin classes
│   │   ├── parameter.py        # Parameter hierarchy
│   │   ├── data_types.py       # DataType enum and DataVariant
│   │   ├── connection.py       # Connection and ConnectionManager
│   │   ├── topic_registry.py   # Topic and TopicRegistry
│   │   ├── execution_engine.py # ExecutionEngine
│   │   └── execution_context.py # ExecutionContext
│   ├── components/              # Component implementations
│   │   ├── __init__.py
│   │   ├── publisher.py        # PublisherComponent base
│   │   ├── subscriber.py       # SubscriberComponent base
│   │   ├── processor.py        # ProcessorComponent base
│   │   ├── math/               # Math components
│   │   │   ├── __init__.py
│   │   │   ├── add.py
│   │   │   ├── subtract.py
│   │   │   ├── multiply.py
│   │   │   └── compare.py
│   │   └── logic/              # Logic components
│   │       ├── __init__.py
│   │       ├── and_gate.py
│   │       ├── or_gate.py
│   │       ├── not_gate.py
│   │       └── xor_gate.py
│   ├── registry/                # Component registry
│   │   ├── __init__.py
│   │   └── component_registry.py
│   ├── serialization/           # Save/load functionality
│   │   ├── __init__.py
│   │   └── project_serializer.py
│   └── gui/                     # GUI implementation
│       ├── __init__.py
│       ├── main_window.py      # Main application window
│       ├── node_editor.py      # DearPyGui node editor wrapper
│       ├── inspector.py        # Component inspector panel
│       ├── component_palette.py # Component selection palette
│       └── execution_control.py # Execution control widget
├── examples/                    # Example projects
│   ├── simple_math.py
│   ├── logic_circuit.py
│   └── topic_system.py
├── tests/                       # Unit tests
│   ├── __init__.py
│   ├── test_core/
│   ├── test_components/
│   └── test_serialization/
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── README.md                    # Documentation
└── main.py                      # Application entry point
```

#### 1.2 Setup Dependencies and Environment
- **Action**: Create requirements.txt and virtual environment setup
- **Success Criteria**: All dependencies install successfully
- **Effort**: Low
- **Dependencies**: 1.1
- **Considerations**: Pin versions for reproducibility

**requirements.txt:**
```
dearpygui>=1.10.0
typing-extensions>=4.8.0
dataclasses-json>=0.6.0
```

#### 1.3 Create Base Package Infrastructure
- **Action**: Create __init__.py files and package imports
- **Success Criteria**: Package can be imported and basic version info exposed
- **Effort**: Low
- **Dependencies**: 1.1, 1.2
- **Considerations**: Export main classes from package level for easier imports

---

### 2. Core Data Types and Type System
**Rationale**: Foundation for all data flow and type checking in the system
**Complexity**: Moderate

#### 2.1 Implement DataType Enum and Type Utilities
- **Action**: Create data_types.py with DataType enum and conversion functions
- **Success Criteria**: All data types defined with string conversion both ways
- **Effort**: Low
- **Dependencies**: 1.3
- **Considerations**: Use Python Enum for type safety

**Implementation Details:**
```python
from enum import Enum, auto
from typing import Any, Union

class DataType(Enum):
    """Pin data type enumeration"""
    NULL = auto()
    BOOLEAN = auto()
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    JSON = auto()
    ANY = auto()

def data_type_to_string(dtype: DataType) -> str:
    """Convert DataType to string"""
    return dtype.name.lower()

def string_to_data_type(s: str) -> DataType:
    """Convert string to DataType"""
    return DataType[s.upper()]

def is_type_compatible(source: DataType, dest: DataType) -> bool:
    """Check if source type can connect to destination type"""
    if dest == DataType.ANY:
        return True
    if source == DataType.ANY:
        return True
    return source == dest
```

#### 2.2 Implement DataVariant Class
- **Action**: Create type-safe data container with conversion methods
- **Success Criteria**: Can store and retrieve all data types with type checking
- **Effort**: Medium
- **Dependencies**: 2.1
- **Considerations**: Use Python's dynamic typing but add runtime type checks

**Implementation Details:**
```python
from typing import Any, Optional
import json

class DataVariant:
    """Type-safe data container for pin values"""

    def __init__(self, value: Any = None, dtype: Optional[DataType] = None):
        self._value = value
        self._dtype = dtype or self._infer_type(value)

    @staticmethod
    def _infer_type(value: Any) -> DataType:
        """Infer DataType from Python value"""
        if value is None:
            return DataType.NULL
        elif isinstance(value, bool):
            return DataType.BOOLEAN
        elif isinstance(value, int):
            return DataType.INTEGER
        elif isinstance(value, float):
            return DataType.FLOAT
        elif isinstance(value, str):
            return DataType.STRING
        elif isinstance(value, (dict, list)):
            return DataType.JSON
        else:
            return DataType.ANY

    @property
    def value(self) -> Any:
        return self._value

    @property
    def dtype(self) -> DataType:
        return self._dtype

    def to_bool(self) -> bool:
        """Convert to boolean with type checking"""
        if self._dtype == DataType.BOOLEAN:
            return self._value
        return bool(self._value)

    def to_int(self) -> int:
        """Convert to integer"""
        return int(self._value)

    def to_float(self) -> float:
        """Convert to float"""
        return float(self._value)

    def to_string(self) -> str:
        """Convert to string"""
        return str(self._value)

    def to_json(self) -> dict:
        """Serialize to JSON-compatible dict"""
        return {
            "type": data_type_to_string(self._dtype),
            "value": self._value
        }

    @classmethod
    def from_json(cls, data: dict) -> 'DataVariant':
        """Deserialize from JSON dict"""
        dtype = string_to_data_type(data["type"])
        return cls(data["value"], dtype)
```

---

### 3. Pin System Implementation
**Rationale**: Pins are the connection points for data flow between components
**Complexity**: Moderate

#### 3.1 Implement Base Pin Class
- **Action**: Create abstract Pin class with common functionality
- **Success Criteria**: Pin class can store name, ID, type, and data type
- **Effort**: Low
- **Dependencies**: 2.2
- **Considerations**: Use ABC (Abstract Base Class) for proper abstraction

#### 3.2 Implement InputPin Class
- **Action**: Create InputPin with single connection and data callback support
- **Success Criteria**: Can connect to OutputPin, receive data, trigger callbacks
- **Effort**: Medium
- **Dependencies**: 3.1
- **Considerations**: Support data callbacks for reactive processing

**Implementation Details:**
```python
from abc import ABC, abstractmethod
from typing import Optional, Callable, List
import uuid

class Pin(ABC):
    """Base class for component pins"""

    def __init__(self, name: str, dtype: DataType):
        self._id = str(uuid.uuid4())
        self._name = name
        self._dtype = dtype

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def dtype(self) -> DataType:
        return self._dtype

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if pin is connected"""
        pass

class InputPin(Pin):
    """Input pin receives data from a single output pin"""

    def __init__(self, name: str, dtype: DataType):
        super().__init__(name, dtype)
        self._connected_pin: Optional['OutputPin'] = None
        self._data = DataVariant(None, DataType.NULL)
        self._callback: Optional[Callable[[DataVariant], None]] = None

    def is_connected(self) -> bool:
        return self._connected_pin is not None

    def connect_to(self, output_pin: 'OutputPin') -> bool:
        """Connect to an output pin"""
        if not is_type_compatible(output_pin.dtype, self._dtype):
            return False
        self._connected_pin = output_pin
        return True

    def disconnect(self):
        """Disconnect from output pin"""
        self._connected_pin = None

    def receive_data(self, data: DataVariant):
        """Receive data on this pin"""
        self._data = data
        if self._callback:
            self._callback(data)

    @property
    def data(self) -> DataVariant:
        return self._data

    def set_callback(self, callback: Callable[[DataVariant], None]):
        """Set data reception callback"""
        self._callback = callback
```

#### 3.3 Implement OutputPin Class
- **Action**: Create OutputPin with multiple connections and broadcast capability
- **Success Criteria**: Can connect to multiple InputPins, transmit data to all
- **Effort**: Medium
- **Dependencies**: 3.1
- **Considerations**: Handle multiple connections efficiently

**Implementation Details:**
```python
class OutputPin(Pin):
    """Output pin transmits data to multiple input pins"""

    def __init__(self, name: str, dtype: DataType):
        super().__init__(name, dtype)
        self._connected_pins: List[InputPin] = []
        self._data = DataVariant(None, DataType.NULL)

    def is_connected(self) -> bool:
        return len(self._connected_pins) > 0

    def add_connection(self, input_pin: InputPin) -> bool:
        """Add connection to an input pin"""
        if not is_type_compatible(self._dtype, input_pin.dtype):
            return False
        if input_pin not in self._connected_pins:
            self._connected_pins.append(input_pin)
        return True

    def remove_connection(self, input_pin: InputPin):
        """Remove connection to an input pin"""
        if input_pin in self._connected_pins:
            self._connected_pins.remove(input_pin)

    def disconnect_all(self):
        """Disconnect all input pins"""
        self._connected_pins.clear()

    def transmit_data(self, data: DataVariant):
        """Transmit data to all connected input pins"""
        self._data = data
        for pin in self._connected_pins:
            pin.receive_data(data)

    @property
    def data(self) -> DataVariant:
        return self._data

    @property
    def connected_pins(self) -> List[InputPin]:
        return self._connected_pins.copy()
```

---

### 4. Parameter System Implementation
**Rationale**: Parameters allow user configuration of component behavior
**Complexity**: Moderate

#### 4.1 Implement Base Parameter Class
- **Action**: Create abstract Parameter base with name, description, value
- **Success Criteria**: Parameter interface defined with JSON serialization
- **Effort**: Low
- **Dependencies**: 1.3
- **Considerations**: Use property decorators for Pythonic API

#### 4.2 Implement Concrete Parameter Types
- **Action**: Create IntParameter, FloatParameter, StringParameter, BoolParameter
- **Success Criteria**: Each type handles validation, min/max, defaults
- **Effort**: Medium
- **Dependencies**: 4.1
- **Considerations**: Use type hints and dataclasses where appropriate

**Implementation Details:**
```python
from abc import ABC, abstractmethod
from typing import Any, Optional
from dataclasses import dataclass

class Parameter(ABC):
    """Base class for component parameters"""

    def __init__(self, name: str, description: str = ""):
        self._name = name
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @abstractmethod
    def get_value(self) -> Any:
        """Get parameter value"""
        pass

    @abstractmethod
    def set_value(self, value: Any):
        """Set parameter value"""
        pass

    @abstractmethod
    def to_json(self) -> dict:
        """Serialize to JSON"""
        pass

    @abstractmethod
    def from_json(self, data: dict):
        """Deserialize from JSON"""
        pass

class IntParameter(Parameter):
    """Integer parameter with min/max validation"""

    def __init__(self, name: str, default: int = 0,
                 min_val: int = -2**31, max_val: int = 2**31-1,
                 description: str = ""):
        super().__init__(name, description)
        self._value = default
        self._min = min_val
        self._max = max_val

    def get_value(self) -> int:
        return self._value

    def set_value(self, value: Any):
        int_val = int(value)
        self._value = max(self._min, min(self._max, int_val))

    @property
    def min_value(self) -> int:
        return self._min

    @property
    def max_value(self) -> int:
        return self._max

    def to_json(self) -> dict:
        return {
            "type": "int",
            "name": self._name,
            "value": self._value,
            "min": self._min,
            "max": self._max,
            "description": self._description
        }

    def from_json(self, data: dict):
        self._value = data["value"]
        self._min = data.get("min", self._min)
        self._max = data.get("max", self._max)

# Similar implementations for FloatParameter, StringParameter,
# BoolParameter, FilePathParameter, ColorParameter
```

---

### 5. Component Base Architecture
**Rationale**: ComponentBase is the foundation for all components in the system
**Complexity**: Complex

#### 5.1 Implement ComponentBase Abstract Class
- **Action**: Create ComponentBase with pins, parameters, state management
- **Success Criteria**: Can add/get pins and parameters, track state, serialize
- **Effort**: High
- **Dependencies**: 3.3, 4.2
- **Considerations**: Use ABC for abstract methods, signals pattern for events

**Implementation Details:**
```python
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Optional, Dict, Callable
import uuid

class ComponentState(Enum):
    """Component execution state"""
    IDLE = auto()
    RUNNING = auto()
    ERROR = auto()
    DISABLED = auto()

class ComponentBase(ABC):
    """Abstract base class for all components"""

    def __init__(self):
        self._id = str(uuid.uuid4())
        self._state = ComponentState.IDLE
        self._input_pins: List[InputPin] = []
        self._output_pins: List[OutputPin] = []
        self._parameters: List[Parameter] = []
        self._state_callbacks: List[Callable[[ComponentState], None]] = []
        self._error_callbacks: List[Callable[[str], None]] = []
        self.initialize()

    @property
    def id(self) -> str:
        return self._id

    def set_id(self, comp_id: str):
        """Set component ID (for deserialization)"""
        self._id = comp_id

    @abstractmethod
    def get_name(self) -> str:
        """Get component name"""
        pass

    @abstractmethod
    def get_category(self) -> str:
        """Get component category"""
        pass

    @abstractmethod
    def get_color(self) -> tuple:
        """Get component color (R, G, B)"""
        pass

    def get_description(self) -> str:
        """Get component description"""
        return ""

    @abstractmethod
    def execute(self):
        """Execute component logic"""
        pass

    @property
    def state(self) -> ComponentState:
        return self._state

    def set_state(self, state: ComponentState):
        """Set component state and notify callbacks"""
        self._state = state
        for callback in self._state_callbacks:
            callback(state)

    # Pin management
    def add_input_pin(self, name: str, dtype: DataType) -> InputPin:
        """Add an input pin"""
        pin = InputPin(name, dtype)
        self._input_pins.append(pin)
        return pin

    def add_output_pin(self, name: str, dtype: DataType) -> OutputPin:
        """Add an output pin"""
        pin = OutputPin(name, dtype)
        self._output_pins.append(pin)
        return pin

    def get_input_pin(self, name: str) -> Optional[InputPin]:
        """Get input pin by name"""
        for pin in self._input_pins:
            if pin.name == name:
                return pin
        return None

    def get_output_pin(self, name: str) -> Optional[OutputPin]:
        """Get output pin by name"""
        for pin in self._output_pins:
            if pin.name == name:
                return pin
        return None

    @property
    def input_pins(self) -> List[InputPin]:
        return self._input_pins.copy()

    @property
    def output_pins(self) -> List[OutputPin]:
        return self._output_pins.copy()

    # Parameter management
    def add_parameter(self, param: Parameter):
        """Add a parameter"""
        self._parameters.append(param)

    def get_parameter(self, name: str) -> Optional[Parameter]:
        """Get parameter by name"""
        for param in self._parameters:
            if param.name == name:
                return param
        return None

    @property
    def parameters(self) -> List[Parameter]:
        return self._parameters.copy()

    def report_error(self, message: str):
        """Report an error"""
        self.set_state(ComponentState.ERROR)
        for callback in self._error_callbacks:
            callback(message)

    def on_state_changed(self, callback: Callable[[ComponentState], None]):
        """Register state change callback"""
        self._state_callbacks.append(callback)

    def on_error(self, callback: Callable[[str], None]):
        """Register error callback"""
        self._error_callbacks.append(callback)

    def initialize(self):
        """Initialize component (called during construction)"""
        pass

    def serialize(self) -> dict:
        """Serialize component to JSON"""
        return {
            "id": self._id,
            "type": self.__class__.__name__,
            "state": self._state.name,
            "parameters": [p.to_json() for p in self._parameters]
        }

    def deserialize(self, data: dict):
        """Deserialize component from JSON"""
        self._id = data["id"]
        self._state = ComponentState[data.get("state", "IDLE")]

        # Deserialize parameters
        param_data = {p["name"]: p for p in data.get("parameters", [])}
        for param in self._parameters:
            if param.name in param_data:
                param.from_json(param_data[param.name])
```

#### 5.2 Implement Component Type Base Classes
- **Action**: Create PublisherComponent, SubscriberComponent, ProcessorComponent
- **Success Criteria**: Each type has appropriate behavior and color coding
- **Effort**: Medium
- **Dependencies**: 5.1
- **Considerations**: Publisher needs timer support, Processor needs auto-execute

**Implementation Details:**
```python
import time
from threading import Thread, Event

class PublisherComponent(ComponentBase):
    """Base for components that generate data"""

    def __init__(self):
        self._periodic_publishing = False
        self._publish_interval = 1000  # ms
        self._running = False
        self._timer_thread: Optional[Thread] = None
        self._stop_event = Event()
        super().__init__()

    def get_category(self) -> str:
        return "Publisher"

    def get_color(self) -> tuple:
        return (76, 175, 80)  # Green

    def set_periodic_publishing(self, enabled: bool):
        """Enable/disable periodic publishing"""
        self._periodic_publishing = enabled

    def set_publish_interval(self, interval_ms: int):
        """Set publishing interval in milliseconds"""
        self._publish_interval = interval_ms

    def start(self):
        """Start periodic publishing"""
        if self._periodic_publishing and not self._running:
            self._running = True
            self._stop_event.clear()
            self._timer_thread = Thread(target=self._timer_loop)
            self._timer_thread.daemon = True
            self._timer_thread.start()

    def stop(self):
        """Stop periodic publishing"""
        if self._running:
            self._running = False
            self._stop_event.set()
            if self._timer_thread:
                self._timer_thread.join()

    def _timer_loop(self):
        """Timer loop for periodic publishing"""
        while self._running:
            self.execute()
            self._stop_event.wait(self._publish_interval / 1000.0)

    def execute(self):
        """Execute component (triggers publishing)"""
        self.publish()

    @abstractmethod
    def publish(self):
        """Publish data to outputs (must be implemented by subclass)"""
        pass

class ProcessorComponent(ComponentBase):
    """Base for components that transform data"""

    def __init__(self):
        self._auto_execute = True
        self._pass_through = False
        super().__init__()

    def get_category(self) -> str:
        return "Processor"

    def get_color(self) -> tuple:
        return (255, 152, 0)  # Orange

    def execute(self):
        """Execute component (processes inputs)"""
        if self.validate_inputs():
            self.process()

    def validate_inputs(self) -> bool:
        """Check if all inputs have valid data"""
        for pin in self._input_pins:
            if not pin.is_connected():
                return False
        return True

    @abstractmethod
    def process(self):
        """Process inputs and generate outputs (must be implemented)"""
        pass

class SubscriberComponent(ComponentBase):
    """Base for components that consume data"""

    def __init__(self):
        self._auto_execute = True
        super().__init__()

    def get_category(self) -> str:
        return "Subscriber"

    def get_color(self) -> tuple:
        return (33, 150, 243)  # Blue

    def execute(self):
        """Execute component (processes inputs)"""
        self.process_inputs()

    @abstractmethod
    def process_inputs(self):
        """Process incoming data (must be implemented)"""
        pass
```

---

### 6. Connection and Topic System
**Rationale**: Manages data flow routing between components via topics
**Complexity**: Moderate

#### 6.1 Implement Connection Class
- **Action**: Create Connection with source/dest pin references and topic
- **Success Criteria**: Can validate type compatibility and serialize
- **Effort**: Medium
- **Dependencies**: 3.3
- **Considerations**: Use PinReference struct for serialization

#### 6.2 Implement Topic and TopicRegistry
- **Action**: Create publish-subscribe topic system with thread safety
- **Success Criteria**: Components can publish/subscribe to named topics
- **Effort**: High
- **Dependencies**: 2.2
- **Considerations**: Use threading.Lock for thread safety

**Implementation Details:**
```python
from threading import Lock
from typing import Optional, Dict

class Topic:
    """Named communication channel for data"""

    def __init__(self, name: str, expected_type: DataType = DataType.NULL):
        self._name = name
        self._expected_type = expected_type
        self._last_value: Optional[DataVariant] = None
        self._subscribers: Dict[int, Callable] = {}
        self._next_id = 0
        self._publish_count = 0
        self._lock = Lock()

    @property
    def name(self) -> str:
        return self._name

    def publish(self, data: DataVariant) -> bool:
        """Publish data to all subscribers"""
        with self._lock:
            if self._expected_type != DataType.NULL:
                if data.dtype != self._expected_type:
                    return False

            self._last_value = data
            self._publish_count += 1

            # Notify all subscribers
            for callback in self._subscribers.values():
                callback(self._name, data)

        return True

    def subscribe(self, callback: Callable) -> int:
        """Subscribe to topic updates"""
        with self._lock:
            sub_id = self._next_id
            self._next_id += 1
            self._subscribers[sub_id] = callback
            return sub_id

    def unsubscribe(self, sub_id: int) -> bool:
        """Unsubscribe from topic"""
        with self._lock:
            if sub_id in self._subscribers:
                del self._subscribers[sub_id]
                return True
            return False

class TopicRegistry:
    """Singleton registry managing all topics"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._topics = {}
                    cls._instance._registry_lock = Lock()
        return cls._instance

    @classmethod
    def instance(cls) -> 'TopicRegistry':
        return cls()

    def create_topic(self, name: str, dtype: DataType = DataType.NULL) -> bool:
        """Create a new topic"""
        with self._registry_lock:
            if name in self._topics:
                return False
            self._topics[name] = Topic(name, dtype)
            return True

    def delete_topic(self, name: str) -> bool:
        """Delete a topic"""
        with self._registry_lock:
            if name in self._topics:
                del self._topics[name]
                return True
            return False

    def has_topic(self, name: str) -> bool:
        """Check if topic exists"""
        with self._registry_lock:
            return name in self._topics

    def publish(self, name: str, data: DataVariant) -> bool:
        """Publish data to a topic"""
        with self._registry_lock:
            if name not in self._topics:
                return False
            return self._topics[name].publish(data)

    def subscribe(self, name: str, callback: Callable) -> int:
        """Subscribe to a topic"""
        with self._registry_lock:
            if name not in self._topics:
                return 0
            return self._topics[name].subscribe(callback)
```

---

### 7. Execution Engine
**Rationale**: Orchestrates component execution with proper dependency ordering
**Complexity**: Complex

#### 7.1 Implement ExecutionContext
- **Action**: Create container for component graph and connections
- **Success Criteria**: Can store components, connections, query by ID
- **Effort**: Medium
- **Dependencies**: 5.2, 6.1
- **Considerations**: Efficient lookup structures

#### 7.2 Implement Topological Sort Algorithm
- **Action**: Create dependency graph and topological sort for execution order
- **Success Criteria**: Can detect cycles, produce valid execution order
- **Effort**: High
- **Dependencies**: 7.1
- **Considerations**: Handle disconnected components gracefully

#### 7.3 Implement ExecutionEngine Core
- **Action**: Create execution loop with state management and timing
- **Success Criteria**: Can start/stop/pause/step execution, track statistics
- **Effort**: High
- **Dependencies**: 7.2
- **Considerations**: Use threading for non-blocking execution, proper cleanup

**Implementation Details:**
```python
from enum import Enum, auto
from typing import List, Set, Dict
import time
from threading import Thread, Lock, Event

class ExecutionState(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    ERROR = auto()

class ExecutionMode(Enum):
    CONTINUOUS = auto()
    SINGLE_STEP = auto()

class ExecutionEngine:
    """Orchestrates execution of component graphs"""

    def __init__(self):
        self._state = ExecutionState.IDLE
        self._mode = ExecutionMode.CONTINUOUS
        self._context: Optional['ExecutionContext'] = None
        self._execution_rate = 60.0  # Hz
        self._execution_order: List[ComponentBase] = []
        self._iteration_count = 0
        self._error_count = 0
        self._last_error = ""
        self._running = False
        self._thread: Optional[Thread] = None
        self._stop_event = Event()
        self._lock = Lock()

    def set_execution_context(self, context: 'ExecutionContext'):
        """Set the execution context"""
        self._context = context
        self._build_execution_order()

    def _build_execution_order(self) -> bool:
        """Perform topological sort on component graph"""
        if not self._context:
            return False

        # Build dependency graph
        graph: Dict[str, Set[str]] = {}
        in_degree: Dict[str, int] = {}

        for comp in self._context.components:
            graph[comp.id] = set()
            in_degree[comp.id] = 0

        # Count dependencies
        for conn in self._context.connections:
            dest_comp_id = conn.destination.component_id
            source_comp_id = conn.source.component_id
            if dest_comp_id != source_comp_id:
                graph[source_comp_id].add(dest_comp_id)
                in_degree[dest_comp_id] = in_degree.get(dest_comp_id, 0) + 1

        # Topological sort using Kahn's algorithm
        queue = [comp_id for comp_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            comp_id = queue.pop(0)
            result.append(comp_id)

            for neighbor in graph[comp_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(result) != len(self._context.components):
            self._last_error = "Cycle detected in component graph"
            return False

        # Convert IDs to components
        comp_map = {c.id: c for c in self._context.components}
        self._execution_order = [comp_map[comp_id] for comp_id in result]

        return True

    def start(self):
        """Start execution"""
        if self._state == ExecutionState.ERROR:
            return

        if not self._build_execution_order():
            self.set_state(ExecutionState.ERROR)
            return

        self._running = True
        self._stop_event.clear()
        self.set_state(ExecutionState.RUNNING)

        self._thread = Thread(target=self._execution_loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        """Stop execution"""
        self._running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self.set_state(ExecutionState.IDLE)

    def pause(self):
        """Pause execution"""
        self.set_state(ExecutionState.PAUSED)
        self._running = False

    def step(self):
        """Execute one iteration"""
        self._execute_iteration()

    def _execution_loop(self):
        """Main execution loop"""
        interval = 1.0 / self._execution_rate

        while self._running:
            start_time = time.time()

            self._execute_iteration()

            # Maintain execution rate
            elapsed = time.time() - start_time
            sleep_time = interval - elapsed
            if sleep_time > 0:
                self._stop_event.wait(sleep_time)

    def _execute_iteration(self):
        """Execute one full iteration"""
        for component in self._execution_order:
            try:
                component.execute()
            except Exception as e:
                self._error_count += 1
                self._last_error = str(e)
                component.report_error(str(e))

        self._iteration_count += 1

    def set_state(self, state: ExecutionState):
        """Set execution state"""
        with self._lock:
            self._state = state
```

---

### 8. Component Registry
**Rationale**: Factory pattern for component instantiation and discovery
**Complexity**: Moderate

#### 8.1 Implement ComponentRegistry Singleton
- **Action**: Create registry with registration, factory, and query methods
- **Success Criteria**: Can register/create components, query by category/tag
- **Effort**: Medium
- **Dependencies**: 5.2
- **Considerations**: Thread-safe singleton, support decorators for auto-registration

**Implementation Details:**
```python
from typing import Dict, List, Callable
from threading import Lock

@dataclass
class ComponentMetadata:
    """Metadata describing a component type"""
    type_name: str
    display_name: str
    category: str
    description: str
    icon_path: str = ""
    tags: List[str] = None
    version: int = 1

class ComponentRegistry:
    """Singleton registry for component types"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._components = {}
                    cls._instance._registry_lock = Lock()
        return cls._instance

    @classmethod
    def instance(cls) -> 'ComponentRegistry':
        return cls()

    def register_component(self,
                          metadata: ComponentMetadata,
                          factory: Callable[[dict], ComponentBase]) -> bool:
        """Register a component type"""
        with self._registry_lock:
            self._components[metadata.type_name] = {
                'metadata': metadata,
                'factory': factory
            }
            return True

    def create_component(self, type_name: str, params: dict = None) -> Optional[ComponentBase]:
        """Create a component instance"""
        with self._registry_lock:
            if type_name not in self._components:
                return None

            factory = self._components[type_name]['factory']
            return factory(params or {})

    def get_components_by_category(self, category: str) -> List[str]:
        """Get all component types in a category"""
        with self._registry_lock:
            return [
                name for name, data in self._components.items()
                if data['metadata'].category == category
            ]

    def get_all_categories(self) -> List[str]:
        """Get all unique categories"""
        with self._registry_lock:
            categories = set()
            for data in self._components.values():
                categories.add(data['metadata'].category)
            return sorted(categories)

# Decorator for auto-registration
def register_component(type_name: str, display_name: str,
                      category: str, description: str):
    """Decorator for automatic component registration"""
    def decorator(cls):
        metadata = ComponentMetadata(
            type_name=type_name,
            display_name=display_name,
            category=category,
            description=description
        )

        def factory(params):
            return cls()

        ComponentRegistry.instance().register_component(metadata, factory)
        return cls

    return decorator
```

---

### 9. Serialization System
**Rationale**: Save and load project files in .vse JSON format
**Complexity**: Moderate

#### 9.1 Implement Project Data Structures
- **Action**: Create dataclasses for ProjectData, ComponentData, ConnectionData
- **Success Criteria**: All project state can be represented in JSON-serializable form
- **Effort**: Low
- **Dependencies**: None
- **Considerations**: Use dataclasses for clean structure

#### 9.2 Implement ProjectSerializer
- **Action**: Create serializer with save/load, validation, version migration
- **Success Criteria**: Can save/load complete projects, validate structure
- **Effort**: High
- **Dependencies**: 9.1, 5.2, 6.1
- **Considerations**: Handle missing component types gracefully, timestamp metadata

---

### 10. Example Components Implementation
**Rationale**: Provide concrete components for testing and demonstration
**Complexity**: Simple

#### 10.1 Implement Math Components
- **Action**: Create AddComponent, SubtractComponent, MultiplyComponent, CompareComponent
- **Success Criteria**: Each performs correct mathematical operation
- **Effort**: Low
- **Dependencies**: 5.2
- **Considerations**: Handle type conversion between int/float

**Example Implementation:**
```python
@register_component("Add", "Add", "Math", "Adds two numbers")
class AddComponent(ProcessorComponent):
    """Adds two numbers"""

    def __init__(self):
        super().__init__()

    def initialize(self):
        self.add_input_pin("A", DataType.FLOAT)
        self.add_input_pin("B", DataType.FLOAT)
        self.add_output_pin("Result", DataType.FLOAT)

    def get_name(self) -> str:
        return "Add"

    def get_category(self) -> str:
        return "Math"

    def get_color(self) -> tuple:
        return (100, 200, 100)

    def process(self):
        pin_a = self.get_input_pin("A")
        pin_b = self.get_input_pin("B")
        result_pin = self.get_output_pin("Result")

        a = pin_a.data.to_float()
        b = pin_b.data.to_float()
        result = a + b

        result_pin.transmit_data(DataVariant(result, DataType.FLOAT))
```

#### 10.2 Implement Logic Components
- **Action**: Create AndGate, OrGate, NotGate, XorGate
- **Success Criteria**: Each performs correct logical operation
- **Effort**: Low
- **Dependencies**: 5.2
- **Considerations**: Boolean type handling

---

### 11. DearPyGui GUI Foundation
**Rationale**: Create the graphical interface using dearpygui's node editor
**Complexity**: Complex

#### 11.1 Research DearPyGui Node Editor API
- **Action**: Study dearpygui documentation and examples for node editor
- **Success Criteria**: Understand dpg.add_node_editor, dpg.add_node, dpg.add_node_link APIs
- **Effort**: Medium
- **Dependencies**: None
- **Considerations**: Note callback patterns and attribute system

**DearPyGui Node Editor Key Concepts:**
- `dpg.add_node_editor()`: Creates node editor container
- `dpg.add_node()`: Creates a node (component) in the editor
- `dpg.add_node_attribute()`: Creates input/output pins on nodes
- `dpg.add_node_link()`: Creates visual connection between pins
- Link callback receives (sender, app_data) where app_data contains pin IDs
- Delink callback for connection removal

**Reference:** https://dearpygui.readthedocs.io/en/latest/documentation/node-editor.html

#### 11.2 Implement NodeEditor Wrapper
- **Action**: Create wrapper class managing dpg node editor, nodes, and links
- **Success Criteria**: Can create/delete nodes, create/delete connections visually
- **Effort**: High
- **Dependencies**: 11.1, 5.1
- **Considerations**: Map between dpg tags and component/pin IDs

**Implementation Details:**
```python
import dearpygui.dearpygui as dpg
from typing import Dict, Tuple

class NodeEditorWrapper:
    """Wrapper for DearPyGui node editor"""

    def __init__(self, parent: int):
        self._editor_id = dpg.add_node_editor(
            parent=parent,
            callback=self._link_callback,
            delink_callback=self._delink_callback
        )

        self._nodes: Dict[str, int] = {}  # component_id -> dpg_node_tag
        self._attributes: Dict[str, int] = {}  # pin_id -> dpg_attribute_tag
        self._links: Dict[Tuple[str, str], int] = {}  # (out_pin, in_pin) -> dpg_link_tag
        self._link_callback_fn = None
        self._delink_callback_fn = None

    def add_node(self, component: ComponentBase, pos: Tuple[float, float]):
        """Add a component as a node"""
        with dpg.node(parent=self._editor_id,
                     label=component.get_name(),
                     pos=pos) as node_id:

            # Add input pins
            for pin in component.input_pins:
                attr_id = dpg.add_node_attribute(
                    attribute_type=dpg.mvNode_Attr_Input,
                    label=pin.name
                )
                self._attributes[pin.id] = attr_id

            # Add output pins
            for pin in component.output_pins:
                attr_id = dpg.add_node_attribute(
                    attribute_type=dpg.mvNode_Attr_Output,
                    label=pin.name
                )
                self._attributes[pin.id] = attr_id

            self._nodes[component.id] = node_id

    def add_link(self, output_pin_id: str, input_pin_id: str):
        """Add a visual link between pins"""
        out_attr = self._attributes.get(output_pin_id)
        in_attr = self._attributes.get(input_pin_id)

        if out_attr and in_attr:
            link_id = dpg.add_node_link(
                out_attr, in_attr,
                parent=self._editor_id
            )
            self._links[(output_pin_id, input_pin_id)] = link_id

    def _link_callback(self, sender, app_data):
        """Called when user creates a link"""
        # app_data is [output_attr_id, input_attr_id]
        if self._link_callback_fn:
            # Reverse lookup: dpg attribute -> pin ID
            out_pin_id = self._find_pin_by_attr(app_data[0])
            in_pin_id = self._find_pin_by_attr(app_data[1])
            if out_pin_id and in_pin_id:
                self._link_callback_fn(out_pin_id, in_pin_id)

    def _delink_callback(self, sender, app_data):
        """Called when user removes a link"""
        if self._delink_callback_fn:
            link_id = app_data
            # Find pin IDs from link
            for (out_pin, in_pin), lid in self._links.items():
                if lid == link_id:
                    self._delink_callback_fn(out_pin, in_pin)
                    del self._links[(out_pin, in_pin)]
                    break

    def _find_pin_by_attr(self, attr_id: int) -> Optional[str]:
        """Reverse lookup: attribute ID -> pin ID"""
        for pin_id, aid in self._attributes.items():
            if aid == attr_id:
                return pin_id
        return None
```

#### 11.3 Implement Main Window
- **Action**: Create main application window with menu bar, node editor, panels
- **Success Criteria**: Window displays with all UI elements
- **Effort**: High
- **Dependencies**: 11.2
- **Considerations**: Layout management, window sizing

#### 11.4 Implement Component Palette
- **Action**: Create component selection panel using ComponentRegistry
- **Success Criteria**: Shows categorized list, double-click adds to canvas
- **Effort**: Medium
- **Dependencies**: 8.1, 11.2
- **Considerations**: Search/filter functionality

#### 11.5 Implement Inspector Panel
- **Action**: Create property editor for selected component's parameters
- **Success Criteria**: Shows and edits parameters with appropriate widgets
- **Effort**: Medium
- **Dependencies**: 4.2, 11.2
- **Considerations**: Dynamic widget creation based on parameter type

#### 11.6 Implement Execution Control Panel
- **Action**: Create UI for execution controls (play/pause/stop/step)
- **Success Criteria**: Buttons control execution engine, display statistics
- **Effort**: Low
- **Dependencies**: 7.3, 11.2
- **Considerations**: Update statistics in real-time

---

### 12. Integration and Application Assembly
**Rationale**: Connect all subsystems into working application
**Complexity**: Moderate

#### 12.1 Implement Application Main Class
- **Action**: Create main application coordinating all subsystems
- **Success Criteria**: All components initialized and connected properly
- **Effort**: Medium
- **Dependencies**: 11.6
- **Considerations**: Proper initialization order, cleanup on exit

#### 12.2 Implement File Operations
- **Action**: Add save/load/new project functionality to main window
- **Success Criteria**: Can save and load .vse files through file dialogs
- **Effort**: Medium
- **Dependencies**: 9.2, 12.1
- **Considerations**: Unsaved changes warning

#### 12.3 Connect GUI Events to Core Logic
- **Action**: Wire up all event handlers between GUI and core systems
- **Success Criteria**: User actions in GUI affect core state correctly
- **Effort**: High
- **Dependencies**: 12.1
- **Considerations**: Proper event propagation, avoid circular dependencies

---

## Execution Recommendations

**Suggested Approach:**

1. **Bottom-Up Core Development** (Phases 1-8): Build foundation first
   - Start with data types and move up the dependency chain
   - Each phase can be unit tested independently
   - Core logic is GUI-independent

2. **Component Implementation** (Phase 10): Create example components early
   - Provides test cases for core functionality
   - Can test without GUI initially

3. **GUI Development** (Phase 11): Build interface last
   - Core functionality already tested and working
   - Can focus on user experience
   - Easier to iterate on UI design

4. **Integration** (Phase 12): Connect everything together
   - Most bugs already fixed in isolated testing
   - Focus on interaction patterns

**Parallel Work Opportunities:**
- Phases 2-4 (data types, pins, parameters) can be developed in parallel
- Phase 10 (components) can start once Phase 5 is complete
- Phase 11 (GUI) can be prototyped early for design validation

**Priority Ordering:**
1. High Priority: Phases 1-7 (foundation and execution)
2. Medium Priority: Phases 8-10 (registry and components)
3. Lower Priority: Phase 11 (GUI polish)
4. Final: Phase 12 (integration)

---

## Critical Success Factors

1. **Maintain Architectural Integrity**: Keep the same design patterns as C++ version
2. **Python Idioms**: Use dataclasses, type hints, properties, decorators appropriately
3. **Type Safety**: Even with dynamic typing, maintain runtime type checking
4. **Thread Safety**: Proper locking for concurrent access (topic registry, registry)
5. **Error Handling**: Graceful degradation, informative error messages

---

## Potential Risks and Mitigations

### Risk 1: DearPyGui Learning Curve
**Mitigation**: Start with simple node editor prototype, study examples thoroughly
**Reference**: https://dearpygui.readthedocs.io/en/latest/documentation/node-editor.html

### Risk 2: Performance with Many Components
**Mitigation**: Profile early, optimize execution engine, consider limiting update rate

### Risk 3: Threading Complexity
**Mitigation**: Use Python's threading primitives carefully, minimize shared state

### Risk 4: Type System Translation
**Mitigation**: Use Python Enums, maintain runtime type checking, comprehensive tests

### Risk 5: GUI State Synchronization
**Mitigation**: Clear separation between GUI and core, event-driven updates

---

## Key Differences from C++ Version

### Python Advantages:
1. **Dynamic Typing**: More flexible parameter system
2. **Decorators**: Cleaner component registration
3. **No Manual Memory Management**: Simpler ownership
4. **Duck Typing**: Easier to extend parameter types
5. **JSON Native**: Built-in JSON support

### Python Considerations:
1. **No Qt Signals**: Use callback lists instead
2. **GIL**: Threading is different (but OK for this use case)
3. **No Strong Typing**: Need runtime validation
4. **Performance**: Slower than C++ (but adequate for visual scripting)

### DearPyGui vs Qt6:
1. **Simpler API**: Less boilerplate than Qt
2. **Immediate Mode**: Different rendering paradigm
3. **Built-in Node Editor**: Less custom code needed
4. **Limited Widgets**: May need custom implementations
5. **No Designer**: GUI must be code-defined

---

## Example Component Implementations

### Simple Publisher Example:
```python
@register_component("ConstantValue", "Constant Value", "Publisher",
                   "Outputs a constant numeric value")
class ConstantValueComponent(PublisherComponent):
    def __init__(self):
        super().__init__()

    def initialize(self):
        self.add_output_pin("Value", DataType.FLOAT)
        self.add_parameter(FloatParameter("value", 0.0,
                                         description="Constant value"))

    def get_name(self) -> str:
        return "Constant Value"

    def publish(self):
        param = self.get_parameter("value")
        out_pin = self.get_output_pin("Value")
        out_pin.transmit_data(DataVariant(param.get_value(), DataType.FLOAT))
```

### Simple Processor Example:
```python
@register_component("Multiply", "Multiply", "Math",
                   "Multiplies two numbers")
class MultiplyComponent(ProcessorComponent):
    def initialize(self):
        self.add_input_pin("A", DataType.FLOAT)
        self.add_input_pin("B", DataType.FLOAT)
        self.add_output_pin("Result", DataType.FLOAT)

    def get_name(self) -> str:
        return "Multiply"

    def process(self):
        a = self.get_input_pin("A").data.to_float()
        b = self.get_input_pin("B").data.to_float()
        result = a * b
        self.get_output_pin("Result").transmit_data(
            DataVariant(result, DataType.FLOAT)
        )
```

### Simple Subscriber Example:
```python
@register_component("ConsoleOutput", "Console Output", "Subscriber",
                   "Prints values to console")
class ConsoleOutputComponent(SubscriberComponent):
    def initialize(self):
        self.add_input_pin("Input", DataType.ANY)

    def get_name(self) -> str:
        return "Console Output"

    def process_inputs(self):
        input_pin = self.get_input_pin("Input")
        if input_pin.is_connected():
            value = input_pin.data.value
            print(f"[Console] {value}")
```

---

## Testing Strategy

### Unit Tests:
- Test each core class independently
- Mock dependencies where needed
- Aim for 80%+ coverage

### Integration Tests:
- Test component graph execution
- Test serialization round-trips
- Test registry operations

### GUI Tests:
- Manual testing primarily
- Test node creation/deletion
- Test connection creation/deletion
- Test parameter editing

---

## Documentation Requirements

1. **README.md**: Installation, quick start, examples
2. **API Documentation**: Docstrings for all public classes/methods
3. **Architecture Guide**: Explain design patterns used
4. **Component Development Guide**: How to create custom components
5. **User Manual**: How to use the application

---

## Version Milestones

**v0.1 - Core Functional** (Phases 1-7)
- All core systems working
- Execution engine functional
- No GUI yet

**v0.2 - Basic Components** (Phase 10)
- Math and logic components
- Can test execution programmatically

**v0.3 - Basic GUI** (Phase 11.1-11.3)
- Node editor displays components
- Can create connections visually

**v0.4 - Full GUI** (Phase 11.4-11.6)
- Component palette
- Inspector panel
- Execution controls

**v0.5 - Complete** (Phase 12)
- Full integration
- Save/load working
- Production ready

---

## Sources

- [DearPyGui Node Editor Documentation](https://dearpygui.readthedocs.io/en/latest/documentation/node-editor.html)
- [DearPyGui GitHub Repository](https://github.com/hoffstadt/DearPyGui)
- [DearPyGui PyPI Package](https://pypi.org/project/dearpygui/1.2.2/)

---

## Conclusion

This plan provides a comprehensive roadmap for implementing VSE_PY. The bottom-up approach ensures each layer is solid before building the next. The key to success is maintaining the architectural integrity of the original C++ design while leveraging Python's strengths for cleaner, more maintainable code.

The DearPyGui node editor provides the necessary GUI capabilities with less complexity than Qt6, making it an excellent choice for this project. The immediate-mode paradigm may require some adjustment, but will ultimately result in simpler code.

By following this plan systematically, you'll create a powerful visual scripting environment in Python that maintains all the functionality of the original C++ version while being more accessible and easier to extend.
