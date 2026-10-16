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
    TOPIC_SUBSCRIPTION_BARRIER,
)

_LOGGER = logging.getLogger(__name__)

# How long to wait for the broker to activate our subscriptions.
_SUBSCRIPTION_BARRIER_TIMEOUT = 2.0
# The barrier is retried: the first publish can still be sent before the broker
# has processed the matching subscribe.
_SUBSCRIPTION_BARRIER_ATTEMPTS = 3
_SUBSCRIPTION_BARRIER_RETRY_DELAY = 1.0


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
        self._on_message_callback: Callable[[str, dict[str, Any], bool], None] | None = None
        self._unsubscribe_callbacks: list[Callable[[], None]] = []
        self._barrier_unsubscribe: Callable[[], None] | None = None
        self._barrier_topic: str | None = None
        self._barrier_received: asyncio.Event | None = None

    def set_on_message_callback(
        self, func: Callable[[str, dict[str, Any], bool], None]
    ) -> None:
        """Set callback function to be called when MQTT message is received.

        Args:
            func: Callback function receiving (topic, payload, retained).
                ``retained`` is True when the broker replayed a stored message
                instead of delivering live traffic.
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

    async def _publish(self, topic_template: str, payload: dict[str, Any]) -> None:
        """Publish one MQTT message.

        Callers must serialise Hub traffic themselves: the Hub answers one
        request at a time, so coordination lives in the coordinator's Hub
        session rather than here.

        Args:
            topic_template: Topic template with {mac} placeholder
            payload: Message payload dictionary
        """
        topic = self._get_topic(topic_template)
        message = json.dumps(payload)
        _LOGGER.debug("Publishing to topic '%s': %s", topic, message)
        await mqtt.async_publish(self.hass, topic, message)

    @callback
    def _message_received(self, msg: mqtt.ReceiveMessage) -> None:
        """Handle received MQTT message.

        Args:
            msg: MQTT message object
        """
        _LOGGER.info(
            "MQTT message received on topic: %s (retained=%s)", msg.topic, msg.retain
        )
        _LOGGER.debug("MQTT payload (raw): %s", msg.payload)

        if msg.topic == self._barrier_topic:
            # Our own subscription barrier came back, which proves the broker has
            # our subscriptions active. This is not Hub traffic.
            if self._barrier_received is not None:
                self._barrier_received.set()
            return

        if self._on_message_callback:
            try:
                # Try to parse payload as JSON
                payload_json = json.loads(msg.payload)
                _LOGGER.debug("MQTT payload (parsed): %s", payload_json)

                # Call callback function set in coordinator, passing topic,
                # parsed payload and whether the broker replayed a stored
                # message (retained) rather than delivering live Hub traffic.
                _LOGGER.debug("Calling message callback for topic: %s", msg.topic)
                self._on_message_callback(msg.topic, payload_json, bool(msg.retain))
            except json.JSONDecodeError:
                # Log error if JSON parsing fails
                _LOGGER.error("Failed to decode JSON from payload: %s", msg.payload)
        else:
            _LOGGER.warning("No message callback registered!")

    async def async_subscribe_to_topics(self) -> None:
        """Subscribe to all MQTT topics that need to be monitored."""
        if self._unsubscribe_callbacks:
            _LOGGER.debug("MQTT topics are already subscribed for %s", self.mac)
            return

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
            unsubscribe = await mqtt.async_subscribe(self.hass, topic, self._message_received)
            self._unsubscribe_callbacks.append(unsubscribe)

        # Private topic in a namespace the Hub does not use; it only exists so
        # async_verify_subscriptions() can prove the round trip through the
        # broker works before we rely on any reply.
        barrier_topic = self._get_topic(TOPIC_SUBSCRIPTION_BARRIER)
        _LOGGER.debug("Subscribing to barrier topic: %s", barrier_topic)
        self._barrier_unsubscribe = await mqtt.async_subscribe(
            self.hass, barrier_topic, self._message_received
        )

    async def async_verify_subscriptions(self) -> bool:
        """Verify the broker has activated our subscriptions.

        Home Assistant registers subscriptions locally before the broker has
        necessarily processed them, so a reply sent immediately after startup
        can be lost. Publishing to the barrier topic and receiving our own
        message back proves the round trip works.

        The topic lives inside the Hub's own namespace because that namespace is
        proven publishable with the configured broker credentials, while a
        private top level namespace can be rejected by broker ACLs. Unlike the
        original barrier this message is not retained, so nothing is left behind
        on the broker and the Hub itself is never asked to do anything.

        Returns:
            True when the round trip succeeded.
        """
        barrier_topic = self._get_topic(TOPIC_SUBSCRIPTION_BARRIER)
        received = asyncio.Event()
        self._barrier_topic = barrier_topic
        self._barrier_received = received

        verified = False
        try:
            for attempt in range(1, _SUBSCRIPTION_BARRIER_ATTEMPTS + 1):
                if attempt > 1:
                    await asyncio.sleep(_SUBSCRIPTION_BARRIER_RETRY_DELAY)

                await mqtt.async_publish(
                    self.hass, barrier_topic, json.dumps({"status": "ready"})
                )

                try:
                    await asyncio.wait_for(
                        received.wait(), timeout=_SUBSCRIPTION_BARRIER_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    _LOGGER.warning(
                        "MQTT subscription barrier timed out for %s on %s (%d/%d)",
                        self.mac,
                        barrier_topic,
                        attempt,
                        _SUBSCRIPTION_BARRIER_ATTEMPTS,
                    )
                    continue

                verified = True
                break
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.error(
                "MQTT subscription barrier failed for %s: %s", self.mac, err
            )
            return False
        finally:
            self._barrier_topic = None
            self._barrier_received = None
            self._drop_barrier_subscription()

        if not verified:
            return False

        _LOGGER.info("MQTT subscriptions verified for %s", self.mac)
        return True

    def _drop_barrier_subscription(self) -> None:
        """Remove the temporary barrier subscription."""
        if self._barrier_unsubscribe is None:
            return

        try:
            self._barrier_unsubscribe()
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("Failed to unsubscribe barrier topic for %s", self.mac)
        self._barrier_unsubscribe = None

    async def async_resubscribe_to_topics(self) -> bool:
        """Re-establish MQTT subscriptions and confirm the broker took them.

        Outbound requests can keep working while the inbound subscription stops
        delivering, which makes a Hub that is actually online look offline until
        the integration is reloaded. Re-subscribing restores the callback path
        without a reload.

        The subscriptions must be verified again afterwards. A request sent
        immediately after subscribing can have its reply dropped by the broker
        before the subscription is active, which is the same race the startup
        barrier exists to prevent.

        Returns:
            True when the subscriptions are confirmed active again.
        """
        _LOGGER.info("Refreshing MQTT subscriptions for %s", self.mac)
        await self.async_unsubscribe_from_topics()
        await self.async_subscribe_to_topics()

        if await self.async_verify_subscriptions():
            return True

        _LOGGER.warning(
            "MQTT subscriptions could not be verified for %s after refreshing",
            self.mac,
        )
        return False

    async def async_unsubscribe_from_topics(self) -> None:
        """Remove MQTT subscriptions created by this API client."""
        self._drop_barrier_subscription()

        unsubscribe_callbacks = self._unsubscribe_callbacks
        self._unsubscribe_callbacks = []

        for unsubscribe in unsubscribe_callbacks:
            try:
                unsubscribe()
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Failed to unsubscribe MQTT topic for %s", self.mac)

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

    async def async_start_activity(self, activity_id: int) -> None:
        """Start an activity (convenience wrapper for switch entity).

        Args:
            activity_id: Activity ID to start
        """
        _LOGGER.info("Starting activity %s", activity_id)
        await self.async_control_activity_state(activity_id, "on")

    async def async_stop_activity(self, activity_id: int) -> None:
        """Stop an activity (convenience wrapper for switch entity).

        Args:
            activity_id: Activity ID to stop
        """
        _LOGGER.info("Stopping activity %s", activity_id)
        await self.async_control_activity_state(activity_id, "off")

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

    async def async_send_favorite_key(self, device_id: int, key_id: int) -> None:
        """Publish command to send Activity favorite command.

        Note: Due to firmware design issue, the device expects device_id in the
        activity_id field for favorite key control commands.

        Args:
            device_id: Device ID (will be sent as activity_id due to firmware issue)
            key_id: Favorite key ID to send
        """
        # Firmware expects device_id in activity_id field
        payload = {"data": {"activity_id": device_id, "key_id": key_id}}
        await self._publish(TOPIC_ACTIVITY_FAVORITES_CONTROL, payload)

    # DEVICE_DISABLED: Device functionality temporarily disabled
    # Uncomment below when re-enabling device support
    """
    async def async_send_device_key(self, device_id: int, key_id: int) -> None:
        # Publish command to send Device command
        payload = {"data": {"device_id": device_id, "key_id": key_id}}
        await self._publish(TOPIC_DEVICE_KEY_CONTROL, payload)
    """
