/**
 * @file ExecutionContext.cpp
 * @brief Implementation of execution context for component graph runtime
 */

#include "core/ExecutionContext.h"
#include "core/Component.h"
#include "core/TopicRegistry.h"
#include <QDebug>
#include <algorithm>
#include <queue>

namespace VSE {
namespace Core {

ExecutionContext::ExecutionContext(QObject* parent)
    : QObject(parent)
    , m_graphBuilt(false)
{
}

ExecutionContext::~ExecutionContext()
{
    clear();
}

bool ExecutionContext::addComponent(std::shared_ptr<Component> component)
{
    if (!component) {
        qWarning() << "Cannot add null component";
        return false;
    }

    QString componentId = component->getId();

    // Check for duplicate ID
    if (componentExists(componentId)) {
        qWarning() << "Component with ID" << componentId << "already exists";
        return false;
    }

    // Add to storage
    m_components.push_back(component);
    m_componentMap[componentId] = component;

    // Mark graph as dirty
    m_graphBuilt = false;

    // Update statistics
    m_statistics.componentCount = m_components.size();

    emit componentAdded(componentId);

    return true;
}

bool ExecutionContext::removeComponent(const QString& componentId)
{
    if (!componentExists(componentId)) {
        return false;
    }

    // Remove from map
    m_componentMap.erase(componentId);

    // Remove from vector
    m_components.erase(
        std::remove_if(m_components.begin(), m_components.end(),
            [&componentId](const std::shared_ptr<Component>& comp) {
                return comp && comp->getId() == componentId;
            }),
        m_components.end()
    );

    // Remove connections involving this component
    m_connections.erase(
        std::remove_if(m_connections.begin(), m_connections.end(),
            [&componentId](const Connection& conn) {
                return conn.sourceComponentId == componentId ||
                       conn.targetComponentId == componentId;
            }),
        m_connections.end()
    );

    // Mark graph as dirty
    m_graphBuilt = false;

    // Update statistics
    m_statistics.componentCount = m_components.size();
    m_statistics.connectionCount = m_connections.size();

    emit componentRemoved(componentId);

    return true;
}

std::shared_ptr<Component> ExecutionContext::getComponent(const QString& componentId) const
{
    auto it = m_componentMap.find(componentId);
    if (it != m_componentMap.end()) {
        return it->second;
    }
    return nullptr;
}

bool ExecutionContext::addConnection(const Connection& connection)
{
    // Validate source component exists
    if (!componentExists(connection.sourceComponentId)) {
        qWarning() << "Source component does not exist:" << connection.sourceComponentId;
        return false;
    }

    // Validate target component exists
    if (!componentExists(connection.targetComponentId)) {
        qWarning() << "Target component does not exist:" << connection.targetComponentId;
        return false;
    }

    // Check for duplicate
    auto it = std::find(m_connections.begin(), m_connections.end(), connection);
    if (it != m_connections.end()) {
        qWarning() << "Connection already exists";
        return false;
    }

    // Add connection
    m_connections.push_back(connection);

    // Mark graph as dirty
    m_graphBuilt = false;

    // Update statistics
    m_statistics.connectionCount = m_connections.size();

    emit connectionAdded(connection);

    return true;
}

bool ExecutionContext::removeConnection(const Connection& connection)
{
    auto it = std::find(m_connections.begin(), m_connections.end(), connection);
    if (it == m_connections.end()) {
        return false;
    }

    m_connections.erase(it);

    // Mark graph as dirty
    m_graphBuilt = false;

    // Update statistics
    m_statistics.connectionCount = m_connections.size();

    emit connectionRemoved(connection);

    return true;
}

void ExecutionContext::setTopicRegistry(std::shared_ptr<TopicRegistry> registry)
{
    m_topicRegistry = registry;
}

bool ExecutionContext::buildExecutionGraph()
{
    // Clear previous graph
    m_adjacencyList.clear();
    m_reverseAdjacencyList.clear();

    // Initialize adjacency lists for all components
    for (const auto& component : m_components) {
        if (!component) continue;
        QString id = component->getId();
        m_adjacencyList[id] = std::vector<QString>();
        m_reverseAdjacencyList[id] = std::vector<QString>();
    }

    // Build adjacency list from connections
    buildAdjacencyList();

    m_graphBuilt = true;
    return true;
}

bool ExecutionContext::validateGraph(QString& errorMessage)
{
    // Build graph if not already built
    if (!m_graphBuilt) {
        if (!buildExecutionGraph()) {
            errorMessage = "Failed to build execution graph";
            emit validationFailed(errorMessage);
            return false;
        }
    }

    // Check for duplicate component IDs
    std::unordered_set<QString> seenIds;
    for (const auto& component : m_components) {
        if (!component) continue;

        QString id = component->getId();
        if (seenIds.count(id) > 0) {
            errorMessage = QString("Duplicate component ID: %1").arg(id);
            emit validationFailed(errorMessage);
            return false;
        }
        seenIds.insert(id);
    }

    // Check for cycles
    if (hasCycles()) {
        errorMessage = "Graph contains cycles (circular dependencies)";
        emit validationFailed(errorMessage);
        return false;
    }

    // Validate connections reference existing components
    for (const Connection& conn : m_connections) {
        if (!componentExists(conn.sourceComponentId)) {
            errorMessage = QString("Connection references non-existent source component: %1")
                .arg(conn.sourceComponentId);
            emit validationFailed(errorMessage);
            return false;
        }

        if (!componentExists(conn.targetComponentId)) {
            errorMessage = QString("Connection references non-existent target component: %1")
                .arg(conn.targetComponentId);
            emit validationFailed(errorMessage);
            return false;
        }

        // Validate pins exist
        auto sourceComp = getComponent(conn.sourceComponentId);
        auto targetComp = getComponent(conn.targetComponentId);

        if (sourceComp && !sourceComp->getOutputPin(conn.sourcePin)) {
            errorMessage = QString("Component %1 does not have output pin: %2")
                .arg(conn.sourceComponentId, conn.sourcePin);
            emit validationFailed(errorMessage);
            return false;
        }

        if (targetComp && !targetComp->getInputPin(conn.targetPin)) {
            errorMessage = QString("Component %1 does not have input pin: %2")
                .arg(conn.targetComponentId, conn.targetPin);
            emit validationFailed(errorMessage);
            return false;
        }
    }

    return true;
}

std::vector<QString> ExecutionContext::getDependencies(const QString& componentId) const
{
    auto it = m_reverseAdjacencyList.find(componentId);
    if (it != m_reverseAdjacencyList.end()) {
        return it->second;
    }
    return std::vector<QString>();
}

std::vector<QString> ExecutionContext::getDependents(const QString& componentId) const
{
    auto it = m_adjacencyList.find(componentId);
    if (it != m_adjacencyList.end()) {
        return it->second;
    }
    return std::vector<QString>();
}

bool ExecutionContext::hasCycles() const
{
    return detectCycle();
}

bool ExecutionContext::getTopologicalOrder(std::vector<QString>& sortedIds) const
{
    sortedIds.clear();

    // Kahn's algorithm for topological sort
    std::unordered_map<QString, int> inDegree;

    // Initialize in-degrees
    for (const auto& pair : m_adjacencyList) {
        inDegree[pair.first] = 0;
    }

    // Calculate in-degrees
    for (const auto& pair : m_adjacencyList) {
        for (const QString& neighbor : pair.second) {
            inDegree[neighbor]++;
        }
    }

    // Queue for nodes with no incoming edges
    std::queue<QString> zeroInDegree;
    for (const auto& pair : inDegree) {
        if (pair.second == 0) {
            zeroInDegree.push(pair.first);
        }
    }

    // Process nodes
    while (!zeroInDegree.empty()) {
        QString current = zeroInDegree.front();
        zeroInDegree.pop();
        sortedIds.push_back(current);

        // Reduce in-degree for neighbors
        auto it = m_adjacencyList.find(current);
        if (it != m_adjacencyList.end()) {
            for (const QString& neighbor : it->second) {
                inDegree[neighbor]--;
                if (inDegree[neighbor] == 0) {
                    zeroInDegree.push(neighbor);
                }
            }
        }
    }

    // Check if all nodes were processed (no cycle)
    if (sortedIds.size() != m_adjacencyList.size()) {
        // Cycle detected
        return false;
    }

    return true;
}

void ExecutionContext::clear()
{
    m_components.clear();
    m_componentMap.clear();
    m_connections.clear();
    m_adjacencyList.clear();
    m_reverseAdjacencyList.clear();
    m_graphBuilt = false;

    m_statistics.componentCount = 0;
    m_statistics.connectionCount = 0;
}

bool ExecutionContext::detectCycle() const
{
    std::unordered_set<QString> visited;
    std::unordered_set<QString> recursionStack;

    // Try DFS from each unvisited node
    for (const auto& pair : m_adjacencyList) {
        const QString& componentId = pair.first;
        if (visited.count(componentId) == 0) {
            if (dfsCycleDetect(componentId, visited, recursionStack)) {
                return true;  // Cycle found
            }
        }
    }

    return false;  // No cycle
}

bool ExecutionContext::dfsCycleDetect(
    const QString& componentId,
    std::unordered_set<QString>& visited,
    std::unordered_set<QString>& recursionStack) const
{
    visited.insert(componentId);
    recursionStack.insert(componentId);

    // Visit all neighbors
    auto it = m_adjacencyList.find(componentId);
    if (it != m_adjacencyList.end()) {
        for (const QString& neighbor : it->second) {
            // If neighbor not visited, recurse
            if (visited.count(neighbor) == 0) {
                if (dfsCycleDetect(neighbor, visited, recursionStack)) {
                    return true;
                }
            }
            // If neighbor in recursion stack, cycle found
            else if (recursionStack.count(neighbor) > 0) {
                return true;
            }
        }
    }

    recursionStack.erase(componentId);
    return false;
}

void ExecutionContext::buildAdjacencyList()
{
    // Build directed graph from connections
    // Edge from source to target means target depends on source
    for (const Connection& conn : m_connections) {
        // Add edge: source -> target (target depends on source)
        m_adjacencyList[conn.sourceComponentId].push_back(conn.targetComponentId);

        // Add reverse edge for dependency queries
        m_reverseAdjacencyList[conn.targetComponentId].push_back(conn.sourceComponentId);
    }

    // Remove duplicates
    for (auto& pair : m_adjacencyList) {
        auto& neighbors = pair.second;
        std::sort(neighbors.begin(), neighbors.end());
        neighbors.erase(std::unique(neighbors.begin(), neighbors.end()), neighbors.end());
    }

    for (auto& pair : m_reverseAdjacencyList) {
        auto& neighbors = pair.second;
        std::sort(neighbors.begin(), neighbors.end());
        neighbors.erase(std::unique(neighbors.begin(), neighbors.end()), neighbors.end());
    }
}

bool ExecutionContext::componentExists(const QString& componentId) const
{
    return m_componentMap.find(componentId) != m_componentMap.end();
}

} // namespace Core
} // namespace VSE
