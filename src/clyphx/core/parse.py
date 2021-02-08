# coding: utf-8
#
# Copyright 2020-2021 Nuno André Novo
# Some rights reserved. See COPYING, COPYING.LESSER
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import absolute_import, unicode_literals
from typing import TYPE_CHECKING
from builtins import map, object
import re

from .models import Action, Command, UserControl

if TYPE_CHECKING:
    from typing import Any, Iterable, Iterator

OBJECT_SYMBOLS = {
    'SEL',
    'LAST',
    '<',
    '>',
    'ALL',
    'MST',
    'RACKS',
    'DETAIL',
    'SELF',
    # return tracks ( index = ord(track) - 65 )
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
}


class Parser(object):
    '''Command parser.
    '''
    command = re.compile(r'\[(?P<id>\w*?)\]\s*?'
                         r'(\((?P<seq>R?[PL]SEQ)\))?\s*?'
                         r'(?P<lists>\S.*?)\s*?$', re.I)
    lists   = re.compile(r'(?P<start>[^:]*?)'
                         r'(?:\s*?[:]\s*?(?P<stop>\S[^:]*?))?\s*?$')
    actions = re.compile(r'^\s+|\s*;\s*|\s+$')
    # action  = re.compile(r'^((?P<tracks>[A-Z0-9"\-,<>\s]*?)/)?'
    #                      r'(?P<name>[A-Z0-9]+?)'
    #                      r'(\((?P<obj>[A-Z0-9"\-,<>.]+?)\))?'
    #                      r'(\s+?(?P<args>(?! ).*))?$', re.I)
    action  = re.compile(r'^((?P<tracks>[\w<>"\-,\s]*?)/)?'
                         r'(?P<name>[A-Z0-9]+?)'
                         r'(\((?P<obj>[A-Z0-9"\-,<>.]+?)\))?'
                         r'(\s+?(?P<args>(?! ).*))?$', re.I)
    # tracks  = re.compile(r'^\s+|\s*,\s*|\s+$')
    tracks  = re.compile(r'\"(?P<literal>[A-Z0-9\-<>\s]*?)?\"|'
                         r'(?:^|[\s,]?(?P<symbol>[A-Z0-9<>]*)|'
                         r'(?P<range>[A-Z0-9\-<>]*))(?:[\s,]|$)', re.I)

    # TODO: parsing and validation
    # def parse_tracks(self, tracks):
    #     if not tracks:
    #         return
    #     return self.tracks.split(tracks)

    def parse_tracks(self, tracks):
        # type: (Text) -> Optional[Iterable[Text]]
        if not tracks:
            return None
        return self.tracks.split(tracks)

    # TODO: lexing and syntactic validation
    def parse_args(self, args):
        # type: (Text) -> Optional[Iterable[Text]]
        if not args:
            return None
        return args.split()

    def parse_action_list(self, actions):
        # type: (Text) -> Iterator[Action]
        try:
            for a in self.actions.split(actions):
                action = self.action.match(a).groupdict()
                action.update(tracks=self.parse_tracks(action['tracks']),  # type: ignore
                              args=self.parse_args(action['args']))
                yield Action(**action)
        except (AttributeError, TypeError):
            raise ValueError("'{}' is not a valid action list".format(actions))

    def __call__(self, text):
        # type: (Text) -> Command
        # split 'id', 'seq' (if any) and action 'lists' from the origin string
        cmd = self.command.search(text).groupdict()
        # split previous 'lists' into 'start' and 'stop' action lists
        start, stop = self.lists.match(cmd.pop('lists')).groups()
        try:
            stop = list(self.parse_action_list(stop))
        except ValueError:
            if not stop or stop == '*':
                stop = stop or None
            else:
                raise
        cmd.update(start=list(self.parse_action_list(start)), stop=stop)  # type: ignore
        return Command(**cmd)
