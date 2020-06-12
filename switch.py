"""Platform for webthing light integration."""
import logging
import aiohttp

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

# Import the device class from the component that you want to support

from homeassistant.components.switch import (
    SwitchEntity
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
        if "OnOffSwitch" in thing["@type"]:
            for p, v in thing["properties"].items():
                add_entities([WebthingSwitch(thing, v["title"], p)])


class WebthingSwitch(WebthingDevice, SwitchEntity):
    """Representation of an Webthing Switch."""

    def __init__(self, thing, model_title, model):
        """Initialize an WebthingLight."""
        WebthingDevice.__init__(self, thing)
        self._switch = thing
        self._uid = thing["id"] + "_" + model
        self._name = thing["title"] + "_" + model_title
        self._model = model
        self._url = f"http://127.0.0.1:8000/things/{self._switch['id']}"
        self._on = True  # thing["properties"]["on"]

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._on

    async def async_turn_on(self, **kwargs):
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        async with aiohttp.ClientSession() as session:
            await session.post(
                self._url + "/actions",
                json={"on": {"input": {"on": True, "model": self._model}}},
            )

    async def async_turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        async with aiohttp.ClientSession() as session:
            await session.post(
                self._url + "/actions", json={"on": {"input": {"on": False, "model": self._model}}}
            )

    async def async_update(self):
        """
        Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        print(self._ws.data)
        for k, v in self._ws.data.items():
            if k == self._model:
                self._on = v
                print(f"property on:{self._on}")
