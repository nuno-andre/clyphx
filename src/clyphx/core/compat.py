"""
Python 2.7/3 compatibility module.
"""
from __future__ import unicode_literals
from builtins import super

import sys
import abc
from abc import abstractmethod

try:
    # the raven package is vendorized in Ableton
    from raven.utils.six import iteritems, with_metaclass
except ImportError:
    from six import iteritems

if sys.version_info.major == 3:
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta(b'ABC', (object,), {b'__slots__': ()})
