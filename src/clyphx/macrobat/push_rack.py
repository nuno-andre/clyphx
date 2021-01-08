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

from __future__ import with_statement, absolute_import, unicode_literals

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from ..consts import NOTE_NAMES


class MacrobatPushRack(ControlSurfaceComponent):
    __module__ = __name__
    __doc__ = 'Sets up Macros 1 and 2 to control Push root note and scale type respectively.'

    def __init__(self, parent, rack):
        ControlSurfaceComponent.__init__(self)
        self._parent = parent
        self._rack = rack
        self._script = None
        self._push_ins = self._connect_to_push()
        self.setup_device()

    def disconnect(self):
        self.remove_macro_listeners()
        self._rack = None
        self._script = None
        self._push_ins = None
        self._parent = None
        ControlSurfaceComponent.disconnect(self)

    def on_enabled_changed(self):
        pass

    def update(self):
        self._push_ins = self._connect_to_push()

    def setup_device(self):
        """Rack names needs to start with nK SCL and Push needs to be selected
        as a control surface.
        """
        self._push_ins = self._connect_to_push()
        self.remove_macro_listeners()
        if self._rack:
            if self._rack.parameters[1].is_enabled:
                self._rack.parameters[1].add_value_listener(self._on_macro_one_value)
            if self._rack.parameters[2].is_enabled:
                self._rack.parameters[2].add_value_listener(self._on_macro_two_value)
            self._parent.schedule_message(1, self._update_rack_name)

    def _connect_to_push(self):
        """Attempt to connect to Push."""
        if self._parent:
            for script in self._parent._control_surfaces():
                if script.__class__.__name__ == 'Push':
                    self._script = script
                    for c in script.components:
                        if c.__class__.__name__ == 'InstrumentComponent':
                            return c
        return None

    def _on_macro_one_value(self):
        """Set Push root note and update rack name."""
        self._tasks.add(self._handle_root_note_change)

    def _handle_root_note_change(self, args=None):
        if self._push_ins:
            new_root = self.scale_macro_value_to_param(self._rack.parameters[1], 12)
            if new_root != self._push_ins._note_layout.root_note:
                self._push_ins._note_layout.root_note = new_root
                self._update_scale_display_and_buttons()
                self._parent.schedule_message(1, self._update_rack_name)

    def _on_macro_two_value(self):
        """Set Push scale type and update rack name."""
        self._tasks.add(self._handle_scale_type_change)

    def _handle_scale_type_change(self, args=None):
        if self._push_ins:
            mode_list = self._script._scales_enabler._mode_map['enabled'].mode._component._scale_list.scrollable_list
            current_type = self._script._scales_enabler._mode_map['enabled'].mode._component._scale_list.scrollable_list.selected_item_index
            new_type = self.scale_macro_value_to_param(self._rack.parameters[2], len(mode_list.items))
            if new_type != current_type:
                mode_list._set_selected_item_index(new_type)
                self._update_scale_display_and_buttons()
                self._parent.schedule_message(1, self._update_rack_name)

    def _update_scale_display_and_buttons(self):
        """Updates Push's scale display and buttons to indicate current
        settings.
        """
        self._script._scales_enabler._mode_map['enabled'].mode._component._update_data_sources()
        self._script._scales_enabler._mode_map['enabled'].mode._component.update()

    def _update_rack_name(self):
        """Update rack name to reflect selected root note and scale type."""
        if self._rack and self._push_ins:
            self._rack.name = 'nK SCL - {} - {}'.format(
                NOTE_NAMES[self._push_ins._note_layout.root_note],
                self._push_ins._note_layout.scale.name,
            )

    def scale_macro_value_to_param(self, macro, hi_value):
        """Scale the value of the macro to the Push parameter being controlled.
        """
        return int((hi_value / 128.0) * macro.value)

    def remove_macro_listeners(self):
        """Remove listeners."""
        if self._rack:
            if self._rack.parameters[1].value_has_listener(self._on_macro_one_value):
                self._rack.parameters[1].remove_value_listener(self._on_macro_one_value)
            if self._rack.parameters[2].value_has_listener(self._on_macro_two_value):
                self._rack.parameters[2].remove_value_listener(self._on_macro_two_value)