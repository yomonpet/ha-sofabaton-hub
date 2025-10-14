"""Test the Sofabaton Hub integration initialization."""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.sofabaton_hub.const import DOMAIN


async def test_setup_entry(hass: HomeAssistant, setup_integration) -> None:
    """Test successful setup of config entry."""
    # Verify the integration is loaded
    assert DOMAIN in hass.data
    
    # Verify config entry is loaded
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    assert entries[0].state == ConfigEntryState.LOADED


async def test_unload_entry(
    hass: HomeAssistant,
    mock_config_entry,
    mock_mqtt_client,
    mock_api_client,
) -> None:
    """Test successful unload of config entry."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.sofabaton_hub.coordinator.SofabatonHubAPI",
        return_value=mock_api_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Verify entry is loaded
    assert mock_config_entry.state == ConfigEntryState.LOADED

    # Unload the entry
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify entry is unloaded
    assert mock_config_entry.state == ConfigEntryState.NOT_LOADED
    
    # Verify data is cleaned up
    assert DOMAIN not in hass.data or not hass.data[DOMAIN]


async def test_setup_entry_mqtt_not_loaded(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test setup fails when MQTT integration is not loaded."""
    mock_config_entry.add_to_hass(hass)

    # Don't add MQTT to components
    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify entry failed to load
    assert mock_config_entry.state == ConfigEntryState.SETUP_ERROR


async def test_setup_entry_api_failure(
    hass: HomeAssistant,
    mock_config_entry,
    mock_mqtt_client,
) -> None:
    """Test setup fails when API client fails to initialize."""
    mock_config_entry.add_to_hass(hass)
    hass.config.components.add("mqtt")

    with patch(
        "custom_components.sofabaton_hub.coordinator.SofabatonHubAPI",
        side_effect=Exception("API initialization failed"),
    ):
        assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Verify entry failed to load
    assert mock_config_entry.state == ConfigEntryState.SETUP_ERROR


async def test_setup_entry_coordinator_failure(
    hass: HomeAssistant,
    mock_config_entry,
    mock_mqtt_client,
    mock_api_client,
) -> None:
    """Test setup fails when coordinator fails to refresh."""
    mock_config_entry.add_to_hass(hass)
    hass.config.components.add("mqtt")

    # Make coordinator refresh fail
    with patch(
        "custom_components.sofabaton_hub.coordinator.SofabatonHubAPI",
        return_value=mock_api_client,
    ), patch(
        "custom_components.sofabaton_hub.coordinator.SofabatonHubDataUpdateCoordinator.async_config_entry_first_refresh",
        side_effect=Exception("Coordinator refresh failed"),
    ):
        assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Verify entry failed to load
    assert mock_config_entry.state == ConfigEntryState.SETUP_ERROR

