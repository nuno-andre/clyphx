# coding: utf-8
from __future__ import absolute_import, unicode_literals
from builtins import super
from typing import TYPE_CHECKING
from functools import partial

if TYPE_CHECKING:
    from typing import Any, Text, List, Dict

from .base import XTrigger


class XCueComponent(XTrigger):
    '''Cue component that monitors cue points and calls main script on
    changes.
    '''
    __module__ = __name__

    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__(parent)
        self.song().add_current_song_time_listener(self.arrange_time_changed)
        self.song().add_is_playing_listener(self.arrange_time_changed)
        self.song().add_cue_points_listener(self.cue_points_changed)
        self._x_points = dict()  # type: Dict[Any, Any]
        self._x_point_time_to_watch_for = -1
        self._last_arrange_position = -1
        self._sorted_times = []  # type: List[Any]
        self.cue_points_changed()

    def disconnect(self):
        self.remove_cue_point_listeners()
        self.song().remove_current_song_time_listener(self.arrange_time_changed)
        self.song().remove_is_playing_listener(self.arrange_time_changed)
        self.song().remove_cue_points_listener(self.cue_points_changed)
        self._x_points = dict()
        super().disconnect()

    def cue_points_changed(self):
        '''Called on cue point changes to set up points to watch, cue
        points can't be named via the API so cue points can't perform
        any actions requiring naming.
        '''
        self.remove_cue_point_listeners()
        self._sorted_times = []
        for cp in self.song().cue_points:
            if not cp.time_has_listener(self.cue_points_changed):
                cp.add_time_listener(self.cue_points_changed)
            if not cp.name_has_listener(self.cue_points_changed):
                cp.add_name_listener(self.cue_points_changed)
            name = cp.name.upper()
            if len(name) > 2 and name[0] == '[' and name.count('[') == 1 and name.count(']') == 1:
                cue_name = name.replace(name[name.index('['):name.index(']')+1].strip(), '')
                self._x_points[cp.time] = cp
        self._sorted_times = sorted(self._x_points.keys())
        self.set_x_point_time_to_watch()

    def arrange_time_changed(self):
        '''Called on arrange time changed and schedules actions where
        necessary.
        '''
        if self.song().is_playing:
            if (self._x_point_time_to_watch_for != -1
                    and self._last_arrange_position < self.song().current_song_time):
                if (self.song().current_song_time >= self._x_point_time_to_watch_for and
                        self._x_point_time_to_watch_for < self._last_arrange_position):
                    self._parent.schedule_message(
                        1, partial(self.schedule_x_point_action_list, self._x_point_time_to_watch_for)
                    )
                    self._x_point_time_to_watch_for = -1
            else:
                self.set_x_point_time_to_watch()
        self._last_arrange_position = self.song().current_song_time

    def set_x_point_time_to_watch(self):
        '''Determine which cue point time to watch for next.'''
        if self._x_points:
            if self.song().is_playing:
                for t in self._sorted_times:
                    if t >= self.song().current_song_time:
                        self._x_point_time_to_watch_for = t
                        break
            else:
                self._x_point_time_to_watch_for = -1

    def schedule_x_point_action_list(self, point):
        self.handle_action_list(self.ref_track, self._x_points[point])

    def remove_cue_point_listeners(self):
        for cp in self.song().cue_points:
            if cp.time_has_listener(self.cue_points_changed):
                cp.remove_time_listener(self.cue_points_changed)
            if cp.name_has_listener(self.cue_points_changed):
                cp.remove_name_listener(self.cue_points_changed)
        self._x_points = dict()
        self._x_point_time_to_watch_for = -1
