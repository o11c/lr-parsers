import pytest

from lr.error import InputError, LoweringError
from lr.grammar import Grammar
from lr.runtime import Runtime
from lr.lr1 import compute_automaton, _mdot, _parallel

from ._util import parm_tests
from . import grammar_examples
from .grammar_examples import GrammarAndInputs


@pytest.mark.xfail
@parm_tests(grammar_examples.lr0)
def test_lr1_lr0(grammar_and_inputs):
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
def test_lr1_slr(grammar_and_inputs):
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
def test_lr1_lalr(grammar_and_inputs):
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
def test_lr1_lr1(grammar_and_inputs):
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
def test_lr1_lr2(grammar_and_inputs):
    grammar = grammar_and_inputs.grammar
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

@pytest.mark.xfail
@parm_tests(grammar_examples.ambiguous)
def test_lr1_ambiguous(grammar_and_inputs):
    grammar = grammar_and_inputs
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

@pytest.mark.xfail
def test_lr1_repr_automaton_lr0():
    ex = grammar_examples.lr0.ex_minimal1
    grammar = ex.grammar

    automaton = compute_automaton(grammar)
    assert repr(automaton) == '<Automaton with 4 states>'
    assert repr(automaton._data) == '''
[<StateData #0 with 1 actions, 1 gotos
  <lr1.ItemSet #0, size 2
    < $accept → • Root $eof ∥ >
    < Root → • term ∥ >
>>, <StateData #1 with 1 actions, 0 gotos
  <lr1.ItemSet #1, size 1
    < Root → term • ∥ { $eof } >
>>, <StateData #2 with 1 actions, 0 gotos
  <lr1.ItemSet #2, size 1
    < $accept → Root • $eof ∥ >
>>, <StateData #3 with 2 actions, 0 gotos
  <lr1.ItemSet #3, size 1
    < $accept → Root $eof • ∥ >
>>]
    '''.strip().replace('•', _mdot).replace('∥', _parallel)
    assert repr(automaton._data[0]._id) == '''
<StateId for <StateData #0 with 1 actions, 1 gotos
  <lr1.ItemSet #0, size 2
    < $accept → • Root $eof ∥ >
    < Root → • term ∥ >
>>>
'''.strip().replace('•', _mdot).replace('∥', _parallel)
    assert repr(next(iter(automaton._data[0]._actions.values()))) == 'Shift(<state 1>)'
    assert repr(next(iter(automaton._data[1]._actions.values()))) == 'Reduce(<rule 1>)'
    assert repr(next(iter(automaton._data[0]._gotos.values()))) == 'Goto(<state 2>)'

@pytest.mark.xfail
def test_lr1_repr_automaton_lalr():
    ex = grammar_examples.lalr.ex1
    grammar = ex.grammar

    automaton = compute_automaton(grammar)
    assert repr(automaton) == '<Automaton with 14 states>'
    assert repr(automaton._data) == '''
[<StateData #0 with 2 actions, 2 gotos
  <lr1.ItemSet #0, size 6
    < $accept → • S $eof ∥ >
    < S → • D A ∥ >
    < S → • b D c ∥ >
    < S → • d c ∥ >
    < S → • b d A ∥ >
    < D → • d ∥ >
>>, <StateData #1 with 1 actions, 1 gotos
  <lr1.ItemSet #1, size 3
    < S → b • D c ∥ >
    < S → b • d A ∥ >
    < D → • d ∥ >
>>, <StateData #2 with 3 actions, 0 gotos
  <lr1.ItemSet #2, size 2
    < S → d • c ∥ >
    < D → d • ∥ { a, e } >
>>, <StateData #3 with 1 actions, 0 gotos
  <lr1.ItemSet #3, size 1
    < $accept → S • $eof ∥ >
>>, <StateData #4 with 2 actions, 1 gotos
  <lr1.ItemSet #4, size 3
    < S → D • A ∥ >
    < A → • a ∥ >
    < A → • e ∥ >
>>, <StateData #5 with 3 actions, 1 gotos
  <lr1.ItemSet #5, size 4
    < S → b d • A ∥ >
    < A → • a ∥ >
    < A → • e ∥ >
    < D → d • ∥ { c } >
>>, <StateData #6 with 1 actions, 0 gotos
  <lr1.ItemSet #6, size 1
    < S → b D • c ∥ >
>>, <StateData #7 with 1 actions, 0 gotos
  <lr1.ItemSet #7, size 1
    < S → d c • ∥ { $eof } >
>>, <StateData #8 with 6 actions, 0 gotos
  <lr1.ItemSet #8, size 1
    < $accept → S $eof • ∥ >
>>, <StateData #9 with 1 actions, 0 gotos
  <lr1.ItemSet #9, size 1
    < A → a • ∥ { $eof } >
>>, <StateData #10 with 1 actions, 0 gotos
  <lr1.ItemSet #10, size 1
    < A → e • ∥ { $eof } >
>>, <StateData #11 with 1 actions, 0 gotos
  <lr1.ItemSet #11, size 1
    < S → D A • ∥ { $eof } >
>>, <StateData #12 with 1 actions, 0 gotos
  <lr1.ItemSet #12, size 1
    < S → b d A • ∥ { $eof } >
>>, <StateData #13 with 1 actions, 0 gotos
  <lr1.ItemSet #13, size 1
    < S → b D c • ∥ { $eof } >
>>]
    '''.strip().replace('•', _mdot).replace('∥', _parallel)
    assert repr(automaton._data[0]._id) == '''
<StateId for <StateData #0 with 2 actions, 2 gotos
  <lr1.ItemSet #0, size 6
    < $accept → • S $eof ∥ >
    < S → • D A ∥ >
    < S → • b D c ∥ >
    < S → • d c ∥ >
    < S → • b d A ∥ >
    < D → • d ∥ >
>>>
'''.strip().replace('•', _mdot).replace('∥', _parallel)

@pytest.mark.xfail
def test_lr1_repr_automaton_lr1():
    ex = grammar_examples.lr1.ex1
    grammar = ex.grammar

    automaton = compute_automaton(grammar)
    assert repr(automaton) == '<Automaton with 15 states>'
    assert repr(automaton._data) == '''
[<StateData #0 with 2 actions, 1 gotos
  <lr1.ItemSet #0, size 5
    < $accept → • S $eof ∥ >
    < S → • a E c ∥ >
    < S → • a F d ∥ >
    < S → • b F c ∥ >
    < S → • b E d ∥ >
>>, <StateData #1 with 1 actions, 2 gotos
  <lr1.ItemSet #1, size 4
    < S → a • E c ∥ >
    < S → a • F d ∥ >
    < E → • e ∥ >
    < F → • e ∥ >
>>, <StateData #2 with 1 actions, 2 gotos
  <lr1.ItemSet #2, size 4
    < S → b • F c ∥ >
    < S → b • E d ∥ >
    < E → • e ∥ >
    < F → • e ∥ >
>>, <StateData #3 with 1 actions, 0 gotos
  <lr1.ItemSet #3, size 1
    < $accept → S • $eof ∥ >
>>, <StateData #4 with 2 actions, 0 gotos
  <lr1.ItemSet #4, size 2
    < E → e • ∥ { c } >
    < F → e • ∥ { d } >
>>, <StateData #5 with 1 actions, 0 gotos
  <lr1.ItemSet #5, size 1
    < S → a E • c ∥ >
>>, <StateData #6 with 1 actions, 0 gotos
  <lr1.ItemSet #6, size 1
    < S → a F • d ∥ >
>>, <StateData #7 with 1 actions, 0 gotos
  <lr1.ItemSet #7, size 1
    < S → b E • d ∥ >
>>, <StateData #8 with 1 actions, 0 gotos
  <lr1.ItemSet #8, size 1
    < S → b F • c ∥ >
>>, <StateData #9 with 6 actions, 0 gotos
  <lr1.ItemSet #9, size 1
    < $accept → S $eof • ∥ >
>>, <StateData #10 with 1 actions, 0 gotos
  <lr1.ItemSet #10, size 1
    < S → a E c • ∥ { $eof } >
>>, <StateData #11 with 1 actions, 0 gotos
  <lr1.ItemSet #11, size 1
    < S → a F d • ∥ { $eof } >
>>, <StateData #12 with 1 actions, 0 gotos
  <lr1.ItemSet #12, size 1
    < S → b E d • ∥ { $eof } >
>>, <StateData #13 with 1 actions, 0 gotos
  <lr1.ItemSet #13, size 1
    < S → b F c • ∥ { $eof } >
>>, <StateData #14 with 2 actions, 0 gotos
  <lr1.ItemSet #14, size 2
    < E → e • ∥ { d } >
    < F → e • ∥ { c } >
>>]
    '''.strip().replace('•', _mdot).replace('∥', _parallel)
    assert repr(automaton._data[0]._id) == '''
<StateId for <StateData #0 with 2 actions, 1 gotos
  <lr1.ItemSet #0, size 5
    < $accept → • S $eof ∥ >
    < S → • a E c ∥ >
    < S → • a F d ∥ >
    < S → • b F c ∥ >
    < S → • b E d ∥ >
>>>
'''.strip().replace('•', _mdot).replace('∥', _parallel)

@pytest.mark.xfail
def test_lr1_repr_runtime():
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
