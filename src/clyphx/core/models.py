# coding: utf-8
#
# Copyright (c) 2020-2021 Nuno André Novo
# Some rights reserved. See COPYING, COPYING.LESSER
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import absolute_import, unicode_literals
from typing import TYPE_CHECKING, NamedTuple, List, Text, Optional, Any
from builtins import object, tuple

from ..consts import MIDI_STATUS
from .utils import repr_slots
from .parse_notes import parse_pitch, pitch_note, first_note, parse_range
from .exceptions import InvalidParam

if TYPE_CHECKING:
    from typing import Dict, Union, Tuple
    from numbers import Integral


Action = NamedTuple('Action', [('tracks', List[Text]),
                               ('name',   Text),
                               ('obj',    Text),
                               ('args',   List[Text])])


Spec = NamedTuple('Spec', [('id',  Text),
                           ('seq', Text),
                           ('on',  List[Action]),
                           ('off', List[Action])])


IdSpec = NamedTuple('Spec', [('id',       Text),
                             ('seq',      Text),
                             ('on',       Text),
                             ('off',      Optional[Text]),
                             ('override', bool)])


class Pitch(int):
    '''Converts either a numeric value or a note + octave string into a
    constrained integer [0,127] with `note` and `octave` properties.

    `note` and `octave`, if not provided, are lazy evaluated.
    '''
    def __new__(cls, value):
        # type: (Union[Text, Integral]) -> 'Pitch'
        try:                    # numeric value
            self = super().__new__(cls, value)
            name, octave = None, None
        except ValueError:      # note + octave
            name, octave, val = parse_pitch(value)
            self = super().__new__(cls, val)
        self._name = name
        self._octave = octave
        if 0 <= self < 128:
            return self
        raise ValueError(int(self))

    @classmethod
    def first_note(cls, string):
        '''Returns the first note found in the string.'''
        return cls(first_note(string))

    @property
    def name(self):
        # type: () -> str
        if self._name is None:
            self._name, self._octave = pitch_note(self)
        return self._name

    @property
    def octave(self):
        # type: () -> int
        if self._octave is None:
            self._name, self._octave = pitch_note(self)
        return self._octave

    def __add__(self, other):
        return self.__class__(int(self) + other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__class__(int(self) - other)

    def __rsub__(self, other):
        return self.__class__(other - int(self))

    def __mul__(self, other):
        '''Up `other` octaves.'''
        return self.__add__(other * 12)

    def __rmul__(self, other):
        return self.__add__(other * 12)

    def __div__(self, other):
        '''Down `other` octaves.'''
        return self.__sub__(other * 12)

    def __rdiv__(self, other):
        return self.__sub__(other * 12)

    def __bool__(self):
        return True

    def __repr__(self):
        return 'Pitch({}, {})'.format(int(self), self)

    def __str__(self):
        return '{}{}'.format(self.name, self.octave)


def pitch_range(string):
    # type: (Text) -> Tuple[Pitch, Pitch]
    return tuple(Pitch[n] for n in parse_range(string))


Note = NamedTuple('Note', [('pitch',  int),  # TODO: Pitch
                           ('start',  float),
                           ('length', float),
                           ('vel',    int),
                           ('mute',   bool)])


Location = NamedTuple('Location', [('bar',       int),
                                   ('beat',      int),
                                   ('sixteenth', int)])


class UserControl(object):
    '''
    X-Controls defined in user settings.

    Args:
        name: A unique one-word identifier for the control.
        type: Message type: 'NOTE' or 'CC'.
        channel: MIDI channel (1 - 16).
        value: Note or CC value (0 - 127).
        on_actions: Action List to perform when the control sends an on.
        off_actions: Optional Action List to perform when the control
            sends an off.
    '''
    __slots__ = (
        'name', 'type', 'channel', 'value', 'on_actions', 'off_actions',
    )

    def __init__(self, name, type, channel, value, on_actions, off_actions=None):
        # type: (Text, Text, Union[Text, int], Union[Text, int], Text, Optional[Text]) -> None
        self.name    = name
        self.type    = type.upper()
        self.channel = int(channel) - 1
        self.value   = Pitch(value) if self.type == 'NOTE' else int(value)
        # TODO: parse action lists
        self.on_actions = '[{}] {}'.format(name, on_actions.strip())
        if off_actions == '*':
            self.off_actions = self.on_actions  # type: Optional[Text]
        elif off_actions:
            self.off_actions = '[{}] {}'.format(name, off_actions.strip())
        else:
            self.off_actions = None
        self._validate()

    @property
    def _key(self):
        # key for XControlComponent._control_list dict
        return self.status_byte + self.channel, self.value

    def __hash__(self):
        return hash(self._key)

    @property
    def status_byte(self):
        try:
            return MIDI_STATUS[self.type]
        except KeyError:
            raise InvalidParam("Message type must be 'NOTE' or 'CC'")

    @classmethod
    def parse(cls, name, data):
        # type: (Text, Text) -> 'UserControl'
        data = [x.strip() for x in data.split(',')]
        # split action lists (on/off)
        data = data[0:3] + data[-1].split(':')
        return UserControl(name, *data)

    def _validate(self):
        # TODO: check valid identifier

        if not (0 <= self.channel <= 15):
            raise InvalidParam('MIDI channel must be an integer between 1 and 16')

        if not (0 <= self.value < 128):
            raise InvalidParam('NOTE or CC must be an integer between 0 and 127')

    __repr__ = repr_slots
