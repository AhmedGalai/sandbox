/**
 * @file MainWindow.h
 * @brief Main application window for the Visual Scripting Environment
 */

#ifndef VSE_GUI_MAINWINDOW_H
#define VSE_GUI_MAINWINDOW_H

#include <QMainWindow>
#include <QString>

// Forward declarations
class QAction;
class QMenu;
class QToolBar;
class QDockWidget;
class CanvasView;
class CanvasScene;
class InspectorWidget;

namespace VSE {
namespace GUI {

/**
 * @class MainWindow
 * @brief Main application window containing canvas, inspector, and menus
 *
 * MainWindow is the primary container for the VSE application. It manages:
 * - Menu bar with File, Edit, View, and Help menus
 * - Toolbar for common actions
 * - Central canvas view for node graph editing
 * - Inspector dock for property editing
 * - Component palette dock
 * - Application state (dirty flag, current file)
 */
class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    /**
     * @brief Construct a new MainWindow
     * @param parent Parent widget (typically nullptr for main window)
     */
    explicit MainWindow(QWidget* parent = nullptr);

    /**
     * @brief Destructor
     */
    ~MainWindow() override;

protected:
    /**
     * @brief Handle close event with unsaved changes confirmation
     * @param event Close event
     */
    void closeEvent(QCloseEvent* event) override;

private slots:
    // File menu actions
    void onNewFile();
    void onOpenFile();
    void onSaveFile();
    void onSaveAsFile();
    void onExit();

    // Edit menu actions
    void onUndo();
    void onRedo();
    void onCut();
    void onCopy();
    void onPaste();
    void onDelete();
    void onSelectAll();

    // View menu actions
    void onResetView();
    void onZoomIn();
    void onZoomOut();
    void onZoomFit();
    void onToggleGrid();
    void onToggleInspector();
    void onTogglePalette();

    // Help menu actions
    void onAbout();
    void onDocumentation();

    // State management
    void onSceneModified();
    void updateWindowTitle();
    void updateActions();

private:
    /**
     * @brief Initialize all UI components
     */
    void setupUI();

    /**
     * @brief Create menu bar and menus
     */
    void createMenus();

    /**
     * @brief Create toolbar
     */
    void createToolBar();

    /**
     * @brief Create dock widgets
     */
    void createDockWidgets();

    /**
     * @brief Connect signals and slots
     */
    void createConnections();

    /**
     * @brief Create all actions
     */
    void createActions();

    /**
     * @brief Prompt user to save unsaved changes
     * @return true if operation should continue, false if cancelled
     */
    bool maybeSave();

    /**
     * @brief Load file from path
     * @param filePath Path to file
     * @return true if successful
     */
    bool loadFile(const QString& filePath);

    /**
     * @brief Save current file
     * @return true if successful
     */
    bool saveFile();

    /**
     * @brief Save to specified file path
     * @param filePath Path to save to
     * @return true if successful
     */
    bool saveFileAs(const QString& filePath);

    /**
     * @brief Set current file and update UI
     * @param filePath Path to current file
     */
    void setCurrentFile(const QString& filePath);

private:
    // Central widgets
    CanvasView* m_canvasView;
    CanvasScene* m_canvasScene;

    // Dock widgets
    QDockWidget* m_inspectorDock;
    InspectorWidget* m_inspectorWidget;
    QDockWidget* m_paletteDock;

    // Menus
    QMenu* m_fileMenu;
    QMenu* m_editMenu;
    QMenu* m_viewMenu;
    QMenu* m_helpMenu;

    // Toolbar
    QToolBar* m_mainToolBar;

    // File menu actions
    QAction* m_newAction;
    QAction* m_openAction;
    QAction* m_saveAction;
    QAction* m_saveAsAction;
    QAction* m_exitAction;

    // Edit menu actions
    QAction* m_undoAction;
    QAction* m_redoAction;
    QAction* m_cutAction;
    QAction* m_copyAction;
    QAction* m_pasteAction;
    QAction* m_deleteAction;
    QAction* m_selectAllAction;

    // View menu actions
    QAction* m_resetViewAction;
    QAction* m_zoomInAction;
    QAction* m_zoomOutAction;
    QAction* m_zoomFitAction;
    QAction* m_toggleGridAction;
    QAction* m_toggleInspectorAction;
    QAction* m_togglePaletteAction;

    // Help menu actions
    QAction* m_aboutAction;
    QAction* m_documentationAction;

    // State
    QString m_currentFilePath;
    bool m_isDirty;
};

} // namespace GUI
} // namespace VSE

#endif // VSE_GUI_MAINWINDOW_H
