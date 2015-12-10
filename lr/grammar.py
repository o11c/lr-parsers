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

    def __init__(self, number, info):
        self._number = number
        self._info = weakref.ref(info)

    def __repr__(self):
        return '<SymbolId for %r>' % (self._data(),)

    def _data(self):
        return self._info()._data[self._number]

    def _grammar_repr(self):
        data = self._data()
        name = data._name
        return name

class SymbolData:
    __slots__ = ('_id', '_name', '_is_term')

    def __init__(self, id, name, is_term):
        self._id = id
        self._name = name
        self._is_term = is_term

    def __repr__(self):
        x = 'terminal' if self._is_term else 'nonterminal'
        return '<SymbolData %s #%d %s>' % (x, self._id._number, self._name)

    def _bison(self):
        if all(c in string.ascii_letters for c in self._name):
            return self._name
        elif len(self._name) == 1 and self._name != "'":
            return "'%s'" % self._name
        else:
            assert '"' not in self._name
            return '"%s"' % self._name

def _fix_sym(sym, is_term):
    if sym == 'error':
        raise SymbolError('other: %r' % sym) # pragma: no cover
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

def _gen_symbol_iter(terminals, nonterminals):
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

    def __init__(self, terminals, nonterminals):
        self._numbers = {}
        self._data = []
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

    def __repr__(self):
        num_symbols = len(self._data)
        num_terminals = self._num_terminals
        num_nonterminals = num_symbols - num_terminals
        return '<SymbolsInfo for %d terminals and %d nonterminals>' % (num_terminals, num_nonterminals)

    def _grammar_repr(self):
        num_symbols = len(self._data)
        num_terminals = self._num_terminals
        num_nonterminals = num_symbols - num_terminals
        return '%d nonterminals, %d terminals' % (num_nonterminals, num_terminals)

    def get(self, sym, maybe_term):
        if not sym.startswith('$'):
            sym = _fix_sym(sym, maybe_term)
        try:
            num = self._numbers[sym]
        except KeyError:
            raise GrammarError('undefined: %r' % sym)
        else:
            return self._data[num]._id

    def all_terminals(self):
        return [d._id for d in self._data[:self._num_terminals]]

    def all_nonterminals(self):
        return [d._id for d in self._data[self._num_terminals:]]

class RuleId:
    __slots__ = ('_number', '_info')

    def __init__(self, number, info):
        self._number = number
        self._info = weakref.ref(info)

    def __repr__(self):
        return '<RuleId for %r>' % (self._data(),)

    def _data(self):
        return self._info()._data[self._number]

class RuleData:
    __slots__ = ('_id', '_lhs', '_alt_number', '_rhs')

    def __init__(self, id, lhs, alt, rhs):
        self._id = id
        self._lhs = lhs
        self._alt_number = alt
        self._rhs = rhs

    def __repr__(self):
        return '<RuleData #%d %s.%d: %s>' % (self._id._number, self._lhs._grammar_repr(), self._alt_number, ' '.join(r._grammar_repr() for r in self._rhs))

    def _grammar_repr(self):
        return '%s: %s' % (self._lhs._grammar_repr(), ' '.join(r._grammar_repr() for r in self._rhs))

    def _bison(self):
        return '%s: %s;' % (self._lhs._data()._bison(), ' '.join(r._data()._bison() for r in self._rhs))


def _gen_rule_iter(rules, start):
    rules = iter(rules)
    if start is None:
        first = next(rules)
        yield _special_accept, [first[0], _special_eof]
        yield first
    else:
        yield _special_accept, [start, _special_eof]
    yield from rules

class Grammar:
    __slots__ = ('_symbols', '_data', '_by_symbol_lhs', '_by_symbol_rhs', '__weakref__')

    def __init__(self, symbols, data, start):
        self._symbols = symbols
        self._data = []
        self._by_symbol_lhs = {}
        self._by_symbol_rhs = {}

        prev = None

        for (lhs, rhs) in _gen_rule_iter(data, start):
            i = len(self._data)
            lhs_sym = symbols.get(lhs, False)
            rhs_syms = [symbols.get(r, True) for r in rhs]
            if lhs_sym != prev:
                for_this_sym = []
                if lhs_sym in self._by_symbol_lhs:
                    raise GrammarError('nonadjacent: %r' % lhs)
                self._by_symbol_lhs[lhs_sym] = for_this_sym
            prev = lhs_sym
            datum = RuleData(RuleId(i, self), lhs_sym, len(for_this_sym), rhs_syms)
            self._data.append(datum)
            for_this_sym.append(datum._id)
            for i, rhs_sym in enumerate(rhs_syms):
                bsr = self._by_symbol_rhs.setdefault(rhs_sym, [])
                bsr.append((datum._id, i))

    def __repr__(self):
        rule_strs = [x._grammar_repr() for x in self._data]
        return '<Grammar with %d rules, %s\n  %s\n>' % (len(rule_strs), self._symbols._grammar_repr(), '\n  '.join(rule_strs))

    @staticmethod
    def _do_parse(lines):
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
    def parse(symbols, lines, start=None):
        if isinstance(lines, str):
            lines = lines.split('\n')
        return Grammar(symbols, Grammar._do_parse(lines), start)

    def all(self, name):
        try:
            rv = self._by_symbol_lhs[name]
        except KeyError:
            assert name._data()._is_term
            return None
        else:
            assert not name._data()._is_term
            return rv

    def uses(self, name):
        return self._by_symbol_rhs.get(name, [])

    def all_terminals(self):
        return self._symbols.all_terminals()

    def all_nonterminals(self):
        return self._symbols.all_nonterminals()
