import pytest

from music_box.colors import key_color
from music_box.icons import ICONS, SIZE
from music_box.modes.beat import Beat
from music_box.modes.echo import Echo
from music_box.modes.follow import Follow
from music_box.modes.piano import Piano
from music_box.songs import SONGS
from music_box.theory import PIANO_NOTES, SONG_NOTES, midi_to_hz, note_to_midi


def test_note_names():
    assert note_to_midi("C4") == 60
    assert note_to_midi("A4") == 69
    assert note_to_midi("F#3") == 54
    assert note_to_midi("Bb4") == 70


def test_a440():
    assert midi_to_hz(69) == pytest.approx(440)
    assert midi_to_hz(81) == pytest.approx(880)


def test_piano_goes_up_by_pentatonic_steps():
    assert len(PIANO_NOTES) == 12
    assert PIANO_NOTES[:6] == [60, 62, 64, 67, 69, 72]
    assert PIANO_NOTES == sorted(PIANO_NOTES)


@pytest.mark.parametrize("icon,notes", SONGS)
def test_every_song_note_has_a_key(icon, notes):
    for name in notes.split():
        assert note_to_midi(name) in SONG_NOTES, name


def test_keys_have_distinct_colors():
    assert len({key_color(k) for k in range(12)}) == 12


def test_icons_are_square():
    for name, rows in ICONS.items():
        assert len(rows) == SIZE, name
        assert all(len(r) == SIZE and set(r) <= {"#", "."} for r in rows), name


def test_every_icon_a_mode_uses_exists():
    for mode in (Piano, Follow, Echo, Beat):
        assert mode.icon in ICONS
        for icon, _ in mode.options:
            assert icon in ICONS
