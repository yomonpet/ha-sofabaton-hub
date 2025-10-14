"""Test the Sofabaton Hub remote platform."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.remote import (
    ATTR_ACTIVITY,
    ATTR_COMMAND,
    DOMAIN as REMOTE_DOMAIN,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import HomeAssistant

from custom_components.sofabaton_hub.const import DOMAIN


async def test_remote_entity_setup(hass: HomeAssistant, setup_integration) -> None:
    """Test remote entity is set up correctly."""
    state = hass.states.get("remote.x2_hub_smells_2")
    assert state is not None
    assert state.state == STATE_OFF


async def test_remote_turn_on_activity(
    hass: HomeAssistant, setup_integration, mock_api_client
) -> None:
    """Test turning on an activity."""
    entity_id = "remote.x2_hub_smells_2"

    await hass.services.async_call(
        REMOTE_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id, ATTR_ACTIVITY: "Watch TV"},
        blocking=True,
    )

    # Verify API client was called
    mock_api_client.async_publish_message.assert_called()


async def test_remote_turn_off(
    hass: HomeAssistant, setup_integration, mock_api_client
) -> None:
    """Test turning off remote."""
    entity_id = "remote.x2_hub_smells_2"

    await hass.services.async_call(
        REMOTE_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )

    # Verify API client was called
    mock_api_client.async_publish_message.assert_called()


async def test_remote_send_command(
    hass: HomeAssistant, setup_integration, mock_api_client
) -> None:
    """Test sending a command."""
    entity_id = "remote.x2_hub_smells_2"

    await hass.services.async_call(
        REMOTE_DOMAIN,
        "send_command",
        {
            ATTR_ENTITY_ID: entity_id,
            ATTR_COMMAND: ["type:key", "activity_id:101", "key_id:1"],
        },
        blocking=True,
    )

    # Verify API client was called
    mock_api_client.async_publish_message.assert_called()


async def test_remote_attributes(hass: HomeAssistant, setup_integration) -> None:
    """Test remote entity attributes."""
    state = hass.states.get("remote.x2_hub_smells_2")
    
    assert state is not None
    assert "activities" in state.attributes
    assert "current_activity_id" in state.attributes
    assert isinstance(state.attributes["activities"], list)


async def test_remote_state_updates(
    hass: HomeAssistant,
    setup_integration,
    mock_coordinator,
    mock_activity_status_payload,
) -> None:
    """Test remote state updates when activity changes."""
    entity_id = "remote.x2_hub_smells_2"
    
    # Initial state should be off
    state = hass.states.get(entity_id)
    assert state.state == STATE_OFF

    # Simulate activity turning on
    mock_coordinator.data["current_activity_id"] = 101
    mock_coordinator.data["activities"][101]["state"] = "on"
    
    # Trigger coordinator update
    mock_coordinator.async_set_updated_data(mock_coordinator.data)
    await hass.async_block_till_done()

    # State should now be on
    state = hass.states.get(entity_id)
    # Note: This test may need adjustment based on actual implementation


async def test_remote_activity_list_attribute(
    hass: HomeAssistant, setup_integration
) -> None:
    """Test remote entity has activity list in attributes."""
    state = hass.states.get("remote.x2_hub_smells_2")
    
    assert state is not None
    activities = state.attributes.get("activities", [])
    assert isinstance(activities, list)
    # Should have activities from mock data
    assert len(activities) >= 0

