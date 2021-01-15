from __future__ import absolute_import, unicode_literals, with_statement
from builtins import map

import re
import os
import logging

from .compat import ABC, abstractmethod, with_metaclass
from .models import Command, UserControl
from .utils import get_base_path

log = logging.getLogger(__name__)


class Parser(object):
    '''Command parser.
    '''
    command = re.compile(r'\[(?P<id>[a-zA-Z0-9\_]*?)\]\s*?'
                         r'(?P<seq>\([a-zA-Z]*?\))?\s*?'
                         r'(?P<actions>\S.*?)\s*?$')
    lists   = re.compile(r'(?P<start>[^,]*?)'
                         r'(\s*?,\s*?(?P<stop>\S[^,]*?))?\s*?$')
    actions = re.compile(r'^\s+|\s*;\s*|\s+$')

    def __init__(self):
        self._user_stettings = dict()

    def __call__(self, text):
        cmd = self.command.search(text).groupdict()
        lists = self.lists.match(cmd.pop('actions')).groupdict()
        cmd.update(
            start=self.actions.split(lists['start']),
            stop=self.actions.split(lists['stop'])
                 if lists['stop'] and lists['stop'] != '*'
                 else lists['stop'],
        )
        return Command(**cmd)



# class Settings(ABC):
#     '''Base class for settings file parsers.
#     '''
#     @classmethod
#     def from_file(cls, filepath):
#         SECTIONS = r'^\*+?\s?([^\*]*?)\s?\*+\s*?$((?!^\*).*?)(?=\n\*|\Z)'
#         CONTENT  = re.compile(r'^(?! )[^\*#\n"]+$')

#         self = cls()

#         for m in re.findall(SECTIONS, open(filepath).read(), re.M | re.S):
#             section, content = m
#             try:
#                 method = self.methods[section]
#                 method(CONTENT.findall(content, re.M))
#             except KeyError:
#                 log.debug('unknown section in %s: %s', filepath, section)

#         return self

#     def _split_lines(self, content, lower=True):
#         for line in map(str.lower if lower else str, content):
#             try:
#                 yield tuple(x.strip() for x in line.split('='))
#             except Exception as e:
#                 log.error('Error parsing setting: %s (%s)', line, e)

#     # # TODO: make Pyy3 compatible
#     # class __metaclass__(ABC):
#     #     @property
#     #     def methods(cls):
#     #         raise NotImplementedError


class UserSettings(object):

    def __init__(self):
        self.vars      = dict()
        self.controls  = dict()
        self.prefs     = dict()
        self.snapshots = dict()
        self.cs_linker = dict()
        self._parse_file()

    def _parse_file(self):
        SECTIONS = r'^\*+?\s?([^\*]*?)\s?\*+\s*?$((?!^\*).*?)(?=\n\*|\Z)'
        CONTENT  = re.compile(r'^(?! )[^\*#\n"]+$')
        METHODS  = dict((
            ('[USER VARIABLES]',    self._user_vars),
            ('[USER CONTROLS]',     self._user_controls),
            ('[EXTRA PREFS]',       self._extra_prefs),
            ('[SNAPSHOT SETTINGS]', self._snapshot_settings),
            ('[CSLINKER]',          self._cs_linker),
        ))

        filepath = get_base_path('UserSettings.txt')

        for m in re.findall(SECTIONS, open(filepath).read(), re.M | re.S):
            section, content = m
            try:
                method = METHODS[section]
                method(CONTENT.findall(content, re.M))
            except KeyError:
                pass

    def _split_lines(self, content, lower=True):
        for line in map(str.lower if lower else str, content):
            try:
                yield tuple(x.strip() for x in line.split('='))
            except Exception as e:
                log.error('Error parsing setting: %s (%s)', line, e)

    def _user_vars(self, content):
        # TODO
        self.vars = dict((k, v) for k, v in self._split_lines(content, False))

    def _user_controls(self, content):
        CONTROL = re.compile(r'^(?P<type>[^,]*?)\s*?,\s*?'
                             r'(?P<channel>(?! )[\d]*)\s*?,\s*?'
                             r'(?P<value>(?! )[\d]*)\s*?'
                             r'([,;]\s*?(?P<actions>(?! ).*))?')

        # TODO: don't split line and parse the name
        for (k, v) in self._split_lines(content):
            try:
                # TODO: parse actions
                res = CONTROL.match(v).groupdict()
                res.update(name=k)
                self.controls[k] = UserControl(**res)
            except Exception as e:
                log.exception(e)

    def _extra_prefs(self, content):
        for (k, v) in self._split_lines(content):
            if k in {'navigation_highlight',
                    'exclusive_arm_on_select',
                    'exclusive_show_group_on_select',
                    'clip_record_length_set_by_global_quantization'}:
                self.prefs[k] = v == 'on'
            elif k == 'process_xclips_if_track_muted':
                self.prefs[k] = v == 'true'
            elif k == 'startup_actions':
                self.prefs[k] = '[]{}'.format(v) if v != 'off' else None
            elif k == 'default_inserted_midi_clip_length':
                self.prefs[k] = False
                try:
                    if 2 <= int(v) < 17:
                        self.prefs[k] = int(v)
                except:
                    pass
            else:
                log.warning('Extra preference unknown: %s = %s', k, v)

    def _snapshot_settings(self, content):
        for (k, v) in self._split_lines(content):
            if k == 'include_nested_devices_in_snapshots':
                self.snapshots['include_nested_devices'] = v == 'on'
            elif k == 'snapshot_parameter_limit':
                try:
                    self.snapshots['parameter_limit'] = int(v)
                except:
                    # TODO: initialize defaults?
                    self.snapshots['parameter_limit'] = 500
            else:
                log.warning('Snapshot setting unknown: %s = %s', k, v)

    def _cs_linker(self, content):
        for (k, v) in self._split_lines(content):
            k = '_{}'.format(k.replace('cslinker_', ''))
            if k in {'_matched_link', '_horizontal_link', '_multi_axis_link'}:
                self.cs_linker[k] = v == 'true'
            elif k in {'_script_1_name', '_script_2_name'}:
                self.cs_linker[k] = v if v != 'none' else None
            else:
                log.warning('CS Linker setting unknown: %s = %s', k, v)
