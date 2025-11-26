/**
 * @file topic_system_example.cpp
 * @brief Example demonstrating the VSE topic/data bus and connection system
 *
 * This example shows:
 * - Creating and managing topics
 * - Publishing and subscribing to data
 * - Creating connections between components
 * - Type checking and validation
 * - Serialization and deserialization
 */

#include "core/TopicRegistry.h"
#include "core/Connection.h"
#include "core/DataVariant.h"
#include "core/TypeConverter.h"
#include <iostream>
#include <iomanip>

using namespace VSE::Core;

// Helper function to print section headers
void printHeader(const std::string& title) {
    std::cout << "\n" << std::string(60, '=') << "\n";
    std::cout << title << "\n";
    std::cout << std::string(60, '=') << "\n";
}

// Example 1: Basic Topic Creation and Publishing
void example1_BasicTopics() {
    printHeader("Example 1: Basic Topic Creation and Publishing");

    auto& registry = TopicRegistry::instance();

    // Create topics with type constraints
    registry.createTopic("sensors/temperature", DataType::Float);
    registry.createTopic("sensors/humidity", DataType::Double);
    registry.createTopic("control/motor_speed", DataType::Int);
    registry.createTopic("debug/messages", DataType::String);

    std::cout << "Created " << registry.getTopicCount() << " topics:\n";
    for (const auto& name : registry.getTopicNames()) {
        std::cout << "  - " << name << "\n";
    }

    // Publish some data
    std::cout << "\nPublishing data...\n";
    registry.publish("sensors/temperature", DataVariant(25.5f));
    registry.publish("sensors/humidity", DataVariant(60.3));
    registry.publish("control/motor_speed", DataVariant(1500));
    registry.publish("debug/messages", DataVariant("System initialized"));

    // Retrieve last values
    std::cout << "\nLast values:\n";
    auto temp = registry.getLastValue("sensors/temperature");
    if (temp) {
        std::cout << "  Temperature: " << temp->toFloat() << " C\n";
    }

    auto humidity = registry.getLastValue("sensors/humidity");
    if (humidity) {
        std::cout << "  Humidity: " << humidity->toDouble() << " %\n";
    }

    auto speed = registry.getLastValue("control/motor_speed");
    if (speed) {
        std::cout << "  Motor Speed: " << speed->toInt() << " RPM\n";
    }
}

// Example 2: Subscriptions and Callbacks
void example2_Subscriptions() {
    printHeader("Example 2: Topic Subscriptions");

    auto& registry = TopicRegistry::instance();
    registry.clear(); // Clear from previous example

    // Create a data processing topic
    registry.createTopic("data/stream", DataType::Int);

    // Subscribe with lambda callbacks
    std::cout << "Setting up subscribers...\n";

    uint64_t sub1 = registry.subscribe("data/stream",
        [](const std::string& topic, const DataVariant& data) {
            std::cout << "  [Subscriber 1] Received on '" << topic
                     << "': " << data.toInt() << "\n";
        });

    uint64_t sub2 = registry.subscribe("data/stream",
        [](const std::string& topic, const DataVariant& data) {
            std::cout << "  [Subscriber 2] Processing: " << data.toInt() * 2 << "\n";
        });

    uint64_t sub3 = registry.subscribe("data/stream",
        [](const std::string& topic, const DataVariant& data) {
            if (data.toInt() > 50) {
                std::cout << "  [Subscriber 3] WARNING: Value exceeds threshold!\n";
            }
        });

    std::cout << "Subscribers active: "
              << registry.getSubscriberCount("data/stream") << "\n";

    // Publish data - all subscribers will be notified
    std::cout << "\nPublishing values...\n";
    registry.publish("data/stream", DataVariant(42));
    registry.publish("data/stream", DataVariant(75));
    registry.publish("data/stream", DataVariant(10));

    // Unsubscribe one
    std::cout << "\nUnsubscribing subscriber 2...\n";
    registry.unsubscribe("data/stream", sub2);

    std::cout << "Publishing after unsubscribe...\n";
    registry.publish("data/stream", DataVariant(100));
}

// Example 3: Type Checking and Validation
void example3_TypeChecking() {
    printHeader("Example 3: Type Checking and Validation");

    auto& registry = TopicRegistry::instance();
    registry.clear();

    // Create strongly-typed topic
    registry.createTopic("typed/float_data", DataType::Float);

    std::cout << "Created typed topic (Float only)\n";

    // Valid publish
    bool result1 = registry.publish("typed/float_data", DataVariant(3.14f));
    std::cout << "Publishing Float: " << (result1 ? "SUCCESS" : "FAILED") << "\n";

    // Invalid publish (wrong type)
    bool result2 = registry.publish("typed/float_data", DataVariant(42));
    std::cout << "Publishing Int to Float topic: " << (result2 ? "SUCCESS" : "FAILED") << "\n";

    // Create untyped topic (accepts any type)
    registry.createTopic("untyped/any_data", DataType::Null);
    std::cout << "\nCreated untyped topic (accepts any type)\n";

    registry.publish("untyped/any_data", DataVariant(42));
    registry.publish("untyped/any_data", DataVariant(3.14f));
    registry.publish("untyped/any_data", DataVariant("Hello"));
    registry.publish("untyped/any_data", DataVariant(true));
    std::cout << "All types accepted!\n";
}

// Example 4: Connections Between Components
void example4_Connections() {
    printHeader("Example 4: Component Connections");

    // Create pin references
    PinReference outputPin("sensor_component_1", "temperature_out", DataType::Float);
    PinReference inputPin("display_component_2", "value_in", DataType::Float);

    // Create connection through a topic
    Connection conn1(outputPin, inputPin, "sensor/temp_data");

    std::cout << "Created connection:\n";
    std::cout << "  ID: " << conn1.getConnectionId() << "\n";
    std::cout << "  Topic: " << conn1.getTopicName() << "\n";
    std::cout << "  Valid: " << (conn1.isValid() ? "YES" : "NO") << "\n";

    // Test type mismatch
    PinReference wrongTypePin("processor_component_3", "count_in", DataType::Int);
    Connection conn2(outputPin, wrongTypePin, "sensor/temp_data");

    std::cout << "\nConnection with type mismatch:\n";
    std::cout << "  Valid: " << (conn2.isValid() ? "YES" : "NO") << "\n";
    if (!conn2.isValid()) {
        std::cout << "  Error: " << conn2.getErrorMessage() << "\n";
    }

    // Connection manager
    ConnectionManager manager;
    manager.addConnection(conn1);

    std::cout << "\nConnection Manager:\n";
    std::cout << "  Total connections: " << manager.getConnectionCount() << "\n";

    // Find connections for component
    auto connections = manager.getConnectionsForComponent("sensor_component_1");
    std::cout << "  Connections for sensor_component_1: " << connections.size() << "\n";
}

// Example 5: Serialization
void example5_Serialization() {
    printHeader("Example 5: Serialization and Persistence");

    auto& registry = TopicRegistry::instance();
    registry.clear();

    // Create and populate topics
    registry.createTopic("app/state", DataType::String);
    registry.createTopic("app/counter", DataType::Int);
    registry.publish("app/state", DataVariant("running"));
    registry.publish("app/counter", DataVariant(42));

    // Export to JSON
    nlohmann::json exportData = registry.exportToJson();
    std::cout << "Exported topics to JSON:\n";
    std::cout << std::setw(2) << exportData << "\n";

    // Serialize a connection
    PinReference src("comp1", "out", DataType::Int);
    PinReference dst("comp2", "in", DataType::Int);
    Connection conn(src, dst, "data_channel");

    nlohmann::json connJson = conn.toJson();
    std::cout << "\nSerialized connection:\n";
    std::cout << std::setw(2) << connJson << "\n";

    // Deserialize
    Connection restoredConn = Connection::fromJson(connJson);
    std::cout << "\nDeserialized connection:\n";
    std::cout << "  ID: " << restoredConn.getConnectionId() << "\n";
    std::cout << "  Valid: " << (restoredConn.isValid() ? "YES" : "NO") << "\n";
}

// Example 6: Data Variant Conversions
void example6_DataVariantConversions() {
    printHeader("Example 6: DataVariant Type Conversions");

    // Create variants of different types
    DataVariant intVal(42);
    DataVariant floatVal(3.14f);
    DataVariant stringVal("123");
    DataVariant boolVal(true);

    std::cout << "Type conversions:\n";
    std::cout << "  Int(42) -> Float: " << intVal.toFloat() << "\n";
    std::cout << "  Int(42) -> String: " << intVal.toString() << "\n";
    std::cout << "  Int(42) -> Bool: " << (intVal.toBool() ? "true" : "false") << "\n";

    std::cout << "\n  String(\"123\") -> Int: " << stringVal.toInt() << "\n";
    std::cout << "  String(\"123\") -> Float: " << stringVal.toFloat() << "\n";

    std::cout << "\n  Bool(true) -> Int: " << boolVal.toInt() << "\n";
    std::cout << "  Bool(true) -> String: " << boolVal.toString() << "\n";

    // JSON conversion
    nlohmann::json jsonData = {
        {"name", "temperature_sensor"},
        {"value", 25.5},
        {"unit", "celsius"}
    };
    DataVariant jsonVariant(jsonData);

    std::cout << "\nJSON variant:\n";
    std::cout << "  Type: " << jsonVariant.getTypeString() << "\n";
    std::cout << "  Content: " << jsonVariant.getJson().dump() << "\n";

    // Serialize to JSON with type info
    nlohmann::json serialized = floatVal.toJson();
    std::cout << "\nSerialized DataVariant:\n";
    std::cout << std::setw(2) << serialized << "\n";

    // Deserialize
    DataVariant restored = DataVariant::fromJson(serialized);
    std::cout << "Restored value: " << restored.toFloat() << "\n";
}

// Example 7: Complete Data Flow
void example7_CompleteDataFlow() {
    printHeader("Example 7: Complete Data Flow Simulation");

    auto& registry = TopicRegistry::instance();
    registry.clear();

    // Simulate sensor -> processor -> actuator flow
    registry.createTopic("sensor/raw_data", DataType::Int);
    registry.createTopic("processor/filtered_data", DataType::Float);
    registry.createTopic("actuator/command", DataType::String);

    std::cout << "Setting up data flow pipeline...\n\n";

    // Sensor subscriber (converts raw to filtered)
    registry.subscribe("sensor/raw_data",
        [&registry](const std::string&, const DataVariant& data) {
            int rawValue = data.toInt();
            float filtered = rawValue * 0.95f; // Simple filter
            std::cout << "  [Processor] Raw: " << rawValue
                     << " -> Filtered: " << filtered << "\n";
            registry.publish("processor/filtered_data", DataVariant(filtered));
        });

    // Processor subscriber (generates commands)
    registry.subscribe("processor/filtered_data",
        [&registry](const std::string&, const DataVariant& data) {
            float value = data.toFloat();
            std::string command = value > 50.0f ? "ACTIVATE" : "STANDBY";
            std::cout << "  [Controller] Value: " << value
                     << " -> Command: " << command << "\n";
            registry.publish("actuator/command", DataVariant(command));
        });

    // Actuator subscriber (executes commands)
    registry.subscribe("actuator/command",
        [](const std::string&, const DataVariant& data) {
            std::string command = data.toString();
            std::cout << "  [Actuator] Executing: " << command << "\n";
        });

    std::cout << "Pipeline ready. Sending sensor data...\n\n";

    // Simulate sensor readings
    registry.publish("sensor/raw_data", DataVariant(30));
    std::cout << "\n";
    registry.publish("sensor/raw_data", DataVariant(60));
    std::cout << "\n";
    registry.publish("sensor/raw_data", DataVariant(45));
}

int main() {
    std::cout << "VSE Topic System and Connection Examples\n";
    std::cout << "=========================================\n";

    try {
        example1_BasicTopics();
        example2_Subscriptions();
        example3_TypeChecking();
        example4_Connections();
        example5_Serialization();
        example6_DataVariantConversions();
        example7_CompleteDataFlow();

        printHeader("All Examples Completed Successfully!");
        return 0;

    } catch (const std::exception& e) {
        std::cerr << "\nERROR: " << e.what() << "\n";
        return 1;
    }
}
