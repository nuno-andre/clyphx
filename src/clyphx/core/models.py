from __future__ import absolute_import, unicode_literals

from collections import namedtuple
from .utils import repr


Action = namedtuple('Action', ['track', 'actions', 'args'])


Command = namedtuple('Command', ['id', 'seq', 'start', 'stop'])


class UserControl(object):
    '''

    Args:
    - name (str): A unique one-word identifier for the control.
    - type (str): Message type: 'NOTE' or 'CC'.
    - channel (str): MIDI channel (1 - 16).
    - value (str): Note or CC value (0 - 127).
    - actions (str, optional): Action List to perform when the control
        sends an on.
    '''
    __slots__ = ('name', 'type', 'channel', 'value', 'actions')

    def __init__(self, name, type, channel, value, actions=None):
        self.name = name
        self.type = type.lower()
        self.channel = int(channel)
        self.value = int(value)
        # TODO: parse actions
        self.actions = actions
        self._validate()

    def _validate(self):
        # TODO: check valid identifier

        if self.type not in {'note', 'cc'}:
            raise ValueError("Message type must be 'NOTE' or 'CC'")

        if not (1 <= self.channel <= 16):
            raise ValueError('MIDI channel must be an integer between 1 and 16')

        if not (0 <= self.value <= 127):
            raise ValueError('NOTE or CC must be an integer between 0 and 127')

    __repr__ = repr
