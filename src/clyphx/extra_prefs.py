# -*- coding: utf-8 -*-
# This file is part of ClyphX.
#
# ClyphX is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# ClyphX is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ClyphX.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals
from builtins import super
from functools import partial
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from typing import Any, Sequence, Text, Dict, List, Optional
    from .core.live import Track

from .core.xcomponent import XComponent

log = logging.getLogger(__name__)


class ExtraPrefs(XComponent):
    '''Extra prefs component for ClyphX.
    '''
    __module__ = __name__

    def __init__(self, parent, config):
        # type: (Any, Dict[Text, Any]) -> None
        super().__init__(parent)
        log.info('Starting ExtraPrefs with %s', config)
        self._show_highlight = config.get('navigation_highlight', True)  # type: bool
        self._exclusive_arm = config.get('exclusive_arm_on_select', False)  # type: bool
        self._exclusive_fold = config.get('exclusive_show_group_on_select', False)  # type: bool
        self._clip_record = config.get('clip_record_length_set_by_global_quantization', False)  # type: bool
        self._clip_record_slot = None  # type: Optional[Any]
        self._midi_clip_length = config.get('default_inserted_midi_clip_length', False)  # type: bool
        self._midi_clip_length_slot = None  # type: Optional[Any]
        self._last_track = self.song().view.selected_track  # type: Track
        self.on_selected_track_changed()

    def disconnect(self):
        self.remove_listeners()
        self._last_track = None
        self._clip_record_slot = None
        self._midi_clip_length_slot = None
        super().disconnect()

    def on_selected_track_changed(self):
        '''Handles navigation highlight, triggering exclusive arm/fold
        functions and removes/sets up listeners for clip-related
        functions.
        '''
        log.info('ExtraPrefs.on_selected_track_changed')
        super().on_selected_track_changed()
        track = self.song().view.selected_track
        clip_slot = self.song().view.highlighted_clip_slot
        self.remove_listeners()
        if self._show_highlight:
            tracks = list(tuple(self.song().visible_tracks) +
                          tuple(self.song().return_tracks) +
                          (self.song().master_track,))
            if self.song().view.selected_track in tracks:
                self._parent._set_session_highlight(
                    tracks.index(self.song().view.selected_track),
                    list(self.song().scenes).index(self.song().view.selected_scene),
                    1, 1, True,
                )
        else:
            self._parent._set_session_highlight(-1, -1, -1, -1, False)
        if self._exclusive_arm and track != self._last_track:
            self._parent.schedule_message(1, partial(self.do_exclusive_arm, track))
        if self._exclusive_fold and track != self._last_track:
            self._parent.schedule_message(1, partial(self.do_exclusive_fold, track))
        if self._clip_record:
            if track.can_be_armed and not clip_slot.has_clip:
                self._clip_record_slot = clip_slot
                if not self._clip_record_slot.has_clip_has_listener(
                    self.clip_record_slot_changed
                ):
                    self._clip_record_slot.add_has_clip_listener(
                        self.clip_record_slot_changed
                    )
        if self._midi_clip_length:
            if track.has_midi_input and not clip_slot.has_clip and not track.is_foldable:
                self._midi_clip_length_slot = clip_slot
                if not self._midi_clip_length_slot.has_clip_has_listener(
                    self.midi_clip_length_slot_changed
                ):
                    self._midi_clip_length_slot.add_has_clip_listener(
                        self.midi_clip_length_slot_changed
                    )
        self._last_track = track
        log.debug('ExtraPrefs.on_selected_track_changed, last track: %r', track)

    def do_exclusive_fold(self, track):
        # type: (Track) -> None
        '''Called on track change. Collapses all group tracks except for
        the current group track.
        '''
        if track.is_foldable:
            for t in self.song().tracks:
                if t.is_foldable:
                    t.fold_state = t != track

    def do_exclusive_arm(self, track):
        # type: (Track) -> None
        '''Called on track change. Disarms all tracks except for the
        current track.
        '''
        for t in self.song().tracks:
            if t.can_be_armed:
                t.arm = t == track

    def clip_record_slot_changed(self):
        '''Called on slot has clip changed. Checks if clip is recording
        and retriggers it if so.
        '''
        track = self.song().view.selected_track
        if self.song().clip_trigger_quantization != 0 and track.arm:
            clip = self._clip_record_slot.clip
            if clip and clip.is_recording:
                clip.fire()

    def midi_clip_length_slot_changed(self):
        '''Called on slot has clip changed to trigger set length
        function. Checks if clip is not playing/triggered, is 1-bar in
        length, has no name and no notes.
        '''
        clip = self._midi_clip_length_slot.clip
        if clip and not clip.is_playing and not clip.is_triggered:
            one_bar = (4.0 / self.song().signature_denominator) * self.song().signature_numerator
            if clip.length == one_bar and not clip.name:
                clip.select_all_notes()
                all_notes = clip.get_selected_notes()
                clip.deselect_all_notes()
                if not all_notes:
                    self._parent.schedule_message(
                        1, partial(self.do_midi_clip_set_length, (clip, one_bar))
                    )

    def do_midi_clip_set_length(self, clip_params):
        # type: (Sequence[Any]) -> None
        '''Sets clip length and loop end to user-defined length.'''
        clip = clip_params[0]
        new_length = clip_params[1] * self._midi_clip_length
        clip.loop_end = new_length
        clip.looping = False
        clip.loop_end = new_length
        clip.looping = True

    def remove_listeners(self):
        '''Remove parameter listeners.'''
        if self._clip_record_slot:
            if self._clip_record_slot.has_clip_has_listener(
                self.clip_record_slot_changed
            ):
                self._clip_record_slot.remove_has_clip_listener(
                    self.clip_record_slot_changed
                )
        self._clip_record_slot = None

        if self._midi_clip_length_slot:
            if self._midi_clip_length_slot.has_clip_has_listener(
                self.midi_clip_length_slot_changed
            ):
                self._midi_clip_length_slot.remove_has_clip_listener(
                    self.midi_clip_length_slot_changed
                )
        self._midi_clip_length_slot = None

    def on_selected_scene_changed(self):
        super().on_selected_scene_changed()
        self.on_selected_track_changed()
