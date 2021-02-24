class ClyphXception(Exception):
    def __init__(self, msg=None, *args, **kwargs):
        suoer().__init__(*args, **kwargs)

class ParsingError(ClyphXception, ValueError):
    pass

class InvalidSpec(ClyphXception, ValueError):
    pass

class InvalidParam(ClyphXception, ValueError):
    pass
