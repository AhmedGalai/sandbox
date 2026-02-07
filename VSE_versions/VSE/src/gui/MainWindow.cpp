/**
 * @file MainWindow.cpp
 * @brief Implementation of MainWindow
 */

#include "gui/MainWindow.h"
#include "gui/CanvasView.h"
#include "gui/CanvasScene.h"
#include "gui/InspectorWidget.h"

#include <QMenuBar>
#include <QToolBar>
#include <QDockWidget>
#include <QStatusBar>
#include <QAction>
#include <QFileDialog>
#include <QMessageBox>
#include <QCloseEvent>
#include <QSettings>
#include <QLabel>
#include <QVBoxLayout>
#include <QApplication>

namespace VSE {
namespace GUI {

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent)
    , m_canvasView(nullptr)
    , m_canvasScene(nullptr)
    , m_inspectorDock(nullptr)
    , m_inspectorWidget(nullptr)
    , m_paletteDock(nullptr)
    , m_isDirty(false)
{
    setWindowTitle("Visual Scripting Environment");
    resize(1400, 900);

    setupUI();
    createActions();
    createMenus();
    createToolBar();
    createDockWidgets();
    createConnections();

    // Initialize state
    setCurrentFile("");
    updateActions();

    // Restore window geometry
    QSettings settings("VSE", "VisualScriptingEnvironment");
    restoreGeometry(settings.value("geometry").toByteArray());
    restoreState(settings.value("windowState").toByteArray());

    statusBar()->showMessage("Ready", 3000);
}

MainWindow::~MainWindow()
{
    // Save window geometry
    QSettings settings("VSE", "VisualScriptingEnvironment");
    settings.setValue("geometry", saveGeometry());
    settings.setValue("windowState", saveState());
}

void MainWindow::setupUI()
{
    // Create scene and view
    m_canvasScene = new CanvasScene(this);
    m_canvasView = new CanvasView(m_canvasScene, this);

    // Set as central widget
    setCentralWidget(m_canvasView);

    // Create status bar
    statusBar()->showMessage("Ready");
}

void MainWindow::createActions()
{
    // File actions
    m_newAction = new QAction(tr("&New"), this);
    m_newAction->setShortcut(QKeySequence::New);
    m_newAction->setStatusTip(tr("Create a new script"));
    m_newAction->setIcon(QIcon::fromTheme("document-new"));

    m_openAction = new QAction(tr("&Open..."), this);
    m_openAction->setShortcut(QKeySequence::Open);
    m_openAction->setStatusTip(tr("Open an existing script"));
    m_openAction->setIcon(QIcon::fromTheme("document-open"));

    m_saveAction = new QAction(tr("&Save"), this);
    m_saveAction->setShortcut(QKeySequence::Save);
    m_saveAction->setStatusTip(tr("Save the current script"));
    m_saveAction->setIcon(QIcon::fromTheme("document-save"));

    m_saveAsAction = new QAction(tr("Save &As..."), this);
    m_saveAsAction->setShortcut(QKeySequence::SaveAs);
    m_saveAsAction->setStatusTip(tr("Save the script with a new name"));
    m_saveAsAction->setIcon(QIcon::fromTheme("document-save-as"));

    m_exitAction = new QAction(tr("E&xit"), this);
    m_exitAction->setShortcut(QKeySequence::Quit);
    m_exitAction->setStatusTip(tr("Exit the application"));
    m_exitAction->setIcon(QIcon::fromTheme("application-exit"));

    // Edit actions
    m_undoAction = new QAction(tr("&Undo"), this);
    m_undoAction->setShortcut(QKeySequence::Undo);
    m_undoAction->setStatusTip(tr("Undo last action"));
    m_undoAction->setIcon(QIcon::fromTheme("edit-undo"));
    m_undoAction->setEnabled(false);

    m_redoAction = new QAction(tr("&Redo"), this);
    m_redoAction->setShortcut(QKeySequence::Redo);
    m_redoAction->setStatusTip(tr("Redo last undone action"));
    m_redoAction->setIcon(QIcon::fromTheme("edit-redo"));
    m_redoAction->setEnabled(false);

    m_cutAction = new QAction(tr("Cu&t"), this);
    m_cutAction->setShortcut(QKeySequence::Cut);
    m_cutAction->setStatusTip(tr("Cut selected items"));
    m_cutAction->setIcon(QIcon::fromTheme("edit-cut"));

    m_copyAction = new QAction(tr("&Copy"), this);
    m_copyAction->setShortcut(QKeySequence::Copy);
    m_copyAction->setStatusTip(tr("Copy selected items"));
    m_copyAction->setIcon(QIcon::fromTheme("edit-copy"));

    m_pasteAction = new QAction(tr("&Paste"), this);
    m_pasteAction->setShortcut(QKeySequence::Paste);
    m_pasteAction->setStatusTip(tr("Paste items from clipboard"));
    m_pasteAction->setIcon(QIcon::fromTheme("edit-paste"));

    m_deleteAction = new QAction(tr("&Delete"), this);
    m_deleteAction->setShortcut(QKeySequence::Delete);
    m_deleteAction->setStatusTip(tr("Delete selected items"));
    m_deleteAction->setIcon(QIcon::fromTheme("edit-delete"));

    m_selectAllAction = new QAction(tr("Select &All"), this);
    m_selectAllAction->setShortcut(QKeySequence::SelectAll);
    m_selectAllAction->setStatusTip(tr("Select all items"));
    m_selectAllAction->setIcon(QIcon::fromTheme("edit-select-all"));

    // View actions
    m_resetViewAction = new QAction(tr("&Reset View"), this);
    m_resetViewAction->setShortcut(QKeySequence(Qt::CTRL | Qt::Key_0));
    m_resetViewAction->setStatusTip(tr("Reset view to default"));
    m_resetViewAction->setIcon(QIcon::fromTheme("zoom-original"));

    m_zoomInAction = new QAction(tr("Zoom &In"), this);
    m_zoomInAction->setShortcut(QKeySequence::ZoomIn);
    m_zoomInAction->setStatusTip(tr("Zoom in"));
    m_zoomInAction->setIcon(QIcon::fromTheme("zoom-in"));

    m_zoomOutAction = new QAction(tr("Zoom &Out"), this);
    m_zoomOutAction->setShortcut(QKeySequence::ZoomOut);
    m_zoomOutAction->setStatusTip(tr("Zoom out"));
    m_zoomOutAction->setIcon(QIcon::fromTheme("zoom-out"));

    m_zoomFitAction = new QAction(tr("&Fit to View"), this);
    m_zoomFitAction->setShortcut(QKeySequence(Qt::CTRL | Qt::Key_F));
    m_zoomFitAction->setStatusTip(tr("Fit all items in view"));
    m_zoomFitAction->setIcon(QIcon::fromTheme("zoom-fit-best"));

    m_toggleGridAction = new QAction(tr("Show &Grid"), this);
    m_toggleGridAction->setCheckable(true);
    m_toggleGridAction->setChecked(true);
    m_toggleGridAction->setStatusTip(tr("Toggle grid display"));

    m_toggleInspectorAction = new QAction(tr("Show &Inspector"), this);
    m_toggleInspectorAction->setCheckable(true);
    m_toggleInspectorAction->setChecked(true);
    m_toggleInspectorAction->setStatusTip(tr("Toggle inspector panel"));

    m_togglePaletteAction = new QAction(tr("Show &Palette"), this);
    m_togglePaletteAction->setCheckable(true);
    m_togglePaletteAction->setChecked(true);
    m_togglePaletteAction->setStatusTip(tr("Toggle component palette"));

    // Help actions
    m_aboutAction = new QAction(tr("&About"), this);
    m_aboutAction->setStatusTip(tr("About Visual Scripting Environment"));
    m_aboutAction->setIcon(QIcon::fromTheme("help-about"));

    m_documentationAction = new QAction(tr("&Documentation"), this);
    m_documentationAction->setShortcut(QKeySequence::HelpContents);
    m_documentationAction->setStatusTip(tr("Open documentation"));
    m_documentationAction->setIcon(QIcon::fromTheme("help-contents"));
}

void MainWindow::createMenus()
{
    // File menu
    m_fileMenu = menuBar()->addMenu(tr("&File"));
    m_fileMenu->addAction(m_newAction);
    m_fileMenu->addAction(m_openAction);
    m_fileMenu->addSeparator();
    m_fileMenu->addAction(m_saveAction);
    m_fileMenu->addAction(m_saveAsAction);
    m_fileMenu->addSeparator();
    m_fileMenu->addAction(m_exitAction);

    // Edit menu
    m_editMenu = menuBar()->addMenu(tr("&Edit"));
    m_editMenu->addAction(m_undoAction);
    m_editMenu->addAction(m_redoAction);
    m_editMenu->addSeparator();
    m_editMenu->addAction(m_cutAction);
    m_editMenu->addAction(m_copyAction);
    m_editMenu->addAction(m_pasteAction);
    m_editMenu->addAction(m_deleteAction);
    m_editMenu->addSeparator();
    m_editMenu->addAction(m_selectAllAction);

    // View menu
    m_viewMenu = menuBar()->addMenu(tr("&View"));
    m_viewMenu->addAction(m_resetViewAction);
    m_viewMenu->addAction(m_zoomInAction);
    m_viewMenu->addAction(m_zoomOutAction);
    m_viewMenu->addAction(m_zoomFitAction);
    m_viewMenu->addSeparator();
    m_viewMenu->addAction(m_toggleGridAction);
    m_viewMenu->addSeparator();
    m_viewMenu->addAction(m_toggleInspectorAction);
    m_viewMenu->addAction(m_togglePaletteAction);

    // Help menu
    m_helpMenu = menuBar()->addMenu(tr("&Help"));
    m_helpMenu->addAction(m_documentationAction);
    m_helpMenu->addSeparator();
    m_helpMenu->addAction(m_aboutAction);
}

void MainWindow::createToolBar()
{
    m_mainToolBar = addToolBar(tr("Main Toolbar"));
    m_mainToolBar->setObjectName("MainToolBar");
    m_mainToolBar->setMovable(false);

    m_mainToolBar->addAction(m_newAction);
    m_mainToolBar->addAction(m_openAction);
    m_mainToolBar->addAction(m_saveAction);
    m_mainToolBar->addSeparator();
    m_mainToolBar->addAction(m_undoAction);
    m_mainToolBar->addAction(m_redoAction);
    m_mainToolBar->addSeparator();
    m_mainToolBar->addAction(m_cutAction);
    m_mainToolBar->addAction(m_copyAction);
    m_mainToolBar->addAction(m_pasteAction);
    m_mainToolBar->addAction(m_deleteAction);
    m_mainToolBar->addSeparator();
    m_mainToolBar->addAction(m_zoomInAction);
    m_mainToolBar->addAction(m_zoomOutAction);
    m_mainToolBar->addAction(m_resetViewAction);
}

void MainWindow::createDockWidgets()
{
    // Inspector dock (right side)
    m_inspectorWidget = new InspectorWidget(this);
    m_inspectorDock = new QDockWidget(tr("Inspector"), this);
    m_inspectorDock->setObjectName("InspectorDock");
    m_inspectorDock->setWidget(m_inspectorWidget);
    m_inspectorDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    addDockWidget(Qt::RightDockWidgetArea, m_inspectorDock);

    // Component palette dock (left side)
    m_paletteDock = new QDockWidget(tr("Components"), this);
    m_paletteDock->setObjectName("ComponentPaletteDock");

    // Placeholder widget for palette
    QWidget* paletteWidget = new QWidget(this);
    QVBoxLayout* paletteLayout = new QVBoxLayout(paletteWidget);
    QLabel* paletteLabel = new QLabel(tr("Component Palette\n(Coming Soon)"), paletteWidget);
    paletteLabel->setAlignment(Qt::AlignCenter);
    paletteLabel->setStyleSheet("color: gray; padding: 20px;");
    paletteLayout->addWidget(paletteLabel);
    paletteWidget->setLayout(paletteLayout);

    m_paletteDock->setWidget(paletteWidget);
    m_paletteDock->setAllowedAreas(Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea);
    addDockWidget(Qt::LeftDockWidgetArea, m_paletteDock);
}

void MainWindow::createConnections()
{
    // File menu
    connect(m_newAction, &QAction::triggered, this, &MainWindow::onNewFile);
    connect(m_openAction, &QAction::triggered, this, &MainWindow::onOpenFile);
    connect(m_saveAction, &QAction::triggered, this, &MainWindow::onSaveFile);
    connect(m_saveAsAction, &QAction::triggered, this, &MainWindow::onSaveAsFile);
    connect(m_exitAction, &QAction::triggered, this, &MainWindow::onExit);

    // Edit menu
    connect(m_undoAction, &QAction::triggered, this, &MainWindow::onUndo);
    connect(m_redoAction, &QAction::triggered, this, &MainWindow::onRedo);
    connect(m_cutAction, &QAction::triggered, this, &MainWindow::onCut);
    connect(m_copyAction, &QAction::triggered, this, &MainWindow::onCopy);
    connect(m_pasteAction, &QAction::triggered, this, &MainWindow::onPaste);
    connect(m_deleteAction, &QAction::triggered, this, &MainWindow::onDelete);
    connect(m_selectAllAction, &QAction::triggered, this, &MainWindow::onSelectAll);

    // View menu
    connect(m_resetViewAction, &QAction::triggered, this, &MainWindow::onResetView);
    connect(m_zoomInAction, &QAction::triggered, this, &MainWindow::onZoomIn);
    connect(m_zoomOutAction, &QAction::triggered, this, &MainWindow::onZoomOut);
    connect(m_zoomFitAction, &QAction::triggered, this, &MainWindow::onZoomFit);
    connect(m_toggleGridAction, &QAction::toggled, this, &MainWindow::onToggleGrid);
    connect(m_toggleInspectorAction, &QAction::toggled, this, &MainWindow::onToggleInspector);
    connect(m_togglePaletteAction, &QAction::toggled, this, &MainWindow::onTogglePalette);

    // Help menu
    connect(m_aboutAction, &QAction::triggered, this, &MainWindow::onAbout);
    connect(m_documentationAction, &QAction::triggered, this, &MainWindow::onDocumentation);

    // Scene changes
    connect(m_canvasScene, &CanvasScene::sceneModified, this, &MainWindow::onSceneModified);

    // Dock widget visibility
    connect(m_inspectorDock, &QDockWidget::visibilityChanged,
            m_toggleInspectorAction, &QAction::setChecked);
    connect(m_paletteDock, &QDockWidget::visibilityChanged,
            m_togglePaletteAction, &QAction::setChecked);
}

void MainWindow::closeEvent(QCloseEvent* event)
{
    if (maybeSave()) {
        event->accept();
    } else {
        event->ignore();
    }
}

// File menu slots
void MainWindow::onNewFile()
{
    if (maybeSave()) {
        m_canvasScene->clear();
        setCurrentFile("");
        m_isDirty = false;
        updateWindowTitle();
        statusBar()->showMessage(tr("New file created"), 3000);
    }
}

void MainWindow::onOpenFile()
{
    if (!maybeSave()) {
        return;
    }

    QString filePath = QFileDialog::getOpenFileName(
        this,
        tr("Open Script"),
        "",
        tr("VSE Scripts (*.vse);;All Files (*)")
    );

    if (!filePath.isEmpty()) {
        if (loadFile(filePath)) {
            statusBar()->showMessage(tr("File loaded: %1").arg(filePath), 3000);
        }
    }
}

void MainWindow::onSaveFile()
{
    if (m_currentFilePath.isEmpty()) {
        onSaveAsFile();
    } else {
        saveFile();
    }
}

void MainWindow::onSaveAsFile()
{
    QString filePath = QFileDialog::getSaveFileName(
        this,
        tr("Save Script"),
        "",
        tr("VSE Scripts (*.vse);;All Files (*)")
    );

    if (!filePath.isEmpty()) {
        if (saveFileAs(filePath)) {
            statusBar()->showMessage(tr("File saved: %1").arg(filePath), 3000);
        }
    }
}

void MainWindow::onExit()
{
    close();
}

// Edit menu slots
void MainWindow::onUndo()
{
    // TODO: Implement undo functionality
    statusBar()->showMessage(tr("Undo not yet implemented"), 3000);
}

void MainWindow::onRedo()
{
    // TODO: Implement redo functionality
    statusBar()->showMessage(tr("Redo not yet implemented"), 3000);
}

void MainWindow::onCut()
{
    // TODO: Implement cut functionality
    statusBar()->showMessage(tr("Cut not yet implemented"), 3000);
}

void MainWindow::onCopy()
{
    // TODO: Implement copy functionality
    statusBar()->showMessage(tr("Copy not yet implemented"), 3000);
}

void MainWindow::onPaste()
{
    // TODO: Implement paste functionality
    statusBar()->showMessage(tr("Paste not yet implemented"), 3000);
}

void MainWindow::onDelete()
{
    m_canvasScene->deleteSelectedItems();
    statusBar()->showMessage(tr("Deleted selected items"), 3000);
}

void MainWindow::onSelectAll()
{
    QPainterPath path;
    path.addRect(m_canvasScene->sceneRect());
    m_canvasScene->setSelectionArea(path);
    statusBar()->showMessage(tr("All items selected"), 3000);
}

// View menu slots
void MainWindow::onResetView()
{
    m_canvasView->resetView();
    statusBar()->showMessage(tr("View reset"), 3000);
}

void MainWindow::onZoomIn()
{
    m_canvasView->zoomIn();
}

void MainWindow::onZoomOut()
{
    m_canvasView->zoomOut();
}

void MainWindow::onZoomFit()
{
    m_canvasView->fitInView();
}

void MainWindow::onToggleGrid()
{
    m_canvasView->setGridVisible(m_toggleGridAction->isChecked());
}

void MainWindow::onToggleInspector()
{
    m_inspectorDock->setVisible(m_toggleInspectorAction->isChecked());
}

void MainWindow::onTogglePalette()
{
    m_paletteDock->setVisible(m_togglePaletteAction->isChecked());
}

// Help menu slots
void MainWindow::onAbout()
{
    QMessageBox::about(this, tr("About VSE"),
        tr("<h2>Visual Scripting Environment</h2>"
           "<p>Version 1.0</p>"
           "<p>A Qt6-based visual scripting environment for creating "
           "interactive node-based programs.</p>"
           "<p>Features:</p>"
           "<ul>"
           "<li>Interactive node graph editor</li>"
           "<li>Real-time component property editing</li>"
           "<li>Extensible component system</li>"
           "</ul>"
           "<p>Built with Qt6</p>"));
}

void MainWindow::onDocumentation()
{
    QMessageBox::information(this, tr("Documentation"),
        tr("Documentation is not yet available.\n"
           "Please refer to the README file in the project directory."));
}

// State management
void MainWindow::onSceneModified()
{
    m_isDirty = true;
    updateWindowTitle();
}

void MainWindow::updateWindowTitle()
{
    QString title = "Visual Scripting Environment";

    if (!m_currentFilePath.isEmpty()) {
        QFileInfo fileInfo(m_currentFilePath);
        title = fileInfo.fileName() + " - " + title;
    } else {
        title = "Untitled - " + title;
    }

    if (m_isDirty) {
        title = "*" + title;
    }

    setWindowTitle(title);
}

void MainWindow::updateActions()
{
    bool hasSelection = !m_canvasScene->selectedItems().isEmpty();
    m_cutAction->setEnabled(hasSelection);
    m_copyAction->setEnabled(hasSelection);
    m_deleteAction->setEnabled(hasSelection);
}

bool MainWindow::maybeSave()
{
    if (!m_isDirty) {
        return true;
    }

    QMessageBox::StandardButton result = QMessageBox::question(
        this,
        tr("Unsaved Changes"),
        tr("The document has been modified.\nDo you want to save your changes?"),
        QMessageBox::Save | QMessageBox::Discard | QMessageBox::Cancel,
        QMessageBox::Save
    );

    switch (result) {
        case QMessageBox::Save:
            return saveFile();
        case QMessageBox::Discard:
            return true;
        case QMessageBox::Cancel:
        default:
            return false;
    }
}

bool MainWindow::loadFile(const QString& filePath)
{
    // TODO: Implement actual file loading with serialization
    // For now, just update the current file
    setCurrentFile(filePath);
    m_isDirty = false;
    updateWindowTitle();
    return true;
}

bool MainWindow::saveFile()
{
    if (m_currentFilePath.isEmpty()) {
        return false;
    }
    return saveFileAs(m_currentFilePath);
}

bool MainWindow::saveFileAs(const QString& filePath)
{
    // TODO: Implement actual file saving with serialization
    // For now, just update the current file
    setCurrentFile(filePath);
    m_isDirty = false;
    updateWindowTitle();
    return true;
}

void MainWindow::setCurrentFile(const QString& filePath)
{
    m_currentFilePath = filePath;
    updateWindowTitle();
}

} // namespace GUI
} // namespace VSE
