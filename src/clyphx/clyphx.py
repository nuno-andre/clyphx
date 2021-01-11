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

from __future__ import with_statement, absolute_import, unicode_literals

import logging
from functools import partial
from itertools import chain
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework import Task
from raven.utils.six import iteritems

from .macrobat import Macrobat
from .extra_prefs import ExtraPrefs
from .cs_linker import CsLinker
from .actions import (
    XTrackActions, XSnapActions, XGlobalActions,
    XDeviceActions, XDrActions, XClipActions,
    XControlSurfaceActions,
)
from .xtriggers import (
    XTrackComponent, XControlComponent, XCueComponent
)
from .user_actions import XUserActions
from .m4l_browser import XM4LBrowserInterface
from .action_list import ActionList
from .push_apc_combiner import PushApcCombiner
from .consts import LIVE_VERSION
from .consts import (CLIP_ACTIONS, DEVICE_ACTIONS, DR_ACTIONS,
                    GLOBAL_ACTIONS, LOOPER_ACTIONS, TRACK_ACTIONS)
from .push_mocks import MockHandshakeTask, MockHandshake
# from utils import get_python_info

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

FOLDER = '/ClyphX/'
SCRIPT_NAME = 'ClyphX v2.7.0'


class ClyphX(ControlSurface):
    '''ClyphX Main.
    '''
    __module__ = __name__

    def __init__(self, c_instance):
        super(ClyphX, self).__init__(c_instance)
        self._user_settings_logged = False
        self._is_debugging = False
        self._push_emulation = False
        self._PushApcCombiner = None
        self._process_xclips_if_track_muted = True
        with self.component_guard():
            self._macrobat = Macrobat(self)
            self._extra_prefs = ExtraPrefs(self)
            self._cs_linker = CsLinker()
            self._track_actions = XTrackActions(self)
            self._snap_actions = XSnapActions(self)
            self._global_actions = XGlobalActions(self)
            self._device_actions = XDeviceActions(self)
            self._dr_actions = XDrActions(self)
            self._clip_actions = XClipActions(self)
            self._control_surface_actions = XControlSurfaceActions(self)
            self._user_actions = XUserActions(self)
            self._control_component = XControlComponent(self)
            XM4LBrowserInterface(self)
            XCueComponent(self)
            self._startup_actions_complete = False
            self._user_variables = {}
            self._play_seq_clips = {}
            self._loop_seq_clips = {}
            self._current_tracks = []
            # live = Live.Application.get_application()
            self._can_have_nested_devices = True
            self.setup_tracks()
        msg = 'ClyphX LOG ------- %s ------- Live Version: %s ------- END LOG'
        log.info(msg, SCRIPT_NAME, '.'.join(map(str, LIVE_VERSION)))
        self.show_message(SCRIPT_NAME)

    def disconnect(self):
        self._PushApcCombiner = None
        self._macrobat = None
        self._extra_prefs = None
        self._cs_linker = None
        self._track_actions = None
        self._snap_actions = None
        self._global_actions = None
        self._device_actions = None
        self._dr_actions = None
        self._clip_actions = None
        self._control_surface_actions = None
        self._user_actions = None
        self._control_component = None
        self._user_variables = {}
        self._play_seq_clips = {}
        self._loop_seq_clips = {}
        self._current_tracks = []
        super(ClyphX, self).disconnect()

    @property
    def _is_debugging(self):
        return log.getEffectiveLevel() <= 10

    @_is_debugging.setter
    def _is_debugging(self, value):
        log.setLevel(logging.DEBUG if value else logging.INFO)

    def action_dispatch(self, tracks, xclip, action_name, args, ident):
        '''Command handler.

        Main dispatch for calling appropriate class of actions, passes
        all necessary arguments to class method.
        '''
        if tracks:
            if action_name.startswith('SNAP'):
                self._snap_actions.store_track_snapshot(tracks, xclip, ident, action_name, args)
            elif action_name.startswith(('SURFACE', 'CS')):
                self._control_surface_actions.dispatch_cs_action(tracks[0], xclip, ident, action_name, args)
            elif action_name.startswith('ARSENAL'):
                self._control_surface_actions.dispatch_arsenal_action(tracks[0], xclip, ident, action_name, args)
            elif action_name.startswith('PUSH'):
                self._control_surface_actions.dispatch_push_action(tracks[0], xclip, ident, action_name, args)
            elif action_name.startswith('PXT'):
                self._control_surface_actions.dispatch_pxt_action(tracks[0], xclip, ident, action_name, args)
            elif action_name.startswith('MXT'):
                self._control_surface_actions.dispatch_mxt_action(tracks[0], xclip, ident, action_name, args)
            elif action_name in GLOBAL_ACTIONS:
                getattr(self._global_actions, GLOBAL_ACTIONS[action_name])(tracks[0], xclip, ident, args)
            elif action_name == 'PSEQ' and args== 'RESET':
                for _, value in iteritems(self._play_seq_clips):
                    value[1] = -1
            elif action_name == 'DEBUG':
                if isinstance(xclip, Live.Clip.Clip):
                    xclip.name = str(xclip.name).upper().replace('DEBUG', 'Debugging Activated')
                self.start_debugging()
            else:
                for t in tracks:
                    if action_name in TRACK_ACTIONS:
                        getattr(self._track_actions, TRACK_ACTIONS[action_name])(t, xclip, ident, args)
                    elif action_name == 'LOOPER':
                        if args and args.split()[0] in LOOPER_ACTIONS:
                            getattr(self._device_actions, LOOPER_ACTIONS[args.split()[0]])(t, xclip, ident, args)
                        elif action_name in LOOPER_ACTIONS:
                            getattr(self._device_actions, LOOPER_ACTIONS[action_name])(t, xclip, ident, args)
                    elif action_name.startswith('DEV'):
                        device_action = self.get_device_to_operate_on(t, action_name, args)
                        device_args = None
                        if device_action[0]:
                            if len(device_action) > 1:
                                device_args = device_action[1]
                            if device_args and device_args.split()[0] in DEVICE_ACTIONS:
                                fn = getattr(self._device_actions, DEVICE_ACTIONS[device_args.split()[0]])
                                fn(device_action[0], t, xclip, ident, device_args)
                            elif device_args and 'CHAIN' in device_args:
                                self._device_actions.dispatch_chain_action(device_action[0], t, xclip, ident, device_args)
                            elif action_name.startswith('DEV'):
                                self._device_actions.set_device_on_off(device_action[0], t, xclip, ident, device_args)
                    elif action_name.startswith('CLIP') and t in self.song().tracks:
                        clip_action = self.get_clip_to_operate_on(t, action_name, args)
                        clip_args = None
                        if clip_action[0]:
                            if len(clip_action) > 1:
                                clip_args = clip_action[1]
                            if clip_args and clip_args.split()[0] in CLIP_ACTIONS:
                                fn = getattr(self._clip_actions, CLIP_ACTIONS[clip_args.split()[0]])
                                fn(clip_action[0], t, xclip, ident, clip_args.replace(clip_args.split()[0], ''))
                            elif clip_args and clip_args.split()[0].startswith('NOTES'):
                                self._clip_actions.do_clip_note_action(clip_action[0], t, xclip, ident, args)
                            elif action_name.startswith('CLIP'):
                                self._clip_actions.set_clip_on_off(clip_action[0], t, xclip, ident, args)
                    elif action_name.startswith('DR'):
                        dr = self.get_drum_rack_to_operate_on(t)
                        arg = args.split()[0]
                        if dr and args:
                            if arg in DR_ACTIONS:
                                getattr(self._dr_actions, DR_ACTIONS[arg])(dr, t, xclip, ident, args.strip())
                            elif 'PAD' in args:
                                self._dr_actions.dispatch_pad_action(dr, t, xclip, ident, args.strip())
                    elif action_name in self._user_actions._action_dict:
                        user_action = self._user_actions._action_dict[action_name]
                        getattr(self._user_actions, user_action)(t, args)
        log.debug('action_dispatch triggered, ident=%s and track(s)=%s and action=%s and args=%s',
                  ident, self.track_list_to_string(tracks), action_name, args)

    def handle_external_trigger(self, xtrigger):
        '''This replaces the below method for compatibility with scripts
        that also work with ClyphX Pro.
        '''
        xtrigger.name = '[] {}'.format(xtrigger.name)
        self.handle_action_list_trigger(self.song().view.selected_track, xtrigger)

    def handle_xclip_name(self, track, xclip):
        '''Only for backwards compatibility (primarily with MapEase
        ClyphX Strip and ClyphX XT). It shouldn't be used if possible.
        '''
        self.handle_action_list_trigger(track, xclip)

    def handle_m4l_trigger(self, name):
        '''Convenience method for triggering actions from M4L by simply
        supplying an action name.
        '''
        self.handle_action_list_trigger(self.song().view.selected_track,
                                        ActionList('[] {}'.format(name)))

    def handle_action_list_trigger(self, track, xtrigger):
        '''Directly dispatches snapshot recall, X-Control overrides and
        Seq X-Clips. Otherwise, separates ident from action names,
        splits up lists of action names and calls action dispatch.
        '''
        # TODO: use case?
        if xtrigger is None:
            return

        name = self.get_name(xtrigger.name).strip()
        if name and name[0] == '[' and ']' in name:
            # snap action, so pass directly to snap component
            if ' || (' in name and isinstance(xtrigger, Live.Clip.Clip) and xtrigger.is_playing:
                self._snap_actions.recall_track_snapshot(name, xtrigger)
            # control reassignment, so pass directly to control component
            elif '[[' in name and ']]' in name:
                self._control_component.assign_new_actions(name)
            # standard trigger
            else:
                ident = name[name.index('['):name.index(']')+1].strip()
                raw_action_list = name.replace(ident, '', 1).strip()
                if not raw_action_list:
                    return
                is_play_seq = False
                is_loop_seq = False

                # X-Clips can have on and off action lists
                if isinstance(xtrigger, Live.Clip.Clip):
                    raw_action_list = self.get_xclip_action_list(xtrigger, raw_action_list)
                    if not raw_action_list:
                        return

                # check if the trigger is a PSEQ (accessible to any type of X-Trigger)
                if raw_action_list[0] == '(' and '(PSEQ)' in raw_action_list:
                    is_play_seq = True
                    raw_action_list = raw_action_list.replace('(PSEQ)', '').strip()

                # check if the trigger is a LSEQ (accessible only to X-Clips)
                elif (isinstance(xtrigger, Live.Clip.Clip) and
                        raw_action_list[0] == '(' and
                        '(LSEQ)' in raw_action_list):
                    is_loop_seq = True
                    raw_action_list = raw_action_list.replace('(LSEQ)', '').strip()

                # build formatted action list
                formatted_action_list = []
                for action in raw_action_list.split(';'):
                    action_data = self.format_action_name(track, action.strip())
                    if action_data:
                        formatted_action_list.append(action_data)

                # if seq, pass to appropriate function, else call action
                #   dispatch for each action in the formatted action list
                if formatted_action_list:
                    if is_play_seq:
                        self.handle_play_seq_action_list(formatted_action_list, xtrigger, ident)
                    elif is_loop_seq:
                        self._loop_seq_clips[xtrigger.name] = [ident, formatted_action_list]
                        self.handle_loop_seq_action_list(xtrigger, 0)
                    else:
                        for action in formatted_action_list:
                            self.action_dispatch(
                                action['track'], xtrigger, action['action'], action['args'], ident
                            )
                            log.debug('handle_action_list_trigger triggered, ident=%s and track(s)=%s and action=%s and args=%s',
                                      ident, self.track_list_to_string(action['track']), action['action'], action['args'])

    def get_xclip_action_list(self, xclip, full_action_list):
        '''Get the action list to perform. X-Clips can have an on and
        off action list separated by a comma. This will return which
        action list to perform based on whether the clip is playing. If
        the clip is not playing and there is no off action, this returns
        None.
        '''
        result = None
        split_list = full_action_list.split(',')
        if xclip.is_playing:
            result = split_list[0]
        elif len(split_list) == 2:
            if split_list[1].strip() == '*':
                result = split_list[0]
            else:
                result = split_list[1]
        log.debug('get_xclip_action_list returning %s', result)
        return result

    def replace_user_variables(self, string_with_vars):
        '''Replace any user variables in the given string with the value
        the variable represents.
        '''
        while '%' in string_with_vars:
            var = string_with_vars[string_with_vars.index('%')+1:]
            if '%' in var:
                var = var[0:var.index('%')]
                string_with_vars = string_with_vars.replace(
                    '%{}%'.format(var), self.get_user_variable_value(var), 1
                )
            else:
                string_with_vars = string_with_vars.replace('%', '', 1)
        if '$' in string_with_vars:
            # for compat with old-style variables
            for string in string_with_vars.split():
                if '$' in string and not '=' in string:
                    var = string.replace('$', '')
                    string_with_vars = string_with_vars.replace(
                        '${}'.format(var), self.get_user_variable_value(var), 1
                    )
        log.debug('replace_user_variables returning %s', string_with_vars)
        return string_with_vars

    def get_user_variable_value(self, var):
        '''Get the value of the given variable name or 0 if var name not
        found.
        '''
        result = '0'
        if var in self._user_variables:
            result = self._user_variables[var]
        log.debug('get_user_variable_value returning %s=%s', var, result)
        return result

    def handle_user_variable_assignment(self, string_with_assign):
        '''Handle assigning new value to variable with either assignment
        or expression enclosed in parens.
        '''
        # for compat with old-style variables
        string_with_assign = string_with_assign.replace('$', '')
        var_data = string_with_assign.split('=')
        if len(var_data) >= 2 and not ';' in var_data[1] and not '%' in var_data[1] and not '=' in var_data[1]:
            if '(' in var_data[1] and ')' in var_data[1]:
                try:
                    self._user_variables[var_data[0].strip()] = str(eval(var_data[1].strip()))
                except:
                    pass
            else:
                self._user_variables[var_data[0].strip()] = var_data[1].strip()
            log.debug('handle_user_variable_assignment, %s=%s',
                      var_data[0].strip(), var_data[1].strip())

    def format_action_name(self, origin_track, origin_name):
        '''Replaces vars (if any) then splits up track, action name and
        arguments (if any) and returns dict.
        '''
        result_name = self.replace_user_variables(origin_name)
        if '=' in result_name:
            self.handle_user_variable_assignment(result_name)
            return
        result_track = [origin_track]
        if len(result_name) >= 4 and (
            ('/' in result_name[:4]) or
            ('-' in result_name[:4] and '/' in result_name[4:]) or
            (result_name[0] == '"' and '"' in result_name[1:])
        ):
            track_data = self.get_track_to_operate_on(result_name)
            result_track, result_name = track_data[0:2]
        args = ''
        name = result_name.split()
        if len(name) > 1:
            args = result_name.replace(name[0], '', 1)
            result_name = result_name.replace(args, '')
        log.debug('format_action_name returning, track(s)=%s and action=%s and args=%s',
                  self.track_list_to_string(result_track), result_name.strip(), args.strip())
        return {'track': result_track, 'action': result_name.strip(), 'args': args.strip()}

    def handle_loop_seq_action_list(self, xclip, count):
        '''Handles sequenced action lists, triggered by xclip looping.
        '''
        if xclip.name in self._loop_seq_clips:
            if count >= len(self._loop_seq_clips[xclip.name][1]):
                count -= ((count / len(self._loop_seq_clips[xclip.name][1])) * len(self._loop_seq_clips[xclip.name][1]))
            action = self._loop_seq_clips[xclip.name][1][count]
            self.action_dispatch(action['track'],
                                 xclip,
                                 action['action'],
                                 action['args'],
                                 self._loop_seq_clips[xclip.name][0])
            log.debug('handle_loop_seq_action_list triggered, xclip.name=%s and track(s)=%s and action=%s and args=%s',
                      xclip.name, self.track_list_to_string(action['track']), action['action'], action['args'])

    def handle_play_seq_action_list(self, action_list, xclip, ident):
        '''Handles sequenced action lists, triggered by replaying/
        retriggering the xtrigger.
        '''
        if xclip.name in self._play_seq_clips:
            count = self._play_seq_clips[xclip.name][1] + 1
            if count > len(self._play_seq_clips[xclip.name][2]) - 1:
                count = 0
            self._play_seq_clips[xclip.name] = [ident, count, action_list]
        else:
            self._play_seq_clips[xclip.name] = [ident, 0, action_list]
        action = self._play_seq_clips[xclip.name][2][self._play_seq_clips[xclip.name][1]]
        self.action_dispatch(action['track'], xclip, action['action'], action['args'], ident)
        log.debug('handle_play_seq_action_list triggered, ident=%s and track(s)=%s and action=%s and args=%s',
                  ident, self.track_list_to_string(action['track']), action['action'], action['args'])

    def do_parameter_adjustment(self, param, value):
        '''Adjust (</>, reset, random, set val) continuous params, also
        handles quantized param adjustment (should just use +1/-1 for
        those).
        '''
        if not param.is_enabled:
            return ()
        step = (param.max - param.min) / 127
        new_value = param.value
        if value.startswith(('<', '>')):
            factor = self.get_adjustment_factor(value)
            new_value += factor if param.is_quantized else (step * factor)
        elif value == 'RESET' and not param.is_quantized:
            new_value = param.default_value
        elif 'RND' in value and not param.is_quantized:
            rnd_min = 0
            rnd_max = 128
            if value != 'RND' and '-' in value:
                rnd_range_data = value.replace('RND', '').split('-')
                if len(rnd_range_data) == 2:
                    try:
                        new_min = int(rnd_range_data[0])
                    except:
                        new_min = 0
                    try:
                        new_max = int(rnd_range_data[1]) + 1
                    except:
                        new_max = 128
                    if 0 <= new_min and new_max <= 128 and new_min < new_max:
                        rnd_min = new_min
                        rnd_max = new_max
            rnd_value = (Live.Application.get_random_int(0, 128) * (rnd_max - rnd_min) / 127) + rnd_min
            new_value = (rnd_value * step) + param.min

        else:
            try:
                if 0 <= int(value) < 128:
                    try:
                        new_value = (int(value) * step) + param.min
                    except:
                        new_value = param.value
            except:
                pass
        if param.min <= new_value <= param.max:
            param.value = new_value
            log.debug('do_parameter_adjustment called on %s, set value to %s',
                      param.name, new_value)

    def get_adjustment_factor(self, string, as_float=False):
        '''Get factor for use with < > actions.'''
        factor = 1

        if len(string) > 1:
            try:
                factor = (float if as_float else int)(string[1:])
            except:
                factor = 1

        if string.startswith('<'):
            factor = -(factor)
        log.debug('get_adjustment_factor returning factor=%s', factor)
        return factor

    def get_track_to_operate_on(self, origin_name):
        '''Gets track or tracks to operate on.'''
        result_tracks = []
        result_name = origin_name
        if '/' in origin_name:
            tracks = list(tuple(self.song().tracks) + tuple(self.song().return_tracks) + (self.song().master_track,))
            sel_track_index = tracks.index(self.song().view.selected_track)
            if origin_name.index('/') > 0:
                track_spec = origin_name.split('/')[0].strip()
                if '"' in track_spec:
                    track_spec = self.get_track_index_by_name(track_spec, tracks)
                if 'SEL' in track_spec:
                    track_spec = track_spec.replace('SEL', str(sel_track_index + 1), 1)
                if 'MST' in track_spec:
                    track_spec = track_spec.replace('MST', str(len(tracks)), 1)
                if track_spec == 'ALL':
                    result_tracks = tracks
                else:
                    track_range_spec = track_spec.split('-')
                    if len(track_range_spec) <= 2:
                        track_range = []
                        try:
                            for spec in track_range_spec:
                                track_index = -1
                                if spec.startswith(('<', '>')):
                                    try:
                                        track_index = self.get_adjustment_factor(spec) + sel_track_index
                                    except:
                                        pass
                                else:
                                    try:
                                        track_index = int(spec) - 1
                                    except:
                                        track_index = (ord(spec) - 65) + len(self.song().tracks)
                                if 0 <= track_index < len(tracks):
                                    track_range.append(track_index)
                        except:
                            track_range = []

                        if track_range:
                            if len(track_range) == 2:
                                if track_range[0] < track_range[1]:
                                    for i in range(track_range[0], track_range[1] + 1):
                                        result_tracks.append(tracks[i])
                            else:
                                result_tracks = [tracks[track_range[0]]]
            result_name = origin_name[origin_name.index('/')+1:].strip()
        log.debug('get_track_to_operate_on returning result_tracks=%s and result_name=%s',
                  self.track_list_to_string(result_tracks), result_name)
        return (result_tracks, result_name)

    def get_track_index_by_name(self, name, tracks):
        '''Gets the index(es) associated with the track name(s) specified
        in name.
        '''
        while '"' in name:
            track_name = name[name.index('"')+1:]
            if '"' in track_name:
                track_name = track_name[0:track_name.index('"')]
                track_index = ''
                def_name = ''
                if ' AUDIO' in track_name or ' MIDI' in track_name:
                    # in Live GUI, default names are 'n Audio' or 'n MIDI',
                    #   in API it's 'n-Audio' or 'n-MIDI'
                    def_name = track_name.replace(' ', '-')
                for track in tracks:
                    current_track_name = self.get_name(track.name)
                    if current_track_name in {track_name, def_name}:
                        track_index = str(tracks.index(track) + 1)
                        break
                name = name.replace('"{}"'.format(track_name), track_index, 1)
                name = name.replace('"{}"'.format(def_name), track_index, 1)
            else:
                name = name.replace('"', '', 1)
        return name

    def get_device_to_operate_on(self, track, action_name, args):
        '''Get device to operate on and action to perform with args.
        '''
        device = None
        device_args = args
        if 'DEV"' in action_name:
            dev_name = action_name[action_name.index('"')+1:]
            if '"' in args:
                dev_name = action_name[action_name.index('"')+1:] + ' ' + args
                device_args = args[args.index('"')+1:].strip()
            if '"' in dev_name:
                dev_name = dev_name[0:dev_name.index('"')]
            for dev in track.devices:
                if dev.name.upper() == dev_name:
                    device = dev
                    break
        else:
            if action_name == 'DEV':
                device = track.view.selected_device
                if device is None:
                    if track.devices:
                        device = track.devices[0]
            else:
                try:
                    dev_num = action_name.replace('DEV', '')
                    if '.' in dev_num and self._can_have_nested_devices:
                        dev_split = dev_num.split('.')
                        top_level = track.devices[int(dev_split[0]) - 1]
                        if top_level and top_level.can_have_chains:
                            device = top_level.chains[int(dev_split[1]) - 1].devices[0]
                            if len(dev_split) > 2:
                                device = top_level.chains[int(dev_split[1]) - 1].devices[int(dev_split[2]) - 1]
                    else:
                        device = track.devices[int(dev_num) - 1]
                except:
                    pass
        log.debug('get_device_to_operate_on returning device=%s and device args=%s',
                  device.name if device else 'None', device_args)
        return (device, device_args)

    def get_clip_to_operate_on(self, track, action_name, args):
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
            if clip is None and track.clip_slots[slot_idx].has_clip:
                clip = track.clip_slots[slot_idx].clip
        log.debug('get_clip_to_operate_on returning clip=%s and clip args=%s',
                  clip.name if clip else 'None', clip_args)
        return (clip, clip_args)

    def get_drum_rack_to_operate_on(self, track):
        '''Get drum rack to operate on.
        '''
        dr = None
        for device in track.devices:
            if device.can_have_drum_pads:
                dr = device
                break
        log.debug('get_drum_rack_to_operate_on returning dr=%s',
                  dr.name if dr else 'None')
        return dr

    def get_user_settings(self, midi_map_handle):
        '''Get user settings (variables, prefs and control settings)
        from text file and perform startup actions if any.
        '''
        import sys

        list_to_build = None
        ctrl_data = []
        prefs_data = []
        try:
            mrs_path = ''
            for path in sys.path:
                if 'MIDI Remote Scripts' in path:
                    mrs_path = path
                    break
            user_file = mrs_path + FOLDER + 'UserSettings.txt'
            if not self._user_settings_logged:
                log.info('Attempting to read UserSettings file: %s', user_file)
            for line in open(user_file):
                line = self.get_name(line.rstrip('\n')).strip()
                if not line:
                    continue
                if line[0] not in {'#', '"', '*'} and not self._user_settings_logged:
                    log.info(str(line))
                if not line.startswith(
                    ('#', '"', 'STARTUP_', 'INCLUDE_NESTED_', 'SNAPSHOT_',
                     'PROCESS_XCLIPS_', 'PUSH_EMU', 'APC_PUSH_EMU', 'CSLINKER')
                ):
                    if '[USER CONTROLS]' in line:
                        list_to_build = 'controls'
                    elif '[USER VARIABLES]' in line:
                        list_to_build = 'vars'
                    elif '[EXTRA PREFS]' in line:
                        list_to_build = 'prefs'
                    elif '=' in line:
                        if list_to_build == 'vars':
                            line = self.replace_user_variables(line)
                            self.handle_user_variable_assignment(line)
                        elif list_to_build == 'controls':
                            ctrl_data.append(line)
                        elif list_to_build == 'prefs':
                            prefs_data.append(line)
                elif 'PUSH_EMULATION' in line:
                    self._push_emulation = line.split('=')[1].strip() == 'ON'
                    if self._push_emulation:
                        if 'APC' in line:
                            with self.component_guard():
                                self._PushApcCombiner = PushApcCombiner(self)
                        self.enable_push_emulation(self._control_surfaces())
                elif line.startswith('INCLUDE_NESTED_DEVICES_IN_SNAPSHOTS ='):
                    include_nested = self.get_name(line[37:].strip())
                    include_nested_devices = False
                    if include_nested.startswith('ON'):
                        include_nested_devices = True
                    self._snap_actions._include_nested_devices = include_nested_devices
                elif line.startswith('SNAPSHOT_PARAMETER_LIMIT ='):
                    try:
                        limit = int(line[26:].strip())
                    except:
                        limit = 500
                    self._snap_actions._parameter_limit = limit
                elif line.startswith('PROCESS_XCLIPS_IF_TRACK_MUTED ='):
                    self._process_xclips_if_track_muted = line.split('=')[1].strip() == 'TRUE'
                elif line.startswith('STARTUP_ACTIONS =') and not self._startup_actions_complete:
                    actions = line[17:].strip()
                    if actions != 'OFF':
                        action_list = '[]{}'.format(actions)
                        self.schedule_message(2, partial(self.perform_startup_actions, action_list))
                        self._startup_actions_complete = True
                elif line.startswith('CSLINKER'):
                    self._cs_linker.parse_settings(line)
            if ctrl_data:
                self._control_component.get_user_control_settings(ctrl_data, midi_map_handle)
            if prefs_data:
                self._extra_prefs.get_user_settings(prefs_data)
        except:
            pass

    def enable_push_emulation(self, scripts):
        '''Try to disable Push's handshake to allow for emulation.

        If emulating for APC, set scripts on combiner component.
        '''
        for script in scripts:
            script_name = script.__class__.__name__
            if script_name == 'Push':
                if True:
                    with script._component_guard():
                        script._start_handshake_task = MockHandshakeTask()
                        script._handshake = MockHandshake()
                    if self._PushApcCombiner:
                        self._PushApcCombiner.set_up_scripts(self._control_surfaces())
                # legacy <9.5 code
                # else:
                #     script._handshake._identification_timeout_task.kill()
                #     script._handshake._identification_timeout_task = Task.Task()
                break

    def start_debugging(self):
        '''Turn on debugging and write all user vars/controls/actions to
        Live's log file to assist in troubleshooting.
        '''
        self._is_debugging = True
        log.info('------- ClyphX Log: Logging User Variables -------')
        for key, value in iteritems(self._user_variables):
            log.info('%s=%s', key, value)

        log.info('------- ClyphX Log: Logging User Controls -------')
        for key, value in iteritems(self._control_component._control_list):
            log.info('%s on_action=%s and off_action=%s',
                        key, value['on_action'], value['off_action'])

        log.info('------- ClyphX Log: Logging User Actions -------')
        for key, value in iteritems(self._user_actions._action_dict):
            log.info('%s=%s', key, value)
        log.info('------- ClyphX Log: Debugging Started -------')

    def track_list_to_string(self, track_list):
        '''Convert list of tracks to a string of track names or None if
        no tracks. This is used for debugging.
        '''
        result = 'None'
        if track_list:
            result = '['
            for track in track_list:
                result += track.name + ', '
            result = result[:len(result)-2]
        return result + ']'

    def perform_startup_actions(self, action_list):
        '''Delay startup action so it can perform actions on values that
        are changed upon set load (like overdub).
        '''
        self.handle_action_list_trigger(self.song().view.selected_track,
                                        ActionList(action_list))

    def setup_tracks(self):
        '''Setup component tracks on ini and track list changes. Also
        call Macrobat's get rack.
        '''
        for t in self.song().tracks:
            self._macrobat.setup_tracks(t)
            if self._current_tracks and t in self._current_tracks:
                pass
            else:
                self._current_tracks.append(t)
                XTrackComponent(self, t)
        for r in chain(self.song().return_tracks, (self.song().master_track,)):
            self._macrobat.setup_tracks(r)
        self._snap_actions.setup_tracks()

    def get_name(self, name):
        '''Convert name to upper-case string or return blank string if
        couldn't be converted.
        '''
        try:
            name = str(name).upper()
        except:
            name = ''
        return name

    def _on_track_list_changed(self):
        super(ClyphX, self)._on_track_list_changed()
        self.setup_tracks()

    def connect_script_instances(self, instanciated_scripts):
        '''Pass connect scripts call to control component.'''
        self._control_component.connect_script_instances(instanciated_scripts)
        self._control_surface_actions.connect_script_instances(instanciated_scripts)
        if self._push_emulation:
            self.enable_push_emulation(instanciated_scripts)

    def build_midi_map(self, midi_map_handle):
        '''Build user-defined list of midi messages for controlling
        ClyphX track.
        '''
        super(ClyphX, self).build_midi_map(midi_map_handle)
        if self._user_settings_logged:
            self._control_component.rebuild_control_map(midi_map_handle)
        else:
            self.get_user_settings(midi_map_handle)
            self._user_settings_logged = True
        if self._push_emulation:
            self.enable_push_emulation(self._control_surfaces())

    def receive_midi(self, midi_bytes):
        '''Receive user-specified messages and send to control script.
        '''
        super(ClyphX, self).receive_midi(midi_bytes)
        self._control_component.receive_midi(midi_bytes)

    def handle_sysex(self, midi_bytes):
        '''Handle sysex received from controller.'''
        pass

    def handle_nonsysex(self, midi_bytes):
        '''Override so that ControlSurface doesn't report this to
        Log.txt.
        '''
        pass
