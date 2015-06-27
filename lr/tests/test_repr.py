import typing

from lr.lr0 import compute_automaton
from lr.runtime import Runtime

from . import grammar_examples


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
