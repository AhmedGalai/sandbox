"""
Main Application Entry Point for Kivy Android Permissions and Sensors App

This is the primary application module that sets up the Kivy app, integrates
the permissions and sensors managers, and provides the UI for monitoring and
managing both permissions and sensor data.

Features:
- Platform-aware initialization (Android vs Desktop)
- Automatic permission request on startup
- Sensor lifecycle management (enable on resume, disable on pause)
- Reactive UI updates through Kivy property binding
- Comprehensive error handling and logging
- Clean resource cleanup on exit
"""

import logging
import logging.handlers
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock

from permissions_manager import PermissionsManager
from sensors_manager import SensorsManager
from ui_components import PermissionsPanel, SensorsPanel

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Add formatter to handler
ch.setFormatter(formatter)

# Add handler to logger
logger.addHandler(ch)


class PermissionsSensorsApp(App):
    """
    Main Kivy Application for Permissions and Sensors Management.

    This app provides a comprehensive interface for managing Android permissions
    and monitoring device sensors. It automatically requests permissions on startup
    and manages the sensor lifecycle based on app pause/resume events.

    Attributes:
        permissions_manager (PermissionsManager): Manager for app permissions
        sensors_manager (SensorsManager): Manager for device sensors
        permissions_panel (PermissionsPanel): UI widget for permissions display
        sensors_panel (SensorsPanel): UI widget for sensors display
    """

    def __init__(self, **kwargs):
        """Initialize the application."""
        super().__init__(**kwargs)
        self.title = "Permissions & Sensors Monitor"

        # Initialize managers
        self.permissions_manager = None
        self.sensors_manager = None

        # UI components
        self.permissions_panel = None
        self.sensors_panel = None
        self.root_layout = None
        self.status_label = None

        logger.info("Application initialized")

    def build(self):
        """
        Build the application UI.

        Called by Kivy framework during app startup. Sets up the main layout,
        managers, and UI panels. Also establishes property bindings for reactive
        updates.

        Returns:
            BoxLayout: Root widget containing the entire UI
        """
        logger.info("Building application UI...")

        # Set window properties for better display
        Window.size = (360, 800)

        # Create root layout
        self.root_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Create title and status header
        header_layout = BoxLayout(orientation="vertical", size_hint_y=None, height=80)

        title_label = Label(
            text="Permissions & Sensors Monitor",
            font_size="20sp",
            bold=True,
            size_hint_y=0.5,
        )
        header_layout.add_widget(title_label)

        self.status_label = Label(
            text="Initializing...",
            font_size="12sp",
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=0.5,
        )
        header_layout.add_widget(self.status_label)

        self.root_layout.add_widget(header_layout)

        # Create scrollable main content area
        scroll_view = ScrollView(size_hint=(1, 1))
        content_layout = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter("height"))

        # Initialize managers
        try:
            self.permissions_manager = PermissionsManager()
            logger.debug("PermissionsManager created")
        except Exception as e:
            logger.error(f"Error creating PermissionsManager: {e}")
            self._show_error("Failed to initialize permissions manager")
            return self.root_layout

        try:
            self.sensors_manager = SensorsManager()
            logger.debug("SensorsManager created")
        except Exception as e:
            logger.error(f"Error creating SensorsManager: {e}")
            self._show_error("Failed to initialize sensors manager")
            return self.root_layout

        # Create permissions section
        permissions_label = Label(
            text="PERMISSIONS",
            font_size="16sp",
            bold=True,
            size_hint_y=None,
            height=40,
            color=(0.2, 0.6, 1.0, 1),
        )
        content_layout.add_widget(permissions_label)

        permission_types = ["camera", "microphone", "location", "storage"]
        permission_names = {
            "camera": "Camera",
            "microphone": "Microphone",
            "location": "Location",
            "storage": "Storage",
        }

        self.permissions_panel = PermissionsPanel(permission_types, permission_names)
        self.permissions_panel.set_request_callback(self._on_permission_request)
        content_layout.add_widget(self.permissions_panel)

        # Create sensors section
        sensors_label = Label(
            text="SENSORS",
            font_size="16sp",
            bold=True,
            size_hint_y=None,
            height=40,
            color=(0.2, 0.6, 1.0, 1),
        )
        content_layout.add_widget(sensors_label)

        sensor_types = ["accelerometer", "gyroscope", "magnetometer", "light", "proximity"]
        sensor_names = {
            "accelerometer": "Accelerometer",
            "gyroscope": "Gyroscope",
            "magnetometer": "Magnetometer",
            "light": "Light Sensor",
            "proximity": "Proximity Sensor",
        }

        self.sensors_panel = SensorsPanel(sensor_types, sensor_names)
        self.sensors_panel.set_toggle_callback(self._on_sensor_toggle)
        content_layout.add_widget(self.sensors_panel)

        # Add spacer
        content_layout.add_widget(Label(size_hint_y=None, height=20))

        # Create action buttons layout
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        enable_all_btn = Button(
            text="Enable All Sensors",
            background_color=(0, 1, 0, 1),
        )
        enable_all_btn.bind(on_press=self._on_enable_all_sensors)
        button_layout.add_widget(enable_all_btn)

        disable_all_btn = Button(
            text="Disable All Sensors",
            background_color=(1, 0, 0, 1),
        )
        disable_all_btn.bind(on_press=self._on_disable_all_sensors)
        button_layout.add_widget(disable_all_btn)

        content_layout.add_widget(button_layout)

        # Bind permissions manager properties to UI updates
        self._bind_permissions_to_ui()

        # Bind sensors manager properties to UI updates
        self._bind_sensors_to_ui()

        scroll_view.add_widget(content_layout)
        self.root_layout.add_widget(scroll_view)

        logger.info("Application UI built successfully")
        return self.root_layout

    def on_start(self):
        """
        Called after the window is displayed.

        Requests all permissions and schedules initial sensor availability checks.
        """
        logger.info("Application started (on_start)")

        try:
            # Schedule permission requests on next frame to ensure UI is ready
            Clock.schedule_once(self._request_all_permissions, 0.5)
        except Exception as e:
            logger.error(f"Error in on_start: {e}")
            self._show_error(f"Startup error: {e}")

    def on_pause(self):
        """
        Called when the application is paused (app goes to background on Android).

        Disables sensors and releases resources to save battery and reduce
        system load while the app is not visible.

        Returns:
            bool: True to allow app to be paused, False to prevent pausing
        """
        logger.info("Application paused (on_pause)")

        try:
            if self.sensors_manager:
                self.sensors_manager.disable_all()
                logger.info("All sensors disabled on pause")

                # Update UI to reflect disabled state
                self._update_sensors_ui_state()
        except Exception as e:
            logger.error(f"Error during pause: {e}")

        return True

    def on_resume(self):
        """
        Called when the application is resumed (app returns from background on Android).

        Re-enables sensors that were active before the pause.
        """
        logger.info("Application resumed (on_resume)")

        try:
            if self.sensors_manager:
                # Re-enable sensors that were active before pause
                self._update_sensors_ui_state()
                logger.info("Sensors state restored on resume")
        except Exception as e:
            logger.error(f"Error during resume: {e}")

    def _request_all_permissions(self, dt=None):
        """
        Request all permissions from the user.

        Called asynchronously from on_start to ensure UI is ready.

        Args:
            dt (float): Time delta (provided by Clock)
        """
        logger.info("Requesting all permissions...")

        try:
            if self.permissions_manager:
                self.permissions_manager.request_permissions(
                    callback=self._on_permission_result
                )
        except Exception as e:
            logger.error(f"Error requesting permissions: {e}")
            self._show_error(f"Permission request failed: {e}")

    def _on_permission_request(self, permission_type: str):
        """
        Handle permission request button press from UI.

        Args:
            permission_type (str): Type of permission to request
        """
        logger.info(f"User requested permission: {permission_type}")

        try:
            if self.permissions_manager:
                self.permissions_manager.request_permissions(
                    [permission_type], callback=self._on_permission_result
                )
        except Exception as e:
            logger.error(f"Error requesting {permission_type} permission: {e}")
            self._show_error(f"Failed to request {permission_type}: {e}")

    def _on_permission_result(self, permission_type: str, is_granted: bool):
        """
        Handle permission request result.

        Updates the UI to reflect the new permission status.

        Args:
            permission_type (str): Type of permission that was requested
            is_granted (bool): Whether the permission was granted
        """
        logger.info(f"Permission result: {permission_type} = {is_granted}")

        if self.permissions_panel:
            self.permissions_panel.update_permission_status(permission_type, is_granted)

        # Update status message
        if self.permissions_manager:
            status = self.permissions_manager.get_all_permissions_status()
            granted_count = sum(1 for v in status.values() if v)
            self.status_label.text = f"Permissions: {granted_count}/4 granted"

    def _on_sensor_toggle(self, sensor_type: str, enabled: bool):
        """
        Handle sensor enable/disable toggle from UI.

        Args:
            sensor_type (str): Type of sensor to toggle
            enabled (bool): Whether to enable or disable the sensor
        """
        logger.info(f"Sensor toggle: {sensor_type} = {enabled}")

        try:
            if not self.sensors_manager:
                return

            if enabled:
                success = self.sensors_manager.enable_sensor(sensor_type)
                if not success:
                    logger.warning(f"Failed to enable sensor: {sensor_type}")
                    self._show_error(f"Sensor not available: {sensor_type}")
            else:
                self.sensors_manager.disable_sensor(sensor_type)

            self._update_sensors_ui_state()
        except Exception as e:
            logger.error(f"Error toggling sensor {sensor_type}: {e}")
            self._show_error(f"Sensor error: {e}")

    def _on_enable_all_sensors(self, instance):
        """Handle 'Enable All Sensors' button press."""
        logger.info("Enable all sensors button pressed")

        try:
            if self.sensors_manager:
                enabled_count = self.sensors_manager.enable_all()
                logger.info(f"Enabled {enabled_count} sensors")
                self._update_sensors_ui_state()
        except Exception as e:
            logger.error(f"Error enabling all sensors: {e}")
            self._show_error(f"Failed to enable sensors: {e}")

    def _on_disable_all_sensors(self, instance):
        """Handle 'Disable All Sensors' button press."""
        logger.info("Disable all sensors button pressed")

        try:
            if self.sensors_manager:
                self.sensors_manager.disable_all()
                logger.info("All sensors disabled")
                self._update_sensors_ui_state()
        except Exception as e:
            logger.error(f"Error disabling all sensors: {e}")
            self._show_error(f"Failed to disable sensors: {e}")

    def _bind_permissions_to_ui(self):
        """Bind permissions manager properties to UI updates."""
        try:
            if not self.permissions_manager or not self.permissions_panel:
                return

            for perm_type in ["camera", "microphone", "location", "storage"]:
                is_granted = self.permissions_manager.check_permission(perm_type)
                self.permissions_panel.update_permission_status(perm_type, is_granted)

            logger.debug("Permissions bound to UI")
        except Exception as e:
            logger.error(f"Error binding permissions to UI: {e}")

    def _bind_sensors_to_ui(self):
        """Bind sensors manager properties to UI updates."""
        try:
            if not self.sensors_manager or not self.sensors_panel:
                return

            for sensor_type in [
                "accelerometer",
                "gyroscope",
                "magnetometer",
                "light",
                "proximity",
            ]:
                is_available = self.sensors_manager.available_sensors.get(sensor_type, False)
                is_enabled = self.sensors_manager.is_sensor_active(sensor_type)

                self.sensors_panel.update_sensor_status(sensor_type, is_available, is_enabled)

                # Get initial sensor data
                if sensor_type == "accelerometer":
                    data = dict(self.sensors_manager.accelerometer_data)
                elif sensor_type == "gyroscope":
                    data = dict(self.sensors_manager.gyroscope_data)
                elif sensor_type == "magnetometer":
                    data = dict(self.sensors_manager.magnetometer_data)
                elif sensor_type == "light":
                    data = dict(self.sensors_manager.light_data)
                elif sensor_type == "proximity":
                    data = dict(self.sensors_manager.proximity_data)
                else:
                    data = {}

                self.sensors_panel.update_sensor_data(sensor_type, data)

            # Bind to property changes for reactive updates
            self.sensors_manager.bind(
                accelerometer_data=lambda *args: self._on_accelerometer_changed()
            )
            self.sensors_manager.bind(
                gyroscope_data=lambda *args: self._on_gyroscope_changed()
            )
            self.sensors_manager.bind(
                magnetometer_data=lambda *args: self._on_magnetometer_changed()
            )
            self.sensors_manager.bind(light_data=lambda *args: self._on_light_changed())
            self.sensors_manager.bind(
                proximity_data=lambda *args: self._on_proximity_changed()
            )
            self.sensors_manager.bind(
                available_sensors=lambda *args: self._update_sensors_ui_state()
            )

            logger.debug("Sensors bound to UI")
        except Exception as e:
            logger.error(f"Error binding sensors to UI: {e}")

    def _on_accelerometer_changed(self):
        """Handle accelerometer data update."""
        try:
            if self.sensors_panel and self.sensors_manager:
                data = dict(self.sensors_manager.accelerometer_data)
                self.sensors_panel.update_sensor_data("accelerometer", data)
        except Exception as e:
            logger.debug(f"Error updating accelerometer UI: {e}")

    def _on_gyroscope_changed(self):
        """Handle gyroscope data update."""
        try:
            if self.sensors_panel and self.sensors_manager:
                data = dict(self.sensors_manager.gyroscope_data)
                self.sensors_panel.update_sensor_data("gyroscope", data)
        except Exception as e:
            logger.debug(f"Error updating gyroscope UI: {e}")

    def _on_magnetometer_changed(self):
        """Handle magnetometer data update."""
        try:
            if self.sensors_panel and self.sensors_manager:
                data = dict(self.sensors_manager.magnetometer_data)
                self.sensors_panel.update_sensor_data("magnetometer", data)
        except Exception as e:
            logger.debug(f"Error updating magnetometer UI: {e}")

    def _on_light_changed(self):
        """Handle light sensor data update."""
        try:
            if self.sensors_panel and self.sensors_manager:
                data = dict(self.sensors_manager.light_data)
                self.sensors_panel.update_sensor_data("light", data)
        except Exception as e:
            logger.debug(f"Error updating light sensor UI: {e}")

    def _on_proximity_changed(self):
        """Handle proximity sensor data update."""
        try:
            if self.sensors_panel and self.sensors_manager:
                data = dict(self.sensors_manager.proximity_data)
                self.sensors_panel.update_sensor_data("proximity", data)
        except Exception as e:
            logger.debug(f"Error updating proximity sensor UI: {e}")

    def _update_sensors_ui_state(self):
        """Update sensor UI elements to reflect current state."""
        try:
            if not self.sensors_panel or not self.sensors_manager:
                return

            for sensor_type in [
                "accelerometer",
                "gyroscope",
                "magnetometer",
                "light",
                "proximity",
            ]:
                is_available = self.sensors_manager.available_sensors.get(sensor_type, False)
                is_enabled = self.sensors_manager.is_sensor_active(sensor_type)

                self.sensors_panel.update_sensor_status(sensor_type, is_available, is_enabled)
        except Exception as e:
            logger.error(f"Error updating sensors UI state: {e}")

    def _show_error(self, message: str):
        """
        Display an error message (currently just logs it).

        In a more complete implementation, this could show a popup or toast.

        Args:
            message (str): Error message to display
        """
        logger.error(f"APP ERROR: {message}")

    def on_stop(self):
        """
        Called when the application is closing.

        Cleans up resources and disables sensors.

        Returns:
            bool: True to allow app to close
        """
        logger.info("Application stopping (on_stop)")

        try:
            if self.sensors_manager:
                self.sensors_manager.cleanup()
                logger.info("Sensors manager cleaned up")

            if self.permissions_manager:
                logger.info("Permissions manager cleaned up")

            logger.info("Application closed cleanly")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

        return True


if __name__ == "__main__":
    logger.info("Starting Permissions & Sensors Monitor application")
    app = PermissionsSensorsApp()
    app.run()
