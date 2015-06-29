import typing

from .grammar import Grammar
from .automaton import Automaton


_arrow = '→'
_mdot = '\x1b[35m•\x1b[39m'
_parallel = '\x1b[32m∥\x1b[39m'


# Canonical LR without merging is a bad idea. There are only two merging
# strategies that are not buggy:
#   1.  The original "Pager's Algorithm". The paper that defines it is not
#       available for free, but there are many open-source implementations.
#       This algorthm is *not* suitable for conflict resolution (i.e.
#       precedence and associativity).
#   2.  The IELR(1) Algorithm. The paper *is* available for free, in two
#       versions, a 2008 one and a 2010 one. There are few implementations.
#       Conflict resolution was the motivating factor.

def compute_automaton(grammar: Grammar) -> Automaton:
    raise NotImplementedError
