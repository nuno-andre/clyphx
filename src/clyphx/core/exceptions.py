class ClyphXception(Exception):
    def __init__(self, msg=None, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ParsingError(ClyphXception, ValueError):
    pass


class InvalidSpec(ClyphXception, ValueError):
    pass


class InvalidParam(ClyphXception, ValueError):
    pass


class InvalidAction(ClyphXception, TypeError):
    pass


class ActionUnavailable(ClyphXception, TypeError):
    pass
