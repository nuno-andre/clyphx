# coding: utf-8
#
# Copyright (c) 2020-2021 Nuno André Novo
# Some rights reserved. See COPYING, COPYING.LESSER
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import absolute_import, unicode_literals
from builtins import map, object, dict
from operator import neg, pos, add
from typing import TYPE_CHECKING
import re

from .models import IdSpec
from .exceptions import ParsingError

if TYPE_CHECKING:
    from typing import Optional, Text, Dict


TERMINALS = dict(
    IDENT    = r'(?P<id>\w*?)',
    OVERRIDE = r'(?:\[(?P<override>\w*?)\])',  # X-Control override
    SEQ      = r'\(R?(?P<seq>[PL]SEQ)\)',
)

NONTERMINALS = dict(
    LISTS   = r'(?P<lists>[\w<>"]\S.*?)',
    ACTIONS = r'(?=[^|;]\s*?)(\S.*?)\s*?(?=$|;)',
)

SYMBOLS = TERMINALS.copy()
SYMBOLS.update(NONTERMINALS)


class IdSpecParser(object):

    #: spec structure
    spec = re.compile(r'''
        ^\[({IDENT}|{OVERRIDE})?\]\s*?
        ({SEQ}\s*)?
        {LISTS}\s*?$
    '''.format(**SYMBOLS), re.I | re.X)

    #: action lists
    lists = re.compile(r'''
        (?P<on>[^:]*?)
        (?:\s*?[:]\s*?
        (?P<off>\S[^:]*?))?\s*?$
    ''', re.X)
    actions = re.compile(NONTERMINALS['ACTIONS'])

    def _parse(self, string):
        # type: (Text) -> IdSpec

        # extract identifier and seq
        spec = self.spec.search(string).groupdict()

        # split lists
        lists = self.lists.match(spec.pop('lists')).groupdict().items()
        spec.update({k: self.actions.findall(v) if v else v for k, v in lists})

        if spec['override']:
            spec.update(id=spec['override'], override=True)
        else:
            spec['override'] = False

        return IdSpec(**spec)

    def __call__(self, string):
        # type: (Text) -> IdSpec
        try:
            return self._parse(string)
        except Exception:
            raise ParsingError(string)


TERMINALS = dict()

NONTERMINALS = dict(
    TRACKS = '^.*?/',
    TOKENS = '',
)


class ActionParser(object):

    tracks = re.compile('', re.I)
    tokens = re.compile('', re.I)

    def _parse(self, string):
        pass

    def __call__(self, string):
        try:
            return self._parse(string)
        except Exception:
            raise ParsingError(string)


TERMINALS = dict(
    POS  = r'(?P<pos>[1-9]\d?)',  # 1-99
    SEL  = r'(?P<sel>SEL)',
    NAME = r'\"(?P<name>[A-Z0-9\-<>\s]+?)?\"',
    ADD  = r'(?P<add>[><])(?P<addval>\d?(?P<addfract>\.\d+?)?)',
)

TARGETS = dict(
    CLIP  = r'(?P<clip>CLIP(?P<clips>\(?{POS}|{SEL}|{NAME}\)?)?)',
    DEV   = r'(?P<dev>DEV(?P<devs>\(?...\)?)?)',
    DR    = r'(?P<dr>DR(?P<drs>\(?...\)?)?)',
    CH    = r'(?P<ch>CH(?P<chs>\(?...\)?)?)',
    PAD   = r'(?P<pad>PAD(?P<pads>\(?...\)?)?)',
    NOTES = r'(?P<note>NOTES(?P<notes>\(?...\)?)?)',
)


class ObjParser(object):

    clip = re.compile(r'CLIP(?P<clip>{POS}|{SEL}|{NAME})?'.format(**TERMINALS), re.I)

    def _parse(self, kind, string):
        match = getattr(self, kind).match(string)

        # # if only fractional part, it's a float in the format: >.012
        # if match.get('add'):
        #     func  = float if match.pop('addfract') else int
        #     value = func(match.pop('addval') or (0 if func is float else 1))
        #     sign  = {'>': pos, '<': neg}[match.pop('add')]
        #     match['op'] = partial(add, sign(value))

        return {k: v for k, v in match.groupdict().items() if v}

    def __call__(self, kind, string):
        # type: (Text, Text) -> Dict[Text, Text]
        try:
            return self._parse(kind, string)
        except Exception:
            raise ParsingError(string)


__all__ = ['IdSpecParser', 'ActionParser', 'ObjParser']

del (TERMINALS, NONTERMINALS, SYMBOLS)
