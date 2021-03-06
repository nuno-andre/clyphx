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
from typing import TYPE_CHECKING
from functools import partial
from builtins import super
import logging

if TYPE_CHECKING:
    from typing import Any, Iterable, Sequence, Optional, Dict, Text, List
    from .core.live import MidiRemoteScript

from pushbase.push_base import PushBase
from _Framework.ControlSurface import ControlSurface
from .core.xcomponent import ControlSurfaceComponent, SessionComponent

log = logging.getLogger(__name__)


class CsLinker(ControlSurfaceComponent):
    '''Links the SessionComponents of two control surface scripts.
    '''

    def __init__(self):
        super().__init__()
        self._slave_objects = [None, None]  # type: List[Any]
        self._script_names = list()  # type: List[Text]
        self._horizontal_link = False
        self._matched_link = False
        self._multi_axis_link = False

    def disconnect(self):
        '''Extends standard to disconnect and remove slave objects.'''
        for obj in self._slave_objects:
            if obj is not None:
                obj.disconnect()
        self._slave_objects = None  # type: ignore
        super().disconnect()

    def update(self):
        pass

    def read_settings(self, settings):
        # type: (Dict[Text, Any]) -> None
        '''Read settings dict.
        '''
        self._matched_link = settings.get('cslinker_matched_link', False)
        self._horizontal_link = settings.get('cslinker_horizontal_link', False)
        self._multi_axis_link = settings.get('cslinker_multi_axis_link', False)
        self._script_names = [x for x in [settings.get('cslinker_script_1_name'),
                                          settings.get('cslinker_script_2_name')] if x]
        # TODO: decouple from settings reading
        # see: clyphx.connect_script_instances
        if self._script_names:
            cs = self.canonical_parent._control_surfaces()
            if 'PUSH2' in self._script_names:
                msg = partial(self.connect_script_instances, cs)
                self.canonical_parent.schedule_message(20, msg)
            else:
                self.connect_script_instances(cs)

    def connect_script_instances(self, instantiated_scripts):
        # type: (Iterable[MidiRemoteScript]) -> None
        '''Attempts to find the two specified scripts, find their
        SessionComponents and create slave objects for them.
        '''
        if self._script_names:
            scripts = [None, None]  # type: List[SessionComponent]
            scripts_have_same_name = self._script_names[0] == self._script_names[1]
            for script in instantiated_scripts:
                script_name = script.__class__.__name__.upper()
                if script_name in ('PUSH', 'PUSH2') or (
                    isinstance(script, ControlSurface) and script.components
                ):
                    if script_name == self._script_names[0]:
                        if scripts_have_same_name:
                            scripts[scripts[0] is not None] = script
                        else:
                            scripts[0] = script
                    elif script_name == self._script_names[1]:
                        scripts[1] = script
                    if scripts[0] and scripts[1]:
                        break
            else:
                log.error('Unable to locate specified scripts (%s)',
                          self.canonical_parent)
                return

            log.info('Scripts found (%s)', self.canonical_parent)
            ssn_comps = []
            for script in scripts:
                if isinstance(script, PushBase):
                    ssn_comps.append(script._session_ring)
                for c in script.components:
                    if isinstance(c, SessionComponent):
                        ssn_comps.append(c)
                        break
            if len(ssn_comps) == 2:
                log.info('SessionComponents for specified scripts located (%s)',
                         self.canonical_parent)
                if self._matched_link:
                    for s in ssn_comps:
                        s._link()
                else:
                    if self._script_names[0] in ('PUSH', 'PUSH2'):
                        h_offset = ssn_comps[0].num_tracks
                        v_offset = ssn_comps[0].num_scenes
                    else:
                        h_offset = ssn_comps[0].width()
                        v_offset = ssn_comps[0].height()
                    h_offset_1 = 0 if not self._horizontal_link and self._multi_axis_link else -(h_offset)
                    v_offset_1 = 0 if self._horizontal_link and self._multi_axis_link else -(v_offset)
                    h_offset_2 = 0 if not self._horizontal_link and self._multi_axis_link else h_offset
                    v_offset_2 = 0 if self._horizontal_link and self._multi_axis_link else v_offset
                    self._slave_objects[0] = SessionSlave(
                        self._horizontal_link, self._multi_axis_link,
                        ssn_comps[0], ssn_comps[1], h_offset_1, v_offset_1,
                    )
                    self._slave_objects[1] = SessionSlaveSecondary(
                        self._horizontal_link, self._multi_axis_link,
                        ssn_comps[1], ssn_comps[0], h_offset_2, v_offset_2,
                    )
                    self.canonical_parent.schedule_message(10, self._refresh_slave_objects)
            else:
                log.error('Unable to locate SessionComponents for specified scripts (%s)',
                          self.canonical_parent)

    def on_track_list_changed(self):
        '''Refreshes slave objects if horizontally linked.'''
        if not self._matched_link and (self._horizontal_link or self._multi_axis_link):
            self._refresh_slave_objects()

    def on_scene_list_changed(self):
        '''Refreshes slave objects if vertically linked.'''
        # TODO: horizontal?
        if not self._matched_link and (not self._horizontal_link or self._multi_axis_link):
            self._refresh_slave_objects()

    def _refresh_slave_objects(self):
        '''Refreshes offsets of slave objects.'''
        for obj in self._slave_objects:
            if obj is not None:
                obj._on_offsets_changed()


class SessionSlave(object):
    '''Base class for linking two SessionComponents.
    '''

    def __init__(self, horz_link, multi_axis, self_comp, observed_comp, h_offset, v_offset):
        # type: (bool, bool, SessionComponent, SessionComponent, int, int) -> None
        self._horizontal_link = horz_link
        self._multi_axis_link = multi_axis
        self._h_offset = h_offset
        self._v_offset = v_offset
        self._self_ssn_comp = self_comp
        self._observed_ssn_comp = observed_comp
        self._last_self_track_offset = -1  # type: int
        self._last_self_scene_offset = -1  # type: int
        self._last_observed_track_offset = -1  # type: int
        self._last_observed_scene_offset = -1  # type: int
        self._num_tracks = -1  # type: int
        self._num_scenes = -1  # type: int
        self._observed_ssn_comp.add_offset_listener(self._on_offsets_changed)

    def disconnect(self):
        self._self_ssn_comp = None
        self._observed_ssn_comp.remove_offset_listener(self._on_offsets_changed)
        self._observed_ssn_comp = None

    def _on_offsets_changed(self, arg_a=None, arg_b=None):
        # type: (None, None) -> None
        '''Called on offset changes to the observed SessionComponent to
        handle moving offsets if possible.
        '''
        if self._horizontal_link or self._multi_axis_link:
            new_num_tracks = len(self._self_ssn_comp.tracks_to_use())
            if new_num_tracks != self._num_tracks:
                # if track list changed, need to completely refresh offsets
                self._num_tracks = new_num_tracks
                self._last_self_track_offset = -1
                self._last_observed_track_offset = -1
            observed_offset = self._observed_track_offset()
            if observed_offset != self._last_observed_track_offset:
                # if observed offset unchanged, do nothing
                self._last_observed_track_offset = observed_offset
                if self.can_change_track_offset:
                    self_offset = max(self._min_track_offset(),
                                      min(self._num_tracks,
                                          self._last_observed_track_offset + self._h_offset))
                    if self_offset != self._last_self_track_offset:
                        # if self offset unchanged, do nothing
                        self._last_self_track_offset = self_offset
                        self._self_ssn_comp.set_offsets(self._last_self_track_offset,
                                                        self._self_scene_offset())
                else:
                    return

        if not self._horizontal_link or self._multi_axis_link:
            if callable(self._self_ssn_comp.song):
                new_num_scenes = len(self._self_ssn_comp.song().scenes)
            else:
                new_num_scenes = len(self._self_ssn_comp.song.scenes)
            if new_num_scenes != self._num_scenes:
                # if scene list changed, need to completely refresh offsets
                self._num_scenes = new_num_scenes
                self._last_self_scene_offset = -1
                self._last_observed_scene_offset = -1
            observed_offset = self._observed_scene_offset()
            if observed_offset != self._last_observed_scene_offset:
                # if observed offset unchanged, do nothing
                self._last_observed_scene_offset = observed_offset
                if self.can_change_scene_offset:
                    self_offset = max(self._min_scene_offset(),
                                      min(self._num_scenes,
                                          self._last_observed_scene_offset + self._v_offset))
                    if self_offset != self._last_self_scene_offset:
                        # if self offset unchanged, do nothing
                        self._last_self_scene_offset = self_offset
                        self._self_ssn_comp.set_offsets(self._self_track_offset(),
                                                        self._last_self_scene_offset)
                else:
                    return

    def _observed_track_offset(self):
        # type: () -> int
        try:
            return self._observed_ssn_comp.track_offset()
        except TypeError:
            return self._observed_ssn_comp.track_offset

    def _self_track_offset(self):
        # type: () -> int
        try:
            return self._self_ssn_comp.track_offset()
        except TypeError:
            return self._self_ssn_comp.track_offset

    def _observed_scene_offset(self):
        # type: () -> int
        try:
            return self._observed_ssn_comp.scene_offset()
        except TypeError:
            return self._observed_ssn_comp.scene_offset

    def _self_scene_offset(self):
        # type: () -> int
        try:
            return self._self_ssn_comp.scene_offset()
        except TypeError:
            return self._self_ssn_comp.scene_offset

    @property
    def can_change_track_offset(self):
        # type: () -> bool
        '''Returns whether is possible to move the track offset.
        '''
        try:
            w = self._self_ssn_comp.width()  # type: int
        except AttributeError:
            w = self._self_ssn_comp.num_tracks
        return self._num_tracks > w

    def _min_track_offset(self):
        '''Returns the minimum track offset.'''
        return 0

    @property
    def can_change_scene_offset(self):
        # type: () -> bool
        '''Returns whether is possible to move the scene offset.
        '''
        try:
            h = self._self_ssn_comp.height()  # type: int
        except AttributeError:
            h = self._self_ssn_comp.num_scenes
        return self._num_scenes > h

    def _min_scene_offset(self):
        '''Returns the minimum scene offset.'''
        return 0


class SessionSlaveSecondary(SessionSlave):
    '''SessionSlaveSecondary is the second of the two linked slave
    objects.

    This overrides the functions that return whether offsets can be
    changed as well as the functions that return minimum offsets.
    '''

    @property
    def can_change_track_offset(self):
        # type: () -> bool
        try:
            self_width = self._self_ssn_comp.width()
        except AttributeError:
            self_width = self._self_ssn_comp.num_tracks
        try:
            obs_width = self._observed_ssn_comp.width()
        except AttributeError:
            obs_width = self._observed_ssn_comp.num_tracks
        return bool(self._num_tracks >= self_width + obs_width)

    def _min_track_offset(self):
        # type: () -> int
        return self._last_observed_track_offset

    @property
    def can_change_scene_offset(self):
        # type: () -> bool
        try:
            self_h = self._self_ssn_comp.height()
        except AttributeError:
            self_h = self._self_ssn_comp.num_scenes
        try:
            obs_h = self._observed_ssn_comp.height()
        except AttributeError:
            obs_h = self._observed_ssn_comp.num_scenes
        return bool(self._num_scenes >= self_h + obs_h)

    def _min_scene_offset(self):
        # type: () -> int
        return self._last_observed_scene_offset
