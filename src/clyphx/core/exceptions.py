class ClyphXception(Exception):
    pass


class ParsingError(ValueError, ClyphXception):
    pass
