# type: ignore
#
# Copyright 2015 Armin Ronacher
# Some rights reserved. See LICENSE
# SPDX-License-Identifier: BSD-3-Clause
#
# https://github.com/nuno-andre/python-regex-scanner

from __future__ import unicode_literals

# Pattern renamed back to State in 3.8.
try:
    from sre_parse import State, SubPattern, parse
except ImportError:
    from sre_parse import Pattern as State, SubPattern, parse
from sre_compile import compile as sre_compile
from sre_constants import BRANCH, SUBPATTERN

# Flags to support modifier spans. Since 3.6
import sre_parse

if hasattr(sre_parse, 'GLOBAL_FLAGS'):
    def subpatternsappend(subpatterns, group, action, flags, state):
        subpatterns.append(SubPattern(state, [
            (SUBPATTERN, (group, 0, 0, parse(action, flags, state))),
        ]))
else:
    def subpatternsappend(subpatterns, group, action, flags, state):
        subpatterns.append(SubPattern(state, [
            (SUBPATTERN, (group, parse(action, flags, state))),
        ]))


class ScanMatch(object):
    __slots__ = ['_match', '_start', '_end', '_action']

    def __init__(self, match, action, start, end):
        self._match = match
        self._start = start
        self._end = end
        self._action = action

    def __getattr__(self, name):
        return getattr(self._match, name)

    def _group_proc(self, method, group):
        if group == 0:
            return method()
        if isinstance(group, (str, bytes)):
            return method('{}\x00{}'.format(self._action, group))
        real_group = self._start + group
        if real_group > self._end:
            raise IndexError('no such group')
        return method(real_group)

    def group(self, *groups):
        if not groups:
            return self._group_proc(self._match.group, 0)
        elif len(groups) == 1:
            return self._group_proc(self._match.group, groups)
        return tuple(self._group_proc(self._match.group, g) for g in groups)

    def groupdict(self, default=None):
        prefix = '{}\x00'.format(self._action)
        preflen = len(prefix)

        return {k[preflen:]: v
                for k, v in self._match.groupdict(default).items()
                if k[:preflen] == prefix}

    def span(self, group=0):
        return self._group_proc(self._match.span, group)

    def groups(self):
        return self._match.groups()[self._start:self._end]

    def start(self, group=0):
        return self._group_proc(self._match.start, group)

    def end(self, group=0):
        return self._group_proc(self._match.end, group)

    def expand(self, template):
        raise RuntimeError('Unsupported on scan matches')


class ScanEnd(Exception):

    def __init__(self, pos):
        Exception.__init__(self, pos)
        self.pos = pos


class Scanner(object):

    def __init__(self, lexicon, flags=0):
        self.lexicon = list()
        subpatterns = list()   # type: List[SubPattern]

        state = State()
        state.flags = flags
        _og = state.opengroup

        def _opengroup(n=None):
            return _og(n and '%s\x00%s' % (action, n) or n)

        state.opengroup = _opengroup

        for group, (action, phrase) in enumerate(lexicon, 1):
            state.opengroup()
            last_group = state.groups - 1
            subpatternsappend(subpatterns, group, phrase, flags, state)
            self.lexicon.append((action, last_group, state.groups - 1))

        subpatterns = SubPattern(state, [(BRANCH, (None, subpatterns))])
        self._scanner = sre_compile(subpatterns).scanner

    def scan(self, string, skip=False):
        sc = self._scanner(string)

        match = None
        for match in iter(sc.search if skip else sc.match, None):
            action, start, end = self.lexicon[match.lastindex - 1]
            yield action, ScanMatch(match, action, start, end)

        if not skip:
            end = match and match.end() or 0
            if end < len(string):
                raise ScanEnd(end)

    def scan_with_holes(self, string):
        pos = 0
        for action, match in self.scan(string, skip=True):
            hole = string[pos:match.start()]
            if hole:
                yield None, hole
            yield action, match
            pos = match.end()
        hole = string[pos:]
        if hole:
            yield None, hole
