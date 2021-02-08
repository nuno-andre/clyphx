from __future__ import absolute_import, unicode_literals
from typing import TYPE_CHECKING
from builtins import super
import logging

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SessionComponent import SessionComponent

if TYPE_CHECKING:
    from typing import Any

log = logging.getLogger(__name__)


class XComponent(ControlSurfaceComponent):
    '''Control Surface base component.
    '''
    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__()
        self._parent = parent

    # def __getattribute__(self, attr):
    #     log.debug('Get %s from %s', attr, self.__name__)
    #     return object.__getattribute__(self, attr)

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

    def _on_enabled_changed(self):
        super().update()

    def update(self):
        '''Called by the control surface on instantiation and in other
        cases such as when exiting MIDI map mode.
        '''

    def _update(self):
        super().update()
