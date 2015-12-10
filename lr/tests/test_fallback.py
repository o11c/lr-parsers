import pytest

from lr.error import InputError, LoweringError
from lr.grammar import Grammar
from lr.runtime import Runtime
from lr.fallback import compute_automaton

from ._util import parm_tests
from . import grammar_examples
from .grammar_examples import GrammarAndInputs


@parm_tests(grammar_examples.lr0)
def test_fallback_lr0(grammar_and_inputs):
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
def test_fallback_slr(grammar_and_inputs):
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
def test_fallback_lalr(grammar_and_inputs):
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
def test_fallback_lr1(grammar_and_inputs):
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

@parm_tests(grammar_examples.lr2)
def test_fallback_lr2(grammar_and_inputs):
    grammar = grammar_and_inputs.grammar
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

@parm_tests(grammar_examples.ambiguous)
def test_fallback_ambiguous(grammar_and_inputs):
    grammar = grammar_and_inputs
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)
