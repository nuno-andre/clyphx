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

import os
import logging
from _Generic.Devices import DEVICE_DICT, DEVICE_BOB_DICT, BANK_NAME_DICT
from .consts import LIVE_VERSION

log = logging.getLogger(__name__)

#: Translation table between API names and friendly names.
DEV_NAME_TRANSLATION_TABLE = {
    'UltraAnalog':            'Analog',
    'MidiArpeggiator':        'Arpeggiator',
    'AudioEffectGroupDevice': 'Audio Effect Rack',
    'MidiChord':              'Chord',
    'Compressor2':            'Compressor',
    'DrumGroupDevice':        'Drum Rack',
    'Tube':                   'Dynamic Tube',
    'Eq8':                    'EQ Eight',
    'FilterEQ3':              'EQ Three',
    'LoungeLizard':           'Electric',
    'InstrumentImpulse':      'Impulse',
    'InstrumentGroupDevice':  'Instrument Rack',
    'MidiEffectGroupDevice':  'MIDI Effect Rack',
    'MidiNoteLength':         'Note Length',
    'MidiPitcher':            'Pitch',
    'MidiRandom':             'Random',
    'MultiSampler':           'Sampler',
    'MidiScale':              'Scale',
    'CrossDelay':             'Simple Delay',
    'OriginalSimpler':        'Simpler',
    'SpectrumAnalyzer':       'Spectrum',
    'StringStudio':           'Tension',
    'StereoGain':             'Utility',
    'MidiVelocity':           'Velocity',
    'Vinyl':                  'Vinyl Distortion',
}

#: Header of the HTML file.
HEADER = (
    '<html><h1>Live Instant Mapping Info for Live v{}.{}.{}</h1><br><br>'
    'The following document covers the parameter banks accessible via Live\'s '
    'Instant Mapping feature for each built in device. This info also applies '
    'to controlling device parameters via ClyphX\'s Device Actions.<br><br>'
    '<i><b>NOTE: </b>The order of parameter banks is sometimes changed by '
    'Ableton. If you find the information in this document to be incorrect, you '
    'can recreate it with ClyphX by triggering an action named MAKE_DEV_DOC. '
    'That will create a new version of this file in your user/home directory</i>.'
    '<hr>'
).format(*LIVE_VERSION)


class InstantMappingMakeDoc(object):
    """Creates a HTML file in the user's home directory containing
    information on the parameter banks defined for all Live devices in
    Devices.pyc.
    """

    def __init__(self):
        log.info('InstantMappingMakeDoc initialized.')
        self._create_html_file(self._collect_device_infos())
        log.info('InstantMappingMakeDoc finished.')

    def _collect_device_infos(self):
        """Returns a dict of dicts for each device containing its friendly
        name, bob parameters and bank names/bank parameters if applicable.
        """
        dev_dict = {}
        for k, v in DEVICE_DICT.iteritems():
            has_banks = len(v) > 1
            info = {
                'name':       DEV_NAME_TRANSLATION_TABLE.get(k, k),
                'bob':        DEVICE_BOB_DICT[k][0],
                'bank_names': BANK_NAME_DICT.get(k, ()) if has_banks else (),
                'banks':      (v if has_banks else ()),
            }
            dev_dict[k] = info
        return dev_dict

    def _create_html_file(self, dev_dict):
        """Creates an HTML file in the user's home directory.
        """
        html_file = os.path.join(os.path.expanduser('~'),
                                 'Live Instant Mapping Info.html')
        try:
            with open(html_file, 'w') as f:
                f.write(HEADER)
                f.write('<h2><a id="index">Device Index</a></h2>')
                f.write(''.join(self._get_device_index(dev_dict)))
                f.write('<hr>')
                for key, value in sorted(dev_dict.iteritems(),
                                         key=lambda (k, v): (v['name'], k)):
                    self._write_device_info(f, value)
                f.write('</html>')
        except IOError:
            log.error('IOError: Unable to write file.')

    def _get_device_index(self, dev_dict):
        """Returns a sorted device index for quickly navigating the file.
        """
        # return sorted(map('<a href="#{name}">{name}<br>'.format_map, dev_dict.values()))
        return sorted(['<a href="#{0}">{0}<br>'.format(v['name'])
                       for v in dev_dict.values()])

    def _write_device_info(self, file, info):
        """Writes info to the file for a device."""
        file.write('<h3><a id="{0}">{0}</h3>'.format(info['name']))
        self._write_bank_parameters(file, 'Best Of Banks', info['bob'])
        for i, bank in enumerate(info['bank_names']):
            self._write_bank_parameters(file, 'B{}: {}'.format(i + 1, bank), info['banks'][i])
        file.write('<br><font size=1><a href="#top">Back to Device Index</a></font><hr>')

    def _write_bank_parameters(self, file, bank_name, bank):
        """Writes the bank name and its parameters to the file."""
        params = ['P{}: {}<br>'.format(i + 1, p) for i, p in enumerate(bank) if p]
        file.write('<b>{}</b><br>{}<br>'.format(bank_name, '<br>'.join(params)))
