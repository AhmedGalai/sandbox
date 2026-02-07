/**
 * @file Connection.h
 * @brief Connection management for linking component pins through topics
 *
 * Provides classes for managing connections between component pins via topics.
 * Connections represent the data flow paths in a VSE circuit/graph.
 */

#ifndef VSE_CORE_CONNECTION_H
#define VSE_CORE_CONNECTION_H

#include "core/DataVariant.h"
#include <string>
#include <memory>
#include <nlohmann/json.hpp>

namespace VSE {
namespace Core {

/**
 * @enum ConnectionState
 * @brief State of a connection between pins
 */
enum class ConnectionState {
    Valid,          ///< Connection is valid and active
    Invalid,        ///< Connection has type mismatch or other error
    Disconnected    ///< Connection has been severed
};

/**
 * @struct PinReference
 * @brief Reference to a component pin
 *
 * Stores the identifiers needed to locate a specific pin on a component.
 * Used to serialize/deserialize connections.
 */
struct PinReference {
    std::string componentId;    ///< Unique ID of the component
    std::string pinId;          ///< ID of the pin on the component
    DataType dataType;          ///< Expected data type of the pin

    PinReference() : dataType(DataType::Null) {}

    PinReference(const std::string& compId, const std::string& pId, DataType type = DataType::Null)
        : componentId(compId), pinId(pId), dataType(type) {}

    /**
     * @brief Check if reference is valid (non-empty IDs)
     */
    bool isValid() const {
        return !componentId.empty() && !pinId.empty();
    }

    /**
     * @brief Serialize to JSON
     */
    nlohmann::json toJson() const;

    /**
     * @brief Deserialize from JSON
     */
    static PinReference fromJson(const nlohmann::json& j);

    /**
     * @brief Equality comparison
     */
    bool operator==(const PinReference& other) const {
        return componentId == other.componentId && pinId == other.pinId;
    }

    /**
     * @brief Inequality comparison
     */
    bool operator!=(const PinReference& other) const {
        return !(*this == other);
    }
};

/**
 * @class Connection
 * @brief Represents a connection between an output pin and input pin via a topic
 *
 * A connection links a source (output) pin to a destination (input) pin through
 * a named topic. The topic acts as the data bus for transmitting values.
 *
 * Key features:
 * - Type compatibility validation
 * - Connection state tracking
 * - Serialization support
 * - Topic-based routing
 *
 * Example usage:
 * @code
 * PinReference source("comp1", "output", DataType::Float);
 * PinReference dest("comp2", "input", DataType::Float);
 * Connection conn(source, dest, "data_flow");
 * if (conn.isValid()) {
 *     // Connection is valid and ready to use
 * }
 * @endcode
 */
class Connection {
public:
    /**
     * @brief Default constructor - creates disconnected connection
     */
    Connection();

    /**
     * @brief Construct connection with pin references and topic
     * @param source Output pin reference
     * @param destination Input pin reference
     * @param topicName Name of topic for data routing
     */
    Connection(const PinReference& source,
               const PinReference& destination,
               const std::string& topicName);

    /**
     * @brief Get source pin reference
     */
    const PinReference& getSource() const { return m_source; }

    /**
     * @brief Get destination pin reference
     */
    const PinReference& getDestination() const { return m_destination; }

    /**
     * @brief Get topic name
     */
    const std::string& getTopicName() const { return m_topicName; }

    /**
     * @brief Get connection state
     */
    ConnectionState getState() const { return m_state; }

    /**
     * @brief Set connection state
     */
    void setState(ConnectionState state) { m_state = state; }

    /**
     * @brief Check if connection is currently valid
     */
    bool isValid() const { return m_state == ConnectionState::Valid; }

    /**
     * @brief Check if connection is disconnected
     */
    bool isDisconnected() const { return m_state == ConnectionState::Disconnected; }

    /**
     * @brief Validate type compatibility between source and destination
     * @return true if types are compatible
     */
    bool validateTypes() const;

    /**
     * @brief Validate the entire connection (pins valid, types compatible, topic exists)
     * @param checkTopicExists If true, verify topic exists in registry
     * @return true if connection is valid
     */
    bool validate(bool checkTopicExists = false) const;

    /**
     * @brief Disconnect this connection
     *
     * Sets state to Disconnected. Does not remove from any registry.
     */
    void disconnect();

    /**
     * @brief Reconnect this connection
     *
     * Sets state back to Valid if validation passes, otherwise Invalid.
     * @return true if reconnected successfully
     */
    bool reconnect();

    /**
     * @brief Get unique connection ID
     *
     * Generates a unique string ID based on source and destination.
     * Format: "sourceCompId:sourcePinId->destCompId:destPinId"
     */
    std::string getConnectionId() const;

    /**
     * @brief Get error message if connection is invalid
     * @return Human-readable error description or empty string if valid
     */
    std::string getErrorMessage() const;

    /**
     * @brief Serialize connection to JSON
     * @return JSON representation
     */
    nlohmann::json toJson() const;

    /**
     * @brief Deserialize connection from JSON
     * @param j JSON object
     * @return Connection object
     * @throws std::runtime_error on invalid JSON
     */
    static Connection fromJson(const nlohmann::json& j);

    /**
     * @brief Equality comparison based on source and destination
     */
    bool operator==(const Connection& other) const;

    /**
     * @brief Inequality comparison
     */
    bool operator!=(const Connection& other) const;

private:
    PinReference m_source;
    PinReference m_destination;
    std::string m_topicName;
    ConnectionState m_state;
    mutable std::string m_errorMessage;

    /**
     * @brief Update error message based on current state
     */
    void updateErrorMessage() const;
};

/**
 * @class ConnectionManager
 * @brief Manages all connections in the VSE system
 *
 * Provides centralized management of connections between components,
 * including validation, cycle detection helpers, and bulk operations.
 */
class ConnectionManager {
public:
    /**
     * @brief Add a connection
     * @param connection Connection to add
     * @return true if added successfully, false if duplicate
     */
    bool addConnection(const Connection& connection);

    /**
     * @brief Remove a connection by ID
     * @param connectionId Connection ID from getConnectionId()
     * @return true if removed, false if not found
     */
    bool removeConnection(const std::string& connectionId);

    /**
     * @brief Get connection by ID
     * @param connectionId Connection ID
     * @return Pointer to connection or nullptr if not found
     */
    const Connection* getConnection(const std::string& connectionId) const;

    /**
     * @brief Get all connections
     */
    const std::vector<Connection>& getAllConnections() const { return m_connections; }

    /**
     * @brief Get connections involving a specific component
     * @param componentId Component ID
     * @return Vector of connections
     */
    std::vector<Connection> getConnectionsForComponent(const std::string& componentId) const;

    /**
     * @brief Get connections from a specific output pin
     * @param componentId Component ID
     * @param pinId Pin ID
     * @return Vector of connections
     */
    std::vector<Connection> getConnectionsFromPin(const std::string& componentId,
                                                   const std::string& pinId) const;

    /**
     * @brief Get connections to a specific input pin
     * @param componentId Component ID
     * @param pinId Pin ID
     * @return Vector of connections
     */
    std::vector<Connection> getConnectionsToPin(const std::string& componentId,
                                                 const std::string& pinId) const;

    /**
     * @brief Validate all connections
     * @return Number of invalid connections found
     */
    size_t validateAllConnections();

    /**
     * @brief Remove all invalid connections
     * @return Number of connections removed
     */
    size_t removeInvalidConnections();

    /**
     * @brief Clear all connections
     */
    void clear();

    /**
     * @brief Get number of connections
     */
    size_t getConnectionCount() const { return m_connections.size(); }

    /**
     * @brief Check if adding a connection would create a cycle
     * @param connection Connection to check
     * @return true if cycle would be created
     *
     * This is a helper for cycle detection. Actual implementation
     * would need component graph information.
     */
    bool wouldCreateCycle(const Connection& connection) const;

    /**
     * @brief Export all connections to JSON
     */
    nlohmann::json exportToJson() const;

    /**
     * @brief Import connections from JSON
     * @param j JSON array of connections
     * @param clearExisting If true, clear existing connections first
     * @return Number of connections imported
     */
    size_t importFromJson(const nlohmann::json& j, bool clearExisting = false);

private:
    std::vector<Connection> m_connections;

    /**
     * @brief Find connection index by ID
     * @return Index or -1 if not found
     */
    int findConnectionIndex(const std::string& connectionId) const;
};

} // namespace Core
} // namespace VSE

#endif // VSE_CORE_CONNECTION_H
