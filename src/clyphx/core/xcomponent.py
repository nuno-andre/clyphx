from __future__ import absolute_import, unicode_literals
from typing import TYPE_CHECKING
from builtins import super
import logging

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SessionComponent import SessionComponent

if TYPE_CHECKING:
    from typing import Any, Text, Union
    from .live import Track

log = logging.getLogger(__name__)


class XComponent(ControlSurfaceComponent):
    '''Control Surface base component.
    '''
    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__()
        self._parent = parent

    # def __getattribute__(self, attr):
    #     log.debug('Get %s from %s', attr, self.__name__)
    #     return object.__getattribute__(self, attr)

    def disconnect(self):
        '''Called by the control surface on disconnect (app closed,
        script closed).
        '''
        log.debug('Disconnecting %s',
                  getattr(self, 'name', 'a {}'.format(self.__class__.name)))
        self._parent = None
        super().disconnect()

    def on_enabled_changed(self):
        '''Called when this script is enabled/disabled (by calling
        set_enabled on it).
        '''

    def _on_enabled_changed(self):
        super().update()

    def update(self):
        '''Called by the control surface on instantiation and in other
        cases such as when exiting MIDI map mode.
        '''

    def _update(self):
        super().update()

    @property
    def sel_track(self):
        # type: () -> Track
        return self.song().view.selected_track

    @sel_track.setter
    def sel_track(self, track):
        # type: (Track) -> None
        self.song().view.selected_track = track

    @property
    def sel_scene(self):
        # type: () -> int
        return list(self.song().scenes).index(self.song().view.selected_scene)

    @staticmethod
    def do_parameter_adjustment(param, value):
        # type: (DeviceParameter, Text) -> None
        '''Adjust (</>, reset, random, set val) continuous params, also
        handles quantized param adjustment (should just use +1/-1 for
        those).
        '''
        if not param.is_enabled:
            return
        step = (param.max - param.min) / 127
        new_value = param.value
        if value.startswith(('<', '>')):
            factor = XComponent.get_adjustment_factor(value)
            new_value += factor if param.is_quantized else (step * factor)
        elif value == 'RESET' and not param.is_quantized:
            new_value = param.default_value
        elif 'RND' in value and not param.is_quantized:
            rnd_min = 0
            rnd_max = 128
            if value != 'RND' and '-' in value:
                rnd_range_data = value.replace('RND', '').split('-')
                if len(rnd_range_data) == 2:
                    try:
                        new_min = int(rnd_range_data[0])
                    except Exception:
                        new_min = 0
                    try:
                        new_max = int(rnd_range_data[1]) + 1
                    except Exception:
                        new_max = 128
                    if 0 <= new_min and new_max <= 128 and new_min < new_max:
                        rnd_min = new_min
                        rnd_max = new_max
            rnd_value = (get_random_int(0, 128) * (rnd_max - rnd_min) / 127) + rnd_min
            new_value = (rnd_value * step) + param.min

        else:
            try:
                if 0 <= int(value) < 128:
                    try:
                        new_value = (int(value) * step) + param.min
                    except Exception:
                        new_value = param.value
            except Exception:
                pass
        if param.min <= new_value <= param.max:
            param.value = new_value
            log.debug('do_parameter_adjustment called on %s, set value to %s',
                      param.name, new_value)

    @staticmethod
    def get_adjustment_factor(string, as_float=False):
        # type: (Text, bool) -> Union[int, float]
        '''Get factor for use with < > actions.'''
        factor = 1

        if len(string) > 1:
            try:
                factor = (float if as_float else int)(string[1:])
            except Exception:
                factor = 1

        if string.startswith('<'):
            factor = -(factor)
        return factor
