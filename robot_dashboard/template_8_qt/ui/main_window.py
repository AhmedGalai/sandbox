"""
Main application window with tabbed interface
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QPushButton, QLabel, QMessageBox, QMenuBar, QMenu)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction, QIcon

from .login_dialog import LoginDialog
from .dashboard_tab import DashboardTab
from .systems_tab import SystemsTab
from .docs_tab import DocsTab
from .settings_dialog import SettingsDialog
from utils.theme import ThemeManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        self.theme_manager = ThemeManager()
        self.is_authenticated = False

        self.setWindowTitle("Robot Simulator Dashboard")
        self.setGeometry(100, 100, 1400, 900)

        # Initialize UI
        self.init_ui()

        # Load theme preference
        self.load_theme_preference()

        # Show login dialog
        self.show_login()

    def init_ui(self):
        """Initialize the user interface"""
        # Create menu bar
        self.create_menu_bar()

        # Create central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create header
        header = self.create_header()
        layout.addWidget(header)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        layout.addWidget(self.tabs)

        # Create tabs
        self.dashboard_tab = DashboardTab()
        self.systems_tab = SystemsTab()
        self.docs_tab = DocsTab()

        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.systems_tab, "Systems")
        self.tabs.addTab(self.docs_tab, "Docs")

    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        theme_action = QAction("Toggle &Theme", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_header(self):
        """Create the header bar"""
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(60)

        layout = QHBoxLayout(header)

        # Logo and title
        title_label = QLabel("🤖 Robot Simulator")
        title_label.setObjectName("title")
        layout.addWidget(title_label)

        layout.addStretch()

        # Theme toggle button
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setObjectName("theme-button")
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setToolTip("Toggle Theme")
        layout.addWidget(self.theme_btn)

        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("logout-button")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        return header

    def show_login(self):
        """Show the login dialog"""
        dialog = LoginDialog(self)
        if dialog.exec():
            self.is_authenticated = True
            username = dialog.get_username()
            # Save username
            self.settings.setValue("username", username)
        else:
            # User cancelled login, exit app
            self.close()

    def logout(self):
        """Handle logout"""
        reply = QMessageBox.question(self, "Logout",
                                    "Are you sure you want to logout?",
                                    QMessageBox.StandardButton.Yes |
                                    QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.is_authenticated = False
            self.show_login()

    def show_settings(self):
        """Show the settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        is_dark = self.theme_manager.toggle_theme()

        # Update button icon
        self.theme_btn.setText("☀️" if is_dark else "🌙")

        # Apply theme to application
        self.setStyleSheet(self.theme_manager.get_stylesheet())

        # Save preference
        self.settings.setValue("theme", "dark" if is_dark else "light")

    def load_theme_preference(self):
        """Load the saved theme preference"""
        theme = self.settings.value("theme", "light")

        if theme == "dark":
            self.theme_manager.set_dark_theme()
            self.theme_btn.setText("☀️")
        else:
            self.theme_manager.set_light_theme()
            self.theme_btn.setText("🌙")

        # Apply theme
        self.setStyleSheet(self.theme_manager.get_stylesheet())

    def show_about(self):
        """Show the about dialog"""
        QMessageBox.about(self, "About Robot Simulator",
                         "<h2>Robot Simulator Dashboard</h2>"
                         "<p>Version 1.0 - PyQt Edition</p>"
                         "<p>A dynamic robot control and monitoring system</p>"
                         "<p>Built with PyQt6</p>")
