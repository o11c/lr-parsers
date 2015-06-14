import typing

from typing import (
        List,
        Set,
)

from lr.grammar import (
        Grammar,
        SymbolsInfo,
)

from lr.value import Terminal


def grammar_parse(source: str) -> Grammar:
    nonterminal_list = [] # type: List[str]
    nonterminal_set = set() # type: Set[str]
    # not actually all
    all_list = [] # type: List[str]
    all_set = set() # type: Set[str]

    for line in source.split('\n'):
        line = line.strip()
        if not line:
            continue
        lhs, rhs = line.split(':', 1)
        rhses = rhs.strip(' ;').split()

        if lhs not in nonterminal_set:
            nonterminal_set.add(lhs)
            nonterminal_list.append(lhs)
        for rhs in rhses:
            if rhs not in all_set:
                all_set.add(rhs)
                all_list.append(rhs)

    terminal_set = all_set - nonterminal_set
    terminal_list = [x for x in all_list if x in terminal_set]

    symbols = SymbolsInfo(terminal_list, nonterminal_list)
    grammar = Grammar.parse(symbols, source)
    return grammar

def input_split(grammar: Grammar, source: str, split_char: str) -> List[Terminal]:
    rv = [] # type: List[Terminal]
    for word in source.split():
        if split_char in word:
            sym, txt = word.split(split_char)
        else:
            if word.isalnum():
                txt = word
                sym = txt
            else:
                txt = word
                sym = repr(txt)
        rv.append(Terminal(grammar._symbols.get(sym, True), txt))
    rv.append(Terminal(grammar._symbols.get('$eof', True), ''))
    return rv


minimal1_grammar = grammar_parse('''
Root: term;
''')
minimal1_input0 = input_split(minimal1_grammar, '', ':')
minimal1_input1 = input_split(minimal1_grammar, 'term', ':')
minimal1_input2 = input_split(minimal1_grammar, 'term term', ':')

minimal2_grammar = grammar_parse('''
Root: term term;
''')
minimal2_input0 = input_split(minimal2_grammar, '', ':')
minimal2_input1 = input_split(minimal2_grammar, 'term', ':')
minimal2_input2 = input_split(minimal2_grammar, 'term term', ':')
minimal2_input3 = input_split(minimal2_grammar, 'term term term', ':')

evil_grammar = grammar_parse('''
Root: A;
Root: B;
A: term;
B: term;
''')


lr0_grammar = grammar_parse('''
Sums: Sums '+' Products;
Sums: Products;
Products: Products '*' Value;
Products: Value;
Value: '+' Value;
Value: int;
Value: id;
''')
lr0_input = input_split(lr0_grammar, 'int:0 + + int:1 * id:a', ':')
