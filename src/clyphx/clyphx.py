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
from builtins import super, dict, range, map
from typing import TYPE_CHECKING
from functools import partial
from itertools import chain
import logging
import os

from _Framework.ControlSurface import OptimizedControlSurface
from .core.legacy import _DispatchCommand, _SingleDispatch
from .core.utils import repr_tracklist, set_user_profile
from .core.live import Live, Track, DeviceIO, Clip, get_random_int
# from .core.parse import SpecParser
from .consts import LIVE_VERSION, SCRIPT_INFO
from .extra_prefs import ExtraPrefs
from .user_config import get_user_settings
from .user_actions import XUserActions
from .macrobat import Macrobat
from .cs_linker import CsLinker
from .m4l_browser import XM4LBrowserInterface
from .push_apc_combiner import PushApcCombiner
from .push_mocks import MockHandshakeTask, MockHandshake
from .triggers import (
    XTrackComponent,
    XControlComponent,
    XCueComponent,
    ActionList,
    get_xclip_action_list,
)
from .actions import (
    XGlobalActions, GLOBAL_ACTIONS,
    XTrackActions, TRACK_ACTIONS,
    XClipActions,
    XDeviceActions,
    XDrActions,
    XSnapActions,
    XCsActions,
)

if TYPE_CHECKING:
    from typing import (Any, Text, Union, Optional, Dict,
                        Iterable, Sequence, List, Tuple)
    from .core.live import (Clip, Device, DeviceParameter,
                            Track, MidiRemoteScript)
    from .triggers import XTrigger

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ClyphX(OptimizedControlSurface):
    '''ClyphX Main.
    '''
    __module__ = __name__

    def __init__(self, c_instance):
        # type: (MidiRemoteScript) -> None
        super().__init__(c_instance)
        set_user_profile()
        self._user_settings_logged = False
        self._is_debugging = False
        self._push_emulation = False
        self._PushApcCombiner = None
        self._process_xclips_if_track_muted = True
        self._user_settings = get_user_settings()
        # self.parse = SpecParser()
        with self.component_guard():
            self.macrobat = Macrobat(self)
            self._extra_prefs = ExtraPrefs(self, self._user_settings.prefs)
            self.cs_linker = CsLinker()
            self.track_actions = XTrackActions(self)
            self.snap_actions = XSnapActions(self)
            self.global_actions = XGlobalActions(self)
            self.device_actions = XDeviceActions(self)
            self.dr_actions = XDrActions(self)
            self.clip_actions = XClipActions(self)
            self.cs_actions = XCsActions(self)
            self.user_actions = XUserActions(self)
            self.control_component = XControlComponent(self)
            XM4LBrowserInterface(self)
            XCueComponent(self)
            self._startup_actions_complete = False
            self._user_variables = dict()   # type: Dict[Text, Any]
            self._play_seq_clips = dict()   # type: Dict[Text, Any]
            self._loop_seq_clips = dict()   # type: Dict[Text, Any]
            self.current_tracks = []  # type: List[Any]
            self._can_have_nested_devices = True
            self.setup_tracks()
        msg = '--- %s --- Live Version: %s ---'
        log.info(msg, SCRIPT_INFO, '.'.join(map(str, LIVE_VERSION)))
        self.show_message(SCRIPT_INFO)

        from .dev_doc import get_device_params
        from .core.utils import get_user_clyphx_path
        path = get_user_clyphx_path('live_instant_mapping.md')
        log.info('Updating Live Instant Mapping info')
        with open(path, 'w') as f:
            f.write(get_device_params(format='md', tables=True))  # type: ignore


    def disconnect(self):
        for attr in (
            '_PushApcCombiner', 'macrobat', '_extra_prefs', 'cs_linker',
            'track_actions', 'snap_actions', 'global_actions',
            'device_actions', 'dr_actions', 'clip_actions', 'cs_actions',
            'user_actions', 'control_component', '_user_variables',
            '_play_seq_clips', '_loop_seq_clips', 'current_tracks',
        ):
            setattr(self, attr, None)
        super().disconnect()

    @property
    def _is_debugging(self):
        # type: () -> bool
        return log.getEffectiveLevel() <= 10

    @_is_debugging.setter
    def _is_debugging(self, value):
        log.setLevel(logging.DEBUG if value else logging.INFO)

    def start_debugging(self):
        '''Turn on debugging and write all user vars/controls/actions to
        Live's log file to assist in troubleshooting.
        '''
        self._is_debugging = True
        log.info('------- Logging User Variables -------')
        for key, value in self._user_variables.items():
            log.info('%s=%s', key, value)

        log.info('------- Logging User Controls -------')
        for key, value in self.control_component._control_list.items():
            log.info('%s on_action=%s and off_action=%s',
                        key, value['on_action'], value['off_action'])

        log.info('------- Logging User Actions -------')
        for key, value in self.user_actions._action_dict.items():
            log.info('%s=%s', key, value)
        log.info('------- Debugging Started -------')

    def handle_dispatch_command(self, cmd):
        try:
            self._handle_dispatch_command(cmd)
        except Exception as e:
            log.exception('Failed to dispatch command: %r', cmd)

    def _handle_dispatch_command(self, cmd):
        # type: (_DispatchCommand) -> None
        '''Command handler.

        Main dispatch for calling appropriate class of actions, passes
        all necessary arguments to class method.
        '''
        name = cmd.action_name

        if not cmd.tracks:
            return  # how?

        if name.startswith('SNAP'):
            self.snap_actions.dispatch_actions(cmd)
        elif name.startswith('DEV'):
            self.device_actions.dispatch_device_actions(cmd)
        elif name.startswith('CLIP'):
            self.clip_actions.dispatch_actions(cmd)
        elif name == 'LOOPER':
            self.device_actions.dispatch_looper_actions(cmd)
        elif name in TRACK_ACTIONS:
            self.track_actions.dispatch_actions(cmd)
        elif name in GLOBAL_ACTIONS:
            self.global_actions.dispatch_action(cmd.to_single())
        elif name.startswith('DR'):
            self.dr_actions.dispatch_dr_actions(cmd)
        elif name.startswith(('SURFACE', 'CS', 'ARSENAL', 'PUSH', 'PXT', 'MXT')):
            self.cs_actions.dispatch_action(cmd.to_single())
        elif name in self.user_actions._action_dict:
            self.dispatch_user_actions(cmd)
        elif name == 'PSEQ' and cmd.args== 'RESET':
            for v in self._play_seq_clips.values():
                v[1] = -1
        elif name == 'DEBUG':
            if isinstance(cmd.xclip, Clip):
                cmd.xclip.name = str(cmd.xclip.name).upper().replace('DEBUG', 'Debugging Activated')
            self.start_debugging()
        else:
            log.error('Not found dispatcher for %r', cmd)
            return

    def dispatch_user_actions(self, cmd):
        # type: (_DispatchCommand) -> None
        action_name = self.user_actions._action_dict[cmd.action_name]
        action = getattr(self.user_actions, action_name)
        for t in cmd.tracks:
            action(t, cmd.args)

    def handle_external_trigger(self, xtrigger):
        # type: (XTrigger) -> None
        '''This replaces the below method for compatibility with scripts
        that also work with ClyphX Pro.
        '''
        xtrigger.name = '[] {}'.format(xtrigger.name)
        self.handle_action_list_trigger(self.song().view.selected_track, xtrigger)

    # deprecated
    def handle_xclip_name(self, track, xclip):
        # type: (Track, Clip) -> None
        '''Only for backwards compatibility (primarily with MapEase
        ClyphX Strip and ClyphX XT). It shouldn't be used if possible.
        '''
        self.handle_action_list_trigger(track, xclip)

    def handle_m4l_trigger(self, name):
        # type: (Text) -> None
        '''Convenience method for triggering actions from M4L by simply
        supplying an action name.
        '''
        self.handle_action_list_trigger(self.song().view.selected_track,
                                        ActionList('[] {}'.format(name)))

    def handle_action_list_trigger(self, track, xtrigger):
        # type: (Track, XTrigger) -> None
        '''Directly dispatches snapshot recall, X-Control overrides and
        Seq X-Clips. Otherwise, separates ident from action names,
        splits up lists of action names and calls action dispatch.
        '''
        log.debug('ClyphX.handle_action_list_trigger'
                  '(track=%r, xtrigger=%r)', track, xtrigger)
        if xtrigger == None:
            # TODO: use case?
            return

        name = xtrigger.name.strip().upper()
        if name and name[0] == '[' and ']' in name:

            # snap action, so pass directly to snap component
            if ' || (' in name and isinstance(xtrigger, Clip) and xtrigger.is_playing:
                # self.snap_actions.recall_track_snapshot(name, xtrigger)
                self.snap_actions.recall_track_snapshot(None, xtrigger)

            # control reassignment, so pass directly to control component
            elif '[[' in name and ']]' in name:
                self.control_component.assign_new_actions(name)

            # standard trigger
            else:
                ident = name[name.index('['):name.index(']')+1].strip()
                raw_action_list = name.replace(ident, '', 1).strip()
                if not raw_action_list:
                    return
                is_play_seq = False
                is_loop_seq = False

                # X-Clips can have on and off action lists
                if isinstance(xtrigger, Clip):
                    raw_action_list = get_xclip_action_list(xtrigger, raw_action_list)
                    if not raw_action_list:
                        return

                # check if the trigger is a PSEQ (accessible to any type of X-Trigger)
                if raw_action_list[0] == '(' and '(PSEQ)' in raw_action_list:
                    is_play_seq = True
                    raw_action_list = raw_action_list.replace('(PSEQ)', '').strip()

                # check if the trigger is a LSEQ (accessible only to X-Clips)
                elif (isinstance(xtrigger, Clip) and
                        raw_action_list[0] == '(' and
                        '(LSEQ)' in raw_action_list):
                    is_loop_seq = True
                    raw_action_list = raw_action_list.replace('(LSEQ)', '').strip()

                # build formatted action list
                formatted_action_list = []  # List[Dict[Text, Any]]
                for action_ in raw_action_list.split(';'):
                    action_data = self.format_action_name(track, action_.strip())
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
                        # TODO: split in singledispatch per track?
                        for action in formatted_action_list:
                            command = _DispatchCommand(action['track'],
                                                       xtrigger,
                                                       ident,
                                                       action['action'],
                                                       action['args'])
                            self.handle_dispatch_command(command)

    def format_action_name(self, origin_track, origin_name):
        # type: (Any, Text) -> Optional[Dict[Text, Any]]
        '''Replaces vars (if any) then splits up track, action name and
        arguments (if any) and returns dict.
        '''
        result_name = self._user_settings.vars.sub(origin_name)
        if '=' in result_name:
            self._user_settings.vars.add(result_name)
            return None
        result_track = [origin_track]
        if len(result_name) >= 4 and (
            ('/' in result_name[:4]) or
            ('-' in result_name[:4] and '/' in result_name[4:]) or
            (result_name[0] == '"' and '"' in result_name[1:])
        ):
            result_track, result_name = self.get_track_to_operate_on(result_name)
        args = ''
        name = result_name.split()
        if len(name) > 1:
            args = result_name.replace(name[0], '', 1)
            result_name = result_name.replace(args, '')
        log.debug('format_action_name -> track(s)=%s, action=%s, args=%s',
                  repr_tracklist(result_track), result_name.strip(), args.strip())
        return dict(track=result_track, action=result_name.strip(), args=args.strip())

    def handle_loop_seq_action_list(self, xclip, count):
        # type: (Clip, int) -> None
        '''Handles sequenced action lists, triggered by xclip looping.
        '''
        if xclip.name in self._loop_seq_clips:
            if count >= len(self._loop_seq_clips[xclip.name][1]):
                count -= (
                    (count // len(self._loop_seq_clips[xclip.name][1]))
                    * len(self._loop_seq_clips[xclip.name][1])
                )
            action = self._loop_seq_clips[xclip.name][1][count]
            # TODO: _SingleDispatch?
            command = _DispatchCommand(action['track'],
                                       xclip,
                                       self._loop_seq_clips[xclip.name][0],
                                       action['action'],
                                       action['args'])
            self.handle_dispatch_command(command)

    def handle_play_seq_action_list(self, action_list, xclip, ident):
        # type: (Any, Clip, Text) -> None
        '''Handles sequenced action lists, triggered by replaying/
        retriggering the xtrigger.
        '''
        if xclip.name not in self._play_seq_clips:
            count = 0
        else:
            count = self._play_seq_clips[xclip.name][1] + 1
            if count > len(self._play_seq_clips[xclip.name][2]) - 1:
                count = 0
        self._play_seq_clips[xclip.name] = [ident, count, action_list]
        action = self._play_seq_clips[xclip.name][2][self._play_seq_clips[xclip.name][1]]
        # TODO: _SingleDispatch?
        command = _DispatchCommand(action['track'],
                                    xclip,
                                    self._loop_seq_clips[xclip.name][0],
                                    action['action'],
                                    action['args'])
        self.handle_dispatch_command(command)

    def do_parameter_adjustment(self, param, value):
        # type: (DeviceParameter, Text) -> None
        '''Adjust (</>, reset, random, set val) continuous params, also
        handles quantized param adjustment (should just use +1/-1 for
        those).
        '''
        if not param.is_enabled:
            return
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
            rnd_value = (get_random_int(0, 128) * (rnd_max - rnd_min) / 127) + rnd_min
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
        # type: (Text, bool) -> Union[int, float]
        '''Get factor for use with < > actions.'''
        factor = 1

        if len(string) > 1:
            try:
                factor = (float if as_float else int)(string[1:])
            except:
                factor = 1

        if string.startswith('<'):
            factor = -(factor)
        return factor

    def get_track_to_operate_on(self, origin_name):
        # type: (Text) -> Tuple[List[Any], Text]
        '''Gets track or tracks to operate on.'''
        result_tracks = []
        result_name = origin_name
        if '/' in origin_name:
            tracks = self.song().tracks + self.song().return_tracks + (self.song().master_track,)  # type: Tuple[Track]
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
                                        track_index = (self.get_adjustment_factor(spec)
                                                       + sel_track_index)
                                    except:
                                        pass
                                else:
                                    try:
                                        track_index = int(spec) - 1
                                    except:
                                        track_index = ((ord(spec) - 65)
                                                       + len(self.song().tracks))
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
            result_name = origin_name[origin_name.index('/') + 1:].strip()
        log.debug('get_track_to_operate_on -> result_tracks=%s, result_name=%s',
                  repr_tracklist(result_tracks), result_name)
        return (result_tracks, result_name)

    def get_track_index_by_name(self, name, tracks):
        # type: (Text, Sequence[Any]) -> Text
        '''Gets the index(es) associated with the track name(s)
        specified in name.
        '''
        while '"' in name:
            track_name = name[name.index('"')+1:]
            if '"' in track_name:
                track_name = track_name[0:track_name.index('"')]
                track_index = ''
                def_name = ''
                if ' AUDIO' in track_name or ' MIDI' in track_name:
                    # in Live GUI, default names are 'n Audio' or
                    #   'n MIDI', in API it's 'n-Audio' or 'n-MIDI'
                    def_name = track_name.replace(' ', '-')
                for track in tracks:
                    current_track_name = track.name.upper()
                    if current_track_name in {track_name, def_name}:
                        track_index = str(tracks.index(track) + 1)
                        break
                name = name.replace('"{}"'.format(track_name), track_index, 1)
                name = name.replace('"{}"'.format(def_name), track_index, 1)
            else:
                name = name.replace('"', '', 1)
        return name

    def get_device_to_operate_on(self, track, action_name, args):
        # type: (Track, Text, Text) -> Tuple[Optional[Device], Text]
        '''Get device to operate on and action to perform with args.
        '''
        device = None
        device_args = args
        if 'DEV"' in action_name:
            dev_name = action_name[action_name.index('"')+1:]
            if '"' in args:
                dev_name = '{} {}'.format(action_name[action_name.index('"')+1:], args)
                device_args = args[args.index('"')+1:].strip()
            if '"' in dev_name:
                dev_name = dev_name[0:dev_name.index('"')]
            for dev in track.devices:
                if dev.name.upper() == dev_name:
                    device = dev
                    break
        elif action_name == 'DEV':
            device = track.view.selected_device
            if device != None:
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
            except Exception as e:
                raise Exception(e)
                # pass
        log.debug('get_device_to_operate_on returning device=%s and device args=%s',
                  device.name if device else 'None', device_args)
        return (device, device_args)

    def _get_snapshot_settings(self, settings):
        try:
            include_nested = settings['include_nested_devices_in_snapshots']
            self.snap_actions._include_nested_devices = include_nested
        except KeyError:
            pass
        try:
            param_limit = settings['snapshot_parameter_limit']
            self.snap_actions._parameter_limit = param_limit
        except KeyError:
            # TODO: set only if defined in usersettings.txt?
            self.snap_actions._parameter_limit = 500

    # compare with ExtraPrefs
    def _get_some_extra_prefs(self, settings):
        if not self._startup_actions_complete:
            actions = settings.get('startup_actions', False)
            if actions:
                msg = partial(self.perform_startup_actions, '[] {}'.format(actions))
                self.schedule_message(2, msg)
                self._startup_actions_complete = True

        try:
            process_in_mute = settings['process_xclips_if_track_muted']
            self._process_xclips_if_track_muted = process_in_mute
        except KeyError:
            # TODO: set only if in usersettings?
            pass

    def get_user_settings(self, midi_map_handle):
        '''Get user settings (variables, prefs and control settings)
        from text file and perform startup actions if any.
        '''
        self._get_snapshot_settings(self._user_settings.snapshot_settings)
        self._get_some_extra_prefs(self._user_settings.extra_prefs)
        self.cs_linker.read_settings(self._user_settings.cslinker)
        self.control_component.get_user_controls(self._user_settings.xcontrols,
                                                 midi_map_handle)

    def enable_push_emulation(self, scripts):
        # type: (Iterable[Any]) -> None
        '''Try to disable Push's handshake to allow for emulation.

        If emulating for APC, set scripts on combiner component.
        '''
        for script in scripts:
            script_name = script.__class__.__name__
            if script_name == 'Push':
                with script._component_guard():
                    script._start_handshake_task = MockHandshakeTask()
                    script._handshake = MockHandshake()
                if self._PushApcCombiner:
                    self._PushApcCombiner.set_up_scripts(self._control_surfaces())
                break

    def perform_startup_actions(self, action_list):
        # type: (Text) -> None
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
            self.macrobat.setup_tracks(t)
            if not (self.current_tracks and t in self.current_tracks):
                self.current_tracks.append(t)
                XTrackComponent(self, t)
        for r in chain(self.song().return_tracks, (self.song().master_track,)):
            self.macrobat.setup_tracks(r)
        self.snap_actions.setup_tracks()

    def _on_track_list_changed(self):
        super()._on_track_list_changed()
        self.setup_tracks()

    def connect_script_instances(self, instantiated_scripts):
        '''Pass connect scripts call to control component.'''
        self.control_component.connect_script_instances(instantiated_scripts)
        self.cs_actions.connect_script_instances(instantiated_scripts)
        if self._push_emulation:
            self.enable_push_emulation(instantiated_scripts)

    def build_midi_map(self, midi_map_handle):
        '''Build user-defined list of MIDI messages for controlling
        ClyphX track.
        '''
        super().build_midi_map(midi_map_handle)
        if self._user_settings_logged:
            self.control_component.rebuild_control_map(midi_map_handle)
        else:
            self.get_user_settings(midi_map_handle)
            self._user_settings_logged = True
        if self._push_emulation:
            self.enable_push_emulation(self._control_surfaces())
        log.info('MIDI map built')

    def receive_midi(self, midi_bytes):
        '''Receive user-specified messages and send to control script.
        '''
        super().receive_midi(midi_bytes)
        self.control_component.receive_midi(midi_bytes)

    def handle_sysex(self, midi_bytes):
        # type: (Any) -> None
        '''Handle sysex received from controller.'''

    def handle_nonsysex(self, midi_bytes):
        # type: (Any) -> None
        '''Override so that ControlSurface doesn't report this to
        Log.txt.
        '''
