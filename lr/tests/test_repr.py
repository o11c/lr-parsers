import typing

import pytest

from lr.error import InputError
from lr.grammar import Grammar
from lr.lr0 import compute_automaton
from lr.runtime import Runtime


def test_minimal1_0() -> None:
    from .grammar_examples import minimal1_grammar as grammar, minimal1_input0 as input
    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    runtime.feed_all(input[:-1])
    with pytest.raises(InputError):
        runtime.feed(input[-1])

def test_minimal1_1() -> None:
    from .grammar_examples import minimal1_grammar as grammar, minimal1_input1 as input
    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    runtime.feed_all(input)
    val = runtime.get()
    assert repr(val) == ".'term'"

def test_minimal1_2() -> None:
    from .grammar_examples import minimal1_grammar as grammar, minimal1_input2 as input
    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    runtime.feed_all(input[:-2])
    with pytest.raises(InputError):
        runtime.feed(input[-2])

def test_minimal2_0() -> None:
    from .grammar_examples import minimal2_grammar as grammar, minimal2_input0 as input
    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    runtime.feed_all(input[:-1])
    with pytest.raises(InputError):
        runtime.feed(input[-1])

def test_minimal2_1() -> None:
    from .grammar_examples import minimal2_grammar as grammar, minimal2_input1 as input
    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    runtime.feed_all(input[:-1])
    with pytest.raises(InputError):
        runtime.feed(input[-1])

def test_minimal2_2() -> None:
    from .grammar_examples import minimal2_grammar as grammar, minimal2_input2 as input
    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    runtime.feed_all(input)
    val = runtime.get()
    assert repr(val) == "Root0('term', 'term')"

def test_minimal2_3() -> None:
    from .grammar_examples import minimal2_grammar as grammar, minimal2_input3 as input
    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    runtime.feed_all(input[:-2])
    with pytest.raises(InputError):
        runtime.feed(input[-2])

def test_repr_grammar() -> None:
    from .grammar_examples import minimal1_grammar as grammar
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

def test_repr_automaton() -> None:
    from .grammar_examples import minimal1_grammar as grammar
    automaton = compute_automaton(grammar)
    assert repr(automaton) == '<Automaton with 4 states>'
    assert repr(automaton._data) == '''
[<StateData #0 with 1 actions, 1 gotos; from
  <ItemSet #0, kernel 1/2, root
  * < $accept → \x1b[35m•\x1b[39m Root $eof >
  + < Root → \x1b[35m•\x1b[39m term >
>>, <StateData #1 with 1 actions, 0 gotos; from
  <ItemSet #1, kernel 1/1, goto[Root] from states 0
  * < $accept → Root \x1b[35m•\x1b[39m $eof >
>>, <StateData #2 with 2 actions, 0 gotos; from
  <ItemSet #2, kernel 1/1, shift[$eof] from states 1
  * < $accept → Root $eof \x1b[35m•\x1b[39m >
>>, <StateData #3 with 2 actions, 0 gotos; from
  <ItemSet #3, kernel 1/1, shift[term] from states 0
  * < Root → term \x1b[35m•\x1b[39m >
>>]
    '''.strip()
    assert repr(automaton._data[0]._id) == '''
<StateId for <StateData #0 with 1 actions, 1 gotos; from
  <ItemSet #0, kernel 1/2, root
  * < $accept → \x1b[35m•\x1b[39m Root $eof >
  + < Root → \x1b[35m•\x1b[39m term >
>>>
'''.strip()
    assert repr(next(iter(automaton._data[0]._actions.values()))) == 'Shift(<state 3>)'
    assert repr(next(iter(automaton._data[-1]._actions.values()))) == 'Reduce(<rule 1>)'
    assert repr(next(iter(automaton._data[0]._gotos.values()))) == 'Goto(<state 1>)'

def test_repr_runtime() -> None:
    from .grammar_examples import minimal1_grammar as grammar, minimal1_input1 as input
    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    assert repr(runtime) == '<Runtime in state #0/4 with 0 values>'
    runtime.feed(input[0])
    assert repr(runtime) == '<Runtime in state #3/4 with 1 values>'
    runtime.feed(input[1])
    # Goes to state 1 internally
    assert repr(runtime) == '<Runtime in state #2/4 with 2 values>'
