"""Echo: the toy plays a little pattern, then you play it back.

STEM idea: memory and patterns. It starts with one note and adds one each
time you get it right. A miss just replays the pattern, no penalty.
The dial picks how many keys are in the game.
"""

import random

from music_box import fx
from music_box.colors import OFF, WHITE, dim, key_color
from music_box.modes.base import Mode
from music_box.theory import PIANO_NOTES, midi_to_hz

WIN_LENGTH = 8
NOTE_MS = 450
GAP_MS = 200


class Echo(Mode):
    icon = "echo"
    options = (
        ("keys4", (0, 2, 9, 11)),
        ("keys6", (0, 1, 2, 9, 10, 11)),
        ("keys12", tuple(range(12))),
    )

    def __init__(self, io, choice=random.choice):
        super().__init__(io)
        self.choice = choice
        self.pattern = []
        self.position = 0
        self.listening = False
        self.held = set()

    def enter(self, now):
        super().enter(now)
        self.new_game(now)

    def setting_changed(self, now):
        self.new_game(now)

    def new_game(self, now):
        self.timeline.clear()
        self.io.all_notes_off()
        self.pattern = [self.choice(self.value)]
        self.show_pattern(now + 600)

    def show_pattern(self, start):
        self.listening = False
        self.timeline.at(start, lambda: self.io.fill(OFF))
        t = start + 150
        for key in self.pattern:
            self.timeline.at(t, lambda k=key: self.play(k, WHITE))
            self.timeline.at(t + NOTE_MS, lambda k=key: self.stop(k, OFF))
            t += NOTE_MS + GAP_MS
        self.timeline.at(t, self.listen)

    def listen(self):
        self.listening = True
        self.position = 0
        for key in self.value:
            self.io.pixel(key, dim(key_color(key)))

    def play(self, key, color):
        self.io.note_on(key, midi_to_hz(PIANO_NOTES[key]), "bell")
        self.io.pixel(key, color)

    def stop(self, key, color):
        self.io.note_off(key)
        self.io.pixel(key, color)

    def key(self, key, pressed, now):
        if not pressed:
            # Stop notes the player started, even if the pattern finished on this press.
            if key in self.held:
                self.held.discard(key)
                self.io.note_off(key)
            if self.listening and key in self.value:
                self.io.pixel(key, dim(key_color(key)))
            return
        if not self.listening or key not in self.value:
            return

        if key != self.pattern[self.position]:
            self.listening = False
            self.io.note_on("fx", midi_to_hz(64), "boop")
            self.timeline.at(now + 300, lambda: self.io.note_off("fx"))
            self.show_pattern(now + 900)
            return

        self.play(key, key_color(key))
        self.held.add(key)
        self.position += 1
        if self.position < len(self.pattern):
            return

        self.listening = False
        if len(self.pattern) >= WIN_LENGTH:
            done = fx.celebrate(self.io, self.timeline, now + 400)
            self.timeline.at(done + 600, lambda: self.new_game(done + 600))
        else:
            self.pattern.append(self.choice(self.value))
            self.show_pattern(now + 900)
