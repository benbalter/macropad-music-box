"""Follow the Lights: the next note of a song glows; press it to play it.

STEM idea: a song is a sequence, one step after another.
The dial picks the song. Pressing a different key still plays its note
(it's still a piano), it just doesn't move the song along.
"""

from music_box import fx
from music_box.colors import OFF, WHITE, dim, key_color
from music_box.modes.base import Mode
from music_box.songs import SONGS
from music_box.theory import SONG_NOTES, midi_to_hz, note_to_midi


def song_keys(notes):
    return [SONG_NOTES.index(note_to_midi(n)) for n in notes.split()]


class Follow(Mode):
    icon = "follow"
    options = tuple((icon, song_keys(notes)) for icon, notes in SONGS)

    def __init__(self, io):
        super().__init__(io)
        self.step = 0
        self.held = set()
        self.partying = False

    @property
    def target(self):
        return self.value[self.step]

    def enter(self, now):
        super().enter(now)
        self.restart()

    def setting_changed(self, now):
        self.timeline.clear()
        self.restart()

    def restart(self):
        self.step = 0
        self.partying = False
        self.light_target()

    def light_target(self):
        self.io.fill(OFF)
        self.io.pixel(self.target, key_color(self.target))

    def key(self, key, pressed, now):
        if self.partying:
            return
        if pressed:
            self.held.add(key)
            self.io.note_on(key, midi_to_hz(SONG_NOTES[key]), "flute")
            if key == self.target:
                self.io.pixel(key, WHITE)
                self.step += 1
            else:
                self.io.pixel(key, dim(key_color(key), 0.3))
            return

        self.held.discard(key)
        self.io.note_off(key)
        if self.held:
            return
        if self.step == len(self.value):
            self.partying = True
            done = fx.celebrate(self.io, self.timeline, now + 200)
            self.timeline.at(done + 800, self.restart)
        else:
            self.light_target()
