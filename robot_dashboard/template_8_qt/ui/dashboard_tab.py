"""
Dashboard tab with robot simulator and controls
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QPushButton, QComboBox, QListWidget,
                             QTableWidget, QTableWidgetItem, QSplitter, QTextEdit,
                             QLineEdit, QSlider, QRadioButton, QButtonGroup, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from .robot_canvas import RobotCanvas
from .chat_widget import ChatWidget
import json


class DashboardTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        main_layout = QHBoxLayout(self)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Chat
        chat_panel = self.create_chat_panel()
        splitter.addWidget(chat_panel)

        # Right side - Simulator and controls
        right_panel = self.create_simulator_panel()
        splitter.addWidget(right_panel)

        # Set initial sizes
        splitter.setSizes([350, 1050])

        main_layout.addWidget(splitter)

    def create_chat_panel(self):
        """Create the chat panel"""
        panel = QGroupBox("Robot Control")
        layout = QVBoxLayout(panel)

        self.chat_widget = ChatWidget()
        layout.addWidget(self.chat_widget)

        return panel

    def create_simulator_panel(self):
        """Create the simulator panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Business name and robot selection
        top_row = QHBoxLayout()

        # Business name
        business_group = QGroupBox("Business Name")
        business_layout = QVBoxLayout(business_group)
        business_input = QLineEdit("ACME Robotics Corp")
        business_input.setEnabled(False)
        business_layout.addWidget(business_input)
        top_row.addWidget(business_group)

        # Robot selection
        robot_group = QGroupBox("Select Robots")
        robot_layout = QVBoxLayout(robot_group)
        self.robot_list = QListWidget()
        self.robot_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.robot_list.addItems([
            "ROB-001 (Active)",
            "ROB-002 (Idle)",
            "ROB-003 (Charging)",
            "ROB-004 (Active)",
            "ROB-005 (Maintenance)"
        ])
        self.robot_list.item(0).setSelected(True)
        self.robot_list.itemSelectionChanged.connect(self.on_robot_selection_changed)
        robot_layout.addWidget(self.robot_list)
        hint = QLabel("Hold Ctrl to select multiple")
        hint.setStyleSheet("color: gray; font-size: 11px;")
        robot_layout.addWidget(hint)
        top_row.addWidget(robot_group)

        layout.addLayout(top_row)

        # Main content area - splitter for horizontal split
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Map and status
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Robot canvas
        self.robot_canvas = RobotCanvas()
        canvas_group = QGroupBox("Map")
        canvas_layout = QVBoxLayout(canvas_group)
        canvas_layout.addWidget(self.robot_canvas)
        left_layout.addWidget(canvas_group)

        # Robot status table
        status_group = self.create_status_table()
        left_layout.addWidget(status_group)

        # Map status table
        map_status_group = self.create_map_status_table()
        left_layout.addWidget(map_status_group)

        content_splitter.addWidget(left_panel)

        # Right side - Task control and builder
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Task control
        task_control = self.create_task_control()
        right_layout.addWidget(task_control)

        # Task builder
        task_builder = self.create_task_builder()
        right_layout.addWidget(task_builder)

        content_splitter.addWidget(right_panel)

        # Set sizes
        content_splitter.setSizes([700, 350])

        layout.addWidget(content_splitter)

        # Update status periodically
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(500)  # Update every 500ms

    def create_status_table(self):
        """Create robot status table"""
        group = QGroupBox("Robot Status")
        layout = QVBoxLayout(group)

        self.status_table = QTableWidget(8, 2)
        self.status_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.status_table.verticalHeader().setVisible(False)

        properties = ["Position X", "Position Y", "Heading", "Current Task",
                     "Status", "Nearest Label", "Distance to Target", "Errors"]
        for i, prop in enumerate(properties):
            self.status_table.setItem(i, 0, QTableWidgetItem(prop))
            self.status_table.setItem(i, 1, QTableWidgetItem("-"))

        self.status_table.resizeColumnsToContents()
        layout.addWidget(self.status_table)

        return group

    def create_map_status_table(self):
        """Create map status table"""
        group = QGroupBox("Map Status")
        layout = QVBoxLayout(group)

        self.map_status_table = QTableWidget(5, 2)
        self.map_status_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.map_status_table.verticalHeader().setVisible(False)

        properties = ["Grid Size", "Work Points", "Charging Points", "Obstacles", "Free Cells"]
        values = ["20 x 20", "A(18,3), B(7,12), C(16,16)", "⚡(2,18)", "50 cells", "347 cells"]

        for i, (prop, val) in enumerate(zip(properties, values)):
            self.map_status_table.setItem(i, 0, QTableWidgetItem(prop))
            self.map_status_table.setItem(i, 1, QTableWidgetItem(val))

        self.map_status_table.resizeColumnsToContents()
        layout.addWidget(self.map_status_table)

        return group

    def create_task_control(self):
        """Create task control panel"""
        group = QGroupBox("Task Control")
        layout = QVBoxLayout(group)

        # POI dropdown
        poi_label = QLabel("Select Point of Interest:")
        layout.addWidget(poi_label)

        self.poi_combo = QComboBox()
        self.poi_combo.addItems(["Point A", "Point B", "Point C", "Charging Station", "Standby Point"])
        layout.addWidget(self.poi_combo)

        # Action dropdown
        action_label = QLabel("Action:")
        layout.addWidget(action_label)

        self.action_combo = QComboBox()
        self.action_combo.addItems(["Go to Point", "Lift", "Wait"])
        self.action_combo.currentTextChanged.connect(self.on_action_changed)
        layout.addWidget(self.action_combo)

        # Lift parameters
        self.lift_widget = QWidget()
        lift_layout = QHBoxLayout(self.lift_widget)
        lift_label = QLabel("Lift Direction:")
        lift_layout.addWidget(lift_label)
        self.lift_group = QButtonGroup()
        lift_up = QRadioButton("Up")
        lift_down = QRadioButton("Down")
        lift_up.setChecked(True)
        self.lift_group.addButton(lift_up, 0)
        self.lift_group.addButton(lift_down, 1)
        lift_layout.addWidget(lift_up)
        lift_layout.addWidget(lift_down)
        self.lift_widget.setVisible(False)
        layout.addWidget(self.lift_widget)

        # Wait parameters
        self.wait_widget = QWidget()
        wait_layout = QVBoxLayout(self.wait_widget)
        self.wait_label = QLabel("Wait Time: 5 seconds")
        wait_layout.addWidget(self.wait_label)
        self.wait_slider = QSlider(Qt.Orientation.Horizontal)
        self.wait_slider.setMinimum(1)
        self.wait_slider.setMaximum(30)
        self.wait_slider.setValue(5)
        self.wait_slider.valueChanged.connect(lambda v: self.wait_label.setText(f"Wait Time: {v} seconds"))
        wait_layout.addWidget(self.wait_slider)
        self.wait_widget.setVisible(False)
        layout.addWidget(self.wait_widget)

        # Execute button
        execute_btn = QPushButton("Execute Task")
        execute_btn.clicked.connect(self.execute_task)
        layout.addWidget(execute_btn)

        # Go back button
        back_btn = QPushButton("Go Back to Standby")
        back_btn.clicked.connect(lambda: self.send_to_standby())
        layout.addWidget(back_btn)

        # Status label
        self.task_status_label = QLabel("")
        self.task_status_label.setStyleSheet("color: green;")
        layout.addWidget(self.task_status_label)

        layout.addStretch()

        return group

    def create_task_builder(self):
        """Create task builder panel"""
        group = QGroupBox("Task Builder")
        layout = QVBoxLayout(group)

        # Task steps list
        steps_label = QLabel("Task Steps:")
        layout.addWidget(steps_label)

        self.steps_list = QListWidget()
        layout.addWidget(self.steps_list)

        # Control buttons
        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_steps)
        btn_layout.addWidget(clear_btn)

        save_btn = QPushButton("Save Task")
        save_btn.clicked.connect(self.save_task)
        btn_layout.addWidget(save_btn)

        load_btn = QPushButton("Load Task")
        load_btn.clicked.connect(self.load_task)
        btn_layout.addWidget(load_btn)

        layout.addLayout(btn_layout)

        return group

    def on_action_changed(self, action):
        """Handle action selection change"""
        self.lift_widget.setVisible(action == "Lift")
        self.wait_widget.setVisible(action == "Wait")

    def on_robot_selection_changed(self):
        """Handle robot selection change"""
        selected_items = self.robot_list.selectedItems()
        robot_ids = [item.text().split()[0] for item in selected_items]
        self.robot_canvas.set_selected_robots(robot_ids)

    def execute_task(self):
        """Execute the selected task"""
        poi = self.poi_combo.currentText()
        action = self.action_combo.currentText()

        selected_robots = [item.text().split()[0] for item in self.robot_list.selectedItems()]

        if not selected_robots:
            QMessageBox.warning(self, "No Robot Selected", "Please select at least one robot.")
            return

        msg = f"Execute {action} for robots: {', '.join(selected_robots)}"
        if action == "Go to Point":
            msg += f" to {poi}"

        self.task_status_label.setText(msg)

    def send_to_standby(self):
        """Send robot to standby point"""
        selected_robots = [item.text().split()[0] for item in self.robot_list.selectedItems()]
        if selected_robots:
            self.task_status_label.setText(f"Sending {', '.join(selected_robots)} to Standby")

    def update_status(self):
        """Update robot status display"""
        robot_id = self.robot_canvas.active_robot
        robot = self.robot_canvas.get_robot_state(robot_id)

        if robot:
            self.status_table.item(0, 1).setText(str(robot.get('x', '-')))
            self.status_table.item(1, 1).setText(str(robot.get('y', '-')))
            self.status_table.item(2, 1).setText(f"{robot.get('heading', 0)}°")
            self.status_table.item(3, 1).setText("Idle")
            self.status_table.item(4, 1).setText("Ready")
            self.status_table.item(5, 1).setText("None")
            self.status_table.item(6, 1).setText("N/A")
            self.status_table.item(7, 1).setText("None")

    def clear_steps(self):
        """Clear all task steps"""
        self.steps_list.clear()

    def save_task(self):
        """Save task to file"""
        QMessageBox.information(self, "Save Task", "Task save functionality would be implemented here")

    def load_task(self):
        """Load task from file"""
        QMessageBox.information(self, "Load Task", "Task load functionality would be implemented here")

        return panel
