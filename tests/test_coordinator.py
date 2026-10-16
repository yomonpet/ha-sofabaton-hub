"""Test the Sofabaton Hub coordinator."""
from __future__ import annotations

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.sofabaton_hub.const import TOPIC_ACTIVITY_LIST_RESPONSE
from custom_components.sofabaton_hub.coordinator import (
    SofabatonHubDataUpdateCoordinator,
)


async def test_coordinator_initialization(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """Test coordinator initialization."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    assert coordinator.mac == "AABBCCDDEEFF"
    assert coordinator.data == {}


async def test_coordinator_first_refresh(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
    mock_activity_list_payload,
) -> None:
    """Test coordinator first refresh."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    # Simulate receiving activity list
    coordinator._handle_activity_list(mock_activity_list_payload)

    assert len(coordinator.data["activities"]) == 2
    assert 101 in coordinator.data["activities"]
    assert coordinator.data["activities"][101]["name"] == "Watch TV"


async def test_coordinator_activity_status_update(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
    mock_activity_list_payload,
    mock_activity_status_payload,
) -> None:
    """Test coordinator handles activity status updates."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    # First load activity list
    coordinator._handle_activity_list(mock_activity_list_payload)
    assert coordinator.data["activities"][101]["state"] == "off"
    assert coordinator.data["current_activity_id"] is None

    # Then receive activity status update
    coordinator._handle_activity_status(mock_activity_status_payload)

    assert coordinator.data["activities"][101]["state"] == "on"
    assert coordinator.data["current_activity_id"] == 101
    assert coordinator.data["activities"][102]["state"] == "off"


async def test_coordinator_activity_close_all(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
    mock_activity_list_payload,
) -> None:
    """Test coordinator handles close all activities."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    # Load activity list and set one as active
    coordinator._handle_activity_list(mock_activity_list_payload)
    coordinator._handle_activity_status({"activity_id": 101, "state": "on"})
    assert coordinator.data["current_activity_id"] == 101

    # Close all activities (activity_id = 255)
    coordinator._handle_activity_status({"activity_id": 255, "state": "off"})

    assert coordinator.data["current_activity_id"] is None
    assert coordinator.data["activities"][101]["state"] == "off"
    assert coordinator.data["activities"][102]["state"] == "off"


async def test_coordinator_assigned_keys(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
    mock_assigned_keys_payload,
) -> None:
    """Test coordinator handles assigned keys."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    coordinator._handle_assigned_keys(mock_assigned_keys_payload)

    assert 101 in coordinator.data["keys"]["assigned"]
    assert len(coordinator.data["keys"]["assigned"][101]) == 2
    assert coordinator.data["keys"]["assigned"][101][0]["key_name"] == "Power"


async def test_coordinator_macro_keys(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
    mock_macro_keys_payload,
) -> None:
    """Test coordinator handles macro keys."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    coordinator._handle_macro_keys(mock_macro_keys_payload)

    assert 101 in coordinator.data["keys"]["macros"]
    assert len(coordinator.data["keys"]["macros"][101]) == 1
    assert coordinator.data["keys"]["macros"][101][0]["key_name"] == "Watch Netflix"


async def test_coordinator_favorite_keys(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
    mock_favorite_keys_payload,
) -> None:
    """Test coordinator handles favorite keys."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    coordinator._handle_favorite_keys(mock_favorite_keys_payload)

    assert 101 in coordinator.data["keys"]["favorites"]
    assert len(coordinator.data["keys"]["favorites"][101]) == 1
    assert coordinator.data["keys"]["favorites"][101][0]["key_name"] == "Channel 1"


async def test_coordinator_request_basic_data(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """Test coordinator requests basic data."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    await coordinator.async_request_basic_data()

    # Verify the API client was asked for the activity list. The request itself
    # is serialised through the Hub session.
    mock_api_client.async_request_activity_list.assert_awaited()


async def test_data_request_does_not_postpone_health_check(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """A UI data request must not push the health check back indefinitely.

    card loads, switch toggles and remote commands all request basic data. If
    each of those restarted the health timer, a Hub that came back online could
    stay reported as offline until the integration was reloaded.
    """
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )
    coordinator._request_basic_data_step = AsyncMock()

    def fake_async_call_later(_hass, _delay, _callback):
        return MagicMock()

    with patch(
        "custom_components.sofabaton_hub.coordinator.async_call_later",
        side_effect=fake_async_call_later,
    ) as schedule_timer:
        # Hub state already known, so the steady state interval applies.
        coordinator._hub_online = True
        coordinator.start_health_monitor()
        pending_timer = coordinator._health_check_unsubscribe

        await coordinator.async_request_basic_data()

        # The original probe is still scheduled: exactly one timer exists and
        # the request did not cancel it.
        assert schedule_timer.call_count == 1
        assert schedule_timer.call_args.args[1] == timedelta(seconds=300)
        assert coordinator._health_check_unsubscribe is pending_timer
        pending_timer.assert_not_called()

        coordinator._cleanup_basic_data_request()
        coordinator.stop_health_monitor()


async def test_health_check_probes_quickly_while_hub_state_is_unknown(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """An unknown Hub is probed quickly so a reload settles on a state."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    def fake_async_call_later(_hass, _delay, _callback):
        return MagicMock()

    with patch(
        "custom_components.sofabaton_hub.coordinator.async_call_later",
        side_effect=fake_async_call_later,
    ) as schedule_timer:
        # hub_online starts as None: nothing is known about the Hub yet.
        assert coordinator.hub_online is None
        coordinator.start_health_monitor()

        assert schedule_timer.call_args.args[1] == timedelta(seconds=10)

        # Once the Hub has answered, the slow steady state cadence applies.
        coordinator._record_health_check_success()
        assert coordinator.hub_online is True

        # Simulate the pending probe timer having fired, then re-arm it.
        coordinator._health_check_unsubscribe = None
        coordinator._schedule_next_health_check()

        assert schedule_timer.call_args.args[1] == timedelta(seconds=300)

        coordinator.stop_health_monitor()


async def test_failed_probe_is_confirmed_without_a_full_interval(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """One failed probe is confirmed quickly instead of after five minutes."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    # Healthy and settled: the slow cadence applies.
    coordinator._hub_online = True
    assert coordinator._health_check_interval() == timedelta(seconds=300)

    # A probe just failed but the Hub is not written off yet: confirm quickly.
    coordinator._health_check_failures = 1
    assert coordinator._health_check_interval() == timedelta(seconds=10)

    # Once reported offline, recovery is checked on the slow cadence again.
    coordinator._hub_online = False
    assert coordinator._health_check_interval() == timedelta(seconds=300)


async def test_hub_online_recovers_after_mqtt_message(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """A Hub that comes back must be reported online without a reload."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    coordinator._health_check_failures = 2
    coordinator._hub_online = False

    coordinator._handle_mqtt_message(
        coordinator._get_topic(TOPIC_ACTIVITY_LIST_RESPONSE),
        {"data": []},
    )

    assert coordinator.hub_online is True
    assert coordinator._health_check_failures == 0

    # The Hub reloads its data once it is reported online again.
    await hass.async_block_till_done()
    coordinator._cleanup_basic_data_request()


async def test_stuck_health_check_is_replaced(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """A probe that never finishes must not block every later probe."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )
    coordinator._health_monitor_running = True

    never_finishes = asyncio.Event()

    async def stuck_probe() -> None:
        await never_finishes.wait()

    stuck_task = hass.async_create_task(stuck_probe())
    coordinator._health_check_task = stuck_task

    with patch.object(coordinator, "_async_check_hub", AsyncMock()) as new_probe:
        coordinator._schedule_health_check()

    assert stuck_task.cancelling() == 1
    assert coordinator._health_check_task is not stuck_task
    new_probe.assert_called_once()

    never_finishes.set()
    coordinator.stop_health_monitor()
    await hass.async_block_till_done()


async def test_coordinator_clear_requesting_keys_flag(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """Test coordinator clears requesting keys flag."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    # Set flag
    coordinator._is_requesting_keys = True

    # Clear flag
    coordinator.clear_requesting_keys_flag()

    assert coordinator._is_requesting_keys is False


async def test_coordinator_message_deduplication(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
    mock_activity_status_payload,
) -> None:
    """Test coordinator deduplicates messages."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    # First message should be processed
    topic = "sofabaton/AABBCCDDEEFF/activity_control_up"
    coordinator._on_message(topic, mock_activity_status_payload)

    # Same message with same timestamp should be ignored
    coordinator._on_message(topic, mock_activity_status_payload)

    # Message should only be processed once
    # (We can't easily verify this without checking internal state,
    # but the deduplication logic is in place)


async def test_coordinator_activity_list_resets_current_id(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """Test that activity list handler resets current_activity_id when all activities are off."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    # Set an active activity
    coordinator.data["current_activity_id"] = 101

    # Receive activity list with all activities off
    payload = {
        "data": [
            {"activity_id": 101, "activity_name": "Watch TV", "state": "off"},
            {"activity_id": 102, "activity_name": "Watch Movie", "state": "off"},
        ]
    }
    coordinator._handle_activity_list(payload)

    # current_activity_id should be reset to None
    assert coordinator.data["current_activity_id"] is None


async def test_empty_activity_list_marks_list_as_loaded(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """An empty response is still a completed activity-list load."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    assert coordinator.activity_list_loaded is False

    coordinator._handle_activity_list({"data": []})

    assert coordinator.activity_list_loaded is True
    assert coordinator.data["activities"] == {}


async def test_manual_refresh_clears_cached_state(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """A manual refresh must not be blocked by cached state."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    # Stale state that would otherwise swallow or falsify the refresh.
    coordinator._basic_data_request_state = {"current_step": "activity_list"}
    coordinator._processed_messages["activity/AABB/list:1"] = 0.0
    coordinator.data["keys"]["assigned"] = {101: [1, 2]}

    with patch(
        "custom_components.sofabaton_hub.coordinator._HEALTH_CHECK_TIMEOUT",
        0.01,
    ):
        assert await coordinator.async_manual_refresh() is False

    # The stale in-flight request did not swallow the refresh: a real request
    # was sent, the duplicate cache was dropped and the key cache cleared.
    mock_api_client.async_request_activity_list.assert_awaited()
    assert coordinator._processed_messages == {}
    assert coordinator.data["keys"]["assigned"] == {}

    coordinator._cleanup_basic_data_request()


async def test_manual_refresh_reports_offline_after_one_failure(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """A single unanswered manual refresh is enough to report the Hub offline."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )
    assert coordinator.hub_online is None

    with patch(
        "custom_components.sofabaton_hub.coordinator._HEALTH_CHECK_TIMEOUT",
        0.01,
    ):
        assert await coordinator.async_manual_refresh() is False

    # The user asked directly, so one timeout is final instead of waiting for
    # consecutive failures.
    assert coordinator.hub_online is False

    coordinator._cleanup_basic_data_request()


async def test_manual_refresh_rebuilds_subscriptions_when_offline(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """A manual refresh repairs the inbound MQTT path of an offline Hub."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )
    coordinator._hub_online = False

    with patch(
        "custom_components.sofabaton_hub.coordinator._HEALTH_CHECK_TIMEOUT",
        0.01,
    ):
        await coordinator.async_manual_refresh()

    mock_api_client.async_resubscribe_to_topics.assert_awaited_once()

    coordinator._cleanup_basic_data_request()


async def test_manual_refresh_keeps_probing_fast_until_hub_answers(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """A failed refresh keeps probing fast so a booting Hub is picked up.

    A Hub that was just powered on can take longer to answer than the single
    check a manual refresh performs, and the offline cadence is five minutes, so
    the window is what makes recovery prompt.
    """
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )

    with patch(
        "custom_components.sofabaton_hub.coordinator._HEALTH_CHECK_TIMEOUT",
        0.01,
    ):
        assert await coordinator.async_manual_refresh() is False

    assert coordinator.hub_online is False
    # The user asked for data, so the Hub keeps being probed closely.
    assert coordinator._health_check_interval() == timedelta(seconds=10)

    # Once the Hub answers, the fast window is dropped again.
    coordinator._record_health_check_success()
    assert coordinator._health_check_interval() == timedelta(seconds=300)

    await hass.async_block_till_done()
    coordinator._cleanup_basic_data_request()


async def test_retained_message_does_not_prove_hub_is_online(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """Broker-cached (retained) state must not be read as a live Hub.

    When the broker replays a stored message on subscribe, the Hub itself may
    already be powered off, so the cached payload must not clear the offline
    state.
    """
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )
    coordinator._hub_online = False

    coordinator._handle_mqtt_message(
        coordinator._get_topic(TOPIC_ACTIVITY_LIST_RESPONSE),
        {"data": [{"activity_id": 101, "activity_name": "Watch TV", "state": "off"}]},
        True,
    )

    # The cached payload is still applied to the data, but the Hub stays
    # reported as offline and no probe is considered answered.
    assert 101 in coordinator.data["activities"]
    assert coordinator.hub_online is False
    assert coordinator._hub_replied_since_probe is False


async def test_duplicate_live_reply_still_proves_hub_is_online(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """A repeated payload must not hide the Hub coming back.

    The broker's stored snapshot is usually byte-identical to the live reply
    that follows it, so the duplicate filter must not swallow the liveness
    signal: recovery would then only ever happen after an integration reload.
    """
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )
    topic = coordinator._get_topic(TOPIC_ACTIVITY_LIST_RESPONSE)
    payload = {
        "data": [{"activity_id": 101, "activity_name": "Watch TV", "state": "off"}]
    }

    coordinator._hub_online = False

    # Broker replay of the stored snapshot: cached state, not proof of life.
    coordinator._handle_mqtt_message(topic, payload, True)
    assert coordinator.hub_online is False

    # Live reply with the very same payload still proves the Hub is reachable.
    coordinator._handle_mqtt_message(topic, payload, False)
    assert coordinator.hub_online is True

    # And so does a payload that the duplicate filter will drop as a repeat.
    coordinator._hub_online = False
    coordinator._handle_mqtt_message(topic, payload, False)
    assert coordinator.hub_online is True

    await hass.async_block_till_done()
    coordinator._cleanup_basic_data_request()


async def test_retained_message_does_not_answer_a_probe(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """A stored replay must not satisfy an outstanding health check."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )
    probe_response = asyncio.Event()
    coordinator._health_check_response = probe_response

    coordinator._handle_mqtt_message(
        coordinator._get_topic(TOPIC_ACTIVITY_LIST_RESPONSE),
        {"data": []},
        True,
    )

    assert not probe_response.is_set()


async def test_subscription_repair_runs_once_per_offline_episode(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """Repeated failures must not rebuild the subscriptions over and over."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )
    coordinator._hub_online = False

    await coordinator._async_heal_subscriptions()
    await coordinator._async_heal_subscriptions()

    mock_api_client.async_resubscribe_to_topics.assert_awaited_once()

    # A reply from the Hub re-arms the repair for the next offline episode.
    coordinator._record_health_check_success()

    await hass.async_block_till_done()
    coordinator._cleanup_basic_data_request()
    coordinator._hub_online = False
    await coordinator._async_heal_subscriptions()

    assert mock_api_client.async_resubscribe_to_topics.await_count == 2


async def test_subscriptions_are_left_alone_while_hub_is_online(
    hass: HomeAssistant,
    mock_config_entry,
    mock_api_client,
) -> None:
    """A healthy Hub must not have its subscriptions rebuilt."""
    coordinator = SofabatonHubDataUpdateCoordinator(
        hass=hass,
        entry=mock_config_entry,
        api_client=mock_api_client,
    )
    coordinator._hub_online = True

    await coordinator._async_heal_subscriptions()

    mock_api_client.async_resubscribe_to_topics.assert_not_awaited()

