#include "core/Pin.h"
#include <QUuid>
#include <algorithm>

namespace VSE {

// ============================================================================
// Utility Functions
// ============================================================================

std::string dataTypeToString(DataType type) {
    switch (type) {
        case DataType::Boolean: return "Boolean";
        case DataType::Integer: return "Integer";
        case DataType::Float:   return "Float";
        case DataType::String:  return "String";
        case DataType::Json:    return "Json";
        case DataType::Any:     return "Any";
        default:                return "Unknown";
    }
}

DataType stringToDataType(const std::string& str) {
    if (str == "Boolean") return DataType::Boolean;
    if (str == "Integer") return DataType::Integer;
    if (str == "Float")   return DataType::Float;
    if (str == "String")  return DataType::String;
    if (str == "Json")    return DataType::Json;
    if (str == "Any")     return DataType::Any;
    return DataType::Any; // Default to Any for unknown types
}

// ============================================================================
// Pin Base Class
// ============================================================================

Pin::Pin(const QString& name, PinType type, DataType dataType)
    : m_name(name),
      m_id(QUuid::createUuid().toString(QUuid::WithoutBraces)),
      m_type(type),
      m_dataType(dataType) {
}

nlohmann::json Pin::toJson() const {
    nlohmann::json j;
    j["id"] = m_id.toStdString();
    j["name"] = m_name.toStdString();
    j["type"] = (m_type == PinType::Input) ? "input" : "output";
    j["dataType"] = dataTypeToString(m_dataType);
    return j;
}

void Pin::fromJson(const nlohmann::json& json) {
    if (json.contains("id") && json["id"].is_string()) {
        m_id = QString::fromStdString(json["id"].get<std::string>());
    }
    if (json.contains("name") && json["name"].is_string()) {
        m_name = QString::fromStdString(json["name"].get<std::string>());
    }
}

// ============================================================================
// InputPin
// ============================================================================

InputPin::InputPin(const QString& name, DataType dataType)
    : Pin(name, PinType::Input, dataType),
      m_connectedPin(nullptr) {
}

bool InputPin::isConnected() const {
    return m_connectedPin != nullptr;
}

bool InputPin::connectTo(std::shared_ptr<OutputPin> outputPin) {
    if (!outputPin) {
        return false;
    }

    // Check type compatibility
    if (!isCompatible(outputPin->getDataType())) {
        return false;
    }

    // Disconnect existing connection
    if (m_connectedPin) {
        disconnect();
    }

    // Establish new connection
    m_connectedPin = outputPin;
    return true;
}

void InputPin::disconnect() {
    m_connectedPin = nullptr;
    m_data = QVariant(); // Clear data
}

void InputPin::receiveData(const QVariant& data) {
    m_data = data;

    // Invoke callback if set
    if (m_dataCallback) {
        m_dataCallback(data);
    }
}

bool InputPin::isCompatible(DataType otherType) const {
    // Any type is compatible with everything
    if (m_dataType == DataType::Any || otherType == DataType::Any) {
        return true;
    }

    // Same types are compatible
    if (m_dataType == otherType) {
        return true;
    }

    // Numeric types can be compatible
    if ((m_dataType == DataType::Integer || m_dataType == DataType::Float) &&
        (otherType == DataType::Integer || otherType == DataType::Float)) {
        return true;
    }

    return false;
}

nlohmann::json InputPin::toJson() const {
    nlohmann::json j = Pin::toJson();

    // Store connected pin ID if connected
    if (m_connectedPin) {
        j["connectedPinId"] = m_connectedPin->getId().toStdString();
    }

    return j;
}

void InputPin::fromJson(const nlohmann::json& json) {
    Pin::fromJson(json);
    // Note: Connection restoration is handled at a higher level
    // since we need access to all pins to resolve IDs
}

// ============================================================================
// OutputPin
// ============================================================================

OutputPin::OutputPin(const QString& name, DataType dataType)
    : Pin(name, PinType::Output, dataType) {
}

bool OutputPin::isConnected() const {
    return !m_connectedPins.empty();
}

bool OutputPin::addConnection(std::shared_ptr<InputPin> inputPin) {
    if (!inputPin) {
        return false;
    }

    // Check if already connected
    auto it = std::find(m_connectedPins.begin(), m_connectedPins.end(), inputPin);
    if (it != m_connectedPins.end()) {
        return false; // Already connected
    }

    // Check type compatibility
    if (!inputPin->isCompatible(m_dataType)) {
        return false;
    }

    // Add connection
    m_connectedPins.push_back(inputPin);
    return true;
}

void OutputPin::removeConnection(std::shared_ptr<InputPin> inputPin) {
    auto it = std::find(m_connectedPins.begin(), m_connectedPins.end(), inputPin);
    if (it != m_connectedPins.end()) {
        m_connectedPins.erase(it);
    }
}

void OutputPin::disconnectAll() {
    m_connectedPins.clear();
}

void OutputPin::transmitData(const QVariant& data) {
    m_data = data;

    // Transmit to all connected input pins
    for (auto& inputPin : m_connectedPins) {
        if (inputPin) {
            inputPin->receiveData(data);
        }
    }
}

nlohmann::json OutputPin::toJson() const {
    nlohmann::json j = Pin::toJson();

    // Store connected pin IDs
    nlohmann::json connections = nlohmann::json::array();
    for (const auto& inputPin : m_connectedPins) {
        if (inputPin) {
            connections.push_back(inputPin->getId().toStdString());
        }
    }
    j["connectedPinIds"] = connections;

    return j;
}

void OutputPin::fromJson(const nlohmann::json& json) {
    Pin::fromJson(json);
    // Note: Connection restoration is handled at a higher level
    // since we need access to all pins to resolve IDs
}

} // namespace VSE
