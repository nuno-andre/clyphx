from __future__ import absolute_import, unicode_literals
from builtins import object
from typing import TYPE_CHECKING
import logging
from ..core.live import get_random_int

if TYPE_CHECKING:
    from typing import Optional, Text, Tuple
    from ..core.live import Clip

log = logging.getLogger(__name__)


class SceneMixin(object):

    def create_scene(self, track, xclip, value=None):
        # type: (None, Clip, Optional[Text]) -> None
        '''Creates scene at end of scene list or at the specified index.
        '''
        if isinstance(xclip, Clip):
            current_name = xclip.name
            xclip.name = ''
        else:
            current_name = None
        if value and value.strip():
            try:
                index = int(value) - 1
                if 0 <= index < len(self.song().scenes):
                    self.song().create_scene(index)
            except Exception as e:
                msg = "Failed to evaluate create_scene value '%s': {%r}"
                log.error(msg, value, e)
        else:
            self.song().create_scene(-1)
        if current_name:
            self._parent.schedule_message(
                4, partial(self.refresh_xclip_name, (xclip, current_name))
            )

    def duplicate_scene(self, track, xclip, args):
        # type: (None, Clip, Text) -> None
        '''Duplicates the given scene.'''
        if isinstance(xclip, Clip) and args:
            current_name = xclip.name
            xclip.name = ''
        else:
            current_name = None
        self.song().duplicate_scene(self.get_scene_to_operate_on(xclip, args.strip()))
        if current_name:
            self._parent.schedule_message(
                4, partial(self.refresh_xclip_name, (xclip, current_name))
            )

    def refresh_xclip_name(self, clip_info):
        # type: (Tuple[Clip, str]) -> None
        '''This is used for both dupe and create scene to prevent the
        action from getting triggered over and over again.
        '''
        if clip_info[0]:
            clip_info[0].name = clip_info[1]

    def delete_scene(self, track, xclip, args):
        # type: (None, Clip, Text) -> None
        '''Deletes the given scene as long as it's not the last scene in
        the set.
        '''
        if len(self.song().scenes) > 1:
            self.song().delete_scene(self.get_scene_to_operate_on(xclip, args.strip()))

    def set_scene(self, track, xclip, args):
        # type: (None, Clip, Text) -> None
        '''Sets scene to play (doesn't launch xclip).
        '''
        args = args.strip()
        scene = self.get_scene_to_operate_on(xclip, args)
        if args:
            # don't allow randomization unless more than 1 scene
            if 'RND' in args and len(self.song().scenes) > 1:
                num_scenes = len(self.song().scenes)
                rnd_range = [0, num_scenes]
                if '-' in args:
                    rnd_range_data = args.replace('RND', '').split('-')
                    if len(rnd_range_data) == 2:
                        try:
                            new_min = int(rnd_range_data[0]) - 1
                        except Exception:
                            new_min = 0
                        try:
                            new_max = int(rnd_range_data[1])
                        except Exception:
                            new_max = num_scenes
                        if 0 < new_min and new_max < num_scenes + 1 and new_min < new_max - 1:
                            rnd_range = [new_min, new_max]
                scene = get_random_int(0, rnd_range[1] - rnd_range[0]) + rnd_range[0]
                if scene == self._last_scene_index:
                    while scene == self._last_scene_index:
                        scene = get_random_int(0, rnd_range[1] - rnd_range[0]) + rnd_range[0]
            # don't allow adjustment unless more than 1 scene
            elif args.startswith(('<', '>')) and len(self.song().scenes) > 1:
                factor = self.get_adjustment_factor(args)
                if factor < len(self.song().scenes):
                    scene = self._last_scene_index + factor
                    if scene >= len(self.song().scenes):
                        scene -= len(self.song().scenes)
                    elif scene < 0 and abs(scene) >= len(self.song().scenes):
                        scene = -(abs(scene) - len(self.song().scenes))
        self._last_scene_index = scene
        for t in self.song().tracks:
            if not (t.is_foldable or (t.clip_slots[scene].has_clip
                    and t.clip_slots[scene].clip == xclip)):
                t.clip_slots[scene].fire()

    def get_scene_to_operate_on(self, xclip, args):
        # type: (Clip, Text) -> int
        if args == 'SEL' or not isinstance(xclip, Clip):
            scene = self.sel_scene
        else:
            scene = xclip.canonical_parent.canonical_parent.playing_slot_index

        if '"' in args:
            scene_name = args[args.index('"')+1:]
            if '"' in scene_name:
                scene_name = scene_name[0:scene_name.index('"')]
                for i, sc in enumerate(self.song().scenes):
                    if scene_name == sc.name.upper():
                        scene = i
                        break
                # for i in range(len(self.song().scenes)):
                #     if scene_name == self.song().scenes[i].name.upper():
                #         scene = i
                #         break
        elif args and args != 'SEL':
            try:
                if 0 <= int(args) < len(self.song().scenes) + 1:
                    scene = int(args) - 1
            except Exception:
                pass
        return scene

# region LISTENERS
    def on_scene_triggered(self, index):
        self._last_scene_index = index

    def on_scene_list_changed(self):
        self.setup_scene_listeners()

    def setup_scene_listeners(self):
        '''Setup listeners for all scenes in set and check that last
        index is in current scene range.
        '''
        self.remove_scene_listeners()
        scenes = self.song().scenes
        if not 0 < self._last_scene_index < len(scenes):
            self._last_scene_index = self.sel_scene
        for i, scene in enumerate(scenes):
            self._scenes_to_monitor.append(scene)
            listener = lambda index=i: self.on_scene_triggered(index)
            if not scene.is_triggered_has_listener(listener):
                scene.add_is_triggered_listener(listener)

    def remove_scene_listeners(self):
        for i, scene in enumerate(self._scenes_to_monitor):
            if scene:
                listener = lambda index=i: self.on_scene_triggered(index)
                if scene.is_triggered_has_listener(listener):
                    scene.remove_is_triggered_listener(listener)
        self._scenes_to_monitor = []
# endregion
