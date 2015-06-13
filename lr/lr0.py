import typing

from typing import (
        Dict,
        Iterator,
        List,
        NamedTuple,
        Optional,
        Sequence,
        Set,
        Tuple,
)

from ._mypy_bugs import as_tuple
from .error import LoweringError
from .grammar import Grammar, RuleId, SymbolId
from .automaton import Automaton, Shift, Reduce, Goto, AbstractItemSet


_arrow = '→'
_mdot = '\x1b[35m•\x1b[39m'


class ClosureTuple:
    __slots__ = ('nonterminal_list', 'terminal_list', 'all_set')

    def __init__(self, nonterminal_list: List[SymbolId], terminal_list: List[SymbolId], all_set: Set[SymbolId]) -> None:
        self.nonterminal_list = nonterminal_list
        self.terminal_list = terminal_list
        self.all_set = all_set

class Item:
    # no lookahead in LR(0)
    __slots__ = ('_rule', '_index')

    def __init__(self, rule: RuleId, index: int) -> None:
        self._rule = rule
        self._index = index

    def __repr__(self) -> str:
        return ' '.join(self._bits())

    def _bits(self) -> Iterator[str]:
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

    def _kernel(self) -> Tuple[RuleId, int]:
        return (self._rule, self._index)

class ItemSet(AbstractItemSet):
    __slots__ = ('_prev', '_items', '_kernel_size', '_origin_type', '_origin_args')

    def __init__(self, seeds: List[Item], automaton: Automaton, prev: Optional['ItemSet'], origin_type: str) -> None:
        super().__init__(automaton)
        self._prev = prev
        self._items = seeds
        self._kernel_size = len(seeds)
        self._origin_type = origin_type
        self._origin_args = [] # type: List[int]

    def __repr__(self) -> str:
        origin = self._origin_type
        if self._origin_args:
            origin = '%s from states %s' % (origin, ', '.join([str(x) for x in sorted(self._origin_args)]))
        bits = '\n  '.join(self._bits())
        return '<ItemSet #%s, kernel %d/%d, %s\n  %s\n>' % (self._state._id._number, self._kernel_size, len(self._items), origin, bits)

    def _bits(self) -> Iterator[str]:
        for i, it in enumerate(self._items):
            s = '+ ' if i >= self._kernel_size else '* '
            yield '%s%r' % (s, it)

    @staticmethod
    def _kernel(items: List[Item]) -> Sequence[Tuple[RuleId, int]]:
        return as_tuple([it._kernel() for it in items])

    def seed(self, item: Item) -> None:
        assert self._kernel_size is None
        self._items.append(item)

    def close(self, grammar: Grammar) -> ClosureTuple:
        rv_nonterminals = [] # type: List[SymbolId]
        rv_terminals = [] # type: List[SymbolId]
        rv_set = set() # type: Set[SymbolId]

        self._kernel_size = len(self._items)
        added_rules = set() # type: Set[RuleId]

        for it in self._items:
            rule_data = it._rule._data()
            if len(rule_data._rhs) == it._index:
                continue
            rv = rule_data._rhs[it._index]
            if rv in rv_set:
                continue
            rv_set.add(rv)
            rvl = grammar.all(rv)
            if rvl is not None:
                rv_nonterminals.append(rv)
                for rvld in rvl:
                    rvli = rvld._id
                    if rvli in added_rules:
                        continue
                    added_rules.add(rvli)
                    self._items.append(Item(rvli, 0))
            else:
                assert rv._data()._is_term
                rv_terminals.append(rv)
        return ClosureTuple(rv_nonterminals, rv_terminals, rv_set)

    def is_initial_state(self) -> bool:
        return self._is_core_state() and self._items[0]._index == 0
    def is_penultimate_state(self) -> bool:
        return self._is_core_state() and self._items[0]._index == 1
    def is_final_state(self) -> bool:
        return self._is_core_state() and self._items[0]._index == 2
    def _is_core_state(self) -> bool:
        if len(self._items) != 1:
            return False
        rule = self._items[0]._rule._data()
        if len(rule._rhs) != 2:
            return False
        if rule._rhs[-1]._number != 0:
            return False
        return True

def _add_item_set(automaton: Automaton, prev: Optional[ItemSet], sym: Optional[SymbolId], lst: List[ItemSet], grammar: Grammar, kernels: Dict[Sequence[Tuple[RuleId, int]], ItemSet], origin_type: str) -> ItemSet:
    if prev is None:
        seeds = [Item(grammar._data[0]._id, 0)]
    else:
        seeds = [
                Item(it._rule, it._index + 1)
                for it in prev._items
                if len(it._rule._data()._rhs) != it._index and it._rule._data()._rhs[it._index] == sym
        ]
    if prev is None:
        assert origin_type == 'root'
        origin_arg = None # type: int
    else:
        assert origin_type in {'shift', 'goto'}
        origin_type = '%s[%s]' % (origin_type, sym._data()._name)
        origin_arg = prev._state._id._number

    kernel = ItemSet._kernel(seeds)
    try:
        item_set = kernels[kernel]
        assert item_set._origin_type == origin_type, '%s == %s' % (item_set._origin_type, origin_type)
        assert origin_arg is not None
        item_set._origin_args.append(origin_arg)
        return item_set
    except KeyError:
        kernels[kernel] = item_set = ItemSet(seeds, automaton, prev, origin_type)
        if origin_arg is not None:
            item_set._origin_args.append(origin_arg)

    # If there is exactly one rule and it is at the end, reduce all.
    # If there is more than one rule and one is at the end, s/r conflict.
    # If there is more than one rule at the end, r/r conflict.
    conflict = None # type: str
    for it in item_set._items:
        if it._index == len(it._rule._data()._rhs):
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
            # FIXME This code is wrong, but I'm not sure how.
            conflict = 'shift'

    clt = item_set.close(grammar) # type: ClosureTuple
    lst.append(item_set)

    for sym2 in clt.nonterminal_list:
        is2 = _add_item_set(automaton, item_set, sym2, lst, grammar, kernels, 'goto') # type: ItemSet
        assert sym2 not in item_set._state._gotos
        item_set._state._gotos[sym2] = Goto(is2._state._id)
    for sym2 in clt.terminal_list:
        if False and sym2._number == 0:
            # My old code this but I think it's better not to?
            # TODO check what happens in Runtime when you can't shift eof
            # should be an error instead.
            item_set._state._actions[sym2] = None
            continue
        is2 = _add_item_set(automaton, item_set, sym2, lst, grammar, kernels, 'shift')
        # This replaces the reduce if present, but from the recursively
        # called function on the line before.
        item_set._state._actions[sym2] = Shift(is2._state._id)
    return item_set

def _init_item_set(grammar: Grammar, automaton: Automaton) -> List[ItemSet]:
    prev = None # type: ItemSet
    sym = None # type: SymbolId
    lst = [] # type: List[ItemSet]
    first = _add_item_set(automaton, prev, sym, lst, grammar, {}, 'root')
    assert first is lst[0]
    return lst

def compute_automaton(grammar: Grammar) -> Automaton:
    automaton = Automaton()
    item_sets = _init_item_set(grammar, automaton)
    return automaton
