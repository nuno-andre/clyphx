import os
import logging
from collections import OrderedDict

from .compat import iteritems

log = logging.getLogger(__name__)


def get_python_info():
    '''Returns info about the Live Python runtime.
    '''
    import sys

    version_info = OrderedDict((k, getattr(sys.version_info, k)) for k in
                               ('major', 'minor', 'micro', 'releaselevel', 'serial'))

    modules = OrderedDict((k, {'module': getattr(v, '__name__', None),
                               'file': getattr(v, '__file__', None)})
                          for k, v in sorted(iteritems(sys.modules)))

    return OrderedDict([
        ('version',         sys.version),
        ('version_info',    version_info),
        ('path',            sys.path),
        ('executable',      sys.executable),
        #('dllhandle',       sys.dllhandle),
        ('prefix',          sys.prefix),
        ('exec_prefix',     sys.exec_prefix),
        ('builtin_modules', sys.builtin_module_names),
        ('modules',         modules),
    ])


def show_python_info():
    import json

    log.info(json.dumps(get_python_info(), indent=4))


def repr(self):
    return '{}({})'.format(
        type(self).__name__,
        ', '.join('{}={}'.format(k, getattr(self, k))
                    for k in self.__slots__),
    )


def get_base_path(*items):
    here = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(here, os.pardir, *items)
