[app]
# Application metadata
title = Permissions & Sensors Demo
package.name = permissionsdemo
package.domain = org.example

# Source files configuration
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Version configuration
version = 1.0

# Requirements - Python packages to include
requirements = python3,kivy==2.3.0,plyer==2.1.0,pyjnius

# Permission requirements
android.permissions = CAMERA,RECORD_AUDIO,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET,ACCESS_NETWORK_STATE,VIBRATE

# Features
android.features =

# Gradle dependencies
android.gradle_dependencies = androidx.appcompat:appcompat:1.6.1,androidx.work:work-runtime:2.8.1

# Build configuration
orientation = portrait
fullscreen = 0

# Java classes to add
# java_classes =

# Libraries to link
# android.add_libs_armeabi_v7a =
# android.add_libs_arm64_v8a =

# Network access
# internet = True

[buildozer]

# Android build configuration
log_level = 2
warn_on_root = 1

# Build directory configuration
android.archs = arm64-v8a,armeabi-v7a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.bootstrap = sdl2

# Presplash configuration (optional - uncomment to use)
# p4a.source_dir =
p4a.local_recipes = ./recipes
# android.presplash_haspath = 1
# android.presplash = ./data/presplash.png

# Icon configuration (optional - uncomment to use)
# android.icon = ./data/icon.png

# Release signing (optional - uncomment for release builds)
# android.release_artifact = apk
# android.keystore = 1
# android.keystore_path = ~/.keystore
# android.keystore_alias = kivy-app

# Gradle options
android.gradle_options = org.gradle.jvmargs=-Xmx4096m

# P4A configuration
p4a.hook =

# Initialization
android.entrypoint = org.kivy.android.PythonActivity
