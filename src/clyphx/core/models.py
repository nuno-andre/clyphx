# coding: utf-8
#
# Copyright (c) 2020-2021 Nuno André Novo
# Some rights reserved. See COPYING, COPYING.LESSER
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import absolute_import, unicode_literals
from typing import TYPE_CHECKING, NamedTuple, List, Text
from builtins import object

from ..consts import MIDI_STATUS
from .utils import repr_slots

if TYPE_CHECKING:
    from typing import Optional, Dict, Union


Action = NamedTuple('Action', [('tracks', List[Text]),
                               ('name',   Text),
                               ('obj',    Text),
                               ('args',   List[Text])])


Spec = NamedTuple('Spec', [('id',  Text),
                           ('seq', Text),
                           ('on',  List[Action]),
                           ('off', List[Action])])


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
        self.name        = name
        self.type        = type.upper()
        self.channel     = int(channel) - 1
        self.value       = int(value)
        # TODO: parse action lists
        self.on_actions  = '[{}] {}'.format(name, on_actions.strip())
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
            raise ValueError("Message type must be 'NOTE' or 'CC'")

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
            raise ValueError('MIDI channel must be an integer between 1 and 16')

        if not (0 <= self.value <= 127):
            raise ValueError('NOTE or CC must be an integer between 0 and 127')

    __repr__ = repr_slots
