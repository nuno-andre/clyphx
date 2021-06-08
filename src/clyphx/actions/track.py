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
from builtins import range
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..core.live import Track
    from typing import Any, Optional, Text, List
    from ..core.legacy import _DispatchCommand

from ..consts import switch
from ..consts import GQ_STATES, MON_STATES, XFADE_STATES
from ..core.xcomponent import XComponent
from ..core.live import Clip, get_random_int

log = logging.getLogger(__name__)


class XTrackActions(XComponent):
    '''Track-related actions.
    '''
    __module__ = __name__

    def dispatch_actions(self, cmd):
        # type: (_DispatchCommand) -> None
        from .consts import TRACK_ACTIONS

        action = TRACK_ACTIONS[cmd.action_name]

        for i, scmd in enumerate(cmd):
            action(self, scmd.track, scmd.xclip, scmd.args)

    def duplicate_track(self, track, xclip, args):
        # type: (Track, None, None, None) -> None
        '''Duplicates the given track (only regular tracks can be
        duplicated).
        '''
        if track in self.song().tracks:
            self.song().duplicate_track(list(self.song().tracks).index(track))

    def delete_track(self, track, xclip, args):
        # type: (Track, None, None, None) -> None
        '''Deletes the given track as long as it's not the last track in
        the set (only regular tracks can be deleted).
        '''
        if track in self.song().tracks:
            self.song().delete_track(list(self.song().tracks).index(track))

    def delete_device(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Delete the device on the track associated with the given index.
        Only top level devices can be deleted.
        '''
        try:
            index = int(args) - 1
            if index < len(track.devices):
                track.delete_device(index)
        except Exception:
            pass

    def create_clip(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Creates a clip in the given slot index (or sel if specified)
        at the given length (in bars). If no args, creates a 1 bar clip
        in the selected slot.
        '''
        if track.has_midi_input:
            slot = self.sel_scene
            bar = (4.0 / self.song().signature_denominator) * self.song().signature_numerator
            length = bar
            if args:
                arg_array = args.split()
                if len(arg_array) > 0:
                    specified_slot = arg_array[0].strip()
                    if specified_slot != 'SEL':
                        try:
                            slot = int(specified_slot) - 1
                        except Exception:
                            pass
                if len(arg_array) > 1:
                    try:
                        length = float(arg_array[1].strip()) * bar
                    except Exception:
                        pass
            if 0 <= slot < len(self.song().scenes):
                if not track.clip_slots[slot].has_clip:
                    track.clip_slots[slot].create_clip(length)

    def set_name(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Set track's name.'''
        if track in self.song().tracks or track in self.song().return_tracks:
            args = args.strip()
            if args:
                track.name = args

    def rename_all_clips(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Renames all clips on the track based on the track's name or
        the name specified in args.
        '''
        if track in self.song().tracks and not track.is_foldable:
            name = args.strip() if args.strip() else track.name
            for i, slot in enumerate(track.clip_slots):
                if slot.has_clip:
                    slot.clip.name = '{} {}'.format(name, i + 1)

    def set_mute(self, track, xclip, value=None):
        # type: (Track, None, None, Optional[Text]) -> None
        '''Toggles or turns on/off track mute.
        '''
        if track in self.song().tracks or track in self.song().return_tracks:
            switch(track, 'mute', value)

    def set_solo(self, track, xclip, value=None):
        # type: (Track, None, None, Optional[Text]) -> None
        '''Toggles or turns on/off track solo.'''
        if track in self.song().tracks or track in self.song().return_tracks:
            switch(track, 'solo', value)

    def set_arm(self, track, xclip, value=None):
        # type: (Track, None, None, Optional[Text]) -> None
        '''Toggles or turns on/off track arm.'''
        if track in self.song().tracks and track.can_be_armed:
            switch(track, 'arm', value)

    def set_fold(self, track, xclip, value=None):
        # type: (Track, None, None, Optional[Text]) -> None
        '''Toggles or turns on/off track fold.'''
        if track.is_foldable:
            switch(track, 'fold_state', value)

    def set_monitor(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Toggles or sets monitor state.'''
        if track in self.song().tracks and not track.is_foldable:
            try:
                track.current_monitoring_state = MON_STATES[args]
            except KeyError:
                if track.current_monitoring_state == 2:
                    track.current_monitoring_state = 0
                else:
                    track.current_monitoring_state += 1

    def set_xfade(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Toggles or sets crossfader assignment.'''
        if track != self.song().master_track:
            try:
                track.mixer_device.crossfade_assign = XFADE_STATES[args]
            except KeyError:
                if track.mixer_device.crossfade_assign == 2:
                    track.mixer_device.crossfade_assign = 0
                else:
                    track.mixer_device.crossfade_assign += 1

    def set_selection(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Sets track/slot selection.'''
        self.sel_track = track
        if track in self.song().tracks:
            if args:
                try:
                    self.song().view.selected_scene = list(self.song().scenes)[int(args) - 1]
                except Exception:
                    pass
            elif track.playing_slot_index >= 0:
                self.song().view.selected_scene = list(self.song().scenes)[track.playing_slot_index]

    def set_jump(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Jumps playing clip on track forward/backward.'''
        if track in self.song().tracks:
            try:
                track.jump_in_running_session_clip(float(args))
            except Exception:
                pass

    def set_stop(self, track, xclip, value=None):
        # type: (Track, None, Optional[Text]) -> None
        '''Stops all clips on track w/no quantization option for Live 9.
        '''
        if track in self.song().tracks:
            track.stop_all_clips((value or '').strip() != 'NQ')

    def set_play(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Plays clips normally. Allow empty slots unless using </> keywords.
        '''
        allow_empty_slots = args != '<' and args != '>'
        slot_to_play = self._get_slot_index_to_play(track, xclip, args.strip(), allow_empty_slots)
        if slot_to_play != -1:
            track.clip_slots[slot_to_play].fire()

    def set_play_w_legato(self, track, xclip, args):
        # type: (Track, Any, Text) -> None
        '''Plays the clip with legato using the current global quantization.
        This will not launch empty slots.
        '''
        slot_to_play = self._get_slot_index_to_play(track, xclip, args.strip())
        if slot_to_play != -1:
            track.clip_slots[slot_to_play].fire(
                force_legato=True,
                launch_quantization=self.song().clip_trigger_quantization,
            )

    def set_play_w_force_qntz(self, track, xclip, args):
        # type: (Track, Any, Text) -> None
        '''Plays the clip with a specific quantization regardless of
        launch/global quantization. This will not launch empty slots.
        '''
        self._handle_force_qntz_play(track, xclip, args, False)

    def set_play_w_force_qntz_and_legato(self, track, xclip, args):
        # type: (Track, Any, Text) -> None
        '''Combination of play_legato and play_w_force_qntz.'''
        self._handle_force_qntz_play(track, xclip, args, True)

    def _handle_force_qntz_play(self, track, xclip, args, w_legato):
        # type: (Track, Any, Text, bool) -> None
        '''Handles playing clips with a specific quantization with or
        without legato.
        '''
        args = args.strip()
        arg_array = args.split()
        qntz_spec = arg_array[0]
        if 'BAR' in args:
            qntz_spec = '{} {}'.format(arg_array[0], arg_array[1])
        try:
            qntz_to_use = GQ_STATES[qntz_spec]
        except KeyError:
            return
        slot_to_play = self._get_slot_index_to_play(
            track, xclip, args.replace(qntz_spec, '').strip()
        )
        if slot_to_play != -1:
            track.clip_slots[slot_to_play].fire(force_legato=w_legato,
                                                launch_quantization=qntz_to_use)

    def _get_slot_index_to_play(self, track, xclip, args, allow_empty_slots=False):
        # type: (Track, Any, Text, bool) -> int
        '''Returns the slot index to play based on keywords in the given args.
        '''
        if track not in self.song().tracks:
            return -1

        slot_to_play = -1
        play_slot = track.playing_slot_index
        if not args:
            if isinstance(xclip, Clip):
                slot_to_play = xclip.canonical_parent.canonical_parent.playing_slot_index
            else:
                slot_to_play = play_slot if play_slot >= 0 else self.sel_scene
        elif args == 'SEL':
            slot_to_play = self.sel_scene
        # TODO: repeated, check refactoring
        # don't allow randomization unless more than 1 scene
        elif 'RND' in args and len(self.song().scenes) > 1:
            num_scenes = len(self.song().scenes)
            rnd_range = [0, num_scenes]
            if '-' in args:
                rnd_range_data = args.replace('RND', '').split('-')
                if len(rnd_range_data) == 2:
                    try:
                        new_min = int(rnd_range_data[0]) - 1
                    except Exception:
                        new_min = 0
                    try:
                        new_max = int(rnd_range_data[1])
                    except Exception:
                        new_max = num_scenes
                    if 0 <= new_min and new_max < num_scenes + 1 and new_min < new_max - 1:
                        rnd_range = [new_min, new_max]
            slot_to_play = get_random_int(0, rnd_range[1] - rnd_range[0]) + rnd_range[0]
            if slot_to_play == play_slot:
                while slot_to_play == play_slot:
                    slot_to_play = get_random_int(0, rnd_range[1] - rnd_range[0]) + rnd_range[0]
        # don't allow adjustment unless more than 1 scene
        elif args.startswith(('<', '>')) and len(self.song().scenes) > 1:
            if track.is_foldable:
                return -1
            factor = self.get_adjustment_factor(args)
            if factor < len(self.song().scenes):
                # only launch slots that contain clips
                if abs(factor) == 1:
                    for _ in range(len(self.song().scenes)):
                        play_slot += factor
                        if play_slot >= len(self.song().scenes):
                            play_slot = 0
                        if track.clip_slots[play_slot].has_clip and track.clip_slots[play_slot].clip != xclip:
                            break
                else:
                    play_slot += factor
                    if play_slot >= len(self.song().scenes):
                        play_slot -= len(self.song().scenes)
                    elif play_slot < 0 and abs(play_slot) >= len(self.song().scenes):
                        play_slot = -(abs(play_slot) - len(self.song().scenes))
                slot_to_play = play_slot
        elif args.startswith('"') and args.endswith('"'):
            clip_name = args.strip('"')
            for i in range(len(track.clip_slots)):
                slot = track.clip_slots[i]
                if slot.has_clip and slot.clip.name.upper() == clip_name:
                    slot_to_play = i
                    break
        else:
            try:
                if 0 <= int(args) < len(self.song().scenes) + 1:
                    slot_to_play = int(args) - 1
            except Exception:
                pass

        if ((not track.clip_slots[slot_to_play].has_clip and allow_empty_slots)
             or (track.clip_slots[slot_to_play].has_clip
                 and track.clip_slots[slot_to_play].clip != xclip)):
            return slot_to_play
        else:
            return -1

    def adjust_preview_volume(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Adjust/set master preview volume.'''
        if track == self.song().master_track:
            self.adjust_param(
                self.song().master_track.mixer_device.cue_volume, args.strip())

    def adjust_crossfader(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Adjust/set master crossfader.'''
        if track == self.song().master_track:
            self.adjust_param(
                self.song().master_track.mixer_device.crossfader, args.strip())

    def adjust_volume(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Adjust/set track volume.'''
        self.adjust_param(track.mixer_device.volume, args.strip())

    def adjust_pan(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Adjust/set track pan.'''
        self.adjust_param(track.mixer_device.panning, args.strip())

    def adjust_sends(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Adjust/set track sends.'''
        largs = args.split()
        if len(args) > 1:
            param = self.get_send_parameter(track, largs[0].strip())
            if param:
                self.adjust_param(param, largs[1].strip())

    def get_send_parameter(self, track, send_string):
        # type: (Track, Text) -> Optional[Any]
        '''Gets the send parameter to operate on.'''
        param = None
        if track != self.song().master_track:
            try:
                param = track.mixer_device.sends[ord(send_string) - 65]
            except Exception:
                pass
        return param

# region ROUTING
    def adjust_input_routing(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Adjust track input routing.'''
        if track in self.song().tracks and not track.is_foldable:
            routings = list(track.input_routings)
            try:
                current_routing = routings.index(track.current_input_routing)
            except ValueError:
                current_routing = 0
            track.current_input_routing = self.handle_track_routing(args, routings, current_routing)

    def adjust_input_sub_routing(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Adjust track input sub-routing.'''
        if track in self.song().tracks and not track.is_foldable:
            routings = list(track.input_sub_routings)
            try:
                current_routing = routings.index(track.current_input_sub_routing)
            except ValueError:
                current_routing = 0
            track.current_input_sub_routing = self.handle_track_routing(args, routings, current_routing)

    def adjust_output_routing(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Adjust track output routing.'''
        if track != self.song().master_track:
            routings = list(track.output_routings)
            try:
                current_routing = routings.index(track.current_output_routing)
            except ValueError:
                current_routing = 0
            track.current_output_routing = self.handle_track_routing(args, routings, current_routing)

    def adjust_output_sub_routing(self, track, xclip, args):
        # type: (Track, None, Text) -> None
        '''Adjust track output sub-routing.'''
        if track != self.song().master_track:
            routings = list(track.output_sub_routings)
            try:
                current_routing = routings.index(track.current_output_sub_routing)
            except ValueError:
                current_routing = 0
            track.current_output_sub_routing = self.handle_track_routing(args, routings, current_routing)

    def handle_track_routing(self, args, routings, current_routing):
        # type: (Text, List[Text], int) -> Text
        '''Handle track routing adjustment.'''
        new_routing = routings[current_routing]
        args = args.strip()
        if args in ('<', '>'):
            factor = self.get_adjustment_factor(args)
            if 0 <= (current_routing + factor) < len(routings):
                new_routing = routings[current_routing + factor]
        else:
            for i in routings:
                if i.upper() == args:
                    new_routing = i
                    break
        return new_routing
# end region
