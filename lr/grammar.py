import typing

from typing import (
        Dict,
        Iterable,
        Iterator,
        List,
        Optional,
        Set,
        Tuple,
        Union,
)

import string
import weakref

from .error import (
        GrammarError,
        SymbolError,
)


_special_eof = '$eof'
_special_accept = '$accept'


class SymbolId:
    __slots__ = ('_number', '_info')

    def __init__(self, number: int, info: 'SymbolsInfo') -> None:
        self._number = number
        self._info = weakref.ref(info)

    def __repr__(self) -> str:
        return '<SymbolId for %r>' % (self._data(),)

    def _data(self) -> 'SymbolData':
        return self._info()._data[self._number]

    def _grammar_repr(self) -> str:
        data = self._data()
        name = data._get_name()
        return name

class SymbolData:
    __slots__ = ('_id', '_name', '_is_term')

    def __init__(self, id: SymbolId, name: str, is_term: bool) -> None:
        self._id = id
        self._name = name
        self._is_term = is_term

    def __repr__(self) -> str:
        x = 'terminal' if self._is_term else 'nonterminal'
        return '<SymbolData %s #%d %s>' % (x, self._id._number, self._name)

    def _get_name(self) -> str:
        # work around a mypy bug
        return self._name

def _fix_sym(sym: str, is_term: bool) -> str:
    if is_term and len(sym) > 2:
        for q in ['\'', '"']:
            if sym[0] == q and sym[-1] == q:
                sym = sym[1:-1]
                if q in sym or not all(c in string.punctuation for c in sym):
                    raise SymbolError('quote: %r' % sym)
                return sym
    if sym != sym.strip('-') or '--' in sym:
        raise SymbolError('dash: %r')
    for w in sym.split('-'):
        if not all(c in string.ascii_letters for c in w):
            raise SymbolError('alpha: %r' % sym)
    return sym

def _gen_symbol_iter(terminals: Iterable[str], nonterminals: Iterable[str]) -> Iterator[Tuple[str, bool]]:
    yield _special_eof, True
    for sym in terminals:
        sym = _fix_sym(sym, True)
        yield sym, True
    yield _special_accept, False
    for sym in nonterminals:
        sym = _fix_sym(sym, False)
        yield sym, False

class SymbolsInfo:
    __slots__ = ('_numbers', '_data', '_num_terminals', '__weakref__')

    def __init__(self, terminals: Iterable[str], nonterminals: Iterable[str]) -> None:
        self._numbers = {} # type: Dict[str, int]
        self._data = [] # type: List[SymbolData]
        num_terminals = 0

        for name, is_term in _gen_symbol_iter(terminals, nonterminals):
            i = len(self._data)
            if name in self._numbers:
                raise SymbolError('duplicate: %r' % name)
            self._numbers[name] = i
            self._data.append(SymbolData(SymbolId(i, self), name, is_term))
            if is_term:
                num_terminals += 1
        self._num_terminals = num_terminals

    def __repr__(self) -> str:
        num_symbols = len(self._data)
        num_terminals = self._num_terminals
        num_nonterminals = num_symbols - num_terminals
        return '<SymbolsInfo for %d terminals and %d nonterminals>' % (num_terminals, num_nonterminals)

    def _grammar_repr(self) -> str:
        num_symbols = len(self._data)
        num_terminals = self._num_terminals
        num_nonterminals = num_symbols - num_terminals
        return '%d nonterminals, %d terminals' % (num_nonterminals, num_terminals)

    def get(self, sym: str, maybe_term: bool) -> SymbolId:
        if not sym.startswith('$'):
            sym = _fix_sym(sym, maybe_term)
        try:
            num = self._numbers[sym]
        except KeyError:
            raise GrammarError('undefined: %r' % sym)
        else:
            return self._data[num]._id

    def all_terminals(self) -> List[SymbolId]:
        return [d._id for d in self._data[:self._num_terminals]]

class RuleId:
    __slots__ = ('_number', '_info')

    def __init__(self, number: int, info: 'Grammar') -> None:
        self._number = number
        self._info = weakref.ref(info)

    def __repr__(self) -> str:
        return '<RuleId for %r>' % (self._data(),)

    def _data(self) -> 'RuleData':
        return self._info()._data[self._number]

class RuleData:
    __slots__ = ('_id', '_lhs', '_alt_number', '_rhs')

    def __init__(self, id: RuleId, lhs: SymbolId, alt: int, rhs: List[SymbolId]) -> None:
        self._id = id
        self._lhs = lhs
        self._alt_number = alt
        self._rhs = rhs

    def __repr__(self) -> str:
        return '<RuleData #%d %s.%d: %s>' % (self._id._number, self._lhs._grammar_repr(), self._alt_number, ' '.join(r._grammar_repr() for r in self._rhs))

    def _grammar_repr(self) -> str:
        return '%s: %s' % (self._lhs._grammar_repr(), ' '.join(r._grammar_repr() for r in self._rhs))


def _gen_rule_iter(rules: Iterable[Tuple[str, List[str]]], start: Optional[str]) -> Iterator[Tuple[str, List[str]]]:
    rules = iter(rules)
    if start is None:
        first = next(rules)
        yield _special_accept, [first[0], _special_eof]
        yield first
    else:
        yield _special_accept, [start, _special_eof]
    yield from rules

class Grammar:
    __slots__ = ('_symbols', '_data', '_by_symbol', '__weakref__')

    def __init__(self, symbols: SymbolsInfo, data: Iterable[Tuple[str, List[str]]], start: Optional[str] = None) -> None:
        self._symbols = symbols
        self._data = [] # type: List[RuleData]
        self._by_symbol = {} # type: Dict[int, List[RuleData]]

        prev = None # type: int

        for (lhs, rhs) in _gen_rule_iter(data, start):
            i = len(self._data)
            lhs_sym = symbols.get(lhs, False)
            lhs_id = lhs_sym._number
            rhs_sym = [symbols.get(r, True) for r in rhs]
            if lhs_id != prev:
                for_this_sym = [] # type: List[RuleData]
                if lhs_id in self._by_symbol:
                    raise GrammarError('duplicate: %r' % lhs)
                self._by_symbol[lhs_id] = for_this_sym
            prev = lhs_id
            datum = RuleData(RuleId(i, self), lhs_sym, len(for_this_sym), rhs_sym)
            self._data.append(datum)
            for_this_sym.append(datum)

    def __repr__(self) -> str:
        rule_strs = [x._grammar_repr() for x in self._data]
        return '<Grammar with %d rules, %s\n  %s\n>' % (len(rule_strs), self._symbols._grammar_repr(), '\n  '.join(rule_strs))

    @staticmethod
    def _do_parse(lines: Iterable[str]) -> Iterator[Tuple[str, List[str]]]:
        for s in lines:
            s = s.strip()
            if not s:
                continue
            if s.startswith('#'):
                continue
            if not s.endswith(';'):
                raise GrammarError('terminator: %r' % s)
            if ':' not in s:
                raise GrammarError('separator: %r' % s)
            lhs, rhs = s.split(':', 1)
            lhs = lhs.rstrip()
            yield lhs, rhs[:-1].split()

    @staticmethod
    def parse(symbols: SymbolsInfo, lines: Union[str, Iterable[str]]) -> 'Grammar':
        if isinstance(lines, str):
            lines = lines.split('\n')
        return Grammar(symbols, Grammar._do_parse(lines))

    def all(self, name: SymbolId) -> Optional[List[RuleData]]:
        try:
            rv = self._by_symbol[name._number]
        except KeyError:
            return None
        else:
            return rv

    def all_terminals(self) -> List[SymbolId]:
        return self._symbols.all_terminals()
