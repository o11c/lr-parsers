import typing

from typing import (
        List,
)


class LrParserException(Exception):
    pass

class SymbolError(LrParserException):
    pass

class GrammarError(LrParserException):
    pass

class LoweringError(LrParserException):
    pass

class InputError(LrParserException):
    def __init__(self, bad_key: str, good_keys: List[str]) -> None:
        msg = 'got %s; expected one of %s' % (bad_key, ', '.join(good_keys))
        super().__init__(msg)
