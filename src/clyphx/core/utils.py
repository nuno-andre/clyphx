from __future__ import absolute_import, unicode_literals
from typing import TYPE_CHECKING
import logging
import os

if TYPE_CHECKING:
    from typing import Text, TypeVar, Iterable
    from .live import Track
    T = TypeVar('T')

log = logging.getLogger(__name__)


def repr_slots(self):
    # type: (T) -> str
    return str('{}({})'.format(
        type(self).__name__,
        ', '.join('{}={}'.format(k, getattr(self, k))
                    for k in self.__slots__),
    ))


def repr_tracklist(tracks):
    # type: (Iterable[Track]) -> Text
    '''Convert list of tracks to a string of track names or 'None' if
    no tracks. This is used for debugging.
    '''
    if not tracks:
        return '[None]'
    else:
        return '[{}]'.format(', '.join(t.name for t in tracks))


def get_base_path(*items):
    # type: (Text) -> Text
    here = os.path.dirname(os.path.realpath(__file__))
    dest = os.path.join(here, os.pardir, *items)
    return os.path.realpath(dest)
