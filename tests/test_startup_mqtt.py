"""Regression tests for MQTT startup subscription verification."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import HomeAssistant

from custom_components.sofabaton_hub.api import SofabatonHubApiClient
from custom_components.sofabaton_hub.const import TOPIC_SUBSCRIPTION_BARRIER
from custom_components.sofabaton_hub.coordinator import SofabatonHubDataUpdateCoordinator


async def test_subscription_barrier_confirms_and_cleans_up(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """A retained loopback confirms subscriptions before the first request."""
    api_client = SofabatonHubApiClient(hass, mock_config_entry)
    unsubscribe_callbacks: list[MagicMock] = []

    async def async_subscribe(*_args, **_kwargs):
        unsubscribe = MagicMock()
        unsubscribe_callbacks.append(unsubscribe)
        return unsubscribe

    async def async_publish(_hass, topic, payload, **_kwargs) -> None:
        if topic == api_client._get_topic(TOPIC_SUBSCRIPTION_BARRIER) and payload:
            api_client._message_received(
                SimpleNamespace(topic=topic, payload=payload)
            )

    with patch("custom_components.sofabaton_hub.api.mqtt") as mock_mqtt:
        mock_mqtt.async_subscribe = AsyncMock(side_effect=async_subscribe)
        mock_mqtt.async_publish = AsyncMock(side_effect=async_publish)

        await api_client.async_subscribe_to_topics()

        assert await api_client.async_verify_subscriptions() is True

        barrier_unsubscribe = unsubscribe_callbacks[-1]
        barrier_unsubscribe.assert_called_once()
        assert barrier_unsubscribe not in api_client._unsubscribe_callbacks
        mock_mqtt.async_publish.assert_any_call(
            hass,
            api_client._get_topic(TOPIC_SUBSCRIPTION_BARRIER),
            "",
            retain=True,
        )

        await api_client.async_unsubscribe_from_topics()

    for unsubscribe in unsubscribe_callbacks[:-1]:
        unsubscribe.assert_called_once()


async def test_coordinator_does_not_register_callback_during_construction(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """The startup barrier owns messages until entry setup enables handling."""
    api_client = MagicMock(spec=SofabatonHubApiClient)

    SofabatonHubDataUpdateCoordinator(hass, api_client, mock_config_entry)

    api_client.set_on_message_callback.assert_not_called()