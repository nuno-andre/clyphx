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
from builtins import super, dict

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import (
        Any, Optional, Text, Dict, Sequence, List,
    )

import logging
from ..core.xcomponent import ControlSurfaceComponent
from ..core.live import Clip

try:
    from _NKFW2.Utils import parse_int
    from _NKFW2.consts import NOTE_NAMES
    from _NKFW2.Scales import SCALE_TYPES
    from _NKFW2.ScaleSettingsComponent import SEQ_OFFSET, FOURTHS_OFFSET, OFFSET_NAMES
    S_TYPES = [s.name.upper() for s in SCALE_TYPES]  # type: List[Text]
    O_NAMES = [o.upper() for o in OFFSET_NAMES]  # type: List[Text]
except:
    pass

log = logging.getLogger(__name__)


def adjust_property(obj, prop, min_v, max_v, arg, setter=None, v_list=None):
    # type: (Any, Any, Any, Any, Text, Optional[Any], Optional[Any]) -> None
    '''Adjusts the given property absolutely or relatively.'''
    if arg:
        arg = arg[0].strip()
        current_v = getattr(obj, prop)
        new_v = current_v
        # get absolute value
        if arg.isdigit():
            new_v = parse_int(arg, current_v + 1, min_v + 1, max_v + 1) - 1
        # get relative value with wrapping
        elif arg == '>':
            new_v = current_v + 1
            if new_v > max_v:
                new_v = min_v
        elif arg == '<':
            new_v = current_v - 1
            if new_v < min_v:
                new_v = max_v
        # get index of arg from v_list
        elif v_list and arg in v_list:
            new_v = v_list.index(arg)
        if setter:
            getattr(obj, setter)(new_v)
        else:
            setattr(obj, prop, new_v)


def toggle_property(obj, prop, arg):
    # type: (object, Text, Any) -> None
    '''Toggles the given property or turns it off/on.'''
    value = arg[0].strip() == 'ON' if arg else not getattr(obj, prop)
    setattr(obj, prop, value)


def get_component(script, comp_name):
    # type: (Any, Text) -> Optional[Any]
    '''Returns the component of the given name.'''
    for c in script._components:
        if c.name == comp_name:
            return c
    return None


# TODO: update...
class XArsenalActions(ControlSurfaceComponent):
    '''Actions related to Arsenal control surface scripts.'''

    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__()
        self._parent = parent
        self._scripts = dict()  # type: Dict[Text, Any]

    def disconnect(self):
        super().disconnect()
        self._parent = None
        self._scripts = None

    def set_script(self, script):
        # type: (Any) -> None
        ''' Adds the given script to the dict of scripts to work with.
        '''
        self._scripts[script.script_name.upper()] = dict(
            top     = script,
            scl     = get_component(script, 'Scale_Settings_Control'),
            targets = get_component(script, 'Targets_Component'),
        )

    def dispatch_action(self, track, xclip, ident, script_name, action):
        # type: (None, Clip, Text, Text, Any) -> None
        '''Dispatches the action to the appropriate handler.'''
        script = self._scripts.get(script_name, None)
        if script:
            action_spec = action.split()
            if action_spec:
                action_name = action_spec[0].strip()
                with script['top'].component_guard():
                    if '_MODE' in action_name:
                        self._handle_mode_action(script, action_spec)
                    elif 'LOCK' in action_name:
                        self._handle_lock_action(script, action_spec)
                    elif 'SCL' in action_name:
                        self._handle_scale_action(script, action_spec, xclip, ident)

    def _handle_mode_action(self, script, spec):
        # type: (Any, Text) -> None
        '''Handles selecting a specific mode or incrementing modes with
        wrapping.
        '''
        mc = (script['top'].matrix_modes_component if spec[0].startswith('M_MODE')
                     else script['top'].encoder_modes_component)
        if mc:
            adjust_property(mc, 'selected_mode_index', 0, mc.num_modes - 1, spec[1:])

    def _handle_lock_action(self, script, spec):
        # type: (Any, Text) -> None
        '''Handles toggling the locking of the current track or
        mode-specific locks.
        '''
        tc = script['targets']
        if tc:
            if 'MODES' in spec:
                tc.toggle_mode_specific_lock()
            else:
                tc.toggle_lock()

    def _handle_scale_action(self, script, spec, xclip, ident):
        # type: (Any, Any, Clip, Text) -> None
        '''Handles scale actions or dispatches them to the appropriate
        handler.
        '''
        if script['scl']:
            scl = script['scl']
            if len(spec) == 1:
                self._capture_scale_settings(script, xclip, ident)
                return
            elif len(spec) >= 5:
                self._recall_scale_settings(scl, spec)
            else:
                prop, value = spec[1], spec[2:]
                if prop == 'INKEY':
                    toggle_property(scl, '_in_key', value)
                elif prop == 'HORZ':
                    toggle_property(scl, '_orientation_is_horizontal', value)
                elif prop == 'ROOT':
                    adjust_property(scl._tonics, '_page_index', 0,
                                    scl._tonics.num_pages - 1, value,
                                    'set_page_index', NOTE_NAMES)
                elif prop == 'TYPE':
                    adjust_property(scl._scales, '_page_index', 0,
                                    scl._scales.num_pages - 1, [' '.join(value)],
                                    'set_page_index', S_TYPES)
                elif prop == 'OFFSET':
                    adjust_property(scl._offsets, '_page_index', 0,
                                    scl._offsets.num_pages - 1, value,
                                    'set_page_index', O_NAMES)
                elif prop == 'SEQ':
                    log.warning('SEQ is deprecated')
                    self._toggle_scale_offset(scl, value)
            scl._notify_scale_settings()

    def _capture_scale_settings(self, script, xclip, ident):
        # type: (Any, Clip, Text) -> None
        '''Captures the current scale type, tonic, in key state, offset
        and orientation and adds them to the given xclip's name.
        '''
        if isinstance(xclip, Clip):
            comp = script['scl']
            xclip.name = '{} {} SCL {} {} {} {} {}'.format(
                ident, script['top'].script_name, comp._scales.page_index,
                comp.tonic, comp.in_key, comp._offsets.page_index,
                comp.orientation_is_horizontal,
            )

    def _recall_scale_settings(self, comp, spec):
        # type: (Any, Text) -> None
        '''Recalls previously stored scale settings.'''
        if len(spec) >= 5:
            scale = parse_int(spec[1], None, 0, comp._scales.num_pages - 1)
            if scale is not None:
                comp._scales.set_page_index(scale)
            tonic = parse_int(spec[2], None, 0, comp._tonics.num_pages - 1)
            if tonic is not None:
                comp._tonics.set_page_index(tonic)
            comp._in_key = spec[3].strip() == 'TRUE'
            # deprecated
            if len(spec) == 5:
                value = ['ON'] if spec[4].strip() == 'TRUE' else ['OFF']
                self._toggle_scale_offset(comp, value)
            else:
                offset = parse_int(spec[4], None, 0, comp._offsets.num_pages - 1)
                if offset is not None:
                    comp._offsets.set_page_index(offset)
                comp._orientation_is_horizontal = spec[5].strip() == 'TRUE'

    def _toggle_scale_offset(self, comp, arg):
        # type: (Any, Sequence[Text]) -> None
        '''Toggles between sequent and 4ths offsets.

        This is deprecated, but maintained for backwards compatibility.
        '''
        offset = FOURTHS_OFFSET
        if (arg and arg[0].strip() == 'ON') or (not arg and comp._offsets.page_index):
            offset = SEQ_OFFSET
        comp._offsets.page_index = offset
