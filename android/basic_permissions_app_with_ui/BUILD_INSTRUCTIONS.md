# Build Instructions for APK Compilation

This guide provides step-by-step instructions to compile the Kivy app to an Android APK.

## Prerequisites

### System Requirements
- Linux operating system (Ubuntu 20.04+ recommended)
- At least 8GB RAM
- 20GB free disk space
- Stable internet connection

### Required System Packages

Install the following packages on Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y \
    python3-pip \
    build-essential \
    git \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libgstreamer1.0-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    openjdk-17-jdk \
    unzip \
    zip \
    autoconf \
    libtool \
    pkg-config \
    cmake \
    ninja-build
```

For other Linux distributions, install equivalent packages.

## Step 1: Install Python Dependencies

```bash
# Navigate to the project directory
cd /home/ag/Desktop/sandbox/android/basic_permissions_app_with_ui

# Install Python requirements
python3 -m pip install --user --upgrade pip
python3 -m pip install --user -r requirements.txt
python3 -m pip install --user buildozer cython
```

## Step 2: Install Buildozer

```bash
# Install buildozer
python3 -m pip install --user buildozer

# Verify installation
buildozer --version
```

## Step 3: First-Time Build Setup

Buildozer will automatically download and install:
- Android SDK
- Android NDK
- Python-for-Android (p4a)
- Required build tools

This happens automatically on the first build.

## Step 4: Build the APK

### Option A: Debug APK (Recommended for Testing)

```bash
# Navigate to project directory
cd /home/ag/Desktop/sandbox/android/basic_permissions_app_with_ui

# Build debug APK (first build takes 30-60 minutes)
buildozer -v android debug
```

The APK will be created at:
```
bin/PermissionsSensorsDemo-1.0-debug.apk
```

### Option B: Release APK (For Distribution)

```bash
# Build release APK
buildozer android release

# Sign the APK (required for installation)
# You'll need to create a keystore first:
keytool -genkey -v -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000

# Then sign the APK
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore bin/PermissionsSensorsDemo-1.0-release-unsigned.apk my-key-alias

# Align the APK
zipalign -v 4 bin/PermissionsSensorsDemo-1.0-release-unsigned.apk bin/PermissionsSensorsDemo-1.0-release.apk
```

## Step 5: Deploy to Android Device

### Enable Developer Mode on Android Device

1. Go to **Settings > About Phone**
2. Tap **Build Number** 7 times to enable Developer Mode
3. Go to **Settings > Developer Options**
4. Enable **USB Debugging**

### Install via USB

```bash
# Connect device via USB

# Deploy and run the APK
buildozer android deploy run

# View logs in real-time
buildozer android logcat
```

### Install via File Transfer

```bash
# Transfer the APK to your device
adb push bin/PermissionsSensorsDemo-1.0-debug.apk /sdcard/Download/

# On your device:
# - Navigate to Downloads folder
# - Tap the APK file
# - Allow installation from unknown sources if prompted
# - Install the app
```

## Step 6: Testing the App

After installation:

1. **Launch the app** from your device's app drawer
2. **Test permissions**:
   - Tap "Request All Permissions" button
   - Grant permissions when prompted
   - Verify status changes to "Granted" (green)
3. **Test sensors**:
   - Tap "Enable All Sensors" button
   - Verify sensor data updates in real-time
   - Move device to see accelerometer/gyroscope changes

## Troubleshooting

### Build Fails with "Command not found"

Ensure all system packages are installed:
```bash
sudo apt install -y openjdk-17-jdk build-essential
```

### Build Fails with "NDK not found"

Buildozer will download NDK automatically. If it fails:
```bash
buildozer android clean
buildozer -v android debug
```

### Build Fails with Memory Error

Increase Java heap size in buildozer.spec:
```ini
android.gradle_options = -Xmx4096m
```

### APK Won't Install on Device

1. Enable "Install from Unknown Sources" in device settings
2. Check minimum Android version (API 21 = Android 5.0+)
3. Try uninstalling previous version if exists

### Permissions Not Working

Ensure your device is running Android 6.0+ (API 23+) for runtime permissions.

### Sensors Not Showing Data

1. Check if device has the sensor (not all devices have all sensors)
2. Ensure permissions are granted
3. Check logcat for errors:
   ```bash
   buildozer android logcat | grep python
   ```

## Build Times

- **First build**: 30-60 minutes (downloads SDK, NDK, compiles dependencies)
- **Subsequent builds**: 2-5 minutes (only recompiles changed code)

## Clean Build

If you encounter persistent issues:

```bash
# Clean all build artifacts
buildozer android clean

# Remove buildozer cache (forces re-download of dependencies)
rm -rf .buildozer

# Rebuild from scratch
buildozer -v android debug
```

## Desktop Testing (Without Building APK)

You can test the UI and basic functionality on desktop:

```bash
# Install Kivy
python3 -m pip install --user kivy plyer

# Run the app
python3 main.py
```

**Note**: Permissions and sensors will use mock data on desktop, but the UI will work identically.

## File Locations

After successful build:

```
android/basic_permissions_app_with_ui/
├── bin/                              # Compiled APK files
│   └── PermissionsSensorsDemo-1.0-debug.apk
├── .buildozer/                       # Buildozer cache (auto-created)
│   └── android/                      # Android SDK, NDK, toolchain
└── buildozer.spec                    # Build configuration
```

## Next Steps

1. **Test on multiple devices** to ensure compatibility
2. **Add custom icons** (update buildozer.spec: `icon.filename`)
3. **Add splash screen** (update buildozer.spec: `presplash.filename`)
4. **Update version** before each release (buildozer.spec: `version`)
5. **Generate signed APK** for Google Play Store distribution

## Additional Resources

- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Kivy Android Documentation](https://kivy.org/doc/stable/guide/android.html)
- [Python-for-Android Documentation](https://python-for-android.readthedocs.io/)

## Support

If you encounter issues:

1. Check the logs: `buildozer android logcat | grep python`
2. Review buildozer verbose output: `buildozer -v android debug`
3. Check Kivy documentation
4. Search Kivy forums and Stack Overflow

---

**The app is now ready to build and deploy! Follow the steps above to compile your APK.**
