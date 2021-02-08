from __future__ import absolute_import, unicode_literals
import sys
import os

import  pytest

HERE = os.path.dirname(os.path.realpath(__file__))
CODE = os.path.realpath(os.path.join(HERE, '..', 'src'))

sys.path.insert(0, str(CODE))


@pytest.fixture(scope='session')
def user_settings():
    here = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(here, 'fixtures', 'UserSettings.txt')
