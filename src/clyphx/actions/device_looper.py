from __future__ import absolute_import, unicode_literals
from builtins import object

from ..consts import LOOPER_STATES, switch


# TODO: turn into a component?
class LooperMixin(object):

    def dispatch_looper_actions(self, cmd):
        # type: (_DispatchCommand) -> None
        from .consts import LOOPER_ACTIONS

        assert cmd.action_name == 'LOOPER'
        if cmd.args and cmd.args.split()[0] in LOOPER_ACTIONS:
            action = LOOPER_ACTIONS[cmd.args.split()[0]]
        else:
            action = LOOPER_ACTIONS[cmd.action_name]
        for scmd in cmd:
            self.get_looper(scmd.track)
            action(self, scmd.args)

    def get_looper(self, track):
        # type: (Track) -> None
        '''Get first looper device on track and its params.'''
        self._looper_data = dict()
        for d in track.devices:
            if d.class_name == 'Looper':
                self._looper_data['Looper'] = d
                for p in d.parameters:
                    if p.name in ('Device On', 'Reverse', 'State'):
                        self._looper_data[p.name] = p
                break
            elif (not self._looper_data and
                    self._parent._can_have_nested_devices and
                    d.can_have_chains and d.chains):
                for c in d.chains:
                    self.get_looper(c)

    def get_param(self, name):
        if not (self._looper_data and self._looper_data['Looper']):
            raise AttributeError('No looper data')
        param = self._looper_data[name]
        if not param.is_enabled:
            raise AttributeError("'{}' is not enabled".format(name))
        return param

    def set_looper_on_off(self, value=None):
        # type: (Optional[Text]) -> None
        '''Toggles or turns looper on/off.'''
        switch(self.get_param('Device On'), 'value', value)

    def set_looper_rev(self, value=None):
        # type: (Optional[Text]) -> None
        '''Toggles or turns looper reverse on/off.'''
        switch(self.get_param('Reverse'), 'value', value)

    def set_looper_state(self, value=None):
        # type: (Optional[Text]) -> None
        '''Sets looper state.'''
        try:
            self.get_param('State').value = LOOPER_STATES[value.upper()]
        except KeyError:
            raise ValueError("'{}' is not a looper state".format(value))
