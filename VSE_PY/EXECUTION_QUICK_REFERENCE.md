# VSE_PY Execution System - Quick Reference

## ExecutionContext

Container for components and connections during execution.

### Create Context
```python
from vse_py.core.execution_context import ExecutionContext

context = ExecutionContext()
```

### Add/Remove Components
```python
# Add component
context.add_component(component)

# Remove component
context.remove_component(component)

# Get component by ID
component = context.get_component_by_id(component_id)

# Get all components
all_components = context.components  # Returns copy
```

### Connection Management
```python
# Add connection
context.add_connection(connection)

# Remove connection
context.remove_connection(connection)

# Get all connections
all_connections = context.connections  # Returns copy
```

### Clear Context
```python
# Clear all components and connections
context.clear()
```

---

## ExecutionEngine

Orchestrates execution of component graphs.

### Create and Configure Engine
```python
from vse_py.core.execution_engine import ExecutionEngine, ExecutionState, ExecutionMode

# Create engine
engine = ExecutionEngine()

# Set execution mode
engine.mode = ExecutionMode.CONTINUOUS  # or SINGLE_STEP

# Set execution rate (Hz)
engine.execution_rate = 60.0  # Default is 60 Hz
```

### Set Execution Context
```python
# Set context with components
success = engine.set_execution_context(context)

if not success:
    # Cycle detected or error
    print(f"Error: {engine.last_error}")
```

### Control Execution
```python
# Start continuous execution
engine.start()

# Pause execution
engine.pause()

# Resume execution
engine.start()  # Restart after pause

# Stop execution
engine.stop()

# Single step (execute one iteration)
engine.step()
```

### Query State and Statistics
```python
# Get current state
state = engine.state  # ExecutionState enum
print(state.name)  # "IDLE", "RUNNING", "PAUSED", or "ERROR"

# Get statistics
iterations = engine.iteration_count
errors = engine.error_count
last_error = engine.last_error

# Reset statistics
engine.reset()
```

### Register Callbacks
```python
# State change callback
def on_state_change(state):
    print(f"State: {state.name}")

engine.on_state_changed(on_state_change)

# Iteration completion callback
def on_iteration():
    print(f"Iteration {engine.iteration_count} completed")

engine.on_iteration_completed(on_iteration)

# Error callback
def on_error(message):
    print(f"Error: {message}")

engine.on_error(on_error)
```

---

## Execution States

- **IDLE**: Engine is not running
- **RUNNING**: Engine is actively executing components
- **PAUSED**: Engine is paused, can resume with start()
- **ERROR**: Engine encountered an error and stopped

## Execution Modes

- **CONTINUOUS**: Automatically execute at specified rate (Hz)
- **SINGLE_STEP**: Manual control via step() calls

---

## Complete Example

```python
from vse_py.core.execution_context import ExecutionContext
from vse_py.core.execution_engine import ExecutionEngine, ExecutionMode

# 1. Create components (assumed to exist)
component1 = Component1()
component2 = Component2()

# 2. Create context and add components
context = ExecutionContext()
context.add_component(component1)
context.add_component(component2)

# Connect them (assumed to exist)
connection = Connection(component1.output, component2.input)
context.add_connection(connection)

# 3. Create engine
engine = ExecutionEngine()

# 4. Configure engine
engine.execution_rate = 30.0  # 30 Hz
engine.mode = ExecutionMode.CONTINUOUS

# 5. Register callbacks
def on_iter():
    print(f"Iteration: {engine.iteration_count}")

engine.on_iteration_completed(on_iter)

# 6. Set context (performs topological sort)
if not engine.set_execution_context(context):
    print(f"Error: {engine.last_error}")
    exit(1)

# 7. Start execution
engine.start()

# 8. Let it run
import time
time.sleep(5)

# 9. Stop execution
engine.stop()

print(f"Total iterations: {engine.iteration_count}")
print(f"Total errors: {engine.error_count}")
```

---

## Common Patterns

### Continuous Execution
```python
engine.mode = ExecutionMode.CONTINUOUS
engine.execution_rate = 60.0  # 60 Hz
engine.set_execution_context(context)
engine.start()

# Run for a while...
time.sleep(10)

engine.stop()
```

### Single-Step Debugging
```python
engine.mode = ExecutionMode.SINGLE_STEP
engine.set_execution_context(context)

for i in range(10):
    engine.step()
    print(f"Iteration {i + 1}")
```

### Error Handling
```python
def on_error(message):
    print(f"Component error: {message}")
    engine.stop()

engine.on_error(on_error)
engine.set_execution_context(context)
engine.start()
```

### Monitor Execution
```python
def on_state_change(state):
    print(f"Engine state: {state.name}")

def on_iteration():
    if engine.iteration_count % 10 == 0:
        print(f"Progress: {engine.iteration_count} iterations")

engine.on_state_changed(on_state_change)
engine.on_iteration_completed(on_iteration)
```

### Pause and Resume
```python
engine.start()
time.sleep(2)

engine.pause()
print(f"Paused at iteration {engine.iteration_count}")

time.sleep(1)

engine.start()  # Resume
time.sleep(2)

engine.stop()
```

---

## Properties Reference

### ExecutionEngine Properties

| Property | Type | R/W | Description |
|----------|------|-----|-------------|
| `state` | ExecutionState | R | Current execution state |
| `mode` | ExecutionMode | R/W | Execution mode |
| `execution_rate` | float | R/W | Execution rate in Hz |
| `iteration_count` | int | R | Number of iterations completed |
| `error_count` | int | R | Number of errors encountered |
| `last_error` | str | R | Description of last error |

### ExecutionContext Properties

| Property | Type | R | Description |
|----------|------|---|-------------|
| `components` | List | R | All components in context |
| `connections` | List | R | All connections in context |

---

## Error Handling

### Cycle Detection
```python
success = engine.set_execution_context(context)
if not success:
    if "Cycle" in engine.last_error:
        print("Graph has a cycle!")
```

### Invalid Inputs
```python
try:
    engine.execution_rate = -1  # ValueError
except ValueError as e:
    print(f"Invalid rate: {e}")

try:
    engine.mode = "INVALID"  # TypeError
except TypeError as e:
    print(f"Invalid mode: {e}")

try:
    engine.set_execution_context(None)  # TypeError
except TypeError as e:
    print(f"Invalid context: {e}")
```

---

## Performance Tips

1. **Batch Operations**: Add all components before starting engine
2. **High Rate**: Set execution_rate higher for faster execution (more CPU usage)
3. **Low Rate**: Set execution_rate lower to reduce CPU usage
4. **Single-Step**: Use single-step mode for debugging, continuous for normal operation
5. **Callbacks**: Keep callbacks fast - they block execution

---

## Thread Safety

- All operations are thread-safe
- State transitions are atomic
- Safe to call from any thread
- Callbacks invoked with proper lock management

---

## Status Check

```python
# Check if running
if engine.state == ExecutionState.RUNNING:
    print("Engine is running")

# Check if error occurred
if engine.state == ExecutionState.ERROR:
    print(f"Error: {engine.last_error}")

# Get execution progress
progress = engine.iteration_count
print(f"Completed {progress} iterations")
```

---

## Troubleshooting

### Engine Not Starting
```python
# Verify context is set
if not engine._context:
    print("Context not set")
    engine.set_execution_context(context)

# Verify no cycle
if engine.state == ExecutionState.ERROR:
    print(f"Error: {engine.last_error}")
```

### No Iterations Happening
```python
# Verify components in context
if not engine._context.components:
    print("No components in context")

# Verify execution loop is running
time.sleep(0.1)
if engine.iteration_count == 0:
    print("No iterations executed")
```

### High CPU Usage
```python
# Lower execution rate
engine.execution_rate = 10.0  # Instead of 60.0

# Use single-step mode
engine.mode = ExecutionMode.SINGLE_STEP
engine.step()  # Only when needed
```

---

## References

- **ExecutionContext**: Full documentation in execution_context.py
- **ExecutionEngine**: Full documentation in execution_engine.py
- **Implementation Summary**: EXECUTION_IMPLEMENTATION.md
