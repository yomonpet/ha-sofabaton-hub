"""Constants for the Sofabaton Hub integration."""
from __future__ import annotations

# Integration domain
DOMAIN = "sofabaton_hub"

# Platforms
PLATFORMS = ["remote"]

# Default Hub name
DEFAULT_NAME = "Sofabaton Hub"

# Default MQTT port
DEFAULT_PORT = 1883

# mDNS service name
MDNS_SERVICE_TYPE = "_sofabaton_hub._udp.local."

# MQTT configuration keys
CONF_MAC = "mac"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Frontend card URLs
CARD_URL_MAIN = f"/{DOMAIN}/www/main-card.js"
CARD_URL_DETAIL = f"/{DOMAIN}/www/detail-card.js"

# MQTT topic templates
# Note: {mac} will be replaced with the actual MAC address at runtime

# Activity-related topics
TOPIC_ACTIVITY_LIST_REQUEST = "activity/{mac}/list_request"
TOPIC_ACTIVITY_LIST_RESPONSE = "activity/{mac}/list"
TOPIC_ACTIVITY_CONTROL_UP = "activity/{mac}/activity_control_up"
TOPIC_ACTIVITY_CONTROL_DOWN = "activity/{mac}/activity_control_down"
TOPIC_ACTIVITY_KEYS_REQUEST = "activity/{mac}/keys_request"
TOPIC_ACTIVITY_KEYS_LIST = "activity/{mac}/keys_list"
TOPIC_ACTIVITY_FAVORITES_REQUEST = "activity/{mac}/favorites_keys_request"
TOPIC_ACTIVITY_FAVORITES_LIST = "activity/{mac}/favorites_keys_list"
TOPIC_ACTIVITY_FAVORITES_CONTROL = "activity/{mac}/favorites_keys_control"
TOPIC_ACTIVITY_MACRO_REQUEST = "activity/{mac}/macro_keys_request"
TOPIC_ACTIVITY_MACRO_LIST = "activity/{mac}/macro_keys_list"
TOPIC_ACTIVITY_ASSIGNED_KEY_CONTROL = "activity/{mac}/keys_control"
TOPIC_ACTIVITY_MACRO_KEY_CONTROL = "activity/{mac}/macro_keys_control"

# Device-related topics
TOPIC_DEVICE_LIST_REQUEST = "device/{mac}/list_request"
TOPIC_DEVICE_LIST_RESPONSE = "device/{mac}/list"
TOPIC_DEVICE_KEYS_REQUEST = "device/{mac}/keys_request"
TOPIC_DEVICE_KEYS_LIST = "device/{mac}/keys_list"
TOPIC_DEVICE_KEY_CONTROL = "device/{mac}/keys_control"

# Remote key definitions (27 keys total)
# Note: key_id values should match your actual hardware configuration
REMOTE_KEYS = {
    # Directional keys and OK
    "up": {"id": 174, "icon": "mdi:arrow-up"},
    "down": {"id": 178, "icon": "mdi:arrow-down"},
    "left": {"id": 175, "icon": "mdi:arrow-left"},
    "right": {"id": 177, "icon": "mdi:arrow-right"},
    "ok": {"id": 176, "icon": "mdi:checkbox-blank-circle-outline"},
    # Function keys
    "back": {"id": 179, "icon": "mdi:arrow-u-left-top"},
    "home": {"id": 180, "icon": "mdi:home"},
    "menu": {"id": 181, "icon": "mdi:menu"},
    # Volume and channel
    "volume_up": {"id": 182, "icon": "mdi:volume-plus"},
    "volume_down": {"id": 185, "icon": "mdi:volume-minus"},
    "channel_up": {"id": 183, "icon": "mdi:chevron-up"},
    "channel_down": {"id": 186, "icon": "mdi:chevron-down"},
    "mute": {"id": 184, "icon": "mdi:volume-mute"},
    "guide": {"id": 157, "icon": "mdi:television-guide"},
    # Media control
    "rewind": {"id": 187, "icon": "mdi:rewind"},
    "play": {"id": 156, "icon": "mdi:play"},
    "fast_forward": {"id": 189, "icon": "mdi:fast-forward"},
    "dvr": {"id": 155, "text": "DVR"},
    "pause": {"id": 188, "icon": "mdi:pause"},
    "exit": {"id": 154, "text": "Exit"},
    # Color keys
    "red": {"id": 190, "color": "red"},
    "green": {"id": 191, "color": "green"},
    "yellow": {"id": 192, "color": "yellow"},
    "blue": {"id": 193, "color": "blue"},
    # Custom keys
    "a": {"id": 153, "text": "A"},
    "b": {"id": 152, "text": "B"},
    "c": {"id": 151, "text": "C"},
}
