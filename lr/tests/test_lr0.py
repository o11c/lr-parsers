import pytest

from lr.error import InputError, LoweringError
from lr.grammar import Grammar
from lr.lr0 import compute_automaton, _mdot
from lr.runtime import Runtime

from ._util import parm_tests
from . import grammar_examples
from .grammar_examples import GrammarAndInputs


@parm_tests(grammar_examples.lr0)
def test_lr0_lr0(grammar_and_inputs):
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
def test_lr0_slr(grammar_and_inputs):
    grammar = grammar_and_inputs.grammar
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

@parm_tests(grammar_examples.lalr)
def test_lr0_lalr(grammar_and_inputs):
    grammar = grammar_and_inputs.grammar
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

@parm_tests(grammar_examples.lr1)
def test_lr0_lr1(grammar_and_inputs):
    grammar = grammar_and_inputs.grammar
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

@parm_tests(grammar_examples.lr2)
def test_lr0_lr2(grammar_and_inputs):
    grammar = grammar_and_inputs.grammar
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

@parm_tests(grammar_examples.ambiguous)
def test_lr0_ambiguous(grammar_and_inputs):
    grammar = grammar_and_inputs
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

def test_lr0_repr_automaton():
    ex = grammar_examples.lr0.ex_minimal1
    grammar = ex.grammar

    automaton = compute_automaton(grammar)
    assert repr(automaton) == '<Automaton with 4 states>'
    assert repr(automaton._data) == '''
[<StateData #0 with 1 actions, 1 gotos
  <lr0.ItemSet #0, kernel 1/2, ← ()
  * < $accept → • Root $eof >
  + < Root → • term >
>>, <StateData #1 with 1 actions, 0 gotos
  <lr0.ItemSet #1, kernel 1/1, ← (0)
  * < $accept → Root • $eof >
>>, <StateData #2 with 2 actions, 0 gotos
  <lr0.ItemSet #2, kernel 1/1, ← (1)
  * < $accept → Root $eof • >
>>, <StateData #3 with 2 actions, 0 gotos
  <lr0.ItemSet #3, kernel 1/1, ← (0)
  * < Root → term • >
>>]
    '''.strip().replace('•', _mdot)
    assert repr(automaton._data[0]._id) == '''
<StateId for <StateData #0 with 1 actions, 1 gotos
  <lr0.ItemSet #0, kernel 1/2, ← ()
  * < $accept → • Root $eof >
  + < Root → • term >
>>>
'''.strip().replace('•', _mdot)
    assert repr(next(iter(automaton._data[0]._actions.values()))) == 'Shift(<state 3>)'
    assert repr(next(iter(automaton._data[-1]._actions.values()))) == 'Reduce(<rule 1>)'
    assert repr(next(iter(automaton._data[0]._gotos.values()))) == 'Goto(<state 1>)'

def test_lr0_repr_runtime():
    ex = grammar_examples.lr0.ex_minimal1
    grammar = ex.grammar
    input, output = ex.good_inputs[0]

    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    assert repr(runtime) == '<Runtime in state #0/4 with 0 values>'
    runtime.feed(input[0])
    assert repr(runtime) == '<Runtime in state #3/4 with 1 values>'
    runtime.feed(input[1])
    # Goes to state 1 internally
    assert repr(runtime) == '<Runtime in state #2/4 with 2 values>'
