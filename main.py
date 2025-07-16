# main.py

import asyncio
import config
from art_client import ArtClient
from status import SystemStatus
from network_manager import NetworkManager
from ui import UIManager


async def main():
    status = SystemStatus()
    network = NetworkManager(config.WIFI_SSID, config.WIFI_PASSWORD, status)
    data_updated_event = asyncio.Event()

    art_client = ArtClient(
        status,
        data_updated_event
    )
    ui = UIManager(
        status,
        data_updated_event
    )
    await asyncio.gather(
        network.manage_connection(),
        art_client.listen_for_updates(),
        ui.manage_display()
    )

if __name__ == "__main__":
    asyncio.run(main())
