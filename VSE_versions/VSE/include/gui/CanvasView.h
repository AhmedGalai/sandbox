/**
 * @file CanvasView.h
 * @brief Graphics view for displaying and interacting with the node canvas
 */

#ifndef VSE_GUI_CANVASVIEW_H
#define VSE_GUI_CANVASVIEW_H

#include <QGraphicsView>
#include <QPointF>

namespace VSE {
namespace GUI {

/**
 * @class CanvasView
 * @brief Custom graphics view with pan, zoom, and grid rendering
 *
 * CanvasView provides:
 * - Pan with left mouse button drag
 * - Zoom with mouse wheel (anchored under cursor)
 * - Grid background rendering
 * - View reset and fit functionality
 * - Context menu for canvas operations
 */
class CanvasView : public QGraphicsView {
    Q_OBJECT

public:
    /**
     * @brief Construct a new CanvasView
     * @param scene Graphics scene to display
     * @param parent Parent widget
     */
    explicit CanvasView(QGraphicsScene* scene, QWidget* parent = nullptr);

    /**
     * @brief Destructor
     */
    ~CanvasView() override;

    /**
     * @brief Set whether grid is visible
     * @param visible True to show grid
     */
    void setGridVisible(bool visible);

    /**
     * @brief Check if grid is visible
     * @return True if grid is visible
     */
    bool isGridVisible() const { return m_gridVisible; }

    /**
     * @brief Set grid size
     * @param size Grid cell size in pixels
     */
    void setGridSize(int size);

    /**
     * @brief Get grid size
     * @return Grid cell size in pixels
     */
    int getGridSize() const { return m_gridSize; }

    /**
     * @brief Get current zoom level
     * @return Zoom level (1.0 = 100%)
     */
    qreal getZoomLevel() const { return m_zoomLevel; }

public slots:
    /**
     * @brief Reset view to default (1:1 zoom, centered at origin)
     */
    void resetView();

    /**
     * @brief Fit all items in view
     */
    void fitInView();

    /**
     * @brief Zoom in by fixed increment
     */
    void zoomIn();

    /**
     * @brief Zoom out by fixed increment
     */
    void zoomOut();

    /**
     * @brief Set zoom to specific level
     * @param level Zoom level (1.0 = 100%)
     */
    void setZoom(qreal level);

signals:
    /**
     * @brief Emitted when zoom level changes
     * @param level New zoom level
     */
    void zoomChanged(qreal level);

protected:
    /**
     * @brief Draw background with optional grid
     * @param painter Painter to draw with
     * @param rect Rectangle to draw
     */
    void drawBackground(QPainter* painter, const QRectF& rect) override;

    /**
     * @brief Handle mouse press events
     * @param event Mouse event
     */
    void mousePressEvent(QMouseEvent* event) override;

    /**
     * @brief Handle mouse move events
     * @param event Mouse event
     */
    void mouseMoveEvent(QMouseEvent* event) override;

    /**
     * @brief Handle mouse release events
     * @param event Mouse event
     */
    void mouseReleaseEvent(QMouseEvent* event) override;

    /**
     * @brief Handle mouse wheel events for zooming
     * @param event Wheel event
     */
    void wheelEvent(QWheelEvent* event) override;

    /**
     * @brief Handle key press events
     * @param event Key event
     */
    void keyPressEvent(QKeyEvent* event) override;

    /**
     * @brief Handle context menu events
     * @param event Context menu event
     */
    void contextMenuEvent(QContextMenuEvent* event) override;

private:
    /**
     * @brief Apply zoom centered at a specific point
     * @param factor Zoom factor to apply
     * @param center Center point in scene coordinates
     */
    void applyZoom(qreal factor, const QPointF& center);

    /**
     * @brief Clamp zoom level to valid range
     * @param level Desired zoom level
     * @return Clamped zoom level
     */
    qreal clampZoom(qreal level) const;

    /**
     * @brief Draw grid lines
     * @param painter Painter to draw with
     * @param rect Rectangle to draw
     */
    void drawGrid(QPainter* painter, const QRectF& rect);

private:
    // Grid settings
    bool m_gridVisible;     ///< Whether grid is visible
    int m_gridSize;         ///< Grid cell size in pixels
    int m_gridSubdivisions; ///< Number of subdivisions per grid cell

    // Zoom settings
    qreal m_zoomLevel;      ///< Current zoom level (1.0 = 100%)
    qreal m_minZoom;        ///< Minimum zoom level
    qreal m_maxZoom;        ///< Maximum zoom level
    qreal m_zoomStep;       ///< Zoom increment for zoom in/out

    // Pan settings
    bool m_isPanning;       ///< Whether currently panning
    QPoint m_lastPanPos;    ///< Last mouse position during pan

    // Interaction mode
    enum class InteractionMode {
        None,
        Pan,
        Select
    };
    InteractionMode m_mode; ///< Current interaction mode
};

} // namespace GUI
} // namespace VSE

#endif // VSE_GUI_CANVASVIEW_H
