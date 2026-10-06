# Macropad Music Box

A music toy for little kids (about 3–6) built on the [Adafruit Macropad RP2040](https://www.adafruit.com/product/5128). Twelve glowing keys, one dial, a tiny screen, and a speaker, with four games that sneak in a little STEM: pitch, sequences, patterns, and loops.

It's designed for kids who can't read yet. The screen shows pictures, never words, and nothing ever plays a "you lost" sound.

## How to play

The controls are the same in every game:

- **Press the dial** to go to the next game. A little jingle plays and the picture changes.
- **Turn the dial** to change the game's one setting. The big picture on the screen shows the current choice, and the dots under it show where you are.

| Game | Screen picture | What you do | Dial changes | The STEM idea |
| --- | --- | --- | --- | --- |
| **Rainbow Piano** | piano | Every key plays a note. Low notes start at the top-left, high notes end at the bottom-right. The scale is pentatonic, so any keys together sound nice. | Instrument: flute, bell, robot, guitar | Pitch: higher notes are faster vibrations |
| **Follow the Lights** | glowing key | One key lights up. Press it to play the next note of a song. Finish the song for a rainbow party. | Song: twinkle star, little lamb, Old MacDonald's cow, birthday cake, rowing boat | A song is a sequence of steps |
| **Echo** | speaker | The toy plays a pattern, then you play it back. It starts with one note and grows by one each time you get it right, up to 8. A miss just replays the pattern. | How many keys are in the game: 4, 6, or all 12 | Memory and patterns |
| **Beat Loop** | drum | A 4-step drum machine. Each row is a step and each column is a drum (kick, snare, shaker). Tap keys to turn drums on or off while the loop plays. | Tempo, from turtle to rabbit | Loops, like a `for` loop in code |

After 10 minutes with no button presses, the lights, screen, and sound turn off. Press any key or the dial to wake it up. That press only wakes the toy; it won't play a note.

## Setup

You need a Macropad RP2040 and a USB-C data cable. The Macropad has no battery, so use a USB power bank to take it off your desk.

1. **Install CircuitPython 10.x.** Download the UF2 from [circuitpython.org/board/adafruit_macropad_rp2040](https://circuitpython.org/board/adafruit_macropad_rp2040/). Hold the dial down while pressing the reset button (left side) to get an `RPI-RP2` drive, then copy the UF2 onto it. The board restarts as a `CIRCUITPY` drive.
2. **Copy the toy over.** With [uv](https://docs.astral.sh/uv/) installed, run:

   ```sh
   scripts/deploy.sh
   ```

   This installs the `neopixel` library with [circup](https://github.com/adafruit/circup) and copies [`circuitpy/`](circuitpy/) onto the drive. Without uv, copy everything in `circuitpy/` to `CIRCUITPY` yourself and put [`neopixel.mpy` and `adafruit_pixelbuf.mpy`](https://circuitpython.org/libraries) in `CIRCUITPY/lib`.

### Parent settings

Edit [`settings.toml`](circuitpy/settings.toml) on the `CIRCUITPY` drive. The board picks up changes on its own.

- `VOLUME`: 0–100, default 100 (the speaker is tiny)
- `BRIGHTNESS`: key lights, 0–100, default 30
- `SLEEP_MINUTES`: idle time before the toy turns off, default 10

## Development

The layout of [`circuitpy/`](circuitpy/) matches the `CIRCUITPY` drive exactly. The game logic doesn't touch the hardware: modes ask an `io` object to play notes and light keys. On the board that object is [`hardware.py`](circuitpy/lib/music_box/hardware.py); in tests it's a fake that records what was asked for, so the games can be tested on a laptop.

```sh
uvx pytest            # tests
uvx ruff check .      # lint
uvx ruff format .     # format
scripts/deploy.sh     # copy to the board
scripts/console.sh    # serial console: prints, tracebacks, REPL
```

CircuitPython is a subset of Python. Modules like `dataclasses`, `enum`, `typing`, and `functools` don't exist on the board, so the lint config bans them.

Screen pictures are 16×16 text art in [`icons.py`](circuitpy/lib/music_box/icons.py) (`#` is a lit pixel), so there are no image files to manage. Songs are note names in [`songs.py`](circuitpy/lib/music_box/songs.py), and a test checks that every note has a key.

## Ideas for later

- Animal sounds bank (WAV files)
- Record a tune and play it back
- "Shake for drums" with an accelerometer on the STEMMA QT port

## Prior art and credits

No existing Macropad project aimed at toddlers turned up, but these showed the way:

- Adafruit's [MacroPad Tone](https://learn.adafruit.com/adafruit-macropad-rp2040/macropad-tone) guide: key-to-note with rainbow colors
- Adafruit's [synthio guide](https://learn.adafruit.com/audio-synthesis-with-circuitpython-synthio) and [todbot/macropadsynthplug](https://github.com/todbot/macropadsynthplug): non-blocking, polyphonic synthesis on the Macropad
- [deckerego/Macropad_4chord_MIDI](https://github.com/deckerego/Macropad_4chord_MIDI): designing so you can't play a wrong note
- Adafruit's [Simon game for Circuit Playground](https://learn.adafruit.com/simon-game-clone-with-circuitplayground-express-and-circuitpython): the classic echo game
- [analogsketchbook/Macropad-Sequencer](https://github.com/analogsketchbook/Macropad-Sequencer): step-sequencer layout ideas (no code borrowed)
- Adafruit's [Dragon Drop](https://learn.adafruit.com/dragon-drop-a-circuitpython-game-for-macropad): a game loop with OLED graphics

## License

[MIT](LICENSE)
