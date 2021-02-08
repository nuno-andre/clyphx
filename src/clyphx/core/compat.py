"""
Python 2.7/3 compatibility module.
"""
from __future__ import unicode_literals, absolute_import
from builtins import super

import sys
import abc
from abc import abstractmethod

if sys.version_info.major == 3:
    ABC = abc.ABC  # type: ignore
else:
    ABC = abc.ABCMeta(b'ABC', (object,), {b'__slots__': ()})

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser
