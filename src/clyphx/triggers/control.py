# coding: utf-8
from __future__ import absolute_import, unicode_literals
from builtins import super
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Text, Dict, Iterable, Sequence, List, Tuple
    from ..core.live import MidiRemoteScript

from .base import XTrigger, ActionList
from ..core.models import UserControl
from ..core.live import forward_midi_cc, forward_midi_note


class XControlComponent(XTrigger):
    '''A control on a MIDI controller.
    '''
    __module__ = __name__

    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__(parent)
        self._control_list = dict()  # type: Dict[Tuple[int, int], Dict[Text, Any]]
        self._xt_scripts = []  # type: List[Any]

    def disconnect(self):
        self._control_list = dict()
        self._xt_scripts = []
        super().disconnect()

    def connect_script_instances(self, instantiated_scripts):
        # type: (Iterable[MidiRemoteScript]) -> None
        '''Try to connect to ClyphX_XT instances.'''
        for i in range(5):
            try:
                if i == 0:
                    from ClyphX_XTA.ClyphX_XT import ClyphX_XT
                elif i == 1:
                    from ClyphX_XTB.ClyphX_XT import ClyphX_XT
                elif i == 2:
                    from ClyphX_XTC.ClyphX_XT import ClyphX_XT
                elif i == 3:
                    from ClyphX_XTD.ClyphX_XT import ClyphX_XT
                elif i == 4:
                    from ClyphX_XTE.ClyphX_XT import ClyphX_XT
                else:
                    continue
            except ImportError:
                pass
            else:
                if ClyphX_XT:
                    for i in instantiated_scripts:
                        if isinstance(i, ClyphX_XT) and not i in self._xt_scripts:
                            self._xt_scripts.append(i)
                            break

    def assign_new_actions(self, string):
        # type: (Text) -> None
        '''Assign new actions to controls via xclips.'''
        if self._xt_scripts:
            for x in self._xt_scripts:
                x.assign_new_actions(string)
        ident = string[string.index('[')+2:string.index(']')].strip()
        actions = string[string.index(']')+2:].strip()
        for c, v in self._control_list.items():
            if ident == v['ident']:
                new_actions = actions.split(',')
                on_action = '[{}] {}'.format(ident, new_actions[0])
                off_action = None
                if on_action and len(new_actions) > 1:
                    if new_actions[1].strip() == '*':
                        off_action = on_action
                    else:
                        off_action = '[{}] {}'.format(ident, new_actions[1])
                if on_action:
                    v['on_action'] = on_action
                    v['off_action'] = off_action
                break

    def receive_midi(self, bytes):
        # type: (Sequence[int]) -> None
        '''Receive user-defined midi messages.'''
        if self._control_list:
            ctrl_data = None
            if bytes[2] == 0 or bytes[0] < 144:
                if ((bytes[0], bytes[1]) in self._control_list.keys() and
                        self._control_list[(bytes[0], bytes[1])]['off_action']):
                    ctrl_data = self._control_list[(bytes[0], bytes[1])]
                elif ((bytes[0] + 16, bytes[1]) in self._control_list.keys() and
                        self._control_list[(bytes[0] + 16, bytes[1])]['off_action']):
                    ctrl_data = self._control_list[(bytes[0] + 16, bytes[1])]
                if ctrl_data:
                    ctrl_data['name'].name = ctrl_data['off_action']
            elif bytes[2] != 0 and (bytes[0], bytes[1]) in self._control_list.keys():
                ctrl_data = self._control_list[(bytes[0], bytes[1])]
                ctrl_data['name'].name = ctrl_data['on_action']
            if ctrl_data:
                self._parent.handle_action_list_trigger(self.song().view.selected_track,
                                                        ctrl_data['name'])

    def get_user_controls(self, settings, midi_map_handle):
        # type: (Dict[Text, Text], int) -> None
        self._control_list = dict()
        for name, data in settings.items():
            uc = UserControl.parse(name, data)
            self._control_list[uc._key] = dict(
                ident      = name,
                on_action  = uc.on_actions,
                off_action = uc.off_actions,
                name       = ActionList(uc.on_actions)
            )
            fn = forward_midi_note if uc.status_byte == 144 else forward_midi_cc
            fn(self._parent._c_instance.handle(), midi_map_handle, uc.channel, uc.value)

    def rebuild_control_map(self, midi_map_handle):
        # type: (int) -> None
        '''Called from main when build_midi_map is called.'''
        for key in self._control_list.keys():
            if key[0] >= 176:
                # forwards a CC msg to the receive_midi method
                forward_midi_cc(
                    self._parent._c_instance.handle(), midi_map_handle, key[0] - 176, key[1]
                )
            else:
                # forwards a NOTE msg to the receive_midi method
                forward_midi_note(
                    self._parent._c_instance.handle(), midi_map_handle, key[0] - 144, key[1]
                )
