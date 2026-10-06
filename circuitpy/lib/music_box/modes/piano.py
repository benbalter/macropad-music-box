"""Rainbow Piano: every key is a note, low (top-left) to high (bottom-right).

STEM idea: pitch. Keys further along are higher notes (faster vibrations).
The dial picks the instrument sound.
"""

from music_box.colors import dim, key_color
from music_box.modes.base import Mode
from music_box.theory import PIANO_NOTES, midi_to_hz

PREVIEW_KEY = 5  # a middle note, played when the instrument changes


class Piano(Mode):
    icon = "piano"
    options = (("flute", "flute"), ("bell", "bell"), ("robot", "robot"), ("guitar", "pluck"))

    def enter(self, now):
        super().enter(now)
        for key in range(12):
            self.io.pixel(key, dim(key_color(key)))

    def key(self, key, pressed, now):
        if pressed:
            self.io.note_on(key, midi_to_hz(PIANO_NOTES[key]), self.value)
            self.io.pixel(key, key_color(key))
        else:
            self.io.note_off(key)
            self.io.pixel(key, dim(key_color(key)))

    def setting_changed(self, now):
        hz = midi_to_hz(PIANO_NOTES[PREVIEW_KEY])
        self.timeline.clear()
        self.io.note_on("fx", hz, self.value)
        self.timeline.at(now + 300, lambda: self.io.note_off("fx"))
