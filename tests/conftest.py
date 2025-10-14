"""Fixtures for Sofabaton Hub integration tests."""
from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.components.mqtt import DOMAIN as MQTT_DOMAIN
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant

from custom_components.sofabaton_hub.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
)

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_mqtt_client():
    """Mock MQTT client."""
    with patch("custom_components.sofabaton_hub.api.mqtt") as mock_mqtt:
        mock_client = MagicMock()
        mock_mqtt.async_subscribe = AsyncMock(return_value=None)
        mock_mqtt.async_publish = AsyncMock(return_value=None)
        mock_mqtt.is_connected = MagicMock(return_value=True)
        yield mock_mqtt


@pytest.fixture
def mock_config_entry():
    """Mock a config entry."""
    from homeassistant.config_entries import ConfigEntry

    return ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title=DEFAULT_NAME,
        data={
            CONF_MAC: "AABBCCDDEEFF",
            CONF_NAME: DEFAULT_NAME,
            CONF_HOST: "192.168.1.100",
            CONF_PORT: DEFAULT_PORT,
            CONF_USERNAME: "test_user",
            CONF_PASSWORD: "test_pass",
        },
        source="user",
        entry_id="test_entry_id",
        unique_id="AABBCCDDEEFF",
    )


@pytest.fixture
def mock_api_client():
    """Mock API client."""
    with patch("custom_components.sofabaton_hub.api.SofabatonHubAPI") as mock_api:
        client = mock_api.return_value
        client.async_subscribe_to_topics = AsyncMock(return_value=None)
        client.async_publish_message = AsyncMock(return_value=None)
        client.set_on_message_callback = MagicMock()
        yield client


@pytest.fixture
def mock_coordinator():
    """Mock coordinator."""
    with patch(
        "custom_components.sofabaton_hub.coordinator.SofabatonHubDataUpdateCoordinator"
    ) as mock_coord:
        coordinator = mock_coord.return_value
        coordinator.async_config_entry_first_refresh = AsyncMock(return_value=None)
        coordinator.data = {
            "activities": {
                101: {"id": 101, "name": "Watch TV", "state": "off"},
                102: {"id": 102, "name": "Watch Movie", "state": "off"},
            },
            "devices": {},
            "current_activity_id": None,
            "keys": {
                "assigned": {},
                "macros": {},
                "favorites": {},
            },
        }
        yield coordinator


@pytest.fixture
def mock_activity_list_payload():
    """Mock activity list payload."""
    return {
        "data": [
            {
                "activity_id": 101,
                "activity_name": "Watch TV",
                "state": "off",
            },
            {
                "activity_id": 102,
                "activity_name": "Watch Movie",
                "state": "off",
            },
        ]
    }


@pytest.fixture
def mock_activity_status_payload():
    """Mock activity status payload."""
    return {
        "activity_id": 101,
        "state": "on",
    }


@pytest.fixture
def mock_assigned_keys_payload():
    """Mock assigned keys payload."""
    return {
        "activity_id": 101,
        "data": [
            {
                "key_id": 1,
                "key_name": "Power",
                "device_id": 201,
                "device_name": "TV",
            },
            {
                "key_id": 2,
                "key_name": "Volume Up",
                "device_id": 201,
                "device_name": "TV",
            },
        ],
    }


@pytest.fixture
def mock_macro_keys_payload():
    """Mock macro keys payload."""
    return {
        "activity_id": 101,
        "data": [
            {
                "key_id": 301,
                "key_name": "Watch Netflix",
                "commands": ["power_on", "input_hdmi1", "launch_netflix"],
            },
        ],
    }


@pytest.fixture
def mock_favorite_keys_payload():
    """Mock favorite keys payload."""
    return {
        "activity_id": 101,
        "data": [
            {
                "key_id": 401,
                "key_name": "Channel 1",
                "command": "channel_1",
            },
        ],
    }


@pytest.fixture
async def setup_integration(
    hass: HomeAssistant,
    mock_config_entry,
    mock_mqtt_client,
    mock_api_client,
) -> Generator[None, None, None]:
    """Set up the Sofabaton Hub integration for testing."""
    mock_config_entry.add_to_hass(hass)

    # Mock MQTT integration as loaded
    hass.config.components.add(MQTT_DOMAIN)

    with patch(
        "custom_components.sofabaton_hub.coordinator.SofabatonHubAPI",
        return_value=mock_api_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    yield

    await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

