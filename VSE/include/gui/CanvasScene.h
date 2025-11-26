/**
 * @file CanvasScene.h
 * @brief Graphics scene for managing node graph components
 */

#ifndef VSE_GUI_CANVASSCENE_H
#define VSE_GUI_CANVASSCENE_H

#include <QGraphicsScene>
#include <QHash>
#include <QSet>

// Forward declarations
class ComponentNodeItem;
class ConnectionItem;

namespace VSE {
namespace GUI {

/**
 * @class CanvasScene
 * @brief Manages the node graph scene containing components and connections
 *
 * CanvasScene is responsible for:
 * - Managing ComponentNodeItem objects (visual representations of components)
 * - Managing ConnectionItem objects (visual connections between pins)
 * - Handling component addition and removal
 * - Managing connections between component pins
 * - Selection handling
 * - Scene bounds management
 */
class CanvasScene : public QGraphicsScene {
    Q_OBJECT

public:
    /**
     * @brief Construct a new CanvasScene
     * @param parent Parent object
     */
    explicit CanvasScene(QObject* parent = nullptr);

    /**
     * @brief Destructor
     */
    ~CanvasScene() override;

    /**
     * @brief Add a component node to the scene
     * @param node Component node to add
     */
    void addComponentNode(ComponentNodeItem* node);

    /**
     * @brief Remove a component node from the scene
     * @param node Component node to remove
     */
    void removeComponentNode(ComponentNodeItem* node);

    /**
     * @brief Add a connection between two pins
     * @param connection Connection item to add
     */
    void addConnection(ConnectionItem* connection);

    /**
     * @brief Remove a connection from the scene
     * @param connection Connection to remove
     */
    void removeConnection(ConnectionItem* connection);

    /**
     * @brief Get all component nodes in the scene
     * @return Set of component nodes
     */
    QSet<ComponentNodeItem*> getComponentNodes() const { return m_componentNodes; }

    /**
     * @brief Get all connections in the scene
     * @return Set of connections
     */
    QSet<ConnectionItem*> getConnections() const { return m_connections; }

    /**
     * @brief Delete all selected items
     */
    void deleteSelectedItems();

    /**
     * @brief Clear all items from the scene
     */
    void clearAll();

signals:
    /**
     * @brief Emitted when the scene is modified
     */
    void sceneModified();

    /**
     * @brief Emitted when selection changes
     * @param selectedNodes Currently selected component nodes
     */
    void selectionChanged(const QList<ComponentNodeItem*>& selectedNodes);

    /**
     * @brief Emitted when a component node is added
     * @param node Added component node
     */
    void componentNodeAdded(ComponentNodeItem* node);

    /**
     * @brief Emitted when a component node is removed
     * @param node Removed component node
     */
    void componentNodeRemoved(ComponentNodeItem* node);

    /**
     * @brief Emitted when a connection is added
     * @param connection Added connection
     */
    void connectionAdded(ConnectionItem* connection);

    /**
     * @brief Emitted when a connection is removed
     * @param connection Removed connection
     */
    void connectionRemoved(ConnectionItem* connection);

protected:
    /**
     * @brief Handle selection change events
     */
    void selectionChangedEvent();

    /**
     * @brief Handle mouse press events
     * @param event Mouse event
     */
    void mousePressEvent(QGraphicsSceneMouseEvent* event) override;

    /**
     * @brief Handle mouse move events
     * @param event Mouse event
     */
    void mouseMoveEvent(QGraphicsSceneMouseEvent* event) override;

    /**
     * @brief Handle mouse release events
     * @param event Mouse event
     */
    void mouseReleaseEvent(QGraphicsSceneMouseEvent* event) override;

private slots:
    /**
     * @brief Handle Qt's selection changed signal
     */
    void onSelectionChanged();

private:
    /**
     * @brief Get selected component nodes
     * @return List of selected component nodes
     */
    QList<ComponentNodeItem*> getSelectedComponentNodes() const;

    /**
     * @brief Update scene bounds to fit all items
     */
    void updateSceneBounds();

private:
    QSet<ComponentNodeItem*> m_componentNodes;  ///< All component nodes in scene
    QSet<ConnectionItem*> m_connections;        ///< All connections in scene

    // Connection creation state
    ConnectionItem* m_tempConnection;           ///< Temporary connection during creation
    bool m_isCreatingConnection;                ///< Flag for connection creation mode
};

} // namespace GUI
} // namespace VSE

#endif // VSE_GUI_CANVASSCENE_H
