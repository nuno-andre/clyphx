from __future__ import absolute_import, unicode_literals
from typing import TYPE_CHECKING
import logging
import os

if TYPE_CHECKING:
    from typing import Text, TypeVar
    T = TypeVar('T')

log = logging.getLogger(__name__)


def repr_slots(self):
    # type: (T) -> str
    return str('{}({})'.format(
        type(self).__name__,
        ', '.join('{}={}'.format(k, getattr(self, k))
                    for k in self.__slots__),
    ))


def get_base_path(*items):
    # type: (Text) -> Text
    here = os.path.dirname(os.path.realpath(__file__))
    dest = os.path.join(here, os.pardir, *items)
    return os.path.realpath(dest)
