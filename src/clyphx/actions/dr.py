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

if TYPE_CHECKING:
    from typing import Any, Optional, Callable, Iterable, Sequence, Text
    from ..core.legacy import _DispatchCommand
    from ..core.live import Track, Clip, Device

from ..core.xcomponent import XComponent
from ..consts import switch

MAX_SCROLL_POS = 28


class XDrActions(XComponent):
    '''Drum Rack actions.
    '''
    __module__ = __name__

    def dispatch_dr_actions(self, cmd):
        if cmd.args:
            for scmd in cmd:
                self.dispatch_dr_action(scmd.track, scmd.xclip, scmd.ident, scmd.args)

    def dispatch_dr_action(self, track, xclip, ident, args):
        # type: (Track, Clip, Text, Text) -> None
        from .consts import DR_ACTIONS

        arg_action = DR_ACTIONS.get(args.split()[0].upper())
        if arg_action:
            action = partial(arg_action, self)   # type: Callable
        elif 'PAD' in args:
            action = self.dispatch_pad_action
        else:
            return

        # get dr to operate on
        for device in track.devices:
            if device.can_have_drum_pads:
                action(device, args)
                break

    def scroll_selector(self, dr, args):
        # type: (Device, Text) -> None
        '''Scroll Drum Rack selector up/down.'''
        args = args.replace('SCROLL', '').strip()
        if args.startswith(('<', '>')):
            factor = self._parent.get_adjustment_factor(args)
            pos = dr.view.drum_pads_scroll_position
            if factor > 0:
                if pos < MAX_SCROLL_POS - factor:
                    value = pos + factor
                else:
                    value = MAX_SCROLL_POS
            else:
                if pos + factor > 0:
                    value = pos + factor
                else:
                    value = 0
            dr.view.drum_pads_scroll_position = value

    def unmute_all(self, dr, args):
        # type: (Device, None) -> None
        '''Unmute all pads in the Drum Rack.'''
        for pad in dr.drum_pads:
            pad.mute = False

    def unsolo_all(self, dr, args):
        # type: (Device, None) -> None
        '''Unsolo all pads in the Drum Rack.'''
        for pad in dr.drum_pads:
            pad.solo = False

# region PAD ACTIONS
    def dispatch_pad_action(self, dr, track, xclip, ident, _args):
        # type: (Any, None, None, None, Text) -> None
        '''Dispatches pad-based actions.'''
        from .consts import PAD_ACTIONS

        args = _args.split()
        if len(args) > 1:
            pads = self._get_pads_to_operate_on(dr, args[0].replace('PAD', '').strip())
            if pads:
                action = args[1].upper()
                action_arg = args[2] if len(args) > 2 else None
                if action in PAD_ACTIONS:
                    PAD_ACTIONS[action](self, pads, action_arg)
                elif action == 'SEL':
                    dr.view.selected_drum_pad = pads[-1]
                elif 'SEND' in action and action_arg and len(args) > 3:
                    self._adjust_pad_send(pads, args[3], action_arg)

    def _mute_pads(self, pads, action_arg):
        # type: (Iterable[Any], Optional[Text]) -> None
        '''Toggles or turns on/off pad mute.'''
        for pad in pads:
            switch(pad, 'mute', action_arg)

    def _solo_pads(self, pads, action_arg):
        # type: (Iterable[Any], Optional[Text]) -> None
        '''Toggles or turns on/off pad solo.'''
        for pad in pads:
            switch(pad, 'solo', action_arg)

    def _adjust_pad_volume(self, pads, action_arg):
        # type: (Sequence[Any], Text) -> None
        '''Adjust/set pad volume.'''
        for pad in pads:
            if pad.chains:
                param = pad.chains[0].mixer_device.volume
                self._parent.do_parameter_adjustment(param, action_arg)

    def _adjust_pad_pan(self, pads, action_arg):
        # type: (Sequence[Any], Text) -> None
        '''Adjust/set pad pan.'''
        for pad in pads:
            if pad.chains:
                param = pad.chains[0].mixer_device.panning
                self._parent.do_parameter_adjustment(param, action_arg)

    def _adjust_pad_send(self, pads, action_arg, send):
        # type: (Sequence[Any], Text, Text) -> None
        '''Adjust/set pad send.'''
        try:
            for pad in pads:
                if pad.chains:
                    param = pad.chains[0].mixer_device.sends[ord(send) - 65]
                    self._parent.do_parameter_adjustment(param, action_arg)
        except:
            pass

    def _get_pads_to_operate_on(self, dr, pads):
        # type: (Any, Text) -> Sequence[Any]
        '''Get the Drum Rack pad or pads to operate on.'''
        pads_to_operate_on = [dr.view.selected_drum_pad]
        if pads == 'ALL':
            pads_to_operate_on = dr.visible_drum_pads
        elif pads:
            try:
                index = int(pads) - 1
                if 0 <= index < 16:
                    pads_to_operate_on = [dr.visible_drum_pads[index]]
            except:
                pass
        return pads_to_operate_on
# endregion
