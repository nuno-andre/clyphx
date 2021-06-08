# -*- coding: utf-8 -*-
# This file is part of ClyphX.
#
# ClyphX is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# ClyphX is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ClyphX.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals
from typing import TYPE_CHECKING
from builtins import dict
import logging

if TYPE_CHECKING:
    from typing import Any, List, Dict, Text

from _Generic.Devices import (DEVICE_DICT, DEVICE_BOB_DICT, BANK_NAME_DICT)
from .consts import LIVE_VERSION, DEV_NAME_TRANSLATION
from .core.utils import get_user_clyphx_path

log = logging.getLogger(__name__)

TEMPLATE = '''\
<html><h1>Live Instant Mapping Info for Live {version}</h1>
<br><br>
The following document covers the parameter banks accessible via Live's Instant
Mapping feature for each built in device. This info also applies to controlling
device parameters via ClyphX's Device Actions.
<br><br>
<i><b>NOTE: </b>The order of parameter banks is sometimes changed by Ableton.
If you find the information in this document to be incorrect, you can recreate
it with ClyphX by triggering an action named MAKE_DEV_DOC. That will create a
new version of this file in your user/home directory</i>.
<hr>
<h2><a id="index">Device Index</a></h2>
{index}
<hr>
{devices}
</html>
'''


class InstantMappingMakeDoc(object):
    '''Creates a HTML file in the user's home directory containing
    information on the parameter banks defined for all Live devices in
    Devices.pyc.
    '''

    def __init__(self):
        self._create_html_file()

    def _get_devices_info(self):
        # type: () -> Dict[Text, Dict[Text, Any]]
        '''Returns a dict of dicts for each device containing its
        friendly name, bob parameters and bank names/bank parameters if
        applicable.
        '''
        return dict((k, dict(name=DEV_NAME_TRANSLATION.get(k, k),
                             bob=DEVICE_BOB_DICT[k][0],
                             bank_names=BANK_NAME_DICT.get(k, ()) if len(v) > 1 else (),
                             banks=v if len(v) > 1 else ()))
                     for k, v in DEVICE_DICT.items())

    def _get_device_index(self, dev_dict):
        '''Returns a sorted device index for quickly navigating the file.
        '''
        return sorted('<a href="#{0}">{0}<br>'.format(v['name'])
                      for v in dev_dict.values())

    def _get_bank_params(self, bank):
        # type: (List[Any]) -> Text
        return '<br>'.join('P{}: {}<br>'.format(i + 1, p)
                           for i, p in enumerate(bank) if p)

    def _get_banks_info(self, info):
        '''Returns the bank name and its parameters.'''
        template = '<b>B{}: {}</b><br>{}<br>'

        return (template.format(i + 1, b, self._get_bank_params(info['banks'][i]))
                for i, b in enumerate(info['bank_names']))

    def _get_device_info(self, info):
        '''Returns formatted info on a device.'''
        template = '''\
            <h3><a id="{device}">{device}</h3>
            <b>Best Of Banks</b>
            <br>{bob}<br>
            {banks}
            <br><font size=1><a href="#top">Back to Device Index</a></font><hr>
        '''

        return template.format(
            device=info['name'],
            bob=self._get_bank_params(info['bob']),
            banks='\n'.join(self._get_banks_info(info)),
        )

    def _format_devices_info(self, dev_dict):
        ## type: (Dict[Text, Dict]) -> List[Text]
        # FIXME: mypy doesn't like
        ##return [self._get_device_info(info) for _, info in sorted(dev_dict.items(), key=lambda k, v: v['name'], k)]
        pass

    def _create_html_file(self):
        '''Creates an HTML file in the user's home directory.
        '''
        dev_dict = self._get_devices_info()
        html_file = get_user_clyphx_path('Live Instant Mapping Info.html')

        data = dict(
            version = 'v{}.{}.{}'.format(*LIVE_VERSION),
            index   = ''.join(self._get_device_index(dev_dict)),
            devices = '\n'.join(self._format_devices_info(dev_dict)),
        )

        try:
            with open(html_file, 'w') as f:
                f.write(TEMPLATE.format(**data))
        except IOError:
            log.error('IOError: Unable to write file.')
