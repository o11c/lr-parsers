import typing

import pytest

from lr.error import InputError, LoweringError
from lr.grammar import Grammar
from lr.runtime import Runtime
from lr.lr1 import compute_automaton

from ._mypy_bugs2 import parm_tests
from . import grammar_examples
from .grammar_examples import GrammarAndInputs


@pytest.mark.xfail
@parm_tests(grammar_examples.lr0)
def test_lr1_lr0(grammar_and_inputs: GrammarAndInputs) -> None:
    grammar = grammar_and_inputs.grammar
    automaton = compute_automaton(grammar)

    for input, output in grammar_and_inputs.good_inputs:
        runtime = Runtime(automaton)
        runtime.feed_all(input)
        assert repr(runtime.get()) == output

    for input in grammar_and_inputs.bad_inputs:
        runtime = Runtime(automaton)
        runtime.feed_all(input[:-1])
        with pytest.raises(InputError):
            runtime.feed(input[-1])

@pytest.mark.xfail
@parm_tests(grammar_examples.slr)
def test_lr1_slr(grammar_and_inputs: GrammarAndInputs) -> None:
    grammar = grammar_and_inputs.grammar
    automaton = compute_automaton(grammar)

    for input, output in grammar_and_inputs.good_inputs:
        runtime = Runtime(automaton)
        runtime.feed_all(input)
        assert repr(runtime.get()) == output

    for input in grammar_and_inputs.bad_inputs:
        runtime = Runtime(automaton)
        runtime.feed_all(input[:-1])
        with pytest.raises(InputError):
            runtime.feed(input[-1])

@pytest.mark.xfail
@parm_tests(grammar_examples.lalr)
def test_lr1_lalr(grammar_and_inputs: GrammarAndInputs) -> None:
    grammar = grammar_and_inputs.grammar
    automaton = compute_automaton(grammar)

    for input, output in grammar_and_inputs.good_inputs:
        runtime = Runtime(automaton)
        runtime.feed_all(input)
        assert repr(runtime.get()) == output

    for input in grammar_and_inputs.bad_inputs:
        runtime = Runtime(automaton)
        runtime.feed_all(input[:-1])
        with pytest.raises(InputError):
            runtime.feed(input[-1])

@pytest.mark.xfail
@parm_tests(grammar_examples.lr1)
def test_lr1_lr1(grammar_and_inputs: GrammarAndInputs) -> None:
    grammar = grammar_and_inputs.grammar
    automaton = compute_automaton(grammar)

    for input, output in grammar_and_inputs.good_inputs:
        runtime = Runtime(automaton)
        runtime.feed_all(input)
        assert repr(runtime.get()) == output

    for input in grammar_and_inputs.bad_inputs:
        runtime = Runtime(automaton)
        runtime.feed_all(input[:-1])
        with pytest.raises(InputError):
            runtime.feed(input[-1])

@pytest.mark.xfail
@parm_tests(grammar_examples.lr2)
def test_lr1_lr2(grammar_and_inputs: GrammarAndInputs) -> None:
    grammar = grammar_and_inputs.grammar
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

@pytest.mark.xfail
@parm_tests(grammar_examples.ambiguous)
def test_lr1_ambiguous(grammar_and_inputs: Grammar) -> None:
    grammar = grammar_and_inputs
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

@pytest.mark.xfail
def test_lr1_repr_automaton() -> None:
    ex = grammar_examples.lr0.ex_minimal1
    grammar = ex.grammar

    automaton = compute_automaton(grammar)
    assert repr(automaton) == '<Automaton with 4 states>'
    assert repr(automaton._data) == '''
[<StateData #0 with 1 actions, 1 gotos
  <slr.ItemSet #0, kernel 1/2, ← ()
  * < $accept → \x1b[35m•\x1b[39m Root $eof >
  + < Root → \x1b[35m•\x1b[39m term >
>>, <StateData #1 with 1 actions, 0 gotos
  <slr.ItemSet #1, kernel 1/1, ← (0)
  * < Root → term \x1b[35m•\x1b[39m >
>>, <StateData #2 with 1 actions, 0 gotos
  <slr.ItemSet #2, kernel 1/1, ← (0)
  * < $accept → Root \x1b[35m•\x1b[39m $eof >
>>, <StateData #3 with 0 actions, 0 gotos
  <slr.ItemSet #3, kernel 1/1, ← (2)
  * < $accept → Root $eof \x1b[35m•\x1b[39m >
>>]
    '''.strip()
    assert repr(automaton._data[0]._id) == '''
<StateId for <StateData #0 with 1 actions, 1 gotos
  <slr.ItemSet #0, kernel 1/2, ← ()
  * < $accept → \x1b[35m•\x1b[39m Root $eof >
  + < Root → \x1b[35m•\x1b[39m term >
>>>
'''.strip()
    assert repr(next(iter(automaton._data[0]._actions.values()))) == 'Shift(<state 1>)'
    assert repr(next(iter(automaton._data[1]._actions.values()))) == 'Reduce(<rule 1>)'
    assert repr(next(iter(automaton._data[0]._gotos.values()))) == 'Goto(<state 2>)'

@pytest.mark.xfail
def test_lr1_repr_runtime() -> None:
    ex = grammar_examples.lr0.ex_minimal1
    grammar = ex.grammar
    input, output = ex.good_inputs[0]

    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    assert repr(runtime) == '<Runtime in state #0/4 with 0 values>'
    runtime.feed(input[0])
    assert repr(runtime) == '<Runtime in state #1/4 with 1 values>'
    runtime.feed(input[1])
    # Goes to state 1 internally
    assert repr(runtime) == '<Runtime in state #3/4 with 2 values>'
