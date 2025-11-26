/**
 * @file Connection.cpp
 * @brief Implementation of connection management system
 */

#include "core/Connection.h"
#include "core/TopicRegistry.h"
#include <algorithm>
#include <sstream>
#include <set>

namespace VSE {
namespace Core {

// ============================================================================
// PinReference Implementation
// ============================================================================

nlohmann::json PinReference::toJson() const {
    nlohmann::json j;
    j["componentId"] = componentId;
    j["pinId"] = pinId;

    // Convert DataType to string
    std::string typeStr;
    switch (dataType) {
        case DataType::Null:    typeStr = "Null"; break;
        case DataType::Bool:    typeStr = "Bool"; break;
        case DataType::Int:     typeStr = "Int"; break;
        case DataType::Float:   typeStr = "Float"; break;
        case DataType::Double:  typeStr = "Double"; break;
        case DataType::String:  typeStr = "String"; break;
        case DataType::Json:    typeStr = "Json"; break;
    }
    j["dataType"] = typeStr;

    return j;
}

PinReference PinReference::fromJson(const nlohmann::json& j) {
    PinReference ref;

    if (j.contains("componentId")) {
        ref.componentId = j["componentId"].get<std::string>();
    }

    if (j.contains("pinId")) {
        ref.pinId = j["pinId"].get<std::string>();
    }

    if (j.contains("dataType")) {
        std::string typeStr = j["dataType"].get<std::string>();

        if (typeStr == "Null") ref.dataType = DataType::Null;
        else if (typeStr == "Bool") ref.dataType = DataType::Bool;
        else if (typeStr == "Int") ref.dataType = DataType::Int;
        else if (typeStr == "Float") ref.dataType = DataType::Float;
        else if (typeStr == "Double") ref.dataType = DataType::Double;
        else if (typeStr == "String") ref.dataType = DataType::String;
        else if (typeStr == "Json") ref.dataType = DataType::Json;
        else ref.dataType = DataType::Null;
    }

    return ref;
}

// ============================================================================
// Connection Implementation
// ============================================================================

Connection::Connection()
    : m_state(ConnectionState::Disconnected)
{
}

Connection::Connection(const PinReference& source,
                       const PinReference& destination,
                       const std::string& topicName)
    : m_source(source)
    , m_destination(destination)
    , m_topicName(topicName)
    , m_state(ConnectionState::Invalid)
{
    // Validate upon construction
    if (validate()) {
        m_state = ConnectionState::Valid;
    } else {
        updateErrorMessage();
    }
}

bool Connection::validateTypes() const {
    // If either type is Null (untyped), connection is compatible
    if (m_source.dataType == DataType::Null || m_destination.dataType == DataType::Null) {
        return true;
    }

    // Types must match exactly for strict type checking
    // Could be extended to allow compatible conversions (int->float, etc.)
    return m_source.dataType == m_destination.dataType;
}

bool Connection::validate(bool checkTopicExists) const {
    // Check pin references are valid
    if (!m_source.isValid() || !m_destination.isValid()) {
        return false;
    }

    // Check topic name is not empty
    if (m_topicName.empty()) {
        return false;
    }

    // Check type compatibility
    if (!validateTypes()) {
        return false;
    }

    // Optionally check if topic exists
    if (checkTopicExists) {
        auto& registry = TopicRegistry::instance();
        if (!registry.hasTopic(m_topicName)) {
            return false;
        }

        // Check topic type matches connection types
        DataType topicType = registry.getTopicType(m_topicName);
        if (topicType != DataType::Null) {
            // Topic is typed - check compatibility
            if (m_source.dataType != DataType::Null && m_source.dataType != topicType) {
                return false;
            }
            if (m_destination.dataType != DataType::Null && m_destination.dataType != topicType) {
                return false;
            }
        }
    }

    return true;
}

void Connection::disconnect() {
    m_state = ConnectionState::Disconnected;
    m_errorMessage = "Connection has been disconnected";
}

bool Connection::reconnect() {
    if (validate(true)) {
        m_state = ConnectionState::Valid;
        m_errorMessage.clear();
        return true;
    } else {
        m_state = ConnectionState::Invalid;
        updateErrorMessage();
        return false;
    }
}

std::string Connection::getConnectionId() const {
    std::ostringstream oss;
    oss << m_source.componentId << ":" << m_source.pinId
        << "->" << m_destination.componentId << ":" << m_destination.pinId;
    return oss.str();
}

std::string Connection::getErrorMessage() const {
    if (m_state == ConnectionState::Valid) {
        return "";
    }
    if (!m_errorMessage.empty()) {
        return m_errorMessage;
    }
    updateErrorMessage();
    return m_errorMessage;
}

void Connection::updateErrorMessage() const {
    if (m_state == ConnectionState::Valid) {
        m_errorMessage.clear();
        return;
    }

    if (m_state == ConnectionState::Disconnected) {
        m_errorMessage = "Connection is disconnected";
        return;
    }

    // Build detailed error message for invalid state
    std::ostringstream oss;
    oss << "Invalid connection: ";

    if (!m_source.isValid()) {
        oss << "Invalid source pin reference. ";
    }

    if (!m_destination.isValid()) {
        oss << "Invalid destination pin reference. ";
    }

    if (m_topicName.empty()) {
        oss << "Empty topic name. ";
    }

    if (!validateTypes()) {
        oss << "Type mismatch (source: " << static_cast<int>(m_source.dataType)
            << ", destination: " << static_cast<int>(m_destination.dataType) << "). ";
    }

    m_errorMessage = oss.str();
}

nlohmann::json Connection::toJson() const {
    nlohmann::json j;
    j["source"] = m_source.toJson();
    j["destination"] = m_destination.toJson();
    j["topicName"] = m_topicName;

    std::string stateStr;
    switch (m_state) {
        case ConnectionState::Valid:        stateStr = "Valid"; break;
        case ConnectionState::Invalid:      stateStr = "Invalid"; break;
        case ConnectionState::Disconnected: stateStr = "Disconnected"; break;
    }
    j["state"] = stateStr;

    if (!m_errorMessage.empty()) {
        j["errorMessage"] = m_errorMessage;
    }

    return j;
}

Connection Connection::fromJson(const nlohmann::json& j) {
    if (!j.contains("source") || !j.contains("destination") || !j.contains("topicName")) {
        throw std::runtime_error("Connection::fromJson: Missing required fields");
    }

    PinReference source = PinReference::fromJson(j["source"]);
    PinReference destination = PinReference::fromJson(j["destination"]);
    std::string topicName = j["topicName"].get<std::string>();

    Connection conn(source, destination, topicName);

    // Restore state if provided
    if (j.contains("state")) {
        std::string stateStr = j["state"].get<std::string>();
        if (stateStr == "Valid") {
            conn.m_state = ConnectionState::Valid;
        } else if (stateStr == "Invalid") {
            conn.m_state = ConnectionState::Invalid;
        } else if (stateStr == "Disconnected") {
            conn.m_state = ConnectionState::Disconnected;
        }
    }

    return conn;
}

bool Connection::operator==(const Connection& other) const {
    return m_source == other.m_source &&
           m_destination == other.m_destination &&
           m_topicName == other.m_topicName;
}

bool Connection::operator!=(const Connection& other) const {
    return !(*this == other);
}

// ============================================================================
// ConnectionManager Implementation
// ============================================================================

bool ConnectionManager::addConnection(const Connection& connection) {
    std::string connId = connection.getConnectionId();

    // Check for duplicate
    if (findConnectionIndex(connId) >= 0) {
        return false;
    }

    m_connections.push_back(connection);
    return true;
}

bool ConnectionManager::removeConnection(const std::string& connectionId) {
    int index = findConnectionIndex(connectionId);
    if (index < 0) {
        return false;
    }

    m_connections.erase(m_connections.begin() + index);
    return true;
}

const Connection* ConnectionManager::getConnection(const std::string& connectionId) const {
    int index = findConnectionIndex(connectionId);
    if (index < 0) {
        return nullptr;
    }
    return &m_connections[index];
}

std::vector<Connection> ConnectionManager::getConnectionsForComponent(const std::string& componentId) const {
    std::vector<Connection> result;

    for (const auto& conn : m_connections) {
        if (conn.getSource().componentId == componentId ||
            conn.getDestination().componentId == componentId) {
            result.push_back(conn);
        }
    }

    return result;
}

std::vector<Connection> ConnectionManager::getConnectionsFromPin(const std::string& componentId,
                                                                  const std::string& pinId) const {
    std::vector<Connection> result;

    for (const auto& conn : m_connections) {
        if (conn.getSource().componentId == componentId &&
            conn.getSource().pinId == pinId) {
            result.push_back(conn);
        }
    }

    return result;
}

std::vector<Connection> ConnectionManager::getConnectionsToPin(const std::string& componentId,
                                                                const std::string& pinId) const {
    std::vector<Connection> result;

    for (const auto& conn : m_connections) {
        if (conn.getDestination().componentId == componentId &&
            conn.getDestination().pinId == pinId) {
            result.push_back(conn);
        }
    }

    return result;
}

size_t ConnectionManager::validateAllConnections() {
    size_t invalidCount = 0;

    for (auto& conn : m_connections) {
        if (!const_cast<Connection&>(conn).validate(true)) {
            const_cast<Connection&>(conn).setState(ConnectionState::Invalid);
            invalidCount++;
        }
    }

    return invalidCount;
}

size_t ConnectionManager::removeInvalidConnections() {
    size_t removedCount = 0;

    auto it = m_connections.begin();
    while (it != m_connections.end()) {
        if (!it->isValid()) {
            it = m_connections.erase(it);
            removedCount++;
        } else {
            ++it;
        }
    }

    return removedCount;
}

void ConnectionManager::clear() {
    m_connections.clear();
}

bool ConnectionManager::wouldCreateCycle(const Connection& connection) const {
    // Basic cycle detection: Check if there's a path from destination back to source
    // This is a simplified version - full implementation would need graph traversal

    std::set<std::string> visited;
    std::vector<std::string> toVisit;

    // Start from the destination component
    toVisit.push_back(connection.getDestination().componentId);

    while (!toVisit.empty()) {
        std::string current = toVisit.back();
        toVisit.pop_back();

        // If we've reached the source, we found a cycle
        if (current == connection.getSource().componentId) {
            return true;
        }

        // Skip if already visited
        if (visited.find(current) != visited.end()) {
            continue;
        }
        visited.insert(current);

        // Find all components that current connects to
        for (const auto& conn : m_connections) {
            if (conn.getSource().componentId == current) {
                toVisit.push_back(conn.getDestination().componentId);
            }
        }
    }

    return false;
}

nlohmann::json ConnectionManager::exportToJson() const {
    nlohmann::json j;
    j["connectionCount"] = m_connections.size();
    j["connections"] = nlohmann::json::array();

    for (const auto& conn : m_connections) {
        j["connections"].push_back(conn.toJson());
    }

    return j;
}

size_t ConnectionManager::importFromJson(const nlohmann::json& j, bool clearExisting) {
    if (clearExisting) {
        clear();
    }

    if (!j.contains("connections") || !j["connections"].is_array()) {
        return 0;
    }

    size_t importedCount = 0;
    const auto& connectionsArray = j["connections"];

    for (const auto& connJson : connectionsArray) {
        try {
            Connection conn = Connection::fromJson(connJson);
            if (addConnection(conn)) {
                importedCount++;
            }
        } catch (const std::exception& e) {
            // Skip invalid connections
            continue;
        }
    }

    return importedCount;
}

int ConnectionManager::findConnectionIndex(const std::string& connectionId) const {
    for (size_t i = 0; i < m_connections.size(); ++i) {
        if (m_connections[i].getConnectionId() == connectionId) {
            return static_cast<int>(i);
        }
    }
    return -1;
}

} // namespace Core
} // namespace VSE
