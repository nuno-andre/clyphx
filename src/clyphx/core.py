from collections import namedtuple
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent


class CsComponent(ControlSurfaceComponent):
    '''Control Surface base component.
    '''
    def __init__(self, parent):
        super(CsComponent, self).__init__()
        self._parent = parent

    def disconnect(self):
        '''Called by the control surface on disconnect (app closed,
        script closed).
        '''
        self._parent = None
        super(CsComponent, self).disconnect()

    def on_enabled_changed(self):
        pass

    def update(self):
        pass


Action = namedtuple('Action', ['track', 'actions', 'args'])
