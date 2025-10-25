"""The Sofabaton Hub integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .api import SofabatonHubApiClient
from .const import DOMAIN, PLATFORMS
from .coordinator import SofabatonHubDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Sofabaton Hub component.

    This component does not support configuration via configuration.yaml.

    Args:
        hass: Home Assistant instance
        config: Configuration dictionary

    Returns:
        True to indicate successful setup
    """
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sofabaton Hub from a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry for this integration

    Returns:
        True if setup was successful
    """
    # Create dedicated space in hass.data for our domain
    hass.data.setdefault(DOMAIN, {})

    # Create API client instance
    api_client = SofabatonHubApiClient(hass, entry)

    # Create data update coordinator instance
    coordinator = SofabatonHubDataUpdateCoordinator(hass, api_client, entry)

    # Store coordinator instance for platforms and other components to access
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api_client": api_client,
    }

    # First data refresh (before subscribing to MQTT topics to avoid receiving messages before data initialization)
    await coordinator.async_config_entry_first_refresh()

    # Subscribe to MQTT topics
    await api_client.async_subscribe_to_topics()

    # Set up platforms (e.g., remote)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register frontend JS card resources
    # This allows us to use custom:sofabaton-main-card in Lovelace UI
    try:
        # Use new async static path registration method
        from homeassistant.components.http import StaticPathConfig  # pylint: disable=import-outside-toplevel

        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    f"/{DOMAIN}/www",
                    hass.config.path(f"custom_components/{DOMAIN}/www"),
                    True,  # cache_headers
                )
            ]
        )

        # Register frontend modules
        # Register all JS files to ensure proper loading order
        # Also defined in manifest.json for compatibility
        from homeassistant.components import frontend  # pylint: disable=import-outside-toplevel

        # Register main card and detail card as ES6 modules first
        frontend.add_extra_js_url(hass, f"/{DOMAIN}/www/main-card.js")
        frontend.add_extra_js_url(hass, f"/{DOMAIN}/www/detail-card.js")
        # Then register the cards.js for Lovelace picker
        frontend.add_extra_js_url(hass, f"/{DOMAIN}/www/cards.js")

        _LOGGER.info("Successfully registered Sofabaton Hub frontend cards")
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.error("Failed to register frontend cards: %s", err)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry to unload

    Returns:
        True if unload was successful
    """
    # Remove our data from hass.data
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        # NOTE: Should also unregister frontend modules and static paths here,
        # but HA Core currently does not provide a standard method for this

    return unload_ok
