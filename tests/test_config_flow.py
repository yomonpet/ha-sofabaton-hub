"""Test the Sofabaton Hub config flow."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.sofabaton_hub.config_flow import CannotConnect, InvalidAuth
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


async def test_user_flow_success(hass: HomeAssistant, mock_mqtt_client) -> None:
    """Test successful user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "custom_components.sofabaton_hub.config_flow.validate_mqtt_connection",
        return_value={
            "title": DEFAULT_NAME,
            CONF_MAC: "AABBCCDDEEFF",
            CONF_HOST: "192.168.1.100",
            CONF_PORT: DEFAULT_PORT,
            CONF_USERNAME: "test_user",
            CONF_PASSWORD: "test_pass",
        },
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MAC: "AA:BB:CC:DD:EE:FF",
                "name": DEFAULT_NAME,
                CONF_HOST: "192.168.1.100",
                CONF_PORT: DEFAULT_PORT,
                CONF_USERNAME: "test_user",
                CONF_PASSWORD: "test_pass",
            },
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == DEFAULT_NAME
    assert result["data"][CONF_MAC] == "AABBCCDDEEFF"
    assert result["data"][CONF_HOST] == "192.168.1.100"


async def test_user_flow_invalid_mac(hass: HomeAssistant) -> None:
    """Test user flow with invalid MAC address."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_MAC: "INVALID",
            "name": DEFAULT_NAME,
            CONF_HOST: "192.168.1.100",
            CONF_PORT: DEFAULT_PORT,
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_mac"}


async def test_user_flow_cannot_connect(hass: HomeAssistant, mock_mqtt_client) -> None:
    """Test user flow when cannot connect to MQTT."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.sofabaton_hub.config_flow.validate_mqtt_connection",
        side_effect=CannotConnect,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MAC: "AA:BB:CC:DD:EE:FF",
                "name": DEFAULT_NAME,
                CONF_HOST: "192.168.1.100",
                CONF_PORT: DEFAULT_PORT,
            },
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_invalid_auth(hass: HomeAssistant, mock_mqtt_client) -> None:
    """Test user flow with invalid authentication."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.sofabaton_hub.config_flow.validate_mqtt_connection",
        side_effect=InvalidAuth,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MAC: "AA:BB:CC:DD:EE:FF",
                "name": DEFAULT_NAME,
                CONF_HOST: "192.168.1.100",
                CONF_PORT: DEFAULT_PORT,
                CONF_USERNAME: "wrong_user",
                CONF_PASSWORD: "wrong_pass",
            },
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_user_flow_already_configured(
    hass: HomeAssistant, mock_config_entry, mock_mqtt_client
) -> None:
    """Test user flow when device is already configured."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.sofabaton_hub.config_flow.validate_mqtt_connection",
        return_value={
            "title": DEFAULT_NAME,
            CONF_MAC: "AABBCCDDEEFF",
            CONF_HOST: "192.168.1.100",
            CONF_PORT: DEFAULT_PORT,
        },
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MAC: "AA:BB:CC:DD:EE:FF",
                "name": DEFAULT_NAME,
                CONF_HOST: "192.168.1.100",
                CONF_PORT: DEFAULT_PORT,
            },
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_zeroconf_flow_success(hass: HomeAssistant, mock_mqtt_client) -> None:
    """Test successful zeroconf flow."""
    discovery_info = zeroconf.ZeroconfServiceInfo(
        ip_address="192.168.1.100",
        ip_addresses=["192.168.1.100"],
        hostname="sofabaton-hub.local.",
        name="Sofabaton Hub._sofabaton_hub._udp.local.",
        port=1883,
        properties={"MAC": "AABBCCDDEEFF", "NAME": "My Hub"},
        type="_sofabaton_hub._udp.local.",
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_ZEROCONF},
        data=discovery_info,
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "zeroconf_confirm"

    with patch(
        "custom_components.sofabaton_hub.config_flow.validate_mqtt_connection",
        return_value={
            "title": "My Hub",
            CONF_MAC: "AABBCCDDEEFF",
            CONF_HOST: "192.168.1.100",
            CONF_PORT: DEFAULT_PORT,
        },
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "192.168.1.100",
                CONF_PORT: DEFAULT_PORT,
            },
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "My Hub"
    assert result["data"][CONF_MAC] == "AABBCCDDEEFF"


async def test_zeroconf_flow_no_mac(hass: HomeAssistant) -> None:
    """Test zeroconf flow aborts when no MAC address in discovery info."""
    discovery_info = zeroconf.ZeroconfServiceInfo(
        ip_address="192.168.1.100",
        ip_addresses=["192.168.1.100"],
        hostname="sofabaton-hub.local.",
        name="Sofabaton Hub._sofabaton_hub._udp.local.",
        port=1883,
        properties={},  # No MAC address
        type="_sofabaton_hub._udp.local.",
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_ZEROCONF},
        data=discovery_info,
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "no_mac_address"


async def test_zeroconf_flow_already_configured(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test zeroconf flow aborts when device is already configured."""
    mock_config_entry.add_to_hass(hass)

    discovery_info = zeroconf.ZeroconfServiceInfo(
        ip_address="192.168.1.100",
        ip_addresses=["192.168.1.100"],
        hostname="sofabaton-hub.local.",
        name="Sofabaton Hub._sofabaton_hub._udp.local.",
        port=1883,
        properties={"MAC": "AABBCCDDEEFF", "NAME": "My Hub"},
        type="_sofabaton_hub._udp.local.",
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_ZEROCONF},
        data=discovery_info,
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"

