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

from __future__ import with_statement
from ClyphXControlSurfaceActions import ClyphXControlSurfaceActions, VisualMetro


class ClyphXControlSurfaceActions9(ClyphXControlSurfaceActions):
    __module__ = __name__
    __doc__ = ' Actions related to control surfaces. This is a specialized version for Live 9.'

    def __init__(self, parent):
        ClyphXControlSurfaceActions.__init__(self, parent)

    def handle_visual_metro(self, script, args):
        """ Handle visual metro for APCs and Launchpad.
        This is a specialized version for L9 that uses component guard to avoid dependency issues. """
        if 'ON' in args and not script['metro']['component']:
            with self._parent.component_guard():
                m = VisualMetro(self._parent, script['metro']['controls'], script['metro']['override'])
                script['metro']['component'] = m
        elif 'OFF' in args and script['metro']['component']:
            script['metro']['component'].disconnect()
            script['metro']['component'] = None
