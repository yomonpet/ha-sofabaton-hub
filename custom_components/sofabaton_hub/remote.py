"""Platform for Sofabaton Hub remote entity."""
from __future__ import annotations

import logging
from typing import Any, Iterable

from homeassistant.components.remote import RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SofabatonHubDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up remote entity from a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry for this integration
        async_add_entities: Callback to add entities
    """
    # Get coordinator instance from hass.data
    coordinator: SofabatonHubDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Create entity and add to HA
    async_add_entities([SofabatonHubRemote(coordinator, entry)])


class SofabatonHubRemote(CoordinatorEntity[SofabatonHubDataUpdateCoordinator], RemoteEntity):
    """Sofabaton Hub Remote entity class."""

    def __init__(
        self,
        coordinator: SofabatonHubDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the remote entity.

        Args:
            coordinator: Data update coordinator
            entry: Config entry for this integration
        """
        super().__init__(coordinator)
        self.entry = entry
        # Set entity unique ID
        self._attr_unique_id = f"{entry.unique_id}_remote"
        # Set entity name
        self._attr_name = entry.title
        # Set entity icon
        self._attr_icon = "mdi:remote"
        # Set device info so entity is associated with correct device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self.entry.unique_id)},
            "name": self.entry.title,
            "manufacturer": "Sofabaton",
            "model": "X2 Hub",
        }
        # Store currently selected activity and device (mainly controlled by frontend card)
        self._selected_activity_id = None
        self._selected_device_id = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("_handle_coordinator_update called - forcing state write")
        # Immediately write state to Home Assistant to ensure frontend receives updates
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool:
        """Return True if any activity is active.

        Returns:
            True if an activity is currently running
        """
        # Check if coordinator.data is None
        if self.coordinator.data is None:
            return False
        return self.coordinator.data.get("current_activity_id") is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes for the entity.

        Frontend cards will retrieve data from here.

        Returns:
            Dictionary of extra state attributes
        """
        data = self.coordinator.data
        # Check if coordinator.data is None
        if data is None:
            _LOGGER.debug("extra_state_attributes: coordinator.data is None")
            return {
                "activities": [],
                # DEVICE_DISABLED: Device functionality temporarily disabled
                # Uncomment below when re-enabling device support
                # "devices": [],
                "current_activity_id": None,
                "assigned_keys": {},
                "macro_keys": {},
                "favorite_keys": {},
                # DEVICE_DISABLED: Device functionality temporarily disabled
                # Uncomment below when re-enabling device support
                # "device_keys": {}
            }

        # Debug logging: print complete data structure
        _LOGGER.debug("extra_state_attributes: coordinator.data keys: %s", data.keys())
        _LOGGER.debug("extra_state_attributes: coordinator.data['keys']: %s", data.get("keys"))

        assigned_keys = data.get("keys", {}).get("assigned", {})
        macro_keys = data.get("keys", {}).get("macros", {})
        favorite_keys = data.get("keys", {}).get("favorites", {})

        _LOGGER.debug("extra_state_attributes: assigned_keys = %s", assigned_keys)
        _LOGGER.debug("extra_state_attributes: macro_keys = %s", macro_keys)
        _LOGGER.debug("extra_state_attributes: favorite_keys = %s", favorite_keys)

        result = {
            "activities": list(data.get("activities", {}).values()),
            # DEVICE_DISABLED: Device functionality temporarily disabled
            # Uncomment below when re-enabling device support
            # "devices": list(data.get("devices", {}).values()),
            "current_activity_id": data.get("current_activity_id"),
            "assigned_keys": assigned_keys,
            "macro_keys": macro_keys,
            "favorite_keys": favorite_keys,
            # DEVICE_DISABLED: Device functionality temporarily disabled
            # Uncomment below when re-enabling device support
            # "device_keys": data.get("keys", {}).get("device_keys", {})
        }

        _LOGGER.debug("extra_state_attributes: returning %s", result)
        return result

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the remote.

        Usually means starting an activity.

        Args:
            **kwargs: Additional arguments
        """
        # HA's turn_on service may not include activity_id, so we just log a warning
        # Actual start operation should be done through custom service or send_command
        _LOGGER.warning(
            "`remote.turn_on` called without an activity. "
            "Please use the custom card to select and start an activity."
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the remote.

        Stops the currently active activity.

        Args:
            **kwargs: Additional arguments
        """
        # Check if coordinator.data is None
        if self.coordinator.data is None:
            return
        current_activity_id = self.coordinator.data.get("current_activity_id")
        if current_activity_id:
            # Send stop command, use 0xFF to stop all
            await self.coordinator.api_client.async_control_activity_state(0xFF, "off")

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send a command to the device.

        Args:
            command: List of command strings in format ["type:action", "id:value"]
            **kwargs: Additional arguments
        """
        _LOGGER.info("Backend: Received send_command request")
        _LOGGER.debug("  command: %s", command)
        _LOGGER.debug("  kwargs: %s", kwargs)

        # command is a list of strings, we parse it to determine what operation to execute
        # Format: ["type:action", "id:value", "extra_id:value"]
        # Example: ["type:start_activity", "activity_id:1"]
        # Example: ["type:send_assigned_key", "activity_id:1", "key_id:5"]

        cmd_dict = {}
        # Parse command list into dictionary
        for item in command:
            try:
                key, value = item.split(":", 1)
                # Try to convert value to integer
                try:
                    cmd_dict[key] = int(value)
                except ValueError:
                    cmd_dict[key] = value  # If not an integer, keep as string
            except ValueError:
                _LOGGER.warning("Invalid command format: %s", item)
                return

        cmd_type = cmd_dict.get("type")  # Get command type
        _LOGGER.info("Backend: Parsed command type: %s", cmd_type)
        _LOGGER.debug("Backend: Parsed command dict: %s", cmd_dict)

        api = self.coordinator.api_client  # Get API client

        # Call different API methods based on command type
        if cmd_type == "start_activity":
            _LOGGER.info("Backend: Starting activity %s", cmd_dict["activity_id"])
            await api.async_control_activity_state(cmd_dict["activity_id"], "on")
        elif cmd_type == "stop_activity":
            _LOGGER.info("Backend: Stopping activity %s", cmd_dict["activity_id"])
            await api.async_control_activity_state(cmd_dict["activity_id"], "off")
        elif cmd_type == "request_assigned_keys":
            # Request assigned_keys (page 1)
            activity_id = cmd_dict.get("activity_id")
            _LOGGER.info("Backend: Requesting assigned_keys for activity %s", activity_id)
            if activity_id:
                await self.coordinator.async_request_assigned_keys(activity_id)
            else:
                _LOGGER.error("Backend: No activity_id provided for request_assigned_keys command")
        elif cmd_type == "request_macro_keys":
            # Request macro_keys (page 2)
            activity_id = cmd_dict.get("activity_id")
            _LOGGER.info("Backend: Requesting macro_keys for activity %s", activity_id)
            if activity_id:
                await self.coordinator.async_request_macro_keys(activity_id)
            else:
                _LOGGER.error("Backend: No activity_id provided for request_macro_keys command")
        elif cmd_type == "request_favorite_keys":
            # Request favorite_keys (page 3)
            activity_id = cmd_dict.get("activity_id")
            _LOGGER.info("Backend: Requesting favorite_keys for activity %s", activity_id)
            if activity_id:
                await self.coordinator.async_request_favorite_keys(activity_id)
            else:
                _LOGGER.error("Backend: No activity_id provided for request_favorite_keys command")
        elif cmd_type == "request_basic_data":
            # Request basic data (activity list and device list)
            await self.coordinator.async_request_basic_data(force_refresh=True)
        elif cmd_type == "clear_requesting_keys_flag":
            # Clear key request flag to allow activity_list updates
            _LOGGER.info("Backend: Clearing _is_requesting_keys flag (detail dialog closed)")
            if hasattr(self.coordinator, "_is_requesting_keys"):
                self.coordinator._is_requesting_keys = False
        # DEVICE_DISABLED: Device functionality temporarily disabled
        # Uncomment below when re-enabling device support
        # elif cmd_type == "request_device_keys":
        #     device_id = cmd_dict.get("device_id")
        #     if device_id:
        #         await api.async_request_device_keys(device_id)
        elif cmd_type == "send_assigned_key":
            _LOGGER.info("Processing send_assigned_key command: %s", cmd_dict)
            await api.async_send_assigned_key(cmd_dict["activity_id"], cmd_dict["key_id"])
        elif cmd_type == "send_macro_key":
            await api.async_send_macro_key(cmd_dict["activity_id"], cmd_dict["key_id"])
        elif cmd_type == "send_favorite_key":
            await api.async_send_favorite_key(cmd_dict["activity_id"], cmd_dict["key_id"])
        # DEVICE_DISABLED: Device functionality temporarily disabled
        # Uncomment below when re-enabling device support
        # elif cmd_type == "send_device_key":
        #     await api.async_send_device_key(cmd_dict["device_id"], cmd_dict["key_id"])
        else:
            _LOGGER.error("Unknown command type received: %s", cmd_type)
