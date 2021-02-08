# coding: utf-8
#
# Copyright 2020-2021 Nuno André Novo
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
    from typing import Text, Dict

log = logging.getLogger(__name__)

SCHEMA = {
    'snapshot_settings': {
        'include_nested_devices_in_snapshots': bool,
        'snapshot_parameter_limit': int,
    },
    'extra_prefs': {
        'process_xclips_if_track_muted': bool,
        'startup_actions': (False, str),
        'navigation_highlight': bool,
        'exclusive_arm_on_select': bool,
        'exclusive_show_group_on_select': bool,
        'clip_record_length_set_by_global_quantization': bool,
        'default_inserted_midi_clip_length': int,
    },
    'cslinker': {
        'cslinker_matched_link': bool,
        'cslinker_horizontal_link': bool,
        'cslinker_multi_axis_link': bool,
        'cslinker_script_1_name': (None, str),
        'cslinker_script_2_name': (None, str),
    },
}


class UserSettings(object):
    '''Read config file(s) and keep the results in attributes:

           self.section[option] = value

       The value is validated if [section][option] in SCHEMA,
       if not is passed as-is.
    '''
    def __init__(self, *filepaths):
        # type: (Text) -> None
        for path in filepaths:
            self._parse_config(path)

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
                    value = config.getint(section, option)
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

    # deprecated
    vars      = property(lambda s: getattr(s, 'user_variables', {}))
    controls  = property(lambda s: getattr(s, 'user_controls', {}))
    prefs     = property(lambda s: getattr(s, 'extra_prefs', {}))
    snapshots = property(lambda s: getattr(s, 'snapshot_settings', {}))
    cs_linker = property(lambda s: getattr(s, 'cs_linker', {}))


def get_user_settings():
    # type: () -> UserSettings
    from .core.utils import get_base_path
    import os

    filepath = os.path.expanduser('~/ClyphX/UserSettings.txt')
    if os.path.exists(filepath):
        return UserSettings(filepath)

    filepath = get_base_path('UserSettings.txt')
    if os.path.exists(filepath):
        return UserSettings(filepath)

    filepath = os.path.expandvars('$CLYPHX_CONFIG')
    if os.path.exists(filepath) and os.path.isfile(filepath):
        return UserSettings(filepath)

    raise Exception('User settings not found.')


# TODO
class UserVars(object):
    _vars = dict()  # type: Dict[Text, Text]

    def __getitem__(self, key):
        # TODO
        return self._vars.get(key, '0')

    def __setitem__(self, key, value):
        self.add_var(key, value)

    def add_var(self, name, value):
        # type: (Text, Text) -> None
        value = str(value)
        if not any(x in value for x in (';', '%', '=')):
            if '(' in value and ')' in value:
                try:
                    value = eval(value)
                except Exception as e:
                    log.error('Evaluation error: %s=%s', name, value)
                    return
            self._vars[name] = str(value)
            log.debug('User variable assigned: %s=%s', name, value)

    def resolve_vars(self, string):
        # type: (Text) -> Text
        '''Replace any user variables in the given string with the value
        the variable represents.
        '''
        pass
