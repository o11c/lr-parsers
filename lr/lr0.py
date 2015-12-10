from .error import LoweringError
from .grammar import Grammar, RuleId, SymbolId
from .automaton import Automaton, Shift, Reduce, Goto, AbstractItemSet, StateId


_arrow = '→'
_mdot = '\x1b[35m•\x1b[39m'


# This file really ought to be rewritten with lessons learned in `slr.py`.


class ClosureTuple:
    __slots__ = ('nonterminal_list', 'terminal_list', 'all_set')

    def __init__(self, nonterminal_list, terminal_list, all_set):
        self.nonterminal_list = nonterminal_list
        self.terminal_list = terminal_list
        self.all_set = all_set

class Item:
    # no lookahead in LR(0)
    __slots__ = ('_rule', '_index')

    def __init__(self, rule, index):
        self._rule = rule
        self._index = index

    def __repr__(self):
        return ' '.join(self._bits())

    def _bits(self):
        rule = self._rule._data()
        yield '<'
        yield rule._lhs._data()._name
        yield _arrow
        for r in rule._rhs[:self._index]:
            yield r._data()._name
        yield _mdot
        for r in rule._rhs[self._index:]:
            yield r._data()._name
        yield '>'

    def _kernel(self):
        return (self._rule, self._index)

    def _next_sym(self):
        rule = self._rule._data()
        index = self._index
        if len(rule._rhs) == index:
            return None
        return rule._rhs[index]

class ItemSet(AbstractItemSet):
    __slots__ = ('_items', '_kernel_size', '_prev_states')

    def __init__(self, seeds, automaton):
        super().__init__(automaton)
        self._items = seeds
        self._kernel_size = len(seeds)
        self._prev_states = []

    def __repr__(self):
        origin = self._origin_str()
        bits = '\n  '.join(self._bits())
        return '<lr0.ItemSet #%d, kernel %d/%d, %s\n  %s\n>' % (self._state._id._number, self._kernel_size, len(self._items), origin, bits)

    def _origin_str(self):
        prev_states = sorted(self._prev_states, key=lambda x: x._number)
        prev_str = ', '.join([str(i._number) for i in prev_states])
        return '← (%s)' % (prev_str)

    def _bits(self):
        for i, it in enumerate(self._items):
            s = '+ ' if i >= self._kernel_size else '* '
            yield '%s%r' % (s, it)

    @staticmethod
    def _kernel(items):
        return tuple([it._kernel() for it in items])

    def close(self, grammar):
        rv_nonterminals = []
        rv_terminals = []
        rv_set = set()

        for it in self._items:
            rv = it._next_sym()
            if rv is None:
                continue
            if rv in rv_set:
                continue
            rv_set.add(rv)
            rvl = grammar.all(rv)
            if rvl is not None:
                rv_nonterminals.append(rv)
                for rvli in rvl:
                    self._items.append(Item(rvli, 0))
            else:
                assert rv._data()._is_term
                rv_terminals.append(rv)
        return ClosureTuple(rv_nonterminals, rv_terminals, rv_set)

    def is_initial_state(self):
        return self._is_core_state(False) and self._items[0]._index == 0 # pragma: no cover
    def is_penultimate_state(self):
        return self._is_core_state(False) and self._items[0]._index == 1 # pragma: no cover
    def is_final_state(self):
        return self._is_core_state(True) and self._items[0]._index == 2
    def _is_core_state(self, final):
        if final and len(self._items) != 1:
            return False # pragma: no cover
        rule = self._items[0]._rule._data()
        if len(rule._rhs) != 2:
            return False # pragma: no cover
        if rule._rhs[-1]._number != 0:
            return False # pragma: no cover
        return True

def _add_item_set(automaton, prev, sym, lst, kernels):
    grammar = automaton._grammar
    if prev is None:
        seeds = [Item(grammar._data[0]._id, 0)]
    else:
        seeds = [
                Item(it._rule, it._index + 1)
                for it in prev._items
                if it._next_sym() == sym
        ]

    kernel = ItemSet._kernel(seeds)
    try:
        item_set = kernels[kernel]
    except KeyError:
        kernels[kernel] = item_set = ItemSet(seeds, automaton)
        if prev is not None:
            item_set._prev_states.append(prev._state._id)
    else:
        item_set._prev_states.append(prev._state._id)
        return item_set

    # If there is exactly one rule and it is at the end, reduce all.
    # If there is more than one rule and one is at the end, s/r conflict.
    # If there is more than one rule at the end, r/r conflict.
    conflict = None
    for it in item_set._items:
        if it._next_sym() is None:
            if conflict is not None:
                raise LoweringError('%s/reduce conflict' % (conflict,))
            else:
                for sym2 in grammar.all_terminals():
                    assert sym2 not in item_set._state._actions
                    # This will be replaced below, but in the recursively
                    # calling function. For the non-recursive case, index
                    # is 0 so the below branch is taken instead.
                    item_set._state._actions[sym2] = Reduce(it._rule)
            conflict = 'reduce'
        else:
            if conflict == 'reduce':
                raise LoweringError('shift/reduce conflict')
            conflict = 'shift'
        # Obvious: there is no such thing as a shift/shift conflict.

    clt = item_set.close(grammar)
    lst.append(item_set)

    for sym2 in clt.nonterminal_list:
        is2 = _add_item_set(automaton, item_set, sym2, lst, kernels)
        assert sym2 not in item_set._state._gotos
        item_set._state._gotos[sym2] = Goto(is2._state._id)
    for sym2 in clt.terminal_list:
        is2 = _add_item_set(automaton, item_set, sym2, lst, kernels)
        # This replaces the reduce if present, but from the recursively
        # called function on the line before.
        item_set._state._actions[sym2] = Shift(is2._state._id)
    return item_set

def _init_item_set(automaton):
    prev = None
    sym = None
    lst = []
    first = _add_item_set(automaton, prev, sym, lst, {})
    assert first is lst[0]
    return lst

def compute_automaton(grammar):
    automaton = Automaton(grammar)
    item_sets = _init_item_set(automaton)
    return automaton
