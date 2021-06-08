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
from builtins import super, dict, range, map
from typing import TYPE_CHECKING
from functools import partial
from itertools import chain
import logging

if TYPE_CHECKING:
    from typing import (
        Any, Optional, Text,
        Iterable, Sequence, Tuple, List,
    )
    from ..core.live import Device, Scene, Track
    from ..core.legacy import _SingleDispatch

from ..core.xcomponent import XComponent
from ..core.live import Application, Clip, DeviceType
from ..consts import KEYWORDS, switch
from ..consts import (AUDIO_DEVS, MIDI_DEVS, INS_DEVS,
                      GQ_STATES, REPEAT_STATES, RQ_STATES,
                      MIDI_STATUS)
from .scene import SceneMixin

log = logging.getLogger(__name__)


class XGlobalActions(XComponent, SceneMixin):
    '''Global actions.
    '''
    __module__ = __name__

    def __init__(self, parent):
        # type: (Any) -> None
        super().__init__(parent)
        self._parent = parent
        self._last_gqntz = 4
        self._last_rqntz = 5
        self._repeat_enabled = False
        self._tempo_ramp_active = False
        self._tempo_ramp_settings = list()  # type: Sequence[Any]
        self._last_beat = -1
        self.song().add_current_song_time_listener(self.on_time_changed)
        self.song().add_is_playing_listener(self.on_time_changed)
        if self.song().clip_trigger_quantization != 0:
            self._last_gqntz = int(self.song().clip_trigger_quantization)
        if self.song().midi_recording_quantization != 0:
            self._last_rqntz = int(self.song().midi_recording_quantization)
        self._last_scene_index = self.sel_scene
        self._scenes_to_monitor = list()  # type: List[Scene]
        self.setup_scene_listeners()

    def disconnect(self):
        self.remove_scene_listeners()
        self.song().remove_current_song_time_listener(self.on_time_changed)
        self.song().remove_is_playing_listener(self.on_time_changed)
        for attr in ('_tempo_ramp_settings', '_scenes_to_monitor'):
            setattr(self, attr, None)
        super().disconnect()

    def dispatch_action(self, cmd):
        # type: (_SingleDispatch) -> None
        from .consts import GLOBAL_ACTIONS

        # if cmd.action_name == 'SCENE' and False:
        #     # TODO:
        #     # action = SCENE_ACTIONS[]
        #     pass
        # else:
        #     action = GLOBAL_ACTIONS[cmd.action_name]
        action = GLOBAL_ACTIONS[cmd.action_name]
        args = cmd.args.strip().split() if cmd.args and cmd.args.strip() else ()
        action(self, cmd.track, cmd.xclip, *args)

    def make_instant_mapping_docs(self, track, xclip, *args):
        # type: (None, Clip, None) -> None
        from ..instant_doc import InstantMappingMakeDoc
        InstantMappingMakeDoc()
        if isinstance(xclip, Clip):
            xclip.name = str(xclip.name).upper().replace('MAKE_DEV_DOC', 'Doc saved')

    def send_midi_message(self, track, xclip, *args):
        # type: (None, None, Text) -> None
        '''Send formatted NOTE/CC/PC message or raw MIDI message.'''
        message = []

        if len(args) >= 3 and args[0] in MIDI_STATUS:
            try:
                data_bytes = list(map(int, args[1:]))
            except Exception:
                pass
            else:
                if 1 <= data_bytes[0] < 17:
                    message = [MIDI_STATUS[args[0]] + data_bytes[0] - 1]
                    for byte in data_bytes[1:]:
                        if 0 <= byte < 128:
                            message.append(byte)
                    if ((args[0] != 'PC' and len(message) != 3) or
                            (args[0] == 'PC' and len(message) != 2)):
                        return
        elif len(args) >= 2:
            try:
                message = list(map(int, args))
            except Exception:
                pass

        if message:
            try:
                self._parent._send_midi(tuple(message))
                # send matching note off for note messages
                if args[0] == 'NOTE':
                    message[-1] = 0
                    self._parent.schedule_message(
                        1, partial(self._parent._send_midi, tuple(message))
                    )
            except Exception:
                pass

    def do_variable_assignment(self, track, xclip, name, start, length):
        # type: (None, None, Text) -> None
        '''Creates numbered variables for the name given in args from
        the offset given in args and in the quantity given in args.
        '''
        try:
            start = int(start)
            for i in range(int(length)):
                self._parent._user_variables['{}{}'.format(name, i + 1)] = str(i + start)
        except Exception:
            pass

# region TRACKS

    def create_audio_track(self, track, xclip, value=None):
        # type: (None, None, Optional[Text]) -> None
        '''Creates audio track at end of track list or at the specified
        index.
        '''
        if value:
            try:
                index = int(value) - 1
                if 0 <= index < len(self.song().tracks):
                    self.song().create_audio_track(index)
            except Exception as e:
                log.error('Error creating audio track: %r', e)
        else:
            self.song().create_audio_track(-1)

    def create_midi_track(self, track, xclip, value=None):
        # type: (None, None, None, Optional[Text]) -> None
        '''Creates MIDI track at end of track list or at the specified
        index.
        '''
        if value:
            try:
                index = int(value) - 1
                if 0 <= index < len(self.song().tracks):
                    self.song().create_midi_track(index)
            except Exception as e:
                log.error('Error creating MIDI track: %r', e)
        else:
            self.song().create_midi_track(-1)

    def create_return_track(self, track, xclip, *args):
        # type: (None, None, None) -> None
        '''Creates return track at end of return list.'''
        self.song().create_return_track()

    def insert_and_configure_audio_track(self, track, xclip, *args):
        # type: (None, None, None) -> None
        '''Inserts an audio track next to the selected track routed from
        the selected track and armed.
        '''
        self._insert_and_configure_track(is_midi=False)

    def insert_and_configure_midi_track(self, track, xclip, *args):
        # type: (None, None, None) -> None
        '''Inserts a midi track next to the selected track routed from
        the selected track and armed.
        '''
        self._insert_and_configure_track(is_midi=True)

    def _insert_and_configure_track(self, is_midi=False):
        # type: (bool) -> None
        '''Handles inserting tracks and configuring them. This method
        will only work if the selected track has the appropriate output/
        input for the insertion.
        '''
        sel_track = self.sel_track
        if is_midi and not sel_track.has_midi_input:
            return
        if not is_midi and not sel_track.has_audio_output:
            return
        try:
            index = list(self.song().tracks).index(sel_track) + 1
            if is_midi:
                self.song().create_midi_track(index)
            else:
                self.song().create_audio_track(index)
            new_track = self.song().tracks[index]
            new_track.name = 'From {}'.format(sel_track.name)
            new_track.current_input_routing = sel_track.name
            new_track.arm = True
        except Exception:
            pass

# endregion

    def swap_device_preset(self, track, xclip, *args):
        # type: (Track, None, Text) -> None
        '''Activates swapping for the selected device or swaps out the
        preset for the given device with the given preset or navigates
        forwards and back through presets.
        '''
        device = track.view.selected_device
        if device:
            if not args:
                self.application().view.toggle_browse()
            else:
                if self.application().view.browse_mode:
                    self.application().view.toggle_browse()
                tag_target = None
                dev_name = device.class_display_name

                if device.type == DeviceType.audio_effect:
                    tag_target = self.application().browser.audio_effects
                elif device.type == DeviceType.midi_effect:
                    tag_target = self.application().browser.midi_effects
                elif device.type == DeviceType.instrument:
                    tag_target = self.application().browser.instruments
                if tag_target:
                    for dev in tag_target.children:
                        if dev.name == dev_name:
                            self._handle_swapping(device, dev, *args)
                            break

    def _handle_swapping(self, device, browser_item, arg):
        # type: (Device, Any, Text) -> None
        dev_items = self._create_device_items(browser_item, [])
        if arg in ('<', '>'):
            factor = self.get_adjustment_factor(arg)
            index = self._get_current_preset_index(device, dev_items)
            new_index = index + factor
            if new_index > len(dev_items) - 1:
                new_index = 0
            elif new_index < 0:
                new_index = -1
            self._load_preset(dev_items[new_index])
        else:
            ext = 'ADG' if device.can_have_chains else 'ADV'
            arg = '{}.{}'.format(arg.upper(), ext)
            for item in dev_items:
                if item.name.upper() == arg:
                    self._load_preset(item)
                    break

    def _get_current_preset_index(self, device, presets):
        # type: (Device, Sequence[Any]) -> int
        '''Returns the index of the current preset (based on the
        device's name) in the presets list. Returns -1 if not found.
        '''
        current_preset_name = '{}.{}'.format(
            device.name, 'adg' if device.can_have_chains else 'adv'
        )

        for i, preset in enumerate(presets):
            if preset.name == current_preset_name:
                return i
        return -1

    def _load_preset(self, preset):
        '''Loads the given preset.'''
        self.application().view.toggle_browse()
        self.application().browser.load_item(preset)
        self.application().view.toggle_browse()

    def _create_device_items(self, device, item_array):
        # type: (Device, List[Any]) -> List[Any]
        '''Returns the array of loadable items for the given device and
        handles digging into sub-folders too.
        '''
        for item in device.children:
            if item.is_folder:
                self._create_device_items(item, item_array)
            elif item.is_loadable:
                item_array.append(item)
        return item_array

    def get_device(self, arg):
        if arg in AUDIO_DEVS:
            tag_target = self.application().browser.audio_effects
            name = AUDIO_DEVS[arg]
        elif arg in MIDI_DEVS:
            tag_target = self.application().browser.midi_effects
            name = MIDI_DEVS[arg]
        elif arg in INS_DEVS:
            tag_target = self.application().browser.instruments
            name = INS_DEVS[arg]
        else:
            log.warning("Device '%s' not found", arg)
            return

        for dev in tag_target.children:
            if dev.name == name:
                return dev
        else:
            log.warning("Device '%s' not found", name)

    def get_m4l_device(self, arg):
        if not arg.endswith('.AMXD'):
            arg = '{}.AMXD'.format(arg)
        for m in self.application().browser.max_for_live.children:
            for device in m.children:
                if device.is_folder:
                    for dev in device.children:
                        if dev.name.upper() == arg:
                            return dev
                elif device.name.upper() == arg:
                    return device
        else:
            log.warning('M4L device not found: %s', arg)

    def load_device(self, track, xclip, arg):
        # type: (None, None, Text) -> None
        '''Loads one of Live's built-in devices onto the selected Track.
        '''
        # XXX: using a similar method for loading plugins doesn't seem to work
        dev = self.get_device(arg)
        if dev is not None:
            self.application().browser.load_item(dev)

    def load_m4l(self, track, xclip, arg):
        # type: (None, None, Text) -> None
        '''Loads M4L device onto the selected Track. The .amxd should be
        omitted by the user.
        '''
        dev = self.get_m4l_device(arg.upper())
        if dev is not None:
            self.application().browser.load_item(dev)

    def set_session_record(self, track, xclip, value=None):
        # type: (None, None, Optional[Text]) -> None
        '''Toggles or turns on/off session record.'''
        switch(self.song(), 'session_record', value)

    def trigger_session_record(self, track, xclip, value=None):
        # type: (None, Clip, Optional[Text]) -> None
        '''Triggers session record in all armed tracks for the specified
        fixed length.
        '''
        if value:
            # the below fixes an issue where Live will crash instead of
            # creating a new scene when triggered via an X-Clip
            if isinstance(xclip, Clip):
                scene = list(xclip.canonical_parent.canonical_parent.clip_slots).index(xclip.canonical_parent)
                for t in self.song().tracks:
                    if t.can_be_armed and t.arm:
                        if not self._track_has_empty_slot(t, scene):
                            self.song().create_scene(-1)
                            break
            bar = (4.0 / self.song().signature_denominator) * self.song().signature_numerator
            try:
                length = float(value) * bar
            except Exception:
                length = bar
            self.song().trigger_session_record(length)

    def _track_has_empty_slot(self, track, start):
        # type: (Track, int) -> bool
        '''Returns whether the given track has an empty slot existing
        after the starting slot index.
        '''
        return any(not s.has_clip for s in track.clip_slots[start:])

    def set_session_automation_record(self, track, xclip, value=None):
        # type: (None, None, Optional[Text]) -> None
        '''Toggles or turns on/off session automation record.'''
        switch(self.song(), 'session_automation_record', value)

    def retrigger_recording_clips(self, track, xclip, value=None):
        # type: (Track, None, None) -> None
        '''Retriggers all clips that are currently recording.'''
        for track in self.song().tracks:
            if track.playing_slot_index >= 0:
                slot = track.clip_slots[track.playing_slot_index]
                if slot.has_clip and slot.clip.is_recording:
                    slot.fire()

    def set_back_to_arrange(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Triggers back to arrange button.'''
        self.song().back_to_arranger = 0

    def set_overdub(self, track, xclip, value=None):
        # type: (None, None, Optional[Text]) -> None
        '''Toggles or turns on/off overdub.'''
        switch(self.song(), 'overdub', value)

    def set_metronome(self, track, xclip, value=None):
        # type: (None, None, Optional[Text]) -> None
        '''Toggles or turns on/off metronome.'''
        switch(self.song(), 'metronome', value)

    def set_record(self, track, xclip, value=None):
        # type: (None, None, Optional[Text]) -> None
        '''Toggles or turns on/off record.'''
        switch(self.song(), 'record_mode', value)

    def set_punch_in(self, track, xclip, value=None):
        # type: (None, None, Optional[Text]) -> None
        '''Toggles or turns on/off punch in.'''
        switch(self.song(), 'punch_in', value)

    def set_punch_out(self, track, xclip, value=None):
        # type: (None, None, Optional[Text]) -> None
        '''Toggles or turns on/off punch out.'''
        switch(self.song(), 'punch_out', value)

    def restart_transport(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Restarts transport to 0.0'''
        self.song().current_song_time = 0

    def set_stop_transport(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Toggles transport.'''
        self.song().is_playing = not self.song().is_playing

    def set_continue_playback(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Continue playback from stop point.'''
        self.song().continue_playing()

    def set_stop_all(self, track, xclip, value=None):
        # type: (None, None, Optional[Text]) -> None
        '''Stop all clips w/no quantization option for Live 9.'''
        self.song().stop_all_clips((value or '').strip() != 'NQ')

    def set_tap_tempo(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Tap tempo.'''
        self.song().tap_tempo()

    def set_undo(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Triggers Live's undo.'''
        if self.song().can_undo:
            self.song().undo()

    def set_redo(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Triggers Live's redo.'''
        if self.song().can_redo:
            self.song().redo()

# region NAVIGATION

    def _move_nav(self, direction):
        # type: (int) -> None
        self.application().view.scroll_view(
            Application.View.NavDirection(direction), '', False
        )

    def move_up(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Scroll up.'''
        self._move_nav(0)

    def move_down(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Scroll down.'''
        self._move_nav(1)

    def move_left(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Scroll left.'''
        self._move_nav(2)

    def move_right(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Scroll right.'''
        self._move_nav(3)

    def show(self, what):
        # type: (Text) -> None
        self.application().view.show_view(what)

    def hide(self, what):
        # type: (Text) -> None
        self.application().view.hide_view(what)

    def focus(self, what):
        # type: (Text) -> None
        self.application().view.focus_view(what)

    # TODO: zoom, scroll

    def is_visible(self, what):
        # type: (Text) -> bool
        return self.application().view.is_view_visible(what)

    def move_to_first_device(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Move to the first device on the track and scroll the view.'''
        self.focus_devices()
        self.sel_track.view.select_instrument()

    def move_to_last_device(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Move to the last device on the track and scroll the view.'''
        self.focus_devices()
        if self.sel_track.devices:
            self.song().view.select_device(self.sel_track.devices[-1])
            # self.song().view.select_device(
            #     self.sel_track.devices[len(self.sel_track.devices) - 1]
            # )
            self.application().view.scroll_view(
                Application.View.NavDirection(3), 'Detail/DeviceChain', False
            )
            self.application().view.scroll_view(
                Application.View.NavDirection(2), 'Detail/DeviceChain', False
            )

    def move_to_prev_device(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Move to the previous device on the track.'''
        self.focus_devices()
        self.application().view.scroll_view(
            Application.View.NavDirection(2), 'Detail/DeviceChain', False
        )

    def move_to_next_device(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Move to the next device on the track.'''
        self.focus_devices()
        self.application().view.scroll_view(
            Application.View.NavDirection(3), 'Detail/DeviceChain', False
        )

    def focus_devices(self):
        '''Make sure devices are in focus and visible.'''
        self.show('Detail')
        self.show('Detail/DeviceChain')

    def show_clip_view(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Show clip view.'''
        self.show('Detail')
        self.show('Detail/Clip')

    def show_track_view(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Show track view.'''
        self.show('Detail')
        self.show('Detail/DeviceChain')

    def show_detail_view(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Toggle between showing/hiding detail view.'''
        if self.is_visible('Detail'):
            self.hide('Detail')
        else:
            self.show('Detail')

    def toggle_browser(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Hide/show browser and move focus to or from browser.'''
        if self.is_visible('Browser'):
            self.hide('Browser')
            self.focus('')
        else:
            self.show('Browser')
            self.focus('Browser')

    def toggle_detail_view(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Toggle between clip and track view.'''
        self.show('Detail')
        if self.is_visible('Detail/Clip'):
            self.show('Detail/DeviceChain')
        else:
            self.show('Detail/Clip')

    def toggle_main_view(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Toggle between session and arrange view.'''
        if self.is_visible('Session'):
            self.show('Arranger')
        else:
            self.show('Session')

    def focus_browser(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Move the focus to the browser, show browser first if
        necessary.
        '''
        if not self.is_visible('Browser'):
            self.show('Browser')
        self.focus('Browser')

    def focus_detail(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Move the focus to the detail view, show detail first if
        necessary.
        '''
        if not self.is_visible('Detail'):
            self.show('Detail')
        self.focus('Detail')

    def focus_main(self, track, xclip, value=None):
        # type: (None, None, None) -> None
        '''Move the focus to the main focu.'''
        self.focus('')

    def adjust_horizontal_zoom(self, track, xclip, value):
        # type: (None, None, Text) -> None
        '''Horizontally zoom in in Arrange the number of times specified
        in value. This can accept ALL, but doesn't have any bearing.
        '''
        zoom_all = 'ALL' in value
        value = value.replace('ALL', '').strip()
        try:
            val = int(value)
        except Exception:
            return
        else:
            # TODO
            direct = (val > 0) + 2
            for _ in range(abs(val) + 1):
                self.application().view.zoom_view(
                    Application.View.NavDirection(direct), '', zoom_all
                )

    def adjust_vertical_zoom(self, track, xclip, value):
        # type: (None, None, Text) -> None
        '''Vertically zoom in on the selected track in Arrange the
        number of times specified in value. This can accept ALL for
        zooming all tracks.
        '''
        zoom_all = 'ALL' in value
        value = value.replace('ALL', '').strip()  # type: Text
        try:
            v = int(value)  # type: int
        except Exception:
            return
        direct = (v > 0)
        for _ in range(abs(v) + 1):
            self.application().view.zoom_view(Application.View.NavDirection(direct), '', zoom_all)

# endregion

    def adjust_tempo(self, track, xclip, arg, *rest):
        # type: (None, None, Text) -> None
        '''Adjust/set tempo or apply smooth synced ramp.'''
        self._tempo_ramp_active = False
        self._tempo_ramp_settings = []
        if arg.startswith(('<', '>')):
            factor = self.get_adjustment_factor(arg, True)
            self.song().tempo = max(20, min(999, (self.song().tempo + factor)))
        elif arg.startswith('*'):
            try:
                self.song().tempo = max(20, min(999, (self.song().tempo * float(arg[1:]))))
            except Exception:
                pass
        elif arg.startswith('RAMP'):
            if len(rest) == 2:
                try:
                    if rest[1].startswith('*'):
                        target_tempo = max(20, min(999, (self.song().tempo * float(rest[1][1:]))))
                    else:
                        target_tempo = float("%.2f" % float(rest[1]))
                    if 20.0 <= target_tempo <= 999.0:
                        ramp_factor = float("%.2f" % (int(rest[0]) * self.song().signature_numerator))
                        self._tempo_ramp_settings = [target_tempo, (target_tempo - self.song().tempo) / ramp_factor]
                        self._tempo_ramp_active = True
                except Exception:
                    pass
        else:
            try:
                self.song().tempo = float(arg)
            except Exception:
                pass

    def on_time_changed(self):
        '''Smooth BPM changes synced to tempo.'''
        if self._tempo_ramp_active and self._tempo_ramp_settings and self.song().is_playing:
            time = int(str(self.song().get_current_beats_song_time()).split('.')[2])
            if self._last_beat != time:
                self._last_beat = time
                self._tasks.add(self.apply_tempo_ramp)

    def apply_tempo_ramp(self, arg=None):
        # type: (None) -> None
        '''Apply tempo smoothing.'''
        target_reached = False
        if self._tempo_ramp_settings[1] > 0:
            target_reached = self._tempo_ramp_settings[0] <= self.song().tempo
        else:
            target_reached = self._tempo_ramp_settings[0] >= self.song().tempo
        if target_reached:
            self.song().tempo = self._tempo_ramp_settings[0]
            self._tempo_ramp_active = False
            self._tasks.kill()
            self._tasks.clear()
        else:
            self.song().tempo += self._tempo_ramp_settings[1]

    def adjust_groove(self, track, xclip, arg):
        # type: (None, None, Text) -> None
        '''Adjust/set global groove.'''
        if arg.startswith(('<', '>')):
            factor = self.get_adjustment_factor(arg, True)
            self.song().groove_amount = max(0.0, min(1.3125, self.song().groove_amount + factor * float(1.3125 / 131.0)))
        else:
            try:
                self.song().groove_amount = int(arg) * float(1.3125 / 131.0)
            except Exception:
                pass

    def set_note_repeat(self, track, xclip, arg=None):
        # type: (None, None, Text) -> None
        '''Set/toggle note repeat.'''
        if arg == 'OFF':
            self._parent._c_instance.note_repeat.enabled = False
            self._repeat_enabled = False
        elif arg in REPEAT_STATES:
            self._parent._c_instance.note_repeat.repeat_rate = REPEAT_STATES[arg]
            self._parent._c_instance.note_repeat.enabled = True
            self._repeat_enabled = True
        else:
            self._repeat_enabled = not self._repeat_enabled
            self._parent._c_instance.note_repeat.enabled = self._repeat_enabled

    def adjust_swing(self, track, xclip, arg):
        # type: (None, None, Text) -> None
        '''Adjust swing amount for use with note repeat.'''
        if arg.startswith(('<', '>')):
            factor = self.get_adjustment_factor(arg, True)
            self.song().swing_amount = max(0.0, min(1.0, (self.song().swing_amount + factor * 0.01)))
        else:
            try:
                self.song().swing_amount = int(arg) * 0.01
            except Exception:
                pass

    def adjust_global_quantize(self, track, xclip, arg=None):
        # type: (None, None, Text) -> None
        '''Adjust/set/toggle global quantization.'''
        if arg in GQ_STATES:
            self.song().clip_trigger_quantization = GQ_STATES[arg]
        elif arg.startswith(('<', '>')):
            factor = self.get_adjustment_factor(arg)
            new_gq = self.song().clip_trigger_quantization + factor
            if 0 <= new_gq < 14:
                self.song().clip_trigger_quantization = new_gq
        elif self.song().clip_trigger_quantization != 0:
            self._last_gqntz = int(self.song().clip_trigger_quantization)
            self.song().clip_trigger_quantization = 0
        else:
            self.song().clip_trigger_quantization = self._last_gqntz

    def adjust_record_quantize(self, track, xclip, arg):
        # type: (None, None, Text) -> None
        '''Adjust/set/toggle record quantization.'''
        if arg in RQ_STATES:
            self.song().midi_recording_quantization = RQ_STATES[arg]
        elif arg.startswith(('<', '>')):
            factor = self.get_adjustment_factor(arg)
            new_rq = self.song().midi_recording_quantization + factor
            if 0 <= new_rq < 9:
                self.song().midi_recording_quantization = new_rq
        elif self.song().midi_recording_quantization != 0:
            self._last_rqntz = int(self.song().midi_recording_quantization)
            self.song().midi_recording_quantization = 0
        else:
            self.song().midi_recording_quantization = self._last_rqntz

    def adjust_time_signature(self, track, xclip, arg):
        # type: (None, None, Text) -> None
        '''Adjust global time signature.'''
        try:
            num, denom = map(int, arg.split('/'))
            self.song().signature_numerator = num
            self.song().signature_denominator = denom
        except Exception as e:
            log.error("Failed to set time signature '%s': %r", arg, e)

    def set_jump_all(self, track, xclip, arg):
        # type: (None, None, Text) -> None
        '''Jump arrange position forward/backward.'''
        try:
            self.song().jump_by(float(arg))
        except Exception:
            pass

    # TODO: to track actions
    def set_unarm_all(self, track, xclip, *args):
        # type: (None, None, None) -> None
        '''Unarm all armable track.'''
        for t in self.song().tracks:
            if t.can_be_armed and t.arm:
                t.arm = 0

    # TODO: to track actions
    def set_unmute_all(self, track, xclip, *args):
        # type: (None, None, None) -> None
        '''Unmute all track.'''
        for t in chain(self.song().tracks, self.song().return_tracks):
            if t.mute:
                t.mute = 0

    # TODO: to track actions
    def set_unsolo_all(self, track, xclip, *args):
        # type: (None, None, None) -> None
        '''Unsolo all track.'''
        for t in chain(self.song().tracks, self.song().return_tracks):
            if t.solo:
                t.solo = 0

    # TODO: to track actions
    def set_fold_all(self, track, xclip, value):
        # type: (None, None, None) -> None
        '''Toggle or turn/on fold for all track.'''
        state_to_set = None
        for t in self.song().tracks:
            if t.is_foldable:
                if state_to_set is None:
                    state_to_set = not t.fold_state
                switch(t, 'fold_state', value, state_to_set)

    def set_locator(self, track, xclip, *args):
        # type: (None, None, None) -> None
        '''Set/delete a locator at the current playback position.'''
        self.song().set_or_delete_cue()

    def do_locator_loop_action(self, track, xclip, arg):
        # type: (None, None, Text) -> None
        '''Same as do_locator_action with name argument, but also sets
        arrangement loop start to pos of locator.
        '''
        self.do_locator_action(track, xclip, arg, True)

    def do_locator_action(self, track, xclip, arg, move_loop_too=False):
        # type: (None, None, Text, bool) -> None
        '''Jump between locators or to a particular locator. Can also
        move loop start to pos of locator if specified.
        '''
        if arg == '>' and self.song().can_jump_to_next_cue:
            self.song().jump_to_next_cue()
        elif arg == '<' and self.song().can_jump_to_prev_cue:
            self.song().jump_to_prev_cue()
        else:
            try:
                for cp in self.song().cue_points:
                    if cp.name.upper() == arg:
                        cp.jump()
                        if move_loop_too:
                            self.song().loop_start = cp.time
                        break
            except Exception:
                pass

    def do_loop_action(self, track, xclip, arg=None):
        # type: (None, None, Text) -> None
        '''Handle arrange loop action.'''
        if not arg or arg.upper() in KEYWORDS:
            self.set_loop_on_off(arg)
        else:
            new_start = self.song().loop_start
            new_length = self.song().loop_length
            if arg.startswith(('<', '>')):
                self.move_loop_by_factor(arg)
                return
            elif arg == 'RESET':
                new_start = 0
            elif arg.startswith('*'):
                try:
                    new_length = self.song().loop_length * float(arg[1:])
                except Exception:
                    pass
            else:
                try:
                    # TODO: int?
                    new_length = float(arg) * (
                        (4.0 / self.song().signature_denominator)
                        * self.song().signature_numerator
                    )
                except Exception:
                    pass
            self.set_new_loop_position(new_start, new_length)

    def set_loop_on_off(self, value=None):
        # type: (Optional[Text]) -> None
        '''Toggles or turns on/off arrange loop.'''
        switch(self.song(), 'loop', value)

    def move_loop_by_factor(self, arg):
        # type: (Text) -> None
        '''Move arrangement loop by its length or by a specified factor.
        '''
        factor = self.song().loop_length
        if arg == '<':
            factor = -(factor)
        elif len(ars) > 1:
            factor = self.get_adjustment_factor(arg, True)
        new_start = self.song().loop_start + factor
        if new_start < 0.0:
            new_start = 0.0
        self.set_new_loop_position(new_start, self.song().loop_length)

    def set_new_loop_position(self, new_start, new_length):
        # type: (float, float) -> None
        '''For use with other loop actions, ensures that loop settings
        are within range.
        '''
        # TODO: maybe (new_start + new_length < self.song().song_length) ?
        if 0 <= new_start and 0 <= new_length <= self.song().song_length:
            self.song().loop_start = new_start
            self.song().loop_length = new_length
