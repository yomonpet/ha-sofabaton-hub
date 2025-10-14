"""Test the Sofabaton Hub diagnostics."""
from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant

from custom_components.sofabaton_hub.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_diagnostics(
    hass: HomeAssistant,
    setup_integration,
    mock_config_entry,
) -> None:
    """Test diagnostics data."""
    diagnostics = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    assert diagnostics is not None
    assert "config_entry" in diagnostics
    assert "coordinator_data" in diagnostics
    assert "coordinator_state" in diagnostics


async def test_diagnostics_config_entry_redaction(
    hass: HomeAssistant,
    setup_integration,
    mock_config_entry,
) -> None:
    """Test that sensitive data is redacted in diagnostics."""
    diagnostics = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    config_entry_data = diagnostics["config_entry"]
    
    # MAC address should be partially redacted
    assert "mac" in config_entry_data
    if config_entry_data["mac"]:
        assert "******" in config_entry_data["mac"]
    
    # Password should not be present, only has_password flag
    assert "password" not in config_entry_data
    assert "has_password" in config_entry_data
    
    # Username should not be present, only has_username flag
    assert "username" not in config_entry_data
    assert "has_username" in config_entry_data


async def test_diagnostics_coordinator_data(
    hass: HomeAssistant,
    setup_integration,
    mock_config_entry,
) -> None:
    """Test coordinator data in diagnostics."""
    diagnostics = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    coordinator_data = diagnostics["coordinator_data"]
    
    # Should have activity count
    assert "activities_count" in coordinator_data
    
    # Should have activities list
    assert "activities" in coordinator_data
    
    # Should have keys stats
    assert "keys_stats" in coordinator_data


async def test_diagnostics_coordinator_state(
    hass: HomeAssistant,
    setup_integration,
    mock_config_entry,
) -> None:
    """Test coordinator state in diagnostics."""
    diagnostics = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    coordinator_state = diagnostics["coordinator_state"]
    
    # Should have last update success status
    assert "last_update_success" in coordinator_state
    
    # Should have update interval
    assert "update_interval_seconds" in coordinator_state

