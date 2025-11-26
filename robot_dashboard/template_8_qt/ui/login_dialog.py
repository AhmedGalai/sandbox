"""
Login dialog for authentication
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.username = ""

        self.setWindowTitle("Login")
        self.setModal(True)
        self.setFixedSize(400, 250)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("Robot Simulator Login")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Username field
        username_label = QLabel("Username:")
        layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        # Load saved username from session
        saved_username = self.settings.value("username", "")
        if saved_username:
            self.username_input.setText(saved_username)
        layout.addWidget(self.username_input)

        # Password field
        password_label = QLabel("Password:")
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input)

        # Error message
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.setObjectName("login-button")
        login_btn.clicked.connect(self.handle_login)
        login_btn.setFixedHeight(40)
        layout.addWidget(login_btn)

        # Hint
        hint = QLabel("Default credentials: admin / admin")
        hint.setStyleSheet("color: gray; font-size: 12px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

    def handle_login(self):
        """Handle the login process"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.error_label.setText("Please enter username and password")
            return

        # Simple authentication (same as web version)
        if username == "admin" and password == "admin":
            self.username = username
            self.accept()
        else:
            self.error_label.setText("Invalid credentials. Try admin/admin")
            self.password_input.clear()
            self.password_input.setFocus()

    def get_username(self):
        """Get the authenticated username"""
        return self.username
