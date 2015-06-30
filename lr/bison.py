import typing

from typing import (
        Dict,
        Iterator,
        List,
)

import subprocess

import lxml.etree as etree

from .error import LoweringError
from .grammar import Grammar, RuleId, SymbolId
from .automaton import Automaton, Shift, Reduce, Goto, AbstractItemSet, StateId
from . import _bison_xml


BISON = 'bison'

_arrow = '→'
_mdot = '\x1b[35m•\x1b[39m'
_parallel = '\x1b[32m∥\x1b[39m'

has_bison_caret = subprocess.call(['bison', '--feature=caret', '--version']) == 0


class Item:
    __slots__ = ('_rule', '_index', '_lookahead')

    def __init__(self, rule: RuleId, index: int, lookahead: List[SymbolId]) -> None:
        self._rule = rule
        self._index = index
        self._lookahead = lookahead

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
        yield _parallel
        if self._lookahead:
            yield '{'
            for s in self._lookahead[:-1]:
                yield s._data()._name + ','
            s = self._lookahead[-1]
            yield s._data()._name
            yield '}'
        yield '>'

class ItemSet(AbstractItemSet):
    __slots__ = ('_items',)

    def __init__(self, items: List[Item], automaton: Automaton) -> None:
        super().__init__(automaton)
        self._items = items

    def __repr__(self) -> str:
        bits = '\n    '.join(self._bits())
        return '<bison.ItemSet #%d, size %d\n    %s\n>' % (self._state._id._number, len(self._items), bits)

    def _bits(self) -> Iterator[str]:
        for it in self._items:
            yield repr(it)

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


def run_bison(grammar: Grammar, lr_type: str) -> etree._ElementTree:
    args = [BISON, '/dev/stdin', '-o', '/dev/null', '--xml=/dev/stdout']
    if has_bison_caret:
        # Without this, bison will attempt to read the input file twice
        # if there is any warning/error, which obviously fails with a pipe.
        # Bug report here: https://lists.gnu.org/archive/html/bug-bison/2015-06/msg00001.html
        args.append('--feature=none')
    args.extend(['-Wall', '-Werror', '-Wno-deprecated'])
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    def p(*s: str) -> None:
        proc.stdin.writelines([x.encode('utf-8') for x in s] + [b'\n'])
    for sym in grammar._symbols._data[1:grammar._symbols._num_terminals]:
        assert sym._is_term
        sym_bison = sym._bison()
        if '\'' in sym_bison or '"' in sym_bison:
            continue
        p('%token ', sym_bison)
    p('%start ', grammar._data[0]._rhs[0]._data()._bison())
    p('%define lr.type ', lr_type)
    p('%define lr.default-reductions accepting')
    p('%%')
    for rule in grammar._data[1:]:
        p(rule._bison())
    p('%%')
    proc.stdin.close()
    parser = etree.XMLParser(schema=etree.XMLSchema(file='bison.xsd'))
    try:
        rv = etree.parse(proc.stdout, parser=parser)
    except etree.XMLSyntaxError as e:                                  # pragma: no cover
        raise LoweringError('bison failed to output valid xml') from e # pragma: no cover
    if proc.wait():
        raise LoweringError('bison failed maybe?') # pragma: no cover
    return rv

def parse_bison(xml: etree._ElementTree) -> _bison_xml.BisonXmlReport:
    return _bison_xml.root(xml, _bison_xml.BisonXmlReport)

def make_symbol_map(grammar: Grammar, bison_xml_report: _bison_xml.BisonXmlReport) -> Dict[str, SymbolId]:
    symbol_map = {} # type: Dict[str, SymbolId]
    for t in bison_xml_report.grammar.terminals:
        name = t.name
        if name == '$end':
            name = '$eof'
        if name == 'error':
            continue
        symbol_map[t.name] = grammar._symbols.get(name, True)
    for nt in bison_xml_report.grammar.nonterminals:
        name = nt.name
        symbol_map[nt.name] = grammar._symbols.get(name, False)
    for rule in bison_xml_report.grammar.rules:
        assert rule is bison_xml_report.grammar.rules[rule.number]
        g_rule = grammar._data[rule.number]
        assert g_rule._lhs is symbol_map[rule.lhs]
        assert len(g_rule._rhs) == len(rule.rhs)
        for g_r, b_r in zip(g_rule._rhs, rule.rhs):
            assert g_r is symbol_map[b_r]
    return symbol_map

def compute_automaton(grammar: Grammar, lr_type: str) -> Automaton:
    xml = run_bison(grammar, lr_type)
    bison_xml_report = parse_bison(xml)
    symbol_map = make_symbol_map(grammar, bison_xml_report)
    automaton = Automaton(grammar)
    state_map = [] # type: List[ItemSet]
    for state in bison_xml_report.automaton:
        items = [] # type: List[Item]
        for it in state.itemset:
            rule_id = grammar._data[it.rule]._id
            lookaheads = [symbol_map[x] for x in it.lookaheads]
            items.append(Item(rule_id, it.point, lookaheads))
        assert len(state_map) == state.number
        state_map.append(ItemSet(items, automaton))

    for state in bison_xml_report.automaton:
        # key: SymbolId
        # value: BaseAction
        actions = state_map[state.number]._state._actions
        gotos = state_map[state.number]._state._gotos

        for transition in state.actions.transitions:
            state_id = state_map[transition.state]._state._id
            key = symbol_map[transition.symbol]
            if transition.type == 'goto':
                gotos[key] = Goto(state_id)
            else:
                actions[key] = Shift(state_id)
        for reduction in state.actions.reductions:
            if not reduction.enabled:
                continue # pragma: no cover
            rule_id = grammar._data[reduction.rule]._id
            if reduction.symbol == '$default':
                for key in grammar.all_terminals():
                    if key not in actions:
                        actions[key] = Reduce(rule_id)
                continue
            key = symbol_map[reduction.symbol]
            actions[key] = Reduce(rule_id)

    return automaton

def compute_automaton_lalr(grammar: Grammar) -> Automaton:
    return compute_automaton(grammar, 'lalr')

def compute_automaton_ielr1(grammar: Grammar) -> Automaton:
    return compute_automaton(grammar, 'ielr')

def compute_automaton_clr1(grammar: Grammar) -> Automaton:
    return compute_automaton(grammar, 'canonical-lr')
