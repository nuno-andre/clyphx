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

# ***************************** [SETTINGS NOTES] **************************

# Please DO NOT change any of the spacing in this file.

# Please DO NOT change the name of this file or its file extension.  When done
# making your changes to the [SETTINGS] below, just save the file.

# After saving this file, you will need to close/restart Live for your changes
# to take effect.

# For Windows 7/Vista users, depending on how your privileges are set up, you
# may not be able to save changes you make to this file. You may receive an
# error such as Access Denied when trying to save. If this occurs, you will
# need todrag this file onto your desktop, then make your changes and save.
# Whendone, drag the file back into the ClyphX folder.


# ******************************* [SETTINGS] *******************************

# Below you can define a list of SysEx messages that can be sent from macros.
# The entries in the list below are just examples and can be removed.

SYSEX_LIST = [#<------Do NOT remove this.

('Motif Arp I/O', 'F0 43 10 6F 40 70 15 nn F7', 0, 1),
('Motif Arp Type', 'F0 43 10 6F 40 70 14 nn F7', 0, 127),
('Motif Mode', 'F0 43 10 6F 0A 00 01 nn F7', 0, 3),
('Motif EQ Lo', 'F0 43 10 6F 40 70 31 nn F7', 0, 127),
('Motif EQ LoMid', 'F0 43 10 6F 40 70 32 nn F7', 0, 127),
('Motif EQ HiMid', 'F0 43 10 6F 40 70 33 nn F7', 0, 127),
('Motif EQ Hi', 'F0 43 10 6F 40 70 34 nn F7', 0, 127)

]#<------Do NOT remove this.

# Entry Format:
# ('Identifier', 'SysEx String', Min Value, Max Value)

# Identifier:
# A name to identify the SysEx string with.

# SysEx String:
# The SysEx string (in hexadecimal) to send.
# This must start with F0 and end with F7.
# All other values in the string should be within the range of 00 - 7F.
# nn represents the variable byte in the SysEx string, the one the macro will control.

# Min Value:
# The lowest value (in decimal) of the variable byte. Should be in the range of 0 - 127.

# Max Value:
# The highest value (in decimal) of the variable byte. Should be in the range of 0 - 127.

# Notes:
# The Min and Max Value do not not have quotes around them.
# Except for the last entry in the list, every entry in the list should have a comma following it.
