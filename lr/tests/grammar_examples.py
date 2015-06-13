import typing

from typing import (
        List,
)

from lr.grammar import (
        Grammar,
        SymbolsInfo,
)

from lr.value import Terminal


def input_split(grammar: Grammar, source: str, split_char: str) -> List[Terminal]:
    rv = [] # type: List[Terminal]
    for word in source.split():
        if split_char in word:
            sym, txt = word.split(split_char)
        else:
            txt = word
            sym = repr(txt)
        rv.append(Terminal(grammar._symbols.get(sym, True), txt))
    rv.append(Terminal(grammar._symbols.get('$eof', True), ''))
    return rv


lr0_grammar = Grammar.parse(
        SymbolsInfo('''
            '+'
            '*'
            int
            id
        '''.split(), '''
            Sums
            Products
            Value
        '''.split()),
'''
Sums: Sums '+' Products;
Sums: Products;
Products: Products '*' Value;
Products: Value;
Value: int;
Value: id;
''')

lr0_input = input_split(lr0_grammar, 'int:0 + int:1 * id:a', ':')
