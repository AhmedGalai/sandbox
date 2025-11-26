"""
Settings dialog
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QCheckBox,
                             QPushButton, QMessageBox)
from PyQt6.QtCore import QSettings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()

        self.setWindowTitle("Settings")
        self.setFixedSize(400, 250)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        form = QFormLayout()

        # Simulator enabled
        self.simulator_check = QCheckBox()
        self.simulator_check.setChecked(self.settings.value("simulator_enabled", True, bool))
        form.addRow("Enable Simulator:", self.simulator_check)

        # Task confirmation
        self.confirm_check = QCheckBox()
        self.confirm_check.setChecked(self.settings.value("task_confirmation", True, bool))
        form.addRow("Confirm Before Executing Tasks:", self.confirm_check)

        layout.addLayout(form)

        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

    def save_settings(self):
        """Save settings"""
        self.settings.setValue("simulator_enabled", self.simulator_check.isChecked())
        self.settings.setValue("task_confirmation", self.confirm_check.isChecked())

        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully!")
        self.accept()
