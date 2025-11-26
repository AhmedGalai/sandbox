"""
Robot simulator canvas widget using QPainter
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF
import math


class RobotCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 600)

        # Grid settings
        self.grid_size = 20
        self.cell_size = 30

        # Robot states (multi-robot support)
        self.robots = {
            'ROB-001': {'x': 5, 'y': 5, 'heading': 0, 'color': QColor('#F51A61'), 'path': []},
            'ROB-002': {'x': 12, 'y': 8, 'heading': 90, 'color': QColor('#2196F3'), 'path': []},
            'ROB-003': {'x': 2, 'y': 18, 'heading': 0, 'color': QColor('#4CAF50'), 'path': []},
            'ROB-004': {'x': 15, 'y': 15, 'heading': 180, 'color': QColor('#FF9800'), 'path': []},
            'ROB-005': {'x': 10, 'y': 5, 'heading': 270, 'color': QColor('#9C27B0'), 'path': []}
        }

        self.selected_robots = ['ROB-001']
        self.active_robot = 'ROB-001'

        # Obstacles (gray cells)
        self.obstacles = [
            # Top wall
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
            # Left wall
            (0, 1), (0, 2), (0, 3), (0, 4),
            # Right wall section
            (19, 5), (19, 6), (19, 7), (19, 8),
            # Bottom wall section
            (15, 19), (16, 19), (17, 19), (18, 19), (19, 19),
            # Interior obstacles
            (10, 10), (11, 10), (12, 10), (13, 10),
            (10, 11), (13, 11),
            (10, 12), (11, 12), (12, 12), (13, 12),
            (15, 5), (15, 6), (15, 7), (16, 6),
            (3, 15), (4, 15), (5, 15), (6, 15),
            (4, 16), (5, 16),
            # More scattered obstacles
            (8, 5), (9, 5),
            (18, 10), (18, 11),
            (6, 8), (7, 8)
        ]

        # Work points (green cells with labels)
        self.work_points = [
            {'x': 18, 'y': 3, 'label': 'A', 'color': QColor('#4CAF50')},
            {'x': 7, 'y': 12, 'label': 'B', 'color': QColor('#4CAF50')},
            {'x': 16, 'y': 16, 'label': 'C', 'color': QColor('#4CAF50')}
        ]

        # Charging point (yellow)
        self.charging_point = {'x': 2, 'y': 18, 'label': '⚡', 'color': QColor('#FFC107')}

        # Standby point (blue)
        self.standby_point = {'x': 1, 'y': 1, 'label': 'S', 'color': QColor('#2196F3')}

    def paintEvent(self, event):
        """Paint the robot map"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw grid
        self.draw_grid(painter)

        # Draw obstacles
        self.draw_obstacles(painter)

        # Draw work points
        self.draw_work_points(painter)

        # Draw charging and standby points
        self.draw_special_points(painter)

        # Draw paths for selected robots
        for robot_id in self.selected_robots:
            if robot_id in self.robots:
                self.draw_path(painter, self.robots[robot_id])

        # Draw robots
        for robot_id in self.selected_robots:
            if robot_id in self.robots:
                self.draw_robot(painter, self.robots[robot_id], robot_id)

    def draw_grid(self, painter):
        """Draw the grid lines"""
        pen = QPen(QColor('#ddd'), 1)
        painter.setPen(pen)

        for i in range(self.grid_size + 1):
            # Vertical lines
            x = i * self.cell_size
            painter.drawLine(x, 0, x, self.grid_size * self.cell_size)

            # Horizontal lines
            y = i * self.cell_size
            painter.drawLine(0, y, self.grid_size * self.cell_size, y)

    def draw_obstacles(self, painter):
        """Draw obstacles"""
        brush = QBrush(QColor('#888'))
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)

        for obs_x, obs_y in self.obstacles:
            painter.drawRect(obs_x * self.cell_size, obs_y * self.cell_size,
                           self.cell_size, self.cell_size)

    def draw_work_points(self, painter):
        """Draw work points"""
        for wp in self.work_points:
            # Draw colored cell
            brush = QBrush(wp['color'])
            painter.setBrush(brush)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(wp['x'] * self.cell_size, wp['y'] * self.cell_size,
                           self.cell_size, self.cell_size)

            # Draw label
            painter.setPen(QPen(QColor('white')))
            font = QFont('Arial', 16, QFont.Weight.Bold)
            painter.setFont(font)
            center_x = wp['x'] * self.cell_size + self.cell_size // 2
            center_y = wp['y'] * self.cell_size + self.cell_size // 2
            painter.drawText(center_x - 8, center_y + 8, wp['label'])

    def draw_special_points(self, painter):
        """Draw charging and standby points"""
        # Charging point
        brush = QBrush(self.charging_point['color'])
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.charging_point['x'] * self.cell_size,
                        self.charging_point['y'] * self.cell_size,
                        self.cell_size, self.cell_size)

        painter.setPen(QPen(QColor('#333')))
        font = QFont('Arial', 12, QFont.Weight.Bold)
        painter.setFont(font)
        center_x = self.charging_point['x'] * self.cell_size + self.cell_size // 2
        center_y = self.charging_point['y'] * self.cell_size + self.cell_size // 2
        painter.drawText(center_x - 6, center_y + 6, self.charging_point['label'])

        # Standby point
        brush = QBrush(self.standby_point['color'])
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.standby_point['x'] * self.cell_size,
                        self.standby_point['y'] * self.cell_size,
                        self.cell_size, self.cell_size)

        painter.setPen(QPen(QColor('white')))
        font = QFont('Arial', 12, QFont.Weight.Bold)
        painter.setFont(font)
        center_x = self.standby_point['x'] * self.cell_size + self.cell_size // 2
        center_y = self.standby_point['y'] * self.cell_size + self.cell_size // 2
        painter.drawText(center_x - 4, center_y + 6, self.standby_point['label'])

    def draw_path(self, painter, robot):
        """Draw robot's path"""
        if not robot.get('path'):
            return

        pen = QPen(robot['color'], 3, Qt.PenStyle.DashLine)
        painter.setPen(pen)

        path = robot['path']
        for i in range(len(path) - 1):
            x1 = path[i]['x'] * self.cell_size + self.cell_size // 2
            y1 = path[i]['y'] * self.cell_size + self.cell_size // 2
            x2 = path[i + 1]['x'] * self.cell_size + self.cell_size // 2
            y2 = path[i + 1]['y'] * self.cell_size + self.cell_size // 2
            painter.drawLine(x1, y1, x2, y2)

    def draw_robot(self, painter, robot, robot_id):
        """Draw a robot"""
        center_x = robot['x'] * self.cell_size + self.cell_size // 2
        center_y = robot['y'] * self.cell_size + self.cell_size // 2
        radius = self.cell_size * 0.4

        # Draw robot body
        brush = QBrush(robot['color'])
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)

        # Draw robot ID
        painter.setPen(QPen(QColor('white')))
        font = QFont('Arial', 10, QFont.Weight.Bold)
        painter.setFont(font)
        robot_num = robot_id.split('-')[1]
        painter.drawText(center_x - 10, center_y + 5, robot_num)

        # Draw direction arrow
        heading_rad = math.radians(robot['heading'] - 90)
        arrow_length = radius
        arrow_end_x = center_x + math.cos(heading_rad) * arrow_length
        arrow_end_y = center_y + math.sin(heading_rad) * arrow_length

        pen = QPen(QColor('white'), 2)
        painter.setPen(pen)
        painter.drawLine(int(center_x), int(center_y), int(arrow_end_x), int(arrow_end_y))

        # Draw arrow head
        arrow_head_size = 6
        angle1 = heading_rad + math.pi * 0.8
        angle2 = heading_rad - math.pi * 0.8

        points = [
            QPointF(arrow_end_x, arrow_end_y),
            QPointF(arrow_end_x + math.cos(angle1) * arrow_head_size,
                   arrow_end_y + math.sin(angle1) * arrow_head_size),
            QPointF(arrow_end_x + math.cos(angle2) * arrow_head_size,
                   arrow_end_y + math.sin(angle2) * arrow_head_size)
        ]

        brush = QBrush(QColor('white'))
        painter.setBrush(brush)
        painter.drawPolygon(QPolygonF(points))

    def update_robot_pose(self, robot_id, x, y, heading):
        """Update robot pose"""
        if robot_id in self.robots:
            self.robots[robot_id]['x'] = x
            self.robots[robot_id]['y'] = y
            self.robots[robot_id]['heading'] = heading
            self.update()

    def set_robot_path(self, robot_id, path):
        """Set robot's path"""
        if robot_id in self.robots:
            self.robots[robot_id]['path'] = path
            self.update()

    def set_selected_robots(self, robot_ids):
        """Set which robots to display"""
        self.selected_robots = robot_ids
        self.update()

    def get_robot_state(self, robot_id):
        """Get robot state"""
        return self.robots.get(robot_id, {})

    def get_work_points(self):
        """Get all work points"""
        return self.work_points

    def get_obstacles(self):
        """Get all obstacles"""
        return self.obstacles

    def get_charging_point(self):
        """Get charging point"""
        return self.charging_point

    def get_standby_point(self):
        """Get standby point"""
        return self.standby_point
