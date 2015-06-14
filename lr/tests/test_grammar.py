import typing

import pytest

from lr.error import SymbolError, GrammarError
from lr.grammar import SymbolsInfo, Grammar


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
