class Action(object):
    __slots__ = 'action', 'args'

    def __init__(self, action=None, *args):
        self.action = action
        self.args = args

    def get_action(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError


class GlobalAction(Action):
    __slots__ = ()


class BrowserAction(Action):
    __slots__ = ()


class TrackAction(Action):
    __slots__ = 'tracks',

    def __init__(self, action=None, *args, tracks):
        self.tracks = tracks
        super().__init__(args)

    def get_action(self):
        pass

    def run(self):
        pass


class DeviceAction(TrackAction):
    __slots__ = 'devices',

    def __init__(self, action, *args, tracks, devices):
        self.devices = devices
        super().__init__(args, tracks)


class ClipAction(TrackAction):
    __slots__ = 'clips',

    def __init__(self, action, *args, tracks, clips):
        self.clips = clips
        super().__init__(args, tracks)


class NotesAction(ClipAction):
    __slots__ = 'notes',

    def __init__(self, action, *args, tracks, clips, notes):
        self.notes = notes
        super().__init__(args, tracks, clips)

    def iter_target(self):
        for clip in super().iter_target():
            if clip.is_audio:
                continue

    def get_action(self):
        # func = NOTES_ACTIONS[action]
        pass
