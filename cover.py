"""Platform for webthing cover integration."""
import logging
import aiohttp

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

# Import the device class from the component that you want to support
from homeassistant.components.cover import ATTR_POSITION, CoverDevice
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
    for thing in things:
        if "Cover" in thing["@type"]:
            add_entities([WebthingCover(thing)])


class WebthingCover(WebthingDevice, CoverDevice):
    """Representation of an Webthing Cover."""

    def __init__(self, thing):
        """Initialize an WebthingCover."""
        WebthingDevice.__init__(self, thing)
        self._cover = thing
        self._url = f"http://127.0.0.1:8000/things/{self._uid}"
        self._pos = 0
        self._state = "open"  # thing["properties"]["on"]

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        return self._pos

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self.current_cover_position <= 0

    async def async_close_cover(self, **kwargs):
        """Close the cover."""
        async with aiohttp.ClientSession() as session:
            await session.post(
                self._url + "/actions/set_state",
                json={"set_state": {"input": {"state": "close"}}},
            )

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        async with aiohttp.ClientSession() as session:
            await session.post(
                self._url + "/actions/set_state",
                json={"set_state": {"input": {"state": "open"}}},
            )

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        async with aiohttp.ClientSession() as session:
            await session.post(
                self._url + "/actions/set_state",
                json={"set_state": {"input": {"state": "stop"}}},
            )

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs.get(ATTR_POSITION)

        async with aiohttp.ClientSession() as session:
            await session.post(
                self._url + "/actions/set_position",
                json={"set_position": {"input": {"position": position}}},
            )

    async def async_update(self):
        """
        Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        print(self._ws.data)
        if self._ws.data.get("state"):
            self._state = self._ws.data.get("state")
            print(f"property state:{self._state}")
        if self._ws.data.get("position"):
            self._pos = self._ws.data.get("position")
            print(f"property position:{self._pos}")
