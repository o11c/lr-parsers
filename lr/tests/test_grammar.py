import typing

import pytest

from lr.error import SymbolError, GrammarError
from lr.grammar import SymbolsInfo, Grammar

from . import grammar_examples


def test_symbol_contents() -> None:
    symbols = SymbolsInfo('''
        a
        b-c-d
    '''.split(), '''
        A
        B-C-D
    '''.split())
    symbols = SymbolsInfo('''
        '-'
        '--'
        '---'
    '''.split(), '''
    '''.split())
    symbols = SymbolsInfo('''
        "."
        ".."
    '''.split(), '''
    '''.split())
    with pytest.raises(SymbolError):
        symbols = SymbolsInfo('''
        '''.split(), '''
            "."
            ".."
        '''.split())
    with pytest.raises(SymbolError):
        symbols = SymbolsInfo('''
            'a'
        '''.split(), '''
        '''.split())
    with pytest.raises(SymbolError):
        symbols = SymbolsInfo('''
            'a.'
        '''.split(), '''
        '''.split())
    with pytest.raises(SymbolError):
        symbols = SymbolsInfo('''
            '\''
        '''.split(), '''
        '''.split())
    with pytest.raises(SymbolError):
        symbols = SymbolsInfo('''
            """
        '''.split(), '''
        '''.split())
    symbols = SymbolsInfo('''
        "'"
    '''.split(), '''
    '''.split())
    symbols = SymbolsInfo('''
        '"'
    '''.split(), '''
    '''.split())
    with pytest.raises(SymbolError):
        symbols = SymbolsInfo('''
            a-
        '''.split(), '''
        '''.split())
    with pytest.raises(SymbolError):
        symbols = SymbolsInfo('''
            -a
        '''.split(), '''
        '''.split())
    with pytest.raises(SymbolError):
        symbols = SymbolsInfo('''
        '''.split(), '''
            a-
        '''.split())
    with pytest.raises(SymbolError):
        symbols = SymbolsInfo('''
        '''.split(), '''
            -a
        '''.split())
    with pytest.raises(SymbolError):
        symbols = SymbolsInfo('''
            a--b
        '''.split(), '''
        '''.split())
    with pytest.raises(SymbolError):
        symbols = SymbolsInfo('''
        '''.split(), '''
            a--b
        '''.split())

def test_symbol_sets() -> None:
    with pytest.raises(SymbolError):
        symbols = SymbolsInfo('''
            a
            a
        '''.split(), '''
        '''.split())
    with pytest.raises(SymbolError):
        symbols = SymbolsInfo('''
        '''.split(), '''
            a
            a
        '''.split())

def test_grammar() -> None:
    symbols = SymbolsInfo('''
        a
        b
    '''.split(), '''
        A
        B
    '''.split())
    grammar = Grammar.parse(symbols, '''
        A: a;
        B: b;
    ''')
    grammar = Grammar.parse(symbols, '''
        A: a;
        B: b;
    ''', 'A')
    grammar = Grammar.parse(symbols, '''
        A: a;
        B: b;
    ''', 'B')
    with pytest.raises(GrammarError):
        grammar = Grammar.parse(symbols, '''
            X: a;
        ''')
    with pytest.raises(GrammarError):
        grammar = Grammar.parse(symbols, '''
            A: b;
            X: a;
        ''')
    with pytest.raises(GrammarError):
        grammar = Grammar.parse(symbols, '''
            A: x;
        ''')
    grammar = Grammar.parse(symbols, '''
        A: a;
        # B: b;
        A: b;
    ''')
    with pytest.raises(GrammarError):
        grammar = Grammar.parse(symbols, '''
            A: a;
            B: b;
            A: b;
        ''')
    with pytest.raises(GrammarError):
        grammar = Grammar.parse(symbols, '''
            A: a
        ''')
    with pytest.raises(GrammarError):
        grammar = Grammar.parse(symbols, '''
            A a;
        ''')

def test_repr_grammar() -> None:
    ex = grammar_examples.lr0.ex_minimal1
    grammar = ex.grammar
    symbols = grammar._symbols

    assert repr(symbols) == '<SymbolsInfo for 2 terminals and 2 nonterminals>'
    assert repr(symbols._data) == '[<SymbolData terminal #0 $eof>, <SymbolData terminal #1 term>, <SymbolData nonterminal #2 $accept>, <SymbolData nonterminal #3 Root>]'
    assert repr(symbols._data[0]._id) == '<SymbolId for <SymbolData terminal #0 $eof>>'
    assert repr(grammar) == '''
<Grammar with 2 rules, 2 nonterminals, 2 terminals
  $accept: Root $eof
  Root: term
>
    '''.strip()
    assert repr(grammar._data) == '[<RuleData #0 $accept.0: Root $eof>, <RuleData #1 Root.0: term>]'
    assert repr(grammar._data[0]._id) == '<RuleId for <RuleData #0 $accept.0: Root $eof>>'
