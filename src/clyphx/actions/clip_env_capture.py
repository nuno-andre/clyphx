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

if TYPE_CHECKING:
    from typing import Any, Optional, Text, Tuple
    from ..core.live import Clip, Device, DeviceParameter, RackDevice, Track

from ..core.xcomponent import ControlSurfaceComponent


class XClipEnvCapture(ControlSurfaceComponent):
    '''Captures mixer/device parameters as clip envelopes.'''

    def disconnect(self):
        self._parent = None
        super().disconnect()

    def update(self):
        pass

    def capture(self, clip, track, args):
        # type: (Clip, Track, Text) -> None
        clip.clear_all_envelopes()
        if not args or 'MIX' in args:
            self._capture_mix_settings(clip, track, args)
        if (not args or 'DEV' in args) and track.devices:
            self._capture_device_settings(clip, track, args)

    def _capture_mix_settings(self, clip, track, args):
        # type: (Clip, Track, Text) -> None
        if 'MIXS' not in args:
            self._insert_envelope(clip, track.mixer_device.volume)
            self._insert_envelope(clip, track.mixer_device.panning)
        if 'MIX-' not in args:
            for s in track.mixer_device.sends:
                self._insert_envelope(clip, s)

    def _capture_device_settings(self, clip, track, args):
        # type: (Clip, Track, Text) -> None
        dev_range = self._get_device_range(args, track)
        if dev_range:
            start, end = dev_range[0:2]
            end = min(end, len(track.devices))
            for i in range(start, end):
                current_device = track.devices[i]  # type: RackDevice
                for p in current_device.parameters:
                    self._insert_envelope(clip, p)
                if current_device.can_have_chains:
                    self._capture_nested_devices(clip, current_device)

    def _capture_nested_devices(self, clip, rack):
        # type: (Clip, RackDevice) -> None
        if rack.chains:
            for chain in rack.chains:
                for device in chain.devices:
                    for p in device.parameters:
                        self._insert_envelope(clip, p)
                    if not rack.class_name.startswith('Midi'):
                        self._insert_envelope(clip, chain.mixer_device.volume)
                        self._insert_envelope(clip, chain.mixer_device.panning)
                        self._insert_envelope(clip, chain.mixer_device.chain_activator)
                        sends = chain.mixer_device.sends
                        if sends:
                            for s in sends:
                                self._insert_envelope(clip, s)
                    if device.can_have_chains and device.chains:
                        self._capture_nested_devices(clip, device)

    @staticmethod
    def _insert_envelope(clip, param):
        # type: (Clip, DeviceParameter) -> None
        env = clip.automation_envelope(param)
        if env:
            env.insert_step(clip.loop_start, 0.0, param.value)

    @staticmethod
    def _get_device_range(args, track):
        # type: (Text, Track) -> Optional[Tuple[int, int]]
        '''Returns range of devices to capture.'''
        dev_args = args.replace('MIX', '')
        dev_args = dev_args.replace('DEV', '')
        start, end = 0, 1
        if dev_args:
            if 'ALL' in dev_args:
                start = 0
                end = len(track.devices)
            elif '-' in dev_args:
                try:
                    s, e = dev_args.split('-')
                    start = int(s) - 1
                    end = int(e)
                except Exception:
                    start, end = 0, 1
            else:
                try:
                    start = int(dev_args) - 1
                    end = start + 1
                except Exception:
                    pass
        if 0 <= start and end <= len(track.devices) and start <= end:
            return (start, end)
        return None
