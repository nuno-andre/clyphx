from __future__ import absolute_import
from .compat import super

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SessionComponent import SessionComponent


class XComponent(ControlSurfaceComponent):
    '''Control Surface base component.
    '''
    def __init__(self, parent):
        super().__init__()
        self._parent = parent

    def disconnect(self):
        '''Called by the control surface on disconnect (app closed,
        script closed).
        '''
        self._parent = None
        super().disconnect()

    def on_enabled_changed(self):
        '''Called when this script is enabled/disabled (by calling
        set_enabled on it).
        '''
        pass

    def _on_enabled_changed(self):
        super().update()

    def update(self):
        '''Called by the control surface on instantiation and in other
        cases such as when exiting MIDI map mode.
        '''
        pass

    def _update(self):
        super().update()
