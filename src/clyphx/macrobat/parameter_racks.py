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

#---This module contains Learn, Chain Mix, DR, DR Multi, Receiver and Track Racks

from __future__ import absolute_import, unicode_literals

from functools import partial
from itertools import chain
from _Generic.Devices import *
from _Framework.SubjectSlot import Subject, SlotManager, subject_slot
from .parameter_rack_template import MacrobatParameterRackTemplate

LAST_PARAM = {}


class MacrobatLearnRack(MacrobatParameterRackTemplate):
    '''Macro 1 to learned param.
    '''
    __module__ = __name__

    def __init__(self, parent, rack, track):
        self._rack = rack
        #---delay adding listener to prevent issue with change on set load
        parent.schedule_message(
            8, partial(parent.song().view.add_selected_parameter_listener, self.on_selected_parameter_changed)
        )
        super(MacrobatLearnRack, self).__init__(parent, rack, track)

    def disconnect(self):
        if self.song().view.selected_parameter_has_listener(self.on_selected_parameter_changed):
            self.song().view.remove_selected_parameter_listener(self.on_selected_parameter_changed)
        self._rack = None
        super(MacrobatLearnRack, self).disconnect()

    def setup_device(self, rack):
        '''Set up macro 1 and learned param.'''
        super(MacrobatLearnRack, self).setup_device(rack)
        self._rack = rack
        param = self.song().view.selected_parameter
        if 0 in LAST_PARAM:
            param = LAST_PARAM[0]
        if self._rack and param:
            if self._rack.parameters[1].is_enabled and param.is_enabled:
                index = 1
                m_listener = lambda index = index:self.macro_changed(index)
                self._rack.parameters[1].add_value_listener(m_listener)
                p_listener = lambda index = index:self.param_changed(index)
                param.add_value_listener(p_listener)
                self._param_macros[index] = (self._rack.parameters[1], param)
            self._tasks.add(self.get_initial_value)

    def on_selected_parameter_changed(self):
        '''Update rack on new param selected.'''
        if (self.song().view.selected_parameter and
                self._rack and
                self.song().view.selected_parameter.canonical_parent != self._rack):
            LAST_PARAM[0] = self.song().view.selected_parameter
            self.setup_device(self._rack)


class MacrobatChainMixRack(MacrobatParameterRackTemplate):
    '''Macros to params of Rack chains.
    '''
    __module__ = __name__

    def __init__(self, parent, rack, track):
        self._rack = {}
        super(MacrobatChainMixRack, self).__init__(parent, rack, track)

    def disconnect(self):
        self._rack = None
        super(MacrobatChainMixRack, self).disconnect()

    def setup_device(self, rack):
        '''Set up macros and rack chain params.'''
        super(MacrobatChainMixRack, self).setup_device(rack)
        self._rack = self.get_rack()
        if self._rack:
            param_name = self._parent.get_name(rack.name[12:].strip())
            for i in range(1, 9):
                chain_to_edit = {}
                macro = rack.parameters[i]
                param = None
                if macro.is_enabled:
                    chain_name = self._parent.get_name(macro.name)
                    if chain_name in self._rack:
                        chain_to_edit = self._rack[chain_name]
                    if param_name in chain_to_edit:
                        param = chain_to_edit[param_name]
                    if param and param.is_enabled:
                        m_listener = lambda index=i: self.macro_changed(index)
                        macro.add_value_listener(m_listener)
                        p_listener = lambda index=i: self.param_changed(index)
                        param.add_value_listener(p_listener)
                        self._param_macros[i] = (macro, param)
            self._tasks.add(self.get_initial_value)

    def get_rack(self):
        '''Get rack to operate on as well as the mixer params of its
        chains.
        '''
        rack_chains = {}
        if self._track and self._track.devices:
            for d in self._track.devices:
                if d.class_name.endswith('GroupDevice') and not d.class_name.startswith('Midi'):
                    for chain_index in range(len(d.chains)):
                        c = d.chains[chain_index]
                        rack_chains[str(chain_index + 1)] = {
                            'VOL':  c.mixer_device.volume,
                            'PAN':  c.mixer_device.panning,
                            'MUTE': c.mixer_device.chain_activator,
                        }
                    break
        return rack_chains


class MacrobatDRMultiRack(MacrobatParameterRackTemplate):
    '''Macros to params of multiple Simplers/Samplers.
    '''
    __module__ = __name__

    def __init__(self, parent, rack, track):
        self._drum_rack = {}
        super(MacrobatDRMultiRack, self).__init__(parent, rack, track)

    def disconnect(self):
        self._drum_rack = None
        super(MacrobatDRMultiRack, self).disconnect()

    def setup_device(self, rack):
        '''Set up macros and drum rack params.'''
        super(MacrobatDRMultiRack, self).setup_device(rack)
        self._drum_rack = self.get_drum_rack()
        if self._drum_rack:
            param_name = self._parent.get_name(rack.name[11:].strip())
            for i in range(1, 9):
                drum_to_edit = {}
                macro = rack.parameters[i]
                param = None
                if macro.is_enabled:
                    drum_name = macro.name
                    if drum_name in self._drum_rack['devs_by_index']:
                        drum_to_edit = self._drum_rack['devs_by_index'][drum_name]
                    elif drum_name in self._drum_rack['devs_by_name']:
                        drum_to_edit = self._drum_rack['devs_by_name'][drum_name]
                    if param_name in drum_to_edit:
                        param = drum_to_edit[param_name]
                    if param and param.is_enabled:
                        m_listener = lambda index=i: self.macro_changed(index)
                        macro.add_value_listener(m_listener)
                        p_listener = lambda index=i: self.param_changed(index)
                        param.add_value_listener(p_listener)
                        self._param_macros[i] = (macro, param)
            self._tasks.add(self.get_initial_value)


class MacrobatDRRack(MacrobatParameterRackTemplate):
    '''Macros to params of single Simpler/Sampler.
    '''
    __module__ = __name__

    def __init__(self, parent, rack, track):
        self._drum_rack = {}
        super(MacrobatDRRack, self).__init__(parent, rack, track)

    def disconnect(self):
        self._drum_rack = None
        super(MacrobatDRRack, self).disconnect()

    def setup_device(self, rack):
        '''Set up macros and drum rack params.'''
        super(MacrobatDRRack, self).setup_device(rack)
        self._drum_rack = self.get_drum_rack()
        if self._drum_rack:
            drum_name = rack.name[5:].strip()
            drum_to_edit = {}
            if drum_name in self._drum_rack['devs_by_index']:
                drum_to_edit = self._drum_rack['devs_by_index'][drum_name]
            elif drum_name in self._drum_rack['devs_by_name']:
                drum_to_edit = self._drum_rack['devs_by_name'][drum_name]
            for i in range(1, 9):
                macro = rack.parameters[i]
                param = None
                if macro.is_enabled:
                    name = self._parent.get_name(macro.name)
                    if name in drum_to_edit:
                        param = drum_to_edit[name]
                    if param and param.is_enabled:
                        m_listener = lambda index=i: self.macro_changed(index)
                        macro.add_value_listener(m_listener)
                        p_listener = lambda index=i: self.param_changed(index)
                        param.add_value_listener(p_listener)
                        self._param_macros[i] = (macro, param)
            self._tasks.add(self.get_initial_value)


class MacrobatReceiverRack(MacrobatParameterRackTemplate):
    '''Macros to macros of other racks.
    '''
    __module__ = __name__

    def __init__(self, parent, rack, track):
        super(MacrobatReceiverRack, self).__init__(parent, rack, track)

    def setup_device(self, rack):
        '''Set up receiver and send macros.'''
        super(MacrobatReceiverRack, self).setup_device(rack)
        receiver_macros = self.get_ident_macros(rack)
        if receiver_macros:
            self._sender_macros = []
            for t in chain(self.song().tracks,
                           self.song().return_tracks,
                           (self.song().master_track,)):
                self.get_sender_macros(t.devices)
            if self._sender_macros:
                for r in receiver_macros:
                    index = 0
                    for s in self._sender_macros:
                        index += 1
                        if r[0] == s[0] and r[1].is_enabled and s[1].is_enabled:
                            r_listener = lambda index = index:self.macro_changed(index)
                            r[1].add_value_listener(r_listener)
                            s_listener = lambda index = index:self.param_changed(index)
                            s[1].add_value_listener(s_listener)
                            self._param_macros[index] = (r[1], s[1])
            self._tasks.add(self.get_initial_value)

    def get_sender_macros(self, dev_list):
        '''Look through all devices/chains on all tracks for sender
        macros.
        '''
        for d in dev_list:
            name = self._parent.get_name(d.name)
            if d and d.class_name.endswith('GroupDevice') and not name.startswith('NK RECEIVER'):
                self._sender_macros.extend(self.get_ident_macros(d))
            if self._parent._can_have_nested_devices and d.can_have_chains:
                for c in d.chains:
                    self.get_sender_macros(c.devices)

    def get_ident_macros(self, rack):
        '''Get send and receiver macros.'''
        ident_macros = []
        ident_names = []
        for macro in rack.parameters:
            name = self._parent.get_name(macro.name)
            if macro.original_name.startswith('Macro') and '(*' in name and '*)' in name and len(name) > 4:
                if not name.count('(') > 1 and not name.count(')') > 1:
                    ident = name[name.index('(') + 2:name.index(')') - 1]
                    if ident not in ident_names:
                        ident_macros.append((ident, macro))
                    ident_names.append(ident)
        return ident_macros

    def on_off_changed(self):
        '''Receiver rack doesn't do reset.'''
        pass


class MacrobatTrackRack(MacrobatParameterRackTemplate):
    '''Macros to track params.
    '''
    __module__ = __name__

    def __init__(self, parent, rack, track):
        self._rack = rack
        super(MacrobatTrackRack, self).__init__(parent, rack, track)

    def disconnect(self):
        self._rack = None
        super(MacrobatTrackRack, self).disconnect()

    def setup_device(self, rack):
        '''Setup macros and track mixer params.'''
        super(MacrobatTrackRack, self).setup_device(rack)
        for i in range(1, 9):
            macro = rack.parameters[i]
            param = None
            if macro.is_enabled:
                name = self._parent.get_name(macro.name)
                if name.startswith('SEND') and self._track != self.song().master_track:
                    try:
                        param = self._track.mixer_device.sends[ord(name[5]) - 65]
                    except:
                        param = None
                elif name.startswith('VOL'):
                    param = self._track.mixer_device.volume
                elif name.startswith('PAN'):
                    param = self._track.mixer_device.panning
            if param and param.is_enabled:
                m_listener = lambda index=i: self.macro_changed(index)
                macro.add_value_listener(m_listener)
                p_listener = lambda index=i: self.param_changed(index)
                param.add_value_listener(p_listener)
                self._param_macros[i] = (macro, param)
        self._tasks.add(self.get_initial_value)


class MacrobatDRPadMixRack(MacrobatParameterRackTemplate):
    '''Macros to mixer params of selected DR pad.
    '''
    __module__ = __name__

    def __init__(self, parent, rack, track):
        self._drum_rack = {}
        self._rack = None
        self._selected_chain = None
        super(MacrobatDRPadMixRack, self).__init__(parent, rack, track)

    def disconnect(self):
        self._drum_rack = None
        self._rack = None
        self._selected_chain = None
        super(MacrobatDRPadMixRack, self).disconnect()

    def setup_device(self, rack):
        '''Set up macros and drum rack params.'''
        super(MacrobatDRPadMixRack, self).setup_device(rack)
        self._rack = rack
        self._drum_rack = self.get_drum_rack()
        self._selected_chain = None
        self._on_sends_changed.subject = None
        self._on_selected_pad_changed.subject = None
        if self._drum_rack:
            self._on_selected_pad_changed.subject = self._drum_rack['rack'].view
            self._set_selected_chain()
            if self._selected_chain:
                num_sends = len(self._selected_chain.mixer_device.sends)
                for i in range(1, 9):
                    if rack.parameters[i].is_enabled:
                        param = None
                        if i == 1:
                            param = self._selected_chain.mixer_device.volume
                        elif i == 2:
                            param = self._selected_chain.mixer_device.panning
                        else:
                            s_index = i - 3
                            if s_index < num_sends:
                                param = self._selected_chain.mixer_device.sends[s_index]
                        if param and param.is_enabled:
                            macro = rack.parameters[i]
                            m_listener = lambda index=i: self.macro_changed(index)
                            macro.add_value_listener(m_listener)
                            p_listener = lambda index=i: self.param_changed(index)
                            param.add_value_listener(p_listener)
                            self._param_macros[i] = (macro, param)
                self._tasks.add(self.get_initial_value)

    @subject_slot('selected_drum_pad')
    def _on_selected_pad_changed(self):
        self.setup_device(self._rack)

    @subject_slot('sends')
    def _on_sends_changed(self):
        self.setup_device(self._rack)

    def _set_selected_chain(self):
        self._selected_chain = None
        self._on_sends_changed.subject = None
        if self._drum_rack:
            sel_pad = self._drum_rack['rack'].view.selected_drum_pad
            if sel_pad and sel_pad.chains:
                self._selected_chain = sel_pad.chains[0]
                self._on_sends_changed.subject = self._selected_chain.mixer_device


class CsWrapper(Subject, SlotManager):
    '''Wrapper for a chain selector that limits the max value to the
    number of chains in the rack.
    '''
    __subject_events__ = ('value',)

    def __init__(self, cs):
        super(CsWrapper, self).__init__()
        self._cs = cs
        self._max = 0
        self._on_cs_value_changed.subject = self._cs

    @property
    def is_enabled(self):
        return self._cs.is_enabled

    @property
    def value(self):
        return min(self._cs.value, self._max)

    @value.setter
    def value(self, value):
        if value <= self._max:
            self._cs.value = value

    @property
    def min(self):
        return self._cs.min

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value):
        self._max = value

    @subject_slot('value')
    def _on_cs_value_changed(self):
        if self._cs.value <= self._max:
            self.notify_value()


class MacrobatChainSelectorRack(MacrobatParameterRackTemplate):
    '''Macro 1 to chain selector.
    '''
    __module__ = __name__

    def __init__(self, parent, rack, track):
        self._rack = rack
        self._wrapper = None
        super(MacrobatChainSelectorRack, self).__init__(parent, rack, track)

    def disconnect(self):
        self._rack = None
        self._wrapper = None
        super(MacrobatChainSelectorRack, self).disconnect()

    def scale_macro_value_to_param(self, macro, param):
        return (((param.max - param.min) / 126.0) * macro.value) + param.min

    def setup_device(self, rack):
        '''Set up macro 1 and chain selector.
        '''
        super(MacrobatChainSelectorRack, self).setup_device(rack)
        self._rack = rack
        if self._rack:
            macro = self._rack.parameters[1]
            cs = self._rack.parameters[9]
            if macro.is_enabled and cs.is_enabled:
                self._wrapper = CsWrapper(cs)
                self._wrapper.max = len(self._rack.chains)
                if self._wrapper.max > 1:
                    self._on_chains_changed.subject = self._rack
                    index = 1
                    m_listener = lambda index = index:self.macro_changed(index)
                    macro.add_value_listener(m_listener)
                    p_listener = lambda index = index:self.param_changed(index)
                    self._wrapper.add_value_listener(p_listener)
                    self._param_macros[index] = (macro, self._wrapper)
                self._tasks.add(self.get_initial_value)

    @subject_slot('chains')
    def _on_chains_changed(self):
        if self._wrapper and self._rack:
            self._wrapper.max = len(self._rack.chains)
            self.param_changed(0)
