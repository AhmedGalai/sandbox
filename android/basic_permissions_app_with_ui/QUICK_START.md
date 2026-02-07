# Quick Start Guide

## Installation (Desktop)

```bash
# Navigate to project directory
cd /home/ag/Desktop/sandbox/android/basic_permissions_app_with_ui

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Application Overview

The app has three main sections:

### 1. Status Header
- Shows app title
- Displays permissions status (e.g., "Permissions: 3/4 granted")

### 2. Permissions Section
Shows 4 permissions with status indicators and request buttons:
- **Camera** (Request button to ask for permission)
- **Microphone** (Request button to ask for permission)
- **Location** (Request button to ask for permission)
- **Storage** (Request button to ask for permission)

Color indicators:
- Green = Permission granted
- Red = Permission denied

### 3. Sensors Section
Shows 5 sensors with status, readings, and enable/disable toggles:
- **Accelerometer** - X, Y, Z acceleration values
- **Gyroscope** - X, Y, Z rotation values
- **Magnetometer** - X, Y, Z magnetic field values
- **Light Sensor** - Illuminance value
- **Proximity Sensor** - Distance value

Color indicators:
- Green = Sensor available and enabled
- Red = Sensor disabled
- Gray = Sensor not available

Control buttons:
- **Enable All Sensors** - Activate all available sensors
- **Disable All Sensors** - Deactivate all sensors

## Desktop vs Android Mode

### Desktop Mode (Default)
When you run on a desktop/laptop:
- All permissions are simulated as granted
- Sensor data is generated with realistic mock values
- Perfect for testing without an Android device
- Allows development of UI without real hardware

### Android Mode
When you deploy to an Android device:
- Permissions use real Android permission system
- Sensor data comes from actual device sensors
- Automatic lifecycle management (pause/resume)
- Full access to device capabilities

## Key Actions

### Requesting Permissions
```
1. Click "Request" button next to any permission
2. On Android: System dialog appears
3. On Desktop: Permission is granted immediately
```

### Enabling Sensors
```
Option 1: Individual sensor
- Click "ON" toggle next to a sensor
- If available (green indicator), it activates
- Real-time data appears in the display

Option 2: All sensors
- Click "Enable All Sensors" button
- All available sensors activate
- Sensor readings update automatically
```

### Disabling Sensors
```
Option 1: Individual sensor
- Click toggle to turn OFF
- Sensor data updates stop

Option 2: All sensors
- Click "Disable All Sensors" button
- All active sensors deactivate
```

## Understanding the Displays

### Permission Widget
```
● [Permission Name] [Status] [Request]
```
- Indicator: Green (granted) or Red (denied)
- Name: Permission description
- Status: "Granted" or "Denied"
- Button: Click to request permission

### Sensor Widget
```
● [Sensor Name] [X:0.12 Y:0.45 Z:9.81] [OFF/ON]
```
For multi-axis sensors (accelerometer, gyroscope, magnetometer):
- Indicator: Green (available) or Gray (unavailable)
- Name: Sensor description
- Data: X, Y, Z values updated in real-time
- Toggle: ON (enabled/green) or OFF (disabled/red)

For single-value sensors (light, proximity):
- Indicator: Green (available) or Gray (unavailable)
- Name: Sensor description
- Data: Current value updated in real-time
- Toggle: ON (enabled/green) or OFF (disabled/red)

## Code Structure

### Main Application Flow
```
main.py
  ├── PermissionsSensorsApp (Kivy App)
  │   ├── Imports PermissionsManager
  │   ├── Imports SensorsManager
  │   ├── Imports UI Components
  │   └── Manages app lifecycle
  │
  ├── permissions_manager.py (Manager)
  │   └── PermissionsManager class
  │
  ├── sensors_manager.py (Manager)
  │   └── SensorsManager class
  │
  └── ui_components.py (UI)
      ├── PermissionWidget
      ├── SensorWidget
      ├── PermissionsPanel
      └── SensorsPanel
```

### Module Interactions
```
main.py
  ↓
  Creates → PermissionsManager
  Creates → SensorsManager
  Creates → UI Panels
  ↓
  Binds properties → Reactive UI updates
  Manages callbacks → Button/Toggle clicks
  Controls lifecycle → Pause/Resume
```

## Common Issues & Solutions

### Issue: "No module named 'kivy'"
**Solution:**
```bash
pip install kivy
```

### Issue: "No module named 'plyer'"
**Solution:**
```bash
pip install plyer
```

### Issue: Sensors not updating
**Solution:**
1. Check that sensor toggle is ON (green)
2. Check that sensor indicator is green (available)
3. Make sure app is in foreground (not paused)

### Issue: "ImportError: No module named 'android'"
**Solution:**
This is normal on desktop! The app automatically detects this and uses mock mode. This error will not occur on Android.

### Issue: App window is too small
**Solution:**
The window size is set to 360x800 pixels. You can adjust in main.py:
```python
Window.size = (360, 800)  # Change these values
```

## Performance Tips

- **Sensor Update Rate**: Currently 10Hz (100ms intervals)
- To adjust: In sensors_manager.py, change `0.1` to `0.05` for 20Hz (more CPU usage)
- **Battery Life**: Disable sensors you don't need
- **UI Responsiveness**: More sensors enabled = more data processing

## Deploying to Android

1. Install buildozer:
```bash
pip install buildozer
```

2. Create buildozer.spec:
```bash
buildozer init
```

3. Edit buildozer.spec:
```ini
requirements = python3,kivy,plyer,android
permissions = CAMERA,RECORD_AUDIO,ACCESS_FINE_LOCATION,WRITE_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE
features = android.hardware.sensor.accelerometer,android.hardware.sensor.gyroscope,...
```

4. Build APK:
```bash
buildozer android debug
```

5. Install and run:
```bash
buildozer android debug deploy run
```

## Testing Checklist

- [ ] App starts without errors
- [ ] Permissions display correctly
- [ ] Sensors display correctly
- [ ] Can request individual permissions
- [ ] Can enable/disable individual sensors
- [ ] Can enable all sensors with button
- [ ] Can disable all sensors with button
- [ ] Sensor data updates in real-time
- [ ] App handles pause/resume gracefully
- [ ] No crashes during normal operation

## File Overview

| File | Purpose | Key Class |
|------|---------|-----------|
| main.py | Application entry point | PermissionsSensorsApp |
| permissions_manager.py | Permission management | PermissionsManager |
| sensors_manager.py | Sensor data collection | SensorsManager |
| ui_components.py | UI widgets | PermissionWidget, SensorWidget, PermissionsPanel, SensorsPanel |
| requirements.txt | Python dependencies | kivy, plyer, buildozer |

## Getting Help

- Check README.md for detailed documentation
- Check IMPLEMENTATION_SUMMARY.md for technical details
- Review docstrings in each Python file for class/method documentation
- Check console output for error messages and debugging info

## Next Steps

1. Run the app on desktop to verify everything works
2. Test permission requests on Android device
3. Test real sensor data from device sensors
4. Customize UI colors/layout as needed
5. Add additional features (data logging, graphs, etc.)

Enjoy! The application is ready to use immediately.
