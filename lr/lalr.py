from .grammar import Grammar
from .automaton import Automaton


_arrow = '→'
_mdot = '\x1b[35m•\x1b[39m'
_parallel = '\x1b[32m∥\x1b[39m'


def compute_automaton(grammar):
    raise NotImplementedError
