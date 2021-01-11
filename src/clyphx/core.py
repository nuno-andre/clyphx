
from __future__ import absolute_import, unicode_literals

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent


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
