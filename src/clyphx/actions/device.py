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
import logging

if TYPE_CHECKING:
    from typing import Any, Sequence, Optional, Text, List, Dict
    from ..core.live import Device, DeviceParameter, Track
    from ..core.legacy import _DispatchCommand, _SingleDispatch

from _Generic.Devices import (
    number_of_parameter_banks, get_parameter_by_name,
    DEVICE_DICT, DEVICE_BOB_DICT,
)
from ..core.xcomponent import XComponent
from ..core.live import Clip, get_random_int
from ..consts import switch
from .device_looper import LooperMixin

log = logging.getLogger(__name__)


class XDeviceActions(XComponent, LooperMixin):
    '''Device and Looper actions.
    '''
    __module__ = __name__

    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__(parent)
        self._parent = parent
        self._looper_data = dict()

    def disconnect(self):
        self._looper_data = dict()
        super().disconnect()

    def dispatch_device_actions(self, cmd):
        # type: (_DispatchCommand) -> None
        from .consts import DEVICE_ACTIONS

        for scmd in cmd:
            _args = scmd.track, scmd.action_name, scmd.args
            device_action = self._parent.get_device_to_operate_on(*_args)
            if device_action[0]:
                try:
                    device_args = device_action[1]
                except IndexError:
                    device_args = None

                if device_args and device_args.split()[0] in DEVICE_ACTIONS:
                    func = DEVICE_ACTIONS[device_args.split()[0]]
                    func(self, device_action[0], scmd.track, scmd.xclip, device_args)
                elif device_args and 'CHAIN' in device_args:
                    self.dispatch_chain_action(device_action[0], device_args)
                elif cmd.action_name.startswith('DEV'):
                    self.set_device_on_off(device_action[0], device_args)

    def select_device(self, device, track, xclip, args):
        # type: (Device, Track, None, None, None) -> None
        '''Select device and bring it and the track it's on into view.
        '''
        if self.song().view.selected_track != track:
            self.song().view.selected_track = track
        self.application().view.show_view('Detail')
        self.application().view.show_view('Detail/DeviceChain')
        self.song().view.select_device(device)

    def set_all_params(self, device, track, xclip, args):
        # type: (Device, None, Clip, Text) -> None
        '''Set the value of all macros in a rack in one go. So don't
        need to use a whole string of DEV Px actions to do this. Can
        also capture the values of macros and store them in X-Clip name
        if no values specified.
        '''
        if device.class_name.endswith('GroupDevice'):
            args = args.replace('SET', '', 1).strip()
            if args:
                param_values = args.split()
                if len(param_values) == 8:
                    for i in range(8):
                        self._parent.do_parameter_adjustment(
                            device.parameters[i + 1],
                            param_values[i].strip()
                        )
            elif isinstance(xclip, Clip):
                assign_string = '{} '.format(xclip.name)
                for param in device.parameters:
                    if 'Macro' in param.original_name:
                        assign_string += '{} '.format(int(param.value))
                xclip.name = assign_string

    def adjust_selected_chain(self, device, track, xclip, args):
        # type: (Device, None, None, Text) -> None
        '''Adjust the selected chain in a rack.'''
        if device.can_have_chains and device.chains:
            args = args.replace('CSEL', '', 1).strip()
            if args in ('<', '>'):
                factor = self._parent.get_adjustment_factor(args)
                new_index = list(device.chains).index(device.view.selected_chain) + factor
            else:
                try:
                    new_index = int(args) - 1
                except:
                    new_index = list(device.chains).index(device.view.selected_chain)
            if 0 <= new_index < len(device.chains):
                device.view.selected_chain = device.chains[new_index]

    def adjust_bob_param(self, device, track, xclip, args):
        # type: (Device, None, None, Text) -> None
        '''Adjust device best-of-bank parameter.'''
        param = None
        name_split = args.split()
        if len(name_split) > 1:
            param = self.get_bob_parameter(device, name_split[0])
            if param and param.is_enabled:
                self._parent.do_parameter_adjustment(param, name_split[-1])

    def adjust_banked_param(self, device, track, xclip, args):
        # type: (Device, None, None, Text) -> None
        '''Adjust device banked parameter.'''
        param = None
        name_split = args.split()
        if len(name_split) > 2:
            param = self.get_banked_parameter(device, name_split[0], name_split[1])
            if param and param.is_enabled:
                self._parent.do_parameter_adjustment(param, name_split[-1])

    def adjust_chain_selector(self, device, track, xclip, args):
        # type: (Device, None, None, Text) -> None
        '''Adjust device chain selector parameter.'''
        param = self.get_chain_selector(device)
        name_split = args.split()
        if param and param.is_enabled and len(name_split) > 1:
            self._parent.do_parameter_adjustment(param, name_split[-1])

    def randomize_params(self, device, track, xclip, args):
        # type: (Device, None, None, None) -> None
        '''Randomize device parameters.'''
        name = device.name.upper()
        if not name.startswith(
            ('NK RND', 'NK RST', 'NK CHAIN MIX', 'NK DR', 'NK LEARN',
            'NK RECEIVER', 'NK TRACK', 'NK SIDECHAIN')
        ):
            for p in device.parameters:
                if p and p.is_enabled and not p.is_quantized and p.name != 'Chain Selector':
                    p.value = (((p.max - p.min) / 127) * get_random_int(0, 128)) + p.min

    def reset_params(self, device, track, xclip, args):
        # type: (Device, None, None, None) -> None
        '''Reset device parameters.'''
        name = device.name.upper()
        if not name.startswith(
            ('NK RND', 'NK RST', 'NK CHAIN MIX', 'NK DR', 'NK LEARN',
            'NK RECEIVER', 'NK TRACK', 'NK SIDECHAIN')
        ):
            for p in device.parameters:
                if p and p.is_enabled and not p.is_quantized and p.name != 'Chain Selector':
                    p.value = p.default_value

    def set_device_on_off(self, device, value=None):
        # type: (Device, Optional[Text]) -> None
        '''Toggles or turns device on/off.'''
        for param in device.parameters:
            if str(param.name).startswith('Device On') and param.is_enabled:
                switch(param, 'value', value)
                # TODO: break?

    def get_chain_selector(self, device):
        # type: (Device) -> Optional[DeviceParameter]
        '''Get rack chain selector param.'''
        if device.class_name.endswith('GroupDevice'):
            for parameter in device.parameters:
                if str(parameter.original_name) == 'Chain Selector':
                    return parameter
        return None

    def get_bob_parameter(self, device, param_string):
        # type: (Device, Text) -> Optional[DeviceParameter]
        '''Get best-of-bank parameter 1-8 for Live's devices.

        The param string should be composed of 'P' followed by the param
        index (like P5).
        '''
        try:
            param_bank = DEVICE_BOB_DICT[device.class_name][0]
            param_num = int(param_string[1]) - 1
            if 0 <= param_num < 8:
                parameter = get_parameter_by_name(device, param_bank[param_num])
                if parameter:
                    return parameter
        except:
            return None

    def get_banked_parameter(self, device, bank_string, param_string):
        # type: (Device, Text, Text) -> Optional[DeviceParameter]
        '''Get bank 1-8/parameter 1-8 for Live's devices.

        :param bank_string: should be composed of 'B' followed by the
            bank index (like B2)
        :param param_string: should be composed of 'P' followed by the
            param index (like P5).
        '''
        try:
            device_bank = DEVICE_DICT[device.class_name]
            bank_num = int(bank_string[1]) - 1
            param_num = int(param_string[1]) - 1
            if 0 <= param_num < 8 and 0 <= bank_num < 8 <= number_of_parameter_banks(device):
                param_bank = device_bank[bank_num]
                parameter = get_parameter_by_name(device, param_bank[param_num])
                if parameter:
                    return parameter
        except:
            pass
        return None

# region CHAIN ACTIONS
    def dispatch_chain_action(self, device, args):
        # type: (Device, Text) -> None
        '''Handle actions related to device chains.'''
        if not (self._parent._can_have_nested_devices and device.can_have_chains and device.chains):
            raise TypeError('This device does not support chain actions.')

        arg_list = [x.strip() for x in args.upper().split()]
        try:
            chain_num, action, value = arg_list[0:3]

            chain = device.chains[int(chain_num.replace('CHAIN', '')) - 1]

            if action not in {'MUTE', 'SOLO', 'VOL', 'PAN'}:
                raise AttributeError('Invalid device chain action: {}'.format(action))
            elif action in {'VOL', 'PAN'} and device.class_name.startswith('Midi'):
                raise AttributeError('Invalid MIDI device chain action: {}'.format(action))
        except Exception as e:
            log.error("Failed to parse chain action args '%s': %r", arg_list, e)
            return

        chain = device.view.selected_chain
        if chain:
            func, param = dict(
                MUTE = (switch, chain.mute),
                SOLO = (switch, chain.solo),
                VOL  = (self._parent.do_parameter_adjustment, chain.mixer_device.volume),
                PAN  = (self._parent.do_parameter_adjustment, chain.mixer_device.panning),
            )
            func(param, value)

# endregion
