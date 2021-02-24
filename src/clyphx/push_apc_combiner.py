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
from builtins import super

from ableton.v2.control_surface.components.session_ring import SessionRingComponent
from ableton.v2.control_surface.elements import TouchEncoderElement
from _APC.RingedEncoderElement import RingedEncoderElement
from APC40 import APC40
from Push import Push

from .core.xcomponent import XComponent, SessionComponent

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, Iterable, Optional, Text, Dict, List
    from .core.live import MidiRemoteScript


class PushApcCombiner(XComponent):
    '''Syncs Push and APC40 session grids for proper emulation.
    '''
    __module__ = __name__

    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__(parent)
        self._push = None           # type: Optional[MidiRemoteScript]
        self._push_session = None
        self._apc = None
        self._apc_session = None

    def disconnect(self):
        self._remove_listeners()
        self._push = None
        self._push_session = None
        self._apc = None
        self._apc_session = None
        super().disconnect()

    def set_up_scripts(self, scripts):
        # type: (Iterable[MidiRemoteScript]) -> None
        '''Remove current listeners, get Push/APC scripts, set up
        listeners and also set feedback delay on APC+Push encoders.
        '''
        self._remove_listeners()
        for script in scripts:
            if isinstance(script, Push):
                self._push = script
                self._push_session = self._get_session_component(script)
                if self._push_session:
                    for c in script.controls:
                        if isinstance(c, TouchEncoderElement):
                            c.set_feedback_delay(-1)
            elif isinstance(script, APC40):
                self._apc = script
                self._apc_session = self._get_session_component(script)
                if self._apc_session:
                    for c in script.controls:
                        if isinstance(c, RingedEncoderElement):
                            c.set_feedback_delay(-1)
                    self._apc_session.add_offset_listener(self._on_apc_offset_changed)
                    self._on_apc_offset_changed()

    def _get_session_component(self, script):
        # type: (MidiRemoteScript) -> Optional[Any]
        '''Get the session component for the given script.
        '''
        if script and script._components:
            for c in script.components:
                if isinstance(c, SessionComponent):
                    return c
        try:
            return script._session_ring
        except AttributeError:
            return None

    def _on_apc_offset_changed(self):
        '''Update Push offset on APC offset changed and suppress its
        highlight.
        '''
        if self._push_session and self._apc_session:
            self._push_session.set_offsets(self._apc_session.track_offset(),
                                           self._apc_session.scene_offset())
            self._push_session._session_ring.hide_highlight()

    def _remove_listeners(self):
        if self._apc_session and self._apc_session.offset_has_listener(self._on_apc_offset_changed):
            self._apc_session.remove_offset_listener(self._on_apc_offset_changed)
