from abc import ABCMeta, abstractmethod
import weakref

from .error import LoweringError
from .grammar import Grammar, RuleId, SymbolId


class BaseAction:
    __slots__ = ()

class Action(BaseAction):
    __slots__ = ()

class Shift(Action):
    __slots__ = ('_state',)

    def __init__(self, state):
        self._state = state

    def __repr__(self):
        return 'Shift(<state %d>)' % (self._state._number)

class Reduce(Action):
    __slots__ = ('_rule',)

    def __init__(self, rule):
        self._rule = rule

    def __repr__(self):
        return 'Reduce(<rule %d>)' % (self._rule._number)

# The Python implementation uses dicts for actions.
# There is no `Error` because it is represented by the key not being found.
# There is no `Accept` because (like in C) it is implicit after $eof shifts.

class Goto(BaseAction):
    __slots__ = ('_state',)

    def __init__(self, state):
        self._state = state

    def __repr__(self):
        return 'Goto(<state %d>)' % (self._state._number)


class StateId:
    __slots__ = ('_number', '_info')

    def __init__(self, number, info):
        self._number = number
        self._info = weakref.ref(info)

    def __repr__(self):
        return '<StateId for %r>' % (self._data(),)

    def _data(self):
        return self._info()._data[self._number]

class StateData:
    __slots__ = ('_id', '_actions', '_gotos', '_creator')

    def __init__(self, id, creator):
        self._id = id
        self._actions = {}
        self._gotos = {}
        self._creator = creator

    def __repr__(self):
        return '<StateData #%d with %d actions, %d gotos\n  %r>' % (self._id._number, len(self._actions), len(self._gotos), self._creator)

class Automaton:
    __slots__ = ('_data', '_grammar', '__weakref__')

    def __init__(self, grammar):
        self._data = []
        self._grammar = grammar

    def __repr__(self):
        return '<Automaton with %d states>' % (len(self._data))

    def add_state(self, creator):
        i = len(self._data)
        rv = StateData(StateId(i, self), creator)
        self._data.append(rv)
        return rv

    def get_state0(self):
        return self._data[0]._id

class AbstractItemSet(metaclass=ABCMeta):
    __slots__ = ('_state',)

    def __init__(self, automaton):
        self._state = automaton.add_state(self)

    @abstractmethod
    def is_initial_state(self):
        pass # pragma: no cover
    @abstractmethod
    def is_penultimate_state(self):
        pass # pragma: no cover
    @abstractmethod
    def is_final_state(self):
        pass # pragma: no cover

def raise_conflicts(conflicts):
    if not conflicts:
        return
    conflict_lines = ['conflicts in %d states:' % len(conflicts)]
    for its, symco in sorted(conflicts.items(), key=lambda pair: pair[0]._state._id._number):
        conflict_lines.append('%d conflicts in %s' % (len(symco), its))
        for sym, acts in sorted(symco.items(), key=lambda pair: pair[0]._number):
            sym_name = sym._data()._name
            sym_acts = ', '.join(str(a) for a in acts)
            conflict_lines.append('  %s: {%s}' % (sym_name, sym_acts))
    conflict_lines.append('\n')
    raise LoweringError('\n'.join(conflict_lines))
