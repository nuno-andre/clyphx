from __future__ import absolute_import, unicode_literals
from typing import TYPE_CHECKING

# TODO: get from .consts.DEVICE_BANKS
from _Generic.Devices import DEVICE_DICT, DEVICE_BOB_DICT, BANK_NAME_DICT
from .consts import LIVE_VERSION, DEV_NAME_TRANSLATION

if TYPE_CHECKING:
    from typing import Union, Optional, List, Tuple, Text
    Output = List[Tuple[Text, List[Tuple[Tuple[Text, Text], List[Tuple[Text, Text]]]]]]


TEMPLATE = '''\
Live Instant Mapping Info for Ableton Live v{}
============================================{}

The following document covers the parameter banks accessible via Ableton Live's
_Instant Mapping_ feature for each built in device. This info also applies to
controlling device parameters via **ClyphX**'s _Device Actions_.

> **NOTE:** The order of parameter banks is sometimes changed by Ableton. If you
find the information in this document to be incorrect, you can recreate it with
**ClyphX** by triggering an action named `MAKE_DEV_DOC`. That will create a new
version of this file in your user/home directory.

* * *

Device Index
------------
'''


def to_markdown(data, tables=False):
    # type: (Output, bool) -> Text
    index = []
    output = []

    for dev, banks in data:
        index.append('[{}](#{})  '.format(dev, dev.lower().replace(' ', '-')))
        output.append('\n* * *\n\n## {}'.format(dev))

        if tables:
            table = ['|'] * 10
            for bank, params in banks:
                width = max(len(x[1]) for x in [bank] + params)
                table[0] += ' `{0}`: {1: <{2}} |'.format(*(bank + (width,)))
                table[1] += ' :{} |'.format('-' * (width + 5))
                for i, param in enumerate(params, 2):
                    table[i] += ' `{0}`: {1: <{2}} |'.format(*(param + (width,)))
            output.extend([''] + table)

        else:
            for bank, params in banks:
                output.append('\n### `{}`: {}\n'.format(*bank))
                for param in params:
                    output.append('`{}`: {}  '.format(*param))

        output.append('\n[Back to Device Index](#device-index)')

    version = '.'.join(map(str, LIVE_VERSION))
    header = TEMPLATE.format(version, '=' * len(version))
    return header + '\n'.join(index + output)


def get_device_params(format=None, tables=False):
    # type: (Optional[Text], bool) -> Union[Output, Text]
    '''Returns the banks and params of Live devices.

    Default format:

        [device, [(Bn, bank), [(Pn, param), ...]]]

    ``B0`` is _Best of Banks_.
    '''
    devname = lambda dev: DEV_NAME_TRANSLATION.get(dev, dev)
    devices = [((devname(d), d), b) for d, b in DEVICE_DICT.items()]

    banks = list()

    for (name, dev), bank_params in sorted(devices):
        if dev.endswith('GroupDevice'):
            # just "Macro n"
            continue

        # TODO: check if devices with unnamed banks have only one bank and B1 == B0 (BoB)
        bank_names = ('Best of Banks',) + BANK_NAME_DICT.get(dev, ('',) * len(bank_params))
        bank_names = [('B{}'.format(i), b) for i, b in enumerate(bank_names)]

        bank_params = (DEVICE_BOB_DICT[dev][0],) + bank_params
        bank_params = [[('P{}'.format(i), p) for i, p in enumerate(bank, 1)] for bank in bank_params]

        banks.append((name, list(zip(bank_names, bank_params))))

    if format and format.lower() in {'md', 'markdown'}:
        return to_markdown(banks, tables=tables)

    return banks
