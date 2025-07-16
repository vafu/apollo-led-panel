import asyncio
import config
import icons
import framebuf
import time
from interstate75 import Interstate75
from picographics import PicoGraphics
from status import PlayerState, NetworkState
import jpegdec

# Color constants
SCRIM_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
ICON_COLOR = (0, 255, 255)
BG_COLOR = (0, 0, 0)


class UIManager:

    def __init__(self, status, data_updated_event):
        display_constant = Interstate75.DISPLAY_INTERSTATE75_128X128
        self.i75 = Interstate75(display=display_constant)
        self.graphics = PicoGraphics(display_constant)
        self.width = self.i75.width
        self.height = self.i75.height

        self._status = status

        self.TEXT_PEN = self.graphics.create_pen(255, 255, 255)
        self.ICON_PEN = self.graphics.create_pen(0, 255, 255)
        self.ICON_PEN_ERROR = self.graphics.create_pen(255, 0, 0)
        self.BG_PEN = self.graphics.create_pen(0, 0, 0)
        self.SCRIM_PEN = self.graphics.create_pen(30, 30, 30)
        self.graphics.set_font("font6")
        self.jpeg = jpegdec.JPEG(self.graphics)
        self._last_state_key = ""
        self._overlay_visible = True
        self._last_activity_time = time.ticks_ms()
        self._is_sleeping = False
        self._data_updated_event = data_updated_event

    def _draw_frame(self):
        if self._status.network == NetworkState.DISCONNECTED:
            self._draw_icon(icons.NO_WIFI, isError=True)
        elif not self._status.artfetcher_connected:
            self._draw_icon(icons.NO_SERVER, isError=True)
        else:
            jpeg_data = self._status.art_cache['data']
            if not jpeg_data:
                self.graphics.set_pen(self.BG_PEN)
                self.graphics.clear()
            else:
                self.jpeg.open_RAM(jpeg_data)
                self.jpeg.decode(0, 0, jpegdec.JPEG_SCALE_FULL)
            if self._overlay_visible:
                if config.UI_SHOW_ARTIST_TOP:
                    self._draw_text_with_scrim(
                        self._status.current_track.artist, 0)
                if config.UI_SHOW_PLAYER_ICON:
                    if self._status.player == PlayerState.PLAYING:
                        self._draw_icon(icons.PLAY_ICON)
                    elif self._status.player == PlayerState.PAUSED:
                        self._draw_icon(icons.PAUSE_ICON)
                    else:
                        self._draw_icon(icons.STOP_ICON)
                if config.UI_SHOW_TRACK_BOTTOM:
                    self._draw_text_with_scrim(
                        self._status.current_track.title, self.height, inverted=True)

        self.i75.update(self.graphics)

    def _draw_blank_screen(self):
        """Helper to clear the screen to black once."""
        self.graphics.set_pen(self.BG_PEN)
        self.graphics.clear()
        self.i75.update(self.graphics)
        print("UI: Display sleeping.")

    def _draw_text_with_scrim(self, text, y, inverted=False):
        if not text:
            return
        text_height = 9
        scrim_height = text_height + 4
        y = y if not inverted else y - scrim_height
        self.graphics.set_pen(self.SCRIM_PEN)
        self.graphics.rectangle(0, y, self.width, scrim_height)
        text_width = self.graphics.measure_text(text, 1)
        x = (self.width - text_width) // 2
        self.graphics.set_pen(self.TEXT_PEN)
        self.graphics.text(text, x, y + text_height // 2 - 1, -1, 1)

    def _draw_icon(self, icon_data, isError=False):
        if (isError):
            self.graphics.set_pen(self.ICON_PEN_ERROR)
        else:
            self.graphics.set_pen(self.ICON_PEN)
        icon_height = len(icon_data)
        icon_width = len(icon_data[0])
        start_x = (self.width - icon_width) // 2
        start_y = (self.height - icon_height) // 2
        for y, row in enumerate(icon_data):
            for x, char in enumerate(row):
                if char == "X":
                    self.graphics.pixel(start_x + x, start_y + y)

    async def manage_display(self):
        while True:
            if self._is_sleeping:
                await self._data_updated_event.wait()
                self._data_updated_event.clear()
                self._is_sleeping = False

            player_state = self._status.player
            songid = self._status.current_track.songid
            current_state_key = f"{player_state}-{songid}"

            if current_state_key != self._last_state_key:
                self._last_state_key = current_state_key
                self._overlay_visible = True
                self._last_activity_time = time.ticks_ms()

            if player_state == PlayerState.PAUSED:
                self._overlay_visible = True

            if config.UI_SLEEP_TIMEOUT_MIN > 0 and not player_state == PlayerState.PLAYING:
                sleep_delay_ms = config.UI_SLEEP_TIMEOUT_MIN * 60 * 1000
                elapsed_ms = time.ticks_diff(
                    time.ticks_ms(), self._last_activity_time)

                if elapsed_ms > sleep_delay_ms and not self._is_sleeping:
                    print("UI: Going to sleep")
                    self._is_sleeping = True
                    self._draw_blank_screen()
                    continue

            # Check if overlay hide timer has expired
            if config.UI_OVERLAY_HIDE_DELAY_S > 0 and self._overlay_visible:
                hide_delay_ms = config.UI_OVERLAY_HIDE_DELAY_S * 1000
                elapsed_ms = time.ticks_diff(
                    time.ticks_ms(), self._last_activity_time)
                if elapsed_ms > hide_delay_ms:
                    self._overlay_visible = False
            self._draw_frame()

            try:
                await asyncio.wait_for_ms(self._data_updated_event.wait(), 500)
                self._data_updated_event.clear()
            except asyncio.TimeoutError:
                pass
