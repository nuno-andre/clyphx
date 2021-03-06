# -*- coding: utf-8 -*-
# This file is part of ClyphX.
#
# ClyphX is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# ClyphX is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ClyphX.  If not, see <https://www.gnu.org/licenses/>.
from __future__ import absolute_import, unicode_literals
from builtins import map, dict
from typing import TYPE_CHECKING
# from fraction import Fraction
import logging

from _Generic.Devices import DEVICE_DICT, DEVICE_BOB_DICT

from . import __version__
from .core.live import (GridQuantization,
                        MixerDevice,
                        RecordingQuantization,
                        WarpMode,
                        get_application)

if TYPE_CHECKING:
    from typing import Any, Optional, Sequence, Text, Mapping, TypeVar
    from .core.live import Application
    T = TypeVar('T')

log = logging.getLogger(__name__)
app = get_application()  # type: Application
unset = object()

LIVE_VERSION = (app.get_major_version(),
                app.get_minor_version(),
                app.get_bugfix_version())

if LIVE_VERSION < (9, 6, 0):
    raise RuntimeError('Live releases earlier than 9.6 are not supported')

SCRIPT_NAME = 'ClyphX'
SCRIPT_INFO = '{} v{}'.format(SCRIPT_NAME, '.'.join(map(str, __version__)))

KEYWORDS = dict(ON=1, OFF=0)  # type: Mapping[Optional[Text], bool]


def switch(obj, attr, value, fallback=unset):
    # type: (T, Text, Text, Any) -> None
    '''Turns object attribute on/off or toggles (if there is no fallback).
    '''
    try:
        v = KEYWORDS[value.upper().strip()]
    except (AttributeError, KeyError):
        v = (not getattr(obj, attr)) if fallback is unset else fallback
    setattr(obj, attr, v)


ONOFF = dict(ON=True, OFF=False)  # type: Mapping[Text, bool]

NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')

ENV_TYPES = (
    'IRAMP',    # Linear increasing ramp
    'DRAMP',    # Linear decreasing ramp
    'IPYR',     # Linear increase until midpoint and then linear decrease
    'DPYR',     # Linear decrease until midpoint and then linear increase
    'SAW',      # Saw wave synced to 1/4 notes
    'SQR',      # Square wave synced to 1/4 notes
    # 'TRI',      # Triangle wave synced to 1/4 notes
)

MIDI_STATUS = dict(
    NOTE  = 144,
    CC    = 176,
    PC    = 192,  # program change
    CA    = 208,  # channel aftertouch
    PB    = 224,  # pitch bend change
    SYSEX = 240,
)  # type: Mapping[Text, int]

WARP_MODES = dict((
    ('BEATS',       WarpMode.beats),
    ('TONES',       WarpMode.tones),
    ('TEXTURE',     WarpMode.texture),
    ('RE-PITCH',    WarpMode.repitch),
    ('COMPLEX',     WarpMode.complex),
    # ('RECYCLE',     WarpMode.rex),  # not implemented
    ('COMPLEX PRO', WarpMode.complex_pro),
    # ('COUNT',       WarpMode.count),
))  # type: Mapping[Text, int]

# region STATES
XFADE_STATES = dict(
    A   = MixerDevice.crossfade_assignments.A,
    OFF = MixerDevice.crossfade_assignments.NONE,
    B   = MixerDevice.crossfade_assignments.B,
)  # type: Mapping[Text, int]

MON_STATES = dict(
    IN   = 0,
    AUTO = 1,
    OFF  = 2,
)  # type: Mapping[Text, int]

LOOPER_STATES = dict(
    STOP = 0.0,
    REC  = 1.0,
    PLAY = 2.0,
    OVER = 3.0,
)  # type: Mapping[Text, float]

# TODO: check gq, rq,r_qnrz, and clip_grid uses
# XXX: bars vs beats
GQ_STATES = dict((
    ('NONE',   0),
    ('8 BAR',  1),
    ('4 BAR',  2),
    ('2 BAR',  3),
    ('1 BAR',  4),
    ('1/2',    5),
    ('1/2T',   6),
    ('1/4',    7),
    ('1/4T',   8),
    ('1/8',    9),
    ('1/8T',   10),
    ('1/16',   11),
    ('1/16T',  12),
    ('1/32',   13),
    # alias
    ('8 BARS', 1),
    ('4 BARS', 2),
    ('2 BARS', 3),
))  # type: Mapping[Text, int]

RQ_STATES = dict((
    ('NONE',         0),
    ('1/4',          1),
    ('1/8',          2),
    ('1/8T',         3),
    ('1/8 + 1/8T',   4),
    ('1/16',         5),
    ('1/16T',        6),
    ('1/16 + 1/16T', 7),
    ('1/32',         8),
))  # type: Mapping[Text, int]

R_QNTZ_STATES = dict((
    ('1/4',          RecordingQuantization.rec_q_quarter),
    ('1/8',          RecordingQuantization.rec_q_eight),
    ('1/8T',         RecordingQuantization.rec_q_eight_triplet),
    ('1/8 + 1/8T',   RecordingQuantization.rec_q_eight_eight_triplet),
    ('1/16',         RecordingQuantization.rec_q_sixtenth),
    ('1/16T',        RecordingQuantization.rec_q_sixtenth_triplet),
    ('1/16 + 1/16T', RecordingQuantization.rec_q_sixtenth_sixtenth_triplet),
    ('1/32',         RecordingQuantization.rec_q_thirtysecond),
))  # type: Mapping[Text, int]

CLIP_GRID_STATES = dict((
    ('OFF',    GridQuantization.no_grid),
    ('8 BAR',  GridQuantization.g_8_bars),
    ('4 BAR',  GridQuantization.g_4_bars),
    ('2 BAR',  GridQuantization.g_2_bars),
    ('1 BAR',  GridQuantization.g_bar),
    ('1/2',    GridQuantization.g_half),
    ('1/4',    GridQuantization.g_quarter),
    ('1/8',    GridQuantization.g_eighth),
    ('1/16',   GridQuantization.g_sixteenth),
    ('1/32',   GridQuantization.g_thirtysecond),
    # alias
    ('8 BARS', GridQuantization.g_8_bars),
    ('4 BARS', GridQuantization.g_4_bars),
    ('2 BARS', GridQuantization.g_2_bars),
))  # type: Mapping[Text, int]

REPEAT_STATES = dict((
    ('OFF',   1.0),
    ('1/4',   1.0),
    ('1/4T',  0.666666666667),
    ('1/8',   0.5),
    ('1/8T',  0.333333333333),
    ('1/16',  0.25),
    ('1/16T', 0.166666666667),
    ('1/32',  0.125),
    ('1/32T', 0.0833333333333),
))  # type: Mapping[Text, float]

# REPEAT_STATES = dict((
#     ('OFF',   Fraction(1, 1)),
#     ('1/4',   Fraction(1, 1)),
#     ('1/4T',  Fraction(2, 3)),
#     ('1/8',   Fraction(1, 2)),
#     ('1/8T',  Fraction(1, 3)),
#     ('1/16',  Fraction(1, 4)),
#     ('1/16T', Fraction(1, 6)),
#     ('1/32',  Fraction(1, 8)),
#     ('1/32T', Fraction(1, 12)),
# ))  # type: Mapping[Text, Fraction]

# endregion

# region DEVICES
_AUDIO_DEVS = (
    'Simple Delay',
    'Overdrive',
    'Looper',
    'Auto Filter',
    'External Audio Effect',
    'Saturator',
    'Phaser',
    'Vinyl Distortion',
    'Dynamic Tube',
    'Beat Repeat',
    'Multiband Dynamics',
    'Cabinet',
    'Audio Effect Rack',
    'Flanger',
    'Gate',
    'Reverb',
    'Grain Delay',
    'Redux',
    'Ping Pong Delay',
    'Spectrum',
    'Compressor',
    'Vocoder',
    'Amp',
    'Glue Compressor',
    'Erosion',
    'EQ Three',
    'EQ Eight',
    'Resonators',
    'Frequency Shifter',
    'Auto Pan',
    'Chorus',
    'Limiter',
    'Corpus',
    'Filter Delay',
    'Utility',
)  # type: Sequence[Text]

_INS_DEVS = (
    'Tension',
    'External Instrument',
    'Electric',
    'Instrument Rack',
    'Drum Rack',
    'Collision',
    'Impulse',
    'Sampler',
    'Operator',
    'Analog',
    'Simpler',
)  # type: Sequence[Text]

_MIDI_DEVS = (
    'Note Length',
    'Chord',
    'Random',
    'MIDI Effect Rack',
    'Scale',
    'Pitch',
    'Arpeggiator',
    'Velocity',
)  # type: Sequence[Text]

AUDIO_DEVS = dict((dev.upper(), dev) for dev in _AUDIO_DEVS)

INS_DEVS = dict((dev.upper(), dev) for dev in _INS_DEVS)

MIDI_DEVS = dict((dev.upper(), dev) for dev in _MIDI_DEVS)

# TODO: Wavetable, Ping Pong Delay
# TODO: update previous dicts
#: Translation table between API names and friendly names.
DEV_NAME_TRANSLATION = dict(
    UltraAnalog            = 'Analog',
    MidiArpeggiator        = 'Arpeggiator',
    AudioEffectGroupDevice = 'Audio Effect Rack',
    AutoFilter             = 'Auto Filter',
    AutoPan                = 'Auto Pan',
    BeatRepeat             = 'Beat Repeat',
    MidiChord              = 'Chord',
    Compressor2            = 'Compressor',
    DrumBuss               = 'Drum Buss',
    DrumGroupDevice        = 'Drum Rack',
    Tube                   = 'Dynamic Tube',
    LoungeLizard           = 'Electric',
    Eq8                    = 'EQ Eight',
    FilterEQ3              = 'EQ Three',
    FilterDelay            = 'Filter Delay',
    FrequencyShifter       = 'Frequency Shifter',
    GlueCompressor         = 'Glue Compressor',
    GrainDelay             = 'Grain Delay',
    InstrumentImpulse      = 'Impulse',
    InstrumentGroupDevice  = 'Instrument Rack',
    MidiEffectGroupDevice  = 'MIDI Effect Rack',
    MultibandDynamics      = 'Multiband Dynamics',
    MidiNoteLength         = 'Note Length',
    MidiPitcher            = 'Pitch',
    MidiRandom             = 'Random',
    Resonator              = 'Resonators',
    MultiSampler           = 'Sampler',
    MidiScale              = 'Scale',
    CrossDelay             = 'Simple Delay',  # FIXME: missing
    OriginalSimpler        = 'Simpler',
    SpectrumAnalyzer       = 'Spectrum',
    StringStudio           = 'Tension',
    StereoGain             = 'Utility',
    MidiVelocity           = 'Velocity',
    Vinyl                  = 'Vinyl Distortion',
)

# BoB is B0, device banks have the index of its label 'B1' = 1, ...
DEVICE_BANKS = dict()
for device, banks in DEVICE_DICT.items():
    DEVICE_BANKS[device] = DEVICE_BOB_DICT[device] + banks

# endregion
