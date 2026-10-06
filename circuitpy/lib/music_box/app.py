"""Routes button presses to the active mode and handles going to sleep.

Same controls everywhere: press the dial for the next mode, turn the dial
to change that mode's one setting.
"""

from music_box import fx
from music_box.timeline import Timeline


class App:
    def __init__(self, io, modes, sleep_ms):
        self.io = io
        self.modes = modes
        self.sleep_ms = sleep_ms
        self.index = 0
        self.asleep = False
        self.last_input = 0
        self.timeline = Timeline()

    @property
    def mode(self):
        return self.modes[self.index]

    def start(self, now):
        self.last_input = now
        self.mode.enter(now)

    def key(self, key, pressed, now):
        # The press that wakes the toy only wakes it. Its release is passed
        # through; every mode treats a stray release as harmless.
        if self.woke(now):
            return
        self.mode.key(key, pressed, now)

    def dial(self, delta, now):
        if not self.woke(now):
            self.mode.dial(delta, now)

    def dial_press(self, now):
        if self.woke(now):
            return
        self.mode.exit()
        self.index = (self.index + 1) % len(self.modes)
        self.mode.enter(now)
        fx.jingle(self.io, self.timeline, now)

    def woke(self, now):
        """Note activity; returns True if this input was used to wake up."""
        self.last_input = now
        if not self.asleep:
            return False
        self.asleep = False
        self.io.wake()
        self.mode.enter(now)
        return True

    def tick(self, now):
        if self.asleep:
            return
        if now - self.last_input >= self.sleep_ms:
            self.asleep = True
            self.timeline.clear()
            self.mode.exit()
            self.io.sleep()
            return
        self.timeline.tick(now)
        self.mode.tick(now)
