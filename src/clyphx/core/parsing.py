from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from typing import Text, Iterable
    from core.live import Clip, Track

log = logging.getLogger(__name__)


def get_xclip_action_list(xclip, full_action_list):
    # type: (Clip, Text) -> Text
    '''Get the action list to perform.

    X-Clips can have an on and off action list separated by a comma.
    This will return which action list to perform based on whether
    the clip is playing. If the clip is not playing and there is no
    off action, this returns None.
    '''
    log.debug('get_xclip_action_list(xclip=%r, full_action_list=%s', xclip, full_action_list)
    split_list = full_action_list.split(',')

    if xclip.is_playing:
        result = split_list[0]
    elif len(split_list) == 2:
        if split_list[1].strip() == '*':
            result = split_list[0]
        else:
            result = split_list[1]
    else:
        # FIXME: shouldn't be None
        result = ''

    log.debug('get_xclip_action_list returning %s', result)
    return result


def track_list_to_string(track_list):
    # type: (Iterable[Track]) -> Text
    '''Convert list of tracks to a string of track names or 'None' if
    no tracks. This is used for debugging.
    '''
    # TODO: if no track_list result is 'None]'
    result = 'None'
    if track_list:
        result = '['
        for track in track_list:
            result += '{}, '.format(track.name)
        result = result[:len(result)-2]
    return result + ']'
