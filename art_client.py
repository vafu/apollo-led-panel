# art_client.py
import uasyncio as asyncio
import ustruct as struct
import ujson as json
import urequests as requests
from status import PlayerState
import config


class ArtClient:

    def __init__(self, status, data_updated_event):
        self._host = config.APOLLO_HOST
        self._port = config.APOLLO_PORT
        self._status = status
        # It now directly controls the art bitmap cache
        self._coverurl = None
        self._base = f"http://{self._host}:{config.IMAGE_PORT}"
        self._data_updated_event = data_updated_event

    async def _fetch_art_task(self, art_url):
        if self._coverurl == art_url:
            return
        self._coverurl = art_url
        if not art_url:
            self._status.art_cache['data'] = None
            return

        print(f"ArtClient: Fetching art from {art_url}")
        art_url = f"{self._base}{art_url}"
        try:
            response = requests.get(art_url, timeout=10)
            if response.status_code == 200:
                self._status.art_cache['data'] = response.content
                print(f"ArtClient: Art cache updated ({
                    len(response.content)} bytes).")
            else:
                self._status.art_cache['data'] = None
                print(f"ArtClient: Art fetch failed with HTTP {
                    response.status_code}")
            response.close()
        except Exception as e:
            self._status.art_cache['data'] = None
            print(f"ArtClient: Exception during art fetch: {e}")

    async def listen_for_updates(self):
        while True:
            print("ArtClient: Attempting to connect...")
            try:
                reader, writer = await asyncio.open_connection(self._host, self._port)
                self._status.artfetcher_connected = True

                print("ArtClient: Connection established.")

                while True:
                    header = await reader.readexactly(4)
                    (msg_len,) = struct.unpack('>I', header)
                    payload = await reader.readexactly(msg_len)
                    state_data = json.loads(payload.decode('utf-8'))
                    print(f"ArtClient: Received new state: {state_data}")
                    self._data_updated_event.set()

                    player_state_str = state_data.get('player_state').lower()

                    if player_state_str == 'playing':
                        self._status.player = PlayerState.PLAYING
                    elif player_state_str == 'paused':
                        self._status.player = PlayerState.PAUSED
                    else:
                        self._status.player = PlayerState.STOPPED

                    self._status.current_track.title = state_data.get('title')
                    self._status.current_track.artist = state_data.get(
                        'artist')
                    self._status.current_track.album = state_data.get('album')
                    self._status.current_track.songid = state_data.get(
                        'songid')

                    asyncio.create_task(self._fetch_art_task(
                        state_data.get('cover_url')))

            except Exception as e:
                self._status.artfetcher_connected = False
                print(f"ArtClient: Error - {e}. Reconnecting in 5s.")
                if 'writer' in locals() and writer:
                    writer.close()
                    await writer.wait_closed()
                await asyncio.sleep(5)
