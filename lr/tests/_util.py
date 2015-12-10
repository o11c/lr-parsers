import pytest


def parm_tests(mod):
    pairs = [x for x in mod.__dict__.items() if not x[0].startswith('_')]
    pairs.sort()
    ids = [x for x, y in pairs]
    grammars = [y for x, y in pairs]
    return pytest.mark.parametrize('grammar_and_inputs', grammars, ids=ids)

