"""
Documentation tab
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QTextEdit,
                             QSplitter)
from PyQt6.QtCore import Qt


class DocsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Doc list
        self.doc_list = QListWidget()
        self.doc_list.addItems([
            "README",
            "Quick Start Guide",
            "Setup Instructions",
            "Features",
            "Testing Guide"
        ])
        self.doc_list.currentRowChanged.connect(self.load_doc)
        splitter.addWidget(self.doc_list)

        # Doc viewer
        self.doc_viewer = QTextEdit()
        self.doc_viewer.setReadOnly(True)
        self.doc_viewer.setPlaceholderText("Select a document to view...")
        splitter.addWidget(self.doc_viewer)

        splitter.setSizes([250, 750])

        layout.addWidget(splitter)

    def load_doc(self, index):
        """Load a document"""
        docs = {
            0: "# README\n\nRobot Simulator Dashboard - PyQt Version\n\nThis is a comprehensive robot control and monitoring system.",
            1: "# Quick Start\n\n1. Install PyQt6\n2. Run main.py\n3. Login with admin/admin",
            2: "# Setup\n\nInstall dependencies:\npip install -r requirements.txt",
            3: "# Features\n\n- Multi-robot control\n- Path planning\n- Task management\n- Real-time visualization",
            4: "# Testing\n\nRun tests:\npython -m pytest tests/"
        }

        self.doc_viewer.setMarkdown(docs.get(index, "No content available"))
