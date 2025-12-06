# VSE_PY Connection and Topic System - Quick Reference

## Connection System (connection.py)

### PinReference
```python
from vse_py.core.connection import PinReference

# Create a pin reference
ref = PinReference("component-uuid", "pin-uuid")
```

### Connection
```python
from vse_py.core.connection import Connection, PinReference

# Create a connection
source = PinReference("comp-1", "out-1")
dest = PinReference("comp-2", "in-1")
conn = Connection(source, dest, "data_channel")

# Validate
assert conn.validate()

# Serialize
json_str = conn.to_json()
restored = Connection.from_json(json_str)

# String representations
print(str(conn))   # "comp-1/out-1 -> comp-2/in-1 (data_channel)"
print(repr(conn))  # Detailed representation
```

### ConnectionManager
```python
from vse_py.core.connection import ConnectionManager, Connection, PinReference

# Create manager
manager = ConnectionManager()

# Add connections
conn = Connection(source, dest, "topic")
manager.add_connection(conn)

# Query connections
all_conns = manager.get_all_connections()
comp_conns = manager.get_connections_for_component("comp-1")

# Remove connections
manager.remove_connection(conn.id)
manager.remove_connections_for_component("comp-1")

# Cleanup
manager.validate_all()
manager.clear()
```

## Topic System (topic_registry.py)

### Topic
```python
from vse_py.core.topic_registry import Topic
from vse_py.core.data_types import DataType, DataVariant

# Create topic
topic = Topic("sensor_data", DataType.FLOAT)

# Publish data
topic.publish(DataVariant(42.5))

# Subscribe to updates
def on_data(topic_name: str, data: DataVariant):
    print(f"{topic_name}: {data.value}")

sub_id = topic.subscribe(on_data)

# Unsubscribe
topic.unsubscribe(sub_id)

# Check statistics
print(topic.publish_count)
print(topic.last_value)
```

### TopicRegistry (Singleton)
```python
from vse_py.core.topic_registry import TopicRegistry
from vse_py.core.data_types import DataType, DataVariant

# Get singleton instance
registry = TopicRegistry.instance()

# Create topics
registry.create_topic("temperature", DataType.FLOAT)
registry.create_topic("status", DataType.STRING)

# Publish
registry.publish("temperature", DataVariant(25.5))

# Subscribe
def handler(name, data):
    print(f"Got {name}: {data.value}")

sub_id = registry.subscribe("temperature", handler)

# Unsubscribe
registry.unsubscribe("temperature", sub_id)

# Discovery
registry.has_topic("temperature")           # True
topic = registry.get_topic("temperature")   # Get Topic instance
names = registry.get_all_topic_names()      # ['temperature', 'status']
registry.get_topic_count()                  # 2

# Cleanup
registry.delete_topic("temperature")
registry.clear()  # Remove all topics
```

## Type System Integration

Topics support all DataTypes:
- `DataType.NULL`: No value
- `DataType.BOOLEAN`: True/False
- `DataType.INTEGER`: Whole numbers
- `DataType.FLOAT`: Decimal numbers
- `DataType.STRING`: Text
- `DataType.JSON`: Objects/lists
- `DataType.ANY`: Any type (flexible)

```python
# Type checking on publish
registry.create_topic("count", DataType.INTEGER)
registry.publish("count", DataVariant(42))      # OK
registry.publish("count", DataVariant("text"))  # FAILS (returns False)
```

## Thread Safety

Both Topic and TopicRegistry are thread-safe:
- Safe to call from multiple threads
- Callbacks invoked safely
- No deadlocks or race conditions

```python
import threading

def publisher():
    registry.publish("data", DataVariant(42))

threads = [threading.Thread(target=publisher) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Common Patterns

### Pub/Sub Pattern
```python
registry = TopicRegistry.instance()
registry.create_topic("events", DataType.STRING)

# Multiple subscribers
def logger(name, data):
    print(f"LOG: {data.value}")

def uploader(name, data):
    print(f"UPLOAD: {data.value}")

sub1 = registry.subscribe("events", logger)
sub2 = registry.subscribe("events", uploader)

# Publish once, notify all subscribers
registry.publish("events", DataVariant("system started"))
```

### Connection Tracking
```python
manager = ConnectionManager()

# Track component connections
for conn in manager.get_connections_for_component("component-id"):
    print(f"Connected via: {conn.topic_name}")

# Clean up on removal
manager.remove_connections_for_component("component-id")
```

### Topic Metadata
```python
registry = TopicRegistry.instance()

for topic_name in registry.get_all_topic_names():
    topic = registry.get_topic(topic_name)
    print(f"{topic.name}: {topic.get_subscriber_count()} subscribers")
    print(f"  Type: {topic.expected_type.name}")
    print(f"  Last value: {topic.last_value}")
```

## Error Handling

Common exceptions:
- `TypeError`: Invalid argument types
- `ValueError`: Invalid argument values
- `KeyError`: Topic or connection not found

```python
try:
    registry.create_topic("", DataType.FLOAT)  # ValueError
except ValueError as e:
    print(f"Invalid topic name: {e}")

try:
    registry.publish("nonexistent", DataVariant(1))  # Returns False
except Exception as e:
    print(f"Publish failed: {e}")
```
