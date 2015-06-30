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
from .grammar import Grammar, RuleId, SymbolId
from .automaton import Automaton, Action, Shift, Reduce, Goto, AbstractItemSet, StateId, raise_conflicts
from .conflict import ConflictMap


_arrow = '→'
_mdot = '\x1b[35m•\x1b[39m'


class Item:
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

    def _next_sym(self) -> Optional[SymbolId]:
        rule = self._rule._data()
        index = self._index
        if len(rule._rhs) == index:
            return None
        return rule._rhs[index]

class ItemSet(AbstractItemSet):
    __slots__ = ('_items', '_kernel_size', '_prev_states')

    def __init__(self, seeds: List[Item], automaton: Automaton) -> None:
        super().__init__(automaton)
        self._items = seeds
        self._kernel_size = len(seeds)
        self._prev_states = [] # type: List[StateId]
        self.close(automaton._grammar)

    def __repr__(self) -> str:
        origin = self._origin_str()
        bits = '\n  '.join(self._bits())
        return '<slr.ItemSet #%d, kernel %d/%d, %s\n  %s\n>' % (self._state._id._number, self._kernel_size, len(self._items), origin, bits)

    def _origin_str(self) -> str:
        prev_states = sorted(self._prev_states, key=lambda x: x._number)
        prev_str = ', '.join([str(i._number) for i in prev_states])
        return '← (%s)' % (prev_str)

    def _bits(self) -> Iterator[str]:
        for i, it in enumerate(self._items):
            s = '+ ' if i >= self._kernel_size else '* '
            yield '%s%r' % (s, it)

    def close(self, grammar: Grammar) -> None:
        rv_set = set() # type: Set[SymbolId]

        for it in self._items:
            rv = it._next_sym()
            if rv is None:
                continue
            if rv in rv_set:
                continue

            rv_set.add(rv)
            rvl = grammar.all(rv)
            if rvl is not None:
                for rvli in rvl:
                    self._items.append(Item(rvli, 0))
            else:
                assert rv._data()._is_term

    def is_initial_state(self) -> bool:
        return self._is_core_state(False) and self._items[0]._index == 0 # pragma: no cover
    def is_penultimate_state(self) -> bool:
        return self._is_core_state(False) and self._items[0]._index == 1 # pragma: no cover
    def is_final_state(self) -> bool:
        return self._is_core_state(True) and self._items[0]._index == 2
    def _is_core_state(self, final: bool) -> bool:
        if final and len(self._items) != 1:
            return False # pragma: no cover
        rule = self._items[0]._rule._data()
        if len(rule._rhs) != 2:
            return False # pragma: no cover
        if rule._rhs[-1]._number != 0:
            return False # pragma: no cover
        return True

def _calc_first(grammar: Grammar, sym: SymbolId) -> List[SymbolId]:
    assert not sym._data()._is_term
    sym_set = {sym}
    first_terminals = [] # type: List[SymbolId]
    first_nonterminals = [sym]

    for sym in first_nonterminals:
        rules = grammar.all(sym)
        assert rules is not None
        for rule in rules:
            sym = rule._data()._rhs[0]
            if sym in sym_set:
                continue
            sym_set.add(sym)
            if sym._data()._is_term:
                first_terminals.append(sym)
            else:
                first_nonterminals.append(sym)
    return first_terminals

def _calc_follow(grammar: Grammar, sym: SymbolId, first: Dict[SymbolId, List[SymbolId]]) -> List[SymbolId]:
    assert not sym._data()._is_term

    follow_terminals = [] # type: List[SymbolId]
    follow_set = set() # type: Set[SymbolId]
    prev_nonterminals = [sym]
    prev_set = {sym}

    for sym in prev_nonterminals:
        for rule_id, i in grammar.uses(sym):
            i += 1
            rule = rule_id._data()
            if i == len(rule._rhs):
                if rule._lhs in prev_set:
                    continue
                prev_set.add(rule._lhs)
                prev_nonterminals.append(rule._lhs)
            else:
                sym2 = rule._rhs[i]
                if sym2._data()._is_term:
                    assert sym2 not in first
                    if sym2 in follow_set:
                        continue
                    follow_set.add(sym2)
                    follow_terminals.append(sym2)
                else:
                    assert sym2 in first
                    for sym3 in first[sym2]:
                        if sym3 in follow_set:
                            continue
                        follow_set.add(sym3)
                        follow_terminals.append(sym3)
    return follow_terminals

def _get_successor_state(istate: ItemSet, sym: SymbolId, automaton: Automaton, kernels: Dict[Sequence[Tuple[RuleId, int]], ItemSet], follow: Dict[SymbolId, List[SymbolId]], conflicts: Dict[AbstractItemSet, Dict[SymbolId, List[Action]]]) -> ItemSet:
    grammar = automaton._grammar
    seeds = [
            Item(it._rule, it._index + 1)
            for it in istate._items
            if it._next_sym() == sym
    ]
    kernel = as_tuple([it._kernel() for it in seeds])
    if kernel in kernels:
        item_set = kernels[kernel]
        item_set._prev_states.append(istate._state._id)
        return item_set
    kernels[kernel] = item_set = ItemSet(seeds, automaton)
    item_set._prev_states.append(istate._state._id)
    _do_state(item_set, automaton, kernels, follow, conflicts)
    return item_set

def _do_state(istate: ItemSet, automaton: Automaton, kernels: Dict[Sequence[Tuple[RuleId, int]], ItemSet], follow: Dict[SymbolId, List[SymbolId]], conflicts: Dict[AbstractItemSet, Dict[SymbolId, List[Action]]]) -> None:
    grammar = automaton._grammar
    shift_syms = [] # type: List[SymbolId]
    goto_syms = [] # type: List[SymbolId]
    shift_items = {} # type: Dict[SymbolId, List[Item]]
    goto_items = {} # type: Dict[SymbolId, List[Item]]
    actions = ConflictMap(grammar.all_terminals()) # type: ConflictMap[SymbolId, Action]

    for item in istate._items:
        sym = item._next_sym()
        if sym is None:
            for sym in follow[item._rule._data()._lhs]:
                actions.add(sym, Reduce(item._rule))
        else:
            if sym._data()._is_term:
                tmp_items = shift_items.setdefault(sym, [])
                if not tmp_items:
                    shift_syms.append(sym)
            else:
                tmp_items = goto_items.setdefault(sym, [])
                if not tmp_items:
                    goto_syms.append(sym)
            tmp_items.append(item)
    # The above loop guarantees that these lists have unique elements.
    for sym in shift_syms:
        succ_state = _get_successor_state(istate, sym, automaton, kernels, follow, conflicts)
        actions.add(sym, Shift(succ_state._state._id))
    for sym in goto_syms:
        succ_state = _get_successor_state(istate, sym, automaton, kernels, follow, conflicts)
        istate._state._gotos[sym] = Goto(succ_state._state._id)
    istate._state._actions, rv = actions.finish()
    if rv:
        conflicts[istate] = rv

def compute_automaton(grammar: Grammar) -> Automaton:
    # key: nonterminal, value: terminal
    first = {} # type: Dict[SymbolId, List[SymbolId]]
    # key: nonterminal, value: terminal
    follow = {} # type: Dict[SymbolId, List[SymbolId]]

    all_nonterminals = grammar.all_nonterminals()

    for sym in all_nonterminals:
        first[sym] = _calc_first(grammar, sym)

    for sym in all_nonterminals:
        follow[sym] = _calc_follow(grammar, sym, first)

    automaton = Automaton(grammar)

    root_item = Item(grammar._data[0]._id, 0)
    istate0 = ItemSet([root_item], automaton)

    # initial state doesn't need to be cached since it can't be a successor
    kernels = {} # type: Dict[Sequence[Tuple[RuleId, int]], ItemSet]

    conflicts = {} # type: Dict[AbstractItemSet, Dict[SymbolId, List[Action]]]
    _do_state(istate0, automaton, kernels, follow, conflicts)
    raise_conflicts(conflicts)
    return automaton
