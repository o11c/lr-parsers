from .grammar import Grammar, RuleId, SymbolId
from .automaton import Automaton, Shift, Reduce, Goto, AbstractItemSet, StateId, raise_conflicts
from .conflict import ConflictMap


_arrow = '→'
_mdot = '\x1b[35m•\x1b[39m'


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
        self.close(automaton._grammar)

    def __repr__(self):
        origin = self._origin_str()
        bits = '\n  '.join(self._bits())
        return '<lr0.ItemSet #%d, kernel %d/%d, %s\n  %s\n>' % (self._state._id._number, self._kernel_size, len(self._items), origin, bits)

    def _origin_str(self):
        prev_states = sorted(self._prev_states, key=lambda x: x._number)
        prev_str = ', '.join([str(i._number) for i in prev_states])
        extra = []
        if self.is_initial_state():
            extra.append('initial')
        if self.is_penultimate_state():
            extra.append('penultimate')
        if self.is_final_state():
            extra.append('final')
        assert len(extra) <= 1
        if extra:
            return '← (%s) [%s]' % (prev_str, extra[0])
        return '← (%s)' % (prev_str)

    def _bits(self):
        for i, it in enumerate(self._items):
            s = '+ ' if i >= self._kernel_size else '* '
            yield '%s%r' % (s, it)

    def close(self, grammar):
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
                for rvli in rvl:
                    self._items.append(Item(rvli, 0))
            else:
                assert rv._data()._is_term

    def is_initial_state(self):
        return self._is_core_state(False) and self._items[0]._index == 0
    def is_penultimate_state(self):
        return self._is_core_state(False) and self._items[0]._index == 1
    def is_final_state(self):
        return self._is_core_state(True) and self._items[0]._index == 2
    def _is_core_state(self, final):
        if final and len(self._items) != 1:
            return False
        rule = self._items[0]._rule._data()
        if rule._rhs[-1]._number != 0:
            return False
        return True

class Lr0Junk:
    __slots__ = ('automaton', 'kernels', 'conflicts')

    def __init__(self, grammar):
        self.automaton = Automaton(grammar)

        # initial state doesn't need to be cached since it can't be a successor
        self.kernels = {}

        self.conflicts = {}

def _get_successor_state(istate, sym, junk):
    automaton = junk.automaton
    kernels = junk.kernels
    conflicts = junk.conflicts
    grammar = automaton._grammar

    seeds = [
            Item(it._rule, it._index + 1)
            for it in istate._items
            if it._next_sym() == sym
    ]
    kernel = tuple([it._kernel() for it in seeds])
    item_set = kernels.get(kernel)
    if item_set:
        item_set._prev_states.append(istate._state._id)
        return item_set
    kernels[kernel] = item_set = ItemSet(seeds, automaton)
    item_set._prev_states.append(istate._state._id)
    _do_state(item_set, junk)
    return item_set

def _do_state(istate, junk):
    automaton = junk.automaton
    kernels = junk.kernels
    conflicts = junk.conflicts
    grammar = automaton._grammar

    shift_syms = []
    goto_syms = []
    shift_items = {}
    goto_items = {}
    actions = ConflictMap(grammar.all_terminals())

    for item in istate._items:
        sym = item._next_sym()
        if sym is None:
            # In LR(0), unlike SLR(1), the follow set is *all* terminals.
            # This is *not* the same as actions.add_default(sym, act)
            act = Reduce(item._rule)
            for sym in grammar.all_terminals():
                actions.add(sym, act)
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
        succ_state = _get_successor_state(istate, sym, junk)
        actions.add(sym, Shift(succ_state._state._id))
    for sym in goto_syms:
        succ_state = _get_successor_state(istate, sym, junk)
        assert sym not in istate._state._gotos
        istate._state._gotos[sym] = Goto(succ_state._state._id)
    istate._state._actions, rv = actions.finish()
    if rv:
        conflicts[istate] = rv

def compute_automaton(grammar):
    junk = Lr0Junk(grammar)

    root_item = Item(grammar._data[0]._id, 0)
    istate0 = ItemSet([root_item], junk.automaton)

    _do_state(istate0, junk)
    raise_conflicts(junk.conflicts)
    return junk.automaton
