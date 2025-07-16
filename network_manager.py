# network_manager.py

import network
import asyncio
from status import NetworkState
import webrepl


class NetworkManager:

    def __init__(self, ssid, password, status):
        self._ssid = ssid
        self._password = password
        self._status = status
        self._wlan = network.WLAN(network.STA_IF)

    async def manage_connection(self):
        self._wlan.active(True)
        while True:
            if self._wlan.status() != 3:
                print("connecting...")
                self._status.network = NetworkState.CONNECTING
                self._wlan.connect(self._ssid, self._password)
                max_wait = 10
                while max_wait > 0 and self._wlan.status() != 3:
                    await asyncio.sleep(1)
                    max_wait -= 1

            if self._wlan.status() == 3 and self._status.network != NetworkState.CONNECTED:
                self._status.network = NetworkState.CONNECTED
                print(f"Network State IP: {
                    self._wlan.ifconfig()[0]}")
                webrepl.start()

            await asyncio.sleep(5)
