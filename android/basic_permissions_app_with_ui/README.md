# Kivy Android Permissions and Sensors Monitor

A production-ready Kivy application for managing Android permissions and monitoring device sensors. This application provides a comprehensive interface for requesting permissions and displaying real-time sensor data from accelerometer, gyroscope, magnetometer, light, and proximity sensors.

## Features

### Permission Management
- Request camera, microphone, location, and storage permissions
- Visual permission status indicators (green=granted, red=denied)
- Individual permission request buttons
- Platform-aware (works on Android and desktop)
- Mock permission system for desktop testing

### Sensor Management
- Support for 5 sensor types:
  - Accelerometer (X, Y, Z acceleration)
  - Gyroscope (X, Y, Z rotation)
  - Magnetometer (X, Y, Z magnetic field)
  - Light Sensor (illuminance)
  - Proximity Sensor (distance)
- Real-time sensor data display (10Hz update rate)
- Individual sensor enable/disable toggles
- Bulk enable/disable all sensors buttons
- Automatic sensor cleanup on app pause/resume
- Platform-aware (real sensors on Android, mock data on desktop)

### User Interface
- Clean, intuitive layout
- Scrollable content for devices with small screens
- Reactive updates using Kivy properties
- Color-coded status indicators
- Real-time sensor data visualization

## File Structure

```
basic_permissions_app_with_ui/
├── main.py                    # Main application entry point
├── permissions_manager.py     # Permission management module
├── sensors_manager.py         # Sensor data collection module
├── ui_components.py           # Reusable UI widgets
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Module Descriptions

### main.py
Main application class (`PermissionsSensorsApp`) that:
- Initializes the application and managers
- Builds the UI layout with permissions and sensors panels
- Handles permission request callbacks
- Manages sensor enable/disable callbacks
- Implements app lifecycle methods (on_start, on_pause, on_resume, on_stop)
- Provides error handling and logging

### permissions_manager.py
`PermissionsManager` class that:
- Handles platform detection (Android vs Desktop)
- Manages permissions: camera, microphone, location, storage
- Provides Kivy properties for reactive UI updates
- Implements check_permission() for individual checks
- Implements request_permissions() with callback support
- Returns permission status as dict via get_all_permissions_status()
- Uses mock data for desktop testing

### sensors_manager.py
`SensorsManager` class that:
- Manages access to device sensors via Plyer library
- Handles platform detection (real sensors on Android, mock on desktop)
- Implements enable_sensor() and disable_sensor() methods
- Uses Kivy Clock for 10Hz periodic updates
- Provides Kivy properties for all sensor data
- Detects available sensors automatically
- Implements enable_all() and disable_all() methods
- Generates realistic mock sensor data for testing

### ui_components.py
Reusable UI widgets:
- `PermissionWidget`: Displays single permission with request button
- `SensorWidget`: Displays sensor data with enable/disable toggle
- `PermissionsPanel`: Container for multiple permission widgets
- `SensorsPanel`: Container for multiple sensor widgets

Color coding:
- Green: Permission granted or sensor available/active
- Red: Permission denied or sensor disabled
- Gray: Sensor unavailable

## Installation

### Prerequisites
- Python 3.7+
- Kivy 2.2.0+
- Plyer 2.1.0+

### On Desktop (for development/testing)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### On Android (with Buildozer)
```bash
# Install buildozer
pip install buildozer

# Create buildozer.spec (if not exists)
buildozer android debug

# Edit buildozer.spec to set:
# - requirements = python3,kivy,plyer,android
# - permissions = CAMERA,RECORD_AUDIO,ACCESS_FINE_LOCATION,WRITE_EXTERNAL_STORAGE
# - features = android.hardware.sensor.accelerometer,android.hardware.sensor.gyroscope, etc.

# Build APK
buildozer android debug

# Install and run
buildozer android debug deploy run
```

## Usage

### Basic Usage
```python
from main import PermissionsSensorsApp

app = PermissionsSensorsApp()
app.run()
```

### Programmatic Usage

#### Using PermissionsManager
```python
from permissions_manager import PermissionsManager

pm = PermissionsManager()

# Request all permissions
pm.request_permissions()

# Request specific permission
pm.request_permissions(['camera'], callback=lambda perm, granted: print(f"{perm}: {granted}"))

# Check permission status
is_camera_granted = pm.check_permission('camera')

# Get all permission status
status = pm.get_all_permissions_status()
# Returns: {'camera': True, 'microphone': False, 'location': True, 'storage': True}
```

#### Using SensorsManager
```python
from sensors_manager import SensorsManager

sm = SensorsManager()

# Detect available sensors
sm.detect_available_sensors()

# Check available sensors
print(sm.available_sensors)  # {'accelerometer': True, 'gyroscope': True, ...}

# Enable specific sensor
sm.enable_sensor('accelerometer')

# Enable all available sensors
sm.enable_all()

# Get sensor data
sensor_data = sm.get_sensor_data()
# Returns: {
#     'accelerometer': {'x': 0.123, 'y': 0.456, 'z': 9.81, 'timestamp': '...'},
#     'gyroscope': {...},
#     ...
# }

# Disable sensor
sm.disable_sensor('accelerometer')

# Cleanup resources
sm.cleanup()
```

## Platform Support

### Android
- Full sensor support via Plyer library
- Real permission requests via Android.permissions
- Automatic lifecycle management (pause/resume)

### Desktop (Linux, macOS, Windows)
- Mock permission system (all permissions granted)
- Generated mock sensor data for testing
- Allows development and testing without Android device

## Architecture

### Design Patterns
- **Manager Pattern**: Separate managers for permissions and sensors
- **Observer Pattern**: Kivy properties for reactive UI updates
- **Singleton Pattern**: Single instance of each manager
- **Factory Pattern**: UI components created dynamically based on permission/sensor types

### Key Design Decisions
1. **Kivy Properties**: Used for reactive binding between managers and UI
2. **Clock-based Updates**: Sensors update at 10Hz via Kivy Clock (non-blocking)
3. **Platform Abstraction**: Platform detection allows desktop testing without Android
4. **Async Callbacks**: Permission requests handled with callbacks for non-blocking operations
5. **Graceful Degradation**: Missing sensors/permissions logged but don't crash app

## Logging

The application uses Python's built-in logging module with DEBUG level:

```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

All logs are printed to console with timestamps.

## Error Handling

The application includes comprehensive error handling:
- Try-except blocks in all critical operations
- Graceful degradation when sensors are unavailable
- User-friendly error messages
- Detailed logging for debugging

## Testing

### Desktop Testing
Run the application on desktop to test without an Android device:
```bash
python main.py
```

On desktop:
- All permissions are simulated as granted
- Sensors generate realistic mock data
- UI behaves identically to Android version

### Testing Specific Features
```python
# Test permissions
pm = PermissionsManager()
pm.request_permissions()  # Grants all on desktop

# Test sensors
sm = SensorsManager()
sm.enable_all()  # Activates all mock sensors
print(sm.get_sensor_data())  # View mock data
```

## Performance

- Sensor update rate: 10Hz (100ms intervals) to balance responsiveness and CPU usage
- Reactive UI updates only when data changes
- Efficient property binding using Kivy's property system
- Minimal memory footprint with proper resource cleanup

## Known Limitations

1. **Plyer Sensor Support**: Not all sensors are available on all devices
2. **Android Permissions**: Requires Android API level 23+ for runtime permissions
3. **Desktop Mock Data**: Mock sensors don't accurately simulate real-world behavior
4. **Proximity Sensor**: Not available on all devices

## Future Enhancements

- Sensor data logging and export
- Permission history tracking
- Advanced sensor data visualization (graphs)
- Sensor data recording
- Permission analytics
- Custom permission request dialogs
- Haptic feedback support
- Advanced gesture recognition from sensors

## Dependencies

- **kivy**: Python UI framework for creating native applications
- **plyer**: Library for accessing device features across platforms
- **buildozer**: Build tool for packaging Kivy apps as APKs

## License

This is example code for demonstration purposes.

## Troubleshooting

### "ImportError: No module named 'android'"
This is expected on desktop. The application detects this and uses mock mode. To fix on Android, ensure `android` library is included in buildozer.spec.

### "Sensor data not updating"
- Ensure sensor is enabled (toggle is ON)
- Check that sensor is available (status indicator is green)
- Verify app is in foreground (sensors disable on pause)

### "Permission request not working"
- On Android, check device settings to see if app has permissions
- On desktop, all permissions are simulated as granted
- Check logcat for permission request errors

### "App crashes on startup"
- Check console output for error messages
- Verify all imports are available (especially plyer)
- Ensure buildozer.spec has all required permissions

## Support

For issues or questions, refer to:
- Kivy Documentation: https://kivy.org/doc/stable/
- Plyer Documentation: https://plyer.readthedocs.io/
- Buildozer Documentation: https://buildozer.readthedocs.io/
