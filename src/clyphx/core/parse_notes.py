# coding: utf-8
#
# Copyright (c) 2020-2021 Nuno André Novo
# Some rights reserved. See COPYING, COPYING.LESSER
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import absolute_import, unicode_literals
from typing import TYPE_CHECKING
from builtins import dict
import re

if TYPE_CHECKING:
    from typing import Text


NOTE = dict([
    ('C',  0),
    ('Db', 1),  ('C#', 1),
    ('D',  2),
    ('Eb', 3),  ('D#', 3),
    ('E',  4),
    ('F',  5),
    ('Gb', 6),  ('F#', 6),
    ('G',  7),
    ('Ab', 8),  ('G#', 8),
    ('A',  9),
    ('Bb', 10), ('A#', 10),
    ('B',  11),
])

OCTAVE = ('-2', '-1', '0', '1', '2', '3', '4', '5', '6', '7', '8')

NOTE_INDEX = dict((v, k) for k, v in NOTE.items())  # returns sharp notes
VALUE_PTRN = r'(\d|[1-9]\d|1[0-1]\d|12[0-7])'
PITCH_PTRN = '({})({})'.format('|'.join(NOTE), '|'.join(OCTAVE))
PITCH = re.compile(PITCH_PTRN, re.I)
RANGE = re.compile(r'{0}\-{0}'.format('({}|{})'.format(PITCH_PTRN, VALUE_PTRN)), re.I)


def parse_pitch(string):
    # type: (Text) -> (Text, Text)
    try:
        name, octave = PITCH.match(string).groups()
        name = name.upper()
        value = NOTE[name] + OCTAVE.index(octave) * 12
        return name, int(octave), value
    except AttributeError:
        raise ValueError(string)


def pitch_note(pitch):
    # type: (int) -> (Text, int)
    return NOTE_INDEX[pitch  % 12], int(OCTAVE[pitch // 12])


def first_note(string):
    try:
        return PITCH.search(string).group(0)
    except AttributeError:
        raise ValueError("No notes were found in '{}'".format(string))


def parse_range(string):
    try:
        _, n1, o1, v1, _, n2, o2, v2 = RANGE.match(string).groups()
        note1 = v1 if v1 else n1 + o1
        note2 = v2 if v2 else n2 + o2
        return note1, note2
    except Exception:
        raise ValueError("Note range not found in '{}'".format(string))


__all__ = ['parse_pitch', 'pitch_note', 'first_note', 'parse_range']

del (NOTE, OCTAVE, NOTE_INDEX, VALUE_PTRN, PITCH_PTRN, PITCH, RANGE)
