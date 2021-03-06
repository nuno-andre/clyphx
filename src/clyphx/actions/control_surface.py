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
from functools import partial
from typing import TYPE_CHECKING

from ableton.v2.control_surface import ControlSurface as CS
from _Framework.ControlSurface import ControlSurface
from _Framework.MixerComponent import MixerComponent
from _Framework.DeviceComponent import DeviceComponent

from ..core.xcomponent import XComponent, SessionComponent
from ..core.live import Clip
from ..consts import REPEAT_STATES
from .push import XPushActions
from .pxt_live import XPxtActions
from .mxt_live import XMxtActions
from .arsenal import XArsenalActions

if TYPE_CHECKING:
    from typing import Any, Iterable, Sequence, Dict, Optional, Tuple, Text
    from ..core.legacy import _DispatchCommand, _SingleDispatch
    from ..core.live import Track


# TODO: update, enable... ??
class XCsActions(XComponent):
    '''Actions related to control surfaces.
    '''
    __module__ = __name__

    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__(parent)    # type: ignore
        self._push_actions = XPushActions(parent)
        self._pxt_actions = XPxtActions(parent)
        self._mxt_actions = XMxtActions(parent)
        self._arsenal_actions = XArsenalActions(parent)
        self._scripts = dict()  # type: Dict[Any, Any]

    def disconnect(self):
        for attr in ('_scripts', '_arsenal_actions', '_push_actions',
                     '_pxt_actions', '_mxt_actions'):
            setattr(self, attr, None)
        super().disconnect()

    def connect_script_instances(self, instantiated_scripts):
        '''Build dict of connected scripts and their components, doesn't
        work with non-Framework scripts, but does work with User Remote
        Scripts.
        '''
        # TODO: arg substituted ??
        instantiated_scripts = self._parent._control_surfaces()

        # TODO: replace with enumerate
        self._scripts = dict()
        for i in range(len(instantiated_scripts)):
            script = instantiated_scripts[i]
            self._scripts[i] = dict(
                script        = script,
                name          = None,
                repeat        = False,
                mixer         = None,
                device        = None,
                last_ring_pos = None,
                session       = None,
                track_link    = False,
                scene_link    = False,
                centered_link = False,
                color         = False,
            )
            script_name = script.__class__.__name__
            if isinstance(script, (ControlSurface, CS)):
                if script_name == 'GenericScript':
                    script_name = script._suggested_input_port
                if script_name.startswith('Arsenal'):
                    self._arsenal_actions.set_script(script)
                if script_name == 'Push':
                    self._push_actions.set_script(script)
                if script_name.startswith('PXT_Live'):
                    self._pxt_actions.set_script(script)
                if script_name == 'MXT_Live':
                    self._mxt_actions.set_script(script)
                if not script_name.startswith('ClyphX'):
                    if script._components is not None:
                        self._scripts[i]['name'] = script_name.upper()
                        for c in script.components:
                            if isinstance(c, SessionComponent):
                                self._scripts[i]['session'] = c
                                if script_name.startswith('APC'):
                                    self._scripts[i]['color'] = dict(
                                        GREEN = (1, 2),
                                        RED   = (3, 4),
                                        AMBER = (5, 6),
                                    )
                                    self._scripts[i]['metro'] = dict(
                                        controls  = c._stop_track_clip_buttons,
                                        component = None,
                                        override  = None,
                                    )
                                elif script_name == 'Launchpad':
                                    self._scripts[i]['color'] = dict(
                                        GREEN = (52, 56),
                                        RED   = (7, 11),
                                        AMBER = (55, 59),
                                    )
                                    self._scripts[i]['metro'] = dict(
                                        controls  = script._selector._side_buttons,
                                        component = None,
                                        override  = script._selector,
                                    )
                            if isinstance(c, MixerComponent):
                                self._scripts[i]['mixer'] = c
                            if isinstance(c, DeviceComponent):
                                self._scripts[i]['device'] = c
                        if script_name == 'Push':
                            self._scripts[i]['session'] = script._session_ring
                            self._scripts[i]['mixer']   = script._mixer
                            self._scripts[i]['device']  = script._device_component
                        elif script_name == 'Push2':
                            # XXX: hackish way to delay for Push2 init, using
                            # monkey patching doesn't work for some reason
                            self.canonical_parent.schedule_message(
                                50, partial(self._handle_push2_init, i)
                            )
            elif script_name == 'Nocturn':
                self._scripts[i]['device'] = script.device_controller
                script.device_controller.canonical_parent = script

    def _handle_push2_init(self, index):
        script = self._scripts[index]['script']
        self._push_actions.set_script(script, is_push2=True)
        self._scripts[index]['session'] = script._session_ring
        self._scripts[index]['device'] = script._device_component

    @property
    def dispatchers(self):
        return dict(
            SURFACE = self.dispatch_cs_action,
            CS      = self.dispatch_cs_action,
            ARSENAL = self.dispatch_arsenal_action,
            PUSH    = self.dispatch_push_action,
            PTX     = self.dispatch_pxt_action,
            MTX     = self.dispatch_mxt_action,
        )

    # TODO: normalize dispatching
    def dispatch_action(self, cmd):
        # type: (_SingleDispatch) -> None
        '''Dispatch appropriate control surface actions.
        '''
        if cmd.action_name.startswith(('SURFACE', 'CS')):
            script = self._get_script_to_operate_on(cmd.action_name)
            if script is not None:
                self.dispatch_cs_action(script, cmd.xclip, cmd.ident, cmd.args)
        else:
            disp = [v for k,v in self.dispatchers.items()
                   if k.startswith(cmd.action_name)][0]
            disp(cmd.track, cmd.xclip, cmd.ident, cmd.action_name, cmd.args)

    def dispatch_cs_action(self, script, xclip, ident, args):
        # type: (Any, Clip, Text, Text) -> None
        '''Dispatch appropriate control surface actions.'''
        _script = self._scripts[script]

        if 'METRO ' in args and 'metro' in _script:
            self.handle_visual_metro(_script, args)
        elif 'RINGLINK ' in args and _script['session']:
            self.handle_ring_link(_script['session'], script, args[9:])
        elif 'RING ' in args and _script['session']:
            self.handle_session_offset(script, _script['session'], args[5:])
        elif ('COLORS ' in args and _script['session'] and _script['color']):
            self.handle_session_colors(_script['session'], _script['color'], args[7:])
        elif 'DEV LOCK' in args and _script['device']:
            _script['device'].canonical_parent.toggle_lock()
        elif 'BANK ' in args and _script['mixer']:
            self.handle_track_bank(
                script, xclip, ident, _script['mixer'], _script['session'], args[5:])
        elif 'RPT' in args:
            self.handle_note_repeat(_script['script'], script, args)
        elif _script['mixer'] and '/' in args[:4]:
            self.handle_track_action(script, _script['mixer'], xclip, ident, args)

    def dispatch_push_action(self, track, xclip, ident, action, args):
        # type: (Track, Clip, Text, None, Text) -> None
        '''Dispatch Push-related actions to PushActions.'''
        if self._push_actions:
            self._push_actions.dispatch_action(track, xclip, ident, None, args)

    def dispatch_pxt_action(self, track, xclip, ident, action, args):
        # type: (Track, Clip, Text, Text, Text) -> None
        '''Dispatch PXT-related actions to PXTActions.'''
        if self._pxt_actions:
            self._pxt_actions.dispatch_action(track, xclip, ident, action, args)

    def dispatch_mxt_action(self, track, xclip, ident, action, args):
        # type: (Track, Clip, Text, Text, Text) -> None
        '''Dispatch MXT-related actions to MXTActions.'''
        if self._mxt_actions:
            self._mxt_actions.dispatch_action(track, xclip, ident, action, args)

    def dispatch_arsenal_action(self, track, xclip, ident, action, args):
        # type: (Track, Clip, Text, Text, Text) -> None
        '''Dispatch Arsenal-related actions to ArsenalActions.'''
        if self._arsenal_actions:
            self._arsenal_actions.dispatch_action(track, xclip, ident, action, args)

    def _get_script_to_operate_on(self, script_info):
        # type: (Text) -> Optional[Any]
        '''Returns the script index to operate on, which can be
        specified in terms of its index or its name. Also, can use
        SURFACE (legacy) or CS (new) to indicate a surface action.
        '''
        script = None
        try:
            if 'SURFACE' in script_info:
                script_spec = script_info.replace('SURFACE', '').strip()
            elif 'CS' in script_info:
                script_spec = script_info.replace('CS', '').strip()
            else:
                return None

            if len(script_spec) == 1:
                script = int(script_spec) - 1
                if script not in self._scripts:
                    script = None
            else:
                script_spec = script_spec.strip('"').strip()
                for k, v in self._scripts.items():
                    if v['name'] == script_spec:
                        script = k
                        break
        except Exception:
            script = None
        return script

    def handle_note_repeat(self, script, script_index, args):
        # type: (Any, int, Text) -> None
        '''Set note repeat for the given surface.'''
        args = args.replace('RPT', '').strip()
        if args == 'OFF':
            script._c_instance.note_repeat.enabled = False
            self._scripts[script_index]['repeat'] = False
        else:
            try:
                script._c_instance.note_repeat.repeat_rate = REPEAT_STATES[args]
            except KeyError:
                self._scripts[script_index]['repeat'] = not self._scripts[script_index]['repeat']
                script._c_instance.note_repeat.enabled = self._scripts[script_index]['repeat']
            else:
                script._c_instance.note_repeat.enabled = True
                self._scripts[script_index]['repeat'] = True

    def handle_track_action(self, script_key, mixer, xclip, ident, args):
        # type: (Text, Any, Clip, Text, Text) -> None
        '''Get control surface track(s) to operate on and call main
        action dispatch.
        '''
        track_range = args.split('/')[0]
        actions = str(args[args.index('/')+1:].strip()).split()
        new_action = actions[0]
        new_args = ''
        if len(actions) > 1:
            new_args = ' '.join(actions[1:])

        try:
            if 'ALL' in track_range:
                track_start = 0
                track_end = len(mixer._channel_strips)
            elif '-' in track_range:
                start, end = track_range.split('-')
                track_start = int(start) - 1
                track_end = int(end)
            else:
                track_start = int(track_range) - 1
                track_end = track_start + 1
        except Exception:
            return

        if (0 <= track_start and track_start < track_end and
                track_end < len(mixer._channel_strips) + 1):
            track_list = []
            _script = self._scripts[script_key]
            if _script['name'] == 'PUSH':
                offset, _ = self._push_actions.get_session_offsets(_script['session'])
                tracks_to_use = _script['session'].tracks_to_use()
            else:
                offset = mixer._track_offset
                tracks_to_use = mixer.tracks_to_use()
            for i in range(track_start, track_end):
                if 0 <= (i + offset) < len(tracks_to_use):
                    track_list.append(tracks_to_use[i + offset])
            if track_list:
                command = _DispatchCommand(track_list, xclip, ident, new_action, new_args)
                self._parent.handle_dispatch_command(command)
                # self._parent.action_dispatch(track_list, xclip, new_action, new_args, ident)

    def handle_track_bank(self, script_key, xclip, ident, mixer, session, args):
        # type: (Text, Clip, Text, Any, Any, Text) -> None
        '''Move track (or session) bank and select first track in bank.

        This works even with controllers without banks like
        User Remote Scripts.
        '''
        if self._scripts[script_key]['name'] == 'PUSH':
            t_offset, s_offset = self._push_actions.get_session_offsets(session)
            tracks = session.tracks_to_use()
        else:
            t_offset, s_offset = mixer._track_offset, session._scene_offset if session else None
            tracks = mixer.tracks_to_use()

        if args == 'FIRST':
            new_offset = 0
        elif args == 'LAST':
            new_offset = len(tracks) - len(mixer._channel_strips)
        else:
            try:
                offset = int(args)
                if 0 <= (offset + t_offset) < len(tracks):
                    new_offset = offset + t_offset
            except Exception:
                return

        if new_offset >= 0:
            if session:
                session.set_offsets(new_offset, s_offset)
            else:
                mixer.set_track_offset(new_offset)
                self.handle_track_action(script_key, mixer, xclip, ident, '1/SEL')

    def handle_session_offset(self, script_key, session, args):
        # type: (Text, Any, Text) -> None
        '''Handle moving session offset absolutely or relatively as well
        as storing/recalling its last position.
        '''
        if self._scripts[script_key]['name'] in ('PUSH', 'PUSH2'):
            last_pos = self._push_actions.handle_session_offset(
                session, self._scripts[script_key]['last_ring_pos'], args, self._parse_ring_spec
            )
            self._scripts[script_key]['last_ring_pos'] = last_pos or None
            return
        try:
            new_track = session._track_offset
            new_scene = session._scene_offset
            if args.strip() == 'LAST':
                last_pos = self._scripts[script_key]['last_ring_pos']
                if last_pos:
                    session.set_offsets(last_pos[0], last_pos[1])
                return
            else:
                self._scripts[script_key]['last_ring_pos'] = (new_track, new_scene)
            new_track, args = self._parse_ring_spec('T', args, new_track, self.song().tracks)
            new_scene, args = self._parse_ring_spec('S', args, new_scene, self.song().scenes)
            if new_track == -1 or new_scene == -1:
                return
            session.set_offsets(new_track, new_scene)
        except Exception:
            pass

    def _parse_ring_spec(self, spec_id, arg_string, default_index, list_to_search):
        # type: (Text, Text, int, Iterable[Any]) -> Tuple[int, Text]
        '''Parses a ring action specification and returns the specified
        track/scene index as well as the arg_string without the
        specification that was parsed.
        '''
        index = default_index
        for a in arg_string.split():
            if a.startswith(spec_id):
                if a[1].isdigit():
                    index = int(a.strip(spec_id)) - 1
                    arg_string = arg_string.replace(a, '', 1).strip()
                    break
                elif a[1] in ('<', '>'):
                    index += self.get_adjustment_factor(a.strip(spec_id))
                    arg_string = arg_string.replace(a, '', 1).strip()
                    break
                elif a[1] == '"':
                    name_start_pos = arg_string.index('{}"'.format(spec_id))
                    name = arg_string[name_start_pos + 2:]
                    name_end_pos = name.index('"')
                    name = name[:name_end_pos]
                    for i, item in enumerate(list_to_search):
                        if name == item.name.upper():
                            index = i
                            break
                    arg_string = arg_string.replace('{}"{}"'.format(spec_id, name), '', 1).strip()
                    break
        return (index, arg_string)

    def handle_ring_link(self, session, script_index, args):
        # type: (Any, Text, Text) -> None
        '''Handles linking/unliking session offsets to the selected
        track or scene with centering if specified.
        '''
        script = self._scripts[script_index]
        script['track_link'] = args == 'T' or 'T ' in args or ' T' in args
        script['scene_link'] = 'S' in args
        script['centered_link'] = 'CENTER' in args

    def handle_session_colors(self, session, colors, args):
        # type: (Any, Any, Text) -> None
        '''Handle changing clip launch LED colors.'''
        largs = args.split()
        if len(largs) == 3:
            for a in largs:
                if a not in colors:
                    return
            for scene_index in range(session.height()):
                scene = session.scene(scene_index)
                for track_index in range(session.width()):
                    clip_slot = scene.clip_slot(track_index)
                    clip_slot.set_started_value(colors[largs[0]][0])
                    clip_slot.set_triggered_to_play_value(colors[largs[0]][1])
                    clip_slot.set_recording_value(colors[largs[1]][0])
                    clip_slot.set_triggered_to_record_value(colors[largs[1]][1])
                    clip_slot.set_stopped_value(colors[largs[2]][0])
                    clip_slot.update()

    def handle_visual_metro(self, script, args):
        # type: (Any, Text) -> None
        '''Handle visual metro for APCs and Launchpad.

        This is a specialized version for L9 that uses component guard
        to avoid dependency issues.
        '''
        metro = script['metro']
        if 'ON' in args and not metro['component']:
            with self._parent.component_guard():
                m = VisualMetro(self._parent, metro['controls'], metro['override'])
                metro['component'] = m
        elif 'OFF' in args and metro['component']:
            metro['component'].disconnect()
            metro['component'] = None

    def on_selected_track_changed(self):
        '''Moves the track offset of all track linked surfaces to the
        selected track with centering if specified.
        '''
        trk = self.sel_track
        if trk in self.song().tracks:
            trk_id = list(self.song().visible_tracks).index(trk)
            for k, v in self._scripts.items():
                if v['track_link']:
                    new_trk_id = trk_id
                    try:
                        session = self._scripts[k]['session']
                        if v['name'] in ('PUSH', 'PUSH2'):
                            width = self._push_actions.get_session_dimensions(session)[0]
                            t_offset, s_offset = self._push_actions.get_session_offsets(session)
                        else:
                            width = session.width()
                            t_offset, s_offset = session._track_offset, session._scene_offset
                        if self._scripts[k]['centered_link']:
                            mid_point = width / 2
                            if new_trk_id < mid_point:
                                if t_offset <= new_trk_id:
                                    return
                                else:
                                    new_trk_id = 0
                            else:
                                centered_id = new_trk_id - mid_point
                                if 0 <= centered_id < len(self.song().visible_tracks):
                                    new_trk_id = centered_id
                        session.set_offsets(new_trk_id, s_offset)
                    except Exception:
                        pass

    def on_selected_scene_changed(self):
        '''Moves the scene offset of all scene linked surfaces to the
        selected scene with centering if specified.
        '''
        scn_id = self.sel_scene
        for k, v in self._scripts.items():
            if v['scene_link']:
                new_scn_id = scn_id
                try:
                    session = self._scripts[k]['session']
                    if v['name'] in ('PUSH', 'PUSH2'):
                        height = self._push_actions.get_session_dimensions(session)[1]
                        t_offset, s_offset = self._push_actions.get_session_offsets(session)
                    else:
                        height = session.height()
                        t_offset, s_offset = session._track_offset, session._scene_offset

                    if self._scripts[k]['centered_link']:
                        mid_point = height / 2
                        if new_scn_id < mid_point:
                            if s_offset <= new_scn_id:
                                return
                            else:
                                new_scn_id = 0
                        else:
                            centered_id = new_scn_id - mid_point
                            if 0 <= centered_id < len(self.song().scenes):
                                new_scn_id = centered_id
                    session.set_offsets(t_offset, new_scn_id)
                except Exception:
                    pass


class VisualMetro(XComponent):
    '''Visual metro for APCs and Launchpad.
    '''
    __module__ = __name__

    def __init__(self, parent, controls, override):
        # type: (Any, Sequence[Any], Any) -> None
        super().__init__(parent)
        self._controls = controls
        self._override = override
        self._last_beat = -1
        self.song().add_current_song_time_listener(self.on_time_changed)
        self.song().add_is_playing_listener(self.on_time_changed)

    def disconnect(self):
        if self._controls:
            self.clear()
        self._controls = None
        self.song().remove_current_song_time_listener(self.on_time_changed)
        self.song().remove_is_playing_listener(self.on_time_changed)
        self._override = None
        super().disconnect()

    def on_time_changed(self):
        '''Show visual metronome via control LEDs upon beat changes
        (will not be shown if in Launchpad User 1).
        '''
        if self.song().is_playing and (not self._override or
            (self._override and self._override._mode_index != 1)
        ):
            time = str(self.song().get_current_beats_song_time()).split('.')
            if self._last_beat != int(time[1]) - 1:
                self._last_beat = int(time[1]) - 1
                self.clear()
                if self._last_beat < len(self._controls):
                    self._controls[self._last_beat].turn_on()
                else:
                    self._controls[len(self._controls) - 1].turn_on()
        else:
            self.clear()

    def clear(self):
        '''Clear all control LEDs.'''
        for c in self._controls:
            c.turn_off()
