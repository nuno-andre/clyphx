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
from builtins import super, dict, range
from typing import TYPE_CHECKING
from functools import partial
import logging

from .core.xcomponent import XComponent
from .core.legacy import ActionList
from .core.models import UserControl
from .core.live import forward_midi_cc, forward_midi_note

if TYPE_CHECKING:
    from typing import (
        Any, Optional, Text, Dict,
        Iterable, Sequence, List, Tuple,
    )
    from .core.live import Clip, Track

log = logging.getLogger(__name__)


class XTrigger(XComponent):
    pass


class XControlComponent(XTrigger):
    '''A control on a MIDI controller.
    '''
    __module__ = __name__

    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__(parent)
        self._control_list = dict()  # type: Dict[Tuple[int, int], Dict[Text, Any]]
        self._xt_scripts = []  # type: List[Any]

    def disconnect(self):
        self._control_list = dict()
        self._xt_scripts = []
        super().disconnect()

    def connect_script_instances(self, instantiated_scripts):
        # type: (Iterable[Any]) -> None
        '''Try to connect to ClyphX_XT instances.'''
        for i in range(5):
            try:
                if i == 0:
                    from ClyphX_XTA.ClyphX_XT import ClyphX_XT
                elif i == 1:
                    from ClyphX_XTB.ClyphX_XT import ClyphX_XT
                elif i == 2:
                    from ClyphX_XTC.ClyphX_XT import ClyphX_XT
                elif i == 3:
                    from ClyphX_XTD.ClyphX_XT import ClyphX_XT
                elif i == 4:
                    from ClyphX_XTE.ClyphX_XT import ClyphX_XT
                else:
                    continue
            except ImportError:
                pass
            else:
                if ClyphX_XT:
                    for i in instantiated_scripts:
                        if isinstance(i, ClyphX_XT) and not i in self._xt_scripts:
                            self._xt_scripts.append(i)
                            break

    def assign_new_actions(self, string):
        # type: (Text) -> None
        '''Assign new actions to controls via xclips.'''
        if self._xt_scripts:
            for x in self._xt_scripts:
                x.assign_new_actions(string)
        ident = string[string.index('[')+2:string.index(']')].strip()
        actions = string[string.index(']')+2:].strip()
        for c, v in self._control_list.items():
            if ident == v['ident']:
                new_actions = actions.split(',')
                on_action = '[{}] {}'.format(ident, new_actions[0])
                off_action = None
                if on_action and len(new_actions) > 1:
                    if new_actions[1].strip() == '*':
                        off_action = on_action
                    else:
                        off_action = '[{}] {}'.format(ident, new_actions[1])
                if on_action:
                    v['on_action'] = on_action
                    v['off_action'] = off_action
                break

    def receive_midi(self, bytes):
        # type: (Sequence[int]) -> None
        '''Receive user-defined midi messages.'''
        if self._control_list:
            ctrl_data = None
            if bytes[2] == 0 or bytes[0] < 144:
                if ((bytes[0], bytes[1]) in self._control_list.keys() and
                        self._control_list[(bytes[0], bytes[1])]['off_action']):
                    ctrl_data = self._control_list[(bytes[0], bytes[1])]
                elif ((bytes[0] + 16, bytes[1]) in self._control_list.keys() and
                        self._control_list[(bytes[0] + 16, bytes[1])]['off_action']):
                    ctrl_data = self._control_list[(bytes[0] + 16, bytes[1])]
                if ctrl_data:
                    ctrl_data['name'].name = ctrl_data['off_action']
            elif bytes[2] != 0 and (bytes[0], bytes[1]) in self._control_list.keys():
                ctrl_data = self._control_list[(bytes[0], bytes[1])]
                ctrl_data['name'].name = ctrl_data['on_action']
            if ctrl_data:
                self._parent.handle_action_list_trigger(self.song().view.selected_track,
                                                        ctrl_data['name'])

    def get_user_controls(self, settings, midi_map_handle):
        # type: (Dict[Text, Text], Any) -> None
        self._control_list = dict()
        for name, data in settings.items():
            uc = UserControl.parse(name, data)
            self._control_list[uc._key] = dict(
                ident      = name,
                on_action  = uc.on_actions,
                off_action = uc.off_actions,
                name       = ActionList(uc.on_actions)
            )
            fn = forward_midi_note if uc.status_byte == 144 else forward_midi_cc
            fn(self._parent._c_instance.handle(), midi_map_handle, uc.channel, uc.value)

    def rebuild_control_map(self, midi_map_handle):
        # type: (int) -> None
        '''Called from main when build_midi_map is called.'''
        log.debug('XControlComponent.rebuild_control_map')
        for key in self._control_list.keys():
            if key[0] >= 176:
                # forwards a CC msg to the receive_midi method
                forward_midi_cc(
                    self._parent._c_instance.handle(), midi_map_handle, key[0] - 176, key[1]
                )
            else:
                # forwards a NOTE msg to the receive_midi method
                forward_midi_note(
                    self._parent._c_instance.handle(), midi_map_handle, key[0] - 144, key[1]
                )


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
        if new_clip and prev_clip and new_clip == prev_clip:
            self._triggered_clips.append(new_clip)
        elif new_clip:
            if prev_clip:
                self._triggered_clips.append(prev_clip)
            self._triggered_clips.append(new_clip)
        elif prev_clip:
            self._triggered_clips.append(prev_clip)
        self._clip = new_clip
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
                    self._parent.handle_action_list_trigger(self._track, clip)
                self._triggered_clips = []
            if self._triggered_lseq_clip:
                self._parent.handle_loop_seq_action_list(self._triggered_lseq_clip,
                                                         self._loop_count)
                self._triggered_lseq_clip = None

    def remove_loop_jump_listener(self):
        self._loop_count = 0
        if self._clip and self._clip.loop_jump_has_listener(self.on_loop_jump):
            self._clip.remove_loop_jump_listener(self.on_loop_jump)


class XCueComponent(XTrigger):
    '''Cue component that monitors cue points and calls main script on
    changes.
    '''
    __module__ = __name__

    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__(parent)
        self.song().add_current_song_time_listener(self.arrange_time_changed)
        self.song().add_is_playing_listener(self.arrange_time_changed)
        self.song().add_cue_points_listener(self.cue_points_changed)
        self._x_points = dict()  # type: Dict[Text, Any]
        self._x_point_time_to_watch_for = -1
        self._last_arrange_position = -1
        self._sorted_times = []  # type: List[Any]
        self.cue_points_changed()

    def disconnect(self):
        self.remove_cue_point_listeners()
        self.song().remove_current_song_time_listener(self.arrange_time_changed)
        self.song().remove_is_playing_listener(self.arrange_time_changed)
        self.song().remove_cue_points_listener(self.cue_points_changed)
        self._x_points = dict()
        super().disconnect()

    def cue_points_changed(self):
        '''Called on cue point changes to set up points to watch, cue
        points can't be named via the API so cue points can't perform
        any actions requiring naming.
        '''
        self.remove_cue_point_listeners()
        self._sorted_times = []
        for cp in self.song().cue_points:
            if not cp.time_has_listener(self.cue_points_changed):
                cp.add_time_listener(self.cue_points_changed)
            if not cp.name_has_listener(self.cue_points_changed):
                cp.add_name_listener(self.cue_points_changed)
            name = cp.name.upper()
            if len(name) > 2 and name[0] == '[' and name.count('[') == 1 and name.count(']') == 1:
                cue_name = name.replace(name[name.index('['):name.index(']')+1].strip(), '')
                self._x_points[cp.time] = cp
        self._sorted_times = sorted(self._x_points.keys())
        self.set_x_point_time_to_watch()

    def arrange_time_changed(self):
        '''Called on arrange time changed and schedules actions where
        necessary.
        '''
        if self.song().is_playing:
            if self._x_point_time_to_watch_for != -1 and self._last_arrange_position < self.song().current_song_time:
                if (self.song().current_song_time >= self._x_point_time_to_watch_for and
                        self._x_point_time_to_watch_for < self._last_arrange_position):
                    self._parent.schedule_message(
                        1, partial(self.schedule_x_point_action_list, self._x_point_time_to_watch_for)
                    )
                    self._x_point_time_to_watch_for = -1
            else:
                self.set_x_point_time_to_watch()
        self._last_arrange_position = self.song().current_song_time

    def set_x_point_time_to_watch(self):
        '''Determine which cue point time to watch for next.'''
        if self._x_points:
            if self.song().is_playing:
                for t in self._sorted_times:
                    if t >= self.song().current_song_time:
                        self._x_point_time_to_watch_for = t
                        break
            else:
                self._x_point_time_to_watch_for = -1

    def schedule_x_point_action_list(self, point):
        self._parent.handle_action_list_trigger(self.song().view.selected_track,
                                                self._x_points[point])

    def remove_cue_point_listeners(self):
        for cp in self.song().cue_points:
            if cp.time_has_listener(self.cue_points_changed):
                cp.remove_time_listener(self.cue_points_changed)
            if cp.name_has_listener(self.cue_points_changed):
                cp.remove_name_listener(self.cue_points_changed)
        self._x_points = dict()
        self._x_point_time_to_watch_for = -1
