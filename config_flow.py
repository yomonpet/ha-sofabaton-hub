"""Config flow for Sofabaton Hub integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import mqtt, zeroconf
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.device_registry import format_mac

from .const import (
    CONF_HOST,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """Error to indicate we cannot connect to MQTT broker."""


class InvalidAuth(Exception):
    """Error to indicate authentication failure."""

# User manual input data schema
USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MAC): str,
        vol.Required("name", default=DEFAULT_NAME): str,
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
    }
)

# mDNS discovery data schema
ZEROCONF_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
    }
)


async def validate_mqtt_connection(hass, data: dict[str, Any]) -> dict[str, Any]:
    """Validate MQTT broker connection.

    Args:
        hass: Home Assistant instance
        data: User input data containing MQTT connection details

    Returns:
        Dictionary containing validated connection info

    Raises:
        CannotConnect: If connection to MQTT broker fails
        InvalidAuth: If authentication fails
    """
    # Check if MQTT integration is loaded
    if not mqtt.is_connected(hass):
        _LOGGER.warning("MQTT integration is not connected")
        raise CannotConnect("MQTT integration is not connected")

    # For Sofabaton Hub, we rely on the existing MQTT integration
    # The actual connection test happens when the coordinator subscribes to topics
    # Here we just validate that MQTT is available and configured

    # Return validated data
    return {
        "title": data.get("name", DEFAULT_NAME),
        CONF_MAC: data[CONF_MAC],
        CONF_HOST: data[CONF_HOST],
        CONF_PORT: data[CONF_PORT],
        CONF_USERNAME: data.get(CONF_USERNAME),
        CONF_PASSWORD: data.get(CONF_PASSWORD),
    }


class SofabatonHubConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sofabaton Hub."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.discovery_info: dict[str, Any] | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step initiated by the user.

        Args:
            user_input: User input data from the config flow form

        Returns:
            FlowResult indicating next step or entry creation
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # Normalize MAC address to uppercase without separators
            mac = user_input[CONF_MAC].replace(":", "").replace("-", "").upper()

            # Validate MAC address format (12 hexadecimal characters)
            if len(mac) != 12:
                errors["base"] = "invalid_mac"
            else:
                # Check if this MAC address is already configured
                await self.async_set_unique_id(format_mac(mac))
                self._abort_if_unique_id_configured()

                # Validate MQTT connection
                try:
                    user_input[CONF_MAC] = mac
                    info = await validate_mqtt_connection(self.hass, user_input)
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except Exception as err:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception during validation")
                    errors["base"] = "unknown"

                if not errors:
                    # If no errors, create config entry and finish flow
                    return self.async_create_entry(
                        title=user_input["name"],
                        data={
                            CONF_MAC: mac,
                            "name": user_input["name"],
                            CONF_HOST: user_input[CONF_HOST],
                            CONF_PORT: user_input[CONF_PORT],
                            CONF_USERNAME: user_input.get(CONF_USERNAME),
                            CONF_PASSWORD: user_input.get(CONF_PASSWORD),
                        },
                    )

        # Show form on first display or if there are errors
        return self.async_show_form(
            step_id="user", data_schema=USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle device discovered via mDNS.

        Args:
            discovery_info: Zeroconf service discovery information

        Returns:
            FlowResult indicating next step or abort
        """
        # Extract MAC address from discovery info
        mac = discovery_info.properties.get("MAC")
        if not mac:
            return self.async_abort(reason="no_mac_address")

        # Format MAC address and set as unique ID
        formatted_mac = format_mac(mac)
        await self.async_set_unique_id(formatted_mac)
        # Abort if already configured
        self._abort_if_unique_id_configured()

        # Store discovery info for use in next step
        self.discovery_info = {
            CONF_MAC: mac.upper(),
            "name": discovery_info.properties.get("NAME", DEFAULT_NAME),
        }

        # Set context for UI to display correct information
        self.context["title_placeholders"] = {"name": self.discovery_info["name"]}

        # Show form for user to input MQTT broker information
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm mDNS discovered device.

        Args:
            user_input: User input data from the confirmation form

        Returns:
            FlowResult indicating entry creation or form display
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # Merge discovery info with user input
            data = {**self.discovery_info, **user_input}

            # Validate MQTT connection
            try:
                info = await validate_mqtt_connection(self.hass, data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during validation")
                errors["base"] = "unknown"

            if not errors:
                # Create config entry
                return self.async_create_entry(
                    title=data["name"],
                    data=data,
                )

        # Show confirmation form
        return self.async_show_form(
            step_id="zeroconf_confirm",
            data_schema=ZEROCONF_DATA_SCHEMA,
            description_placeholders={"name": self.discovery_info["name"]},
            errors=errors,
        )
