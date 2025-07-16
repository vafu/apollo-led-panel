# Album Art LED Panel Client

A MicroPython project to display "now playing" information and album art on a Pimoroni Interstate75-driven HUB75 RGB LED panel.

---
## Overview

This project runs on a Pico W-based microcontroller board (like the Interstate 75W). It acts as a client for the `apollo` media state server.

It establishes a persistent TCP socket connection to the `apollo` service to receive real-time JSON state updates for the currently playing media. When it receives a state update containing a URL for processed album art, it fetches the image via HTTP and renders it as a background. It then overlays metadata like artist, title, and player status icons.

The UI is designed to be dynamic, with configurable overlays that automatically hide after a period of inactivity, and a sleep mode to blank the screen when music is stopped for an extended time.

---
## Hardware Requirements

* **Controller Board:** Pimoroni Interstate 75 or 75W.
* **LED Panel:** A 128x128 (or other supported size) HUB75-compatible RGB LED matrix panel.
* **Power Supply:** A 5V power supply capable of providing sufficient current for your LED panel (e.g., 5V 10A).
* **Cabling:** A USB-C cable for programming and the necessary ribbon cable to connect the driver board to the panel.

---
## Software Setup


#### 0. Install apollo server

First make sure [apollo server](https://github.com/vafu/apollo-server) is up and running.

#### 1. Install Pimoroni MicroPython Firmware

Your board requires the custom Pimoroni MicroPython firmware, which includes the necessary graphics and hardware libraries.

1.  Download the latest UF2 file for the **Interstate 75** from the [Pimoroni MicroPython Releases page](https://github.com/pimoroni/pimoroni-pico/releases).
2.  Put your board into "bootsel" mode by holding the `BOOTSEL` button while plugging it into your computer via USB. It will appear as a USB drive.
3.  Drag and drop the downloaded `.uf2` file onto the drive. The board will automatically reboot with MicroPython installed.

#### 2. Install Libraries

The `Pimoroni` firmware already includes the `interstate75`, `picographics`, `jpegdec`, and `urequests` libraries, so no additional installation is needed.

---
## Configuration

Edit the `config.py` file on the board to match your local setup.
