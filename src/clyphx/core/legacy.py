# coding: utf-8
#
# Copyright (c) 2020-2021 Nuno André Novo
# Some rights reserved. See COPYING, COPYING.LESSER
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import absolute_import, unicode_literals
from typing import TYPE_CHECKING
from builtins import object, super
import logging

from .utils import repr_tracklist

if TYPE_CHECKING:
    from typing import Text, Sequence, Iterator
    from .live import Track, Clip

log = logging.getLogger(__name__)


class _DispatchCommand(object):
    '''Action dispatching command transition class.
    '''
    def __init__(self, tracks, xclip, ident, action_name, args):
        # type: (Sequence[Track], Clip, Text, Text, Text) -> None
        self.tracks = tracks
        self.xclip = xclip  # TODO: xtrigger
        self.ident = ident
        self.action_name = action_name
        self.args = args.strip()

    def __repr__(self):
        # type: () -> str
        return str('_DispatchCommand(tracks={}, xclip={}, {})'.format(
            repr_tracklist(self.tracks),
            self.xclip.name if self.xclip else '',
            ', '.join('{}={}'.format(k, self.__dict__[str(k)])
                         for k in ('ident', 'action_name', 'args')),
        ))

    def __iter__(self):
        # type: () -> Iterator[_SingleDispatch]
        for i, t in enumerate(self.tracks):
            yield _SingleDispatch(t, self.xclip, self.ident, self.action_name, self.args)

    def to_single(self):
        # type: () -> _SingleDispatch
        return _SingleDispatch(self.tracks[0], self.xclip, self.ident, self.action_name, self.args)


class _SingleDispatch(_DispatchCommand):
    '''Dispatch command for a single track.
    '''
    def __init__(self, track, xclip, ident, action_name, args):
        if isinstance(track, list):
            # FIXME:
            if len(track) == 1:
                track = track[0]
            else:
                msg = 'SingleDispatch should receive an only track: {}'
                raise TypeError(msg.format(track))
        super().__init__([track], xclip, ident, action_name, args)
        self.track = track
