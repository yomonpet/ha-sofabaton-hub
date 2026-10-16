"""Data update coordinator for Sofabaton Hub integration."""
from __future__ import annotations

import asyncio
import copy
import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
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
_HEALTH_CHECK_INTERVAL = timedelta(seconds=300)
# While the Hub has never answered, its state is still unknown. Probe quickly
# so a reload that happens to catch an offline Hub settles on "offline" within
# about a minute instead of after a full five minute interval.
_HEALTH_CHECK_DISCOVERY_INTERVAL = timedelta(seconds=10)
# After an explicit refresh the Hub is expected to answer, so keep probing
# quickly for a while. A Hub that is still booting is then picked up within
# seconds of being ready instead of at the next scheduled interval.
_HEALTH_CHECK_REFRESH_WINDOW = timedelta(seconds=120)
_HEALTH_CHECK_TIMEOUT = 15
_HEALTH_CHECK_FAILURE_LIMIT = 2
# The Hub processes one request at a time, so every exchange is serialised and
# followed by a settle delay before the next one may start.
_HUB_SETTLE_DELAY = 1.0

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

        # Hub connectivity monitor based on activity-list request/response.
        self._hub_online: bool | None = None
        self._activity_list_loaded = False
        self._health_check_failures = 0
        self._health_check_response: asyncio.Event | None = None
        self._health_check_task: asyncio.Task | None = None
        self._health_check_unsubscribe = None
        # Single gate for all Hub traffic: see _hub_session().
        self._hub_lock = asyncio.Lock()
        # True once the Hub answered since the last scheduled probe.
        self._hub_replied_since_probe = False
        # Monotonic deadline until which probes use the fast interval.
        self._fast_probe_until: float | None = None
        self._health_monitor_running = False
        self._subscriptions_healed = False
        self._manual_refresh_lock = asyncio.Lock()

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

    @property
    def hub_online(self) -> bool | None:
        """Return the last known Hub connectivity state."""
        return self._hub_online

    @property
    def activity_list_loaded(self) -> bool:
        """Return whether an activity-list response has been received."""
        return self._activity_list_loaded

    def start_health_monitor(self) -> None:
        """Start Hub reachability checks."""
        if self._health_monitor_running:
            return

        self._health_monitor_running = True
        self._schedule_next_health_check()

    def stop_health_monitor(self) -> None:
        """Stop periodic Hub reachability checks and cancel an active probe."""
        self._health_monitor_running = False
        if self._health_check_unsubscribe is not None:
            self._health_check_unsubscribe()
            self._health_check_unsubscribe = None

        if self._health_check_task is not None:
            self._health_check_task.cancel()
            self._health_check_task = None

    def _health_check_interval(self) -> timedelta:
        """Return how long to wait before the next probe.

        A Hub whose state is not settled yet is probed quickly, so a loss or a
        recovery is reported within about a minute. Once the state is known and
        stable, the slow steady state cadence applies.
        """
        if self._fast_probe_until is not None:
            if time.monotonic() < self._fast_probe_until:
                # An explicit refresh (or a fresh start) asked for the Hub, so
                # keep watching it closely until the window expires.
                return _HEALTH_CHECK_DISCOVERY_INTERVAL
            self._fast_probe_until = None

        if self._hub_online is False:
            # Already reported offline: recover on the normal cadence.
            return _HEALTH_CHECK_INTERVAL

        if self._hub_online is None or self._health_check_failures > 0:
            # Unknown state, or a probe just failed and the Hub is not written
            # off yet: confirm quickly instead of waiting a whole interval.
            return _HEALTH_CHECK_DISCOVERY_INTERVAL

        return _HEALTH_CHECK_INTERVAL

    def _schedule_next_health_check(self) -> None:
        """Ensure the next probe is scheduled.

        The timer is only ever added, never restarted. Data requests from the
        UI therefore cannot postpone (and effectively starve) the health
        monitor, which previously left a Hub that came back online reported as
        offline until the integration was reloaded.
        """
        if not self._health_monitor_running:
            return

        if self._health_check_unsubscribe is None:
            self._health_check_unsubscribe = async_call_later(
                self.hass,
                self._health_check_interval(),
                self._schedule_health_check,
            )

    @asynccontextmanager
    async def _hub_session(self) -> AsyncIterator[None]:
        """Serialise one complete exchange with the Hub.

        The Hub handles a single request at a time, so the whole exchange - not
        just the publish - must be exclusive. A settle delay is held after the
        exchange so back-to-back operations cannot overlap inside the Hub either.

        Yields:
            None while the Hub is exclusively reserved for the caller.
        """
        async with self._hub_lock:
            try:
                yield
            finally:
                await asyncio.sleep(_HUB_SETTLE_DELAY)

    def _clear_cached_state(self) -> None:
        """Drop cached state so an explicit refresh cannot be blocked by it."""
        # A request still marked as in flight would make the refresh a silent
        # no-op, so release it first.
        self._cleanup_basic_data_request()

        # A cached inbound message would be discarded as a duplicate.
        self._processed_messages.clear()

        # Key data is loaded on demand; drop it so it is fetched again.
        self._is_requesting_keys = False
        self._ensure_data_initialized()
        self.data["keys"]["assigned"] = {}
        self.data["keys"]["macros"] = {}
        self.data["keys"]["favorites"] = {}

    async def async_manual_refresh(self) -> bool:
        """Handle an explicit user refresh.

        Cached state is dropped so nothing stale can block the refresh, a
        possibly stale inbound MQTT path is rebuilt, and the Hub is checked once
        straight away. Unlike the periodic monitor, a single unanswered request
        is final here, so the user gets a verdict even when the Hub is off.

        Refreshes are serialised so repeated clicks cannot race each other into
        a wrong offline verdict.

        Returns:
            True when the Hub answered the request.
        """
        async with self._manual_refresh_lock:
            return await self._async_run_manual_refresh()

    def _arm_fast_probe_window(self) -> None:
        """Probe quickly for a while after an explicit user request.

        The Hub may still be booting when the user asks for data, so a single
        short check is not enough. The window is dropped again as soon as the
        Hub answers.
        """
        self._fast_probe_until = (
            time.monotonic() + _HEALTH_CHECK_REFRESH_WINDOW.total_seconds()
        )

        # Drop a pending slow timer so the faster cadence starts now.
        if self._health_check_unsubscribe is not None:
            self._health_check_unsubscribe()
            self._health_check_unsubscribe = None

    async def _async_run_manual_refresh(self) -> bool:
        """Run one explicit Hub check and report the verdict."""
        self._clear_cached_state()
        self._arm_fast_probe_window()

        if self._hub_online is False:
            await self._async_heal_subscriptions(force=True)

        # Never let a probe that is already running race with this check.
        if self._health_check_task is not None and not self._health_check_task.done():
            self._health_check_task.cancel()
            self._health_check_task = None

        response = asyncio.Event()
        self._health_check_response = response

        try:
            async with self._hub_session():
                await asyncio.wait_for(
                    self._async_probe_hub(response),
                    timeout=_HEALTH_CHECK_TIMEOUT,
                )
        except asyncio.TimeoutError:
            self._record_health_check_failure(
                "no activity-list response to manual refresh", definitive=True
            )
            # Rebuild the inbound MQTT path so the next attempt starts clean.
            await self._async_heal_subscriptions(force=True)
            return False
        except asyncio.CancelledError:
            raise
        except Exception as err:  # pylint: disable=broad-except
            self._record_health_check_failure(
                f"manual refresh failed: {err}", definitive=True
            )
            return False
        finally:
            if self._health_check_response is response:
                self._health_check_response = None
            # Keep the periodic monitor scheduled after this explicit check.
            self._schedule_next_health_check()

        _LOGGER.info("Manual refresh for %s reached the Hub", self.mac)
        return True

    async def _async_heal_subscriptions(self, *, force: bool = False) -> None:
        """Rebuild the MQTT subscriptions after the Hub stopped answering."""
        if self._hub_online is not False and not force:
            return

        if self._subscriptions_healed and not force:
            # Only do this once per offline episode; the next successful reply
            # re-arms it.
            return

        self._subscriptions_healed = True
        try:
            await self.api_client.async_resubscribe_to_topics()
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.warning(
                "Failed to refresh MQTT subscriptions for %s: %s", self.mac, err
            )

    @callback
    def _schedule_health_check(self, _now: datetime | None = None) -> None:
        """Start a probe, replacing one that never finished."""
        self._health_check_unsubscribe = None
        if not self._health_monitor_running:
            return

        if self._hub_replied_since_probe:
            # The Hub was heard from since the last probe, so it is reachable and
            # an extra request would only risk colliding with its own work.
            _LOGGER.debug(
                "Hub %s answered since the last check, skipping probe", self.mac
            )
            self._record_health_check_success()
            self._schedule_next_health_check()
            return

        if self._hub_lock.locked():
            # A user operation is talking to the Hub right now; do not queue a
            # probe behind it and risk overlapping inside the Hub.
            _LOGGER.debug("Hub %s is busy, skipping probe", self.mac)
            self._schedule_next_health_check()
            return

        if self._health_check_task is not None and not self._health_check_task.done():
            # A probe that is still around after a whole interval must not be
            # allowed to block every future probe (for example when the MQTT
            # publish never returns). Abandon it and probe again.
            _LOGGER.warning(
                "Previous health check for %s never finished, starting a new one",
                self.mac,
            )
            self._health_check_task.cancel()
            self._health_check_task = None

        self._health_check_task = self.hass.async_create_task(
            self._async_check_hub()
        )

    async def _async_check_hub(self) -> None:
        """Probe the Hub, bounded end to end by the health check timeout."""
        response = asyncio.Event()
        self._health_check_response = response

        try:
            async with self._hub_session():
                await asyncio.wait_for(
                    self._async_probe_hub(response),
                    timeout=_HEALTH_CHECK_TIMEOUT,
                )
        except asyncio.TimeoutError:
            self._record_health_check_failure("no activity-list response")
            # The request went out but nothing came back: also repair the
            # inbound subscription in case only that side is broken.
            await self._async_heal_subscriptions()
        except asyncio.CancelledError:
            raise
        except Exception as err:  # pylint: disable=broad-except
            self._record_health_check_failure(f"request failed: {err}")
        finally:
            if self._health_check_response is response:
                self._health_check_response = None
            if self._health_check_task is asyncio.current_task():
                self._health_check_task = None
            self._schedule_next_health_check()

    async def _async_probe_hub(self, response: asyncio.Event) -> None:
        """Ask the Hub for its activity list and wait for an answer.

        Must run with the Hub session held.

        Args:
            response: Event that the MQTT message handler sets on a Hub reply.
        """
        if self._basic_data_request_state is None:
            await self._async_request_basic_data_locked()
        else:
            # Another request is already talking to the Hub; the firmware
            # handles one request at a time, so reuse it instead of adding a
            # second one. Its answer still proves the Hub is reachable.
            _LOGGER.debug(
                "Health check for %s reuses the in-flight data request", self.mac
            )

        await response.wait()

    def _record_health_check_success(self) -> None:
        """Mark the Hub online after receiving one of its MQTT messages."""
        was_offline = self._hub_online is False
        self._health_check_failures = 0
        self._subscriptions_healed = False
        self._hub_replied_since_probe = True
        self._fast_probe_until = None

        if self._health_check_response is not None:
            self._health_check_response.set()

        if self._hub_online is not True:
            _LOGGER.info("Sofabaton Hub %s is online", self.mac)
            self._hub_online = True
            self.async_set_updated_data(copy.deepcopy(self.data))

        if was_offline:
            # The Hub was power cycled or reconnected while we could not hear
            # it, so its state may have changed behind our back: reload it.
            _LOGGER.info("Sofabaton Hub %s is back, reloading its data", self.mac)
            self.hass.async_create_task(self.async_request_basic_data())

    def _record_health_check_failure(
        self, reason: str, *, definitive: bool = False
    ) -> None:
        """Mark the Hub offline after consecutive unanswered probes.

        Args:
            reason: Why the probe failed.
            definitive: Treat this single failure as final instead of waiting
                for consecutive failures (used for explicit user requests).
        """
        self._health_check_failures += 1
        _LOGGER.debug(
            "Hub health check failed for %s (%d/%d): %s",
            self.mac,
            self._health_check_failures,
            _HEALTH_CHECK_FAILURE_LIMIT,
            reason,
        )

        if not definitive and self._health_check_failures < _HEALTH_CHECK_FAILURE_LIMIT:
            return

        if self._hub_online is False:
            return

        _LOGGER.warning(
            "Sofabaton Hub %s is offline after %d failed health check(s): %s",
            self.mac,
            self._health_check_failures,
            reason,
        )
        self._hub_online = False
        self.async_set_updated_data(copy.deepcopy(self.data))

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

        # Wait for activity list to be populated (with timeout)
        max_wait = 10  # Maximum wait time in seconds
        wait_interval = 0.5  # Check every 0.5 seconds
        elapsed = 0

        while elapsed < max_wait:
            if self.data and self.data.get("activities"):
                _LOGGER.info(
                    "Activity list received for %s (%d activities) after %.1f seconds",
                    self.mac,
                    len(self.data.get("activities", {})),
                    elapsed,
                )
                return

            _LOGGER.debug(
                "Waiting for activity list... (elapsed: %.1fs, data: %s)",
                elapsed,
                "None" if self.data is None else f"activities={len(self.data.get('activities', {}))}",
            )
            await asyncio.sleep(wait_interval)
            elapsed += wait_interval

        _LOGGER.warning(
            "Timeout waiting for activity list for %s (waited %d seconds)",
            self.mac,
            max_wait,
        )

    # Control commands, serialised through the same Hub session as everything
    # else so they can never overlap with a key request or a health check.
    async def async_control_activity_state(self, activity_id: int, state: str) -> None:
        """Send an Activity on/off command to the Hub.

        Args:
            activity_id: Activity ID to control
            state: Desired state ("on" or "off")
        """
        async with self._hub_session():
            await self.api_client.async_control_activity_state(activity_id, state)

    async def async_start_activity(self, activity_id: int) -> None:
        """Start an activity."""
        await self.async_control_activity_state(activity_id, "on")

    async def async_stop_activity(self, activity_id: int) -> None:
        """Stop an activity."""
        await self.async_control_activity_state(activity_id, "off")

    async def async_send_assigned_key(self, activity_id: int, key_id: int) -> None:
        """Send an assigned key press to the Hub."""
        async with self._hub_session():
            await self.api_client.async_send_assigned_key(activity_id, key_id)

    async def async_send_macro_key(self, activity_id: int, key_id: int) -> None:
        """Send a macro key press to the Hub."""
        async with self._hub_session():
            await self.api_client.async_send_macro_key(activity_id, key_id)

    async def async_send_favorite_key(self, device_id: int, key_id: int) -> None:
        """Send a favorite key press to the Hub."""
        async with self._hub_session():
            await self.api_client.async_send_favorite_key(device_id, key_id)

    # Basic data sequential request
    async def async_request_basic_data(self) -> None:
        """Request basic data, serialised against all other Hub traffic.

        Note: DEVICE_DISABLED - currently only requests activity_list
        """
        async with self._hub_session():
            await self._async_request_basic_data_locked()

    async def _async_request_basic_data_locked(self) -> None:
        """Send the basic data request. The Hub session must be held.

        This method will skip the request if one is already in progress to avoid
        duplicate MQTT requests and potential data race conditions.
        """
        # Only check if request is already in progress
        # Skip duplicate requests to avoid MQTT message conflicts
        if self._basic_data_request_state:
            _LOGGER.info(
                "Basic data request already in progress for %s, reusing it", self.mac
            )
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
        if self._hub_online is False:
            # The Hub is already known to be offline, repeating this warning for
            # every request would only flood the log.
            _LOGGER.debug("Basic data request timeout for %s (Hub offline)", self.mac)
        else:
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
        async with self._hub_session():
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
        async with self._hub_session():
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
        async with self._hub_session():
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
            async with self._hub_session():
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
    def _is_duplicate_message(
        self, topic: str, payload: dict, retained: bool = False
    ) -> bool:
        """Check if message is a duplicate.

        Args:
            topic: MQTT topic
            payload: Message payload
            retained: True when the broker replayed a stored message.

        Returns:
            True if message is a duplicate, False otherwise
        """
        if retained:
            # A stored replay is one-shot and is often byte-identical to the
            # live reply that follows it. Recording it would make that live
            # reply look like a duplicate and hide the Hub coming back.
            return False

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
    def _handle_mqtt_message(
        self, topic: str, payload: dict, retained: bool = False
    ) -> None:
        """Handle MQTT message received from API client.

        Args:
            topic: MQTT topic
            payload: Message payload
            retained: True when the broker replayed a stored message instead of
                delivering live Hub traffic. Such a message is cached state and
                must never be taken as proof that the Hub is reachable.
        """
        is_duplicate = False
        try:
            # Message deduplication check
            is_duplicate = self._is_duplicate_message(topic, payload, retained)

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
            if retained:
                # Broker-cached state from a previous session, not a live reply:
                # keep the data but do not conclude the Hub is online.
                _LOGGER.debug(
                    "Ignoring retained %s message for Hub reachability", topic
                )
            else:
                # Marked before the duplicate check below: a repeated payload is
                # not applied twice, but it still proves the Hub is reachable.
                self._record_health_check_success()

            if is_duplicate:
                _LOGGER.debug(
                    "Duplicate payload on %s already applied, reachability kept",
                    topic,
                )
                return

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
        self._activity_list_loaded = True

        # Check if key request is in progress
        # If yes, we need to be careful not to clear keys data
        is_requesting_keys = hasattr(self, "_is_requesting_keys") and self._is_requesting_keys

        if is_requesting_keys:
            _LOGGER.info("Keys request in progress, updating activities without clearing keys data")
            # Preserve existing keys data
            existing_keys = copy.deepcopy(self.data["keys"])

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

        # If key request is in progress, restore keys data before updating state
        if is_requesting_keys:
            _LOGGER.info("Restoring keys data after activity_list update")
            self.data["keys"] = existing_keys

        # Always update Home Assistant state to ensure frontend receives activity changes
        # Even if keys request is in progress, we need to update activity states
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
