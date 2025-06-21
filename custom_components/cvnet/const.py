"""Constants for the CVnet Integration with web version integration."""
from homeassistant.const import Platform

DOMAIN = "cvnet"

CONF_REGION = "region"
CONF_SITE_NAME = "site_name"

PLATFORMS = [Platform.SENSOR, Platform.LIGHT, Platform.CLIMATE, Platform.FAN, Platform.SWITCH]
