import typing

from typing import (
        List,
        Optional,
        Set,
        Tuple,
)

from lr._mypy_bugs import module_decorator as module

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

def input_split(grammar: Grammar, source: str, split_char: Optional[str] = None) -> List[Terminal]:
    rv = [] # type: List[Terminal]
    for word in source.split():
        if split_char is not None and split_char in word:
            sym, txt = word.split(split_char)
        else:
            if word.isalnum():
                txt = word
                sym = txt
            else:
                txt = word
                sym = repr(txt)
        rv.append(Terminal(grammar._symbols.get(sym, True), txt))
    rv.append(Terminal(grammar._symbols.get('$eof', True), ""))
    return rv

class GrammarAndInputs:
    __slots__ = ('grammar', 'good_inputs', 'bad_inputs')

    def __init__(self, grammar: str, good_inputs: List[Tuple[str, str]], short_inputs: List[str], bad_inputs: List[str], split: Optional[str]) -> None:
        self.grammar = grammar_parse(grammar)
        self.good_inputs = [(input_split(self.grammar, i, split), o) for i, o in good_inputs]
        self.bad_inputs = [input_split(self.grammar, i, split) for i in short_inputs]
        self.bad_inputs += [input_split(self.grammar, i, split)[:-1] for i in bad_inputs]


@module
class lr0:
    ex_minimal1 = GrammarAndInputs('''
            Root: term;
        ''', [
            ('term', ".'term'"),
        ], [
            '',
        ], [
            'term term',
        ], ':')

    ex_minimal2 = GrammarAndInputs('''
            Root: term term;
        ''', [
            ('term term', "Root0('term', 'term')"),
        ], [
            '',
            'term',
        ], [
            'term term term',
        ], ':')

    ex_minimal3 = GrammarAndInputs('''
            Root: '...';
        ''', [
            ('...', ".'...'"),
        ], [
            '',
        ], [
            '... ...',
        ], ':')

    ex_kern = GrammarAndInputs('''
            S: a C a;
            S: b C b;
            C: c;
        ''', [
            ('a c a', "S0('a', .'c', 'a')"),
            ('b c b', "S1('b', .'c', 'b')"),
        ], [
            '',
            'a',
            'a c',
            'b',
            'b c',
        ], [
            'a a',
            'b b',
            'a b',
            'b a',
            'a c b',
            'b c a',
        ], None)

    ex_follow1 = GrammarAndInputs('''
            S: C a a;
            S: C a b;
            C: c;
        ''', [
            ('c a a', "S0(.'c', 'a', 'a')"),
            ('c a b', "S1(.'c', 'a', 'b')"),
        ], [
            '',
            'c',
            'c a',
        ], [
            'a',
            'b',
            'c b',
            'c a c',
        ], None)

    ex_follow2 = GrammarAndInputs('''
            S: C A a;
            S: C A b;
            A: a;
            C: c;
        ''', [
            ('c a a', "S0(.'c', .'a', 'a')"),
            ('c a b', "S1(.'c', .'a', 'b')"),
        ], [
            '',
            'c',
            'c a',
        ], [
            'a',
            'b',
            'c b',
            'c a c',
        ], None)

@module
class slr:
    example = GrammarAndInputs('''
            Sums: Sums '+' Products;
            Sums: Products;
            Products: Products '*' Value;
            Products: Value;
            Value: '+' Value;
            Value: int;
            Value: id;
            Value: '(' Sums ')';
        ''', [
            ('( int:0 ) + + int:1 * id:a', "Sums0(..Value3('(', ...int('0'), ')'), '+', Products0(.Value0('+', .int('1')), '*', .id('a')))"),
        ], [
            '',
            'int:1 *',
        ], [
            'int:1 * *',
        ], ':')

    ex1 = GrammarAndInputs('''
            S: E;
            E: t E;
            E: t;
        ''', [
            ('t', "..'t'"),
            ('t t', ".E0('t', .'t')"),
            ('t t t', ".E0('t', E0('t', .'t'))"),
        ], [
            '',
        ], [
        ], None)

    ex2 = GrammarAndInputs('''
            E: A a;
            E: B b;
            A: c;
            B: c;
        ''', [
            ('c a', "E0(.'c', 'a')"),
            ('c b', "E1(.'c', 'b')"),
        ], [
            '',
            'c',
        ], [
            'a',
            'b',
            'c c',
            'c a a',
            'c a b',
            'c a c',
        ], None)

@module
class lalr:
    ex1 = GrammarAndInputs('''
            S: D A;
            S: b D c;
            S: d c;
            S: b d A;
            A: a;
            A: e;
            D: d;
        ''', [
            ('d a', "S0(.'d', .'a')"),
            ('d e', "S0(.'d', .'e')"),
            ('b d c', "S1('b', .'d', 'c')"),
            ('d c', "S2('d', 'c')"),
            ('b d a', "S3('b', 'd', .'a')"),
            ('b d e', "S3('b', 'd', .'e')"),
        ], [
            '',
        ], [
        ], None)

    ex2 = GrammarAndInputs('''
            E: L '=' R;
            E: R;
            L: '*' R;
            L: id;
            R: L;
        ''', [
            ('* id = id', "E0(L0('*', ..'id'), '=', ..'id')"),
            ('id = * id', "E0(.'id', '=', .L0('*', ..'id'))"),
            ('* * id', "..L0('*', .L0('*', ..'id'))"),
            ('id', "...'id'"),
        ], [
            '',
            '*',
            'id = *',
            '* id =',
        ], [
            '=',
        ], None)

    example10 = GrammarAndInputs('''
        E: a X d;
        E: b X c;
        E: b Y d;
        X: e X;
        X: e;
        Y: e Y;
        Y: e;
    ''', [
    ], [
    ], [
    ], None)


@module
class lr1:
    # TODO find an example that produces different tables in IELR and CLR.
    ex1 = GrammarAndInputs('''
            S: a E c;
            S: a F d;
            S: b F c;
            S: b E d;
            E: e;
            F: e;
        ''', [
            ('a e c', "S0('a', .'e', 'c')"),
            ('a e d', "S1('a', .'e', 'd')"),
            ('b e c', "S2('b', .'e', 'c')"),
            ('b e d', "S3('b', .'e', 'd')"),
        ], [
            '',
        ], [
        ], None)

    example8 = GrammarAndInputs('''
        S: a A a;
        S: b A b;
        S: a B b;
        S: b B a;
        A: c c;
        B: c c;
    ''', [
    ], [
    ], [
    ], None)

@module
class lr2:
    # Not having an LR(2) parser, I'm not sure if these really are.
    # What is certain is that they are not LR(1).
    ex1 = GrammarAndInputs('''
            S: a A a;
            S: b A b;
            A: a;
            A: a a;
        ''', [
            ('a a a', "S0('a', .'a', 'a')"),
            ('a a a a', "S0('a', A1('a', 'a'), 'a')"),
            ('b a b', "S1('b', .'a', 'b')"),
            ('b a a b', "S1('b', A1('a', 'a'), 'b')"),
        ], [
        ], [
        ], None)

    example3 = GrammarAndInputs('''
        S: a A a;
        S: b A b;
        S: c C;
        A: a a;
        A: a;
        C: a b;
        C: A;
    ''', [
    ], [
    ], [
    ], None)

    example4 = GrammarAndInputs('''
        S: A '+' A;
        A: T '+' T;
        A: T;
        T: r;
    ''', [
    ], [
    ], [
    ], None)

    example5 = GrammarAndInputs('''
        S: a A a;
        S: b A b;
        A: a a a;
        A: a a;
    ''', [
    ], [
    ], [
    ], None)

@module
class ambiguous:
    # not a GrammarAndInputs
    evil1_grammar = grammar_parse('''
            Root: A;
            Root: B;
            A: term;
            B: term;
        ''')

    evil2_grammar = grammar_parse('''
            Expr: Expr '*' Val;
            Expr: Val '+' Expr;
            Expr: Val;
        ''')
    # input: Val + Val * Val
    #   1: (Val + (Val)) * Val
    #   2: Val + ((Val) * Val)

@module
class other:
    # examples that either are or are not LL(1), LL(k), and LL(*)

    misc1_grammar = grammar_parse('''
        S: F;
        S: '(' S '+' F ')';
        F: a;
    ''')
