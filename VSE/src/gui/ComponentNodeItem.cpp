/**
 * @file ComponentNodeItem.cpp
 * @brief Implementation of ComponentNodeItem
 */

#include "gui/ComponentNodeItem.h"

#include <QPainter>
#include <QStyleOptionGraphicsItem>
#include <QGraphicsSceneHoverEvent>
#include <QGraphicsSceneMouseEvent>
#include <QFontMetrics>
#include <QtMath>

namespace VSE {
namespace GUI {

ComponentNodeItem::ComponentNodeItem(const QString& componentName, QGraphicsItem* parent)
    : QGraphicsItem(parent)
    , m_componentName(componentName)
    , m_nodeColor(QColor(60, 60, 65))
    , m_titleBarColor(QColor(80, 80, 85))
    , m_isHovered(false)
    , m_width(180)
    , m_height(100)
    , m_titleBarHeight(30)
    , m_pinRadius(6)
    , m_pinSpacing(25)
    , m_cornerRadius(8)
{
    setFlag(QGraphicsItem::ItemIsMovable, true);
    setFlag(QGraphicsItem::ItemIsSelectable, true);
    setFlag(QGraphicsItem::ItemSendsGeometryChanges, true);
    setAcceptHoverEvents(true);

    // Set Z-value so nodes appear above connections
    setZValue(1);

    updateGeometry();
}

ComponentNodeItem::~ComponentNodeItem()
{
}

void ComponentNodeItem::setComponentName(const QString& name)
{
    if (m_componentName != name) {
        m_componentName = name;
        update();
    }
}

void ComponentNodeItem::addInputPin(const QString& name, const QString& type)
{
    QColor color = getTypeColor(type);
    PinInfo pin(name, type, color, true);
    m_inputPins.append(pin);
    updateGeometry();
    updatePinPositions();
}

void ComponentNodeItem::addOutputPin(const QString& name, const QString& type)
{
    QColor color = getTypeColor(type);
    PinInfo pin(name, type, color, false);
    m_outputPins.append(pin);
    updateGeometry();
    updatePinPositions();
}

QPointF ComponentNodeItem::getInputPinPos(int index) const
{
    if (index >= 0 && index < m_inputPins.size()) {
        return mapToScene(m_inputPins[index].position);
    }
    return QPointF();
}

QPointF ComponentNodeItem::getOutputPinPos(int index) const
{
    if (index >= 0 && index < m_outputPins.size()) {
        return mapToScene(m_outputPins[index].position);
    }
    return QPointF();
}

bool ComponentNodeItem::getPinAtPos(const QPointF& scenePos, bool& isInput, int& pinIndex) const
{
    QPointF localPos = mapFromScene(scenePos);
    qreal clickRadius = m_pinRadius + 3; // Slightly larger hit area

    // Check input pins
    for (int i = 0; i < m_inputPins.size(); ++i) {
        QPointF pinPos = m_inputPins[i].position;
        qreal distance = QLineF(localPos, pinPos).length();
        if (distance <= clickRadius) {
            isInput = true;
            pinIndex = i;
            return true;
        }
    }

    // Check output pins
    for (int i = 0; i < m_outputPins.size(); ++i) {
        QPointF pinPos = m_outputPins[i].position;
        qreal distance = QLineF(localPos, pinPos).length();
        if (distance <= clickRadius) {
            isInput = false;
            pinIndex = i;
            return true;
        }
    }

    return false;
}

QRectF ComponentNodeItem::boundingRect() const
{
    qreal extra = m_pinRadius + 2;
    return QRectF(-extra, -extra,
                  m_width + 2 * extra,
                  m_height + 2 * extra);
}

QPainterPath ComponentNodeItem::shape() const
{
    QPainterPath path;
    path.addRoundedRect(0, 0, m_width, m_height, m_cornerRadius, m_cornerRadius);
    return path;
}

void ComponentNodeItem::paint(QPainter* painter, const QStyleOptionGraphicsItem* option, QWidget* widget)
{
    Q_UNUSED(option)
    Q_UNUSED(widget)

    painter->setRenderHint(QPainter::Antialiasing);

    // Draw selection highlight first (behind everything)
    if (isSelected()) {
        drawSelection(painter);
    }

    // Draw body
    drawBody(painter);

    // Draw title bar
    drawTitleBar(painter);

    // Draw pins
    drawPins(painter);

    // Draw hover effect
    if (m_isHovered && !isSelected()) {
        QPen hoverPen(QColor(100, 150, 200, 100), 2);
        painter->setPen(hoverPen);
        painter->setBrush(Qt::NoBrush);
        painter->drawRoundedRect(QRectF(0, 0, m_width, m_height),
                                m_cornerRadius, m_cornerRadius);
    }
}

void ComponentNodeItem::hoverEnterEvent(QGraphicsSceneHoverEvent* event)
{
    Q_UNUSED(event)
    m_isHovered = true;
    update();
}

void ComponentNodeItem::hoverLeaveEvent(QGraphicsSceneHoverEvent* event)
{
    Q_UNUSED(event)
    m_isHovered = false;
    update();
}

void ComponentNodeItem::mousePressEvent(QGraphicsSceneMouseEvent* event)
{
    // Check if clicking on a pin
    bool isInput;
    int pinIndex;
    if (getPinAtPos(event->scenePos(), isInput, pinIndex)) {
        // Pin clicked - could start connection creation here
        // For now, just don't move the node
        event->accept();
        return;
    }

    QGraphicsItem::mousePressEvent(event);
}

void ComponentNodeItem::mouseReleaseEvent(QGraphicsSceneMouseEvent* event)
{
    QGraphicsItem::mouseReleaseEvent(event);
}

QVariant ComponentNodeItem::itemChange(GraphicsItemChange change, const QVariant& value)
{
    if (change == ItemPositionHasChanged) {
        // Notify connections to update
        // This will be handled by the scene/connection items
    }

    return QGraphicsItem::itemChange(change, value);
}

void ComponentNodeItem::updateGeometry()
{
    int maxPins = qMax(m_inputPins.size(), m_outputPins.size());
    qreal minHeight = m_titleBarHeight + maxPins * m_pinSpacing + 20;
    m_height = qMax(m_height, minHeight);

    updatePinPositions();
    update();
}

QColor ComponentNodeItem::getTypeColor(const QString& type) const
{
    // Color code based on data type
    static QMap<QString, QColor> typeColors = {
        {"int", QColor(100, 150, 255)},
        {"float", QColor(150, 255, 150)},
        {"double", QColor(150, 255, 150)},
        {"bool", QColor(255, 100, 100)},
        {"string", QColor(255, 200, 100)},
        {"vector", QColor(255, 150, 255)},
        {"void", QColor(150, 150, 150)},
        {"any", QColor(200, 200, 200)}
    };

    QString lowerType = type.toLower();
    if (typeColors.contains(lowerType)) {
        return typeColors[lowerType];
    }

    // Default color for unknown types
    return QColor(180, 180, 180);
}

void ComponentNodeItem::updatePinPositions()
{
    // Calculate input pin positions (left side)
    qreal inputStartY = m_titleBarHeight + m_pinSpacing;
    for (int i = 0; i < m_inputPins.size(); ++i) {
        m_inputPins[i].position = QPointF(0, inputStartY + i * m_pinSpacing);
    }

    // Calculate output pin positions (right side)
    qreal outputStartY = m_titleBarHeight + m_pinSpacing;
    for (int i = 0; i < m_outputPins.size(); ++i) {
        m_outputPins[i].position = QPointF(m_width, outputStartY + i * m_pinSpacing);
    }
}

void ComponentNodeItem::drawTitleBar(QPainter* painter)
{
    // Title bar background
    QPainterPath titlePath;
    titlePath.moveTo(m_cornerRadius, 0);
    titlePath.lineTo(m_width - m_cornerRadius, 0);
    titlePath.arcTo(m_width - 2 * m_cornerRadius, 0,
                    2 * m_cornerRadius, 2 * m_cornerRadius, 90, -90);
    titlePath.lineTo(m_width, m_titleBarHeight);
    titlePath.lineTo(0, m_titleBarHeight);
    titlePath.lineTo(0, m_cornerRadius);
    titlePath.arcTo(0, 0, 2 * m_cornerRadius, 2 * m_cornerRadius, 180, -90);

    painter->setPen(Qt::NoPen);
    painter->setBrush(m_titleBarColor);
    painter->drawPath(titlePath);

    // Title text
    painter->setPen(Qt::white);
    QFont font = painter->font();
    font.setBold(true);
    font.setPointSize(10);
    painter->setFont(font);

    QRectF titleRect(0, 0, m_width, m_titleBarHeight);
    painter->drawText(titleRect, Qt::AlignCenter, m_componentName);
}

void ComponentNodeItem::drawBody(QPainter* painter)
{
    // Body background
    QPainterPath bodyPath;
    bodyPath.addRoundedRect(0, 0, m_width, m_height, m_cornerRadius, m_cornerRadius);

    painter->setPen(QPen(QColor(30, 30, 35), 2));
    painter->setBrush(m_nodeColor);
    painter->drawPath(bodyPath);
}

void ComponentNodeItem::drawPins(QPainter* painter)
{
    QFont font = painter->font();
    font.setPointSize(8);
    painter->setFont(font);

    // Draw input pins
    for (const PinInfo& pin : m_inputPins) {
        // Pin circle
        painter->setPen(QPen(pin.color.darker(150), 2));
        painter->setBrush(pin.color);
        painter->drawEllipse(pin.position, m_pinRadius, m_pinRadius);

        // Pin label
        painter->setPen(Qt::white);
        QRectF textRect(pin.position.x() + m_pinRadius + 5,
                       pin.position.y() - 8,
                       m_width / 2 - m_pinRadius - 10,
                       16);
        painter->drawText(textRect, Qt::AlignLeft | Qt::AlignVCenter, pin.name);
    }

    // Draw output pins
    for (const PinInfo& pin : m_outputPins) {
        // Pin circle
        painter->setPen(QPen(pin.color.darker(150), 2));
        painter->setBrush(pin.color);
        painter->drawEllipse(pin.position, m_pinRadius, m_pinRadius);

        // Pin label
        painter->setPen(Qt::white);
        QRectF textRect(pin.position.x() - m_width / 2 + 10,
                       pin.position.y() - 8,
                       m_width / 2 - m_pinRadius - 15,
                       16);
        painter->drawText(textRect, Qt::AlignRight | Qt::AlignVCenter, pin.name);
    }
}

void ComponentNodeItem::drawSelection(QPainter* painter)
{
    QPen selectionPen(QColor(100, 150, 255), 3);
    painter->setPen(selectionPen);
    painter->setBrush(Qt::NoBrush);
    painter->drawRoundedRect(QRectF(-2, -2, m_width + 4, m_height + 4),
                            m_cornerRadius + 1, m_cornerRadius + 1);
}

} // namespace GUI
} // namespace VSE
