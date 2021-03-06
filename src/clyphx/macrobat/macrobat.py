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
    from typing import Any, Iterable, Sequence, List
    from ..core.live import Device, RackDevice, Track

from ..core.xcomponent import XComponent


class Macrobat(XComponent):
    '''Macrobat script component for ClyphX.
    '''
    __module__ = __name__

    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__(parent)
        self.current_tracks = []  # type: List[Any]

    def disconnect(self):
        self.current_tracks = []
        super().disconnect()

    def setup_tracks(self, track):
        # type: (Track) -> None
        '''Setup component tracks on ini and track list changes.'''
        if track not in self.current_tracks:
            self.current_tracks.append(track)
            MacrobatTrackComponent(track, self._parent)


class MacrobatTrackComponent(XComponent):
    '''Track component that monitors track devices.
    '''
    __module__ = __name__

    def __init__(self, track, parent):
        # type: (Track, Any) -> None
        super().__init__(parent)
        self._track = track
        self._track.add_devices_listener(self.setup_devices)
        self._current_devices = []  # type: List[Any]
        self._update_in_progress = False
        self._has_learn_rack = False
        self.setup_devices()

    def disconnect(self):
        self.remove_listeners()
        if self._track:
            if self._track.devices_has_listener(self.setup_devices):
                self._track.remove_devices_listener(self.setup_devices)
            self.remove_devices(self._track.devices)
        self._track = None
        self._current_devices = []
        super().disconnect()

    def update(self):
        if self._track and self.sel_track == self._track:
            self.setup_devices()

    def reallow_updates(self):
        '''Reallow device updates, used to prevent updates happening in
        quick succession.
        '''
        self._update_in_progress = False

    def setup_devices(self):
        # type: () -> None
        '''Get devices on device/chain list and device name changes.'''
        if self._track and not self._update_in_progress:
            self._update_in_progress = True
            self._has_learn_rack = False
            self.remove_listeners()
            self.get_devices(self._track.devices)
            self._parent.schedule_message(5, self.reallow_updates)

    def remove_listeners(self):
        '''Disconnect Macrobat rack components.'''
        for d in self._current_devices:
            d[0].disconnect()
        self._current_devices = []

    def get_devices(self, dev_list):
        # type: (Iterable[RackDevice]) -> None
        '''Go through device and chain lists and setup Macrobat racks.
        '''
        for d in dev_list:
            self.setup_macrobat_rack(d)
            if not d.name_has_listener(self.setup_devices):
                d.add_name_listener(self.setup_devices)
            if self._parent._can_have_nested_devices and d.can_have_chains:
                if not d.chains_has_listener(self.setup_devices):
                    d.add_chains_listener(self.setup_devices)
                for c in d.chains:
                    if not c.devices_has_listener(self.setup_devices):
                        c.add_devices_listener(self.setup_devices)
                    self.get_devices(c.devices)

    def setup_macrobat_rack(self, rack):
        # type: (RackDevice) -> None
        '''Setup Macrobat rack if meets criteria.'''
        from .consts import MACROBAT_RACKS

        if rack.class_name.endswith('GroupDevice'):
            name = rack.name.upper()
            for key, cls in MACROBAT_RACKS.items():
                if name.startswith(key):
                    break
            else:
                return None

            # checks
            if key == 'NK TRACK' and self._track.has_midi_output:
                return None
            elif (key in ('NK DR MULTI', 'NK CHAIN MIX', 'NK DR', 'NK LEARN')
                    and not self._parent._can_have_nested_devices):
                return None
            elif key == 'NK LEARN':
                if self._track != self.song().master_track or self._has_learn_rack:
                    return None
                self._has_learn_rack = True

            # instances
            if key == 'NK MIDI':
                args = self._parent, rack, name
            elif key in ('NK RST', 'NK RND'):
                args = self._parent, rack, name, self._track
            elif key == 'NK SCL':
                args = self._parent, rack
            else:
                # all param racks and push rack
                args= self._parent, rack, self._track

            self._current_devices.append((cls(*args), rack))

    def remove_devices(self, dev_list):
        # type: (Iterable[RackDevice]) -> None
        '''Remove all device listeners.'''
        for d in dev_list:
            if d.name_has_listener(self.setup_devices):
                d.remove_name_listener(self.setup_devices)
            if self._parent._can_have_nested_devices and d.can_have_chains:
                if d.chains_has_listener(self.setup_devices):
                    d.remove_chains_listener(self.setup_devices)
                for c in d.chains:
                    if c.devices_has_listener(self.setup_devices):
                        c.remove_devices_listener(self.setup_devices)
                    self.remove_devices(c.devices)

    def on_selected_track_changed(self):
        self.update()
