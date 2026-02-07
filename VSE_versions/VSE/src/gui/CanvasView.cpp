/**
 * @file CanvasView.cpp
 * @brief Implementation of CanvasView
 */

#include "gui/CanvasView.h"

#include <QPainter>
#include <QMouseEvent>
#include <QWheelEvent>
#include <QKeyEvent>
#include <QContextMenuEvent>
#include <QMenu>
#include <QScrollBar>
#include <QtMath>

namespace VSE {
namespace GUI {

CanvasView::CanvasView(QGraphicsScene* scene, QWidget* parent)
    : QGraphicsView(scene, parent)
    , m_gridVisible(true)
    , m_gridSize(50)
    , m_gridSubdivisions(5)
    , m_zoomLevel(1.0)
    , m_minZoom(0.1)
    , m_maxZoom(5.0)
    , m_zoomStep(1.2)
    , m_isPanning(false)
    , m_mode(InteractionMode::None)
{
    // Set view properties
    setRenderHint(QPainter::Antialiasing, true);
    setRenderHint(QPainter::SmoothPixmapTransform, true);
    setRenderHint(QPainter::TextAntialiasing, true);
    setViewportUpdateMode(QGraphicsView::FullViewportUpdate);
    setHorizontalScrollBarPolicy(Qt::ScrollBarAsNeeded);
    setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
    setTransformationAnchor(QGraphicsView::AnchorUnderMouse);
    setResizeAnchor(QGraphicsView::AnchorViewCenter);
    setDragMode(QGraphicsView::RubberBandDrag);

    // Set background color
    setBackgroundBrush(QColor(45, 45, 48));

    // Enable mouse tracking for hover effects
    setMouseTracking(true);
}

CanvasView::~CanvasView()
{
}

void CanvasView::setGridVisible(bool visible)
{
    if (m_gridVisible != visible) {
        m_gridVisible = visible;
        viewport()->update();
    }
}

void CanvasView::setGridSize(int size)
{
    if (size > 0 && m_gridSize != size) {
        m_gridSize = size;
        if (m_gridVisible) {
            viewport()->update();
        }
    }
}

void CanvasView::resetView()
{
    resetTransform();
    m_zoomLevel = 1.0;
    centerOn(0, 0);
    emit zoomChanged(m_zoomLevel);
}

void CanvasView::fitInView()
{
    if (!scene()) {
        return;
    }

    QRectF itemsRect = scene()->itemsBoundingRect();
    if (itemsRect.isEmpty()) {
        resetView();
        return;
    }

    // Add padding
    itemsRect.adjust(-50, -50, 50, 50);

    // Fit the items in view
    QGraphicsView::fitInView(itemsRect, Qt::KeepAspectRatio);

    // Calculate and store zoom level
    m_zoomLevel = transform().m11();
    m_zoomLevel = clampZoom(m_zoomLevel);

    emit zoomChanged(m_zoomLevel);
}

void CanvasView::zoomIn()
{
    QPointF center = mapToScene(viewport()->rect().center());
    applyZoom(m_zoomStep, center);
}

void CanvasView::zoomOut()
{
    QPointF center = mapToScene(viewport()->rect().center());
    applyZoom(1.0 / m_zoomStep, center);
}

void CanvasView::setZoom(qreal level)
{
    level = clampZoom(level);
    if (qAbs(level - m_zoomLevel) < 0.001) {
        return;
    }

    QPointF center = mapToScene(viewport()->rect().center());
    qreal factor = level / m_zoomLevel;
    applyZoom(factor, center);
}

void CanvasView::drawBackground(QPainter* painter, const QRectF& rect)
{
    // Draw base background
    QGraphicsView::drawBackground(painter, rect);

    if (!m_gridVisible) {
        return;
    }

    drawGrid(painter, rect);
}

void CanvasView::drawGrid(QPainter* painter, const QRectF& rect)
{
    // Calculate grid spacing in scene coordinates
    qreal gridSpacing = m_gridSize;
    qreal subGridSpacing = gridSpacing / m_gridSubdivisions;

    // Get the visible rect in scene coordinates
    QRectF sceneRect = rect;

    // Calculate grid bounds
    int left = static_cast<int>(qFloor(sceneRect.left() / subGridSpacing));
    int right = static_cast<int>(qCeil(sceneRect.right() / subGridSpacing));
    int top = static_cast<int>(qFloor(sceneRect.top() / subGridSpacing));
    int bottom = static_cast<int>(qCeil(sceneRect.bottom() / subGridSpacing));

    // Draw sub-grid (fine lines)
    painter->setPen(QPen(QColor(60, 60, 63), 0));
    for (int x = left; x <= right; ++x) {
        if (x % m_gridSubdivisions != 0) {
            qreal xPos = x * subGridSpacing;
            painter->drawLine(QPointF(xPos, sceneRect.top()),
                            QPointF(xPos, sceneRect.bottom()));
        }
    }
    for (int y = top; y <= bottom; ++y) {
        if (y % m_gridSubdivisions != 0) {
            qreal yPos = y * subGridSpacing;
            painter->drawLine(QPointF(sceneRect.left(), yPos),
                            QPointF(sceneRect.right(), yPos));
        }
    }

    // Draw main grid (thicker lines)
    painter->setPen(QPen(QColor(80, 80, 83), 0));
    for (int x = left; x <= right; ++x) {
        if (x % m_gridSubdivisions == 0) {
            qreal xPos = x * subGridSpacing;
            painter->drawLine(QPointF(xPos, sceneRect.top()),
                            QPointF(xPos, sceneRect.bottom()));
        }
    }
    for (int y = top; y <= bottom; ++y) {
        if (y % m_gridSubdivisions == 0) {
            qreal yPos = y * subGridSpacing;
            painter->drawLine(QPointF(sceneRect.left(), yPos),
                            QPointF(sceneRect.right(), yPos));
        }
    }

    // Draw axes (even thicker)
    painter->setPen(QPen(QColor(120, 120, 123), 0));
    if (sceneRect.left() <= 0 && sceneRect.right() >= 0) {
        painter->drawLine(QPointF(0, sceneRect.top()),
                         QPointF(0, sceneRect.bottom()));
    }
    if (sceneRect.top() <= 0 && sceneRect.bottom() >= 0) {
        painter->drawLine(QPointF(sceneRect.left(), 0),
                         QPointF(sceneRect.right(), 0));
    }
}

void CanvasView::mousePressEvent(QMouseEvent* event)
{
    if (event->button() == Qt::MiddleButton) {
        // Middle button for panning
        m_isPanning = true;
        m_lastPanPos = event->pos();
        m_mode = InteractionMode::Pan;
        setCursor(Qt::ClosedHandCursor);
        event->accept();
        return;
    } else if (event->button() == Qt::LeftButton && event->modifiers() & Qt::AltModifier) {
        // Alt + Left button for panning
        m_isPanning = true;
        m_lastPanPos = event->pos();
        m_mode = InteractionMode::Pan;
        setCursor(Qt::ClosedHandCursor);
        event->accept();
        return;
    }

    // Default handling for selection and item interaction
    QGraphicsView::mousePressEvent(event);
}

void CanvasView::mouseMoveEvent(QMouseEvent* event)
{
    if (m_isPanning) {
        // Pan the view
        QPoint delta = event->pos() - m_lastPanPos;
        m_lastPanPos = event->pos();

        horizontalScrollBar()->setValue(horizontalScrollBar()->value() - delta.x());
        verticalScrollBar()->setValue(verticalScrollBar()->value() - delta.y());

        event->accept();
        return;
    }

    QGraphicsView::mouseMoveEvent(event);
}

void CanvasView::mouseReleaseEvent(QMouseEvent* event)
{
    if (m_isPanning) {
        if (event->button() == Qt::MiddleButton ||
            (event->button() == Qt::LeftButton && event->modifiers() & Qt::AltModifier)) {
            m_isPanning = false;
            m_mode = InteractionMode::None;
            setCursor(Qt::ArrowCursor);
            event->accept();
            return;
        }
    }

    QGraphicsView::mouseReleaseEvent(event);
}

void CanvasView::wheelEvent(QWheelEvent* event)
{
    if (event->modifiers() & Qt::ControlModifier) {
        // Zoom with Ctrl + Wheel
        QPoint numDegrees = event->angleDelta() / 8;
        QPoint numSteps = numDegrees / 15;

        if (!numSteps.isNull()) {
            qreal factor = qPow(m_zoomStep, numSteps.y());
            QPointF center = mapToScene(event->position().toPoint());
            applyZoom(factor, center);
        }

        event->accept();
    } else {
        // Default scroll behavior
        QGraphicsView::wheelEvent(event);
    }
}

void CanvasView::keyPressEvent(QKeyEvent* event)
{
    switch (event->key()) {
        case Qt::Key_Plus:
        case Qt::Key_Equal:
            if (event->modifiers() & Qt::ControlModifier) {
                zoomIn();
                event->accept();
                return;
            }
            break;

        case Qt::Key_Minus:
            if (event->modifiers() & Qt::ControlModifier) {
                zoomOut();
                event->accept();
                return;
            }
            break;

        case Qt::Key_0:
            if (event->modifiers() & Qt::ControlModifier) {
                resetView();
                event->accept();
                return;
            }
            break;

        case Qt::Key_F:
            if (event->modifiers() & Qt::ControlModifier) {
                fitInView();
                event->accept();
                return;
            }
            break;
    }

    QGraphicsView::keyPressEvent(event);
}

void CanvasView::contextMenuEvent(QContextMenuEvent* event)
{
    // Check if click was on an item
    QGraphicsItem* item = itemAt(event->pos());

    if (!item) {
        // Canvas context menu
        QMenu menu(this);
        menu.addAction(tr("Reset View"), this, &CanvasView::resetView);
        menu.addAction(tr("Fit to View"), this, &CanvasView::fitInView);
        menu.addSeparator();

        QAction* gridAction = menu.addAction(tr("Show Grid"));
        gridAction->setCheckable(true);
        gridAction->setChecked(m_gridVisible);
        connect(gridAction, &QAction::toggled, this, &CanvasView::setGridVisible);

        menu.exec(event->globalPos());
        event->accept();
    } else {
        // Let the scene/item handle it
        QGraphicsView::contextMenuEvent(event);
    }
}

void CanvasView::applyZoom(qreal factor, const QPointF& center)
{
    qreal newZoom = m_zoomLevel * factor;
    newZoom = clampZoom(newZoom);

    if (qAbs(newZoom - m_zoomLevel) < 0.001) {
        return;
    }

    qreal actualFactor = newZoom / m_zoomLevel;
    m_zoomLevel = newZoom;

    // Apply the zoom transformation
    scale(actualFactor, actualFactor);

    emit zoomChanged(m_zoomLevel);
}

qreal CanvasView::clampZoom(qreal level) const
{
    return qBound(m_minZoom, level, m_maxZoom);
}

} // namespace GUI
} // namespace VSE
