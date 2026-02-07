/**
 * @file ExecutionContext.h
 * @brief Runtime context for component graph execution
 *
 * Holds all runtime state including component instances, connections,
 * and execution statistics. Provides methods for building and validating
 * the execution graph.
 */

#ifndef VSE_CORE_EXECUTIONCONTEXT_H
#define VSE_CORE_EXECUTIONCONTEXT_H

#include <QString>
#include <QObject>
#include <memory>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <string>

namespace VSE {
namespace Core {

// Forward declarations
class Component;
class TopicRegistry;
class DataVariant;

/**
 * @struct Connection
 * @brief Represents a connection between component pins
 */
struct Connection {
    QString sourceComponentId;   ///< ID of source component
    QString sourcePin;            ///< Name of source output pin
    QString targetComponentId;   ///< ID of target component
    QString targetPin;            ///< Name of target input pin
    QString topic;                ///< Optional topic for pub/sub connections

    /**
     * @brief Default constructor
     */
    Connection() = default;

    /**
     * @brief Construct a direct pin-to-pin connection
     */
    Connection(const QString& srcComp, const QString& srcPin,
               const QString& tgtComp, const QString& tgtPin)
        : sourceComponentId(srcComp), sourcePin(srcPin),
          targetComponentId(tgtComp), targetPin(tgtPin) {}

    /**
     * @brief Construct a topic-based connection
     */
    Connection(const QString& srcComp, const QString& srcPin,
               const QString& tgtComp, const QString& tgtPin,
               const QString& topicName)
        : sourceComponentId(srcComp), sourcePin(srcPin),
          targetComponentId(tgtComp), targetPin(tgtPin),
          topic(topicName) {}

    /**
     * @brief Check if connection is topic-based
     */
    bool isTopicBased() const { return !topic.isEmpty(); }

    /**
     * @brief Equality comparison
     */
    bool operator==(const Connection& other) const {
        return sourceComponentId == other.sourceComponentId &&
               sourcePin == other.sourcePin &&
               targetComponentId == other.targetComponentId &&
               targetPin == other.targetPin &&
               topic == other.topic;
    }
};

/**
 * @struct ExecutionStatistics
 * @brief Statistics about execution
 */
struct ExecutionStatistics {
    uint64_t iterationCount;      ///< Total iterations completed
    int64_t elapsedTimeMs;        ///< Total elapsed time in milliseconds
    size_t errorCount;            ///< Number of errors encountered
    size_t componentCount;        ///< Number of components in graph
    size_t connectionCount;       ///< Number of connections in graph
    double averageIterationMs;    ///< Average iteration time

    /**
     * @brief Default constructor
     */
    ExecutionStatistics()
        : iterationCount(0), elapsedTimeMs(0), errorCount(0),
          componentCount(0), connectionCount(0), averageIterationMs(0.0) {}

    /**
     * @brief Reset all statistics
     */
    void reset() {
        iterationCount = 0;
        elapsedTimeMs = 0;
        errorCount = 0;
        averageIterationMs = 0.0;
    }
};

/**
 * @class ExecutionContext
 * @brief Runtime context for executing component graphs
 *
 * The ExecutionContext manages all runtime state for executing a visual
 * program, including:
 * - Component instances and their lifecycle
 * - Connections between components
 * - Topic registry for pub/sub communication
 * - Execution statistics
 * - Graph validation and analysis
 *
 * It provides methods to:
 * - Add/remove components and connections
 * - Build execution graph from components
 * - Validate graph for cycles and connectivity
 * - Query dependencies and topology
 *
 * Example usage:
 * @code
 * auto context = std::make_shared<ExecutionContext>();
 * context->addComponent(componentPtr);
 * context->addConnection(conn);
 * if (context->validateGraph()) {
 *     // Graph is valid, ready for execution
 * }
 * @endcode
 */
class ExecutionContext : public QObject {
    Q_OBJECT

public:
    /**
     * @brief Construct a new Execution Context
     * @param parent Parent QObject
     */
    explicit ExecutionContext(QObject* parent = nullptr);

    /**
     * @brief Destructor
     */
    ~ExecutionContext() override;

    /**
     * @brief Add a component to the context
     * @param component Component to add
     * @return true if added successfully
     */
    bool addComponent(std::shared_ptr<Component> component);

    /**
     * @brief Remove a component from the context
     * @param componentId ID of component to remove
     * @return true if removed successfully
     */
    bool removeComponent(const QString& componentId);

    /**
     * @brief Get component by ID
     * @param componentId Component ID
     * @return std::shared_ptr<Component> Component pointer or nullptr
     */
    std::shared_ptr<Component> getComponent(const QString& componentId) const;

    /**
     * @brief Get all components
     * @return const std::vector<std::shared_ptr<Component>>& Component list
     */
    const std::vector<std::shared_ptr<Component>>& getComponents() const {
        return m_components;
    }

    /**
     * @brief Add a connection between components
     * @param connection Connection to add
     * @return true if added successfully
     */
    bool addConnection(const Connection& connection);

    /**
     * @brief Remove a connection
     * @param connection Connection to remove
     * @return true if removed successfully
     */
    bool removeConnection(const Connection& connection);

    /**
     * @brief Get all connections
     * @return const std::vector<Connection>& Connection list
     */
    const std::vector<Connection>& getConnections() const {
        return m_connections;
    }

    /**
     * @brief Set the topic registry
     * @param registry Shared pointer to topic registry
     */
    void setTopicRegistry(std::shared_ptr<TopicRegistry> registry);

    /**
     * @brief Get the topic registry
     * @return std::shared_ptr<TopicRegistry> Topic registry
     */
    std::shared_ptr<TopicRegistry> getTopicRegistry() const {
        return m_topicRegistry;
    }

    /**
     * @brief Get execution statistics
     * @return const ExecutionStatistics& Statistics
     */
    const ExecutionStatistics& getStatistics() const {
        return m_statistics;
    }

    /**
     * @brief Update iteration count
     * @param count New iteration count
     */
    void updateIterationCount(uint64_t count) {
        m_statistics.iterationCount = count;
    }

    /**
     * @brief Update elapsed time
     * @param timeMs Elapsed time in milliseconds
     */
    void updateElapsedTime(int64_t timeMs) {
        m_statistics.elapsedTimeMs = timeMs;
    }

    /**
     * @brief Increment error count
     */
    void incrementErrorCount() {
        m_statistics.errorCount++;
    }

    /**
     * @brief Reset statistics
     */
    void resetStatistics() {
        m_statistics.reset();
    }

    /**
     * @brief Build execution graph from components and connections
     *
     * Constructs internal dependency graph for topological sorting.
     * Must be called before validateGraph().
     *
     * @return true if graph built successfully
     */
    bool buildExecutionGraph();

    /**
     * @brief Validate the execution graph
     *
     * Checks for:
     * - Cycles in dependency graph
     * - Unconnected required inputs
     * - Invalid component references
     * - Duplicate component IDs
     *
     * @param errorMessage Output parameter for error details
     * @return true if graph is valid
     */
    bool validateGraph(QString& errorMessage);

    /**
     * @brief Get dependencies for a component
     *
     * Returns all components that must execute before the given component.
     *
     * @param componentId Component to query
     * @return std::vector<QString> List of dependency component IDs
     */
    std::vector<QString> getDependencies(const QString& componentId) const;

    /**
     * @brief Get dependents of a component
     *
     * Returns all components that depend on the given component.
     *
     * @param componentId Component to query
     * @return std::vector<QString> List of dependent component IDs
     */
    std::vector<QString> getDependents(const QString& componentId) const;

    /**
     * @brief Check if graph has cycles
     * @return true if cycles detected
     */
    bool hasCycles() const;

    /**
     * @brief Get topologically sorted component order
     *
     * Uses Kahn's algorithm for topological sort.
     *
     * @param sortedIds Output parameter for sorted component IDs
     * @return true if sort successful (no cycles)
     */
    bool getTopologicalOrder(std::vector<QString>& sortedIds) const;

    /**
     * @brief Clear all components and connections
     */
    void clear();

    /**
     * @brief Get number of components
     * @return size_t Component count
     */
    size_t getComponentCount() const {
        return m_components.size();
    }

    /**
     * @brief Get number of connections
     * @return size_t Connection count
     */
    size_t getConnectionCount() const {
        return m_connections.size();
    }

signals:
    /**
     * @brief Emitted when a component is added
     * @param componentId ID of added component
     */
    void componentAdded(const QString& componentId);

    /**
     * @brief Emitted when a component is removed
     * @param componentId ID of removed component
     */
    void componentRemoved(const QString& componentId);

    /**
     * @brief Emitted when a connection is added
     * @param connection Added connection
     */
    void connectionAdded(const Connection& connection);

    /**
     * @brief Emitted when a connection is removed
     * @param connection Removed connection
     */
    void connectionRemoved(const Connection& connection);

    /**
     * @brief Emitted when graph validation fails
     * @param errorMessage Validation error message
     */
    void validationFailed(const QString& errorMessage);

private:
    /**
     * @brief Detect cycles using DFS
     * @return true if cycle detected
     */
    bool detectCycle() const;

    /**
     * @brief DFS helper for cycle detection
     * @param componentId Current component
     * @param visited Set of visited components
     * @param recursionStack Set of components in current DFS path
     * @return true if cycle detected
     */
    bool dfsCycleDetect(const QString& componentId,
                        std::unordered_set<QString>& visited,
                        std::unordered_set<QString>& recursionStack) const;

    /**
     * @brief Build adjacency list from connections
     */
    void buildAdjacencyList();

    /**
     * @brief Validate component exists
     * @param componentId Component to check
     * @return true if exists
     */
    bool componentExists(const QString& componentId) const;

    // Component storage
    std::vector<std::shared_ptr<Component>> m_components;
    std::unordered_map<QString, std::shared_ptr<Component>> m_componentMap;

    // Connection storage
    std::vector<Connection> m_connections;

    // Dependency graph (adjacency list)
    std::unordered_map<QString, std::vector<QString>> m_adjacencyList;
    std::unordered_map<QString, std::vector<QString>> m_reverseAdjacencyList;

    // Topic registry
    std::shared_ptr<TopicRegistry> m_topicRegistry;

    // Statistics
    ExecutionStatistics m_statistics;

    // Graph state
    bool m_graphBuilt;
};

} // namespace Core
} // namespace VSE

// Hash function for Connection (for unordered containers)
namespace std {
    template<>
    struct hash<VSE::Core::Connection> {
        size_t operator()(const VSE::Core::Connection& conn) const {
            return qHash(conn.sourceComponentId) ^
                   qHash(conn.sourcePin) ^
                   qHash(conn.targetComponentId) ^
                   qHash(conn.targetPin) ^
                   qHash(conn.topic);
        }
    };
}

#endif // VSE_CORE_EXECUTIONCONTEXT_H
