"""Webthings integration."""
import aiohttp

from homeassistant.core import callback
from homeassistant.helpers.entity import Entity

from .websocket_client import WS


DOMAIN = "webthing"


async def fetch(session, url):
    async with session.get(url) as resp:
        return await resp.json()


async def async_setup(hass, config):
    # hass.states.async_set("hello_state.world", "Paulus")
    async with aiohttp.ClientSession() as session:
        things = await fetch(session, "http://dev.wormhole.monad.site:8000")
        print(things)

    hass.data["things"] = things
    hass.helpers.discovery.async_load_platform("webthing", DOMAIN, {}, config)
    # Return boolean to indicate that initialization was successful.
    return True


class WebthingDevice(Entity):
    """Representation a base Webthing device."""

    def __init__(self, thing):
        """Initialize the Xiaomi device."""
        self._ws = WS(self)
        self._is_available = True
        self._uid = thing["id"]
        self._name = thing["title"]
        self._type = thing["@type"]
        self._remove_unavailability_tracker = None

    def _add_push_data_job(self, *args):
        self.hass.loop.create_task(self._ws.get_state(self._uid))

    async def async_added_to_hass(self):
        """Start unavailability tracking."""
        # self._async_track_unavailable()
        self._add_push_data_job(self._uid)

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._uid

    @property
    def available(self):
        """Return True if entity is available."""
        return self._is_available

    @property
    def should_poll(self):
        """Return the polling state. No polling needed."""
        return False

    # @property
    # def device_state_attributes(self):
    #     """Return the state attributes."""
    #     return self._device_state_attributes

    @callback
    def _async_set_unavailable(self, now):
        """Set state to UNAVAILABLE."""
        self._remove_unavailability_tracker = None
        self._is_available = False
        self.async_write_ha_state()

    def parse_data(self, data, raw_data):
        """Parse data sent by gateway."""
        raise NotImplementedError()
