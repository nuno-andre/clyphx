# coding: utf-8
from __future__ import absolute_import, unicode_literals
from builtins import super
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Text, List
    from ..core.live import Clip, Track

from .base import XTrigger


class XTrackComponent(XTrigger):
    '''Track component that monitors play slot index and calls main
    script on changes.
    '''
    __module__ = __name__

    def __init__(self, parent, track):
        # type: (Any, Track) -> None
        super().__init__(parent)
        self._track = track
        self._clip = None
        self._loop_count = 0
        self._track.add_playing_slot_index_listener(self.play_slot_index_changed)
        self._register_timer_callback(self.on_timer)
        self._last_slot_index = -1
        self._triggered_clips = []  # type: List[Clip]
        self._triggered_lseq_clip = None

    def disconnect(self):
        self.remove_loop_jump_listener()
        self._unregister_timer_callback(self.on_timer)
        if self._track and self._track.playing_slot_index_has_listener(self.play_slot_index_changed):
            self._track.remove_playing_slot_index_listener(self.play_slot_index_changed)
        self._track = None
        self._clip = None
        self._triggered_clips = []
        self._triggered_lseq_clip = None
        super().disconnect()

    def play_slot_index_changed(self):
        '''Called on track play slot index changes to set up clips to
        trigger (on play and stop) and set up loop listener for LSEQ.
        '''
        self.remove_loop_jump_listener()
        new_clip = self.get_xclip(self._track.playing_slot_index)
        prev_clip = self.get_xclip(self._last_slot_index)
        self._last_slot_index = self._track.playing_slot_index
        if prev_clip:
            self._triggered_clips.append(prev_clip)
        if new_clip and new_clip != prev_clip:
            self._triggered_clips.append(new_clip)
        self._clip = new_clip
        # FIXME
        if (self._clip and '(LSEQ)' in self._clip.name.upper() and
                not self._clip.loop_jump_has_listener(self.on_loop_jump)):
            self._clip.add_loop_jump_listener(self.on_loop_jump)

    def get_xclip(self, slot_index):
        # type: (int) -> Optional[Clip]
        '''Get the xclip associated with slot_index or None.'''
        clip = None
        if self._track and 0 <= slot_index < len(self._track.clip_slots):
            slot = self._track.clip_slots[slot_index]
            if slot.has_clip and not slot.clip.is_recording and not slot.clip.is_triggered:
                clip_name = slot.clip.name
                # TODO: make XClip
                if len(clip_name) > 2 and clip_name[0] == '[' and ']' in clip_name:
                    clip = slot.clip
        return clip

    def on_loop_jump(self):
        '''Called on loop changes to increment loop count and set clip
        to trigger.
        '''
        self._loop_count += 1
        if self._clip:
            self._triggered_lseq_clip = self._clip

    def on_timer(self):
        '''Continuous timer, calls main script if there are any
        triggered clips.
        '''
        if self._track and (not self._track.mute or
                            self._parent._process_xclips_if_track_muted):
            if self._triggered_clips:
                for clip in self._triggered_clips:
                    try:
                        if clip.name.lstrip()[0] == '[':
                            self._parent.handle_action_list_trigger(self._track, clip)
                    except IndexError:
                        pass
                self._triggered_clips = []
            if self._triggered_lseq_clip:
                self._parent.handle_loop_seq_action_list(self._triggered_lseq_clip,
                                                         self._loop_count)
                self._triggered_lseq_clip = None

    def remove_loop_jump_listener(self):
        self._loop_count = 0
        if self._clip and self._clip.loop_jump_has_listener(self.on_loop_jump):
            self._clip.remove_loop_jump_listener(self.on_loop_jump)
