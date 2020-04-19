import json
import websockets


class WS:
    def __init__(self, hass_device):
        self.data = None
        self.hass_device = hass_device

    async def get_state(self, uid):
        uri = f"ws://dev.wormhole.monad.site:8000/{uid}"
        ws = await websockets.connect(uri)
        while True:
            recv_data = json.loads(await ws.recv())
            if recv_data.get("messageType") == "propertyStatus":
                self.data = recv_data.get("data")
                self.hass_device.schedule_update_ha_state(force_refresh=True)
            print(f"data push from ws:{self.data}")
