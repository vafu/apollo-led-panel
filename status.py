# status.py

class NetworkState:
    DISCONNECTED = 1
    CONNECTING = 2
    CONNECTED = 3


class PlayerState:
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2


class TrackMetadata:
    def __init__(self):
        self.artist = None
        self.album = None
        self.title = None
        self.songid = None
        self.album_art_url = None


class SystemStatus:
    def __init__(self):
        self.network = NetworkState.DISCONNECTED
        self.player = PlayerState.STOPPED
        self.current_track = TrackMetadata()
        self.artfetcher_connected = False
        self.art_cache = {'data': None}
