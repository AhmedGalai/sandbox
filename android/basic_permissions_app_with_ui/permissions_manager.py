"""
Permission Management Module for Kivy Android Applications

This module handles platform-specific permission management for both Android and
desktop environments. It provides a unified interface for checking and requesting
permissions with reactive Kivy properties for UI updates.

Features:
- Platform detection (Android vs Desktop)
- Multiple permission types (camera, microphone, location, storage)
- Permission state tracking with Kivy properties
- Mock data for desktop testing
- Error handling for permission denials
"""

import logging
from kivy.properties import BooleanProperty, DictProperty, StringProperty
from kivy.core.window import Window

logger = logging.getLogger(__name__)

# Platform detection
try:
    from android.permissions import request_permissions, Permission, check_permission
    PLATFORM = "android"
    logger.info("Running on Android platform")
except ImportError:
    PLATFORM = "desktop"
    logger.info("Running on desktop platform (mock mode)")


class PermissionsManager:
    """
    Manages application permissions with support for both Android and desktop platforms.

    Uses Kivy properties to maintain permission state for reactive UI updates.
    On desktop, uses mock data to simulate Android behavior for testing.

    Attributes:
        camera_granted: BooleanProperty - Camera permission status
        microphone_granted: BooleanProperty - Microphone permission status
        location_granted: BooleanProperty - Location permission status
        storage_granted: BooleanProperty - Storage permission status
        permissions_requested: BooleanProperty - Flag indicating if permissions were requested
        status_message: StringProperty - Human-readable status message
    """

    # Define Kivy properties for reactive UI updates
    camera_granted = BooleanProperty(False)
    microphone_granted = BooleanProperty(False)
    location_granted = BooleanProperty(False)
    storage_granted = BooleanProperty(False)
    permissions_requested = BooleanProperty(False)
    status_message = StringProperty("Ready to request permissions")

    # Permission to property mapping
    PERMISSION_PROPERTIES = {
        "camera": "camera_granted",
        "microphone": "microphone_granted",
        "location": "location_granted",
        "storage": "storage_granted",
    }

    # Android permission strings
    ANDROID_PERMISSIONS = {
        "camera": Permission.CAMERA,
        "microphone": Permission.RECORD_AUDIO,
        "location": Permission.ACCESS_FINE_LOCATION,
        "storage": Permission.WRITE_EXTERNAL_STORAGE,
    }

    def __init__(self):
        """Initialize the permissions manager."""
        self.platform = PLATFORM
        self._permission_callbacks = {}
        logger.debug(f"PermissionsManager initialized on {self.platform}")

    def check_permission(self, permission_type: str) -> bool:
        """
        Check if a specific permission is granted.

        Args:
            permission_type (str): Type of permission to check
                ('camera', 'microphone', 'location', 'storage')

        Returns:
            bool: True if permission is granted, False otherwise

        Raises:
            ValueError: If permission_type is not recognized
        """
        if permission_type not in self.PERMISSION_PROPERTIES:
            raise ValueError(f"Unknown permission type: {permission_type}")

        if self.platform == "android":
            try:
                android_perm = self.ANDROID_PERMISSIONS[permission_type]
                is_granted = check_permission(android_perm)
                logger.debug(f"{permission_type} permission check: {is_granted}")
                return is_granted
            except Exception as e:
                logger.error(f"Error checking {permission_type} permission: {e}")
                return False
        else:
            # Desktop mode: return mock data
            property_name = self.PERMISSION_PROPERTIES[permission_type]
            return getattr(self, property_name)

    def request_permissions(self, permission_types: list = None, callback=None):
        """
        Request one or more permissions from the user.

        Args:
            permission_types (list): List of permission types to request.
                If None, requests all permissions.
                Valid types: 'camera', 'microphone', 'location', 'storage'
            callback (callable): Optional callback function called with
                (permission_type, granted) when request completes

        Returns:
            None
        """
        if permission_types is None:
            permission_types = list(self.PERMISSION_PROPERTIES.keys())

        # Validate permission types
        invalid_perms = [p for p in permission_types if p not in self.PERMISSION_PROPERTIES]
        if invalid_perms:
            raise ValueError(f"Unknown permission types: {invalid_perms}")

        logger.info(f"Requesting permissions: {permission_types}")

        if self.platform == "android":
            self._request_android_permissions(permission_types, callback)
        else:
            self._request_desktop_permissions(permission_types, callback)

        self.permissions_requested = True

    def _request_android_permissions(self, permission_types: list, callback=None):
        """
        Request permissions on Android platform.

        Args:
            permission_types (list): Permissions to request
            callback (callable): Callback function for permission results
        """
        try:
            android_perms = [
                self.ANDROID_PERMISSIONS[perm_type]
                for perm_type in permission_types
            ]

            def on_permissions_result(permissions, grant_results):
                """Callback for Android permission request results."""
                for perm_type in permission_types:
                    android_perm = self.ANDROID_PERMISSIONS[perm_type]
                    is_granted = android_perm in permissions and grant_results[android_perm]
                    property_name = self.PERMISSION_PROPERTIES[perm_type]
                    setattr(self, property_name, is_granted)

                    logger.info(
                        f"Permission {perm_type}: {'granted' if is_granted else 'denied'}"
                    )

                    if callback:
                        try:
                            callback(perm_type, is_granted)
                        except Exception as e:
                            logger.error(f"Error in permission callback: {e}")

                self._update_status_message()

            request_permissions(android_perms, on_permissions_result)
        except Exception as e:
            logger.error(f"Error requesting Android permissions: {e}")
            self.status_message = f"Error requesting permissions: {e}"

    def _request_desktop_permissions(self, permission_types: list, callback=None):
        """
        Request permissions on desktop platform (simulated).

        On desktop, all permissions are simulated as granted for testing purposes.

        Args:
            permission_types (list): Permissions to request
            callback (callable): Callback function for permission results
        """
        logger.info("Desktop mode: simulating permission grants")

        for perm_type in permission_types:
            property_name = self.PERMISSION_PROPERTIES[perm_type]
            setattr(self, property_name, True)

            logger.debug(f"{perm_type} permission granted (simulated)")

            if callback:
                try:
                    callback(perm_type, True)
                except Exception as e:
                    logger.error(f"Error in permission callback: {e}")

        self._update_status_message()

    def get_all_permissions_status(self) -> dict:
        """
        Get the status of all permissions.

        Returns:
            dict: Dictionary mapping permission types to their granted status
                Example: {
                    'camera': True,
                    'microphone': True,
                    'location': False,
                    'storage': True
                }
        """
        return {
            perm_type: self.check_permission(perm_type)
            for perm_type in self.PERMISSION_PROPERTIES.keys()
        }

    def _update_status_message(self):
        """Update the status message based on current permission state."""
        status = self.get_all_permissions_status()
        granted_count = sum(1 for v in status.values() if v)
        total_count = len(status)

        self.status_message = f"Permissions: {granted_count}/{total_count} granted"
        logger.debug(self.status_message)

    def has_all_permissions(self) -> bool:
        """
        Check if all permissions are granted.

        Returns:
            bool: True if all permissions are granted, False otherwise
        """
        status = self.get_all_permissions_status()
        return all(status.values())

    def get_permission_description(self, permission_type: str) -> str:
        """
        Get a human-readable description of a permission.

        Args:
            permission_type (str): Type of permission

        Returns:
            str: Human-readable description
        """
        descriptions = {
            "camera": "Camera",
            "microphone": "Microphone",
            "location": "Location",
            "storage": "Storage",
        }
        return descriptions.get(permission_type, permission_type)

    def reset_permissions(self):
        """Reset all permission properties to False (for testing)."""
        logger.warning("Resetting all permissions")
        self.camera_granted = False
        self.microphone_granted = False
        self.location_granted = False
        self.storage_granted = False
        self.permissions_requested = False
        self._update_status_message()
