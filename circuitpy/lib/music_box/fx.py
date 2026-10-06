"""Little shared shows: the mode-change jingle and the "you did it!" party."""

from music_box.colors import OFF, key_color
from music_box.theory import midi_to_hz, note_to_midi

JINGLE = ("C5", "E5", "G5")
PARTY = ("C5", "E5", "G5", "C6", "G5", "C6")


def play_notes(io, timeline, now, names, step=110, instrument="bell"):
    for i, name in enumerate(names):
        hz = midi_to_hz(note_to_midi(name))
        start = now + i * step
        timeline.at(start, lambda hz=hz: io.note_on("fx", hz, instrument))
    timeline.at(now + len(names) * step + step, lambda: io.note_off("fx"))


def jingle(io, timeline, now):
    play_notes(io, timeline, now, JINGLE, step=90)


def celebrate(io, timeline, now):
    """A rainbow chase around the keys with a happy arpeggio. Lasts ~2s."""
    play_notes(io, timeline, now, PARTY, step=150, instrument="bell")
    for frame in range(24):
        timeline.at(now + frame * 80, lambda f=frame: _rainbow(io, f))
    timeline.at(now + 24 * 80, lambda: io.fill(OFF))
    return now + 24 * 80


def _rainbow(io, frame):
    for key in range(12):
        io.pixel(key, key_color((key + frame) % 12))
