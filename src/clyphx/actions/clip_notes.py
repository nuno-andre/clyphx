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
from builtins import object, dict, range
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from typing import Any, Union, Optional, Text, Dict, List, Tuple
    Note = Tuple[int, float, Any, Any, bool]
    NoteActionSignature = Clip, Text, List[Note], List[Note]

import random
from ..consts import NOTE_NAMES, OCTAVE_NAMES
from ..core.live import Clip, get_random_int


class ClipNotesMixin(object):

    def dispatch_clip_note_action(self, clip, args):
        # type: (Clip, Text) -> None
        '''Handle clip note actions.'''
        from .consts import CLIP_NOTE_ACTIONS_CMD, CLIP_NOTE_ACTIONS_PREF

        if clip.is_audio_clip:
            return
        note_data = self.get_notes_to_operate_on(clip, args.strip())
        if note_data['notes_to_edit']:
            newargs = (clip, note_data['args'], note_data['notes_to_edit'], note_data['other_notes'])
            func = CLIP_NOTE_ACTIONS_CMD.get(note_data['args'])
            if not func:
                for k, v in CLIP_NOTE_ACTIONS_PREF.items():
                    if note_data['args'].startswith(k):
                        func = v
                        break
                else:
                    return
            func(self, *newargs)

    def get_notes_to_operate_on(self, clip, args=None):
        # type: (Clip, Optional[Text]) -> Union[Dict[Text, List[Any]], Optional[Text]]
        '''Get notes within loop braces to operate on.'''
        notes_to_edit = []
        other_notes = []
        new_args = None
        note_range = (0, 128)
        pos_range = (clip.loop_start, clip.loop_end)
        if args:
            new_args = [a.strip() for a in args.split()]
            note_range = self.get_note_range(new_args[0])
            new_args.remove(new_args[0])
            if new_args and '@' in new_args[0]:
                pos_range = self.get_pos_range(clip, new_args[0])
                new_args.remove(new_args[0])
            new_args = ' '.join(new_args)  # type: ignore
        clip.select_all_notes()
        all_notes = clip.get_selected_notes()
        clip.deselect_all_notes()
        for n in all_notes:
            if note_range[0] <= n[0] < note_range[1] and pos_range[0] <= n[1] < pos_range[1]:
                notes_to_edit.append(n)
            else:
                other_notes.append(n)
        return dict(
            notes_to_edit = notes_to_edit,
            other_notes   = other_notes,
            args          = new_args,
        )

    def get_pos_range(self, clip, string):
        # type: (Clip, Text) -> Tuple[float, float]
        '''Get note position or range to operate on.'''
        pos_range = (clip.loop_start, clip.loop_end)
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
        return pos_range

    def get_note_range(self, string):
        # type: (Text) -> Tuple[int, int]
        '''Get note lane or range to operate on.'''
        note_range = (0, 128)
        string = string.replace('NOTES', '')
        if len(string) > 1:
            try:
                note_range = self.get_note_range_from_string(string)
            except:
                try:
                    start_note_name = self.get_note_name_from_string(string)
                    start_note_num = self.string_to_note(start_note_name)
                    note_range = (start_note_num, start_note_num + 1)
                    string = string.replace(start_note_name, '').strip()
                    if len(string) > 1 and string.startswith('-'):
                        string = string[1:]
                        end_note_name = self.get_note_name_from_string(string)
                        end_note_num = self.string_to_note(end_note_name)
                        if end_note_num > start_note_num:
                            note_range = (start_note_num, end_note_num + 1)
                except ValueError:
                    pass
        return note_range

    def get_note_range_from_string(self, string):
        # type: (Text) -> Tuple[int, int]
        '''Returns a note range (specified in ints) from string.
        '''
        int_split = string.split('-')
        start = int(int_split[0])
        try:
            end = int(int_split[1]) + 1
        except IndexError:
            end = start + 1
        if 0 <= start and end <= 128 and start < end:
            return (start, end)
        raise ValueError("Invalid range note: '{}'".format(string))

    def get_note_name_from_string(self, string):
        # type: (Text) -> Text
        '''Get the first note name specified in the given string.'''
        if len(string) >= 2:
            result = string[:2].strip()
            if (result.endswith('#') or result.endswith('-')) and len(string) >= 3:
                result = string[:3].strip()
                if result.endswith('-') and len(string) >= 4:
                    result = string[:4].strip()
            return result
        raise ValueError("'{}' does not contain a note".format(string))

    def string_to_note(self, string):
        # type: (Text) -> Any
        '''Get note value from string.'''
        base_note = None

        for s in string:
            if s in NOTE_NAMES:
                base_note = NOTE_NAMES.index(s)
            if base_note is not None and s == '#':
                base_note += 1

        if base_note is not None:
            for o in OCTAVE_NAMES:
                if o in string:
                    base_note = base_note + (OCTAVE_NAMES.index(o) * 12)
                    break
            if 0 <= base_note < 128:
                return base_note

        raise ValueError("Invalid note: '{}'".format(string))

    def write_all_notes(self, clip, edited_notes, other_notes):
        # type: (Clip, List[Note], Any) -> None
        '''Writes new notes to clip.'''
        edited_notes.extend(other_notes)
        clip.select_all_notes()
        clip.replace_selected_notes(tuple(edited_notes))
        clip.deselect_all_notes()

# region NOTE ACTIONS
    def set_notes_on_off(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        '''Toggles or turns note mute on/off.'''
        edited_notes = []
        for n in notes_to_edit:
            new_mute = False
            if not args:
                new_mute = not n[4]
            elif args == 'ON':
                new_mute = True
            # TODO: check appending same tuple n times
            edited_notes.append((n[0], n[1], n[2], n[3], new_mute))
        if edited_notes:
            self.write_all_notes(clip, edited_notes, other_notes)

    def do_note_gate_adjustment(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        '''Adjust note gate.'''
        edited_notes = []
        factor = self._parent.get_adjustment_factor(args.split()[1], True)
        for n in notes_to_edit:
            new_gate = n[2] + (factor * 0.03125)
            if n[1] + new_gate > clip.loop_end or new_gate < 0.03125:
                edited_notes = []
                return
            else:
                edited_notes.append((n[0], n[1], new_gate, n[3], n[4]))
        if edited_notes:
            self.write_all_notes(clip, edited_notes, other_notes)

    def do_note_nudge_adjustment(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        '''Adjust note position.'''
        edited_notes = []
        factor = self._parent.get_adjustment_factor(args.split()[1], True)
        for n in notes_to_edit:
            new_pos = n[1] + (factor * 0.03125)
            if n[2] + new_pos > clip.loop_end or new_pos < 0.0:
                edited_notes = []
                return
            else:
                edited_notes.append((n[0], new_pos, n[2], n[3], n[4]))
        if edited_notes:
            self.write_all_notes(clip, edited_notes, other_notes)

    def do_note_velo_adjustment(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        '''Adjust/set/randomize note velocity.'''
        edited_notes = []
        args = args.replace('VELO ', '')
        args = args.strip()
        for n in notes_to_edit:
            if args == 'RND':
                # FIXME: get_random_int
                edited_notes.append((n[0], n[1], n[2], get_random_int(64, 64), n[4]))
            elif args.startswith(('<', '>')):
                factor = self._parent.get_adjustment_factor(args)
                new_velo = n[3] + factor
                if 0 <= new_velo < 128:
                    edited_notes.append((n[0], n[1], n[2], new_velo, n[4]))
                else:
                    edited_notes = []
                    return
            else:
                try:
                    edited_notes.append((n[0], n[1], n[2], float(args), n[4]))
                except:
                    pass
        if edited_notes:
            self.write_all_notes(clip, edited_notes, other_notes)

    def do_pitch_scramble(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        '''Scrambles the pitches in the clip, but maintains rhythm.'''
        edited_notes = []
        pitches = [n[0] for n in notes_to_edit]
        random.shuffle(pitches)
        for i in range(len(notes_to_edit)):
            edited_notes.append((
                pitches[i],
                notes_to_edit[i][1],
                notes_to_edit[i][2],
                notes_to_edit[i][3],
                notes_to_edit[i][4],
            ))
        if edited_notes:
            self.write_all_notes(clip, edited_notes, other_notes)

    def do_position_scramble(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        '''Scrambles the position of notes in the clip, but maintains
        pitches.
        '''
        edited_notes = []
        positions = [n[1] for n in notes_to_edit]
        random.shuffle(positions)
        for i in range(len(notes_to_edit)):
            edited_notes.append((
                notes_to_edit[i][0],
                positions[i],
                notes_to_edit[i][2],
                notes_to_edit[i][3],
                notes_to_edit[i][4],
            ))
        if edited_notes:
            self.write_all_notes(clip, edited_notes, other_notes)

    def do_note_reverse(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        '''Reverse the position of notes.'''
        edited_notes = []
        for n in notes_to_edit:
            edited_notes.append(
                (n[0], abs(clip.loop_end - (n[1] + n[2]) + clip.loop_start), n[2], n[3], n[4])
            )
        if edited_notes:
            self.write_all_notes(clip, edited_notes, other_notes)

    def do_note_invert(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        ''' Inverts the pitch of notes.'''
        edited_notes = []
        for n in notes_to_edit:
            edited_notes.append((127 - n[0], n[1], n[2], n[3], n[4]))
        if edited_notes:
            self.write_all_notes(clip, edited_notes, other_notes)

    def do_note_compress(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        '''Compresses the position and duration of notes by half.'''
        edited_notes = []
        for n in notes_to_edit:
            edited_notes.append((n[0], n[1] / 2, n[2] / 2, n[3], n[4]))
        if edited_notes:
            self.write_all_notes(clip, edited_notes, other_notes)

    def do_note_expand(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        '''Expands the position and duration of notes by 2.'''
        edited_notes = []
        for n in notes_to_edit:
            edited_notes.append((n[0], n[1] * 2, n[2] * 2, n[3], n[4]))
        if edited_notes:
            self.write_all_notes(clip, edited_notes, other_notes)

    def do_note_split(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        '''Split notes into 2 equal parts.
        '''
        edited_notes = []

        for n in notes_to_edit:
            if n[2] / 2 < 0.03125:
                return
            else:
                edited_notes.append(n)
                edited_notes.append((n[0], n[1] + (n[2] / 2), n[2] / 2, n[3], n[4]))

        if edited_notes:
            self.write_all_notes(clip, edited_notes, other_notes)

    def do_note_combine(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        '''Combine each consecutive set of 2 notes.
        '''
        edited_notes = []
        current_note = []
        check_next_instance = False

        for n in notes_to_edit:
            edited_notes.append(n)
            if current_note and check_next_instance:
                if current_note[0] == n[0] and current_note[1] + current_note[2] == n[1]:
                    edited_notes[edited_notes.index(current_note)] = [
                        current_note[0],
                        current_note[1],
                        current_note[2] + n[2],
                        current_note[3],
                        current_note[4],
                    ]
                    edited_notes.remove(n)
                    current_note = []
                    check_next_instance = False
                else:
                    current_note = n
            else:
                current_note = n
                check_next_instance = True

        if edited_notes:
            self.write_all_notes(clip, edited_notes, other_notes)

    def do_note_crescendo(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        '''Applies crescendo/decrescendo to notes.'''
        edited_notes = []
        last_pos = -1
        pos_index = 0
        new_pos = -1
        new_index = 0

        sorted_notes = sorted(notes_to_edit, key=lambda note: note[1], reverse=False)
        if args == 'VELO <<':
            sorted_notes = sorted(notes_to_edit, key=lambda note: note[1], reverse=True)
        for n in sorted_notes:
            if n[1] != last_pos:
                last_pos = n[1]
                pos_index += 1
        for n in sorted_notes:
            if n[1] != new_pos:
                new_pos = n[1]
                new_index += 1
            edited_notes.append((n[0], n[1], n[2], ((128 / pos_index) * new_index) - 1, n[4]))
        if edited_notes:
            self.write_all_notes(clip, edited_notes, other_notes)

    def do_note_delete(self, clip, args, notes_to_edit, other_notes):
        # type: (NoteActionSignature) -> None
        '''Delete notes.'''
        self.write_all_notes(clip, [], other_notes)
# endregion
