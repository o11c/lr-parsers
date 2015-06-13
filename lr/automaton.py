import typing

from typing import (
        Dict,
        Iterable,
        List,
        Tuple,
)

from abc import ABCMeta, abstractmethod
import weakref

from .grammar import RuleId, SymbolId


class BaseAction:
    __slots__ = ()

class Action(BaseAction):
    __slots__ = ()

class Shift(Action):
    __slots__ = ('_state',)

    def __init__(self, state: 'StateId') -> None:
        self._state = state

    def __repr__(self) -> str:
        return 'Shift(<state %d>)' % (self._state._get_number())

class Reduce(Action):
    __slots__ = ('_rule',)

    def __init__(self, rule: RuleId) -> None:
        self._rule = rule

    def __repr__(self) -> str:
        return 'Reduce(<rule %d>)' % (self._rule._number)

# The Python implementation uses dicts for actions.
# There is no `Error` because it is represented by the key not being found.
# There is no `Accept` because (like in C) it is implicit after $eof shifts.

class Goto(BaseAction):
    __slots__ = ('_state',)

    def __init__(self, state: 'StateId') -> None:
        self._state = state

    def __repr__(self) -> str:
        return 'Goto(<state %d>)' % (self._state._get_number())


class StateId:
    __slots__ = ('_number', '_info')

    def __init__(self, number: int, info: 'Automaton') -> None:
        self._number = number
        self._info = weakref.ref(info)

    # work around a mypy bug
    def _get_number(self) -> int:
        return self._number

    def __repr__(self) -> str:
        return '<StateId for %r>' % (self._data(),)

    def _data(self) -> 'StateData':
        return self._info()._data[self._number]

class StateData:
    __slots__ = ('_id', '_actions', '_gotos', '_creator')

    def __init__(self, id: StateId, creator: 'AbstractItemSet') -> None:
        self._id = id
        self._actions = {} # type: Dict[SymbolId, Action]
        self._gotos = {} # type: Dict[SymbolId, Goto]
        self._creator = creator

    def __repr__(self) -> str:
        return '<StateData #%d with %d actions, %d gotos; from\n  %r>' % (self._id._number, len(self._actions), len(self._gotos), self._creator)

class Automaton:
    __slots__ = ('_data', '__weakref__')

    def __init__(self) -> None:
        self._data = [] # type: List[StateData]

    def __repr__(self) -> str:
        return '<Automaton with %d states>' % (len(self._data))

    def add_state(self, creator: 'AbstractItemSet') -> StateData:
        i = len(self._data)
        rv = StateData(StateId(i, self), creator)
        self._data.append(rv)
        return rv

    def get_state0(self) -> StateId:
        return self._data[0]._id

class AbstractItemSet(metaclass=ABCMeta):
    __slots__ = ('_state',)

    def __init__(self, automaton: Automaton) -> None:
        self._state = automaton.add_state(self)

    @abstractmethod
    def is_initial_state(self) -> bool:
        pass
    @abstractmethod
    def is_penultimate_state(self) -> bool:
        pass
    @abstractmethod
    def is_final_state(self) -> bool:
        pass
