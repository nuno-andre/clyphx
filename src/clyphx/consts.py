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

from __future__ import unicode_literals
from builtins import map, dict

import Live

app = Live.Application.get_application()
LIVE_VERSION = (app.get_major_version(),
                app.get_minor_version(),
                app.get_bugfix_version())

if LIVE_VERSION < (9, 5, 0):
    raise RuntimeError('Live releases earlier than 9.5 are not supported')


SCRIPT_NAME = 'ClyphX'

SCRIPT_VERSION = (2, 7, 0)

SCRIPT_INFO = '{} v{}'.format(SCRIPT_NAME, '.'.join(map(str, SCRIPT_VERSION)))

KEYWORDS = dict(ON=1, OFF=0)

NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')

OCTAVE_NAMES = ('-2', '-1', '0', '1', '2', '3', '4', '5', '6', '7', '8')

ENV_TYPES = ('IRAMP', 'DRAMP', 'IPYR', 'DPYR', 'SQR', 'SAW')

# TODO: mode 5?
WARP_MODES = dict((
    ('BEATS',       0),
    ('TONES',       1),
    ('TEXTURE',     2),
    ('RE-PITCH',    3),
    ('COMPLEX',     4),
    ('COMPLEX PRO', 6),
))

# region STATES
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
))

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
))

XFADE_STATES = dict(
    A   = 0,
    OFF = 1,
    B   = 2,
)

MON_STATES = dict(
    IN   = 0,
    AUTO = 1,
    OFF  = 2,
)

LOOPER_STATES = dict(
    STOP = 0.0,
    REC  = 1.0,
    PLAY = 2.0,
    OVER = 3.0,
)

R_QNTZ_STATES = dict((
    ('1/4',          Live.Song.RecordingQuantization.rec_q_quarter),
    ('1/8',          Live.Song.RecordingQuantization.rec_q_eight),
    ('1/8T',         Live.Song.RecordingQuantization.rec_q_eight_triplet),
    ('1/8 + 1/8T',   Live.Song.RecordingQuantization.rec_q_eight_eight_triplet),
    ('1/16',         Live.Song.RecordingQuantization.rec_q_sixtenth),
    ('1/16T',        Live.Song.RecordingQuantization.rec_q_sixtenth_triplet),
    ('1/16 + 1/16T', Live.Song.RecordingQuantization.rec_q_sixtenth_sixtenth_triplet),
    ('1/32',         Live.Song.RecordingQuantization.rec_q_thirtysecond),
))

CLIP_GRID_STATES = dict((
    ('OFF',    Live.Clip.GridQuantization.no_grid),
    ('8 BAR',  Live.Clip.GridQuantization.g_8_bars),
    ('4 BAR',  Live.Clip.GridQuantization.g_4_bars),
    ('2 BAR',  Live.Clip.GridQuantization.g_2_bars),
    ('1 BAR',  Live.Clip.GridQuantization.g_bar),
    ('1/2',    Live.Clip.GridQuantization.g_half),
    ('1/4',    Live.Clip.GridQuantization.g_quarter),
    ('1/8',    Live.Clip.GridQuantization.g_eighth),
    ('1/16',   Live.Clip.GridQuantization.g_sixteenth),
    ('1/32',   Live.Clip.GridQuantization.g_thirtysecond),
    # alias
    ('8 BARS', Live.Clip.GridQuantization.g_8_bars),
    ('4 BARS', Live.Clip.GridQuantization.g_4_bars),
    ('2 BARS', Live.Clip.GridQuantization.g_2_bars),
))

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
))
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
)

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
)

_MIDI_DEVS = (
    'Note Length',
    'Chord',
    'Random',
    'MIDI Effect Rack',
    'Scale',
    'Pitch',
    'Arpeggiator',
    'Velocity',
)

AUDIO_DEVS = dict((dev.upper(), dev) for dev in _AUDIO_DEVS)

INS_DEVS = dict((dev.upper(), dev) for dev in _INS_DEVS)

MIDI_DEVS = dict((dev.upper(), dev) for dev in _MIDI_DEVS)
# endregion
