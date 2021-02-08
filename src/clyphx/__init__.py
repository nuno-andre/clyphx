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
__version__ = 2, 7, 2

import sys
import os

base = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(base, 'vendor'))  # type: ignore
sys.path.insert(0, os.path.join(base, 'vendor', 'future'))  # type: ignore

from future import standard_library
standard_library.install_aliases()

import Live
from .clyphx import ClyphX

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any


def create_instance(c_instance):
    # type: (Any) -> ClyphX
    '''
    :param c_instance: A MidiRemoteScript object that is used to
    communicate with the C++ core of Ableton Live.
    '''
    return ClyphX(c_instance)
