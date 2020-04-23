"""Platform for webthing light integration."""
import logging
import aiohttp

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

# Import the device class from the component that you want to support

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    PLATFORM_SCHEMA,
    Light,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    SUPPORT_COLOR_TEMP,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME

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
    """Set up the webthing platform."""
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
    for thing in things:
        if "Light" in thing["@type"]:
            add_entities([WebthingLight(thing)])


class WebthingLight(WebthingDevice, Light):
    """Representation of an Webthing Light."""

    def __init__(self, thing):
        """Initialize an WebthingLight."""
        WebthingDevice.__init__(self, thing)
        self._light = thing
        self._url = f"http://dev.wormhole.monad.site:8000/{self._uid}"
        self._on = True  # thing["properties"]["on"]
        self._brightness = thing["properties"]["brightness"]
        self._color_temp = thing["properties"]["color_temp"]

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def color_temp(self):
        return self._color_temp

    @property
    def hs_color(self):
        pass

    @property
    def supported_features(self):
        """Return the supported features."""
        return SUPPORT_BRIGHTNESS | SUPPORT_COLOR | SUPPORT_COLOR_TEMP

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._on

    async def async_turn_on(self, **kwargs):
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        print(kwargs)
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        color_temp = kwargs.get(ATTR_COLOR_TEMP)
        hs_color = kwargs.get(ATTR_HS_COLOR)
        if brightness:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    self._url + "/actions/set_brightness",
                    json={"set_brightness": {"input": {"brightness": brightness}}},
                )
        elif color_temp:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    self._url + "/actions/set_color_temp",
                    json={"set_color_temp": {"input": {"color_temp": color_temp}}},
                )
        elif hs_color:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    self._url + "/actions/set_hs_color",
                    json={"set_hs_color": {"input": {"hs_color": color_temp}}},
                )
        else:
            async with aiohttp.ClientSession() as session:
                await session.post(
                    self._url + "/actions/set_on",
                    json={"set_on": {"input": {"on": True}}},
                )

    async def async_turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        async with aiohttp.ClientSession() as session:
            await session.post(
                self._url + "/actions/set_on", json={"set_on": {"input": {"on": False}}}
            )

    async def async_update(self):
        """
        Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        if self._ws.data.get("on") is not None:
            self._on = self._ws.data.get("on")
            print(f"property on:{self._on}")

        if self._ws.data.get("brightness"):
            self._brightness = self._ws.data.get("brightness")
            print(f"property on:{self._brightness}")
