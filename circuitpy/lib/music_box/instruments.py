"""Instrument and drum sounds, built from synthio waveforms and envelopes.

Device-only (needs synthio). Tune the numbers here by ear.
"""

import math
import random
from array import array

import synthio

SAMPLES = 256


def _wave(fn):
    return array("h", [int(32000 * fn(i / SAMPLES)) for i in range(SAMPLES)])


SINE = _wave(lambda t: math.sin(2 * math.pi * t))
# A sine with a quieter octave and twelfth on top rings more like a bell.
BELLISH = _wave(
    lambda t: (
        0.6 * math.sin(2 * math.pi * t)
        + 0.25 * math.sin(4 * math.pi * t)
        + 0.15 * math.sin(6 * math.pi * t)
    )
)
SQUARE = _wave(lambda t: 0.5 if t < 0.5 else -0.5)
TRIANGLE = _wave(lambda t: 4 * t - 1 if t < 0.5 else 3 - 4 * t)
NOISE = array("h", [random.randint(-24000, 24000) for _ in range(SAMPLES)])

# name: (waveform, envelope, amplitude)
INSTRUMENTS = {
    "flute": (
        SINE,
        synthio.Envelope(attack_time=0.03, decay_time=0.1, sustain_level=0.8, release_time=0.2),
        0.6,
    ),
    "bell": (
        BELLISH,
        synthio.Envelope(attack_time=0.002, decay_time=1.2, sustain_level=0.0, release_time=0.8),
        0.7,
    ),
    "robot": (
        SQUARE,
        synthio.Envelope(attack_time=0.01, decay_time=0.05, sustain_level=0.7, release_time=0.1),
        0.4,
    ),
    "pluck": (
        TRIANGLE,
        synthio.Envelope(attack_time=0.002, decay_time=0.5, sustain_level=0.0, release_time=0.2),
        0.8,
    ),
    "boop": (
        SINE,
        synthio.Envelope(attack_time=0.05, decay_time=0.2, sustain_level=0.0, release_time=0.2),
        0.3,
    ),
}

_KICK_ENV = synthio.Envelope(attack_time=0.001, decay_time=0.25, sustain_level=0.0)
_SNARE_ENV = synthio.Envelope(attack_time=0.001, decay_time=0.15, sustain_level=0.0)
_SHAKER_ENV = synthio.Envelope(attack_time=0.001, decay_time=0.04, sustain_level=0.0)
# Pitch falls from +1.5 octaves to 0 in ~60ms: the "thump" of a kick drum.
_DROP = array("h", [32767, 0])


def instrument_note(hz, name):
    waveform, envelope, amplitude = INSTRUMENTS[name]
    return synthio.Note(hz, waveform=waveform, envelope=envelope, amplitude=amplitude)


def drum_note(name):
    if name == "kick":
        bend = synthio.LFO(waveform=_DROP, rate=16, scale=1.5, once=True)
        return synthio.Note(110, waveform=SINE, envelope=_KICK_ENV, bend=bend, amplitude=1.0)
    if name == "snare":
        return synthio.Note(180, waveform=NOISE, envelope=_SNARE_ENV, amplitude=0.6)
    return synthio.Note(900, waveform=NOISE, envelope=_SHAKER_ENV, amplitude=0.4)
