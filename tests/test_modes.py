from music_box.app import App
from music_box.colors import OFF
from music_box.modes.beat import Beat
from music_box.modes.echo import WIN_LENGTH, Echo
from music_box.modes.follow import Follow
from music_box.modes.piano import Piano


def run(mode, start, end, step=10):
    for t in range(start, end, step):
        mode.tick(t)


# --- Piano ---


def test_piano_key_plays_and_lights(io):
    piano = Piano(io)
    piano.enter(0)
    piano.key(0, True, 0)
    piano.key(11, True, 0)
    assert set(io.sounding) == {0, 11}
    assert io.sounding[11][0] > io.sounding[0][0]  # higher key, higher pitch
    piano.key(0, False, 10)
    assert set(io.sounding) == {11}


def test_piano_dial_changes_instrument(io):
    piano = Piano(io)
    piano.enter(0)
    piano.dial(1, 0)
    assert io.screen == ("piano", "bell", 1, 4)
    piano.key(3, True, 0)
    assert io.sounding[3][1] == "bell"
    piano.dial(-2, 0)
    assert io.screen[1] == "guitar"  # wraps around


# --- Follow the Lights ---


def press(mode, key, now):
    mode.key(key, True, now)
    mode.key(key, False, now + 50)


def test_follow_lights_the_next_note(io):
    follow = Follow(io)
    follow.enter(0)
    assert io.lit() == [follow.target]


def test_follow_advances_only_on_the_lit_key(io):
    follow = Follow(io)
    follow.enter(0)
    first = follow.target
    wrong = (first + 1) % 12
    press(follow, wrong, 0)
    assert follow.step == 0
    press(follow, first, 100)
    assert follow.step == 1


def test_follow_plays_a_whole_song_then_celebrates(io):
    follow = Follow(io)
    follow.enter(0)
    t = 0
    for key in follow.value:
        press(follow, key, t)
        t += 100
    assert follow.partying
    run(follow, t, t + 5000)
    assert not follow.partying
    assert follow.step == 0


def test_follow_dial_switches_song(io):
    follow = Follow(io)
    follow.enter(0)
    press(follow, follow.target, 0)
    follow.dial(1, 100)
    assert follow.step == 0
    assert io.screen[1] == "sheep"


# --- Echo ---


def first_choice(keys):
    return keys[0]


def test_echo_shows_then_listens(io):
    echo = Echo(io, choice=first_choice)
    echo.enter(0)
    assert not echo.listening
    run(echo, 0, 3000)
    assert echo.listening
    assert echo.pattern == [0]


def test_echo_grows_when_copied(io):
    echo = Echo(io, choice=first_choice)
    echo.enter(0)
    run(echo, 0, 3000)
    press(echo, 0, 3000)
    assert len(echo.pattern) == 2
    run(echo, 3000, 8000)
    assert echo.listening


def test_echo_miss_replays_same_pattern(io):
    echo = Echo(io, choice=first_choice)
    echo.enter(0)
    run(echo, 0, 3000)
    press(echo, 2, 3000)
    assert echo.pattern == [0]
    assert not echo.listening
    run(echo, 3000, 6000)
    assert echo.listening
    assert echo.position == 0


def test_echo_ignores_keys_not_in_play(io):
    echo = Echo(io, choice=first_choice)
    echo.enter(0)
    run(echo, 0, 3000)
    press(echo, 5, 3000)  # middle key isn't in the 4-key game
    assert echo.listening
    assert echo.position == 0


def test_echo_release_stops_note_even_after_pattern_done(io):
    echo = Echo(io, choice=first_choice)
    echo.enter(0)
    run(echo, 0, 3000)
    echo.key(0, True, 3000)
    assert 0 in io.sounding
    echo.key(0, False, 3200)
    assert 0 not in io.sounding


def test_echo_celebrates_and_restarts_after_win(io):
    echo = Echo(io, choice=first_choice)
    echo.enter(0)
    t = 0
    while True:
        t += 10
        echo.tick(t)
        if not echo.listening:
            continue
        if len(echo.pattern) == WIN_LENGTH:
            break
        for key in list(echo.pattern):
            press(echo, key, t)
    for key in echo.pattern:
        press(echo, key, t)
    run(echo, t, t + 10000)
    assert len(echo.pattern) == 1


def test_echo_dial_changes_keys(io):
    echo = Echo(io, choice=first_choice)
    echo.enter(0)
    echo.dial(2, 0)
    assert io.screen[1] == "keys12"
    run(echo, 0, 3000)
    assert io.lit() == list(range(12))


# --- Beat Loop ---


def test_beat_loops_through_steps(io):
    beat = Beat(io)
    beat.enter(0)
    interval = beat.value
    run(beat, 0, interval * 4, step=interval)
    assert io.drums == ["kick", "kick"]  # default pattern: kick on steps 1 and 3
    assert beat.step == 3


def test_beat_toggle_adds_a_drum(io):
    beat = Beat(io)
    beat.enter(0)
    beat.key(1, True, 0)  # step 1, snare
    assert beat.grid[0][1]
    assert io.drums == ["snare"]  # plays immediately so you hear what you added
    beat.key(1, True, 10)
    assert not beat.grid[0][1]


def test_beat_tempo_from_dial(io):
    beat = Beat(io)
    beat.enter(0)
    slow = beat.value
    beat.dial(1, 0)
    assert beat.value < slow
    assert io.screen[1] == "rabbit"


def test_beat_resyncs_after_falling_behind(io):
    beat = Beat(io)
    beat.enter(0)
    beat.tick(0)
    beat.tick(100_000)
    assert beat.next_step_at > 100_000


# --- App ---


def make_app(io):
    modes = [Piano(io), Follow(io), Echo(io), Beat(io)]
    app = App(io, modes, sleep_ms=60_000)
    app.start(0)
    return app


def test_dial_press_cycles_modes(io):
    app = make_app(io)
    names = []
    for i in range(5):
        names.append(type(app.mode).__name__)
        app.dial_press(i * 100)
    assert names == ["Piano", "Follow", "Echo", "Beat", "Piano"]


def test_mode_change_plays_jingle(io):
    app = make_app(io)
    app.dial_press(0)
    for t in range(0, 600, 10):
        app.tick(t)
    assert ("on", "fx") in io.log


def test_sleeps_when_idle_and_wakes_on_key(io):
    app = make_app(io)
    app.tick(59_000)
    assert io.awake
    app.tick(60_000)
    assert not io.awake
    assert io.lit() == []
    app.key(4, True, 70_000)
    assert io.awake
    assert 4 not in io.sounding  # the waking press doesn't play a note
    app.key(4, True, 70_100)
    assert 4 in io.sounding


def test_input_resets_sleep_timer(io):
    app = make_app(io)
    app.dial(1, 50_000)
    app.tick(100_000)
    assert io.awake


def test_mode_exit_clears_lights(io):
    app = make_app(io)
    app.dial_press(0)
    app.dial_press(0)
    app.dial_press(0)  # into Beat
    app.tick(0)
    app.dial_press(10)  # back to Piano: no Beat lights left behind
    assert all(c != OFF for c in io.pixels)  # piano dims every key
    assert io.drums == ["kick"]
