# pyright: reportUnusedImport=false
from __future__ import absolute_import, unicode_literals


import Live

try:
    from Live.Application import (
        Application, get_application,
        get_random_int,
    )
    from Live.Browser import (
        Browser, BrowserItem, FilterType, Relation
    )
    from Live.Chain import Chain
    from Live.Clip import Clip, AutomationEnvelope, GridQuantization, WarpMode
    from Live.CompressorDevice import CompressorDevice
    from Live.Device import Device, DeviceType
    from Live.DeviceIO import DeviceIO
    from Live.DeviceParameter import DeviceParameter, ParameterState, AutomationState
    from Live.DrumPad import DrumPad
    from Live.LomObject import LomObject
    from Live.MidiMap import (
        forward_midi_cc,
        forward_midi_note,
    )
    from Live.MixerDevice import MixerDevice
    from Live.RackDevice import RackDevice
    from Live.Scene import Scene
    from Live.Sample import Sample, TransientLoopMode, SlicingStyle, SlicingBeatDivision
    from Live.SimplerDevice import SimplerDevice, SlicingPlaybackMode, PlaybackMode
    from Live.Song import Song, RecordingQuantization
    from Live.Track import (
        Track, DeviceContainer, RoutingTypeCategory,
        RoutingChannelLayout, DeviceInsertMode,
    )
except ImportError:
    # import modules
    from Live import (
        Application,
        Browser,
        Chain,
        Clip,
        CompressorDevice,
        Device,
        DeviceIO,
        DeviceParameter,
        DrumChain,
        DrumPad,
        Eq8Device,
        LomObject,
        MidiMap,
        MixerDevice,
        PluginDevice,
        RackDevice,
        Sample,
        Scene,
        SimplerDevice,
        Song,
        Track,
        WavetableDevice,
    )

    # import classes and functions
    from Application import (
        Application,
        get_application,
        get_random_int,
    )
    from Browser import (
        Browser, BrowserItem, FilterType, Relation
    )
    from Chain import Chain
    from Clip import Clip, AutomationEnvelope, GridQuantization, WarpMode
    from CompressorDevice import CompressorDevice
    from Device import Device, DeviceType
    from DeviceParameter import DeviceParameter, ParameterState, AutomationState
    from DrumPad import DrumPad
    from LomObject import LomObject
    from MidiMap import (
        forward_midi_cc,
        forward_midi_note,
    )
    from MixerDevice import MixerDevice
    from RackDevice import RackDevice
    from Sample import Sample, TransientLoopMode, SlicingStyle, SlicingBeatDivision
    from Scene import Scene
    from SimplerDevice import SimplerDevice, SlicingPlaybackMode, PlaybackMode
    from Song import Song, RecordingQuantization
    from Track import (
        Track, DeviceContainer, RoutingTypeCategory,
        RoutingChannelLayout, DeviceInsertMode,
    )
    from MidiRemoteScript import MidiRemoteScript
