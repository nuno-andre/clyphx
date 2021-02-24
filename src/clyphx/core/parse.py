# coding: utf-8
#
# Copyright (c) 2020-2021 Nuno André Novo
# Some rights reserved. See COPYING, COPYING.LESSER
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import absolute_import, unicode_literals
from typing import TYPE_CHECKING
from builtins import map, object
import re

from .models import Action, Spec, UserControl
from .exceptions import ParsingError

if TYPE_CHECKING:
    from typing import Any, Optional, Text, Iterator, Iterable


# region TERMINAL SYMBOLS
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

TRACKCNT = r'\b(?P<num>\d{1,2})\b'
TRACKRET = r'\b(?P<ret>[A-La-l])\b'
TRACKNAM = r'\b\"(?P<lit>[\w\s\]+?)\"\b'
TRACKSYM = r'\b(?P<sym>[A-Za-z]\w+?)\b'
TRACK    = r'({}|{}|{}|{})'.format(TRACKCNT, TRACKRET, TRACKNAM, TRACKSYM)
TRACKRG  = r'(?P<range>{}\-{})'.format(TRACK.replace('P<', 'P<r1'), TRACK.replace('P<', 'P<r2'))
TRACKS   = r'[\s,]?({}|{})[\s,]?'.format(TRACK, TRACKRG)
# endregion


class SpecParser(object):
    '''Spec parser.
    '''
    #: spec structure
    spec = re.compile(r'''
        \[(?P<id>\w*?)\]\s*?
        (\((?P<seq>R?[PL]SEQ)\))?\s*?
        (?P<lists>\S.*?)\s*?$
    ''', re.I | re.X)

    #: action lists
    lists = re.compile(r'''
        (?P<on>[^:]*?)
        (?:\s*?[:]\s*?(?P<off>\S[^:]*?))?\s*?$
    ''', re.X)

    #: list actions
    actions = re.compile(r'^\s+|\s*;\s*|\s+$')

    #: action structure
    action  = re.compile(
        r'^((?P<tracks>[\w<>"\-,\s]*?)\s?/)?'
        r'(?P<name>[A-Z0-9]+?)'
        r'(\((?P<obj>[A-Z0-9"\-,<>.]+?)\))?'
        r'(\s+?(?P<args>(?! ).*))?$'
    , re.I)

    splittracks = re.compile(r'\s?[\\A,\\Z]\s?').split

    #: tracks definition
    tracks  = re.compile(r'''
        \"(?P<literal>[A-Z0-9\-<>\s]+?)?\"|
        (?:^|[\s,]?(?P<symbol>[A-Z0-9<>]+?)|
        (?P<range>[A-Z0-9\-<>]+?))(?:[\s,]|$)  # ranges
    ''', re.I | re.X)

    def parse_tracks(self, tracks):
        # type: (Text) -> Optional[Iterable[Text]]
        if not tracks:
            return None

        # TODO: split before parsing
        # tracks = self.splittracks(tracks)

        return [{k:v for k, v in m.groupdict().items() if v}
                for m in self.tracks.finditer(tracks)]

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
        # type: (Text) -> Spec

        # split the label into 'id', 'seq' (if any) and action 'lists'
        spec = self.spec.search(text).groupdict()

        # split previous 'lists' into 'on' and 'off' action lists
        on, off = self.lists.match(spec.pop('lists')).groups()
        try:
            off = list(self.parse_action_list(off))
        except ValueError as e:
            if not off or off == '*':
                off = off or None
            else:
                # raise ParsingError(e)
                raise Exception(e)

        spec.update(on=list(self.parse_action_list(on)), off=off)  # type: ignore
        return Spec(**spec)
