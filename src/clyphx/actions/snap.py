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
    from typing import (
        Any, Union, Optional, Text,
        Iterable, List, Tuple, Mapping, Dict,
    )
    from ..core.live import Device, RackDevice, Track, DeviceParameter
    from ..core.legacy import _DispatchCommand

from functools import partial
from itertools import chain
from Live import Clip
import pickle
from ..core.xcomponent import XComponent


# SNAP DATA ARRAY
# Positions of the main categories
MIX_STD_SETTINGS = 0
MIX_EXT_SETTINGS = 1
PLAY_SETTINGS = 2
DEVICE_SETTINGS = 3


# ASSOCIATED ARRAY
# Positions of standard mix settings
MIX_VOL = 0
MIX_PAN = 1
MIX_SEND_START = 2

# Positions of extended mix settings
MIX_MUTE = 0
MIX_SOLO = 1
MIX_CF = 2

# Positions of chain mix settings
CHAIN_VOL = 0
CHAIN_PAN = 1
CHAIN_MUTE = 2
CHAIN_SEND_START = 3


class XSnapActions(XComponent):
    '''Snapshot-related actions.
    '''
    __module__ = __name__

    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__(parent)
        self.current_tracks = dict()  # type: Dict[Text, Any]
        self._parameters_to_smooth = dict()  # type: Dict[Text, Any]
        self._rack_parameters_to_smooth = dict()  # type: Dict[Text, Any]
        self._smoothing_active = False
        self._synced_smoothing_active = False
        self._rack_smoothing_active = False
        self._smoothing_speed = 7
        self._smoothing_count = 0
        self._last_beat = -1
        self._control_rack = None
        self._snap_id = None
        self._is_control_track = False
        self._include_nested_devices = False
        self._parameter_limit = 500
        self._register_timer_callback(self._on_timer)
        self._has_timer = True
        self.song().add_current_song_time_listener(self._on_time_changed)
        self.song().add_is_playing_listener(self._on_time_changed)

    def disconnect(self):
        if self._has_timer:
            self._unregister_timer_callback(self._on_timer)
        self._remove_control_rack()
        self._remove_track_listeners()
        self.song().remove_current_song_time_listener(self._on_time_changed)
        self.song().remove_is_playing_listener(self._on_time_changed)
        self.current_tracks = dict()
        self._parameters_to_smooth = dict()
        self._rack_parameters_to_smooth = dict()
        self._control_rack = None
        self._snap_id = None
        super().disconnect()

    def dispatch_actions(self, cmd, force=False):
        # type: (_DispatchCommand, bool) -> None
        '''Stores snapshot of track params.'''
        if not isinstance(cmd.xclip, Clip) and not force:
            return
        self.store_track_snapshot(cmd.tracks, cmd.xclip, cmd.ident, cmd.args)

    def store_track_snapshot(self, track_list, xclip, ident, args):
        # type: (Iterable[Track], Union[Clip, Any], Text, Text) -> None
        '''Stores snapshot of track params.'''
        param_count = 0
        snap_data = dict()
        if track_list:
            for track in track_list:
                track_name = track.name.upper()
                if not track_name.startswith('CLYPHX SNAP') and track.name not in snap_data:
                    self._current_track_data = [[], [], None, dict()]  # type: List[Any]  # [List, List, None, Dict]
                    if not args or 'MIX' in args:
                        param_count += self._store_mix_settings(track, args)
                    if 'PLAY' in args and track in self.song().tracks:
                        self._current_track_data[PLAY_SETTINGS] = track.playing_slot_index
                        param_count += 1
                    if (not args or 'DEV' in args) and track.devices:
                        param_count += self._store_device_settings(track, args)
                    snap_data[track.name] = self._current_track_data
            if snap_data:
                if param_count <= self._parameter_limit:
                    xclip.name = '{} || {}'.format(ident, pickle.dumps(snap_data))
                else:
                    current_name = xclip.name
                    xclip.name = 'Too many parameters to store!'
                    self._parent.schedule_message(
                        8, partial(self._refresh_xclip_name, (xclip, current_name))
                    )

    def _store_mix_settings(self, track, args):
        # type: (Track, Text) -> int
        '''Stores mixer related settings and returns the number of
        parameters that were stored.'''
        param_count = 0
        if not 'MIXS' in args:
            mix_vals = [track.mixer_device.volume.value, track.mixer_device.panning.value]
        else:
            mix_vals = [-1, -1]
        if not 'MIX-' in args:
            mix_vals.extend([s.value for s in track.mixer_device.sends])
        param_count += len(mix_vals)
        self._current_track_data[MIX_STD_SETTINGS] = mix_vals
        if ('MIX+' in args or 'MIX-' in args) and track != self.song().master_track:
            self._current_track_data[MIX_EXT_SETTINGS] = [
                int(track.mute), int(track.solo), track.mixer_device.crossfade_assign
            ]
            param_count += 3
        return param_count

    def _store_device_settings(self, track, args):
        # type: (Track, Text) -> int
        '''Stores device related settings and returns the number of
        parameters that were stored.
        '''
        param_count = 0
        try:
            start, end = self._get_snap_device_range(args, track)
        except ValueError:
            pass
        else:
            track_devices = dict()
            for dev_index in range(start, end):
                if dev_index < len(track.devices):
                    current_device = track.devices[dev_index]
                    if current_device.name not in track_devices:
                        track_devices[current_device.name] = dict(
                            params=[p.value for p in current_device.parameters],
                        )
                        param_count += len(current_device.parameters)
                        if (self._include_nested_devices and
                            self._parent._can_have_nested_devices and
                            current_device.can_have_chains
                        ):
                            param_count += self._get_nested_devices(
                                current_device, track_devices[current_device.name], 0
                            )
            if track_devices:
                self._current_track_data[DEVICE_SETTINGS] = track_devices

        return param_count

    def _get_nested_devices(self, rack, nested_devs, parameter_count):
        '''Creates recursive dict of nested devices and returns count of
        parameters.
        '''
        if rack.chains:
            nested_devs['chains'] = dict()
            for ci, c in enumerate(rack.chains):
                nested_devs['chains'][ci] = dict(devices=dict())
                for di, d in enumerate(c.devices):
                    nested_devs['chains'][ci]['devices'][di] = dict(
                        params=[p.value for p in d.parameters]
                    )
                    parameter_count += len(d.parameters)
                    if not rack.class_name.startswith('Midi'):
                        mix_settings = [c.mixer_device.volume.value,
                                        c.mixer_device.panning.value,
                                        c.mixer_device.chain_activator.value]
                        parameter_count += 3
                        sends = c.mixer_device.sends
                        if sends:
                            for s in sends:
                                mix_settings.append(s.value)
                            parameter_count += len(sends)
                        nested_devs['chains'][ci]['mixer'] = mix_settings
                    if d.can_have_chains and d.chains:
                        self._get_nested_devices(
                            d, nested_devs['chains'][ci]['devices'][di], parameter_count
                        )
        return parameter_count

    def recall_track_snapshot(self, name, xclip, disable_smooth=False):
        # type: (None, Clip, bool) -> None
        '''Recalls snapshot of track params.'''
        self._snap_id = xclip.name[xclip.name.index('['):xclip.name.index(']')+1].strip().upper()
        #FIXME
        snap_data = pickle.loads(str(xclip.name)[len(self._snap_id) + 4:])
        self._parameters_to_smooth = dict()
        self._rack_parameters_to_smooth = dict()
        is_synced = False if disable_smooth else self._init_smoothing(xclip)

        for track, param_data in snap_data.items():
            pos = param_data[PLAY_SETTINGS]
            if track in self.current_tracks:
                track = self.current_tracks[track]
                self._recall_mix_settings(track, param_data)
                if (pos is not None and not track.is_foldable
                        and track is not self.song().master_track):
                    if pos < 0:
                        track.stop_all_clips()
                    elif (track.clip_slots[pos].has_clip
                            and track.clip_slots[pos].clip != xclip):
                        track.clip_slots[pos].fire()
                if pos:
                    self._recall_device_settings(track, param_data)

        if self._is_control_track and self._parameters_to_smooth:
            if (not self._control_rack or
                    (self._control_rack and
                        self._control_rack.parameters[0].value != 1.0)):
                self._smoothing_active = not is_synced
                self._synced_smoothing_active = is_synced
            else:
                self._parent.schedule_message(1, self._refresh_control_rack)

    def _recall_mix_settings(self, track, param_data):
        # type: (Track, Mapping[int, Any]) -> None
        '''Recalls mixer related settings.'''
        std = param_data[MIX_STD_SETTINGS]
        if std:
            pan_value = std[MIX_PAN]
            if (track.mixer_device.volume.is_enabled and std[MIX_VOL] != -1):
                self._get_parameter_data_to_smooth(
                    track.mixer_device.volume, std[MIX_VOL])

            if track.mixer_device.panning.is_enabled and not isinstance(pan_value, int):
                self._get_parameter_data_to_smooth(
                    track.mixer_device.panning, std[MIX_PAN])

            if track is not self.song().master_track:
                sends = track.mixer_device.sends
                for i in range(len(std) - MIX_SEND_START):
                    if (i <= len(sends) - 1 and sends[i].is_enabled):
                        self._get_parameter_data_to_smooth(
                            sends[i], std[MIX_SEND_START + i])

        if param_data[1] and track is not self.song().master_track:
            ext = param_data[MIX_EXT_SETTINGS]
            track.mute = ext[MIX_MUTE]
            track.solo = ext[MIX_SOLO]
            track.mixer_device.crossfade_assign = ext[MIX_CF]

    def _recall_device_settings(self, track, param_data):
        # type: (Track, Mapping[int, Any]) -> None
        '''Recalls device related settings.'''
        settings = param_data[DEVICE_SETTINGS]
        for device in track.devices:
            if device.name in settings:
                self._recall_device_snap(device, settings[device.name]['params'])
                if (self._include_nested_devices
                        and self._parent._can_have_nested_devices
                        and device.can_have_chains
                        and 'chains' in settings[device.name]):
                    self._recall_nested_device_snap(
                        device, settings[device.name]['chains'])
                del settings[device.name]

    def _recall_device_snap(self, device, stored_params):
        # type: (Device, Any) -> None
        '''Recalls the settings of a single device.'''
        if device and len(device.parameters) == len(stored_params):
            for i, param in enumerate(device.parameters):
                if param.is_enabled:
                    self._get_parameter_data_to_smooth(param, stored_params[i])

    def _recall_nested_device_snap(self, rack, stored_params):
        # type: (RackDevice, Mapping) -> None
        '''Recalls the settings and mixer settings of nested devices.'''
        if rack.chains and stored_params:
            num_chains = len(rack.chains)
            for chain_key in stored_params.keys():
                if chain_key < num_chains:
                    chain = rack.chains[chain_key]
                    chain_devices = chain.devices
                    num_chain_devices = len(chain_devices)
                    stored_chain = stored_params[chain_key]
                    stored_devices = stored_chain['devices']
                    for device_key in stored_devices.keys():
                        if device_key < num_chain_devices:
                            self._recall_device_snap(
                                chain_devices[device_key],
                                stored_devices[device_key]['params'],
                            )
                            if (chain_devices[device_key].can_have_chains and
                                    'chains' in stored_devices[device_key]):
                                self._recall_nested_device_snap(
                                    chain_devices[device_key],
                                    stored_devices[device_key]['chains'],
                                )
                    if not rack.class_name.startswith('Midi') and 'mixer' in stored_chain:
                        if chain.mixer_device.volume.is_enabled:
                            self._get_parameter_data_to_smooth(
                                chain.mixer_device.volume,
                                stored_chain['mixer'][CHAIN_VOL],
                            )
                        if chain.mixer_device.panning.is_enabled:
                            self._get_parameter_data_to_smooth(
                                chain.mixer_device.panning,
                                stored_chain['mixer'][CHAIN_PAN],
                            )
                        if chain.mixer_device.chain_activator.is_enabled:
                            self._get_parameter_data_to_smooth(
                                chain.mixer_device.chain_activator,
                                stored_chain['mixer'][CHAIN_MUTE],
                            )
                        sends = chain.mixer_device.sends
                        if sends:
                            num_sends = len(sends)
                            for i in range(len(stored_chain['mixer']) - CHAIN_SEND_START):
                                if i < num_sends and sends[i].is_enabled:
                                    self._get_parameter_data_to_smooth(
                                        sends[i],
                                        stored_chain['mixer'][CHAIN_SEND_START + i],
                                    )

    def _init_smoothing(self, xclip):
        # type: (Clip) -> bool
        '''Initializes smoothing and returns whether or not smoothing is
        synced to tempo or not.
        '''
        self._smoothing_count = 0
        self._smoothing_active = False
        self._rack_smoothing_active = False
        self._synced_smoothing_active = False
        is_synced = False
        track_name = xclip.canonical_parent.canonical_parent.name.upper()
        self._is_control_track = track_name.startswith('CLYPHX SNAP')
        if self._is_control_track:
            self._setup_control_rack(xclip.canonical_parent.canonical_parent)
            self._smoothing_speed = 8
            new_speed = 8
            if 'SP:' in self._snap_id:
                speed = self._snap_id[self._snap_id.index(':')+1:self._snap_id.index(']')].strip()
                is_synced = 'S' in speed
                try:
                    new_speed = int(speed.replace('S', ''))
                except Exception:
                    new_speed = 8
            else:
                if '[' and ']' in track_name:
                    speed = track_name[track_name.index('[')+1:track_name.index(']')].strip()
                    is_synced = 'S' in speed
                    try:
                        new_speed = int(speed.replace('S', ''))
                    except Exception:
                        new_speed = 8
            if is_synced:
                new_speed *= self.song().signature_numerator
            if 0 <= new_speed < 501:
                self._smoothing_speed = new_speed
        return is_synced

    def _setup_control_rack(self, track):
        # type: (Track) -> None
        '''Sets up rack to use for morphing between current vals and
        snapped vals.'''
        self._remove_control_rack()
        for dev in track.devices:
            dev_name = dev.name.upper()
            if dev.class_name.endswith('GroupDevice') and dev_name.startswith('CLYPHX SNAP'):
                self._control_rack = dev
                break

    def _refresh_control_rack(self):
        '''Refreshes rack name and macro value on snap triggered. If
        triggered when rack off, clear snap id from rack name.
        '''
        if self._control_rack and self._snap_id:
            if self._control_rack.parameters[0].value == 1.0:
                self._control_rack.name = 'ClyphX Snap {}'.format(self._snap_id)
                self._control_rack.parameters[1].value = 0.0
                self._rack_smoothing_active = True
                if not self._control_rack.parameters[1].value_has_listener(
                        self._control_rack_macro_changed):
                    self._control_rack.parameters[1].add_value_listener(
                        self._control_rack_macro_changed)
            else:
                self._control_rack.name = 'ClyphX Snap'

    def _control_rack_macro_changed(self):
        '''Returns param values to set based on macro value and build
        dict.
        '''
        if (self._rack_smoothing_active and
                self._parameters_to_smooth and
                self._control_rack.parameters[0].value == 1.0):
            self._rack_parameters_to_smooth = dict()
            macro_value = self._control_rack.parameters[1].value
            new_dict = dict()
            for p, v in self._parameters_to_smooth.items():
                param_value = v[2] + (macro_value * v[0])
                if p.is_quantized:
                    if macro_value < 63 and p.value != v[2]:
                        param_value = v[2]
                    elif macro_value > 63 and p.value != v[1]:
                        param_value = v[1]
                    else:
                        param_value = None
                if param_value is not None:
                    new_dict[p] = param_value
            self._rack_parameters_to_smooth = new_dict

    def _on_timer(self):
        '''Smoothes parameter value changes via timer.'''
        if self._smoothing_active and self._parameters_to_smooth:
            self._apply_timed_smoothing()
        if self._rack_smoothing_active and self._rack_parameters_to_smooth:
            for p, v in self._rack_parameters_to_smooth.items():
                p.value = v
                del self._rack_parameters_to_smooth[p]

    def _on_time_changed(self):
        '''Smoothes parameter value changes synced to playback.'''
        if (self._synced_smoothing_active and
                self._parameters_to_smooth and
                self.song().is_playing):
            time = int(str(self.song().get_current_beats_song_time()).split('.')[2])
            if self._last_beat != time:
                self._last_beat = time
                self._tasks.add(self._apply_timed_smoothing)

    def _apply_timed_smoothing(self, arg=None):
        # type: (None) -> None
        '''Applies smoothing for either timer or sync.'''
        self._smoothing_count += 1
        for p, v in self._parameters_to_smooth.items():
            param_value = v[2] + (self._smoothing_count * v[0])
            if p.is_quantized:
                p.value = v[1]
                del self._parameters_to_smooth[p]
            elif param_value == v[1] or self._smoothing_count >= self._smoothing_speed:
                del self._parameters_to_smooth[p]
                p.value = v[1]
            else:
                p.value = param_value

    def _get_parameter_data_to_smooth(self, parameter, new_value):
        # type: (DeviceParameter, float) -> None
        '''Returns parameter data to smooth and return list of smoothing
        value, target value and current value.
        '''
        factor = self._smoothing_speed
        if (self._is_control_track and
                self._control_rack and
                self._control_rack.parameters[0].value == 1.0):
            factor = 127
        if factor and self._is_control_track:
            difference = new_value - parameter.value
            if difference and (factor == 127 or (factor != 127 and abs(difference) > 0.01)):
                if parameter.is_quantized:
                    factor = 1
                param_data = [(new_value - parameter.value) / factor, new_value, parameter.value]
                if difference < 0.0:
                    param_data = [((parameter.value - new_value) / factor) * -1, new_value, parameter.value]
                self._parameters_to_smooth[parameter] = param_data
            else:
                parameter.value = new_value
        else:
            parameter.value = new_value

    @staticmethod
    def _get_snap_device_range(args, track):
        # type: (Text, Track) -> Tuple[int, int]
        '''Returns range of devices to snapshot.'''
        dev_args = (args.replace('MIX', '').replace('PLAY', '')
            .replace('DEV', '').replace('IO', ''))
        start = 0
        end = 1

        if dev_args:
            if 'ALL' in dev_args:
                end = len(track.devices)
            elif '-' in dev_args:
                try:
                    start, end = map(int, dev_args.split('-'))
                    start -= 1
                except Exception:
                    pass
            else:
                try:
                    start = int(dev_args) - 1
                    end = start + 1
                except Exception:
                    pass

        if end > len(track.devices) or start < 0 or end < start:
            raise ValueError("Range of devices not found in '{}'".format(dev_args))

        return (start, end)

    def setup_tracks(self):
        '''Stores dictionary of tracks by name.'''
        self.current_tracks = dict()
        self._remove_track_listeners()
        for track in chain(self.song().tracks,
                           self.song().return_tracks,
                           (self.song().master_track,)):
            if not track.name_has_listener(self.setup_tracks):
                track.add_name_listener(self.setup_tracks)
            name = track.name.upper()
            if track.name not in self.current_tracks and not name.startswith('CLYPHX SNAP'):
                self.current_tracks[track.name] = track

    def _refresh_xclip_name(self, xclip_data):
        # type: (Dict) -> None
        '''Refreshes xclip's previous name in cases where a snap is
        asking to store too many params.
        '''
        xclip_data[0].name = xclip_data[1]

    def _remove_control_rack(self):
        '''Removes control rack listeners.'''
        if self._control_rack:
            self._control_rack.name = 'ClyphX Snap'
            if self._control_rack.parameters[1].value_has_listener(
                self._control_rack_macro_changed
            ):
                self._control_rack.parameters[1].remove_value_listener(
                    self._control_rack_macro_changed
                )
        self._control_rack = None

    def _remove_track_listeners(self):
        '''Removes track name listeners.'''
        for track in chain(self.song().tracks,
                           self.song().return_tracks,
                           (self.song().master_track,)):
            if track.name_has_listener(self.setup_tracks):
                track.remove_name_listener(self.setup_tracks)
