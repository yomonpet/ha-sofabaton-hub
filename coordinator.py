"""Data update coordinator for Sofabaton Hub integration."""
from __future__ import annotations

import asyncio
import copy
import logging
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import SofabatonHubApiClient
from .const import (
    CONF_MAC,
    DOMAIN,
    TOPIC_ACTIVITY_ASSIGNED_KEY_CONTROL,
    TOPIC_ACTIVITY_CONTROL_DOWN,
    TOPIC_ACTIVITY_CONTROL_UP,
    TOPIC_ACTIVITY_FAVORITES_CONTROL,
    TOPIC_ACTIVITY_FAVORITES_LIST,
    TOPIC_ACTIVITY_FAVORITES_REQUEST,
    TOPIC_ACTIVITY_KEYS_LIST,
    TOPIC_ACTIVITY_KEYS_REQUEST,
    TOPIC_ACTIVITY_LIST_REQUEST,
    TOPIC_ACTIVITY_LIST_RESPONSE,
    TOPIC_ACTIVITY_MACRO_KEY_CONTROL,
    TOPIC_ACTIVITY_MACRO_LIST,
    TOPIC_ACTIVITY_MACRO_REQUEST,
    TOPIC_DEVICE_KEY_CONTROL,
    TOPIC_DEVICE_KEYS_LIST,
    TOPIC_DEVICE_KEYS_REQUEST,
    TOPIC_DEVICE_LIST_REQUEST,
    TOPIC_DEVICE_LIST_RESPONSE,
)

_LOGGER = logging.getLogger(__name__)

class SofabatonHubDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage and coordinate Sofabaton Hub data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: SofabatonHubApiClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance
            api_client: API client instance for communicating with the hub
            entry: Config entry for this integration
        """
        self.api_client = api_client
        self.entry = entry
        self.mac: str = entry.data[CONF_MAC]

        # Message deduplication mechanism
        self._processed_messages: dict[str, float] = {}  # Message ID -> timestamp
        self._message_cache_duration = 5.0  # Cache messages for 5 seconds

        # Batch update mechanism
        self._pending_updates: set[str] = set()  # Pending update types
        self._update_debounce_timer = None  # Debounce timer
        self._update_debounce_delay = 0.5  # Debounce delay 500ms

        # Sequential request mechanism (activity key data)
        self._sequential_requests: dict[int, dict[str, Any]] = {}  # activity_id -> request state
        self._request_timeouts: dict[int, Any] = {}  # activity_id -> timeout handler

        # Basic data sequential request mechanism
        self._basic_data_request_state = None  # Basic data request state
        self._basic_data_timeout = None  # Basic data request timeout

        # Set MQTT message callback
        self.api_client.set_on_message_callback(self._handle_mqtt_message)

        # Initialize data structure
        self.data: dict[str, Any] = {
            "activities": {},  # activity_id -> {name, id, state}
            "devices": {},  # device_id -> {name, id}
            "current_activity_id": None,  # Current activity ID
            "keys": {
                "assigned": {},  # activity_id -> [key_id, ...]
                "macros": {},  # activity_id -> [{id, name}, ...]
                "favorites": {},  # activity_id -> [{id, name, device_id}, ...]
                "device_keys": {},  # device_id -> [{id, name}, ...]
            },
        }

        # Initialize parent class
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,  # No periodic polling, rely on MQTT push
        )

    def _ensure_data_initialized(self) -> None:
        """Ensure self.data is initialized."""
        if self.data is None:
            self.data = {
                "activities": {},
                "devices": {},
                "current_activity_id": None,
                "keys": {
                    "assigned": {},
                    "macros": {},
                    "favorites": {},
                    "device_keys": {},
                },
            }

    async def _async_update_data(self) -> dict[str, Any]:
        """Periodic data update (using sequential requests).

        Returns:
            Updated data dictionary
        """
        _LOGGER.debug("Coordinator periodic refresh for %s", self.mac)

        # Use sequential request mechanism to get basic data
        await self.async_request_basic_data()

        return self.data

    async def async_config_entry_first_refresh(self) -> None:
        """Special handling for first refresh (using sequential requests)."""
        _LOGGER.info("Starting sequential basic data request for %s", self.mac)

        # Use sequential request mechanism to get basic data
        await self.async_request_basic_data()

    # Basic data sequential request
    async def async_request_basic_data(self, force_refresh: bool = False) -> None:
        """Request basic data sequentially (activity_list → device_list).

        Note: DEVICE_DISABLED - currently only requests activity_list

        Args:
            force_refresh: Force refresh even if request is in progress
        """
        if not force_refresh and self._basic_data_request_state:
            _LOGGER.debug("Basic data request already in progress for %s", self.mac)
            return

        _LOGGER.info("Starting sequential basic data request for %s", self.mac)

        # Initialize sequential request state
        self._basic_data_request_state = {
            "current_step": "activity_list",
            "steps_completed": [],
            "start_time": time.time(),
        }

        # Set timeout handler (15 seconds)
        self._basic_data_timeout = self.hass.loop.call_later(
            15.0,
            self._handle_basic_data_timeout,
        )

        # Start first step: request activity list
        await self._request_basic_data_step("activity_list")

    def _handle_basic_data_timeout(self) -> None:
        """Handle basic data request timeout."""
        _LOGGER.warning("Basic data request timeout for %s", self.mac)
        self._cleanup_basic_data_request()

    def _cleanup_basic_data_request(self) -> None:
        """Clean up basic data request state."""
        if self._basic_data_request_state:
            self._basic_data_request_state = None

        if self._basic_data_timeout:
            try:
                self._basic_data_timeout.cancel()
            except Exception:  # pylint: disable=broad-except
                pass
            self._basic_data_timeout = None

    async def _request_basic_data_step(self, step: str) -> None:
        """Execute basic data request step.

        Args:
            step: Step name to execute
        """
        if not self._basic_data_request_state:
            return

        _LOGGER.debug("Requesting basic data step '%s' for %s", step, self.mac)

        try:
            if step == "activity_list":
                await self.api_client.async_request_activity_list()
            # DEVICE_DISABLED: Device functionality temporarily disabled
            # Uncomment below when re-enabling device support
            # elif step == "device_list":
            #     await self.api_client.async_request_device_list()
            else:
                _LOGGER.error("Unknown basic data step: %s", step)
                self._cleanup_basic_data_request()
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("Error in basic data step '%s' for %s: %s", step, self.mac, err)
            self._cleanup_basic_data_request()

    def _advance_basic_data_request(self, completed_step: str) -> None:
        """Advance basic data sequential request to next step.

        Args:
            completed_step: Name of the step that was just completed
        """
        if not self._basic_data_request_state:
            return

        request_state = self._basic_data_request_state
        request_state["steps_completed"].append(completed_step)

        # Define step sequence
        # DEVICE_DISABLED: Currently only includes activity_list
        # Change to ['activity_list', 'device_list'] when re-enabling device support
        step_sequence = ["activity_list"]

        try:
            current_index = step_sequence.index(completed_step)
            if current_index + 1 < len(step_sequence):
                # More steps remaining
                next_step = step_sequence[current_index + 1]
                request_state["current_step"] = next_step
                _LOGGER.debug("Advancing basic data request to '%s' for %s", next_step, self.mac)

                # Execute next step asynchronously
                asyncio.create_task(self._request_basic_data_step(next_step))
            else:
                # All steps completed
                elapsed = time.time() - request_state["start_time"]
                _LOGGER.info("Basic data request completed for %s in %.2f seconds", self.mac, elapsed)
                self._cleanup_basic_data_request()
        except ValueError:
            _LOGGER.error("Unknown basic data step completed: %s", completed_step)
            self._cleanup_basic_data_request()

    # Request activity key data (on-demand loading, always fetch latest)
    async def async_request_assigned_keys(self, activity_id: int) -> None:
        """Request assigned_keys separately (on-demand loading).

        Args:
            activity_id: Activity ID to request keys for
        """
        _LOGGER.info("Backend: Requesting assigned_keys for activity %s", activity_id)

        # Set flag to prevent activity_list updates from overwriting key data
        self._is_requesting_keys = True
        _LOGGER.debug("Set _is_requesting_keys flag to prevent activity_list interference")

        # Ensure data structure is initialized
        self._ensure_data_initialized()

        # Clear all assigned_keys (only keep data for the activity being requested)
        if self.data["keys"]["assigned"]:
            _LOGGER.debug("Clearing all assigned_keys (had %d activities)", len(self.data["keys"]["assigned"]))
        self.data["keys"]["assigned"] = {}

        # Send MQTT request
        await self.api_client.async_request_assigned_keys(activity_id)
        _LOGGER.debug("Sent MQTT request for assigned_keys, activity %s", activity_id)

    async def async_request_macro_keys(self, activity_id: int) -> None:
        """Request macro_keys separately (on-demand loading).

        Args:
            activity_id: Activity ID to request keys for
        """
        _LOGGER.info("Backend: Requesting macro_keys for activity %s", activity_id)

        # Set flag to prevent activity_list updates from overwriting key data
        self._is_requesting_keys = True
        _LOGGER.debug("Set _is_requesting_keys flag to prevent activity_list interference")

        # Ensure data structure is initialized
        self._ensure_data_initialized()

        # Clear all macro_keys (only keep data for the activity being requested)
        if self.data["keys"]["macros"]:
            _LOGGER.debug("Clearing all macro_keys (had %d activities)", len(self.data["keys"]["macros"]))
        self.data["keys"]["macros"] = {}

        # Send MQTT request
        await self.api_client.async_request_macro_keys(activity_id)
        _LOGGER.debug("Sent MQTT request for macro_keys, activity %s", activity_id)

    async def async_request_favorite_keys(self, activity_id: int) -> None:
        """Request favorite_keys separately (on-demand loading).

        Args:
            activity_id: Activity ID to request keys for
        """
        _LOGGER.info("Backend: Requesting favorite_keys for activity %s", activity_id)

        # Set flag to prevent activity_list updates from overwriting key data
        self._is_requesting_keys = True
        _LOGGER.debug("Set _is_requesting_keys flag to prevent activity_list interference")

        # Ensure data structure is initialized
        self._ensure_data_initialized()

        # Clear all favorite_keys (only keep data for the activity being requested)
        if self.data["keys"]["favorites"]:
            _LOGGER.debug("Clearing all favorite_keys (had %d activities)", len(self.data["keys"]["favorites"]))
        self.data["keys"]["favorites"] = {}

        # Send MQTT request
        await self.api_client.async_request_favorite_keys(activity_id)
        _LOGGER.debug("Sent MQTT request for favorite_keys, activity %s", activity_id)

    def _handle_request_timeout(self, activity_id: int) -> None:
        """Handle request timeout.

        Args:
            activity_id: Activity ID that timed out
        """
        _LOGGER.warning("Sequential request timeout for activity %s", activity_id)
        self._cleanup_sequential_request(activity_id)

    def _cleanup_sequential_request(self, activity_id: int) -> None:
        """Clean up sequential request state.

        Args:
            activity_id: Activity ID to clean up
        """
        if activity_id in self._sequential_requests:
            del self._sequential_requests[activity_id]

        if activity_id in self._request_timeouts:
            try:
                self._request_timeouts[activity_id].cancel()
            except Exception:  # pylint: disable=broad-except
                pass
            del self._request_timeouts[activity_id]

        # Clear key request flag to allow activity_list updates
        if hasattr(self, "_is_requesting_keys"):
            self._is_requesting_keys = False
            _LOGGER.debug("Cleared _is_requesting_keys flag, activity_list updates allowed")

    async def _request_next_step(self, activity_id: int) -> None:
        """Execute next request step.

        Args:
            activity_id: Activity ID to request next step for
        """
        if activity_id not in self._sequential_requests:
            _LOGGER.debug("_request_next_step: activity %s not in sequential requests", activity_id)
            return

        request_state = self._sequential_requests[activity_id]
        current_step = request_state["current_step"]

        _LOGGER.debug("Requesting step '%s' for activity %s", current_step, activity_id)

        try:
            if current_step == "assigned_keys":
                _LOGGER.debug("Sending MQTT request for assigned_keys, activity %s", activity_id)
                await self.api_client.async_request_assigned_keys(activity_id)
            elif current_step == "macro_keys":
                _LOGGER.debug("Sending MQTT request for macro_keys, activity %s", activity_id)
                await self.api_client.async_request_macro_keys(activity_id)
            elif current_step == "favorite_keys":
                _LOGGER.debug("Sending MQTT request for favorite_keys, activity %s", activity_id)
                await self.api_client.async_request_favorite_keys(activity_id)
            else:
                _LOGGER.error("Unknown request step: %s", current_step)
                self._cleanup_sequential_request(activity_id)
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("Error in request step '%s' for activity %s: %s", current_step, activity_id, err)
            self._cleanup_sequential_request(activity_id)

    def _advance_sequential_request(self, activity_id: int, completed_step: str) -> None:
        """Advance sequential request to next step.

        Args:
            activity_id: Activity ID to advance
            completed_step: Name of the step that was just completed
        """
        _LOGGER.debug("_advance_sequential_request called: activity_id=%s, completed_step=%s", activity_id, completed_step)
        _LOGGER.debug("Current sequential requests: %s", list(self._sequential_requests.keys()))

        if activity_id not in self._sequential_requests:
            _LOGGER.warning("Activity %s not in sequential requests! Cannot advance from step '%s'", activity_id, completed_step)
            _LOGGER.debug("Available activities in sequential requests: %s", list(self._sequential_requests.keys()))
            return

        request_state = self._sequential_requests[activity_id]
        _LOGGER.debug("Current request state before advancing: %s", request_state)
        request_state["steps_completed"].append(completed_step)

        # Define step sequence
        step_sequence = ["assigned_keys", "macro_keys", "favorite_keys"]

        try:
            current_index = step_sequence.index(completed_step)
            if current_index + 1 < len(step_sequence):
                # More steps remaining
                next_step = step_sequence[current_index + 1]
                request_state["current_step"] = next_step
                _LOGGER.debug("Advancing to next step '%s' for activity %s", next_step, activity_id)

                # Execute next step asynchronously (avoid blocking current message processing)
                asyncio.create_task(self._request_next_step(activity_id))
            else:
                # All steps completed
                elapsed = time.time() - request_state["start_time"]
                _LOGGER.info("Sequential request completed for activity %s in %.2f seconds", activity_id, elapsed)
                self._cleanup_sequential_request(activity_id)
        except ValueError:
            _LOGGER.error("Unknown completed step: %s", completed_step)
            self._cleanup_sequential_request(activity_id)

    # Message deduplication check
    def _is_duplicate_message(self, topic: str, payload: dict) -> bool:
        """Check if message is a duplicate.

        Args:
            topic: MQTT topic
            payload: Message payload

        Returns:
            True if message is a duplicate, False otherwise
        """
        # Generate unique message identifier
        message_id = f"{topic}:{hash(str(payload))}"
        current_time = time.time()

        # Clean up expired message records
        expired_keys = [
            key
            for key, timestamp in self._processed_messages.items()
            if current_time - timestamp > self._message_cache_duration
        ]
        for key in expired_keys:
            del self._processed_messages[key]

        # Check if message is duplicate
        if message_id in self._processed_messages:
            _LOGGER.debug("Duplicate message detected for topic %s, ignoring", topic)
            return True

        # Record new message
        self._processed_messages[message_id] = current_time
        return False

    # Batch update debouncing
    @callback
    def _schedule_debounced_update(self, update_type: str) -> None:
        """Schedule debounced update.

        Args:
            update_type: Type of update to schedule
        """
        self._pending_updates.add(update_type)

        # Cancel previous timer
        if self._update_debounce_timer:
            self._update_debounce_timer.cancel()

        # Create new timer
        self._update_debounce_timer = self.hass.loop.call_later(
            self._update_debounce_delay, self._execute_debounced_update
        )

    @callback
    def _execute_debounced_update(self) -> None:
        """Execute batch update."""
        if self._pending_updates:
            _LOGGER.debug("Executing debounced update for types: %s", self._pending_updates)
            self._pending_updates.clear()
            self._update_debounce_timer = None
            self.async_set_updated_data(self.data)

    @callback
    def _handle_mqtt_message(self, topic: str, payload: dict) -> None:
        """Handle MQTT message received from API client.

        Args:
            topic: MQTT topic
            payload: Message payload
        """
        try:
            # Message deduplication check
            if self._is_duplicate_message(topic, payload):
                return

            _LOGGER.debug("Processing unique message on topic '%s'", topic)

            # Validate payload
            if not isinstance(payload, dict):
                _LOGGER.warning("Invalid payload format for topic %s: %s", topic, payload)
                return

        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error("Error in MQTT message handling: %s", err)
            return

        # Dispatch to different handler functions based on topic
        topic_map = {
            self._get_topic(TOPIC_ACTIVITY_LIST_RESPONSE): ("activity_list", self._handle_activity_list, False),  # Immediate update to avoid overwriting key data
            self._get_topic(TOPIC_ACTIVITY_CONTROL_UP): ("activity_status", self._handle_activity_status, False),  # Immediate update for real-time activity status
            # DEVICE_DISABLED: Device functionality temporarily disabled
            # Uncomment below when re-enabling device support
            # self._get_topic(TOPIC_DEVICE_LIST_RESPONSE): ("device_list", self._handle_device_list, True),  # Use debounce
            self._get_topic(TOPIC_ACTIVITY_KEYS_LIST): ("assigned_keys", self._handle_assigned_keys, False),  # Immediate update, no debounce
            self._get_topic(TOPIC_ACTIVITY_MACRO_LIST): ("macro_keys", self._handle_macro_keys, False),  # Immediate update, no debounce
            self._get_topic(TOPIC_ACTIVITY_FAVORITES_LIST): ("favorite_keys", self._handle_favorite_keys, False),  # Immediate update, no debounce
            # DEVICE_DISABLED: Device functionality temporarily disabled
            # Uncomment below when re-enabling device support
            # self._get_topic(TOPIC_DEVICE_KEYS_LIST): ("device_keys", self._handle_device_keys, False),  # Immediate update, no debounce
        }

        handler_info = topic_map.get(topic)
        if handler_info:
            update_type, handler, use_debounce = handler_info
            handler(payload)
            # Only use debounce update mechanism for messages that need it
            if use_debounce:
                self._schedule_debounced_update(update_type)
        else:
            _LOGGER.warning("Unhandled MQTT topic: %s", topic)

    def _get_topic(self, topic_template: str) -> str:
        """Generate complete topic from template.

        Args:
            topic_template: Topic template with {mac} placeholder

        Returns:
            Complete topic with MAC address substituted
        """
        return topic_template.format(mac=self.mac)

    # --- Message handler functions ---

    def _handle_activity_list(self, payload: dict) -> None:
        """Handle Activity list response.

        Args:
            payload: MQTT message payload
        """
        activities = payload.get("data", [])
        _LOGGER.info("Received activity list for %s: %d activities", self.mac, len(activities))
        _LOGGER.debug("Raw activity list data: %s", activities)

        # Ensure self.data is initialized
        self._ensure_data_initialized()

        self.data["activities"].clear()  # Clear old data

        # Reset current_activity_id, will be set if any activity is on
        self.data["current_activity_id"] = None

        for activity in activities:
            activity_id = activity.get("activity_id")
            if activity_id is not None:
                self.data["activities"][activity_id] = {
                    "id": activity_id,
                    "name": activity.get("activity_name"),
                    "state": activity.get("state", "off"),
                }
                # If this activity is on, update current activity ID
                if activity.get("state") == "on":
                    self.data["current_activity_id"] = activity_id
        _LOGGER.debug("Updated activities: %s", self.data["activities"])
        _LOGGER.debug("Current activity ID: %s", self.data["current_activity_id"])

        # Trigger next step of basic data sequential request
        self._advance_basic_data_request("activity_list")

        # Check if key request is in progress, defer update to avoid overwriting key data
        if hasattr(self, "_is_requesting_keys") and self._is_requesting_keys:
            _LOGGER.info("Keys request in progress, deferring activity_list state update to avoid data race")
            # Don't update state immediately, wait for key request to complete
            # Key data will include latest activities data in _handle_favorite_keys
            return

        # Immediately update Home Assistant state to avoid debounce delay overwriting key data
        data_copy = copy.deepcopy(self.data)
        _LOGGER.info("Sending data update to Home Assistant (activity_list)")
        _LOGGER.debug(
            "Data snapshot: activities=%d, assigned_keys=%s, macro_keys=%s, favorite_keys=%s",
            len(data_copy["activities"]),
            list(data_copy["keys"]["assigned"].keys()),
            list(data_copy["keys"]["macros"].keys()),
            list(data_copy["keys"]["favorites"].keys()),
        )
        self.async_set_updated_data(data_copy)

    def _handle_activity_status(self, payload: dict) -> None:
        """Handle Activity status update.

        Args:
            payload: MQTT message payload
        """
        activity_id = payload.get("activity_id")
        state = payload.get("state")

        _LOGGER.info(
            "Received activity status update for %s: activity_id=%s, state=%s, full_payload=%s",
            self.mac,
            activity_id,
            state,
            payload,
        )

        # Ensure self.data is initialized
        self._ensure_data_initialized()

        # Handle Activity status according to MCU return rules
        if activity_id == 0xFF or activity_id == 255:
            # ID 255 means close all activities (off button pressed)
            _LOGGER.info("Received close all activities command (activity_id=255)")
            self.data["current_activity_id"] = None
            for act_id in self.data["activities"]:
                self.data["activities"][act_id]["state"] = "off"
        elif activity_id is not None and state == "on":
            # Switch activity: close others, open specified one
            _LOGGER.info("Switching to activity %s, closing all others", activity_id)
            # Close all other activities
            for act_id in self.data["activities"]:
                self.data["activities"][act_id]["state"] = "off"
            # Open specified activity
            if activity_id in self.data["activities"]:
                self.data["activities"][activity_id]["state"] = "on"
                self.data["current_activity_id"] = activity_id
            else:
                _LOGGER.warning("Received unknown activity_id: %s", activity_id)
        elif activity_id is not None and state == "off":
            # Individual activity closed (rare case)
            _LOGGER.info("Individual activity %s turned off", activity_id)
            if activity_id in self.data["activities"]:
                self.data["activities"][activity_id]["state"] = "off"
                # If closing current activity, clear current_activity_id
                if self.data["current_activity_id"] == activity_id:
                    self.data["current_activity_id"] = None
        else:
            _LOGGER.warning("Unhandled activity status: activity_id=%s, state=%s", activity_id, state)

        # Immediately update Home Assistant state to ensure frontend receives activity status changes in real-time
        data_copy = copy.deepcopy(self.data)
        _LOGGER.info("Sending data update to Home Assistant (activity_status)")
        self.async_set_updated_data(data_copy)

    # DEVICE_DISABLED: Device functionality temporarily disabled
    # Uncomment below when re-enabling device support
    """
    def _handle_device_list(self, payload: dict) -> None:
        # Handle Device list response
        devices = payload.get("data", [])
        _LOGGER.info("Received device list for %s: %d devices", self.mac, len(devices))

        # Ensure self.data is initialized
        self._ensure_data_initialized()

        self.data["devices"].clear()
        for device in devices:
            device_id = device.get("device_id")
            if device_id is not None:
                self.data["devices"][device_id] = {
                    "id": device_id,
                    "name": device.get("device_name"),
                }
        _LOGGER.debug("Updated devices: %s", self.data["devices"])

        # Trigger next step of basic data sequential request (device_list is last step)
        self._advance_basic_data_request("device_list")
    """

    def _handle_assigned_keys(self, payload: dict) -> None:
        """Handle assigned keys list.

        Args:
            payload: MQTT message payload
        """
        _LOGGER.info("Received assigned_keys response from MQTT")
        _LOGGER.debug("Payload: %s", payload)

        activity_id = payload.get("activity_id")
        keys = payload.get("data", [])

        # Ensure self.data is initialized
        self._ensure_data_initialized()

        if activity_id is not None:
            self.data["keys"]["assigned"][activity_id] = [key.get("key_id") for key in keys]
            _LOGGER.info("Updated assigned keys for activity %s: %d keys", activity_id, len(self.data["keys"]["assigned"][activity_id]))

            # Immediately update Home Assistant state
            data_copy = copy.deepcopy(self.data)
            _LOGGER.debug("Sending data update to Home Assistant (assigned_keys)")
            self.async_set_updated_data(data_copy)

    def _handle_macro_keys(self, payload: dict) -> None:
        """Handle macro command list.

        Args:
            payload: MQTT message payload
        """
        _LOGGER.info("Received macro_keys response from MQTT")
        _LOGGER.debug("Payload: %s", payload)

        activity_id = payload.get("activity_id")
        keys = payload.get("data", [])

        # Ensure self.data is initialized
        self._ensure_data_initialized()

        if activity_id is not None:
            self.data["keys"]["macros"][activity_id] = [
                {"id": k.get("key_id"), "name": k.get("key_name")} for k in keys
            ]
            _LOGGER.info(
                "Updated macro keys for activity %s: %d keys",
                activity_id,
                len(self.data["keys"]["macros"][activity_id]),
            )

            # Immediately update Home Assistant state
            data_copy = copy.deepcopy(self.data)
            _LOGGER.debug("Sending data update to Home Assistant (macro_keys)")
            self.async_set_updated_data(data_copy)

    def _handle_favorite_keys(self, payload: dict) -> None:
        """Handle favorite command list.

        Args:
            payload: MQTT message payload
        """
        _LOGGER.info("Received favorite_keys response from MQTT")
        _LOGGER.debug("Payload: %s", payload)

        activity_id = payload.get("activity_id")
        keys = payload.get("data", [])

        # Ensure self.data is initialized
        self._ensure_data_initialized()

        if activity_id is not None:
            self.data["keys"]["favorites"][activity_id] = [
                {"id": k.get("key_id"), "name": k.get("key_name"), "device_id": k.get("device_id")}
                for k in keys
            ]
            _LOGGER.info(
                "Updated favorite keys for activity %s: %d keys",
                activity_id,
                len(self.data["keys"]["favorites"][activity_id]),
            )

            # Immediately update Home Assistant state
            data_copy = copy.deepcopy(self.data)
            _LOGGER.debug("Sending data update to Home Assistant (favorite_keys)")
            self.async_set_updated_data(data_copy)

    # DEVICE_DISABLED: Device functionality temporarily disabled
    # Uncomment below when re-enabling device support
    """
    def _handle_device_keys(self, payload: dict) -> None:
        # Handle device command list
        device_id = payload.get("device_id")
        keys = payload.get("data", [])

        # Ensure self.data is initialized
        self._ensure_data_initialized()

        if device_id is not None:
            self.data["keys"]["device_keys"][device_id] = [
                {"id": k.get("key_id"), "name": k.get("key_name")} for k in keys
            ]
            _LOGGER.debug("Updated keys for device %s", device_id)
    """
