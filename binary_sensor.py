"""Platform for webthing binary sensor integration."""
import logging
import aiohttp

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

# Import the device class from the component that you want to support
from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_MOTION,
    BinarySensorDevice,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    STATE_OFF,
    STATE_ON,
)


from . import WebthingDevice

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
#     {
#         vol.Required(CONF_HOST): cv.string,
#         # vol.Optional(CONF_USERNAME, default="admin"): cv.string,
#         # vol.Optional(CONF_PASSWORD): cv.string,
#     }
# )


async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    # host = config[CONF_HOST]

    # Setup connection with devices/cloud
    things = hass.data["things"]
    # Verify that passed in configuration works
    # if not hub.is_valid_login():
    #     _LOGGER.error("Could not connect to AwesomeLight hub")
    #     return

    # Add devices
    devices = []
    for thing in things:
        if "BinarySensor" in thing["@type"]:
            if "PIR" in thing["@type"]:
                devices.append(WebthingBinarySensor(thing, "motion"))

        print(devices)
        add_entities(devices)


class WebthingBinarySensor(WebthingDevice, BinarySensorDevice):
    """Representation of an Webthing BinarySensor."""

    def __init__(self, thing, device_class):
        """Initialize an WebthingBinarySensor."""
        WebthingDevice.__init__(self, thing)
        self._cover = thing
        self._url = f"http://dev.wormhole.monad.site:8000/{self._uid}"
        self._on = True  # thing["properties"]["on"]
        self._battery_level = 100
        self._device_class = device_class

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {"battery_level": self._battery_level}

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._on

    @property
    def state(self):
        """Return the state of the binary sensor."""
        return STATE_ON if self.is_on else STATE_OFF

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return self._device_class

    async def async_update(self):
        """
        Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        if self._ws.data.get("state"):
            self._on = self._ws.data.get("state")
            print(f"property on:{self._on}")
        if self._ws.data.get("battery_level"):
            self._battery_level = self._ws.data.get("battery_level")
            print(f"property battery_level:{self._battery_level}")
