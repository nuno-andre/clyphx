from __future__ import absolute_import, unicode_literals
from builtins import dict
from typing import TYPE_CHECKING

from .global_ import XGlobalActions
from .track import XTrackActions
from .clip import XClipActions, NotesMixin
from .device import XDeviceActions
from .dr import XDrActions

if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Text, Optional, Sequence, Tuple
    from ..core.live import Device

    Note = Tuple[int, float, Any, Any, bool]

# NOTE: Action names and their corresponding values can't contain a '/' or '-'
#       within the first four chars like this 'EX/ONE', but 'EXMP/ONE' is okay.

GLOBAL_ACTIONS = dict(
    ASN          = XGlobalActions.do_variable_assignment,
    ADDAUDIO     = XGlobalActions.create_audio_track,
    ADDMIDI      = XGlobalActions.create_midi_track,
    INSAUDIO     = XGlobalActions.insert_and_configure_audio_track,
    INSMIDI      = XGlobalActions.insert_and_configure_midi_track,
    ADDRETURN    = XGlobalActions.create_return_track,
    ADDSCENE     = XGlobalActions.create_scene,
    DELSCENE     = XGlobalActions.delete_scene,
    DUPESCENE    = XGlobalActions.duplicate_scene,
    LOADDEV      = XGlobalActions.load_device,
    LOADM4L      = XGlobalActions.load_m4l,
    SWAP         = XGlobalActions.swap_device_preset,
    SREC         = XGlobalActions.set_session_record,
    SRECFIX      = XGlobalActions.trigger_session_record,
    SATM         = XGlobalActions.set_session_automation_record,
    B2A          = XGlobalActions.set_back_to_arrange,
    RPT          = XGlobalActions.set_note_repeat,
    SWING        = XGlobalActions.adjust_swing,
    BPM          = XGlobalActions.adjust_tempo,
    DEVFIRST     = XGlobalActions.move_to_first_device,
    DEVLAST      = XGlobalActions.move_to_last_device,
    DEVLEFT      = XGlobalActions.move_to_prev_device,
    DEVRIGHT     = XGlobalActions.move_to_next_device,
    FOCBRWSR     = XGlobalActions.focus_browser,
    FOCDETAIL    = XGlobalActions.focus_detail,
    FOCMAIN      = XGlobalActions.focus_main,
    GQ           = XGlobalActions.adjust_global_quantize,
    GRV          = XGlobalActions.adjust_groove,
    HZOOM        = XGlobalActions.adjust_horizontal_zoom,
    VZOOM        = XGlobalActions.adjust_vertical_zoom,
    UP           = XGlobalActions.move_up,
    DOWN         = XGlobalActions.move_down,
    LEFT         = XGlobalActions.move_left,
    RIGHT        = XGlobalActions.move_right,
    LOOP         = XGlobalActions.do_loop_action,
    LOC          = XGlobalActions.do_locator_action,
    LOCLOOP      = XGlobalActions.do_locator_loop_action,
    METRO        = XGlobalActions.set_metronome,
    MIDI         = XGlobalActions.send_midi_message,
    OVER         = XGlobalActions.set_overdub,
    PIN          = XGlobalActions.set_punch_in,
    POUT         = XGlobalActions.set_punch_out,
    REC          = XGlobalActions.set_record,
    REDO         = XGlobalActions.set_redo,
    UNDO         = XGlobalActions.set_undo,
    RESTART      = XGlobalActions.restart_transport,
    RQ           = XGlobalActions.adjust_record_quantize,
    RTRIG        = XGlobalActions.retrigger_recording_clips,
    SIG          = XGlobalActions.adjust_time_signature,
    SCENE        = XGlobalActions.set_scene,
    SHOWCLIP     = XGlobalActions.show_clip_view,
    SHOWDEV      = XGlobalActions.show_track_view,
    SHOWDETAIL   = XGlobalActions.show_detail_view,
    TGLBRWSR     = XGlobalActions.toggle_browser,
    TGLDETAIL    = XGlobalActions.toggle_detail_view,
    TGLMAIN      = XGlobalActions.toggle_main_view,
    STOPALL      = XGlobalActions.set_stop_all,
    SETCONT      = XGlobalActions.set_continue_playback,
    SETLOC       = XGlobalActions.set_locator,
    SETSTOP      = XGlobalActions.set_stop_transport,
    SETFOLD      = XGlobalActions.set_fold_all,
    SETJUMP      = XGlobalActions.set_jump_all,
    TAPBPM       = XGlobalActions.set_tap_tempo,
    UNARM        = XGlobalActions.set_unarm_all,
    UNMUTE       = XGlobalActions.set_unmute_all,
    UNSOLO       = XGlobalActions.set_unsolo_all,
    MAKE_DEV_DOC = XGlobalActions.make_instant_mapping_docs,
)  # type: Dict[Text, Callable]

SCENE_ACIONS = dict(
    ADD  = XGlobalActions.create_scene,
    DEL  = XGlobalActions.delete_scene,
    DUPE = XGlobalActions.duplicate_scene,
)

TRACK_ACTIONS = dict(
    ARM       = XTrackActions.set_arm,
    MUTE      = XTrackActions.set_mute,
    SOLO      = XTrackActions.set_solo,
    MON       = XTrackActions.set_monitor,
    XFADE     = XTrackActions.set_xfade,
    SEL       = XTrackActions.set_selection,
    ADDCLIP   = XTrackActions.create_clip,
    DEL       = XTrackActions.delete_track,
    DELDEV    = XTrackActions.delete_device,
    DUPE      = XTrackActions.duplicate_track,
    FOLD      = XTrackActions.set_fold,
    PLAY      = XTrackActions.set_play,
    PLAYL     = XTrackActions.set_play_w_legato,
    PLAYQ     = XTrackActions.set_play_w_force_qntz,
    PLAYLQ    = XTrackActions.set_play_w_force_qntz_and_legato,
    STOP      = XTrackActions.set_stop,
    JUMP      = XTrackActions.set_jump,
    VOL       = XTrackActions.adjust_volume,
    PAN       = XTrackActions.adjust_pan,
    SEND      = XTrackActions.adjust_sends,
    CUE       = XTrackActions.adjust_preview_volume,
    XFADER    = XTrackActions.adjust_crossfader,
    IN        = XTrackActions.adjust_input_routing,
    INSUB     = XTrackActions.adjust_input_sub_routing,
    OUT       = XTrackActions.adjust_output_routing,
    OUTSUB    = XTrackActions.adjust_output_sub_routing,
    NAME      = XTrackActions.set_name,
    RENAMEALL = XTrackActions.rename_all_clips,
)  # type: Dict[Text, Callable]

CLIP_ACTIONS = dict(
    CENT     = XClipActions.adjust_detune,
    SEMI     = XClipActions.adjust_transpose,
    GAIN     = XClipActions.adjust_gain,
    CUE      = XClipActions.adjust_cue_point,
    END      = XClipActions.adjust_end,
    START    = XClipActions.adjust_start,
    GRID     = XClipActions.adjust_grid_quantization,
    TGRID    = XClipActions.set_triplet_grid,
    ENVINS   = XClipActions.insert_envelope,
    ENVCLR   = XClipActions.clear_envelope,
    ENVCAP   = XClipActions.capture_to_envelope,
    ENVSHOW  = XClipActions.show_envelope,
    ENVHIDE  = XClipActions.hide_envelopes,
    QNTZ     = XClipActions.quantize,
    EXTEND   = XClipActions.duplicate_clip_content,
    DEL      = XClipActions.delete_clip,
    DUPE     = XClipActions.duplicate_clip,
    CHOP     = XClipActions.chop_clip,
    CROP     = XClipActions.crop,
    SPLIT    = XClipActions.split_clip,
    WARPMODE = XClipActions.adjust_warp_mode,
    LOOP     = XClipActions.do_clip_loop_action,
    SIG      = XClipActions.adjust_time_signature,
    WARP     = XClipActions.set_warp,
    NAME     = XClipActions.set_clip_name,
    # TOMIDI   = XClipActions.to_midi,
    TODR     = XClipActions.to_drum_rack,
    TOSIMP   = XClipActions.to_simpler,
)  # type: Dict[Text, Callable]

NOTES_ACTIONS = dict([
    ('REV',   NotesMixin.do_note_reverse),
    ('INV',   NotesMixin.do_note_invert),
    ('COMP',  NotesMixin.do_note_compress),
    ('EXP',   NotesMixin.do_note_expand),
    ('GATE',  NotesMixin.do_note_gate_adjustment),
    ('NUDGE', NotesMixin.do_note_nudge_adjustment),
    ('SCRN',  NotesMixin.do_pitch_scramble),
    ('SCRP',  NotesMixin.do_position_scramble),
    ('CMB',   NotesMixin.do_note_combine),
    ('SPLIT', NotesMixin.do_note_split),
    ('DEL',   NotesMixin.do_note_delete),
    ('VELO',  NotesMixin.do_note_velo_adjustment),
    ('ON',    NotesMixin.set_notes_on_off),
    ('OFF',   NotesMixin.set_notes_on_off),
    (None,    NotesMixin.set_notes_on_off),
    ('',      NotesMixin.set_notes_on_off),
])  # type: Dict[Text, Callable[[Clip, Any], List[None]]]


DEVICE_ACTIONS = dict(
    CSEL  = XDeviceActions.adjust_selected_chain,
    CS    = XDeviceActions.adjust_chain_selector,
    RESET = XDeviceActions.reset_params,
    RND   = XDeviceActions.randomize_params,
    SEL   = XDeviceActions.select_device,
    SET   = XDeviceActions.set_all_params,
    P1    = XDeviceActions.adjust_bob_param,
    P2    = XDeviceActions.adjust_bob_param,
    P3    = XDeviceActions.adjust_bob_param,
    P4    = XDeviceActions.adjust_bob_param,
    P5    = XDeviceActions.adjust_bob_param,
    P6    = XDeviceActions.adjust_bob_param,
    P7    = XDeviceActions.adjust_bob_param,
    P8    = XDeviceActions.adjust_bob_param,
    B1    = XDeviceActions.adjust_banked_param,
    B2    = XDeviceActions.adjust_banked_param,
    B3    = XDeviceActions.adjust_banked_param,
    B4    = XDeviceActions.adjust_banked_param,
    B5    = XDeviceActions.adjust_banked_param,
    B6    = XDeviceActions.adjust_banked_param,
    B7    = XDeviceActions.adjust_banked_param,
    B8    = XDeviceActions.adjust_banked_param,
)  # type: Dict[Text, Callable]

LOOPER_ACTIONS = dict(
    LOOPER = XDeviceActions.set_looper_on_off,
    REV    = XDeviceActions.set_looper_rev,
    OVER   = XDeviceActions.set_looper_state,
    PLAY   = XDeviceActions.set_looper_state,
    REC    = XDeviceActions.set_looper_state,
    STOP   = XDeviceActions.set_looper_state,
)  # type: Dict[Text, Callable[[XDeviceActions, Optional[Text]], None]]

DR_ACTIONS = dict(
    SCROLL = XDrActions.scroll_selector,
    UNMUTE = XDrActions.unmute_all,
    UNSOLO = XDrActions.unsolo_all,
)  # type: Dict[Text, Callable[[XDrActions, Device, Optional[Text]], None]]

PAD_ACTIONS = dict(
    MUTE = XDrActions._mute_pads,
    SOLO = XDrActions._solo_pads,
    VOL  = XDrActions._adjust_pad_volume,
    PAN  = XDrActions._adjust_pad_pan,
    # TODO: SEL, SEND
)  # type: Dict[Text, Callable[[XDrActions, Sequence[Any], Optional[Text]], None]]
