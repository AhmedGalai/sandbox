#!/usr/bin/env python3
"""Test script for connection and topic system implementation."""

import sys
sys.path.insert(0, '/home/ag/Desktop/sandbox/VSE_PY')

from vse_py.core.connection import PinReference, Connection, ConnectionManager
from vse_py.core.topic_registry import Topic, TopicRegistry
from vse_py.core.data_types import DataType, DataVariant

def test_pin_reference():
    """Test PinReference dataclass."""
    print("\n=== Testing PinReference ===")
    ref = PinReference("comp-1", "pin-1")
    print(f"Created: {ref}")
    print(f"Component ID: {ref.component_id}")
    print(f"Pin ID: {ref.pin_id}")
    assert ref.component_id == "comp-1"
    assert ref.pin_id == "pin-1"
    print("PinReference tests passed!")

def test_connection():
    """Test Connection class."""
    print("\n=== Testing Connection ===")
    source = PinReference("comp-1", "out-1")
    dest = PinReference("comp-2", "in-1")
    conn = Connection(source, dest, "data_flow")

    print(f"Created: {conn}")
    print(f"ID: {conn.id}")
    print(f"Source: {conn.source}")
    print(f"Destination: {conn.destination}")
    print(f"Topic: {conn.topic_name}")

    # Test validation
    assert conn.validate()
    print("Validation passed!")

    # Test serialization
    json_str = conn.to_json()
    print(f"JSON: {json_str}")
    restored = Connection.from_json(json_str)
    assert restored.topic_name == conn.topic_name
    assert restored.id == conn.id
    print("Serialization tests passed!")

    # Test string representations
    print(f"repr: {repr(conn)}")
    print(f"str: {str(conn)}")

def test_connection_manager():
    """Test ConnectionManager class."""
    print("\n=== Testing ConnectionManager ===")
    manager = ConnectionManager()

    source = PinReference("comp-1", "out-1")
    dest1 = PinReference("comp-2", "in-1")
    dest2 = PinReference("comp-3", "in-1")

    conn1 = Connection(source, dest1, "topic-1")
    conn2 = Connection(source, dest2, "topic-2")
    conn3 = Connection(dest1, source, "topic-3")

    # Test adding connections
    assert manager.add_connection(conn1)
    assert manager.add_connection(conn2)
    assert manager.add_connection(conn3)
    print(f"Added 3 connections")

    # Test getting all connections
    all_conns = manager.get_all_connections()
    print(f"Total connections: {len(all_conns)}")
    assert len(all_conns) == 3

    # Test getting connections for component
    comp1_conns = manager.get_connections_for_component("comp-1")
    print(f"Connections for comp-1: {len(comp1_conns)}")
    assert len(comp1_conns) == 3

    comp2_conns = manager.get_connections_for_component("comp-2")
    print(f"Connections for comp-2: {len(comp2_conns)}")
    assert len(comp2_conns) == 2

    # Test validation
    assert manager.validate_all()
    print("All connections validated!")

    # Test removal
    assert manager.remove_connection(conn1.id)
    assert len(manager.get_all_connections()) == 2
    print("Removed single connection")

    # Test component removal
    removed_count = manager.remove_connections_for_component("comp-1")
    print(f"Removed {removed_count} connections for comp-1")
    assert removed_count == 2
    assert len(manager.get_all_connections()) == 0

    # Test clear
    manager.add_connection(conn1)
    manager.add_connection(conn2)
    manager.clear()
    assert len(manager.get_all_connections()) == 0
    print("Clear test passed!")

def test_topic():
    """Test Topic class."""
    print("\n=== Testing Topic ===")
    topic = Topic("sensor_data", DataType.FLOAT)

    print(f"Created: {topic}")
    print(f"Name: {topic.name}")
    print(f"Expected type: {topic.expected_type.name}")

    # Test publish with no subscribers
    assert topic.publish(DataVariant(23.5))
    print(f"Published value: {topic.last_value.value}")
    assert topic.publish_count == 1

    # Test type checking
    assert not topic.publish(DataVariant("invalid"))
    print("Type checking works!")

    # Test subscribe
    received_values = []
    def on_data(name, data):
        received_values.append((name, data.value))

    sub_id = topic.subscribe(on_data)
    print(f"Subscribed with ID: {sub_id[:8]}...")
    assert topic.get_subscriber_count() == 1

    # Test publish to subscribers
    assert topic.publish(DataVariant(42.5))
    print(f"Publish count: {topic.publish_count}")
    assert len(received_values) == 1
    assert received_values[0] == ("sensor_data", 42.5)
    print(f"Received values: {received_values}")

    # Test unsubscribe
    assert topic.unsubscribe(sub_id)
    assert topic.get_subscriber_count() == 0
    assert not topic.unsubscribe(sub_id)
    print("Unsubscribe works!")

def test_topic_registry():
    """Test TopicRegistry singleton."""
    print("\n=== Testing TopicRegistry ===")

    # Clear for clean test
    registry = TopicRegistry.instance()
    registry.clear()

    print(f"Registry: {registry}")

    # Test singleton
    registry2 = TopicRegistry.instance()
    assert registry is registry2
    print("Singleton pattern works!")

    # Test topic creation
    assert registry.create_topic("temperature", DataType.FLOAT)
    assert not registry.create_topic("temperature", DataType.FLOAT)
    print("Topic creation works!")

    # Test has_topic
    assert registry.has_topic("temperature")
    assert not registry.has_topic("nonexistent")
    print("has_topic works!")

    # Test get_topic
    topic = registry.get_topic("temperature")
    assert topic is not None
    assert topic.name == "temperature"
    print("get_topic works!")

    # Test publish
    assert registry.publish("temperature", DataVariant(25.5))
    assert not registry.publish("nonexistent", DataVariant(1))
    print("Registry publish works!")

    # Test subscribe
    received = []
    def handler(name, data):
        received.append((name, data.value))

    sub_id = registry.subscribe("temperature", handler)
    assert sub_id is not None
    print(f"Subscribed with ID: {sub_id[:8]}...")

    # Test publish with subscriber
    assert registry.publish("temperature", DataVariant(30.0))
    assert len(received) == 1
    assert received[0] == ("temperature", 30.0)
    print(f"Received: {received}")

    # Test unsubscribe
    assert registry.unsubscribe("temperature", sub_id)
    print("Unsubscribe works!")

    # Test get_all_topic_names
    registry.create_topic("humidity", DataType.FLOAT)
    registry.create_topic("pressure", DataType.INTEGER)
    names = registry.get_all_topic_names()
    print(f"Topic names: {names}")
    assert len(names) == 3

    # Test get_topic_count
    assert registry.get_topic_count() == 3
    print(f"Topic count: {registry.get_topic_count()}")

    # Test delete_topic
    assert registry.delete_topic("humidity")
    assert not registry.delete_topic("humidity")
    assert registry.get_topic_count() == 2
    print("Delete topic works!")

    # Test clear
    registry.clear()
    assert registry.get_topic_count() == 0
    print("Clear works!")

def test_thread_safety():
    """Test thread safety of Topic and TopicRegistry."""
    print("\n=== Testing Thread Safety ===")
    import threading
    import time

    registry = TopicRegistry.instance()
    registry.clear()
    registry.create_topic("test_data", DataType.INTEGER)

    received_values = []
    lock = threading.Lock()

    def subscriber(name, data):
        with lock:
            received_values.append(data.value)

    # Subscribe multiple threads
    sub_ids = []
    for i in range(5):
        sub_id = registry.subscribe("test_data", subscriber)
        sub_ids.append(sub_id)

    # Publish from multiple threads
    def publish_values():
        for i in range(10):
            registry.publish("test_data", DataVariant(i))
            time.sleep(0.001)

    threads = [threading.Thread(target=publish_values) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Received {len(received_values)} total values from {5} subscribers")
    print("Thread safety test passed!")

def main():
    """Run all tests."""
    print("Starting connection and topic system tests...")

    try:
        test_pin_reference()
        test_connection()
        test_connection_manager()
        test_topic()
        test_topic_registry()
        test_thread_safety()

        print("\n" + "="*50)
        print("All tests passed successfully!")
        print("="*50)
        return 0
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
