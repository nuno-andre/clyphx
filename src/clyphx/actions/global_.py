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
from ..core.live import Application, Clip, DeviceType, get_random_int
from ..consts import KEYWORDS
from ..consts import (AUDIO_DEVS, MIDI_DEVS, INS_DEVS,
                      GQ_STATES, REPEAT_STATES, RQ_STATES,
                      MIDI_STATUS)

log = logging.getLogger(__name__)


class XGlobalActions(XComponent):
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
        self._last_scene_index = list(self.song().scenes).index(self.song().view.selected_scene)
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

        action = GLOBAL_ACTIONS[cmd.action_name]
        action(self, cmd.track, cmd.xclip, cmd.ident, cmd.args)

    def on_scene_triggered(self, index):
        self._last_scene_index = index

    def on_scene_list_changed(self):
        self.setup_scene_listeners()

    def make_instant_mapping_docs(self, track, xclip, ident, args):
        # type: (None, Clip, None, Text) -> None
        from ..instant_doc import InstantMappingMakeDoc
        InstantMappingMakeDoc()
        if isinstance(xclip, Clip):
            xclip.name = str(xclip.name).upper().replace('MAKE_DEV_DOC', 'Doc saved')

    def send_midi_message(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Send formatted NOTE/CC/PC message or raw MIDI message.'''
        message = []
        if args:
            byte_array = args.split()
            if len(byte_array) >= 3 and byte_array[0] in MIDI_STATUS:
                try:
                    data_bytes = list(map(int, byte_array[1:]))
                except:
                    pass
                else:
                    if 1 <= data_bytes[0] < 17:
                        message = [MIDI_STATUS[byte_array[0]] + data_bytes[0] - 1]
                        for byte in data_bytes[1:]:
                            if 0 <= byte < 128:
                                message.append(byte)
                        if ((byte_array[0] != 'PC' and len(message) != 3) or
                                (byte_array[0] == 'PC' and len(message) != 2)):
                            return
            elif len(byte_array) >= 2:
                try:
                    message = list(map(int, byte_array))
                except:
                    pass
            if message:
                try:
                    self._parent._send_midi(tuple(message))
                    # send matching note off for note messages
                    if byte_array[0] == 'NOTE':
                        message[-1] = 0
                        self._parent.schedule_message(
                            1, partial(self._parent._send_midi, tuple(message))
                        )
                except:
                    pass

    def do_variable_assignment(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Creates numbered variables for the name given in args from
        the offset given in args and in the quantity given in args.
        '''
        args = args.strip()
        arg_array = args.split()
        if len(arg_array) == 3:
            try:
                start = int(arg_array[1])
                length = int(arg_array[2])
                for i in range(length):
                    self._parent._user_variables[arg_array[0] + str(i + 1)] = str(i + start)
            except:
                pass

# region TRACKS

    def create_audio_track(self, track, xclip, ident, value=None):
        # type: (None, None, None, Optional[Text]) -> None
        '''Creates audio track at end of track list or at the specified
        index.
        '''
        if value and value.strip():
            try:
                index = int(value) - 1
                if 0 <= index < len(self.song().tracks):
                    self.song().create_audio_track(index)
            except Exception as e:
                log.error('Error creating audio track: %r', e)
        else:
            self.song().create_audio_track(-1)

    def create_midi_track(self, track, xclip, ident, value=None):
        # type: (None, None, None, Optional[Text]) -> None
        '''Creates MIDI track at end of track list or at the specified
        index.
        '''
        if value and value.strip():
            try:
                index = int(value) - 1
                if 0 <= index < len(self.song().tracks):
                    self.song().create_midi_track(index)
            except Exception as e:
                log.error('Error creating MIDI track: %r', e)
        else:
            self.song().create_midi_track(-1)

    def create_return_track(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Creates return track at end of return list.'''
        self.song().create_return_track()

    def insert_and_configure_audio_track(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Inserts an audio track next to the selected track routed from
        the selected track and armed.
        '''
        self._insert_and_configure_track(is_midi=False)

    def insert_and_configure_midi_track(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
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
        sel_track = self.song().view.selected_track
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
        except:
            pass

# endregion

    def swap_device_preset(self, track, xclip, ident, args):
        # type: (Track, None, None, Text) -> None
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
                args = args.strip()
                if device.type == DeviceType.audio_effect:
                    tag_target = self.application().browser.audio_effects
                elif device.type == DeviceType.midi_effect:
                    tag_target = self.application().browser.midi_effects
                elif device.type == DeviceType.instrument:
                    tag_target = self.application().browser.instruments
                if tag_target:
                    for dev in tag_target.children:
                        if dev.name == dev_name:
                            self._handle_swapping(device, dev, args)
                            break

    def _handle_swapping(self, device, browser_item, args):
        # type: (Device, Any, Text) -> None
        dev_items = self._create_device_items(browser_item, [])
        if args in ('<', '>'):
            factor = self._parent.get_adjustment_factor(args)
            index = self._get_current_preset_index(device, dev_items)
            new_index = index + factor
            if new_index > len(dev_items) - 1:
                new_index = 0
            elif new_index < 0:
                new_index = -1
            self._load_preset(dev_items[new_index])
        else:
            args += '.ADG' if device.can_have_chains else '.ADV'
            for item in dev_items:
                if item.name.upper() == args:
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

    def load_device(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Loads one of Live's built-in devices onto the selected Track.
        '''
        # XXX: using a similar method for loading plugins doesn't seem to work!
        args = args.strip()

        if args in AUDIO_DEVS:
            tag_target = self.application().browser.audio_effects
            name = AUDIO_DEVS[args]
        elif args in MIDI_DEVS:
            tag_target = self.application().browser.midi_effects
            name = MIDI_DEVS[args]
        elif args in INS_DEVS:
            tag_target = self.application().browser.instruments
            name = INS_DEVS[args]
        else:
            log.warning("Device '%s' not found", args)
            return

        for dev in tag_target.children:
            if dev.name == name:
                self.application().browser.load_item(dev)
                break

    def load_m4l(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Loads M4L device onto the selected Track. The .amxd should be
        omitted by the user.
        '''
        args = '{}.AMXD'.format(args.strip())
        found_dev = False
        for m in self.application().browser.max_for_live.children:
            for device in m.children:
                if device.is_folder:
                    for dev in device.children:
                        if dev.name.upper() == args:
                            found_dev = dev
                            break
                elif device.name.upper() == args:
                    found_dev = device
                if found_dev:
                    self.application().browser.load_item(found_dev)
                    break

    def set_session_record(self, track, xclip, ident, value=None):
        # type: (None, None, None, Optional[Text]) -> None
        '''Toggles or turns on/off session record.'''
        self.song().session_record = KEYWORDS.get(value, not self.song().session_record)

    def trigger_session_record(self, track, xclip, ident, value=None):
        # type: (None, Clip, None, Optional[Text]) -> None
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
            except:
                length = bar
            self.song().trigger_session_record(length)

    def _track_has_empty_slot(self, track, start):
        # type: (Track, int) -> bool
        '''Returns whether the given track has an empty slot existing
        after the starting slot index.
        '''
        for s in track.clip_slots[start:]:
            if not s.has_clip:
                return True
        return False

    def set_session_automation_record(self, track, xclip, ident, value=None):
        # type: (None, None, None, Optional[Text]) -> None
        '''Toggles or turns on/off session automation record.'''
        self.song().session_automation_record = KEYWORDS.get(
            value, not self.song().session_automation_record
        )

    def retrigger_recording_clips(self, track, xclip, ident, value=None):
        # type: (Track, None, None, None) -> None
        '''Retriggers all clips that are currently recording.'''
        for track in self.song().tracks:
            if track.playing_slot_index >= 0:
                slot = track.clip_slots[track.playing_slot_index]
                if slot.has_clip and slot.clip.is_recording:
                    slot.fire()

    def set_back_to_arrange(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Triggers back to arrange button.'''
        self.song().back_to_arranger = 0

    def set_overdub(self, track, xclip, ident, value=None):
        # type: (None, None, None, Optional[Text]) -> None
        '''Toggles or turns on/off overdub.'''
        self.song().overdub = KEYWORDS.get(value, not self.song().overdub)

    def set_metronome(self, track, xclip, ident, value=None):
        # type: (None, None, None, Optional[Text]) -> None
        '''Toggles or turns on/off metronome.'''
        self.song().metronome = KEYWORDS.get(value, not self.song().metronome)

    def set_record(self, track, xclip, ident, value=None):
        # type: (None, None, None, Optional[Text]) -> None
        '''Toggles or turns on/off record.'''
        self.song().record_mode = KEYWORDS.get(value, not self.song().record_mode)

    def set_punch_in(self, track, xclip, ident, value=None):
        # type: (None, None, None, Optional[Text]) -> None
        '''Toggles or turns on/off punch in.'''
        self.song().punch_in = KEYWORDS.get(value, not self.song().punch_in)

    def set_punch_out(self, track, xclip, ident, value=None):
        # type: (None, None, None, Optional[Text]) -> None
        '''Toggles or turns on/off punch out.'''
        self.song().punch_out = KEYWORDS.get(value, not self.song().punch_out)

    def restart_transport(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Restarts transport to 0.0'''
        self.song().current_song_time = 0

    def set_stop_transport(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Toggles transport.'''
        self.song().is_playing = not self.song().is_playing

    def set_continue_playback(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Continue playback from stop point.'''
        self.song().continue_playing()

    def set_stop_all(self, track, xclip, ident, value=None):
        # type: (None, None, None, Optional[Text]) -> None
        '''Stop all clips w/no quantization option for Live 9.'''
        self.song().stop_all_clips((value or '').strip() != 'NQ')

    def set_tap_tempo(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Tap tempo.'''
        self.song().tap_tempo()

    def set_undo(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Triggers Live's undo.'''
        if self.song().can_undo:
            self.song().undo()

    def set_redo(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Triggers Live's redo.'''
        if self.song().can_redo:
            self.song().redo()

# region NAVIGATION

    def move_up(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Scroll up.'''
        self._move_nav(0)

    def move_down(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Scroll down.'''
        self._move_nav(1)

    def move_left(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Scroll left.'''
        self._move_nav(2)

    def move_right(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Scroll right.'''
        self._move_nav(3)

    def _move_nav(self, direction):
        # type: (int) -> None
        self.application().view.scroll_view(
            Application.View.NavDirection(direction), '', False
        )

    def move_to_first_device(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Move to the first device on the track and scroll the view.'''
        self.focus_devices()
        self.song().view.selected_track.view.select_instrument()

    def move_to_last_device(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Move to the last device on the track and scroll the view.'''
        self.focus_devices()
        if self.song().view.selected_track.devices:
            self.song().view.select_device(
                self.song().view.selected_track.devices[len(self.song().view.selected_track.devices) - 1]
            )
            self.application().view.scroll_view(
                Application.View.NavDirection(3), 'Detail/DeviceChain', False
            )
            self.application().view.scroll_view(
                Application.View.NavDirection(2), 'Detail/DeviceChain', False
            )

    def move_to_prev_device(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Move to the previous device on the track.'''
        self.focus_devices()
        self.application().view.scroll_view(
            Application.View.NavDirection(2), 'Detail/DeviceChain', False
        )

    def move_to_next_device(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Move to the next device on the track.'''
        self.focus_devices()
        self.application().view.scroll_view(
            Application.View.NavDirection(3), 'Detail/DeviceChain', False
        )

    def focus_devices(self):
        '''Make sure devices are in focus and visible.'''
        self.application().view.show_view('Detail')
        self.application().view.show_view('Detail/DeviceChain')

    def show_clip_view(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Show clip view.'''
        self.application().view.show_view('Detail')
        self.application().view.show_view('Detail/Clip')

    def show_track_view(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Show track view.'''
        self.application().view.show_view('Detail')
        self.application().view.show_view('Detail/DeviceChain')

    def show_detail_view(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Toggle between showing/hiding detail view.'''
        if self.application().view.is_view_visible('Detail'):
            self.application().view.hide_view('Detail')
        else:
            self.application().view.show_view('Detail')

    def toggle_browser(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Hide/show browser and move focus to or from browser.'''
        if self.application().view.is_view_visible('Browser'):
            self.application().view.hide_view('Browser')
            self.application().view.focus_view('')
        else:
            self.application().view.show_view('Browser')
            self.application().view.focus_view('Browser')

    def toggle_detail_view(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Toggle between clip and track view.'''
        self.application().view.show_view('Detail')
        if self.application().view.is_view_visible('Detail/Clip'):
            self.application().view.show_view('Detail/DeviceChain')
        else:
            self.application().view.show_view('Detail/Clip')

    def toggle_main_view(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Toggle between session and arrange view.'''
        if self.application().view.is_view_visible('Session'):
            self.application().view.show_view('Arranger')
        else:
            self.application().view.show_view('Session')

    def focus_browser(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Move the focus to the browser, show browser first if
        necessary.
        '''
        if not self.application().view.is_view_visible('Browser'):
            self.application().view.show_view('Browser')
        self.application().view.focus_view('Browser')

    def focus_detail(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Move the focus to the detail view, show detail first if
        necessary.
        '''
        if not self.application().view.is_view_visible('Detail'):
            self.application().view.show_view('Detail')
        self.application().view.focus_view('Detail')

    def focus_main(self, track, xclip, ident, value=None):
        # type: (None, None, None, None) -> None
        '''Move the focus to the main focu.'''
        self.application().view.focus_view('')

    def adjust_horizontal_zoom(self, track, xclip, ident, value):
        # type: (None, None, None, Text) -> None
        '''Horizontally zoom in in Arrange the number of times specified
        in value. This can accept ALL, but doesn't have any bearing.
        '''
        zoom_all = 'ALL' in value
        value = value.replace('ALL', '').strip()
        try:
            val = int(value)
        except:
            return
        else:
            # TODO
            direct = (val > 0) + 2
            for _ in range(abs(val) + 1):
                self.application().view.zoom_view(
                    Application.View.NavDirection(direct), '', zoom_all
                )

    def adjust_vertical_zoom(self, track, xclip, ident, value):
        # type: (None, None, None, Text) -> None
        '''Vertically zoom in on the selected track in Arrange the
        number of times specified in value. This can accept ALL for
        zooming all tracks.
        '''
        zoom_all = 'ALL' in value
        value = value.replace('ALL', '').strip()  # type: Text
        try:
            v = int(value)  # type: int
        except:
            return
        direct = (v > 0)
        for _ in range(abs(v) + 1):
            self.application().view.zoom_view(Application.View.NavDirection(direct), '', zoom_all)

# endregion

    def adjust_tempo(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Adjust/set tempo or apply smooth synced ramp.'''
        self._tempo_ramp_active = False
        self._tempo_ramp_settings = []
        args = args.strip()
        if args.startswith(('<', '>')):
            factor = self._parent.get_adjustment_factor(args, True)
            self.song().tempo = max(20, min(999, (self.song().tempo + factor)))
        elif args.startswith('*'):
            try:
                self.song().tempo = max(20, min(999, (self.song().tempo * float(args[1:]))))
            except:
                pass
        elif args.startswith('RAMP'):
            arg_array = args.split()
            if len(arg_array) == 3:
                try:
                    ramp_factor = float("%.2f" % (int(arg_array[1]) * self.song().signature_numerator))
                    if arg_array[2].startswith('*'):
                        target_tempo = max(20, min(999, (self.song().tempo * float(arg_array[2][1:]))))
                    else:
                        target_tempo = float("%.2f" % float(arg_array[2]))
                    if target_tempo >= 20.0 and target_tempo <= 999.0:
                        self._tempo_ramp_settings = [target_tempo, (target_tempo - self.song().tempo) / ramp_factor]
                        self._tempo_ramp_active = True
                except:
                    pass
        else:
            try:
                self.song().tempo = float(args)
            except:
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

    def adjust_groove(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Adjust/set global groove.'''
        args = args.strip()
        if args.startswith(('<', '>')):
            factor = self._parent.get_adjustment_factor(args, True)
            self.song().groove_amount = max(0.0, min(1.3125, self.song().groove_amount + factor * float(1.3125 / 131.0)))
        else:
            try:
                self.song().groove_amount = int(args) * float(1.3125 / 131.0)
            except:
                pass

    def set_note_repeat(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Set/toggle note repeat.'''
        args = args.strip()
        if args == 'OFF':
            self._parent._c_instance.note_repeat.enabled = False
            self._repeat_enabled = False
        elif args in REPEAT_STATES:
            self._parent._c_instance.note_repeat.repeat_rate = REPEAT_STATES[args]
            self._parent._c_instance.note_repeat.enabled = True
            self._repeat_enabled = True
        else:
            self._repeat_enabled = not self._repeat_enabled
            self._parent._c_instance.note_repeat.enabled = self._repeat_enabled

    def adjust_swing(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Adjust swing amount for use with note repeat.'''
        args = args.strip()
        if args.startswith(('<', '>')):
            factor = self._parent.get_adjustment_factor(args, True)
            self.song().swing_amount = max(0.0, min(1.0, (self.song().swing_amount + factor * 0.01)))
        else:
            try:
                self.song().swing_amount = int(args) * 0.01
            except:
                pass

    def adjust_global_quantize(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Adjust/set/toggle global quantization.'''
        args = args.strip()
        if args in GQ_STATES:
            self.song().clip_trigger_quantization = GQ_STATES[args]
        elif args in ('<', '>'):
            factor = self._parent.get_adjustment_factor(args)
            new_gq = self.song().clip_trigger_quantization + factor
            if 0 <= new_gq < 14:
                self.song().clip_trigger_quantization = new_gq
        elif self.song().clip_trigger_quantization != 0:
            self._last_gqntz = int(self.song().clip_trigger_quantization)
            self.song().clip_trigger_quantization = 0
        else:
            self.song().clip_trigger_quantization = self._last_gqntz

    def adjust_record_quantize(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Adjust/set/toggle record quantization.'''
        args = args.strip()
        if args in RQ_STATES:
            self.song().midi_recording_quantization = RQ_STATES[args]
        elif args in ('<', '>'):
            factor = self._parent.get_adjustment_factor(args)
            new_rq = self.song().midi_recording_quantization + factor
            if 0 <= new_rq < 9:
                self.song().midi_recording_quantization = new_rq
        elif self.song().midi_recording_quantization != 0:
            self._last_rqntz = int(self.song().midi_recording_quantization)
            self.song().midi_recording_quantization = 0
        else:
            self.song().midi_recording_quantization = self._last_rqntz

    def adjust_time_signature(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Adjust global time signature.'''
        if '/' in args:
            try:
                num, denom = args.split('/')
                self.song().signature_numerator = int(num)
                self.song().signature_denominator = int(denom)
            except:
                pass

    def set_jump_all(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Jump arrange position forward/backward.'''
        try:
            self.song().jump_by(float(args))
        except:
            pass

    def set_unarm_all(self, track, xclip, ident, args):
        # type: (None, None, None, None) -> None
        '''Unarm all armable track.'''
        for t in self.song().tracks:
            if t.can_be_armed and t.arm:
                t.arm = 0

    def set_unmute_all(self, track, xclip, ident, args):
        # type: (None, None, None, None) -> None
        '''Unmute all track.'''
        for t in chain(self.song().tracks, self.song().return_tracks):
            if t.mute:
                t.mute = 0

    def set_unsolo_all(self, track, xclip, ident, args):
        # type: (None, None, None, None) -> None
        '''Unsolo all track.'''
        for t in chain(self.song().tracks, self.song().return_tracks):
            if t.solo:
                t.solo = 0

    def set_fold_all(self, track, xclip, ident, value):
        # type: (None, None, None, None) -> None
        '''Toggle or turn/on fold for all track.'''
        state_to_set = None
        for t in self.song().tracks:
            if t.is_foldable:
                if state_to_set is None:
                    state_to_set = not t.fold_state
                t.fold_state = KEYWORDS.get(value, state_to_set)

    def set_locator(self, track, xclip, ident, args):
        # type: (None, None, None, None) -> None
        '''Set/delete a locator at the current playback position.'''
        self.song().set_or_delete_cue()

    def do_locator_loop_action(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Same as do_locator_action with name argument, but also sets
        arrangement loop start to pos of locator.
        '''
        self.do_locator_action(track, xclip, ident, args, True)

    def do_locator_action(self, track, xclip, ident, args, move_loop_too=False):
        # type: (None, None, None, Text, bool) -> None
        '''Jump between locators or to a particular locator. Can also
        move loop start to pos of locator if specified.
        '''
        args = args.strip()
        if args == '>' and self.song().can_jump_to_next_cue:
            self.song().jump_to_next_cue()
        elif args == '<' and self.song().can_jump_to_prev_cue:
            self.song().jump_to_prev_cue()
        else:
            try:
                for cp in self.song().cue_points:
                    if cp.name.upper() == args:
                        cp.jump()
                        if move_loop_too:
                            self.song().loop_start = cp.time
                        break
            except:
                pass

    def do_loop_action(self, track, xclip, ident, args):
        # type: (None, None, None, Text) -> None
        '''Handle arrange loop action.'''
        args = args.strip()
        if not args or args in KEYWORDS:
            self.set_loop_on_off(args)
        else:
            new_start = self.song().loop_start
            new_length = self.song().loop_length
            if args.startswith(('<', '>')):
                self.move_loop_by_factor(args)
                return
            elif args == 'RESET':
                new_start = 0
            elif args.startswith('*'):
                try:
                    new_length = self.song().loop_length * float(args[1:])
                except:
                    pass
            else:
                try:
                    # TODO: int?
                    new_length = float(args) * (
                        (4.0 / self.song().signature_denominator)
                        * self.song().signature_numerator
                    )
                except:
                    pass
            self.set_new_loop_position(new_start, new_length)

    def set_loop_on_off(self, value=None):
        # type: (Optional[Text]) -> None
        '''Toggles or turns on/off arrange loop.'''
        self.song().loop = KEYWORDS.get(value, not self.song().loop)

    def move_loop_by_factor(self, args):
        # type: (Text) -> None
        '''Move arrangement loop by its length or by a specified factor.
        '''
        factor = self.song().loop_length
        if args == '<':
            factor = -(factor)
        elif len(args) > 1:
            factor = self._parent.get_adjustment_factor(args, True)
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
        if new_start >= 0 and new_length >= 0 and new_length <= self.song().song_length:
            self.song().loop_start = new_start
            self.song().loop_length = new_length

# region SCENES

    def create_scene(self, track, xclip, ident, value=None):
        # type: (None, Clip, None, Optional[Text]) -> None
        '''Creates scene at end of scene list or at the specified index.
        '''
        current_name = None
        if isinstance(xclip, Clip):
            current_name = xclip.name
            xclip.name = ''
        if value and value.strip():
            try:
                index = int(value) - 1
                if 0 <= index < len(self.song().scenes):
                    self.song().create_scene(index)
            except:
                pass
        else:
            self.song().create_scene(-1)
        if current_name:
            self._parent.schedule_message(
                4, partial(self.refresh_xclip_name, (xclip, current_name))
            )

    def duplicate_scene(self, track, xclip, ident, args):
        # type: (None, Clip, None, Text) -> None
        '''Duplicates the given scene.'''
        current_name = None
        if isinstance(xclip, Clip) and args:
            current_name = xclip.name
            xclip.name = ''
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

    def delete_scene(self, track, xclip, ident, args):
        # type: (None, Clip, None, Text) -> None
        '''Deletes the given scene as long as it's not the last scene in
        the set.
        '''
        if len(self.song().scenes) > 1:
            self.song().delete_scene(self.get_scene_to_operate_on(xclip, args.strip()))

    def set_scene(self, track, xclip, ident, args):
        # type: (None, Clip, None, Text) -> None
        '''Sets scene to play (doesn't launch xclip).'''
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
                        except:
                            new_min = 0
                        try:
                            new_max = int(rnd_range_data[1])
                        except:
                            new_max = num_scenes
                        if 0 < new_min and new_max < num_scenes + 1 and new_min < new_max - 1:
                            rnd_range = [new_min, new_max]
                scene = get_random_int(0, rnd_range[1] - rnd_range[0]) + rnd_range[0]
                if scene == self._last_scene_index:
                    while scene == self._last_scene_index:
                        scene = get_random_int(0, rnd_range[1] - rnd_range[0]) + rnd_range[0]
            # don't allow adjustment unless more than 1 scene
            elif args.startswith(('<', '>')) and len(self.song().scenes) > 1:
                factor = self._parent.get_adjustment_factor(args)
                if factor < len(self.song().scenes):
                    scene = self._last_scene_index + factor
                    if scene >= len(self.song().scenes):
                        scene -= len(self.song().scenes)
                    elif scene < 0 and abs(scene) >= len(self.song().scenes):
                        scene = -(abs(scene) - len(self.song().scenes))
        self._last_scene_index = scene
        for t in self.song().tracks:
            if t.is_foldable or (t.clip_slots[scene].has_clip and t.clip_slots[scene].clip == xclip):
                pass
            else:
                t.clip_slots[scene].fire()

    def get_scene_to_operate_on(self, xclip, args):
        # type: (Clip, Text) -> int
        scene = list(self.song().scenes).index(self.song().view.selected_scene)
        if isinstance(xclip, Clip):
            scene = xclip.canonical_parent.canonical_parent.playing_slot_index
        if '"' in args:
            scene_name = args[args.index('"')+1:]
            if '"' in scene_name:
                scene_name = scene_name[0:scene_name.index('"')]
                for i in range(len(self.song().scenes)):
                    if scene_name == self.song().scenes[i].name.upper():
                        scene = i
                        break
        elif args == 'SEL':
            scene = list(self.song().scenes).index(self.song().view.selected_scene)
        elif args:
            try:
                if 0 <= int(args) < len(self.song().scenes) + 1:
                    scene = int(args) - 1
            except:
                pass
        return scene

    def setup_scene_listeners(self):
        '''Setup listeners for all scenes in set and check that last
        index is in current scene range.
        '''
        self.remove_scene_listeners()
        scenes = self.song().scenes
        if not 0 < self._last_scene_index < len(scenes):
            self._last_scene_index = list(self.song().scenes).index(self.song().view.selected_scene)
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
