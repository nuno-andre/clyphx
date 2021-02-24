# coding: utf-8
from __future__ import absolute_import, unicode_literals
from builtins import object, super
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Text

from _Framework.SubjectSlot import subject_slot

from ..core.xcomponent import XComponent


class ActionList(object):
    '''Allows X-Triggers with no name to trigger Action Lists. It can
    also be used to trigger ClyphX Actions via UserActions.
    '''
    __module__ = __name__

    def __init__(self, name='none'):
        # type: (Text) -> None
        self.name = name


class XTrigger(XComponent):
    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__(parent)

    @subject_slot('name')
    def _on_name_changed(self):
        self.updated()

    @property
    def ref_track(self):
        '''The track indicated as SEL.

        It's the song's selected track for all triggers except for
        X-Clips, where is the host track.
        '''
        return self._parent.song().selected_track
