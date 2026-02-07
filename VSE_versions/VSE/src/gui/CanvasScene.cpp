/**
 * @file CanvasScene.cpp
 * @brief Implementation of CanvasScene
 */

#include "gui/CanvasScene.h"
#include "gui/ComponentNodeItem.h"
#include "gui/ConnectionItem.h"

#include <QGraphicsSceneMouseEvent>
#include <QKeyEvent>

namespace VSE {
namespace GUI {

CanvasScene::CanvasScene(QObject* parent)
    : QGraphicsScene(parent)
    , m_tempConnection(nullptr)
    , m_isCreatingConnection(false)
{
    // Set initial scene bounds
    setSceneRect(-5000, -5000, 10000, 10000);

    // Connect selection changed signal
    connect(this, &QGraphicsScene::selectionChanged,
            this, &CanvasScene::onSelectionChanged);
}

CanvasScene::~CanvasScene()
{
    clearAll();
}

void CanvasScene::addComponentNode(ComponentNodeItem* node)
{
    if (!node || m_componentNodes.contains(node)) {
        return;
    }

    addItem(node);
    m_componentNodes.insert(node);

    emit componentNodeAdded(node);
    emit sceneModified();

    updateSceneBounds();
}

void CanvasScene::removeComponentNode(ComponentNodeItem* node)
{
    if (!node || !m_componentNodes.contains(node)) {
        return;
    }

    // Remove all connections to/from this node
    QSet<ConnectionItem*> connectionsToRemove;
    for (ConnectionItem* conn : m_connections) {
        if (conn->getSourceNode() == node || conn->getDestNode() == node) {
            connectionsToRemove.insert(conn);
        }
    }

    for (ConnectionItem* conn : connectionsToRemove) {
        removeConnection(conn);
    }

    // Remove the node
    m_componentNodes.remove(node);
    removeItem(node);

    emit componentNodeRemoved(node);
    emit sceneModified();

    // Note: node is not deleted here - caller is responsible
    updateSceneBounds();
}

void CanvasScene::addConnection(ConnectionItem* connection)
{
    if (!connection || m_connections.contains(connection)) {
        return;
    }

    addItem(connection);
    m_connections.insert(connection);

    emit connectionAdded(connection);
    emit sceneModified();
}

void CanvasScene::removeConnection(ConnectionItem* connection)
{
    if (!connection || !m_connections.contains(connection)) {
        return;
    }

    m_connections.remove(connection);
    removeItem(connection);

    emit connectionRemoved(connection);
    emit sceneModified();

    // Note: connection is not deleted here - caller is responsible
}

void CanvasScene::deleteSelectedItems()
{
    QList<QGraphicsItem*> selected = selectedItems();
    if (selected.isEmpty()) {
        return;
    }

    // First, collect items to delete
    QSet<ComponentNodeItem*> nodesToDelete;
    QSet<ConnectionItem*> connectionsToDelete;

    for (QGraphicsItem* item : selected) {
        if (ComponentNodeItem* node = dynamic_cast<ComponentNodeItem*>(item)) {
            nodesToDelete.insert(node);
        } else if (ConnectionItem* conn = dynamic_cast<ConnectionItem*>(item)) {
            connectionsToDelete.insert(conn);
        }
    }

    // Delete connections first
    for (ConnectionItem* conn : connectionsToDelete) {
        removeConnection(conn);
        delete conn;
    }

    // Delete nodes (this will also delete their connections)
    for (ComponentNodeItem* node : nodesToDelete) {
        removeComponentNode(node);
        delete node;
    }
}

void CanvasScene::clearAll()
{
    // Clear all connections
    QSet<ConnectionItem*> connectionsCopy = m_connections;
    for (ConnectionItem* conn : connectionsCopy) {
        removeConnection(conn);
        delete conn;
    }

    // Clear all nodes
    QSet<ComponentNodeItem*> nodesCopy = m_componentNodes;
    for (ComponentNodeItem* node : nodesCopy) {
        removeComponentNode(node);
        delete node;
    }

    // Clear any remaining items
    clear();

    emit sceneModified();
}

void CanvasScene::mousePressEvent(QGraphicsSceneMouseEvent* event)
{
    // Handle connection creation (to be implemented when pins are clicked)
    QGraphicsScene::mousePressEvent(event);
}

void CanvasScene::mouseMoveEvent(QGraphicsSceneMouseEvent* event)
{
    // Handle connection creation dragging
    if (m_isCreatingConnection && m_tempConnection) {
        m_tempConnection->updateEndPoint(event->scenePos());
    }

    QGraphicsScene::mouseMoveEvent(event);
}

void CanvasScene::mouseReleaseEvent(QGraphicsSceneMouseEvent* event)
{
    // Handle connection creation completion
    if (m_isCreatingConnection && m_tempConnection) {
        // Check if we released over a valid pin
        // This will be implemented when pin interaction is added

        m_isCreatingConnection = false;
        if (m_tempConnection) {
            removeItem(m_tempConnection);
            delete m_tempConnection;
            m_tempConnection = nullptr;
        }
    }

    QGraphicsScene::mouseReleaseEvent(event);
}

void CanvasScene::onSelectionChanged()
{
    emit selectionChanged();
}

QList<ComponentNodeItem*> CanvasScene::getSelectedComponentNodes() const
{
    QList<ComponentNodeItem*> result;
    QList<QGraphicsItem*> selected = selectedItems();

    for (QGraphicsItem* item : selected) {
        if (ComponentNodeItem* node = dynamic_cast<ComponentNodeItem*>(item)) {
            result.append(node);
        }
    }

    return result;
}

void CanvasScene::updateSceneBounds()
{
    if (m_componentNodes.isEmpty()) {
        return;
    }

    // Calculate bounding rect of all nodes
    QRectF bounds;
    for (ComponentNodeItem* node : m_componentNodes) {
        bounds = bounds.united(node->sceneBoundingRect());
    }

    // Add padding
    bounds.adjust(-500, -500, 500, 500);

    // Ensure minimum size
    QRectF minRect(-5000, -5000, 10000, 10000);
    bounds = bounds.united(minRect);

    setSceneRect(bounds);
}

} // namespace GUI
} // namespace VSE
