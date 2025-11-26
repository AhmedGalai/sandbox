"""
Chat widget for robot control
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QLineEdit, QPushButton)
from PyQt6.QtCore import Qt


class ChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        # Chat messages display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Chat messages will appear here...")
        layout.addWidget(self.chat_display)

        # Add initial welcome message
        self.add_message("Hello! I'm your robot control assistant. You can give me tasks for the robot to execute!", "bot")

        # Chat input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Give robot a task...")
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)

    def send_message(self):
        """Send a message"""
        message = self.chat_input.text().strip()
        if not message:
            return

        # Add user message
        self.add_message(message, "user")

        # Clear input
        self.chat_input.clear()

        # Simulate bot response
        self.add_message("Task received! I'll process your request.", "bot")

    def add_message(self, text, sender):
        """Add a message to the chat display"""
        if sender == "user":
            html = f'<div style="text-align: right; margin: 5px; padding: 8px; background-color: #667eea; color: white; border-radius: 10px;"><b>You:</b> {text}</div>'
        else:
            html = f'<div style="text-align: left; margin: 5px; padding: 8px; background-color: #f0f0f0; border-radius: 10px;"><b>Bot:</b> {text}</div>'

        self.chat_display.append(html)
