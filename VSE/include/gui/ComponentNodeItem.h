/**
 * @file ComponentNodeItem.h
 * @brief Visual representation of a component in the node graph
 */

#ifndef VSE_GUI_COMPONENTNODEITEM_H
#define VSE_GUI_COMPONENTNODEITEM_H

#include <QGraphicsItem>
#include <QList>
#include <QString>
#include <QColor>

namespace VSE {
namespace GUI {

/**
 * @struct PinInfo
 * @brief Information about an input or output pin
 */
struct PinInfo {
    QString name;           ///< Pin name
    QString type;           ///< Data type
    QColor color;           ///< Pin color (based on type)
    QPointF position;       ///< Position relative to node
    bool isInput;           ///< True if input pin, false if output

    PinInfo(const QString& n = "", const QString& t = "", const QColor& c = Qt::white, bool input = true)
        : name(n), type(t), color(c), isInput(input) {}
};

/**
 * @class ComponentNodeItem
 * @brief Visual representation of a component node in the graph
 *
 * ComponentNodeItem provides:
 * - Visual display with title bar and pins
 * - Input pins on the left side
 * - Output pins on the right side
 * - Selection highlight
 * - Hover effects
 * - Drag and drop support
 * - Pin click detection for connections
 */
class ComponentNodeItem : public QGraphicsItem {
public:
    /**
     * @brief Construct a new ComponentNodeItem
     * @param componentName Name of the component
     * @param parent Parent item
     */
    explicit ComponentNodeItem(const QString& componentName = "Component",
                              QGraphicsItem* parent = nullptr);

    /**
     * @brief Destructor
     */
    ~ComponentNodeItem() override;

    /**
     * @brief Get component name
     * @return Component name
     */
    QString getComponentName() const { return m_componentName; }

    /**
     * @brief Set component name
     * @param name New component name
     */
    void setComponentName(const QString& name);

    /**
     * @brief Add an input pin
     * @param name Pin name
     * @param type Data type
     */
    void addInputPin(const QString& name, const QString& type);

    /**
     * @brief Add an output pin
     * @param name Pin name
     * @param type Data type
     */
    void addOutputPin(const QString& name, const QString& type);

    /**
     * @brief Get all input pins
     * @return List of input pins
     */
    QList<PinInfo> getInputPins() const { return m_inputPins; }

    /**
     * @brief Get all output pins
     * @return List of output pins
     */
    QList<PinInfo> getOutputPins() const { return m_outputPins; }

    /**
     * @brief Get position of specific input pin
     * @param index Pin index
     * @return Pin position in scene coordinates
     */
    QPointF getInputPinPos(int index) const;

    /**
     * @brief Get position of specific output pin
     * @param index Pin index
     * @return Pin position in scene coordinates
     */
    QPointF getOutputPinPos(int index) const;

    /**
     * @brief Get pin at a specific position
     * @param scenePos Position in scene coordinates
     * @param isInput Output parameter: true if pin is input
     * @param pinIndex Output parameter: index of the pin
     * @return True if a pin was found at the position
     */
    bool getPinAtPos(const QPointF& scenePos, bool& isInput, int& pinIndex) const;

    /**
     * @brief Set node color
     * @param color New color
     */
    void setNodeColor(const QColor& color) { m_nodeColor = color; update(); }

    /**
     * @brief Get node color
     * @return Current node color
     */
    QColor getNodeColor() const { return m_nodeColor; }

    // QGraphicsItem interface
    QRectF boundingRect() const override;
    QPainterPath shape() const override;
    void paint(QPainter* painter, const QStyleOptionGraphicsItem* option, QWidget* widget) override;

protected:
    void hoverEnterEvent(QGraphicsSceneHoverEvent* event) override;
    void hoverLeaveEvent(QGraphicsSceneHoverEvent* event) override;
    void mousePressEvent(QGraphicsSceneMouseEvent* event) override;
    void mouseReleaseEvent(QGraphicsSceneMouseEvent* event) override;
    QVariant itemChange(GraphicsItemChange change, const QVariant& value) override;

private:
    /**
     * @brief Calculate node dimensions
     */
    void updateGeometry();

    /**
     * @brief Get color for a data type
     * @param type Data type name
     * @return Color for the type
     */
    QColor getTypeColor(const QString& type) const;

    /**
     * @brief Calculate pin positions
     */
    void updatePinPositions();

    /**
     * @brief Draw title bar
     * @param painter Painter to draw with
     */
    void drawTitleBar(QPainter* painter);

    /**
     * @brief Draw body
     * @param painter Painter to draw with
     */
    void drawBody(QPainter* painter);

    /**
     * @brief Draw pins
     * @param painter Painter to draw with
     */
    void drawPins(QPainter* painter);

    /**
     * @brief Draw selection highlight
     * @param painter Painter to draw with
     */
    void drawSelection(QPainter* painter);

private:
    QString m_componentName;            ///< Component name
    QList<PinInfo> m_inputPins;         ///< Input pins
    QList<PinInfo> m_outputPins;        ///< Output pins

    // Visual properties
    QColor m_nodeColor;                 ///< Node base color
    QColor m_titleBarColor;             ///< Title bar color
    bool m_isHovered;                   ///< Hover state

    // Geometry
    qreal m_width;                      ///< Node width
    qreal m_height;                     ///< Node height
    qreal m_titleBarHeight;             ///< Title bar height
    qreal m_pinRadius;                  ///< Pin circle radius
    qreal m_pinSpacing;                 ///< Spacing between pins
    qreal m_cornerRadius;               ///< Corner radius for rounded rect
};

} // namespace GUI
} // namespace VSE

#endif // VSE_GUI_COMPONENTNODEITEM_H
