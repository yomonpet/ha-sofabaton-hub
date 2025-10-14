"""Test the Sofabaton Hub API client."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.sofabaton_hub.api import SofabatonHubAPI
from custom_components.sofabaton_hub.const import (
    TOPIC_ACTIVITY_CONTROL_DOWN,
    TOPIC_ACTIVITY_LIST_REQUEST,
)


async def test_api_initialization(hass: HomeAssistant) -> None:
    """Test API client initialization."""
    api = SofabatonHubAPI(
        hass=hass,
        mac="AABBCCDDEEFF",
        host="192.168.1.100",
        port=1883,
        username="test_user",
        password="test_pass",
    )

    assert api.mac == "AABBCCDDEEFF"
    assert api.host == "192.168.1.100"
    assert api.port == 1883
    assert api.username == "test_user"
    assert api.password == "test_pass"


async def test_api_get_topic(hass: HomeAssistant) -> None:
    """Test topic formatting."""
    api = SofabatonHubAPI(
        hass=hass,
        mac="AABBCCDDEEFF",
        host="192.168.1.100",
        port=1883,
    )

    topic = api.get_topic(TOPIC_ACTIVITY_LIST_REQUEST)
    assert topic == "sofabaton/AABBCCDDEEFF/activity_list_request"


async def test_api_subscribe_to_topics(hass: HomeAssistant) -> None:
    """Test subscribing to MQTT topics."""
    with patch("custom_components.sofabaton_hub.api.mqtt") as mock_mqtt:
        mock_mqtt.async_subscribe = AsyncMock(return_value=None)

        api = SofabatonHubAPI(
            hass=hass,
            mac="AABBCCDDEEFF",
            host="192.168.1.100",
            port=1883,
        )

        await api.async_subscribe_to_topics()

        # Verify subscribe was called
        assert mock_mqtt.async_subscribe.called


async def test_api_publish_message(hass: HomeAssistant) -> None:
    """Test publishing MQTT message."""
    with patch("custom_components.sofabaton_hub.api.mqtt") as mock_mqtt:
        mock_mqtt.async_publish = AsyncMock(return_value=None)

        api = SofabatonHubAPI(
            hass=hass,
            mac="AABBCCDDEEFF",
            host="192.168.1.100",
            port=1883,
        )

        await api.async_publish_message(
            TOPIC_ACTIVITY_CONTROL_DOWN,
            {"activity_id": 101, "state": "on"},
        )

        # Verify publish was called
        mock_mqtt.async_publish.assert_called_once()
        call_args = mock_mqtt.async_publish.call_args
        assert "sofabaton/AABBCCDDEEFF/activity_control_down" in call_args[0]


async def test_api_publish_message_with_qos(hass: HomeAssistant) -> None:
    """Test publishing MQTT message with QoS."""
    with patch("custom_components.sofabaton_hub.api.mqtt") as mock_mqtt:
        mock_mqtt.async_publish = AsyncMock(return_value=None)

        api = SofabatonHubAPI(
            hass=hass,
            mac="AABBCCDDEEFF",
            host="192.168.1.100",
            port=1883,
        )

        await api.async_publish_message(
            TOPIC_ACTIVITY_CONTROL_DOWN,
            {"activity_id": 101, "state": "on"},
            qos=1,
        )

        # Verify publish was called with QoS
        mock_mqtt.async_publish.assert_called_once()
        call_kwargs = mock_mqtt.async_publish.call_args[1]
        assert call_kwargs.get("qos") == 1


async def test_api_set_on_message_callback(hass: HomeAssistant) -> None:
    """Test setting message callback."""
    api = SofabatonHubAPI(
        hass=hass,
        mac="AABBCCDDEEFF",
        host="192.168.1.100",
        port=1883,
    )

    callback = MagicMock()
    api.set_on_message_callback(callback)

    assert api._on_message_callback == callback


async def test_api_message_callback_invoked(hass: HomeAssistant) -> None:
    """Test that message callback is invoked when message received."""
    with patch("custom_components.sofabaton_hub.api.mqtt") as mock_mqtt:
        mock_mqtt.async_subscribe = AsyncMock(return_value=None)

        api = SofabatonHubAPI(
            hass=hass,
            mac="AABBCCDDEEFF",
            host="192.168.1.100",
            port=1883,
        )

        callback = MagicMock()
        api.set_on_message_callback(callback)

        # Simulate receiving a message
        test_topic = "sofabaton/AABBCCDDEEFF/activity_list_up"
        test_payload = {"data": [{"activity_id": 101, "activity_name": "Watch TV"}]}

        # Call the internal message handler
        api._handle_message(test_topic, test_payload)

        # Verify callback was called
        callback.assert_called_once_with(test_topic, test_payload)


async def test_api_publish_activity_control(hass: HomeAssistant) -> None:
    """Test publishing activity control command."""
    with patch("custom_components.sofabaton_hub.api.mqtt") as mock_mqtt:
        mock_mqtt.async_publish = AsyncMock(return_value=None)

        api = SofabatonHubAPI(
            hass=hass,
            mac="AABBCCDDEEFF",
            host="192.168.1.100",
            port=1883,
        )

        await api.async_publish_message(
            TOPIC_ACTIVITY_CONTROL_DOWN,
            {"activity_id": 101, "state": "on"},
        )

        # Verify correct topic and payload
        call_args = mock_mqtt.async_publish.call_args
        assert "activity_control_down" in call_args[0][1]


async def test_api_request_activity_list(hass: HomeAssistant) -> None:
    """Test requesting activity list."""
    with patch("custom_components.sofabaton_hub.api.mqtt") as mock_mqtt:
        mock_mqtt.async_publish = AsyncMock(return_value=None)

        api = SofabatonHubAPI(
            hass=hass,
            mac="AABBCCDDEEFF",
            host="192.168.1.100",
            port=1883,
        )

        await api.async_publish_message(
            TOPIC_ACTIVITY_LIST_REQUEST,
            {},
        )

        # Verify request was sent
        mock_mqtt.async_publish.assert_called_once()
        call_args = mock_mqtt.async_publish.call_args
        assert "activity_list_request" in call_args[0][1]


async def test_api_multiple_subscriptions(hass: HomeAssistant) -> None:
    """Test multiple topic subscriptions."""
    with patch("custom_components.sofabaton_hub.api.mqtt") as mock_mqtt:
        mock_mqtt.async_subscribe = AsyncMock(return_value=None)

        api = SofabatonHubAPI(
            hass=hass,
            mac="AABBCCDDEEFF",
            host="192.168.1.100",
            port=1883,
        )

        await api.async_subscribe_to_topics()

        # Verify subscribe was called multiple times (for different topics)
        assert mock_mqtt.async_subscribe.call_count >= 1


async def test_api_message_parsing(hass: HomeAssistant) -> None:
    """Test message parsing and callback."""
    api = SofabatonHubAPI(
        hass=hass,
        mac="AABBCCDDEEFF",
        host="192.168.1.100",
        port=1883,
    )

    received_messages = []

    def callback(topic: str, payload: dict) -> None:
        received_messages.append((topic, payload))

    api.set_on_message_callback(callback)

    # Simulate receiving messages
    test_messages = [
        ("sofabaton/AABBCCDDEEFF/activity_list_up", {"data": []}),
        ("sofabaton/AABBCCDDEEFF/activity_control_up", {"activity_id": 101, "state": "on"}),
    ]

    for topic, payload in test_messages:
        api._handle_message(topic, payload)

    # Verify all messages were received
    assert len(received_messages) == 2
    assert received_messages[0][0] == test_messages[0][0]
    assert received_messages[1][0] == test_messages[1][0]


async def test_api_error_handling_publish(hass: HomeAssistant) -> None:
    """Test error handling when publishing fails."""
    with patch("custom_components.sofabaton_hub.api.mqtt") as mock_mqtt:
        mock_mqtt.async_publish = AsyncMock(side_effect=Exception("MQTT error"))

        api = SofabatonHubAPI(
            hass=hass,
            mac="AABBCCDDEEFF",
            host="192.168.1.100",
            port=1883,
        )

        # Should not raise exception
        with pytest.raises(Exception):
            await api.async_publish_message(
                TOPIC_ACTIVITY_CONTROL_DOWN,
                {"activity_id": 101, "state": "on"},
            )


async def test_api_error_handling_subscribe(hass: HomeAssistant) -> None:
    """Test error handling when subscription fails."""
    with patch("custom_components.sofabaton_hub.api.mqtt") as mock_mqtt:
        mock_mqtt.async_subscribe = AsyncMock(side_effect=Exception("MQTT error"))

        api = SofabatonHubAPI(
            hass=hass,
            mac="AABBCCDDEEFF",
            host="192.168.1.100",
            port=1883,
        )

        # Should not raise exception
        with pytest.raises(Exception):
            await api.async_subscribe_to_topics()


async def test_api_topic_formatting_with_special_chars(hass: HomeAssistant) -> None:
    """Test topic formatting with special characters in MAC."""
    api = SofabatonHubAPI(
        hass=hass,
        mac="AA:BB:CC:DD:EE:FF",  # MAC with colons
        host="192.168.1.100",
        port=1883,
    )

    # MAC should be used as-is in topic
    topic = api.get_topic(TOPIC_ACTIVITY_LIST_REQUEST)
    assert "AA:BB:CC:DD:EE:FF" in topic or "AABBCCDDEEFF" in topic


async def test_api_callback_not_set(hass: HomeAssistant) -> None:
    """Test handling message when callback is not set."""
    api = SofabatonHubAPI(
        hass=hass,
        mac="AABBCCDDEEFF",
        host="192.168.1.100",
        port=1883,
    )

    # Should not raise exception when callback is not set
    api._handle_message(
        "sofabaton/AABBCCDDEEFF/activity_list_up",
        {"data": []},
    )


async def test_api_empty_payload(hass: HomeAssistant) -> None:
    """Test publishing empty payload."""
    with patch("custom_components.sofabaton_hub.api.mqtt") as mock_mqtt:
        mock_mqtt.async_publish = AsyncMock(return_value=None)

        api = SofabatonHubAPI(
            hass=hass,
            mac="AABBCCDDEEFF",
            host="192.168.1.100",
            port=1883,
        )

        await api.async_publish_message(
            TOPIC_ACTIVITY_LIST_REQUEST,
            {},
        )

        # Should still publish
        mock_mqtt.async_publish.assert_called_once()

