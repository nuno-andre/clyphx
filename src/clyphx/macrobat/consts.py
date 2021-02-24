from __future__ import absolute_import, unicode_literals
from collections import OrderedDict
from builtins import dict

from .midi_rack import MacrobatMidiRack
from .push_rack import MacrobatPushRack
from .rnr_rack import MacrobatRnRRack
from .sidechain_rack import MacrobatSidechainRack
from .parameter_racks import (
    MacrobatLearnRack, MacrobatChainMixRack, MacrobatDRMultiRack,
    MacrobatDRRack, MacrobatReceiverRack, MacrobatTrackRack,
    MacrobatChainSelectorRack, MacrobatDRPadMixRack,
)


MACROBAT_RACKS = OrderedDict([
    ('NK RECEIVER',   MacrobatReceiverRack),  # param rack
    ('NK TRACK',      MacrobatTrackRack),     # param rack
    ('NK DR PAD MIX', MacrobatDRPadMixRack),  # param rack
    ('NK DR MULTI',   MacrobatDRMultiRack),   # param rack
    ('NK CHAIN MIX',  MacrobatChainMixRack),  # param rack
    ('NK DR',         MacrobatDRRack),        # param rack
    ('NK LEARN',      MacrobatLearnRack),     # param rack
    ('NK MIDI',       MacrobatMidiRack),
    ('NK RST',        MacrobatRnRRack),    # RnR
    ('NK RND',        MacrobatRnRRack),    # RnR
    ('NK SIDECHAIN',  MacrobatSidechainRack),
    ('NK SCL',        MacrobatPushRack),
    ('NK CS',         MacrobatChainSelectorRack),  # param rack
])


# {param: (mess_type, reset)}
RNR_ON_OFF = dict([
    ('NK RND ALL', ('all',  False)),
    ('NK RND',     ('next', False)),
    ('NK RST ALL', ('all',  True)),
    ('NK RST',     ('next', True)),
])
