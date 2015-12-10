class LrParserException(Exception):
    pass

class SymbolError(LrParserException):
    pass

class GrammarError(LrParserException):
    pass

class LoweringError(LrParserException):
    pass

class InputError(LrParserException):
    def __init__(self, bad_key, good_keys):
        msg = 'got %s; expected one of %s' % (bad_key, ', '.join(good_keys))
        super().__init__(msg)
