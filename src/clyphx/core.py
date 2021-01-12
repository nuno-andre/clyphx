from __future__ import absolute_import, unicode_literals

import re
from collections import namedtuple
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent


Action = namedtuple('Action', ['track', 'actions', 'args'])

Command = namedtuple('Command', ['id', 'seq', 'start', 'stop'])


class Parser(object):
    command = re.compile(r'\[(?P<id>[a-zA-Z0-9\_]*?)\]\s*?'
                         r'(?P<seq>\([a-zA-Z]*?\))?\s*?'
                         r'(?P<actions>\S.*?)\s*?$')
    lists   = re.compile(r'(?P<start>[^,]*?)'
                         r'(\s*?,\s*?(?P<stop>\S[^,]*?))?\s*?$')
    actions = re.compile(r'^\s+|\s*;\s*|\s+$')

    def __call__(self, text):
        cmd = self.command.search(text).groupdict()
        lists = self.lists.match(cmd.pop('actions')).groupdict()
        cmd.update(
            start=self.actions.split(lists['start']),
            stop=self.actions.split(lists['stop'])
                 if lists['stop'] and lists['stop'] != '*'
                 else lists['stop'],
        )
        return Command(**cmd)


class XComponent(ControlSurfaceComponent):
    '''Control Surface base component.
    '''
    def __init__(self, parent):
        super(XComponent, self).__init__()
        self._parent = parent

    def disconnect(self):
        '''Called by the control surface on disconnect (app closed,
        script closed).
        '''
        self._parent = None
        super(XComponent, self).disconnect()

    def on_enabled_changed(self):
        '''Called when this script is enabled/disabled (by calling
        set_enabled on it).
        '''
        pass

    def update(self):
        '''Called by the control surface on instantiation and in other
        cases such as when exiting MIDI map mode.
        '''
        pass
