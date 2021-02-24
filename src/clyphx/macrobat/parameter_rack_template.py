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

if TYPE_CHECKING:
    from typing import Callable, Dict, List, Any, Text
    from ..core.live import DeviceParameter, RackDevice, Track

from ..core.xcomponent import XComponent


class MacrobatParameterRackTemplate(XComponent):
    '''Template for Macrobat racks that control parameters.
    '''
    __module__ = __name__

    def __init__(self, parent, rack, track):
        # type: (Any, RackDevice, Track) -> None
        super().__init__(parent)
        self._on_off_param = list()  # type: List[Any]
        self._param_macros = dict()  # type: Dict[int, DeviceParameter]
        self._update_macro = 0
        self._update_param = 0
        self._track = track
        self.setup_device(rack)

    def disconnect(self):
        self.remove_macro_listeners()
        self._on_off_param = list()
        self._param_macros = dict()
        self._track = None
        super().disconnect()

    def setup_device(self, rack):
        # type: (RackDevice) -> None
        '''Remove any current listeners and set up listener for on/off
        (used for resetting assigned params).
        '''
        self.remove_macro_listeners()
        if not rack.parameters[0].value_has_listener(self.on_off_changed):
            self._on_off_param = [rack.parameters[0], rack.parameters[0].value]
            rack.parameters[0].add_value_listener(self.on_off_changed)

    def scale_macro_value_to_param(self, macro, param):
        # type: (DeviceParameter, DeviceParameter) -> float
        return (((param.max - param.min) / 127.0) * macro.value) + param.min

    def scale_param_value_to_macro(self, param):
        # type: (DeviceParameter) -> int
        return int(((param.value - param.min) / (param.max - param.min)) * 127.0)

    def get_initial_value(self, arg=None):
        # type: (None) -> None
        '''Get initial values to set macros to.'''
        for i in range(1, 9):
            try:
                # TODO: indexed dict?
                param = self._param_macros[i]
            except KeyError:
                pass
            else:
                if param[0] and param[1]:
                    value = self.scale_param_value_to_macro(param[1])
                    if param[0].value != value:
                        param[0].value = value

    def get_drum_rack(self):
        '''For use with DR racks, get drum rack to operate on as well as
        the params of any simplers/samplers in the rack.
        '''
        drum_rack = dict(devs_by_index=dict(), devs_by_name=dict())  # type: Dict[Text, Dict]

        if self._track and self._track.devices:
            for d in self._track.devices:
                if d.class_name == 'DrumGroupDevice':
                    drum_rack['rack'] = d
                    by_index = drum_rack['devs_by_index']
                    by_name = drum_rack['devs_by_name']
                    for i, chain in enumerate(d.chains):
                        for device in chain.devices:
                            if device.class_name in ('OriginalSimpler', 'MultiSampler'):
                                params = dict((str(p.name).upper(), p) for p in device.params)
                                by_index[str(i + 1)] = params
                                by_name[str(device.name)] = params
                            break
                    break
        return drum_rack

    def on_off_changed(self):
        '''On/off changed, schedule param reset.'''
        if self._on_off_param and self._on_off_param[0]:
            if (self._on_off_param[0].value != self._on_off_param[1]
                    and self._on_off_param[0].value == 1.0):
                self._parent.schedule_message(1, self.do_reset)
            self._on_off_param[1] = self._on_off_param[0].value

    def set_param_macro_listeners(self, macro, param, index):
        # type: (DeviceParameter, DeviceParameter, int) -> None
        macro.add_value_listener(lambda i=index: self.macro_changed(i))
        param.add_value_listener(lambda i=index: self.param_changed(i))
        self._param_macros[index] = (macro, param)

    def remove_macro_listeners(self):
        for i in range(1, 9):
            try:
                macro = self._param_macros[i]
            except KeyError:
                pass
            else:
                m_listener = lambda index=i: self.macro_changed(index)  # type: Callable[[int], None]
                p_listener = lambda index=i: self.param_changed(index)  # type: Callable[[int], None]
                if macro[0] and macro[0].value_has_listener(m_listener):
                    macro[0].remove_value_listener(m_listener)
                if macro[1] and macro[1].value_has_listener(p_listener):
                    macro[1].remove_value_listener(p_listener)
        self._param_macros = dict()
        if (self._on_off_param and
                self._on_off_param[0] and
                self._on_off_param[0].value_has_listener(self.on_off_changed)):
            self._on_off_param[0].remove_value_listener(self.on_off_changed)
        self._on_off_param = []

    def macro_changed(self, index):
        # type: (int) -> None
        '''Called on macro changes to update param values.'''
        if index in self._param_macros and self._param_macros[index][0] and self._param_macros[index][1]:
            scaled_value = self.scale_param_value_to_macro(self._param_macros[index][1])
            if scaled_value != self._param_macros[index][0].value:
                self._update_param = index
                self._tasks.kill()
                self._tasks.clear()
                self._tasks.add(self.update_param)

    def update_macro(self, arg=None):
        # type: (None) -> None
        '''Update macro to match value of param.'''
        macro = self._param_macros.get(self._update_macro)
        if macro:
            if macro[0] and macro[1]:
                macro[0].value = self.scale_param_value_to_macro(macro[1])
        self._tasks.kill()
        self._tasks.clear()

    def param_changed(self, index):
        # type: (int) -> None
        '''Called on param changes to update macros.'''
        if index in self._param_macros and self._param_macros[index][0] and self._param_macros[index][1]:
            scaled_value = self.scale_macro_value_to_param(self._param_macros[index][0],
                                                           self._param_macros[index][1])
            if scaled_value != self._param_macros[index][1].value:
                self._update_macro = index
                self._tasks.kill()
                self._tasks.clear()
                self._tasks.add(self.update_macro)

    def update_param(self, arg=None):
        # type: (None) -> None
        '''Update param to match value of macro.'''
        try:
            param = self._param_macros[self._update_param]
        except KeyError:
            pass
        else:
            if param[0] and param[1]:
                param[1].value = self.scale_macro_value_to_param(param[0], param[1])
        self._tasks.kill()
        self._tasks.clear()

    def do_reset(self):
        '''Reset assigned params to default.'''
        self._update_param = 0
        self._update_macro = 0
        self._tasks.kill()
        self._tasks.clear()
        for k, v in self._param_macros.items():
            if v[1] and not v[1].is_quantized and v[1].name != 'Chain Selector':
                v[1].value = v[1].default_value
                v[0].value = self.scale_param_value_to_macro(v[1])
