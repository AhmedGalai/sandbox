# Parameter System - Quick Reference Guide

## Quick Start

### Basic Parameter Usage
```python
from vse_py.core.parameter import IntParameter, FloatParameter, StringParameter, BoolParameter

# Integer parameter
count = IntParameter("count", default=5, min_val=0, max_val=100)
count.set_value(10)
print(count.get_value())  # 10

# Float parameter
ratio = FloatParameter("ratio", default=0.5, min_val=0.0, max_val=1.0)
ratio.set_value(0.75)
print(ratio.get_value())  # 0.75

# String parameter
filename = StringParameter("filename", default="output.txt")
filename.set_value("result.dat")
print(filename.get_value())  # result.dat

# Boolean parameter
enabled = BoolParameter("enabled", default=True)
enabled.set_value(False)
print(enabled.get_value())  # False
```

---

## Parameter Type Comparison

| Feature | Int | Float | String | Bool |
|---------|-----|-------|--------|------|
| Range Constraints | ✓ (min/max) | ✓ (min/max) | ✗ | ✗ |
| Type Conversion | ✓ | ✓ | ✓ | ✓ |
| Default Value | ✓ | ✓ | ✓ | ✓ |
| JSON Serialization | ✓ | ✓ | ✓ | ✓ |
| Value Clamping | ✓ | ✓ | ✗ | ✗ |
| NaN Rejection | N/A | ✓ | N/A | N/A |

---

## IntParameter Recipes

### Simple Counter
```python
count = IntParameter("count", default=0)
count.set_value(10)
```

### Percentage (0-100)
```python
percentage = IntParameter("percentage", default=50, min_val=0, max_val=100)
```

### Port Number (1024-65535)
```python
port = IntParameter("port", default=8080, min_val=1024, max_val=65535)
```

### Iterations (at least 1)
```python
iterations = IntParameter("iterations", default=1, min_val=1, max_val=10000)
```

### With Description
```python
param = IntParameter(
    "threshold",
    default=50,
    min_val=0,
    max_val=100,
    description="Detection sensitivity threshold"
)
```

---

## FloatParameter Recipes

### Probability (0.0-1.0)
```python
probability = FloatParameter("probability", default=0.5, min_val=0.0, max_val=1.0)
```

### Scale Factor
```python
scale = FloatParameter("scale", default=1.0, min_val=0.1, max_val=10.0)
```

### Angle (0-360)
```python
angle = FloatParameter("angle", default=0.0, min_val=0.0, max_val=360.0)
```

### Learning Rate
```python
lr = FloatParameter("learning_rate", default=0.001, min_val=0.0001, max_val=1.0)
```

### Unbounded Value
```python
value = FloatParameter("value")  # Default range: -1e308 to 1e308
```

---

## StringParameter Recipes

### File Path
```python
path = StringParameter("path", default="/home/user/data.txt")
```

### Regular Parameter
```python
name = StringParameter("name", default="unknown")
```

### URL
```python
url = StringParameter("url", default="http://localhost:8080")
```

### Command
```python
command = StringParameter("command", default="")
```

---

## BoolParameter Recipes

### Feature Flag
```python
enabled = BoolParameter("enabled", default=False)
```

### Verbose Output
```python
verbose = BoolParameter("verbose", default=False)
```

### Debug Mode
```python
debug = BoolParameter("debug", default=False)
```

---

## JSON Serialization

### Save Parameter
```python
param = IntParameter("count", default=42, min_val=0, max_val=100)
json_data = param.to_json()
# Output: {'type': 'int', 'name': 'count', 'value': 42, 'min': 0, 'max': 100, 'description': ''}
```

### Load Parameter
```python
param = IntParameter("count")
param.from_json({
    'value': 42,
    'min': 0,
    'max': 100
})
print(param.get_value())  # 42
```

### Full Roundtrip
```python
# Save
original = IntParameter("test", default=42, min_val=0, max_val=100)
data = original.to_json()

# Load
restored = IntParameter("test")
restored.from_json(data)

# Verify
assert restored.get_value() == original.get_value()
assert restored.min_value == original.min_value
assert restored.max_value == original.max_value
```

---

## Type Conversion Examples

### IntParameter Conversion
```python
param = IntParameter("test")

param.set_value(42.7)     # float -> int: 42
param.set_value("42")     # string -> int: 42
param.set_value(True)     # bool -> int: 1
param.set_value(False)    # bool -> int: 0
```

### FloatParameter Conversion
```python
param = FloatParameter("test")

param.set_value(42)       # int -> float: 42.0
param.set_value("3.14")   # string -> float: 3.14
```

### StringParameter Conversion
```python
param = StringParameter("test")

param.set_value(42)       # int -> string: "42"
param.set_value(3.14)     # float -> string: "3.14"
param.set_value(None)     # None -> string: ""
```

### BoolParameter Conversion
```python
param = BoolParameter("test")

param.set_value(1)        # Non-zero int -> True
param.set_value(0)        # Zero int -> False
param.set_value("yes")    # Non-empty string -> True
param.set_value("")       # Empty string -> False
param.set_value([1, 2])   # Non-empty list -> True
param.set_value([])       # Empty list -> False
param.set_value(None)     # None -> False
```

---

## Common Patterns

### Parameter in Component
```python
from vse_py.core.parameter import IntParameter, FloatParameter

class MyProcessor:
    def __init__(self):
        self.max_iterations = IntParameter("max_iterations", default=100, min_val=1)
        self.threshold = FloatParameter("threshold", default=0.5, min_val=0.0, max_val=1.0)

    def process(self):
        iterations = self.max_iterations.get_value()
        threshold = self.threshold.get_value()

        for i in range(iterations):
            if i > threshold * iterations:
                break
```

### Parameter GUI Binding (Pseudo-code)
```python
# Get parameter
param = component.get_parameter("count")

# Create UI widget
slider = create_slider(
    min=param.min_value if hasattr(param, 'min_value') else 0,
    max=param.max_value if hasattr(param, 'max_value') else 100,
    value=param.get_value()
)

# Bind slider to parameter
slider.on_change = lambda v: param.set_value(v)

# Bind parameter to slider
param.on_change = lambda v: slider.set_value(v)
```

### Batch Parameter Update
```python
# Save all component parameters
def save_params(component):
    params = {}
    for param in component.parameters:
        params[param.name] = param.to_json()
    return params

# Load all component parameters
def load_params(component, params):
    for param in component.parameters:
        if param.name in params:
            param.from_json(params[param.name])
```

---

## Error Handling

### Handling Invalid Ranges
```python
try:
    param = IntParameter("test", min_val=100, max_val=0)
except ValueError as e:
    print(f"Invalid range: {e}")
```

### Handling Type Errors
```python
param = IntParameter("test")
try:
    param.set_value("not_a_number")
except TypeError as e:
    print(f"Type error: {e}")
```

### Handling NaN/Infinity
```python
param = FloatParameter("test")
try:
    param.set_value(float('nan'))
except ValueError:
    print("NaN not allowed")

try:
    param.set_value(float('inf'))
except ValueError:
    print("Infinity handling depends on context")
```

### Handling Missing JSON Keys
```python
param = IntParameter("test")
try:
    param.from_json({'min': 0, 'max': 100})  # Missing 'value'
except KeyError as e:
    print(f"Missing JSON key: {e}")
```

---

## Performance Tips

### Avoid Repeated Type Conversions
```python
# SLOW: Multiple conversions
for i in range(1000):
    param.set_value(str(i))

# FAST: Convert once
for i in range(1000):
    param.set_value(i)  # Integer is native type
```

### Cache Parameter References
```python
# SLOW: Lookup parameter each time
for _ in range(100):
    value = component.get_parameter("count").get_value()

# FAST: Cache the reference
param = component.get_parameter("count")
for _ in range(100):
    value = param.get_value()
```

---

## Validation Summary

| Scenario | Behavior |
|----------|----------|
| Int too high | Clamped to max |
| Int too low | Clamped to min |
| Float NaN | ValueError |
| Float infinity | Clamped (for range constrained) |
| String invalid | Converted if possible |
| Bool invalid | Converted via truthiness |

---

## Properties Available

### All Parameters
```python
param.name              # str - Parameter name
param.description       # str - Parameter description
```

### Int/Float Parameters Only
```python
param.min_value         # int/float - Minimum value
param.max_value         # int/float - Maximum value
```

---

## Method Reference

### All Parameters
```python
get_value() -> Any          # Get current value
set_value(value: Any)       # Set value with validation
to_json() -> dict           # Serialize to JSON
from_json(data: dict)       # Deserialize from JSON
```

---

## Troubleshooting

### "Parameter name must be a non-empty string"
```python
# WRONG
param = IntParameter("")  # Empty name not allowed
param = IntParameter(42)  # Name must be string

# RIGHT
param = IntParameter("count")
```

### "min_val cannot exceed max_val"
```python
# WRONG
param = IntParameter("test", min_val=100, max_val=50)

# RIGHT
param = IntParameter("test", min_val=50, max_val=100)
```

### "Cannot convert to int"
```python
# WRONG
param = IntParameter("test")
param.set_value("not_a_number")  # Not convertible

# RIGHT
param.set_value(42)
param.set_value(42.7)
param.set_value("42")
```

### "NaN values are not allowed"
```python
# WRONG
param = FloatParameter("test")
param.set_value(float('nan'))

# RIGHT
param.set_value(0.0)
param.set_value(3.14)
```

---

## Integration Checklist

When integrating parameters into your component:

- [ ] Import parameter classes
- [ ] Add parameters in `initialize()`
- [ ] Set sensible defaults
- [ ] Add descriptions for user documentation
- [ ] Use parameters in `process()` / `execute()` methods
- [ ] Test parameter validation (min/max constraints)
- [ ] Test JSON serialization (save/load)
- [ ] Handle parameter changes gracefully

---

## Next Steps

After implementing parameters:
1. ✓ Phase 4 - Parameter System (COMPLETE)
2. → Phase 5 - ComponentBase (uses parameters)
3. → Phase 6 - Connection System (connects components)
4. → Phase 7 - Execution Engine (runs components)

---

## Code Snippets Library

### Complete Component Example
```python
from vse_py.core.parameter import IntParameter, FloatParameter, StringParameter

class ProcessorWithParams:
    def __init__(self):
        # Define parameters
        self.param_iterations = IntParameter(
            "iterations",
            default=10,
            min_val=1,
            max_val=1000,
            description="Number of processing iterations"
        )

        self.param_threshold = FloatParameter(
            "threshold",
            default=0.5,
            min_val=0.0,
            max_val=1.0,
            description="Detection threshold"
        )

        self.param_mode = StringParameter(
            "mode",
            default="normal",
            description="Processing mode"
        )

    def process(self):
        # Get parameter values
        iterations = self.param_iterations.get_value()
        threshold = self.param_threshold.get_value()
        mode = self.param_mode.get_value()

        # Use in processing
        for i in range(iterations):
            value = (i + 1) / iterations
            if value > threshold:
                print(f"Iteration {i}: mode={mode}, value={value:.2f}")

    def save(self):
        """Serialize parameters to dict"""
        return {
            "iterations": self.param_iterations.to_json(),
            "threshold": self.param_threshold.to_json(),
            "mode": self.param_mode.to_json()
        }

    def load(self, data):
        """Deserialize parameters from dict"""
        if "iterations" in data:
            self.param_iterations.from_json(data["iterations"])
        if "threshold" in data:
            self.param_threshold.from_json(data["threshold"])
        if "mode" in data:
            self.param_mode.from_json(data["mode"])
```

---

## Resources

- **Implementation**: `/home/ag/Desktop/sandbox/VSE_PY/vse_py/core/parameter.py`
- **Tests**: `/home/ag/Desktop/sandbox/VSE_PY/tests/test_core/test_parameter.py`
- **Documentation**: `PARAMETER_IMPLEMENTATION.md`
