/**
 * @file main.cpp
 * @brief Entry point for the Visual Scripting Environment (VSE) application
 *
 * This file initializes the Qt application and creates the main window.
 * The VSE is a visual programming environment that allows users to create
 * and execute logic flows using a node-based interface.
 */

#include <QApplication>
#include <QMessageBox>
#include <QDebug>
#include <iostream>

// Forward declare MainWindow until it's implemented
// #include "gui/MainWindow.h"

/**
 * @brief Main application entry point
 *
 * Initializes the Qt application, sets up the main window,
 * and enters the event loop.
 *
 * @param argc Number of command-line arguments
 * @param argv Array of command-line argument strings
 * @return int Application exit code (0 for success)
 */
int main(int argc, char *argv[])
{
    // Create the Qt application instance
    // This must be created before any other Qt objects
    QApplication app(argc, argv);

    // Set application metadata
    QApplication::setApplicationName("VSE");
    QApplication::setApplicationDisplayName("Visual Scripting Environment");
    QApplication::setApplicationVersion("1.0.0");
    QApplication::setOrganizationName("VSE Project");

    qDebug() << "Starting Visual Scripting Environment...";
    qDebug() << "Qt version:" << qVersion();

    try {
        // TODO: Uncomment once MainWindow is implemented
        /*
        // Create and show the main window
        MainWindow mainWindow;
        mainWindow.setWindowTitle("Visual Scripting Environment");
        mainWindow.show();
        */

        // Temporary: Show a message box until MainWindow is implemented
        QMessageBox msgBox;
        msgBox.setWindowTitle("VSE");
        msgBox.setText("Visual Scripting Environment");
        msgBox.setInformativeText("Build system configured successfully!\n\n"
                                   "The MainWindow will be implemented in the next phase.");
        msgBox.setIcon(QMessageBox::Information);
        msgBox.exec();

        std::cout << "VSE build system is ready!" << std::endl;
        std::cout << "Next steps:" << std::endl;
        std::cout << "  1. Implement core classes (Node, Edge, Topic, DataBus)" << std::endl;
        std::cout << "  2. Implement GUI classes (MainWindow, NodeView, NodeScene)" << std::endl;
        std::cout << "  3. Implement component classes (LogicComponent, MathComponent, etc.)" << std::endl;
        std::cout << "  4. Implement serialization (save/load graphs)" << std::endl;

        // For now, just return success without entering event loop
        return 0;

        // When MainWindow is ready, use this instead:
        // return app.exec();

    } catch (const std::exception& e) {
        qCritical() << "Fatal error:" << e.what();
        QMessageBox::critical(nullptr, "Fatal Error",
            QString("Application encountered a fatal error:\n%1").arg(e.what()));
        return 1;
    } catch (...) {
        qCritical() << "Unknown fatal error occurred";
        QMessageBox::critical(nullptr, "Fatal Error",
            "Application encountered an unknown fatal error");
        return 1;
    }
}
