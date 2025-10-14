"""Diagnostics support for Sofabaton Hub."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import SofabatonHubDataUpdateCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry.
    
    Args:
        hass: Home Assistant instance
        entry: Config entry to get diagnostics for
        
    Returns:
        Dictionary containing diagnostic information with sensitive data redacted
    """
    coordinator: SofabatonHubDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Get coordinator data
    data = coordinator.data or {}
    
    # Build diagnostics data with sensitive information redacted
    diagnostics_data = {
        "config_entry": _get_config_entry_diagnostics(entry),
        "coordinator_data": _get_coordinator_data_diagnostics(data),
        "coordinator_state": _get_coordinator_state_diagnostics(coordinator),
    }
    
    return diagnostics_data


def _get_config_entry_diagnostics(entry: ConfigEntry) -> dict[str, Any]:
    """Get config entry diagnostics with sensitive data redacted.
    
    Args:
        entry: Config entry
        
    Returns:
        Dictionary containing config entry information
    """
    return {
        "title": entry.title,
        "version": entry.version,
        # Redact MAC address: only show first 6 characters
        "mac": entry.data.get("mac", "")[:6] + "******" if entry.data.get("mac") else None,
        "host": entry.data.get("host"),
        "port": entry.data.get("port"),
        # Don't expose actual credentials, just indicate if they exist
        "has_username": bool(entry.data.get("username")),
        "has_password": bool(entry.data.get("password")),
        "unique_id": entry.unique_id,
        "entry_id": entry.entry_id,
    }


def _get_coordinator_data_diagnostics(data: dict[str, Any]) -> dict[str, Any]:
    """Get coordinator data diagnostics.
    
    Args:
        data: Coordinator data dictionary
        
    Returns:
        Dictionary containing coordinator data information
    """
    activities = data.get("activities", {})
    devices = data.get("devices", {})
    keys = data.get("keys", {})
    
    return {
        # Activity information
        "activities_count": len(activities),
        "activities": [
            {
                "id": activity.get("id"),
                "name": activity.get("name"),
                "state": activity.get("state"),
            }
            for activity in activities.values()
        ],
        "current_activity_id": data.get("current_activity_id"),
        
        # Device information (if enabled)
        "devices_count": len(devices),
        "devices": [
            {
                "id": device.get("id"),
                "name": device.get("name"),
            }
            for device in devices.values()
        ] if devices else [],
        
        # Keys statistics (don't expose actual key data, just counts)
        "keys_stats": {
            "assigned_keys": {
                "activities_count": len(keys.get("assigned", {})),
                "total_keys": sum(
                    len(key_list) if isinstance(key_list, list) else 0
                    for key_list in keys.get("assigned", {}).values()
                ),
                "activities_with_keys": list(keys.get("assigned", {}).keys()),
            },
            "macro_keys": {
                "activities_count": len(keys.get("macros", {})),
                "total_keys": sum(
                    len(key_list) if isinstance(key_list, list) else 0
                    for key_list in keys.get("macros", {}).values()
                ),
                "activities_with_keys": list(keys.get("macros", {}).keys()),
            },
            "favorite_keys": {
                "activities_count": len(keys.get("favorites", {})),
                "total_keys": sum(
                    len(key_list) if isinstance(key_list, list) else 0
                    for key_list in keys.get("favorites", {}).values()
                ),
                "activities_with_keys": list(keys.get("favorites", {}).keys()),
            },
            "device_keys": {
                "devices_count": len(keys.get("device_keys", {})),
                "total_keys": sum(
                    len(key_list) if isinstance(key_list, list) else 0
                    for key_list in keys.get("device_keys", {}).values()
                ),
                "devices_with_keys": list(keys.get("device_keys", {}).keys()),
            } if keys.get("device_keys") else None,
        },
    }


def _get_coordinator_state_diagnostics(
    coordinator: SofabatonHubDataUpdateCoordinator,
) -> dict[str, Any]:
    """Get coordinator state diagnostics.
    
    Args:
        coordinator: Data update coordinator
        
    Returns:
        Dictionary containing coordinator state information
    """
    return {
        "last_update_success": coordinator.last_update_success,
        "last_update_time": (
            coordinator.last_update_success_time.isoformat()
            if coordinator.last_update_success_time
            else None
        ),
        "update_interval": (
            coordinator.update_interval.total_seconds()
            if coordinator.update_interval
            else None
        ),
        # Request state information
        "has_basic_data_request": bool(
            getattr(coordinator, "_basic_data_request_state", None)
        ),
        "is_requesting_keys": getattr(coordinator, "_is_requesting_keys", False),
        "sequential_requests_count": len(
            getattr(coordinator, "_sequential_requests", {})
        ),
        # Message processing statistics
        "processed_messages_count": len(
            getattr(coordinator, "_processed_messages", {})
        ),
        "pending_updates_count": len(getattr(coordinator, "_pending_updates", set())),
    }

