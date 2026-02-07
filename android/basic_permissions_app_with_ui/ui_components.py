"""
Reusable UI Components for Permission and Sensor Monitoring

This module provides Kivy widgets for displaying permission status and sensor data
with reactive updates through Kivy properties. All components use consistent styling
and color coding.

Features:
- PermissionWidget: Display permission status with request button
- SensorWidget: Display sensor data with enable/disable toggle
- Color coding: Green (granted/available), Red (denied/unavailable), Gray (unknown)
- Reactive updates through Kivy property binding
- Multi-axis sensor data formatting
- Single-value sensor data formatting
- Consistent styling and layout
"""

import logging
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.graphics import Color, Ellipse, Line
from kivy.properties import BooleanProperty, StringProperty, DictProperty
from kivy.core.window import Window

logger = logging.getLogger(__name__)


class PermissionWidget(BoxLayout):
    """
    Widget for displaying and managing a single permission.

    Displays the permission name, status indicator with color coding,
    and a button to request the permission. Updates reactively when
    permission status changes.

    Layout:
    [indicator] [permission name ........] [request button]

    Attributes:
        permission_type (str): Type of permission (camera, microphone, etc.)
        permission_name (str): Human-readable permission name
        is_granted (BooleanProperty): Whether permission is granted
        on_request_callback (callable): Callback when request button is clicked
    """

    permission_type = StringProperty("")
    permission_name = StringProperty("")
    is_granted = BooleanProperty(False)

    def __init__(self, permission_type: str, permission_name: str, **kwargs):
        """
        Initialize the permission widget.

        Args:
            permission_type (str): Type of permission (camera, microphone, location, storage)
            permission_name (str): Human-readable name to display
            **kwargs: Additional arguments passed to BoxLayout
        """
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 60
        self.padding = 10
        self.spacing = 10

        self.permission_type = permission_type
        self.permission_name = permission_name
        self.on_request_callback = None

        # Status indicator circle
        self.indicator = Label(size_hint_x=0.1, text="")
        self.add_widget(self.indicator)

        # Permission name label
        self.name_label = Label(
            text=permission_name,
            size_hint_x=0.6,
            text_size=(None, None),
            halign="left",
            valign="middle",
        )
        self.add_widget(self.name_label)

        # Status text label
        self.status_label = Label(
            text="Unknown", size_hint_x=0.15, halign="center", valign="middle"
        )
        self.add_widget(self.status_label)

        # Request button
        self.request_button = Button(
            text="Request",
            size_hint_x=0.15,
            background_color=(0.2, 0.6, 1.0, 1),
        )
        self.request_button.bind(on_press=self._on_request_pressed)
        self.add_widget(self.request_button)

        # Bind to is_granted property changes
        self.bind(is_granted=self._update_display)

        # Initial display update
        self._update_display()

        logger.debug(f"PermissionWidget created for {permission_type}")

    def _update_display(self, *args):
        """Update the visual display based on permission status."""
        if self.is_granted:
            # Permission granted - green
            self.indicator.text = ""
            self.status_label.text = "Granted"
            self.status_label.color = (0, 1, 0, 1)  # Green
            self.request_button.disabled = True
            self.request_button.opacity = 0.5
        else:
            # Permission not granted - red
            self.indicator.text = ""
            self.status_label.text = "Denied"
            self.status_label.color = (1, 0, 0, 1)  # Red
            self.request_button.disabled = False
            self.request_button.opacity = 1.0

    def _on_request_pressed(self, instance):
        """Handle request button press."""
        logger.info(f"Permission request button pressed for {self.permission_type}")
        if self.on_request_callback:
            try:
                self.on_request_callback(self.permission_type)
            except Exception as e:
                logger.error(f"Error in permission request callback: {e}")

    def set_request_callback(self, callback):
        """
        Set the callback function for permission request button.

        Args:
            callback (callable): Function to call when request button is pressed
                Should accept permission_type as argument
        """
        self.on_request_callback = callback


class SensorWidget(BoxLayout):
    """
    Widget for displaying and managing a single sensor.

    Displays sensor name, availability status, current readings for multi-axis
    sensors or single values, and an enable/disable toggle. Updates reactively
    when sensor data changes.

    Layout:
    [status] [sensor name] [readings] [enable toggle]

    Attributes:
        sensor_type (str): Type of sensor (accelerometer, gyroscope, etc.)
        sensor_name (str): Human-readable sensor name
        is_available (BooleanProperty): Whether sensor is available
        is_enabled (BooleanProperty): Whether sensor is currently enabled
        sensor_data (DictProperty): Current sensor readings
    """

    sensor_type = StringProperty("")
    sensor_name = StringProperty("")
    is_available = BooleanProperty(False)
    is_enabled = BooleanProperty(False)
    sensor_data = DictProperty({"x": 0.0, "y": 0.0, "z": 0.0, "timestamp": None})

    def __init__(self, sensor_type: str, sensor_name: str, **kwargs):
        """
        Initialize the sensor widget.

        Args:
            sensor_type (str): Type of sensor (accelerometer, gyroscope, etc.)
            sensor_name (str): Human-readable name to display
            **kwargs: Additional arguments passed to BoxLayout
        """
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 80
        self.padding = 10
        self.spacing = 10

        self.sensor_type = sensor_type
        self.sensor_name = sensor_name
        self.on_toggle_callback = None

        # Status indicator
        self.status_label = Label(size_hint_x=0.08, text="")
        self.add_widget(self.status_label)

        # Sensor name
        self.name_label = Label(
            text=sensor_name,
            size_hint_x=0.25,
            text_size=(None, None),
            halign="left",
            valign="middle",
        )
        self.add_widget(self.name_label)

        # Data readings display
        self.data_label = Label(
            text="--",
            size_hint_x=0.45,
            text_size=(None, None),
            halign="left",
            valign="middle",
            font_size="10sp",
        )
        self.add_widget(self.data_label)

        # Enable/disable toggle
        self.toggle_button = ToggleButton(
            text="OFF",
            size_hint_x=0.12,
            background_color=(1, 0, 0, 1),
        )
        self.toggle_button.bind(state=self._on_toggle_state)
        self.add_widget(self.toggle_button)

        # Bind properties to update handlers
        self.bind(is_available=self._update_availability_display)
        self.bind(is_enabled=self._update_enabled_display)
        self.bind(sensor_data=self._update_data_display)

        # Initial display
        self._update_availability_display()
        self._update_data_display()

        logger.debug(f"SensorWidget created for {sensor_type}")

    def _update_availability_display(self, *args):
        """Update display based on sensor availability."""
        if self.is_available:
            self.status_label.text = "●"
            self.status_label.color = (0, 1, 0, 1)  # Green
            self.toggle_button.disabled = False
            self.toggle_button.opacity = 1.0
        else:
            self.status_label.text = "●"
            self.status_label.color = (0.5, 0.5, 0.5, 1)  # Gray
            self.toggle_button.disabled = True
            self.toggle_button.opacity = 0.5

    def _update_enabled_display(self, *args):
        """Update toggle button display based on enabled state."""
        if self.is_enabled:
            self.toggle_button.state = "down"
            self.toggle_button.text = "ON"
            self.toggle_button.background_color = (0, 1, 0, 1)  # Green
        else:
            self.toggle_button.state = "normal"
            self.toggle_button.text = "OFF"
            self.toggle_button.background_color = (1, 0, 0, 1)  # Red

    def _update_data_display(self, *args):
        """Update data display based on current sensor readings."""
        try:
            data = self.sensor_data
            if not data or not self.is_available:
                self.data_label.text = "--"
                return

            # Format based on sensor type
            if "x" in data and "y" in data and "z" in data:
                # Multi-axis sensor (accelerometer, gyroscope, magnetometer)
                x = data.get("x", 0.0)
                y = data.get("y", 0.0)
                z = data.get("z", 0.0)
                self.data_label.text = f"X:{x:.2f} Y:{y:.2f} Z:{z:.2f}"
            elif "value" in data:
                # Single-value sensor (light, proximity)
                value = data.get("value", 0.0)
                self.data_label.text = f"Value: {value:.1f}"
            else:
                self.data_label.text = "--"
        except Exception as e:
            logger.error(f"Error updating sensor data display: {e}")
            self.data_label.text = "Error"

    def _on_toggle_state(self, instance, value):
        """Handle toggle button state change."""
        logger.info(f"Sensor {self.sensor_type} toggle: {value}")
        if self.on_toggle_callback:
            try:
                # Convert toggle state to boolean
                enabled = value == "down"
                self.on_toggle_callback(self.sensor_type, enabled)
            except Exception as e:
                logger.error(f"Error in sensor toggle callback: {e}")

    def set_toggle_callback(self, callback):
        """
        Set the callback function for sensor toggle button.

        Args:
            callback (callable): Function to call when toggle state changes
                Should accept (sensor_type, enabled) as arguments
        """
        self.on_toggle_callback = callback

    def set_sensor_data(self, data: dict):
        """
        Update the sensor data display.

        Args:
            data (dict): Dictionary containing sensor readings
                For multi-axis: {'x': float, 'y': float, 'z': float, 'timestamp': str}
                For single-value: {'value': float, 'timestamp': str}
        """
        self.sensor_data = data


class PermissionsPanel(GridLayout):
    """
    Container widget for displaying multiple permissions.

    Creates a PermissionWidget for each permission type and manages
    the collection of permission status displays.

    Attributes:
        permissions_widgets (dict): Dictionary mapping permission types to their widgets
        on_request_callback (callable): Callback for all permission requests
    """

    def __init__(self, permission_types: list, permission_names: dict, **kwargs):
        """
        Initialize the permissions panel.

        Args:
            permission_types (list): List of permission types to display
            permission_names (dict): Dictionary mapping permission types to display names
            **kwargs: Additional arguments passed to GridLayout
        """
        super().__init__(**kwargs)
        self.cols = 1
        self.spacing = 5
        self.size_hint_y = None
        self.height = len(permission_types) * 70

        self.permissions_widgets = {}
        self.on_request_callback = None

        for perm_type in permission_types:
            perm_name = permission_names.get(perm_type, perm_type.capitalize())
            widget = PermissionWidget(perm_type, perm_name)
            widget.set_request_callback(self._on_permission_request)
            self.permissions_widgets[perm_type] = widget
            self.add_widget(widget)

        logger.debug(f"PermissionsPanel created with {len(permission_types)} permissions")

    def _on_permission_request(self, permission_type: str):
        """Handle permission request from any widget."""
        if self.on_request_callback:
            try:
                self.on_request_callback(permission_type)
            except Exception as e:
                logger.error(f"Error in panel request callback: {e}")

    def set_request_callback(self, callback):
        """
        Set the callback for all permission requests.

        Args:
            callback (callable): Function to call when any permission is requested
        """
        self.on_request_callback = callback

    def update_permission_status(self, permission_type: str, is_granted: bool):
        """
        Update the status of a specific permission widget.

        Args:
            permission_type (str): Type of permission to update
            is_granted (bool): Whether the permission is granted
        """
        if permission_type in self.permissions_widgets:
            self.permissions_widgets[permission_type].is_granted = is_granted


class SensorsPanel(GridLayout):
    """
    Container widget for displaying multiple sensors.

    Creates a SensorWidget for each sensor type and manages the collection
    of sensor status and data displays.

    Attributes:
        sensor_widgets (dict): Dictionary mapping sensor types to their widgets
        on_toggle_callback (callable): Callback for all sensor toggles
    """

    def __init__(self, sensor_types: list, sensor_names: dict, **kwargs):
        """
        Initialize the sensors panel.

        Args:
            sensor_types (list): List of sensor types to display
            sensor_names (dict): Dictionary mapping sensor types to display names
            **kwargs: Additional arguments passed to GridLayout
        """
        super().__init__(**kwargs)
        self.cols = 1
        self.spacing = 5
        self.size_hint_y = None
        self.height = len(sensor_types) * 90

        self.sensor_widgets = {}
        self.on_toggle_callback = None

        for sensor_type in sensor_types:
            sensor_name = sensor_names.get(sensor_type, sensor_type.capitalize())
            widget = SensorWidget(sensor_type, sensor_name)
            widget.set_toggle_callback(self._on_sensor_toggle)
            self.sensor_widgets[sensor_type] = widget
            self.add_widget(widget)

        logger.debug(f"SensorsPanel created with {len(sensor_types)} sensors")

    def _on_sensor_toggle(self, sensor_type: str, enabled: bool):
        """Handle sensor toggle from any widget."""
        if self.on_toggle_callback:
            try:
                self.on_toggle_callback(sensor_type, enabled)
            except Exception as e:
                logger.error(f"Error in panel toggle callback: {e}")

    def set_toggle_callback(self, callback):
        """
        Set the callback for all sensor toggles.

        Args:
            callback (callable): Function to call when any sensor is toggled
        """
        self.on_toggle_callback = callback

    def update_sensor_status(
        self, sensor_type: str, is_available: bool, is_enabled: bool
    ):
        """
        Update the status of a specific sensor widget.

        Args:
            sensor_type (str): Type of sensor to update
            is_available (bool): Whether the sensor is available
            is_enabled (bool): Whether the sensor is currently enabled
        """
        if sensor_type in self.sensor_widgets:
            widget = self.sensor_widgets[sensor_type]
            widget.is_available = is_available
            widget.is_enabled = is_enabled

    def update_sensor_data(self, sensor_type: str, data: dict):
        """
        Update the sensor data display for a specific sensor.

        Args:
            sensor_type (str): Type of sensor to update
            data (dict): Sensor data dictionary
        """
        if sensor_type in self.sensor_widgets:
            self.sensor_widgets[sensor_type].set_sensor_data(data)
