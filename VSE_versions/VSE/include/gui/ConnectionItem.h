/**
 * @file ConnectionItem.h
 * @brief Visual representation of a connection between component pins
 */

#ifndef VSE_GUI_CONNECTIONITEM_H
#define VSE_GUI_CONNECTIONITEM_H

#include <QGraphicsPathItem>
#include <QColor>

namespace VSE {
namespace GUI {

// Forward declaration
class ComponentNodeItem;

/**
 * @class ConnectionItem
 * @brief Visual representation of a connection between two pins
 *
 * ConnectionItem provides:
 * - Cubic bezier curve rendering between pins
 * - Automatic updates when connected nodes move
 * - Selection highlighting
 * - Hover effects
 * - Color coding by data type
 * - Arrow indicator at destination
 */
class ConnectionItem : public QGraphicsPathItem {
public:
    /**
     * @brief Construct a new ConnectionItem
     * @param sourceNode Source component node
     * @param sourcePin Source pin index
     * @param destNode Destination component node
     * @param destPin Destination pin index
     * @param parent Parent item
     */
    ConnectionItem(ComponentNodeItem* sourceNode, int sourcePin,
                   ComponentNodeItem* destNode, int destPin,
                   QGraphicsItem* parent = nullptr);

    /**
     * @brief Construct a temporary connection (for creation)
     * @param startPos Start position
     * @param endPos End position
     * @param parent Parent item
     */
    ConnectionItem(const QPointF& startPos, const QPointF& endPos,
                   QGraphicsItem* parent = nullptr);

    /**
     * @brief Destructor
     */
    ~ConnectionItem() override;

    /**
     * @brief Get source node
     * @return Source component node
     */
    ComponentNodeItem* getSourceNode() const { return m_sourceNode; }

    /**
     * @brief Get destination node
     * @return Destination component node
     */
    ComponentNodeItem* getDestNode() const { return m_destNode; }

    /**
     * @brief Get source pin index
     * @return Source pin index
     */
    int getSourcePin() const { return m_sourcePin; }

    /**
     * @brief Get destination pin index
     * @return Destination pin index
     */
    int getDestPin() const { return m_destPin; }

    /**
     * @brief Set connection color
     * @param color New color
     */
    void setConnectionColor(const QColor& color);

    /**
     * @brief Get connection color
     * @return Current color
     */
    QColor getConnectionColor() const { return m_color; }

    /**
     * @brief Update the connection path
     */
    void updatePath();

    /**
     * @brief Update end point (for temporary connections)
     * @param endPos New end position
     */
    void updateEndPoint(const QPointF& endPos);

    /**
     * @brief Check if this is a temporary connection
     * @return True if temporary
     */
    bool isTemporary() const { return m_isTemporary; }

protected:
    void hoverEnterEvent(QGraphicsSceneHoverEvent* event) override;
    void hoverLeaveEvent(QGraphicsSceneHoverEvent* event) override;
    void paint(QPainter* painter, const QStyleOptionGraphicsItem* option, QWidget* widget) override;

private:
    /**
     * @brief Create cubic bezier curve path
     * @param start Start point
     * @param end End point
     * @return Bezier curve path
     */
    QPainterPath createCurve(const QPointF& start, const QPointF& end) const;

    /**
     * @brief Create arrow polygon at destination
     * @param endPoint End point of the curve
     * @param direction Direction of the arrow (tangent)
     * @return Arrow polygon
     */
    QPolygonF createArrow(const QPointF& endPoint, const QPointF& direction) const;

    /**
     * @brief Update visual appearance (pen, selection, etc.)
     */
    void updateAppearance();

private:
    ComponentNodeItem* m_sourceNode;    ///< Source component node
    ComponentNodeItem* m_destNode;      ///< Destination component node
    int m_sourcePin;                    ///< Source pin index
    int m_destPin;                      ///< Destination pin index

    QColor m_color;                     ///< Connection color
    bool m_isHovered;                   ///< Hover state
    bool m_isTemporary;                 ///< Temporary connection flag

    // For temporary connections
    QPointF m_startPos;                 ///< Start position
    QPointF m_endPos;                   ///< End position

    qreal m_lineWidth;                  ///< Line width
    qreal m_selectedLineWidth;          ///< Line width when selected
    qreal m_hoverLineWidth;             ///< Line width when hovered
};

} // namespace GUI
} // namespace VSE

#endif // VSE_GUI_CONNECTIONITEM_H
