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

from _Framework.SessionComponent import SessionComponent
from ableton.v2.control_surface.components.session_ring import SessionRingComponent
from .core import XComponent


class PushApcCombiner(XComponent):
    '''Syncs Push and APC40 session grids for proper
    emulation.
    '''
    __module__ = __name__

    def __init__(self, parent):
        super(PushApcCombiner, self).__init__(parent)
        self._push = None
        self._push_session = None
        self._apc = None
        self._apc_session = None

    def disconnect(self):
        self._remove_listeners()
        self._push = None
        self._push_session = None
        self._apc = None
        self._apc_session = None
        super(PushApcCombiner, self).disconnect()

    def set_up_scripts(self, scripts):
        '''Remove current listeners, get Push/APC scripts, set up listeners
        and also set feedback delay on APC+Push encoders.
        '''
        self._remove_listeners()
        for script in scripts:
            script_name = script.__class__.__name__
            if script_name == 'Push':
                self._push = script
                self._push_session = self._get_session_component(script)
                if self._push_session:
                    for c in script.controls:
                        if c.__class__.__name__ == 'TouchEncoderElement':
                            c.set_feedback_delay(-1)
            elif script_name == 'APC40':
                self._apc = script
                self._apc_session = self._get_session_component(script)
                if self._apc_session:
                    for c in script.controls:
                        if c.__class__.__name__ == 'RingedEncoderElement':
                            c.set_feedback_delay(-1)
                    self._apc_session.add_offset_listener(self._on_apc_offset_changed)
                    self._on_apc_offset_changed()

    def _get_session_component(self, script):
        '''Get the session component for the given script.
        '''
        # comp = None
        # if script and script._components:
        #     for c in script.components:
        #         if isinstance(c, SessionComponent):
        #             comp = c
        #             break
        # if comp is None:
        #     if hasattr(script, '_session_ring'):
        #         return script._session_ring
        # return comp
        if script and script._components:
            for c in script.components:
                if isinstance(c, SessionComponent):
                    return c
        try:
            return script._session_ring
        except AttributeError:
            pass

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
