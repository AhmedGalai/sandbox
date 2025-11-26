"""
Theme manager for light and dark modes
"""

class ThemeManager:
    def __init__(self):
        self.is_dark = False

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.is_dark = not self.is_dark
        return self.is_dark

    def set_dark_theme(self):
        """Set dark theme"""
        self.is_dark = True

    def set_light_theme(self):
        """Set light theme"""
        self.is_dark = False

    def get_stylesheet(self):
        """Get the current stylesheet"""
        if self.is_dark:
            return self._dark_stylesheet()
        return self._light_stylesheet()

    def _light_stylesheet(self):
        """Light theme stylesheet"""
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QWidget#header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        QLabel#title {
            font-size: 20px;
            font-weight: bold;
            color: white;
        }
        QPushButton {
            background-color: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #764ba2;
        }
        QPushButton#theme-button {
            background-color: rgba(255, 255, 255, 0.2);
            font-size: 18px;
        }
        QPushButton#logout-button {
            background-color: #dc3545;
        }
        QPushButton#logout-button:hover {
            background-color: #c82333;
        }
        QTabWidget::pane {
            border: 1px solid #ddd;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #f0f0f0;
            color: #333;
            padding: 10px 20px;
            border: 1px solid #ddd;
            border-bottom: none;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: white;
            color: #667eea;
            font-weight: bold;
        }
        QGroupBox {
            border: 2px solid #ddd;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QTextEdit {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 5px;
        }
        QListWidget {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        QTableWidget {
            background-color: white;
            border: 1px solid #ddd;
            gridline-color: #ddd;
        }
        QTableWidget::item {
            padding: 5px;
        }
        QHeaderView::section {
            background-color: #667eea;
            color: white;
            padding: 5px;
            border: none;
            font-weight: bold;
        }
        """

    def _dark_stylesheet(self):
        """Dark theme stylesheet"""
        return """
        QMainWindow {
            background-color: #1a1a1a;
            color: #e0e0e0;
        }
        QWidget {
            background-color: #1a1a1a;
            color: #e0e0e0;
        }
        QWidget#header {
            background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
            color: white;
        }
        QLabel {
            color: #e0e0e0;
        }
        QLabel#title {
            font-size: 20px;
            font-weight: bold;
            color: white;
        }
        QPushButton {
            background-color: #4a5568;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #5a6578;
        }
        QPushButton#theme-button {
            background-color: rgba(255, 255, 255, 0.1);
            font-size: 18px;
        }
        QPushButton#logout-button {
            background-color: #c53030;
        }
        QPushButton#logout-button:hover {
            background-color: #9b2c2c;
        }
        QTabWidget::pane {
            border: 1px solid #333;
            background-color: #2d2d2d;
        }
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #a0a0a0;
            padding: 10px 20px;
            border: 1px solid #333;
            border-bottom: none;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #3a3a3a;
            color: #667eea;
            font-weight: bold;
        }
        QGroupBox {
            border: 2px solid #444;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
            color: #e0e0e0;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QTextEdit {
            background-color: #2d2d2d;
            border: 1px solid #444;
            border-radius: 5px;
            padding: 5px;
            color: #e0e0e0;
        }
        QLineEdit {
            background-color: #2d2d2d;
            border: 1px solid #444;
            border-radius: 5px;
            padding: 5px;
            color: #e0e0e0;
        }
        QListWidget {
            background-color: #2d2d2d;
            border: 1px solid #444;
            border-radius: 5px;
            color: #e0e0e0;
        }
        QTableWidget {
            background-color: #2d2d2d;
            border: 1px solid #444;
            gridline-color: #444;
            color: #e0e0e0;
        }
        QTableWidget::item {
            padding: 5px;
        }
        QHeaderView::section {
            background-color: #4a5568;
            color: white;
            padding: 5px;
            border: none;
            font-weight: bold;
        }
        QComboBox {
            background-color: #2d2d2d;
            border: 1px solid #444;
            border-radius: 5px;
            padding: 5px;
            color: #e0e0e0;
        }
        QComboBox QAbstractItemView {
            background-color: #2d2d2d;
            border: 1px solid #444;
            selection-background-color: #4a5568;
            color: #e0e0e0;
        }
        QSpinBox, QDoubleSpinBox {
            background-color: #2d2d2d;
            border: 1px solid #444;
            border-radius: 5px;
            padding: 5px;
            color: #e0e0e0;
        }
        QSlider::groove:horizontal {
            background: #444;
            height: 8px;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #667eea;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        QCheckBox {
            color: #e0e0e0;
        }
        QRadioButton {
            color: #e0e0e0;
        }
        """
