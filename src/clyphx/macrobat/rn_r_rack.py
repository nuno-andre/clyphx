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

import Live
from functools import partial
from ..core import XComponent


class MacrobatRnRRack(XComponent):
    '''Rack on/off to Device Randomize/Reset.
    '''
    __module__ = __name__

    def __init__(self, parent, rack, name, track):
        super(MacrobatRnRRack, self).__init__(parent)
        self._on_off_param = []
        self._devices_to_operate_on = []
        self._track = track
        self.setup_device(rack, name)

    def disconnect(self):
        self.remove_on_off_listeners()
        self._on_off_param = []
        self._devices_to_operate_on = []
        self._track = None
        super(MacrobatRnRRack, self).disconnect()

    def setup_device(self, rack, name):
        '''
        - Will not reset/randomize any other Macrobat racks except for MIDI Rack
        - Allowable rack names are: ['NK RST', 'NK RST ALL', 'NK RND', 'NK RND ALL']
        '''
        self.remove_on_off_listeners()
        if rack:
            for p in rack.parameters:
                if p.name == 'Device On' and p.is_enabled:
                    if not p.value_has_listener(self.on_off_changed):
                        self._on_off_param = [p, name]
                        #---use this to get around device on/off switches
                        #   getting turned on upon set load
                        self._parent.schedule_message(
                            5, partial(p.add_value_listener, self.on_off_changed)
                        )
                        break

    def on_off_changed(self):
        '''On/off changed, perform assigned function.'''
        if self._on_off_param and self._on_off_param[0]:
            mess_type = None
            is_reset = False
            if self._on_off_param[1].startswith('NK RND ALL'):
                mess_type = 'all'
            elif self._on_off_param[1].startswith('NK RND'):
                mess_type = 'next'
            elif self._on_off_param[1].startswith('NK RST ALL'):
                mess_type = 'all'
                is_reset = True
            elif self._on_off_param[1].startswith('NK RST'):
                mess_type = 'next'
                is_reset = True
            if mess_type:
                action = self.do_device_reset if is_reset else self.do_device_randomize
                self._parent.schedule_message(1, partial(action, mess_type))

    def do_device_randomize(self, params):
        '''Randomize device params.'''
        if self._on_off_param and self._on_off_param[0]:
            self._devices_to_operate_on = []
            self.get_devices_to_operate_on(
                self._on_off_param[0].canonical_parent.canonical_parent.devices, params
            )
            if self._devices_to_operate_on:
                for d in self._devices_to_operate_on:
                    for p in d.parameters:
                        if p.is_enabled and not p.is_quantized and p.name != 'Chain Selector':
                            p.value = (((p.max - p.min) / 127) * Live.Application.get_random_int(0, 128)) + p.min

    def do_device_reset(self, params):
        '''Reset device params.'''
        if self._on_off_param and self._on_off_param[0]:
            self._devices_to_operate_on = []
            self.get_devices_to_operate_on(
                self._on_off_param[0].canonical_parent.canonical_parent.devices, params
            )
            if self._devices_to_operate_on:
                for d in self._devices_to_operate_on:
                    for p in d.parameters:
                        if p and p.is_enabled and not p.is_quantized and p.name != 'Chain Selector':
                            p.value = p.default_value

    def get_devices_to_operate_on(self, dev_list, devices_to_get):
        '''Get next device on track, all devices on track or all devices
        on chain.
        '''
        if devices_to_get == 'all':
            if (self._parent._can_have_nested_devices and
                isinstance(self._on_off_param[0].canonical_parent.canonical_parent, Live.Chain.Chain)
            ):
                dev_list = self._on_off_param[0].canonical_parent.canonical_parent.devices
            for d in dev_list:
                name = self._parent.get_name(d.name)
                if d and not name.startswith(
                    ('NK RND', 'NK RST', 'NK CHAIN MIX', 'NK DR',
                    'NK LEARN', 'NK RECEIVER', 'NK TRACK', 'NK SIDECHAIN')
                ):
                    self._devices_to_operate_on.append(d)
                    if self._parent._can_have_nested_devices and d.can_have_chains:
                        for c in d.chains:
                            self.get_devices_to_operate_on(c.devices, 'all')
        else:
            self.get_next_device(self._on_off_param[0].canonical_parent, dev_list)

    def get_next_device(self, rnr_rack, dev_list, store_next = False):
        '''Get the next non-RnR device on the track or in the chain.'''
        for d in dev_list:
            if d and not store_next:
                if d == rnr_rack:
                    store_next = True
            elif d and store_next:
                if not self._devices_to_operate_on or (
                    self._parent._can_have_nested_devices and
                    isinstance(d.canonical_parent, Live.Chain.Chain)
                ):
                    name = self._parent.get_name(d.name)
                    if d and not name.startswith(
                        ('NK RND', 'NK RST', 'NK CHAIN MIX', 'NK DR',
                        'NK LEARN', 'NK RECEIVER', 'NK TRACK', 'NK SIDECHAIN')
                    ):
                        self._devices_to_operate_on.append(d)
                        if (self._parent._can_have_nested_devices and
                                isinstance(rnr_rack.canonical_parent, Live.Chain.Chain)):
                            return
                        if self._parent._can_have_nested_devices and d.can_have_chains:
                            for c in d.chains:
                                self.get_next_device(rnr_rack, c.devices, True)
                else:
                    return

    def remove_on_off_listeners(self):
        '''Remove listeners.'''
        if (self._on_off_param and
                self._on_off_param[0] and
                self._on_off_param[0].value_has_listener(self.on_off_changed)):
            self._on_off_param[0].remove_value_listener(self.on_off_changed)
        self._on_off_param = []
