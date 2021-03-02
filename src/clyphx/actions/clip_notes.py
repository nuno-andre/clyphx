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
from builtins import object, dict, range, tuple
from typing import NamedTuple, List, Text, Tuple
import logging
import random

from ..core.live import Clip, get_random_int
from ..core.models import Pitch, pitch_range #, Note

log = logging.getLogger(__name__)

Note = Tuple[int, float, float, int, bool]


CmdData = NamedTuple('CmdData', [('clip',          Clip),
                                 ('notes_to_edit', List[Note]),
                                 ('other_notes',   List[Note]),
                                 ('args',          List[Text])])


class NotesMixin(object):

    def dispatch_clip_note_action(self, clip, args):
        # type: (Clip, List[Text]) -> None
        '''Handle clip note actions.'''
        from .consts import NOTES_ACTIONS

        if clip.is_audio_clip:
            return

        data = self.get_notes_to_edit(clip, args)
        if data.notes_to_edit:
            # TODO: pop arg
            action = data.args[0] if data.args else None
            try:
                func = NOTES_ACTIONS[action]
            except KeyError:
                log.error("Note action not found in %s", data.args)
            else:
                edited = func(self, data)
                if edited:
                    self.write_notes(data, edited)

    def get_notes_to_edit(self, clip, args):
        # type: (Clip, List[Text]) -> CmdData
        '''Get notes within loop braces to operate on.'''
        notes_to_edit = []
        other_notes = []
        note_range = (0, 128)
        pos_range = None

        if args:
            note_range = self.get_note_range(args[0])
            args.pop(0)
            if args and '@' in args[0]:
                pos_range = self.get_pos_range(clip, args[0])
                args.pop(0)
        pos_range = pos_range or (clip.loop_start, clip.loop_end)

        clip.select_all_notes()
        all_notes = clip.get_selected_notes()
        clip.deselect_all_notes()

        for n in all_notes:
            if note_range[0] <= n[0] < note_range[1] and pos_range[0] <= n[1] < pos_range[1]:
                notes_to_edit.append(n)
            else:
                other_notes.append(n)
        return CmdData(clip, notes_to_edit, other_notes, args)

    @staticmethod
    def get_pos_range(clip, string):
        # type: (Clip, Text) -> Tuple[float, float]
        '''Get note position or range to operate on.'''
        pos_range = None
        user_range = string.split('-')
        try:
            start = float(user_range[0].replace('@', ''))
        except:
            pass
        else:
            if start >= 0.0:
                pos_range = (start, start)
                if len(user_range) > 1:
                    try:
                        pos_range = (start, float(user_range[1]))
                    except:
                        pass
        return pos_range or (clip.loop_start, clip.loop_end)

    def get_note_range(self, string):
        # type: (Text) -> Tuple[int, int]
        '''Get note lane or range to operate on.'''
        # TODO: check limit range in 128
        note_range = (0, 128)
        string = string.replace('NOTES', '')
        if len(string) > 1:
            try:
                note_range = pitch_range(string)
            except:
                try:
                    start_note = Pitch.first_note(string)
                    note_range = (start_note, start_note + 1)
                    string = string.replace(str(start_note), '').strip()

                    end_note = Pitch.first_note(string[1:])
                    if end_note > start_note_num:
                        note_range = (start_note_num, end_note + 1)
                except ValueError:
                    pass
        return note_range

    @staticmethod
    def write_notes(data, edited):
        # type: (CmdData, List[Note]) -> None
        edited.extend(data.other_notes)
        data.clip.select_all_notes()
        data.clip.replace_selected_notes(tuple(edited))
        data.clip.deselect_all_notes()


# region NOTE ACTIONS
    def set_notes_on_off(self, data):
        # type: (CmdData) -> List[Note]
        '''Toggles or turns note mute on/off.'''
        if not data.args:
            edited = [(n[0], n[1], n[2], n[3], not n[4]) for n in data.notes_to_edit]
        else:
            mute = data.args[0] == 'ON'
            edited = [(n[0], n[1], n[2], n[3], mute) for n in data.notes_to_edit]
        return edited

    def do_note_gate_adjustment(self, data):
        # type: (CmdData) -> List[Note]
        '''Adjust note gate.'''
        edited = []
        factor = self.get_adjustment_factor(data.args[1], True)
        loop_end = data.clip.loop_end
        for n in data.notes_to_edit:
            new_gate = n[2] + (factor * 0.03125)
            if n[1] + new_gate > loop_end or new_gate < 0.03125:
                edited = []
                return
            else:
                edited.append((n[0], n[1], new_gate, n[3], n[4]))
        return edited

    def do_note_nudge_adjustment(self, data):
        # type: (CmdData) -> List[Note]
        '''Adjust note position.'''
        edited = []
        factor = self.get_adjustment_factor(data.args[1], True)
        for n in data.notes_to_edit:
            new_pos = n[1] + (factor * 0.03125)
            if n[2] + new_pos > data.clip.loop_end or new_pos < 0.0:
                edited = []
                return
            else:
                edited.append((n[0], new_pos, n[2], n[3], n[4]))
        return edited

    def do_pitch_scramble(self, data):
        # type: (CmdData) -> List[Note]
        '''Scrambles the pitches in the clip, but maintains rhythm.'''
        pitches = [n[0] for n in data.notes_to_edit]
        random.shuffle(pitches)
        notes = [tuple(n[1:5]) for n in data.notes_to_edit]
        return [(pitches[i],) + n for i, n in enumerate(notes)]

    def do_position_scramble(self, data):
        # type: (CmdData) -> List[Note]
        '''Scrambles the position of notes in the clip, but maintains
        pitches.
        '''
        positions = [n[1] for n in data.notes_to_edit]
        random.shuffle(positions)
        return [(n[0], positions[i], n[2], n[3], n[4])
                for i, n in enumerate(data.notes_to_edit)]

    def do_note_reverse(self, data):
        # type: (CmdData) -> List[Note]
        '''Reverse the position of notes.'''
        end, start = data.clip.loop_end, data.clip.loop_start
        reverse = lambda n: abs(end - (n[1] + n[2]) + start)
        return [(n[0], reverse(n), n[2], n[3], n[4]) for n in data.notes_to_edit]

    def do_note_invert(self, data):
        # type: (CmdData) -> List[Note]
        ''' Inverts the pitch of notes.'''
        return [(127 - n[0], n[1], n[2], n[3], n[4]) for n in data.notes_to_edit]

    def do_note_compress(self, data):
        # type: (CmdData) -> List[Note]
        '''Compresses the position and duration of notes by half.'''
        return [(n[0], n[1] / 2, n[2] / 2, n[3], n[4]) for n in data.notes_to_edit]

    def do_note_expand(self, data):
        # type: (CmdData) -> List[Note]
        '''Expands the position and duration of notes by 2.'''
        return [(n[0], n[1] * 2, n[2] * 2, n[3], n[4]) for n in data.notes_to_edit]

    def do_note_split(self, data):
        # type: (CmdData) -> List[Note]
        '''Split notes into 2 equal parts.
        '''
        edited = []

        for n in data.notes_to_edit:
            if n[2] / 2 < 0.03125:
                return
            else:
                edited.append(n)
                edited.append((n[0], n[1] + (n[2] / 2), n[2] / 2, n[3], n[4]))

        return edited

    def do_note_combine(self, data):
        # type: (CmdData) -> List[Note]
        '''Combine each consecutive set of 2 notes.
        '''
        edited = []
        current_note = []
        check_next_instance = False

        for n in data.notes_to_edit:
            edited.append(n)
            if current_note and check_next_instance:
                if current_note[0] == n[0] and current_note[1] + current_note[2] == n[1]:
                    edited[edited.index(current_note)] = [
                        current_note[0],
                        current_note[1],
                        current_note[2] + n[2],
                        current_note[3],
                        current_note[4],
                    ]
                    edited.remove(n)
                    current_note = []
                    check_next_instance = False
                else:
                    current_note = n
            else:
                current_note = n
                check_next_instance = True

        return edited

    def do_note_velo_adjustment(self, data):
        # type: (CmdData) -> List[Note]
        '''Adjust/set/randomize note velocity.'''
        edited = []
        arg = data.args[1]  # data.args[0] == 'VELO'

        if arg == 'RND':
            for n in data.notes_to_edit:
                # FIXME: get_random_int
                edited.append((n[0], n[1], n[2], get_random_int(64, 64), n[4]))

        elif arg.starswith(('<', '>')):
            for n in data.notes_to_edit:
                factor = self.get_adjustment_factor(arg)
                new_velo = n[3] + factor
                if 0 <= new_velo < 128:
                    edited.append((n[0], n[1], n[2], new_velo, n[4]))
                else:
                    edited = []
                    return

        elif arg in ('<<', '>>'):
            return self.do_note_crescendo(data)

        else:
            for n in data.notes_to_edit:
                try:
                    edited.append((n[0], n[1], n[2], float(arg), n[4]))
                except:
                    pass

        return edited

    def do_note_crescendo(self, data):
        # type: (CmdData) -> List[Note]
        '''Applies crescendo/decrescendo to notes.'''
        edited = []
        last_pos = -1
        pos_index = 0
        new_pos = -1
        new_index = 0

        reverse = data.args[1] == '<<'
        sorted_notes = sorted(data.notes_to_edit, key=lambda n: n[1], reverse=reverse)
        for n in sorted_notes:
            if n[1] != last_pos:
                last_pos = n[1]
                pos_index += 1
        for n in sorted_notes:
            if n[1] != new_pos:
                new_pos = n[1]
                new_index += 1
            edited.append((n[0], n[1], n[2], ((128 / pos_index) * new_index) - 1, n[4]))
        return edited

    def do_note_delete(self, data):
        # type: (CmdData) -> None
        '''Delete notes.'''
        # XXX: write here, edited would be evaluated to False
        self.write_notes(data, [])
# endregion
