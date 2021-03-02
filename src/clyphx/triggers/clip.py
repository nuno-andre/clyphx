# coding: utf-8
from __future__ import absolute_import, unicode_literals
from builtins import super
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from typing import Optional, Text
    from ..core.live import Clip

from .base import XTrigger

log = logging.getLogger(__name__)


def get_xclip_action_list(xclip, full_action_list):
    # type: (Clip, Text) -> Text
    '''Get the action list to perform.

    X-Clips can have an on and off action list separated by a colon.
    This will return which action list to perform based on whether
    the clip is playing. If the clip is not playing and there is no
    off action, this returns None.
    '''
    log.info('get_xclip_action_list(xclip=%r, full_action_list=%s',
              xclip, full_action_list)
    split_list = full_action_list.split(':')

    if xclip.is_playing:
        result = split_list[0]
    elif len(split_list) == 2:
        if split_list[1].strip() == '*':
            result = split_list[0]
        else:
            result = split_list[1]
    else:
        # FIXME: shouldn't be None
        result = ''

    return result


class XClip(XTrigger):
    '''A control on a Session View Clip.
    '''
    can_have_off_list = True
    can_loop_seq = True

    __module__ = __name__

    def __init__(self, parent, clip):
        # type: (Any, Clip) -> None
        super().__init__(parent)
        self._clip = clip
        self._on_name_changed.subject = self._clip

    def update(self):
        super().update()

    @property
    def slot(self):
        # type: () -> int
        return self._clip.canonical_parent.canonical_parent.playing_slot_index
        # return self.ref_track.playing_slot_index

    @property
    def actions(self):
        # type: () -> Optional[Text]
        # TODO: split actions
        if self.is_playing:
            return self.spec.on
        elif self.spec.off == '*':
            return self.spec.on
        elif self.spec.off:
            return self.spec.off

    @property
    def is_playing(self):
        # type: () -> bool
        return self._clip.is_playing

    @property
    def in_loop_seq(self):
        # type: () -> bool
        return self.name in self._parent._loop_seq_clips

    @property
    def in_play_seq(self):
        # type: () -> bool
        return self.name in self._parent._play_seq_clips

    @property
    def ref_track(self):
        '''The track indicated as SEL.

        It's the song's selected track for all triggers except for
        X-Clips, where is the host track.
        '''
        raise NotImplementedError
        # return self._clip.canonical_parent.canonical_parent
