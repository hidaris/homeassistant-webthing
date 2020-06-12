import json
import socket
import asyncio
import websockets


class WS:
    def __init__(self, hass_device):
        self.data = None
        self.hass_device = hass_device
        self.sleep_time = 5

    async def get_state(self, uid):
        uri = f"wss://cloud.iot.longan.link/things/{uid}"
        while True:
            # outer loop restarted every time the connection fails
            print(f"Creating new connection to {uri}")
            try:
                async with websockets.connect(uri) as ws:
                    while True:
                        try:
                            rep = await ws.recv()
                        except websockets.exceptions.ConnectionClosed:
                            print(f"Ping error - retrying connection in {self.sleep_time} sec (Ctrl-C to quit)")
                            await asyncio.sleep(self.sleep_time)
                            break
                        recv_data = json.loads(rep)
                        if recv_data.get("messageType") == "propertyStatus":
                            self.data = recv_data.get("data")
                            self.hass_device.schedule_update_ha_state(force_refresh=True)
                            print(f"data push from ws:{self.data}")
            except socket.gaierror:
                print(
                    f"Socket error - retrying connection in {self.sleep_time} sec (Ctrl-C to quit)")
                await asyncio.sleep(self.sleep_time)
                continue
            except (websockets.exceptions.InvalidStatusCode, ConnectionRefusedError):
                print('Nobody seems to listen to this endpoint. Please check the URL.')
                print(f"Retrying connection in {self.sleep_time} sec (Ctrl-C to quit)")
                await asyncio.sleep(self.sleep_time)
                continue
