# pyright: reportMissingTypeStubs=true
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
from builtins import super, range
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from typing import Any, Optional, Text, Dict, List, Tuple
    from ..core.live import DeviceParameter, Track
    from ..core.legacy import _DispatchCommand

from ..core.xcomponent import XComponent
from ..core.live import Clip
from .clip_env_capture import XClipEnvCapture
from .clip_notes import ClipNotesMixin
from ..consts import (CLIP_GRID_STATES, R_QNTZ_STATES,
                      WARP_MODES, ENV_TYPES,
                      KEYWORDS, ONOFF, switch)

log = logging.getLogger(__name__)


class XClipActions(XComponent, ClipNotesMixin):
    '''Clip-related actions.
    '''
    __module__ = __name__

    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__(parent)
        self._env_capture = XClipEnvCapture()

    def dispatch_actions(self, cmd):
        # type: (_DispatchCommand) -> None
        from .consts import CLIP_ACTIONS

        for scmd in cmd:
            # TODO: compare with dispatch_device_actions
            if scmd.track in self._parent.song().tracks:
                _args = scmd.track, scmd.action_name, scmd.args
                action = self.get_clip_to_operate_on(*_args)
                clip_args = None
                if action[0]:
                    if len(action) > 1:
                        clip_args = action[1]
                    if clip_args and clip_args.split()[0] in CLIP_ACTIONS:
                        func = CLIP_ACTIONS[clip_args.split()[0]]
                        func(self, action[0], scmd.track, scmd.xclip, scmd.ident,
                             clip_args.replace(clip_args.split()[0], ''))
                    elif clip_args and clip_args.split()[0].startswith('NOTES'):
                        self.dispatch_clip_note_action(action[0], cmd.args)
                    elif cmd.action_name.startswith('CLIP'):
                        self.set_clip_on_off(action[0], scmd.track, scmd.xclip, None, cmd.args)

    def get_clip_to_operate_on(self, track, action_name, args):
        # type: (Track, Text, Text) -> Tuple[Optional[Clip], Text]
        '''Get clip to operate on and action to perform with args.'''
        clip = None
        clip_args = args
        if 'CLIP"' in action_name:
            clip_name = action_name[action_name.index('"')+1:]
            if '"' in args:
                clip_name = '{} {}'.format(action_name[action_name.index('"')+1:], args)
                clip_args = args[args.index('"')+1:].strip()
            if '"' in clip_name:
                clip_name = clip_name[0:clip_name.index('"')]
            for slot in track.clip_slots:
                if slot.has_clip and slot.clip.name.upper() == clip_name:
                    clip = slot.clip
                    break
        else:
            sel_slot_idx = list(self.song().scenes).index(self.song().view.selected_scene)
            slot_idx = sel_slot_idx
            if action_name == 'CLIP':
                if track.playing_slot_index >= 0:
                    slot_idx = track.playing_slot_index
            elif action_name == 'CLIPSEL':
                if self.application().view.is_view_visible('Arranger'):
                    clip = self.song().view.detail_clip
            else:
                try:
                    slot_idx = int(action_name.replace('CLIP', ''))-1
                except:
                    slot_idx = sel_slot_idx
            if clip != None and track.clip_slots[slot_idx].has_clip:
                clip = track.clip_slots[slot_idx].clip
        log.debug('get_clip_to_operate_on -> clip=%s, clip args=%s',
                  clip.name if clip else 'None', clip_args)
        return (clip, clip_args)

    def set_clip_name(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Set clip's name.'''
        args = args.strip()
        if args:
            clip.name = args

    def set_clip_on_off(self, clip, track, xclip, ident, value=None):
        # type: (Clip, None, None, None, Optional[Text]) -> None
        '''Toggles or turns clip on/off.'''
        # XXX: reversed value, not fallback
        clip.muted = not KEYWORDS.get(value, clip.muted)

    def set_warp(self, clip, track, xclip, ident, value=None):
        # type: (Clip, None, None, None, Optional[Text]) -> None
        '''Toggles or turns clip warp on/off.'''
        if clip.is_audio_clip:
            switch(clip, 'warping', value)

    def adjust_time_signature(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Adjust clip's time signature.'''
        if '/' in args:
            try:
                num, denom = args.split('/')
                clip.signature_numerator = int(num)
                clip.signature_denominator = int(denom)
            except Exception as e:
                log.error('Failed to adjust time signature: %r', e)

    def adjust_detune(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Adjust/set audio clip detune.'''
        if clip.is_audio_clip:
            args = args.strip()
            if args.startswith(('<', '>')):
                factor = self._parent.get_adjustment_factor(args)
                clip.pitch_fine = clip.pitch_fine + factor
            else:
                try:
                    clip.pitch_fine = int(args)
                except Exception as e:
                    log.error('Failed to adjust detune: %r', e)

    def adjust_transpose(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Adjust audio or midi clip transpose, also set audio clip
        transpose.
        '''
        args = args.strip()
        if args.startswith(('<', '>')):
            factor = self._parent.get_adjustment_factor(args)
            if clip.is_audio_clip:
                clip.pitch_coarse = max(-48, min(48, (clip.pitch_coarse + factor)))
            elif clip.is_midi_clip:
                self.do_note_pitch_adjustment(clip, factor)
        else:
            if clip.is_audio_clip:
                try:
                    clip.pitch_coarse = int(args)
                except Exception as e:
                    log.error('Failed to adjust transpose: %r', e)

    def do_note_pitch_adjustment(self, clip, factor):
        # type: (Clip, Any) -> None
        '''Adjust note pitch. This isn't a note action, it's called via
        Clip Semi.
        '''
        edited_notes = []
        note_data = self.get_notes_to_operate_on(clip)
        if note_data['notes_to_edit']:
            for n in note_data['notes_to_edit']:
                new_pitch = n[0] + factor
                if 0 <= new_pitch < 128:
                    edited_notes.append((new_pitch, n[1], n[2], n[3], n[4]))
                else:
                    edited_notes = []
                    return
            if edited_notes:
                self.write_all_notes(clip, edited_notes, note_data['other_notes'])

    def adjust_gain(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Adjust/set clip gain for Live 9. For settings, range is
        0 - 127.
        '''
        if clip.is_audio_clip:
            args = args.strip()
            if args.startswith(('<', '>')):
                factor = self._parent.get_adjustment_factor(args, True)
                clip.gain = max(0.0, min(1.0, (clip.gain + factor * float(1.0 / 127.0))))
            else:
                try:
                    clip.gain = int(args) * float(1.0 / 127.0)
                except Exception as e:
                    log.error('Failed to adjust gain: %r', e)

    def adjust_start(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Adjust/set clip start exclusively for Live 9. In Live 8, same
        as adjust_loop_start.
        '''
        args = args.strip()
        if args.startswith(('<', '>')):
            factor = self._parent.get_adjustment_factor(args, True)
            if clip.looping:
                clip.start_marker = max(0.0, min(clip.end_marker - factor, (clip.start_marker + factor)))
            else:
                clip.loop_start = max(0.0, min(clip.loop_end - factor, (clip.loop_start + factor)))
        else:
            try:
                if clip.looping:
                    clip.start_marker = float(args)
                else:
                    clip.loop_start = float(args)
            except Exception as e:
                log.error('Failed to adjust start: %r', e)

    def adjust_loop_start(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Adjust/set clip loop start if loop is on or clip start otherwise.'''
        args = args.strip()
        if args.startswith(('<', '>')):
            factor = self._parent.get_adjustment_factor(args, True)
            clip.loop_start = max(0.0, min(clip.loop_end - factor, (clip.loop_start + factor)))
        else:
            try:
                clip.loop_start = float(args)
            except Exception as e:
                log.error('Failed to adjust loop start: %r', e)

    def adjust_end(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Adjust/set clip end exclusively for Live 9. In Live 8, same as
        adjust_loop_end.
        '''
        args = args.strip()
        if args.startswith(('<', '>')):
            factor = self._parent.get_adjustment_factor(args, True)
            if clip.looping:
                clip.end_marker = max((clip.start_marker - factor),
                                      (clip.end_marker + factor))
            else:
                clip.loop_end = max((clip.loop_start - factor),
                                    (clip.loop_end + factor))
        else:
            try:
                if clip.looping:
                    clip.end_marker = float(args)
                else:
                    clip.loop_end = float(args)
            except Exception as e:
                log.error('Failed to adjust end: %r', e)

    def adjust_loop_end(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Adjust/set clip loop end if loop is on or close end otherwise.
        '''
        args = args.strip()
        if args.startswith(('<', '>')):
            factor = self._parent.get_adjustment_factor(args, True)
            clip.loop_end = max((clip.loop_start - factor), (clip.loop_end + factor))
        else:
            try:
                clip.loop_end = float(args)
            except Exception as e:
                log.error('Failed to adjust loop end: %r', e)

    def adjust_cue_point(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Adjust clip's start point and fire (also stores cue point if
        not specified). Will not fire xclip itself as this causes a loop.
        '''
        if clip.is_midi_clip or (clip.is_audio_clip and clip.warping):
            if args:
                args = args.strip()
                if args.startswith(('<', '>')):
                    factor = self._parent.get_adjustment_factor(args, True)
                    args = clip.loop_start + factor
                try:
                    clip.loop_start = float(args)
                    if clip.looping:
                        clip.looping = False
                        clip.loop_start = float(args)
                        clip.looping = True
                    if clip != xclip:
                        clip.fire()
                except Exception as e:
                    log.error('Failed to adjust cue point: %r', e)
            else:
                if isinstance(xclip, Clip):
                    xclip.name = '{} {}'.format(xclip.name.strip(), clip.loop_start)

    def adjust_warp_mode(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Adjusts the warp mode of the clip. This cannot be applied if the
        warp mode is currently rex (5).
        '''
        if clip.is_audio_clip and clip.warping and clip.warp_mode != 5:
            args = args.strip()
            if args in WARP_MODES:
                clip.warp_mode = WARP_MODES[args]
            elif args in ('<', '>'):
                factor = self._parent.get_adjustment_factor(args)
                new_mode = clip.warp_mode + factor
                if new_mode == 5 and '>' in args:
                    new_mode = 6
                elif new_mode == 5 and '<' in args:
                    new_mode = 4
                if 0 <= new_mode < 7 and new_mode != 5:
                    clip.warp_mode = new_mode

    def adjust_grid_quantization(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Adjusts clip grid quantization.'''
        args = args.strip()
        if args in CLIP_GRID_STATES:
            clip.view.grid_quantization = CLIP_GRID_STATES[args]

    def set_triplet_grid(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Toggles or turns triplet grid on or off.'''
        switch(clip.view, 'grid_is_triplet', args)

    def capture_to_envelope(self, clip, track, xclip, ident, args):
        # type: (Clip, Any, None, None, Text) -> None
        self._env_capture.capture(clip, track, args)

    def insert_envelope(self, clip, track, xclip, ident, args):
        # type: (Clip, Any, None, None, Text) -> None
        '''Inserts an envelope for the given parameter into the clip.

        This doesn't apply to quantized parameters.
        '''
        args = args.strip()
        arg_array = args.split()
        if len(arg_array) > 1:
            # used to determine whether env_type is last arg...
            #   otherwise a range is specified
            last_arg_index = len(arg_array) - 1
            env_type_index = last_arg_index
            env_type = None
            for i in range(len(arg_array)):
                if arg_array[i] in ENV_TYPES:
                    env_type_index = i
                    env_type = arg_array[i]
                    break
            if env_type:
                env_param_spec = ''
                for i in range(env_type_index):
                    env_param_spec += '{} '.format(arg_array[i])
                param = self._get_envelope_parameter(track, env_param_spec)
                if param and not param.is_quantized:
                    env_range = (param.min, param.max)
                    # calculate range if specified in args
                    if env_type_index != last_arg_index:
                        try:
                            min_factor = int(arg_array[-2])
                            max_factor = int(arg_array[-1])
                            if 0 <= min_factor and max_factor < 101 and min_factor < max_factor:
                                env_range = ((min_factor / 100.0) * param.max,
                                             (max_factor / 100.0) * param.max)
                        except:
                            pass
                    self.song().view.detail_clip = clip
                    clip.view.show_envelope()
                    clip.view.select_envelope_parameter(param)
                    clip.clear_envelope(param)
                    self._perform_envelope_insertion(clip, param, env_type, env_range)

    def _perform_envelope_insertion(self, clip, param, env_type, env_range):
        # type: (Clip, DeviceParameter, Text, Tuple[Any, Any]) -> None
        '''Performs the actual insertion of the envelope into the clip.'''
        env = clip.automation_envelope(param)
        if env:
            median = ((clip.loop_end - clip.loop_start) / 2.0) + clip.loop_start
            num_beats = int(clip.loop_end - clip.loop_start) + 1
            start_beat = int(clip.loop_start)
            if env_type == 'IRAMP':
                env.insert_step(clip.loop_start, 0.0, env_range[0])
                env.insert_step(clip.loop_end, 0.0, env_range[1])
            elif env_type == 'DRAMP':
                env.insert_step(clip.loop_start, 0.0, env_range[1])
                env.insert_step(clip.loop_end, 0.0, env_range[0])
            elif env_type == 'IPYR':
                env.insert_step(clip.loop_start, 0.0, env_range[0])
                env.insert_step(median, 0.0, env_range[1])
                env.insert_step(clip.loop_end, 0.0, env_range[0])
            elif env_type == 'DPYR':
                env.insert_step(clip.loop_start, 0.0, env_range[1])
                env.insert_step(median, 0.0, env_range[0])
                env.insert_step(clip.loop_end, 0.0, env_range[1])
            elif env_type == 'SAW':
                for b in range(num_beats):
                    beat = float(b + start_beat)
                    env.insert_step(beat, 0.0, env_range[1])
                    if beat < clip.loop_end:
                        env.insert_step(beat + 0.5, 0.0, env_range[0])
            elif env_type == 'SQR':
                for b in range(num_beats):
                    beat = float(b + start_beat)
                    if beat < clip.loop_end:
                        if b % 2 == 0:
                            env.insert_step(beat, 1.0, env_range[1])
                        else:
                            env.insert_step(beat, 1.0, env_range[0])

    def clear_envelope(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Clears the envelope of the specified param or all envelopes
        from the given clip.
        '''
        if args:
            param = self._get_envelope_parameter(track, args.strip())
            if param:
                clip.clear_envelope(param)
        else:
            clip.clear_all_envelopes()

    def show_envelope(self, clip, track, xclip, ident, args):
        # type: (Clip, Any, None, None, Text) -> None
        '''Shows the clip's envelope view and a particular envelope if
        specified. Requires 9.1 or later.
        '''
        self.song().view.detail_clip = clip
        clip.view.show_envelope()
        if args:
            param = self._get_envelope_parameter(track, args.strip())
            if param:
                clip.view.select_envelope_parameter(param)

    def _get_envelope_parameter(self, track, args):
        # type: (Track, Text) -> Optional[Any]
        '''Gets the selected, mixer or device parameter for envelope-
        -related actions.
        '''
        param = None
        if 'SEL' in args:
            param = self.song().view.selected_parameter
        elif 'VOL' in args:
            param = track.mixer_device.volume
        elif 'PAN' in args:
            param = track.mixer_device.panning
        elif 'SEND' in args:
            param = self._parent.track_actions.get_send_parameter(
                track, args.replace('SEND', '').strip())
        elif 'DEV' in args:
            arg_array = args.split()
            if len(arg_array) > 1:
                dev_array = self._parent.get_device_to_operate_on(
                    track, arg_array[0], args.replace(arg_array[0], '').strip()
                )
                if len(dev_array) == 2:
                    param_array = dev_array[1].strip().split()
                    param = None
                    if len(param_array) > 1:
                        param = self._parent.device_actions.get_banked_parameter(
                            dev_array[0], param_array[0], param_array[1])
                    else:
                        param = self._parent.device_actions.get_bob_parameter(
                            dev_array[0], param_array[0])
        return param

    def hide_envelopes(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, None) -> None
        '''Hides the clip's envelope view.'''
        clip.view.hide_envelope()

    def quantize(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, Text) -> None
        '''Quantizes notes or warp markers to the given quantization
        value, at the (optional) given strength and with the (optional)
        percentage of swing. Can optionally be applied to specific notes
        or ranges of notes.
        '''
        args = args.strip()
        arg_array = args.split()
        array_offset = 0
        rate_to_apply = None
        # standard qntz to all
        if arg_array[0] in R_QNTZ_STATES:
            rate_to_apply = R_QNTZ_STATES[arg_array[0]]
        # qntz to specific note or note range
        elif arg_array[1] in R_QNTZ_STATES and clip.is_midi_clip:
            array_offset = 1
            rate_to_apply = R_QNTZ_STATES[arg_array[1]]
        if rate_to_apply:
            strength = 1.0
            swing_to_apply = 0.0
            current_swing = self.song().swing_amount
            if len(arg_array) > 1 + array_offset:
                try:
                    strength = float(arg_array[1 + array_offset]) / 100.0
                    if strength > 1.0 or strength < 0.0:
                        strength = 1.0
                except:
                    strength = 1.0
            if len(arg_array) > 2 + array_offset:
                try:
                    swing_to_apply = float(arg_array[2 + array_offset]) / 100.0
                    if swing_to_apply > 1.0 or swing_to_apply < 0.0:
                        swing_to_apply = 0.0
                except:
                    swing_to_apply = 0.0
            self.song().swing_amount = swing_to_apply
            # apply standard qntz to all
            if array_offset == 0:
                clip.quantize(rate_to_apply, strength)
            # apply qntz to specific note or note range
            else:
                note_range = self.get_note_range(arg_array[0])
                for note in range(note_range[0], note_range[1]):
                    clip.quantize_pitch(note, rate_to_apply, strength)
            self.song().swing_amount = current_swing

    def duplicate_clip_content(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, None) -> None
        '''Duplicates all the content in a MIDI clip and doubles loop length.
        Will also zoom out to show entire loop if loop is on.
        '''
        if clip.is_midi_clip:
            try:
                clip.duplicate_loop()
            except Exception as e:
                log.error('Failed to duplicate clip content: %r', e)

    def delete_clip(self, clip, track, xclip, ident, args):
        # type: (Clip, None, None, None, None) -> None
        '''Deletes the given clip.'''
        clip.canonical_parent.delete_clip()

    def duplicate_clip(self, clip, track, xclip, ident, args):
        # type: (Clip, Track, None, None, None) -> None
        '''Duplicates the given clip. This will overwrite clips if any exist
        in the slots used for duplication.
        '''
        try:
            track.duplicate_clip_slot(list(track.clip_slots).index(clip.canonical_parent))
        except Exception as e:
            log.error('Failed to duplicate clip: %r', e)

    def chop_clip(self, clip, track, xclip, ident, args):
        # type: (Clip, Track, None, None, Text) -> None
        '''Duplicates the clip the number of times specified and sets evenly
        distributed start points across all duplicates. This will overwrite
        clips if any exist in the slots used for duplication.
        '''
        args = args.strip()
        num_chops = 8
        if args:
            try:
                num_chops = int(args)
            except:
                pass
        slot_index = list(track.clip_slots).index(clip.canonical_parent)
        current_start = clip.start_marker
        chop_length = (clip.loop_end - current_start) / num_chops
        try:
            for i in range(num_chops - 1):
                track.duplicate_clip_slot(slot_index + i)
                dupe_start = (chop_length * (i + 1)) + current_start
                dupe = track.clip_slots[slot_index + i + 1].clip
                dupe.start_marker = dupe_start
                dupe.loop_start = dupe_start
                dupe.name = '{}-{}'.format(clip.name, i + 1)
        except Exception as e:
            log.error('Failed to chop clip: %r', e)

    def split_clip(self, clip, track, xclip, ident, args):
        # type: (Clip, Track, None, None, Text) -> None
        '''Duplicates the clip and sets each duplicate to have the length
        specified in args.  This will overwrite clips if any exist in the
        slots used for duplication.
        '''
        try:
            bar_arg = float(args)
            bar_length = (4.0 / clip.signature_denominator) * clip.signature_numerator
            split_size = bar_length * bar_arg
            num_splits = int(clip.length / split_size)
            if split_size * num_splits < clip.end_marker:
                num_splits += 1
            if num_splits >= 2:
                slot_index = list(track.clip_slots).index(clip.canonical_parent)
                current_start = clip.start_marker
                actual_end = clip.end_marker
                for i in range(num_splits):
                    track.duplicate_clip_slot(slot_index + i)
                    dupe_start = (split_size * i) + current_start
                    dupe_end = dupe_start + split_size
                    if dupe_end > actual_end:
                        dupe_end = actual_end
                    dupe = track.clip_slots[slot_index + i + 1].clip
                    dupe.loop_end = dupe_end
                    dupe.start_marker = dupe_start
                    dupe.loop_start = dupe_start
                    dupe.name = '{}-{}'.format(clip.name, i + 1)
        except Exception as e:
            log.error('Failed to split clip: %r', e)

    def get_clip_stats(self, clip):
        # type: (Clip) -> Dict[Text, Any]
        '''Get real length and end of looping clip.'''
        clip.looping = 0
        length = clip.length
        end = clip.loop_end
        clip.looping = 1
        loop_length = clip.loop_end - clip.loop_start
        return dict(
            clip_length = length,
            real_end    = end,
            loop_length = loop_length,
        )

# TODO: make Mixin together with transport functions
# TODO: check XGlobalActions.do_loop_action and device_looper
# region CLIP LOOP ACTIONS
    def do_clip_loop_action(self, clip, track, xclip, ident, args):
        # type: (Clip, Track, Clip, None, Text) -> None
        '''Handle clip loop actions.'''
        args = args.strip()
        if not args or args.upper() in KEYWORDS:
            self.set_loop_on_off(clip, args)
        else:
            if args.startswith('START'):
                self.adjust_loop_start(
                    clip, track, xclip, ident, args.replace('START', '', 1).strip()
                )
            elif args.startswith('END'):
                self.adjust_loop_end(
                    clip, track, xclip, ident, args.replace('END', '', 1).strip()
                )
            elif args == 'SHOW':
                clip.view.show_loop()
            if clip.looping:
                clip_stats = self.get_clip_stats(clip)
                new_start = clip.loop_start
                new_end = clip.loop_end
                if args.startswith(('<', '>')):
                    self.move_clip_loop_by_factor(clip, args, clip_stats)
                    return
                elif args == 'RESET':
                    new_start = 0.0
                    new_end = clip_stats['real_end']
                elif args.startswith('*'):
                    try:
                        new_end = ((clip.loop_end - clip_stats['loop_length'])
                                   + (clip_stats['loop_length'] * float(args[1:])))
                    except Exception as e:
                        log.error('Failed to do clip action: %r', e)
                else:
                    self.do_loop_set(clip, args, clip_stats)
                    return
                self.set_new_loop_position(clip, new_start, new_end, clip_stats)

    def set_loop_on_off(self, clip, value=None):
        # type: (Clip, Optional[Text]) -> None
        '''Toggles or turns clip loop on/off.'''
        clip.looping = ONOFF.get(value, not clip.looping)

    def move_clip_loop_by_factor(self, clip, args, clip_stats):
        # type: (Clip, Text, Dict[Text, Any]) -> None
        '''Move clip loop by its length or by a specified factor.'''
        factor = clip_stats['loop_length']
        if args == '<':
            factor = -(factor)
        if len(args) > 1:
            factor = self._parent.get_adjustment_factor(args, True)
        new_end = clip.loop_end + factor
        new_start = clip.loop_start + factor
        if new_start < 0.0:
            new_end -= new_start
            new_start = 0.0
        self.set_new_loop_position(clip, new_start, new_end, clip_stats)

    def do_loop_set(self, clip, args, clip_stats):
        # type: (Clip, Text, Dict[Text, Any]) -> None
        '''Set loop length and (if clip is playing) position, quantizes to 1/4
        by default or bar if specified.
        '''
        try:
            qntz = False
            if 'B' in args:
                qntz = True
            bars_to_loop = float(args.strip('B'))
            bar = (4.0 / clip.signature_denominator) * clip.signature_numerator
            start = clip.loop_start
            if clip.is_playing:
                start = round(clip.playing_position)
                if qntz:
                    distance = start % bar
                    if distance <= bar / 2:
                        start -= distance
                    else:
                        start += bar - distance
            end = start + (bar * bars_to_loop)
            self.set_new_loop_position(clip, start, end, clip_stats)
        except Exception as e:
            log.error('Failed to do loop set: %r', e)

    def set_new_loop_position(self, clip, new_start, new_end, clip_stats):
        # type: (Clip, float, float, Dict[Text, Any]) -> None
        '''For use with other clip loop actions, ensures that loop settings
        are within range and applies in correct order.
        '''
        if new_end <= clip_stats['real_end'] and new_start >= 0:
            # FIXME: same values
            if new_end > clip.loop_start:
                clip.loop_end = new_end
                clip.loop_start = new_start
            else:
                clip.loop_start = new_start
                clip.loop_end = new_end
# endregion
