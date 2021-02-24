# coding: utf-8
#
# Copyright (c) 2020-2021 Nuno André Novo
# Some rights reserved. See COPYING, COPYING.LESSER
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import absolute_import, unicode_literals, with_statement
from typing import TYPE_CHECKING
from builtins import dict, object
import logging
import re

try:
    from ConfigParser import ConfigParser
    from StringIO import StringIO
except ImportError:
    from configparser import ConfigParser
    from io import StringIO

if TYPE_CHECKING:
    from typing import Any, Text, Dict

log = logging.getLogger(__name__)

unset = object()

SCHEMA = dict(
    snapshot_settings = dict(
        include_nested_devices_in_snapshots = bool,
        snapshot_parameter_limit = int,
    ),
    extra_prefs = dict(
        process_xclips_if_track_muted = bool,
        startup_actions = (False, str),
        navigation_highlight = bool,
        exclusive_arm_on_select = bool,
        exclusive_show_group_on_select = bool,
        clip_record_length_set_by_global_quantization = bool,
        default_inserted_midi_clip_length = int,
    ),
    cslinker = dict(
        cslinker_matched_link = bool,
        cslinker_horizontal_link = bool,
        cslinker_multi_axis_link = bool,
        cslinker_script_1_name = (None, str),
        cslinker_script_2_name = (None, str),
    ),
)


class UserSettings(object):
    '''Read config file(s) and keep the results in attributes:

        self.section[option] = value

    The value is validated if [section][option] in SCHEMA,
    if not is passed as-is.
    '''
    def __init__(self, *filepaths):
        # type: (Text) -> None
        self._vars = None
        for path in filepaths:
            self._parse_config(path)

    @property
    def vars(self):
        if self._vars is None:
            self._vars = UserVars()
            valid_section_names = ['user_variables', 'variables']
            config = self._getattrs(valid_section_names, fallback=dict())
            for k, v in config.items():
                self._vars[k] = v
        return self._vars

    @property
    def prefs(self):
        valid_section_names = ['extra_prefs', 'general_settings']
        return self._getattrs(valid_section_names, fallback=dict())

    def _getattrs(self, attrs, fallback=unset):
        for attr in attrs:
            try:
                return getattr(self, attr)
            except AttributeError:
                pass
        else:
            if fallback is not unset:
                return fallback
            else:
                raise AttributeError

    def _parse_config(self, path):
        HEADER = re.compile(r'^\*+?\s*?(\[.*?\]).*?$')

        lines = ['[DEFAULT]']
        with open(path) as f:
            for line in f:
                if line.startswith(('#', '"')) or not line.strip():
                    continue
                match = HEADER.match(line)
                if match:
                    lines.append(match.group(1).lower().replace(' ', '_'))
                else:
                    lines.append(line)

        config = ConfigParser(allow_no_value=True)
        buffer = StringIO('\n'.join(lines))
        config.readfp(buffer)
        config.remove_section('settings_notes')

        any = object()

        for section in config.sections():
            setattr(self, section, dict())

            for option in config.options(section):
                _type = SCHEMA.get(section, {}).get(option, any)
                if _type is int:
                    value = config.getint(section, option)  # type: Any
                elif _type is bool:
                    value = config.getboolean(section, option)
                elif _type == (None, str):
                    value = config.get(section, option)
                    if value.lower() == 'none':
                        value = None
                elif _type == (False, str):
                    value = config.get(section, option)
                    if value.lower() == 'off':
                        value = False
                else:
                    value = config.get(section, option)
                getattr(self, section)[option] = value

    xcontrols  = property(lambda s: getattr(s, 'user_controls', {}))
    snapshots = property(lambda s: getattr(s, 'snapshot_settings', {}))


def get_user_settings():
    # type: () -> UserSettings
    from .core.utils import get_base_path
    import os

    for func, arg in [
        # (os.path.expandvars, '$CLYPHX_CONFIG'),
        (os.path.expanduser, '~/ClyphX/UserSettings.txt'),
        (get_base_path,      'UserSettings.txt'),
    ]:
        filepath = func(arg)
        if os.path.exists(filepath):
            log.info('Reading settings from %s', filepath)
            return UserSettings(filepath)

    raise OSError('User settings not found.')


# TODO
class UserVars(object):
    '''User vars container.

    Var names are case-insensitive and should not contain characters
    other than letters, numbers, and underscores.
    '''
    _vars = dict()  # type: Dict[Text, Text]

    # new format: %VARNAME%
    re_var = re.compile(r'%(\w+?)%')

   # legacy format: $VARNAME
    re_legacy_var = re.compile(r'\$(\w+?)\b')

    def __getitem__(self, key):
        # (Text) -> Text
        try:
            key = key.group(1)
        except AttributeError:
            pass
        try:
            return self._vars[key.lower()]
        except KeyError:
            log.warning("Var '%s' not found. Defaults to '0'.", key)
            return '0'

    def __setitem__(self, key, value):
        # type: (Text, Text) -> None
        self._add_var(key.lower(), value)

    def _add_var(self, name, value):
        # type: (Text, Text) -> None
        value = self.sub(str(value))

        if any(x in value for x in (';', '%', '=')):
            err = "Invalid assignment: {} = {}"
            raise ValueError(err.format(name, value))

        if '(' in value and ')' in value:
            value = eval(value)
        self._vars[name] = str(value)
        log.debug('User variable assigned: %s=%s', name, value)

    def add(self, statement):
        # type: (Text) -> None
        '''Evaluates the expression (either an assignment or an
        expression enclosed in parens) and stores the result.
        '''
        statement = statement.replace('$', '')  # legacy vars compat
        try:
            key, val = [x.strip() for x in statement.split('=')]
            self._add_var(key, val)
        except Exception as e:
            log.error("Failed to evaluate '%s': %r", statement, e)

    def sub(self, string):
        # type: (Text) -> Text
        '''Replace any user variables in the given string with their
        stored value.
        '''
        try:
            if '%' in string:
                return self.re_var.sub(self.__getitem__, string)
            elif '$' in string:
                return self.re_legacy_var.sub(self.__getitem__, string)
        except Exception as e:
            log.error("Failed to substitute '%s': %r", string, e)
        return string
