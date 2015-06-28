import typing

import pytest

from lr.error import InputError, LoweringError
from lr.grammar import Grammar
from lr.runtime import Runtime
from lr.bison import compute_automaton

from ._mypy_bugs2 import parm_tests
from . import grammar_examples
from .grammar_examples import GrammarAndInputs


@parm_tests(grammar_examples.lr0)
def test_bison_lr0(grammar_and_inputs: GrammarAndInputs) -> None:
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

@parm_tests(grammar_examples.slr)
def test_bison_slr(grammar_and_inputs: GrammarAndInputs) -> None:
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

@parm_tests(grammar_examples.lalr)
def test_bison_lalr(grammar_and_inputs: GrammarAndInputs) -> None:
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

@parm_tests(grammar_examples.lr1)
def test_bison_lr1(grammar_and_inputs: GrammarAndInputs) -> None:
    grammar = grammar_and_inputs.grammar
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

@parm_tests(grammar_examples.lr2)
def test_bison_lr2(grammar_and_inputs: GrammarAndInputs) -> None:
    grammar = grammar_and_inputs.grammar
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

@parm_tests(grammar_examples.ambiguous)
def test_bison_ambiguous(grammar_and_inputs: Grammar) -> None:
    grammar = grammar_and_inputs
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

def test_bison_repr_automaton() -> None:
    ex = grammar_examples.lr0.ex_minimal1
    grammar = ex.grammar

    automaton = compute_automaton(grammar)
    assert repr(automaton) == '<Automaton with 4 states>'
    assert repr(automaton._data) == '''
[<StateData #0 with 1 actions, 1 gotos
  <bison.ItemSet #0, size 2
    < $accept → \x1b[35m•\x1b[39m Root $eof \x1b[32m∥\x1b[39m >
    < Root → \x1b[35m•\x1b[39m term \x1b[32m∥\x1b[39m >
>>, <StateData #1 with 2 actions, 0 gotos
  <bison.ItemSet #1, size 1
    < Root → term \x1b[35m•\x1b[39m \x1b[32m∥\x1b[39m >
>>, <StateData #2 with 1 actions, 0 gotos
  <bison.ItemSet #2, size 1
    < $accept → Root \x1b[35m•\x1b[39m $eof \x1b[32m∥\x1b[39m >
>>, <StateData #3 with 2 actions, 0 gotos
  <bison.ItemSet #3, size 1
    < $accept → Root $eof \x1b[35m•\x1b[39m \x1b[32m∥\x1b[39m >
>>]
    '''.strip()
    assert repr(automaton._data[0]._id) == '''
<StateId for <StateData #0 with 1 actions, 1 gotos
  <bison.ItemSet #0, size 2
    < $accept → \x1b[35m•\x1b[39m Root $eof \x1b[32m∥\x1b[39m >
    < Root → \x1b[35m•\x1b[39m term \x1b[32m∥\x1b[39m >
>>>
'''.strip()
    assert repr(next(iter(automaton._data[0]._actions.values()))) == 'Shift(<state 1>)'
    assert repr(next(iter(automaton._data[1]._actions.values()))) == 'Reduce(<rule 1>)'
    assert repr(next(iter(automaton._data[0]._gotos.values()))) == 'Goto(<state 2>)'

def test_bison_repr_automaton_lalr() -> None:
    ex = grammar_examples.lalr.ex1
    grammar = ex.grammar

    automaton = compute_automaton(grammar)
    assert repr(automaton) == '<Automaton with 14 states>'
    assert repr(automaton._data) == '''
[<StateData #0 with 2 actions, 2 gotos
  <bison.ItemSet #0, size 6
    < $accept → \x1b[35m•\x1b[39m S $eof \x1b[32m∥\x1b[39m >
    < S → \x1b[35m•\x1b[39m D A \x1b[32m∥\x1b[39m >
    < S → \x1b[35m•\x1b[39m b D c \x1b[32m∥\x1b[39m >
    < S → \x1b[35m•\x1b[39m d c \x1b[32m∥\x1b[39m >
    < S → \x1b[35m•\x1b[39m b d A \x1b[32m∥\x1b[39m >
    < D → \x1b[35m•\x1b[39m d \x1b[32m∥\x1b[39m >
>>, <StateData #1 with 1 actions, 1 gotos
  <bison.ItemSet #1, size 3
    < S → b \x1b[35m•\x1b[39m D c \x1b[32m∥\x1b[39m >
    < S → b \x1b[35m•\x1b[39m d A \x1b[32m∥\x1b[39m >
    < D → \x1b[35m•\x1b[39m d \x1b[32m∥\x1b[39m >
>>, <StateData #2 with 6 actions, 0 gotos
  <bison.ItemSet #2, size 2
    < S → d \x1b[35m•\x1b[39m c \x1b[32m∥\x1b[39m >
    < D → d \x1b[35m•\x1b[39m \x1b[32m∥\x1b[39m { a, e } >
>>, <StateData #3 with 1 actions, 0 gotos
  <bison.ItemSet #3, size 1
    < $accept → S \x1b[35m•\x1b[39m $eof \x1b[32m∥\x1b[39m >
>>, <StateData #4 with 2 actions, 1 gotos
  <bison.ItemSet #4, size 3
    < S → D \x1b[35m•\x1b[39m A \x1b[32m∥\x1b[39m >
    < A → \x1b[35m•\x1b[39m a \x1b[32m∥\x1b[39m >
    < A → \x1b[35m•\x1b[39m e \x1b[32m∥\x1b[39m >
>>, <StateData #5 with 6 actions, 1 gotos
  <bison.ItemSet #5, size 4
    < S → b d \x1b[35m•\x1b[39m A \x1b[32m∥\x1b[39m >
    < A → \x1b[35m•\x1b[39m a \x1b[32m∥\x1b[39m >
    < A → \x1b[35m•\x1b[39m e \x1b[32m∥\x1b[39m >
    < D → d \x1b[35m•\x1b[39m \x1b[32m∥\x1b[39m { c } >
>>, <StateData #6 with 1 actions, 0 gotos
  <bison.ItemSet #6, size 1
    < S → b D \x1b[35m•\x1b[39m c \x1b[32m∥\x1b[39m >
>>, <StateData #7 with 6 actions, 0 gotos
  <bison.ItemSet #7, size 1
    < S → d c \x1b[35m•\x1b[39m \x1b[32m∥\x1b[39m >
>>, <StateData #8 with 6 actions, 0 gotos
  <bison.ItemSet #8, size 1
    < $accept → S $eof \x1b[35m•\x1b[39m \x1b[32m∥\x1b[39m >
>>, <StateData #9 with 6 actions, 0 gotos
  <bison.ItemSet #9, size 1
    < A → a \x1b[35m•\x1b[39m \x1b[32m∥\x1b[39m >
>>, <StateData #10 with 6 actions, 0 gotos
  <bison.ItemSet #10, size 1
    < A → e \x1b[35m•\x1b[39m \x1b[32m∥\x1b[39m >
>>, <StateData #11 with 6 actions, 0 gotos
  <bison.ItemSet #11, size 1
    < S → D A \x1b[35m•\x1b[39m \x1b[32m∥\x1b[39m >
>>, <StateData #12 with 6 actions, 0 gotos
  <bison.ItemSet #12, size 1
    < S → b d A \x1b[35m•\x1b[39m \x1b[32m∥\x1b[39m >
>>, <StateData #13 with 6 actions, 0 gotos
  <bison.ItemSet #13, size 1
    < S → b D c \x1b[35m•\x1b[39m \x1b[32m∥\x1b[39m >
>>]
    '''.strip()
    assert repr(automaton._data[0]._id) == '''
<StateId for <StateData #0 with 2 actions, 2 gotos
  <bison.ItemSet #0, size 6
    < $accept → \x1b[35m•\x1b[39m S $eof \x1b[32m∥\x1b[39m >
    < S → \x1b[35m•\x1b[39m D A \x1b[32m∥\x1b[39m >
    < S → \x1b[35m•\x1b[39m b D c \x1b[32m∥\x1b[39m >
    < S → \x1b[35m•\x1b[39m d c \x1b[32m∥\x1b[39m >
    < S → \x1b[35m•\x1b[39m b d A \x1b[32m∥\x1b[39m >
    < D → \x1b[35m•\x1b[39m d \x1b[32m∥\x1b[39m >
>>>
'''.strip()

def test_bison_repr_runtime() -> None:
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
