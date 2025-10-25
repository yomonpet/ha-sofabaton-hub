"""Support for Sofabaton Hub Activity switches."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sofabaton Activity switches from a config entry.

    This function sets up dynamic switch creation that responds to activity list changes.
    When activities are added or removed in the Sofabaton app, the switches will be
    automatically added or removed in Home Assistant.
    """
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    _LOGGER.info("Setting up Sofabaton Activity switches with dynamic entity management")

    # Dictionary to track created switches: activity_id -> SofabatonActivitySwitch
    created_switches: dict[int, SofabatonActivitySwitch] = {}

    @callback
    def async_add_remove_switches() -> None:
        """Add or remove switches based on activity list changes.

        This callback is triggered whenever the coordinator data is updated.
        It compares the current activity list with the already created switches
        and adds new switches or removes deleted ones.
        """
        # Check if coordinator data is available
        if coordinator.data is None:
            _LOGGER.debug("Coordinator data is None, skipping switch update")
            return

        current_activities = coordinator.data.get("activities", {})
        current_ids = set(current_activities.keys())
        created_ids = set(created_switches.keys())

        # Find newly added activities
        new_ids = current_ids - created_ids
        # Find removed activities
        removed_ids = created_ids - current_ids

        # Create switches for new activities
        if new_ids:
            new_switches = []
            for activity_id in new_ids:
                activity = current_activities[activity_id]
                _LOGGER.info(
                    "Creating new switch for activity: id=%s, name=%s",
                    activity_id,
                    activity.get("name"),
                )
                switch = SofabatonActivitySwitch(
                    coordinator=coordinator,
                    activity_id=activity_id,
                    activity_data=activity,
                )
                created_switches[activity_id] = switch
                new_switches.append(switch)

            if new_switches:
                async_add_entities(new_switches, update_before_add=True)
                _LOGGER.info("Added %d new activity switches", len(new_switches))

        # Remove switches for deleted activities
        if removed_ids:
            for activity_id in removed_ids:
                switch = created_switches.pop(activity_id)
                _LOGGER.info(
                    "Removing switch for deleted activity: id=%s, name=%s",
                    activity_id,
                    switch.name,
                )
                # Remove the entity from Home Assistant
                # The entity will be automatically removed when it's no longer referenced
                # and the coordinator update triggers
                hass.async_create_task(switch.async_remove())

            _LOGGER.info("Removed %d activity switches", len(removed_ids))

    # Register the callback to be called on every coordinator update
    entry.async_on_unload(coordinator.async_add_listener(async_add_remove_switches))

    # Initial creation of switches
    async_add_remove_switches()

    _LOGGER.info(
        "Switch platform setup complete with %d initial switches",
        len(created_switches),
    )


class SofabatonActivitySwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Sofabaton Activity as a Switch."""

    def __init__(
        self,
        coordinator,
        activity_id: int,
        activity_data: dict,
    ) -> None:
        """Initialize the switch.

        Args:
            coordinator: The data coordinator
            activity_id: Activity ID
            activity_data: Activity data dictionary containing name, icon, etc.
        """
        super().__init__(coordinator)
        self._activity_id = activity_id
        self._activity_data = activity_data
        self._attr_name = f"{activity_data.get('name', f'Activity {activity_id}')}"
        self._attr_unique_id = f"sofabaton_{coordinator.mac}_{activity_id}"

        # Enable by default for easier access
        # User can see switches in dashboard and automation editor
        # Uncomment the line below to disable by default:
        # self._attr_entity_registry_enabled_default = False

        _LOGGER.debug(
            "Initialized switch: name=%s, unique_id=%s, activity_id=%s, enabled_by_default=False",
            self._attr_name,
            self._attr_unique_id,
            self._activity_id,
        )

    @property
    def device_info(self):
        """Return device information about this entity.

        Use the same device info as the Remote entity to ensure all entities
        are grouped under the same device with the user-friendly name.
        """
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.unique_id)},
            "name": self.coordinator.entry.title,
            "manufacturer": "Sofabaton",
            "model": "X2 Hub",
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available.

        The switch is available if:
        1. The coordinator has data
        2. The activity still exists in the activity list
        """
        if self.coordinator.data is None:
            return False

        # Check if this activity still exists in the coordinator data
        activities = self.coordinator.data.get("activities", {})
        return self._activity_id in activities

    @property
    def is_on(self) -> bool:
        """Return true if the activity is currently running."""
        # Check if coordinator data is available
        if self.coordinator.data is None:
            _LOGGER.debug(
                "Activity %s (%s) - coordinator data is None",
                self._activity_id,
                self._attr_name,
            )
            return False

        current_activity_id = self.coordinator.data.get("current_activity_id")

        # Get the activity state from activities dict
        activity = self.coordinator.data.get("activities", {}).get(self._activity_id)
        if activity:
            state = activity.get("state")
            is_on = state == "on"
            _LOGGER.debug(
                "Activity %s (%s) state check: current_activity_id=%s, state=%s, is_on=%s",
                self._activity_id,
                self._attr_name,
                current_activity_id,
                state,
                is_on,
            )
            return is_on

        _LOGGER.debug(
            "Activity %s (%s) not found in coordinator data",
            self._activity_id,
            self._attr_name,
        )
        return False

    @property
    def icon(self) -> str:
        """Return the icon for this switch."""
        # Check if coordinator data is available
        if self.coordinator.data is None:
            return "mdi:play-circle-outline"

        # Use activity icon if available, otherwise use default
        activity = self.coordinator.data.get("activities", {}).get(self._activity_id)
        if activity and activity.get("icon"):
            return activity.get("icon")

        # Default icon based on state
        return "mdi:play-circle" if self.is_on else "mdi:play-circle-outline"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        # Check if coordinator data is available
        if self.coordinator.data is None:
            return {}

        activity = self.coordinator.data.get("activities", {}).get(self._activity_id)
        if not activity:
            return {}

        return {
            "activity_id": self._activity_id,
            "activity_name": activity.get("name"),
            "state": activity.get("state"),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the activity (start the activity)."""
        _LOGGER.info(
            "Turning on activity switch: %s (activity_id=%s)",
            self._attr_name,
            self._activity_id,
        )

        try:
            await self.coordinator.api_client.async_start_activity(self._activity_id)
            _LOGGER.info("Successfully sent start command for activity %s", self._activity_id)

            # Request basic data to update activity states
            # This will trigger MQTT request and update the coordinator data
            # Note: If request is already in progress, this will be skipped
            await self.coordinator.async_request_basic_data()

        except Exception as err:
            _LOGGER.error(
                "Error turning on activity %s: %s",
                self._attr_name,
                err,
            )
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the activity (stop the activity)."""
        _LOGGER.info(
            "Turning off activity switch: %s (activity_id=%s)",
            self._attr_name,
            self._activity_id,
        )

        try:
            await self.coordinator.api_client.async_stop_activity(self._activity_id)
            _LOGGER.info("Successfully sent stop command for activity %s", self._activity_id)

            # Request basic data to update activity states
            # This will trigger MQTT request and update the coordinator data
            # Note: If request is already in progress, this will be skipped
            await self.coordinator.async_request_basic_data()

        except Exception as err:
            _LOGGER.error(
                "Error turning off activity %s: %s",
                self._attr_name,
                err,
            )
            raise

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(
            "Coordinator update received for activity switch %s (activity_id=%s)",
            self._attr_name,
            self._activity_id,
        )
        self.async_write_ha_state()

