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

import Live
from ..consts import KEYWORDS
from ..consts import GQ_STATES, MON_STATES, XFADE_STATES
from ..core import XComponent


class XTrackActions(XComponent):
    '''Track-related actions.
    '''
    __module__ = __name__

    def duplicate_track(self, track, xclip, ident, args):
        '''Duplicates the given track (only regular tracks can be
        duplicated).
        '''
        if track in self.song().tracks:
            self.song().duplicate_track(list(self.song().tracks).index(track))

    def delete_track(self, track, xclip, ident, args):
        '''Deletes the given track as long as it's not the last track in
        the set (only regular tracks can be deleted).
        '''
        if track in self.song().tracks:
            self.song().delete_track(list(self.song().tracks).index(track))

    def delete_device(self, track, xclip, ident, args):
        '''Delete the device on the track associated with the given index.
        Only top level devices can be deleted.
        '''
        try:
            index = int(args) - 1
            if index < len(track.devices):
                track.delete_device(index)
        except:
            pass

    def create_clip(self, track, xclip, ident, args):
        '''Creates a clip in the given slot index (or sel if specified)
        at the given length (in bars). If no args, creates a 1 bar clip
        in the selected slot.
        '''
        if track.has_midi_input:
            slot = list(self.song().scenes).index(self.song().view.selected_scene)
            bar = (4.0 / self.song().signature_denominator) * self.song().signature_numerator
            length = bar
            if args:
                arg_array = args.split()
                if len(arg_array) > 0:
                    specified_slot = arg_array[0].strip()
                    if specified_slot != 'SEL':
                        try:
                            slot = int(specified_slot) - 1
                        except:
                            pass
                if len(arg_array) > 1:
                    try:
                        length = float(arg_array[1].strip()) * bar
                    except:
                        pass
            if 0 <= slot < len(self.song().scenes):
                if not track.clip_slots[slot].has_clip:
                    track.clip_slots[slot].create_clip(length)

    def set_name(self, track, xclip, ident, args):
        '''Set track's name.'''
        if track in self.song().tracks or track in self.song().return_tracks:
            args = args.strip()
            if args:
                track.name = args

    def rename_all_clips(self, track, xclip, ident, args):
        '''Renames all clips on the track based on the track's name or
        the name specified in args.
        '''
        if track in self.song().tracks and not track.is_foldable:
            name = args.strip() if args.strip() else track.name
            for i, slot in enumerate(track.clip_slots):
                if slot.has_clip:
                    slot.clip.name = '{} {}'.format(name, i + 1)

    def set_mute(self, track, xclip, ident, value=None):
        '''Toggles or turns on/off track mute.
        '''
        if track in self.song().tracks or track in self.song().return_tracks:
            track.mute = KEYWORDS.get(value, not track.mute)

    def set_solo(self, track, xclip, ident, value=None):
        '''Toggles or turns on/off track solo.'''
        if track in self.song().tracks or track in self.song().return_tracks:
            track.solo = KEYWORDS.get(value, not track.solo)

    def set_arm(self, track, xclip, ident, value=None):
        '''Toggles or turns on/off track arm.'''
        if track in self.song().tracks and track.can_be_armed:
            track.arm = KEYWORDS.get(value, not track.arm)

    def set_fold(self, track, xclip, ident, value=None):
        '''Toggles or turns on/off track fold.'''
        if track.is_foldable:
            track.fold_state = KEYWORDS.get(value, not track.fold_state)

    def set_monitor(self, track, xclip, ident, args):
        '''Toggles or sets monitor state.'''
        if track in self.song().tracks and not track.is_foldable:
            try:
                track.current_monitoring_state = MON_STATES[args]
            except KeyError:
                if track.current_monitoring_state == 2:
                    track.current_monitoring_state = 0
                else:
                    track.current_monitoring_state += 1

    def set_xfade(self, track, xclip, ident, args):
        '''Toggles or sets crossfader assignment.'''
        if track != self.song().master_track:
            try:
                track.mixer_device.crossfade_assign = XFADE_STATES[args]
            except KeyError:
                if track.mixer_device.crossfade_assign == 2:
                    track.mixer_device.crossfade_assign = 0
                else:
                    track.mixer_device.crossfade_assign += 1

    def set_selection(self, track, xclip, ident, args):
        '''Sets track/slot selection.'''
        self.song().view.selected_track = track
        if track in self.song().tracks:
            if args:
                try:
                    self.song().view.selected_scene = list(self.song().scenes)[int(args) - 1]
                except:
                    pass
            else:
                if track.playing_slot_index >= 0:
                    self.song().view.selected_scene = list(self.song().scenes)[track.playing_slot_index]

    def set_jump(self, track, xclip, ident, args):
        '''Jumps playing clip on track forward/backward.'''
        if track in self.song().tracks:
            try:
                track.jump_in_running_session_clip(float(args))
            except:
                pass

    def set_stop(self, track, xclip, ident, value=None):
        '''Stops all clips on track w/no quantization option for Live 9.
        '''
        if track in self.song().tracks:
            track.stop_all_clips(value.strip() != 'NQ')

    def set_play(self, track, xclip, ident, args):
        '''Plays clips normally. Allow empty slots unless using </> keywords.
        '''
        allow_empty_slots = args != '<' and args != '>'
        slot_to_play = self._get_slot_index_to_play(track, xclip, args.strip(), allow_empty_slots)
        if slot_to_play != -1:
            track.clip_slots[slot_to_play].fire()

    def set_play_w_legato(self, track, xclip, ident, args):
        '''Plays the clip with legato using the current global quantization.
        This will not launch empty slots.
        '''
        slot_to_play = self._get_slot_index_to_play(track, xclip, args.strip())
        if slot_to_play != -1:
            track.clip_slots[slot_to_play].fire(
                force_legato=True,
                launch_quantization=self.song().clip_trigger_quantization,
            )

    def set_play_w_force_qntz(self, track, xclip, ident, args):
        '''Plays the clip with a specific quantization regardless of
        launch/global quantization. This will not launch empty slots.
        '''
        self._handle_force_qntz_play(track, xclip, args, False)

    def set_play_w_force_qntz_and_legato(self, track, xclip, ident, args):
        '''Combination of play_legato and play_w_force_qntz.'''
        self._handle_force_qntz_play(track, xclip, args, True)

    def _handle_force_qntz_play(self, track, xclip, args, w_legato):
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
        '''Returns the slot index to play based on keywords in the given args.
        '''
        slot_to_play = -1
        if track in self.song().tracks:
            play_slot = track.playing_slot_index
            select_slot = list(self.song().scenes).index(self.song().view.selected_scene)
            if not args:
                if isinstance(xclip, Live.Clip.Clip):
                    slot_to_play = xclip.canonical_parent.canonical_parent.playing_slot_index
                else:
                    slot_to_play = play_slot if play_slot >= 0 else select_slot
            elif args == 'SEL':
                slot_to_play = select_slot
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
                        except:
                            new_min = 0
                        try:
                            new_max = int(rnd_range_data[1])
                        except:
                            new_max = num_scenes
                        if 0 <= new_min and new_max < num_scenes + 1 and new_min < new_max - 1:
                            rnd_range = [new_min, new_max]
                slot_to_play = Live.Application.get_random_int(0, rnd_range[1] - rnd_range[0]) + rnd_range[0]
                if slot_to_play == play_slot:
                    while slot_to_play == play_slot:
                        slot_to_play = Live.Application.get_random_int(0, rnd_range[1] - rnd_range[0]) + rnd_range[0]
            # don't allow adjustment unless more than 1 scene
            elif args.startswith(('<', '>')) and len(self.song().scenes) > 1:
                if track.is_foldable:
                    return -1
                factor = self._parent.get_adjustment_factor(args)
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
                except:
                    pass
        else:
            return -1
        if (not track.clip_slots[slot_to_play].has_clip and allow_empty_slots) or (
            track.clip_slots[slot_to_play].has_clip and
            track.clip_slots[slot_to_play].clip != xclip
        ):
            return slot_to_play
        else:
            return -1

    def adjust_preview_volume(self, track, xclip, ident, args):
        '''Adjust/set master preview volume.'''
        if track == self.song().master_track:
            self._parent.do_parameter_adjustment(self.song().master_track.mixer_device.cue_volume, args.strip())

    def adjust_crossfader(self, track, xclip, ident, args):
        '''Adjust/set master crossfader.'''
        if track == self.song().master_track:
            self._parent.do_parameter_adjustment(self.song().master_track.mixer_device.crossfader, args.strip())

    def adjust_volume(self, track, xclip, ident, args):
        '''Adjust/set track volume.'''
        self._parent.do_parameter_adjustment(track.mixer_device.volume, args.strip())

    def adjust_pan(self, track, xclip, ident, args):
        '''Adjust/set track pan.'''
        self._parent.do_parameter_adjustment(track.mixer_device.panning, args.strip())

    def adjust_sends(self, track, xclip, ident, args):
        '''Adjust/set track sends.'''
        args = args.split()
        if len(args) > 1:
            param = self.get_send_parameter(track, args[0].strip())
            if param:
                self._parent.do_parameter_adjustment(param, args[1].strip())

    def get_send_parameter(self, track, send_string):
        '''Gets the send parameter to operate on.'''
        param = None
        if track != self.song().master_track:
            try:
                param = track.mixer_device.sends[ord(send_string) - 65]
            except:
                pass
        return param

    def adjust_input_routing(self, track, xclip, ident, args):
        '''Adjust track input routing.'''
        if track in self.song().tracks and not track.is_foldable:
            routings = list(track.input_routings)
            if track.current_input_routing in routings:
                current_routing = routings.index(track.current_input_routing)
            else:
                current_routing = 0
            track.current_input_routing = self.handle_track_routing(args, routings, current_routing)

    def adjust_input_sub_routing(self, track, xclip, ident, args):
        '''Adjust track input sub-routing.'''
        if track in self.song().tracks and not track.is_foldable:
            routings = list(track.input_sub_routings)
            if track.current_input_sub_routing in routings:
                current_routing = routings.index(track.current_input_sub_routing)
            else:
                current_routing = 0
            track.current_input_sub_routing = self.handle_track_routing(args, routings, current_routing)

    def adjust_output_routing(self, track, xclip, ident, args):
        '''Adjust track output routing.'''
        if track != self.song().master_track:
            routings = list(track.output_routings)
            if track.current_output_routing in routings:
                current_routing = routings.index(track.current_output_routing)
            else:
                current_routing = 0
            track.current_output_routing = self.handle_track_routing(args, routings, current_routing)

    def adjust_output_sub_routing(self, track, xclip, ident, args):
        '''Adjust track output sub-routing.'''
        if track != self.song().master_track:
            routings = list(track.output_sub_routings)
            if track.current_output_sub_routing in routings:
                current_routing = routings.index(track.current_output_sub_routing)
            else:
                current_routing = 0
            track.current_output_sub_routing = self.handle_track_routing(args, routings, current_routing)

    def handle_track_routing(self, args, routings, current_routing):
        '''Handle track routing adjustment.'''
        new_routing = routings[current_routing]
        args = args.strip()
        if args in ('<', '>'):
            factor = self._parent.get_adjustment_factor(args)
            if 0 <= (current_routing + factor) < len(routings):
                new_routing = routings[current_routing + factor]
        else:
            for i in routings:
                if self._parent.get_name(i) == args:
                    new_routing = i
                    break
        return new_routing
