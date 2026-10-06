"""Macropad Music Box: a music toy for little kids.

Press the dial for the next game; turn it to change the game's setting.
Parent settings (volume, brightness, sleep timer) live in settings.toml.
"""

import os
import time

from music_box.app import App
from music_box.hardware import Macropad
from music_box.modes.beat import Beat
from music_box.modes.echo import Echo
from music_box.modes.follow import Follow
from music_box.modes.piano import Piano


def setting(name, default):
    value = os.getenv(name)
    return default if value is None else int(value)


def now():
    return time.monotonic_ns() // 1_000_000


io = Macropad(volume=setting("VOLUME", 40), brightness=setting("BRIGHTNESS", 30))
app = App(
    io,
    [Piano(io), Follow(io), Echo(io), Beat(io)],
    sleep_ms=setting("SLEEP_MINUTES", 10) * 60_000,
)
app.start(now())

while True:
    t = now()
    io.poll(app, t)
    app.tick(t)
    io.flush()
