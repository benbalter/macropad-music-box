import pytest


class FakeIO:
    """Records what modes ask the hardware to do."""

    def __init__(self):
        self.pixels = [(0, 0, 0)] * 12
        self.sounding = {}
        self.drums = []
        self.screen = None
        self.awake = True
        self.log = []

    def note_on(self, voice, hz, instrument):
        self.sounding[voice] = (hz, instrument)
        self.log.append(("on", voice))

    def note_off(self, voice):
        self.sounding.pop(voice, None)
        self.log.append(("off", voice))

    def all_notes_off(self):
        self.sounding = {}

    def drum(self, name):
        self.drums.append(name)

    def pixel(self, key, color):
        self.pixels[key] = color

    def fill(self, color):
        self.pixels = [color] * 12

    def show(self, mode_icon, setting_icon, index, count):
        self.screen = (mode_icon, setting_icon, index, count)

    def sleep(self):
        self.awake = False

    def wake(self):
        self.awake = True

    def lit(self):
        return [k for k, c in enumerate(self.pixels) if c != (0, 0, 0)]


@pytest.fixture
def io():
    return FakeIO()
