"""API client for MQTT communication with Sofabaton Hub."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Callable

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from .const import (
    CONF_MAC,
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
)

_LOGGER = logging.getLogger(__name__)


class SofabatonHubApiClient:
    """API client for MQTT communication with Sofabaton Hub."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the API client.

        Args:
            hass: Home Assistant instance
            entry: Config entry for this integration
        """
        self.hass = hass
        self.entry = entry
        self.mac: str = entry.data[CONF_MAC]
        self._on_message_callback: Callable[[str, dict[str, Any]], None] | None = None
        self._request_lock = asyncio.Lock()

    def set_on_message_callback(self, func: Callable[[str, dict[str, Any]], None]) -> None:
        """Set callback function to be called when MQTT message is received.

        Args:
            func: Callback function that takes topic and payload as arguments
        """
        self._on_message_callback = func

    def _get_topic(self, topic_template: str) -> str:
        """Generate complete topic from template and MAC address.

        Args:
            topic_template: Topic template with {mac} placeholder

        Returns:
            Complete topic with MAC address substituted
        """
        return topic_template.format(mac=self.mac)

    async def _publish(
        self, topic_template: str, payload: dict[str, Any], use_lock: bool = True
    ) -> None:
        """Publish MQTT message.

        Args:
            topic_template: Topic template with {mac} placeholder
            payload: Message payload dictionary
            use_lock: Whether to use request lock for sequential processing
        """

        async def _do_publish() -> None:
            topic = self._get_topic(topic_template)
            message = json.dumps(payload)
            _LOGGER.debug("Publishing to topic '%s': %s", topic, message)
            await mqtt.async_publish(self.hass, topic, message)

            # Add small delay for Hub single-threaded processing
            await asyncio.sleep(0.2)

        if use_lock:
            async with self._request_lock:
                await _do_publish()
        else:
            await _do_publish()

    @callback
    def _message_received(self, msg: mqtt.ReceiveMessage) -> None:
        """Handle received MQTT message.

        Args:
            msg: MQTT message object
        """
        _LOGGER.info("MQTT message received on topic: %s", msg.topic)
        _LOGGER.debug("MQTT payload (raw): %s", msg.payload)

        if self._on_message_callback:
            try:
                # Try to parse payload as JSON
                payload_json = json.loads(msg.payload)
                _LOGGER.debug("MQTT payload (parsed): %s", payload_json)

                # Call callback function set in coordinator, passing topic and parsed payload
                _LOGGER.debug("Calling message callback for topic: %s", msg.topic)
                self._on_message_callback(msg.topic, payload_json)
            except json.JSONDecodeError:
                # Log error if JSON parsing fails
                _LOGGER.error("Failed to decode JSON from payload: %s", msg.payload)
        else:
            _LOGGER.warning("No message callback registered!")

    async def async_subscribe_to_topics(self) -> None:
        """Subscribe to all MQTT topics that need to be monitored."""
        topics_to_subscribe = [
            TOPIC_ACTIVITY_LIST_RESPONSE,
            TOPIC_ACTIVITY_CONTROL_UP,
            # DEVICE_DISABLED: Device functionality temporarily disabled
            # Uncomment below when re-enabling device support
            # TOPIC_DEVICE_LIST_RESPONSE,
            TOPIC_ACTIVITY_KEYS_LIST,
            TOPIC_ACTIVITY_FAVORITES_LIST,
            # DEVICE_DISABLED: Device functionality temporarily disabled
            # Uncomment below when re-enabling device support
            # TOPIC_DEVICE_KEYS_LIST,
            TOPIC_ACTIVITY_MACRO_LIST,
        ]

        for topic_template in topics_to_subscribe:
            topic = self._get_topic(topic_template)
            _LOGGER.info("Subscribing to topic: %s", topic)
            # Subscribe to topic and specify callback function for message arrival
            await mqtt.async_subscribe(self.hass, topic, self._message_received)

    # --- Request publishing methods ---

    async def async_request_activity_list(self) -> None:
        """Publish request to get Activity list."""
        import traceback  # pylint: disable=import-outside-toplevel

        stack_trace = "".join(traceback.format_stack()[-3:-1])
        _LOGGER.debug("ACTIVITY LIST REQUEST - Called from: %s", stack_trace.strip())
        _LOGGER.info("Requesting activity list from Sofabaton Hub %s", self.mac)
        await self._publish(TOPIC_ACTIVITY_LIST_REQUEST, {"data": "activity_list"})

    # DEVICE_DISABLED: Device functionality temporarily disabled
    # Uncomment below when re-enabling device support
    """
    async def async_request_device_list(self) -> None:
        # Publish request to get Device list
        import traceback  # pylint: disable=import-outside-toplevel

        stack_trace = "".join(traceback.format_stack()[-3:-1])
        _LOGGER.debug("DEVICE LIST REQUEST - Called from: %s", stack_trace.strip())
        _LOGGER.info("Requesting device list from Sofabaton Hub %s", self.mac)
        await self._publish(TOPIC_DEVICE_LIST_REQUEST, {"data": "device_list"})
    """

    async def async_request_assigned_keys(self, activity_id: int) -> None:
        """Publish request to get assigned keys for specified Activity.

        Args:
            activity_id: Activity ID to request keys for
        """
        _LOGGER.info("API: Requesting assigned_keys for activity %s", activity_id)
        _LOGGER.debug("API: Will publish to topic: %s", self._get_topic(TOPIC_ACTIVITY_KEYS_REQUEST))
        _LOGGER.debug("API: Expecting response on topic: %s", self._get_topic(TOPIC_ACTIVITY_KEYS_LIST))
        payload = {"data": {"activity_id": activity_id}}
        await self._publish(TOPIC_ACTIVITY_KEYS_REQUEST, payload)

    async def async_request_macro_keys(self, activity_id: int) -> None:
        """Publish request to get macro commands for specified Activity.

        Args:
            activity_id: Activity ID to request keys for
        """
        _LOGGER.info("API: Requesting macro_keys for activity %s", activity_id)
        _LOGGER.debug("API: Will publish to topic: %s", self._get_topic(TOPIC_ACTIVITY_MACRO_REQUEST))
        _LOGGER.debug("API: Expecting response on topic: %s", self._get_topic(TOPIC_ACTIVITY_MACRO_LIST))
        payload = {"data": {"activity_id": activity_id}}
        await self._publish(TOPIC_ACTIVITY_MACRO_REQUEST, payload)

    async def async_request_favorite_keys(self, activity_id: int) -> None:
        """Publish request to get favorite commands for specified Activity.

        Args:
            activity_id: Activity ID to request keys for
        """
        _LOGGER.info("API: Requesting favorite_keys for activity %s", activity_id)
        _LOGGER.debug("API: Will publish to topic: %s", self._get_topic(TOPIC_ACTIVITY_FAVORITES_REQUEST))
        _LOGGER.debug("API: Expecting response on topic: %s", self._get_topic(TOPIC_ACTIVITY_FAVORITES_LIST))
        payload = {"data": {"activity_id": activity_id}}
        await self._publish(TOPIC_ACTIVITY_FAVORITES_REQUEST, payload)

    # DEVICE_DISABLED: Device functionality temporarily disabled
    # Uncomment below when re-enabling device support
    """
    async def async_request_device_keys(self, device_id: int) -> None:
        # Publish request to get command list for specified Device
        payload = {"data": {"device_id": device_id}}
        await self._publish(TOPIC_DEVICE_KEYS_REQUEST, payload)
    """

    # --- Control command publishing methods ---

    async def async_control_activity_state(self, activity_id: int, state: str) -> None:
        """Publish command to control Activity on/off state.

        Args:
            activity_id: Activity ID to control
            state: Desired state ("on" or "off")
        """
        payload = {"data": {"activity_id": activity_id, "state": state}}
        await self._publish(TOPIC_ACTIVITY_CONTROL_DOWN, payload)

    async def async_send_assigned_key(self, activity_id: int, key_id: int) -> None:
        """Publish command to send Activity assigned key.

        Args:
            activity_id: Activity ID
            key_id: Key ID to send
        """
        _LOGGER.info("Sending assigned key: activity_id=%s, key_id=%s", activity_id, key_id)
        payload = {"data": {"activity_id": activity_id, "key_id": key_id}}
        await self._publish(TOPIC_ACTIVITY_ASSIGNED_KEY_CONTROL, payload)
        _LOGGER.debug(
            "Assigned key command published to topic: %s",
            self._get_topic(TOPIC_ACTIVITY_ASSIGNED_KEY_CONTROL),
        )

    async def async_send_macro_key(self, activity_id: int, key_id: int) -> None:
        """Publish command to send Activity macro command.

        Args:
            activity_id: Activity ID
            key_id: Macro key ID to send
        """
        payload = {"data": {"activity_id": activity_id, "key_id": key_id}}
        await self._publish(TOPIC_ACTIVITY_MACRO_KEY_CONTROL, payload)

    async def async_send_favorite_key(self, activity_id: int, key_id: int) -> None:
        """Publish command to send Activity favorite command.

        Args:
            activity_id: Activity ID
            key_id: Favorite key ID to send
        """
        payload = {"data": {"activity_id": activity_id, "key_id": key_id}}
        await self._publish(TOPIC_ACTIVITY_FAVORITES_CONTROL, payload)

    # DEVICE_DISABLED: Device functionality temporarily disabled
    # Uncomment below when re-enabling device support
    """
    async def async_send_device_key(self, device_id: int, key_id: int) -> None:
        # Publish command to send Device command
        payload = {"data": {"device_id": device_id, "key_id": key_id}}
        await self._publish(TOPIC_DEVICE_KEY_CONTROL, payload)
    """
