"""Runs once at power-up, before code.py.

By default the CIRCUITPY drive is hidden from the computer and the board
can write its own files: scripts/deploy.py sends updates over USB serial.
That keeps macOS's FAT driver, which corrupted the drive during
development (adafruit/circuitpython#8449), from writing to it, and it
means unplugging mid-play can't corrupt anything.

Hold the top-left key while plugging in to show the drive instead, to
edit settings.toml by hand or to recover.
"""

import board
import digitalio
import storage

key = digitalio.DigitalInOut(board.KEY1)
key.switch_to_input(pull=digitalio.Pull.UP)
show_drive = not key.value  # a pressed key reads low
key.deinit()

if not show_drive:
    storage.disable_usb_drive()
    storage.remount("/", readonly=False)
