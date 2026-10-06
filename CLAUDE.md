# CLAUDE.md

A CircuitPython music toy for the [Adafruit Macropad RP2040](https://learn.adafruit.com/adafruit-macropad-rp2040), for preschoolers. The [README](README.md) has the games and setup.

## Layout

- [`circuitpy/`](circuitpy/) mirrors the `CIRCUITPY` drive one-to-one: [`code.py`](circuitpy/code.py) is the entry point, [`settings.toml`](circuitpy/settings.toml) holds parent settings, and the package is [`lib/music_box/`](circuitpy/lib/music_box/) (`lib/` is on the board's import path).
- Modes in [`modes/`](circuitpy/lib/music_box/modes/) never touch hardware. They call the `io` interface documented in [`modes/base.py`](circuitpy/lib/music_box/modes/base.py), implemented by [`hardware.py`](circuitpy/lib/music_box/hardware.py) on the board and `FakeIO` in [`tests/conftest.py`](tests/conftest.py).
- Timing is done in milliseconds with [`timeline.py`](circuitpy/lib/music_box/timeline.py), never `time.sleep`, so input stays responsive.
- [`instruments.py`](circuitpy/lib/music_box/instruments.py), [`screen.py`](circuitpy/lib/music_box/screen.py), and `hardware.py` import CircuitPython-only modules (`synthio`, `displayio`, `board`), so they can't be imported in tests.

## Commands

- `uvx pytest`, `uvx ruff check .`, `uvx ruff format .`: run all three before committing; CI runs the same.
- [`scripts/deploy.sh`](scripts/deploy.sh): installs `neopixel` with circup and rsyncs `circuitpy/` to `/Volumes/CIRCUITPY`. The board restarts on every file write.
- To see on-device errors without an interactive terminal, open the first `/dev/cu.usbmodem*` with pyserial (`uv run --with pyserial python`), send `\x03` then `\x04` to soft-reload, and read the output. [`scripts/console.sh`](scripts/console.sh) is the interactive version.

## Gotchas

- Target is CircuitPython 10.x. Use the [10.x API docs](https://docs.circuitpython.org/en/latest/), not older guide code: for example `display.root_group = group` (`display.show()` was removed in 9).
- CircuitPython lacks `dataclasses`, `enum`, `typing`, `functools`, `itertools`, `bisect`, and `random.Random`. Ruff's `banned-api` in [`pyproject.toml`](pyproject.toml) catches them; add any new ones you hit to that list.
- Don't use `adafruit_macropad.MacroPad`: it takes the `SPEAKER_ENABLE` pin and its sound calls block.
- The encoder counts down when turned clockwise; `hardware.py` negates it.
- Inject randomness (see `Echo(choice=...)`) so tests stay deterministic.
- The toy can't use text: anything shown on the screen is a 16×16 icon in [`icons.py`](circuitpy/lib/music_box/icons.py), and a test checks that every icon a mode uses exists.
- Keep the child's name and household details out of the repo; it's meant to be open source.
- `backup/` (gitignored) holds the board's previous Zoom-mute RPC firmware files.
