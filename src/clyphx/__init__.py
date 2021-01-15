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

# from __future__ import absolute_import, unicode_literals
import sys
import os

base = os.path.dirname(os.path.realpath(__file__))
vendor = os.path.join(base, 'vendor', 'future')
sys.path.insert(0, vendor)

from future import standard_library
standard_library.install_aliases()

import Live
from .clyphx import ClyphX


def create_instance(c_instance):
    return ClyphX(c_instance)
