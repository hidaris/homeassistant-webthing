"""Platform for webthing sensor integration."""
import logging
import aiohttp

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

# Import the device class from the component that you want to support
from homeassistant.components.alarm_control_panel import AlarmControlPanel

from homeassistant.components.alarm_control_panel.const import SUPPORT_ALARM_TRIGGER
from homeassistant.const import (
    STATE_ALARM_DISARMED,
    STATE_ALARM_PENDING,
    STATE_ALARM_TRIGGERED,
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

# SENSOR_TYPES = {
#     "temperature": [TEMP_CELSIUS, None],
#     "humidity": [UNIT_PERCENTAGE, None],
#     "illumination": ["lm", None],
#     "lux": ["lx", None],
#     "pressure": ["hPa", None],
#     "bed_activity": ["μm", None],
# }


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
    devices = []
    for thing in things:
        if "Alarm" in thing["@type"]:
            if "gas" in thing["@type"]:
                devices.append(WebthingAlarmPanel(thing, "gas"))
            if "smoke" in thing["@type"]:
                devices.append(WebthingAlarmPanel(thing, "smoke"))
        # if "Sensor" in thing["@type"]:
        #     if "temperature" in thing["@type"]:
        #         devices.append(WebthingAlarmPanel(thing, "gas"))

    print(devices)
    add_entities(devices)


class WebthingAlarmPanel(WebthingDevice, AlarmControlPanel):
    """Representation of an Webthing AlarmPanel."""

    def __init__(self, thing, device_class):
        """Initialize an Webthing AlarmPanel."""
        WebthingDevice.__init__(self, thing)
        # self._alarm_panel = thing
        self._url = f"http://dev.wormhole.monad.site:8000/{self._uid}"
        self._state = STATE_ALARM_DISARMED
        self._battery_level = 100
        self._device_class = device_class

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_ALARM_TRIGGER

    async def async_alarm_disarm(self, code=None) -> None:
        """Send disarm command."""
        async with aiohttp.ClientSession() as session:
            await session.post(
                self._url + "/actions/set_on", json={"set_on": {"input": {"on": False}}}
            )
        self._state = STATE_ALARM_DISARMED

    async def async_alarm_trigger(self, code=None) -> None:
        """Send alarm trigger command."""
        async with aiohttp.ClientSession() as session:
            await session.post(
                self._url + "/actions/set_on", json={"set_on": {"input": {"on": True}}}
            )
        self._state = STATE_ALARM_TRIGGERED

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {"battery_level": self._battery_level}

    @property
    def state(self):
        """Return the state of the binary sensor."""
        return self._state

    async def async_update(self):
        """
        Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        if self._ws.data.get("state") is not None:
            self._state = self._ws.data.get("state")
            print(f"{self.name} property state:{self._state}")
        if self._ws.data.get("battery_level"):
            self._battery_level = self._ws.data.get("battery_level")
            print(f"property battery_level:{self._battery_level}")
