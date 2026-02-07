"""
Sensor Management Module for Kivy Android Applications

This module provides unified access to device sensors including accelerometer,
gyroscope, magnetometer, light, and proximity sensors. It handles platform-specific
differences between Android and desktop environments.

Features:
- Multi-axis sensor support (accelerometer, gyroscope, magnetometer)
- Single-value sensor support (light, proximity)
- Platform detection (Android vs Desktop)
- Periodic sensor data updates via Kivy Clock
- Mock data generation for desktop testing
- Reactive Kivy properties for UI updates
- Graceful error handling for unavailable sensors
"""

import logging
from datetime import datetime
from kivy.properties import DictProperty, BooleanProperty, StringProperty
from kivy.clock import Clock

logger = logging.getLogger(__name__)

# Platform detection and sensor imports
try:
    from plyer import accelerometer, gyroscope, magnetometer, light, proximity
    PLATFORM = "android"
    logger.info("Running on Android platform with sensor support")
except (ImportError, NotImplementedError) as e:
    PLATFORM = "desktop"
    logger.info(f"Running on desktop platform (mock mode): {e}")
    # We'll create mock objects below


class SensorsManager:
    """
    Manages device sensors with support for both Android and desktop platforms.

    Provides reactive access to sensor data through Kivy properties. On desktop,
    generates mock sensor data for testing purposes.

    Attributes:
        accelerometer_data: DictProperty - Accelerometer (x, y, z) values
        gyroscope_data: DictProperty - Gyroscope (x, y, z) values
        magnetometer_data: DictProperty - Magnetometer (x, y, z) values
        light_data: DictProperty - Light sensor value
        proximity_data: DictProperty - Proximity sensor value
        available_sensors: DictProperty - Status of available sensors
        is_enabled: BooleanProperty - Overall sensor state
        status_message: StringProperty - Human-readable status message
    """

    # Sensor data properties
    accelerometer_data = DictProperty({"x": 0.0, "y": 0.0, "z": 0.0, "timestamp": None})
    gyroscope_data = DictProperty({"x": 0.0, "y": 0.0, "z": 0.0, "timestamp": None})
    magnetometer_data = DictProperty({"x": 0.0, "y": 0.0, "z": 0.0, "timestamp": None})
    light_data = DictProperty({"value": 0.0, "timestamp": None})
    proximity_data = DictProperty({"value": 0.0, "timestamp": None})

    # Status properties
    available_sensors = DictProperty(
        {
            "accelerometer": False,
            "gyroscope": False,
            "magnetometer": False,
            "light": False,
            "proximity": False,
        }
    )
    is_enabled = BooleanProperty(False)
    status_message = StringProperty("Ready to enable sensors")

    # Sensor list
    SENSOR_TYPES = ["accelerometer", "gyroscope", "magnetometer", "light", "proximity"]

    def __init__(self):
        """Initialize the sensors manager."""
        self.platform = PLATFORM
        self._active_sensors = set()
        self._update_clock = None
        self._mock_data_counters = {}

        logger.debug(f"SensorsManager initialized on {self.platform}")

        # Detect available sensors
        self.detect_available_sensors()

    def detect_available_sensors(self):
        """
        Detect which sensors are available on the device.

        Updates the available_sensors property based on platform and hardware.
        """
        logger.info("Detecting available sensors...")

        if self.platform == "android":
            self._detect_android_sensors()
        else:
            self._detect_desktop_sensors()

        # Log detected sensors
        available = [s for s, v in self.available_sensors.items() if v]
        logger.info(f"Available sensors: {available}")
        self._update_status_message()

    def _detect_android_sensors(self):
        """Detect sensors available on Android platform."""
        sensors_status = {}

        for sensor_type in self.SENSOR_TYPES:
            try:
                if sensor_type == "accelerometer":
                    # Try to read accelerometer to verify availability
                    data = accelerometer.acceleration
                    sensors_status[sensor_type] = data is not None
                elif sensor_type == "gyroscope":
                    data = gyroscope.rotation
                    sensors_status[sensor_type] = data is not None
                elif sensor_type == "magnetometer":
                    data = magnetometer.magnetic_field
                    sensors_status[sensor_type] = data is not None
                elif sensor_type == "light":
                    data = light.illuminance
                    sensors_status[sensor_type] = data is not None
                elif sensor_type == "proximity":
                    data = proximity.distance
                    sensors_status[sensor_type] = data is not None
                else:
                    sensors_status[sensor_type] = False
            except Exception as e:
                logger.debug(f"Sensor {sensor_type} not available: {e}")
                sensors_status[sensor_type] = False

        self.available_sensors = sensors_status

    def _detect_desktop_sensors(self):
        """Detect sensors in desktop mode (all simulated as available)."""
        # On desktop, simulate all sensors as available
        sensors_status = {sensor: True for sensor in self.SENSOR_TYPES}
        self.available_sensors = sensors_status

        # Initialize mock data counters
        for sensor in self.SENSOR_TYPES:
            self._mock_data_counters[sensor] = 0

    def enable_sensor(self, sensor_type: str) -> bool:
        """
        Enable a specific sensor for data collection.

        Args:
            sensor_type (str): Type of sensor to enable
                ('accelerometer', 'gyroscope', 'magnetometer', 'light', 'proximity')

        Returns:
            bool: True if sensor was enabled, False if unavailable

        Raises:
            ValueError: If sensor_type is not recognized
        """
        if sensor_type not in self.SENSOR_TYPES:
            raise ValueError(f"Unknown sensor type: {sensor_type}")

        if not self.available_sensors.get(sensor_type, False):
            logger.warning(f"Sensor {sensor_type} is not available")
            return False

        if sensor_type in self._active_sensors:
            logger.debug(f"Sensor {sensor_type} is already enabled")
            return True

        self._active_sensors.add(sensor_type)
        logger.info(f"Enabled sensor: {sensor_type}")

        # Start periodic updates if not already running
        if self._update_clock is None:
            self._start_sensor_updates()

        self._update_status_message()
        return True

    def disable_sensor(self, sensor_type: str) -> bool:
        """
        Disable a specific sensor.

        Args:
            sensor_type (str): Type of sensor to disable

        Returns:
            bool: True if sensor was disabled, False if it wasn't active

        Raises:
            ValueError: If sensor_type is not recognized
        """
        if sensor_type not in self.SENSOR_TYPES:
            raise ValueError(f"Unknown sensor type: {sensor_type}")

        if sensor_type not in self._active_sensors:
            logger.debug(f"Sensor {sensor_type} is not currently enabled")
            return False

        self._active_sensors.discard(sensor_type)
        logger.info(f"Disabled sensor: {sensor_type}")

        # Stop updates if no sensors are active
        if not self._active_sensors:
            self._stop_sensor_updates()

        self._update_status_message()
        return True

    def enable_all(self) -> int:
        """
        Enable all available sensors.

        Returns:
            int: Number of sensors enabled
        """
        enabled_count = 0
        for sensor_type in self.SENSOR_TYPES:
            if self.available_sensors.get(sensor_type, False):
                if self.enable_sensor(sensor_type):
                    enabled_count += 1

        logger.info(f"Enabled {enabled_count} sensors")
        return enabled_count

    def disable_all(self):
        """Disable all active sensors."""
        active_sensors = list(self._active_sensors)
        for sensor_type in active_sensors:
            self.disable_sensor(sensor_type)

        logger.info("Disabled all sensors")

    def _start_sensor_updates(self):
        """Start periodic sensor data updates (10Hz = 100ms intervals)."""
        if self._update_clock is not None:
            logger.warning("Sensor updates already running")
            return

        logger.debug("Starting sensor update loop (10Hz)")
        self.is_enabled = True
        self._update_clock = Clock.schedule_interval(self._update_sensor_data, 0.1)

    def _stop_sensor_updates(self):
        """Stop periodic sensor data updates."""
        if self._update_clock is not None:
            logger.debug("Stopping sensor update loop")
            self._update_clock.cancel()
            self._update_clock = None

        self.is_enabled = False

    def _update_sensor_data(self, dt=None):
        """
        Update sensor data from device or mock source.

        Called periodically by Kivy Clock. Updates all active sensor properties.

        Args:
            dt (float): Time delta from previous call (provided by Clock)
        """
        timestamp = datetime.now().isoformat()

        for sensor_type in self._active_sensors:
            try:
                if self.platform == "android":
                    self._read_android_sensor(sensor_type, timestamp)
                else:
                    self._read_mock_sensor(sensor_type, timestamp)
            except Exception as e:
                logger.error(f"Error reading {sensor_type}: {e}")

    def _read_android_sensor(self, sensor_type: str, timestamp: str):
        """
        Read sensor data from Android device.

        Args:
            sensor_type (str): Type of sensor to read
            timestamp (str): ISO format timestamp
        """
        try:
            if sensor_type == "accelerometer":
                data = accelerometer.acceleration
                if data:
                    self.accelerometer_data = {
                        "x": round(data[0], 3),
                        "y": round(data[1], 3),
                        "z": round(data[2], 3),
                        "timestamp": timestamp,
                    }
            elif sensor_type == "gyroscope":
                data = gyroscope.rotation
                if data:
                    self.gyroscope_data = {
                        "x": round(data[0], 3),
                        "y": round(data[1], 3),
                        "z": round(data[2], 3),
                        "timestamp": timestamp,
                    }
            elif sensor_type == "magnetometer":
                data = magnetometer.magnetic_field
                if data:
                    self.magnetometer_data = {
                        "x": round(data[0], 3),
                        "y": round(data[1], 3),
                        "z": round(data[2], 3),
                        "timestamp": timestamp,
                    }
            elif sensor_type == "light":
                data = light.illuminance
                if data is not None:
                    self.light_data = {"value": round(data, 1), "timestamp": timestamp}
            elif sensor_type == "proximity":
                data = proximity.distance
                if data is not None:
                    self.proximity_data = {"value": round(data, 2), "timestamp": timestamp}
        except Exception as e:
            logger.debug(f"Could not read {sensor_type}: {e}")

    def _read_mock_sensor(self, sensor_type: str, timestamp: str):
        """
        Read simulated sensor data for desktop testing.

        Generates realistic-looking mock data based on sine/cosine functions.

        Args:
            sensor_type (str): Type of sensor to read
            timestamp (str): ISO format timestamp
        """
        import math

        counter = self._mock_data_counters.get(sensor_type, 0)
        self._mock_data_counters[sensor_type] = (counter + 1) % 360

        angle_rad = math.radians(counter)

        if sensor_type == "accelerometer":
            self.accelerometer_data = {
                "x": round(math.sin(angle_rad) * 9.8, 3),
                "y": round(math.cos(angle_rad) * 9.8, 3),
                "z": round(9.81, 3),
                "timestamp": timestamp,
            }
        elif sensor_type == "gyroscope":
            self.gyroscope_data = {
                "x": round(math.sin(angle_rad) * 30, 3),
                "y": round(math.cos(angle_rad) * 30, 3),
                "z": round(math.sin(angle_rad * 2) * 15, 3),
                "timestamp": timestamp,
            }
        elif sensor_type == "magnetometer":
            self.magnetometer_data = {
                "x": round(math.sin(angle_rad) * 50, 3),
                "y": round(math.cos(angle_rad) * 50, 3),
                "z": round(25, 3),
                "timestamp": timestamp,
            }
        elif sensor_type == "light":
            light_value = 500 + 300 * math.sin(angle_rad)
            self.light_data = {"value": round(light_value, 1), "timestamp": timestamp}
        elif sensor_type == "proximity":
            proximity_value = 5 + 4 * math.cos(angle_rad)
            self.proximity_data = {
                "value": round(proximity_value, 2),
                "timestamp": timestamp,
            }

    def get_sensor_data(self) -> dict:
        """
        Get formatted data from all sensors.

        Returns:
            dict: Dictionary containing data from all active sensors
                Example: {
                    'accelerometer': {'x': 0.123, 'y': 0.456, 'z': 9.81, ...},
                    'gyroscope': {...},
                    'magnetometer': {...},
                    'light': {'value': 500.0, ...},
                    'proximity': {'value': 5.2, ...}
                }
        """
        return {
            "accelerometer": dict(self.accelerometer_data),
            "gyroscope": dict(self.gyroscope_data),
            "magnetometer": dict(self.magnetometer_data),
            "light": dict(self.light_data),
            "proximity": dict(self.proximity_data),
        }

    def _update_status_message(self):
        """Update the status message based on current sensor state."""
        active_count = len(self._active_sensors)
        available_count = sum(1 for v in self.available_sensors.values() if v)

        if active_count == 0:
            self.status_message = f"Sensors: {available_count}/{len(self.SENSOR_TYPES)} available"
        else:
            self.status_message = f"Sensors: {active_count} active ({available_count} available)"

        logger.debug(self.status_message)

    def is_sensor_active(self, sensor_type: str) -> bool:
        """
        Check if a specific sensor is currently active.

        Args:
            sensor_type (str): Type of sensor to check

        Returns:
            bool: True if sensor is active, False otherwise
        """
        return sensor_type in self._active_sensors

    def get_active_sensors(self) -> list:
        """
        Get list of currently active sensors.

        Returns:
            list: List of active sensor types
        """
        return list(self._active_sensors)

    def cleanup(self):
        """Clean up sensor resources (should be called on app exit)."""
        logger.info("Cleaning up sensor resources")
        self.disable_all()
        if self._update_clock is not None:
            self._update_clock.cancel()
            self._update_clock = None
