import typing

from .error import LrParserException
from .grammar import Grammar
from .automaton import Automaton

from . import lr0, slr, lalr, lr1


# fallback order: lr0, slr, lalr, lr1

# http://cs.stackexchange.com/questions/43/language-theoretic-comparison-of-ll-and-lr-grammars

# Fallback would be much more complicated if I did LL parsers too.

def compute_automaton(grammar: Grammar) -> Automaton:
    funcs = [
            lr0.compute_automaton,
            slr.compute_automaton,
            lalr.compute_automaton,
            lr1.compute_automaton,
    ]

    for fun in funcs:
        try:
            return fun(grammar)
        except LrParserException as e:
            last_e = e
        except NotImplementedError:
            pass
    raise last_e
