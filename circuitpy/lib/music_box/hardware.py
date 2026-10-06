"""The real Macropad: keys, dial, lights, speaker, and screen.

This is the `io` object modes talk to (see modes/base.py). It uses
CircuitPython's core modules directly rather than adafruit_macropad, whose
sound calls block and which keeps the speaker pin for itself.
"""

import time

import audiomixer
import audiopwmio
import board
import digitalio
import keypad
import neopixel
import rotaryio
import synthio

from music_box.instruments import drum_note, instrument_note
from music_box.screen import Screen

SAMPLE_RATE = 22050
# Turn the amplifier off after this much silence: the PWM output hisses
# through the speaker whenever the amp is on, even with nothing playing.
AMP_OFF_AFTER = 2.0
KEY_PINS = tuple(getattr(board, "KEY%d" % n) for n in range(1, 13))


class Macropad:
    def __init__(self, volume=40, brightness=30):
        self.keys = keypad.Keys(KEY_PINS, value_when_pressed=False, pull=True)
        self.button = keypad.Keys((board.BUTTON,), value_when_pressed=False, pull=True)
        self.encoder = rotaryio.IncrementalEncoder(board.ROTA, board.ROTB)
        self.last_position = -self.encoder.position

        self.pixels = neopixel.NeoPixel(
            board.NEOPIXEL, 12, brightness=brightness / 100, auto_write=False
        )
        self.dirty = False

        self.speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
        self.speaker_enable.switch_to_output(value=False)
        self.awake = True
        self.last_sound = 0.0
        self.audio = audiopwmio.PWMAudioOut(board.SPEAKER)
        # The mixer gives a master volume and a buffer that keeps audio smooth
        # while the screen redraws.
        self.mixer = audiomixer.Mixer(
            voice_count=1, sample_rate=SAMPLE_RATE, channel_count=1, buffer_size=2048
        )
        self.synth = synthio.Synthesizer(sample_rate=SAMPLE_RATE)
        self.audio.play(self.mixer)
        self.mixer.voice[0].play(self.synth)
        self.mixer.voice[0].level = volume / 100
        self.voices = {}

        self.screen = Screen(board.DISPLAY)

    def poll(self, app, now):
        """Read the keys and dial and hand any changes to the app."""
        event = self.keys.events.get()
        while event:
            app.key(event.key_number, event.pressed, now)
            event = self.keys.events.get()

        event = self.button.events.get()
        while event:
            if event.pressed:
                app.dial_press(now)
            event = self.button.events.get()

        # The encoder counts down when turned clockwise; flip it.
        position = -self.encoder.position
        if position != self.last_position:
            app.dial(position - self.last_position, now)
            self.last_position = position

    def flush(self):
        if self.dirty:
            self.pixels.show()
            self.dirty = False
        if (
            self.speaker_enable.value
            and not any(isinstance(v, int) for v in self.voices)  # no keys held
            and time.monotonic() - self.last_sound > AMP_OFF_AFTER
        ):
            self.speaker_enable.value = False

    def _sound(self):
        self.last_sound = time.monotonic()
        if self.awake:
            self.speaker_enable.value = True

    # --- the io interface used by modes ---

    def note_on(self, voice, hz, instrument):
        self.note_off(voice)
        note = instrument_note(hz, instrument)
        self.voices[voice] = note
        self._sound()
        self.synth.press(note)

    def note_off(self, voice):
        note = self.voices.pop(voice, None)
        if note is not None:
            self.synth.release(note)

    def all_notes_off(self):
        self.synth.release_all()
        self.voices = {}

    def drum(self, name):
        # Drums fade out on their own; release the last hit of the same drum
        # so a fast loop doesn't use up all of synthio's voices.
        self.note_off(("drum", name))
        note = drum_note(name)
        self.voices[("drum", name)] = note
        self._sound()
        self.synth.press(note)

    def pixel(self, key, color):
        self.pixels[key] = color
        self.dirty = True

    def fill(self, color):
        self.pixels.fill(color)
        self.dirty = True

    def show(self, mode_icon, setting_icon, index, count):
        self.screen.show(mode_icon, setting_icon, index, count)

    def sleep(self):
        self.all_notes_off()
        self.fill((0, 0, 0))
        self.flush()
        self.screen.sleep()
        self.awake = False
        self.speaker_enable.value = False

    def wake(self):
        self.awake = True
        self.screen.wake()
