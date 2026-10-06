"""What every mode has in common.

Modes never touch hardware. They call methods on `io`, which is the real
Macropad on the device (hardware.Macropad) and a recorder in tests:

    io.note_on(voice, hz, instrument)  io.note_off(voice)  io.all_notes_off()
    io.drum(name)
    io.pixel(key, color)  io.fill(color)
    io.show(mode_icon, setting_icon, index, count)

`voice` is any label (a key number, "fx", ...); starting a voice that is
already sounding replaces it. Times are in milliseconds.
"""

from music_box.timeline import Timeline


class Mode:
    icon = ""
    # One (icon, value) pair per dial position.
    options = (("", None),)

    def __init__(self, io):
        self.io = io
        self.timeline = Timeline()
        self.setting = 0

    @property
    def value(self):
        return self.options[self.setting][1]

    def enter(self, now):
        """Called when the mode becomes active (also after waking up)."""
        self.refresh_screen()

    def exit(self):
        self.timeline.clear()
        self.io.all_notes_off()
        self.io.fill((0, 0, 0))

    def key(self, key, pressed, now):
        pass

    def dial(self, delta, now):
        self.setting = (self.setting + delta) % len(self.options)
        self.refresh_screen()
        self.setting_changed(now)

    def setting_changed(self, now):
        pass

    def tick(self, now):
        self.timeline.tick(now)

    def refresh_screen(self):
        self.io.show(self.icon, self.options[self.setting][0], self.setting, len(self.options))
