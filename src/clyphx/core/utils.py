from __future__ import absolute_import, unicode_literals
from typing import TYPE_CHECKING
import logging
import os

from ..consts import SCRIPT_NAME

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
        try:
            return '[{}]'.format(', '.join(t.name for t in tracks))
        except Exception:
            return '[ERROR {}]'.format(tracks)


def get_base_path(*items):
    # type: (Text) -> Text
    here = os.path.dirname(os.path.realpath(__file__))
    dest = os.path.join(here, os.pardir, *items)
    return os.path.realpath(dest)


def get_user_clyphx_path(*items):
    name = '.' + SCRIPT_NAME.lower()
    base = os.path.join(os.path.expanduser('~'), name)
    dest = os.path.join(base, *items)
    return os.path.realpath(dest)


def set_user_profile():
    path = get_user_clyphx_path()
    if not os.path.exists(path):
        os.mkdir(path)
        os.mkdir(os.path.join(path, 'log'))


def logger():
    pass
