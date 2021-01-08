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

from __future__ import unicode_literals

from Push.handshake_component import HandshakeComponent


class MockHandshakeTask(object):
    '''Mock objects used to replace Push's handshake task.'''

    def kill(self):
        pass

    def restart(self):
        pass

    def is_running(self):
        return False


class MockHandshake(HandshakeComponent):
    '''Extended HandshakeComponent that overrides methods to allow for
    emulation.
    '''

    def __init__(self, *a, **k):
        super(MockHandshake, self).__init__(*a, **k)
        self._on_identity_value.subject = None
        self._on_dongle_value.subject = None

    def _start_handshake(self):
        self._handshake_succeeded = None
        self._do_succeed()

    def firmware_version(self):
        return 1.16

    def has_version_requirements(self, x, y):
        return True
