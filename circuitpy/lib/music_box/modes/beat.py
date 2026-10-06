"""Beat Loop: a 4-step drum machine.

Each row is one step of the loop (top to bottom) and each column is a drum:
left = kick, middle = snare, right = shaker. Tap a key to turn it on or off;
the bright row shows where the loop is right now.

STEM idea: loops and patterns, the same idea as a `for` loop in code.
The dial picks the tempo, from turtle to rabbit.
"""

from music_box.colors import OFF, dim
from music_box.modes.base import Mode

DRUMS = ("kick", "snare", "shaker")
DRUM_COLORS = ((255, 0, 0), (255, 160, 0), (0, 80, 255))
PLAYHEAD = (40, 40, 40)
STEPS = 4


class Beat(Mode):
    icon = "drum"
    # Milliseconds per step.
    options = (("turtle", 600), ("turtle", 480), ("drum", 380), ("rabbit", 300), ("rabbit", 230))

    def __init__(self, io):
        super().__init__(io)
        self.setting = 2
        # Start with a kick on the beat so it's obviously a loop.
        self.grid = [[step % 2 == 0, False, False] for step in range(STEPS)]
        self.step = 0
        self.next_step_at = 0

    def enter(self, now):
        super().enter(now)
        self.step = STEPS - 1
        self.next_step_at = now

    def key(self, key, pressed, now):
        if not pressed:
            return
        step, drum = divmod(key, 3)
        self.grid[step][drum] = not self.grid[step][drum]
        if self.grid[step][drum]:
            self.io.drum(DRUMS[drum])
        self.draw()

    def tick(self, now):
        super().tick(now)
        if now < self.next_step_at:
            return
        self.step = (self.step + 1) % STEPS
        for drum, on in enumerate(self.grid[self.step]):
            if on:
                self.io.drum(DRUMS[drum])
        self.draw()
        self.next_step_at += self.value
        if self.next_step_at <= now:  # fell behind (e.g. after sleep); resync
            self.next_step_at = now + self.value

    def draw(self):
        for step in range(STEPS):
            for drum in range(3):
                key = step * 3 + drum
                if self.grid[step][drum]:
                    color = DRUM_COLORS[drum]
                    self.io.pixel(key, color if step == self.step else dim(color, 0.25))
                else:
                    self.io.pixel(key, PLAYHEAD if step == self.step else OFF)
