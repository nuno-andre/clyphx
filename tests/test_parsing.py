from __future__ import absolute_import, unicode_literals


# region USER SETTINGS TEST

RESULT = {
    'snapshot_settings': {
        'include_nested_devices_in_snapshots': True,
        'snapshot_parameter_limit': 500
    },
    'extra_prefs': {
        'process_xclips_if_track_muted': True,
        'startup_actions': False,
        'navigation_highlight': True,
        'exclusive_arm_on_select': False,
        'exclusive_show_group_on_select': False,
        'clip_record_length_set_by_global_quantization': False,
        'default_inserted_midi_clip_length': 0
    },
    'cslinker': {
        'cslinker_matched_link': False,
        'cslinker_horizontal_link': True,
        'cslinker_multi_axis_link': False,
        'cslinker_script_1_name': None,
        'cslinker_script_2_name': None
    },
    'user_controls': {},
    'user_variables': {
        'ex_var1': '10',
        'ex_var2': 'mute'
    },
    'identifier_note': {}
}


def test_user_settings(user_settings):
    from clyphx.core import UserSettings
    cfg = UserSettings(user_settings)

    assert cfg.prefs == cfg.extra_prefs == RESULT['extra_prefs']
    assert cfg.xcontrols == cfg.user_controls == RESULT['user_controls']
    assert cfg.snapshots == cfg.snapshots_settings == RESULT['snapshot_settings']
    assert cfg.cslinker == RESULT['cslinker']
    assert cfg.vars == cfg.user_variables == RESULT['user_variables']
    assert cfg.identifier_note == RESULT['identifier_note']

# endregion

# region USER CONTROLS

def test_user_controls():
    from clyphx.core.models import UserControl, STATUS_BYTE

    TEST = {'no_off': ('NOTE, 1, 10, 1/MUTE ; 2/MUTE',
                       {'status_byte': 144, 'channel': 0, 'value': 10}),
            'off':    ('CC, 16, 117, 1/MUTE ; 2/MUTE : 3/PLAY >',
                       {'status_byte': 176, 'channel': 15, 'value': 117}),
    }

    for name, (data, asserts) in TEST.items():
        uc = UserControl.parse(name, data)
        for attr, val in asserts.items():
            assert getattr(uc, attr) == val

# endregion

# region COMMAND PARSER TEST

def test_tracks():
    from clyphx.core.parse import Parser

    parse = Parser()

    for (source, target) in [
        (
            '[] 1, 3, 5, "My Track", A-MST/MUTE',
            {'on': [['1', '3', '5', '"My Track"', 'A-MST']]},
        ),
        (
            '[] >-5/CLIP(SEL-7) WARP',
            {'on': [['>-5']]},
        ),
        (
            '[] DUMMY : "My Track"/DEV(ALL) OFF',
            {'on': [['"My Track"']]},
        ),
        (
            '[IDENT] REC ON ; 1-2/ARM : UNARM ; 3-4/REC OFF',
            {'on': [None, ['1-2']], 'off': [None, ['3-4']]},
        ),
    ]:
        res = parse(source)
        for step in ('on', 'off'):
            for i, value in enumerate(target.get(step, [])):
                assert getattr(res, step)[i].tracks == value

def test_actions():
    pass

# rendregion
