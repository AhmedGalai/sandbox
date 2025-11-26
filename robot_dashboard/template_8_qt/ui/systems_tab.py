"""
Systems tab for AI task planning
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QTextEdit)


class SystemsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        # Task plan display
        plan_group = QGroupBox("Current Task Plan")
        plan_layout = QVBoxLayout(plan_group)

        self.plan_display = QTextEdit()
        self.plan_display.setReadOnly(True)
        self.plan_display.setPlainText("No active plan. Send a command via the chatbot to see the AI planning process.")
        plan_layout.addWidget(self.plan_display)

        layout.addWidget(plan_group)

        # Execution status
        status_group = QGroupBox("Execution Status")
        status_layout = QVBoxLayout(status_group)

        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setPlainText("Idle - Waiting for tasks...")
        status_layout.addWidget(self.status_display)

        layout.addWidget(status_group)
