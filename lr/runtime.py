from .automaton import Automaton, Shift, Reduce
from .value import Value, Terminal, Nonterminal
from .error import InputError


class Runtime:
    __slots__ = ('_automaton', '_state_stack', '_value_stack')

    def __init__(self, automaton):
        self._automaton = automaton
        self._state_stack = [automaton.get_state0()]
        self._value_stack = []

    def __repr__(self):
        return '<Runtime in state #%d/%d with %d values>' % (self._state_stack[-1]._number, len(self._automaton._data), len(self._value_stack))

    def feed_all(self, toks):
        for tok in toks:
            self.feed(tok)

    def feed(self, tok):
        while True:
            assert len(self._state_stack) == 1 + len(self._value_stack)
            current_state = self._state_stack[-1]._data()
            try:
                action = current_state._actions[tok._sym]
            except KeyError:
                raise InputError(tok._sym._data()._name, [a._data()._name for a in current_state._actions]) from None
            if isinstance(action, Shift):
                self._value_stack.append(tok)
                self._state_stack.append(action._state)
                return
            if isinstance(action, Reduce):
                rule = action._rule
                rule_len = len(rule._data()._rhs)
                assert len(self._value_stack) >= rule_len > 0
                new_value = Nonterminal(rule, self._value_stack[-rule_len:])
                del self._state_stack[-rule_len:]
                del self._value_stack[-rule_len:]
                trampoline_state = self._state_stack[-1]
                try:
                    new_state = trampoline_state._data()._gotos[rule._data()._lhs]._state
                except KeyError: # pragma: no cover
                    assert False, 'should not be reachable I think' # pragma: no cover
                self._state_stack.append(new_state)
                self._value_stack.append(new_value)
                continue
            assert False, 'unknown subclass' # pragma: no cover

    def get(self):
        assert len(self._state_stack) == 3
        assert self._state_stack[-1]._data()._creator.is_final_state()
        assert len(self._value_stack) == 2
        return self._value_stack[0]
