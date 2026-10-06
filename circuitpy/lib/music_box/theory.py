"""Music math: note names, frequencies, and the key layouts the modes use.

Keys are numbered 0-11 in reading order (top-left is 0), so pitch always
goes up as you read the keypad left to right, top to bottom.
"""

LETTERS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

PENTATONIC = (0, 2, 4, 7, 9)


def note_to_midi(name):
    """Convert a note name like "C4" or "F#3" to a MIDI note number."""
    offset = LETTERS[name[0]]
    rest = name[1:]
    if rest[0] == "#":
        offset += 1
        rest = rest[1:]
    elif rest[0] == "b":
        offset -= 1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + offset


def midi_to_hz(midi):
    """Equal temperament, A4 = 440 Hz."""
    return 440.0 * 2 ** ((midi - 69) / 12)


def scale(root, steps, count):
    """The first `count` notes of a scale starting at MIDI note `root`."""
    return [root + 12 * (i // len(steps)) + steps[i % len(steps)] for i in range(count)]


# Pentatonic has no "wrong" notes: any keys pressed together sound nice.
PIANO_NOTES = scale(note_to_midi("C4"), PENTATONIC, 12)

# The white keys from G to D cover every song in songs.py.
SONG_NOTES = [note_to_midi(n) for n in "G4 A4 B4 C5 D5 E5 F5 G5 A5 B5 C6 D6".split()]
