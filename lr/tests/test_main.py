import typing

from lr.grammar import (
        Grammar,
)

from lr.fallback import compute_automaton
from lr.runtime import Runtime

from . import grammar_examples


def test_main() -> None:
    grammar = grammar_examples.lr0_grammar
    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    runtime.feed_all(grammar_examples.lr0_input)
    val = runtime.get()
    assert repr(val) == "Sums0(...int('0'), '+', Products0(.Value0('+', .int('1')), '*', .id('a')))"
    assert automaton._data[0]._creator.is_initial_state()
    assert not automaton._data[0]._creator.is_penultimate_state()
    assert not automaton._data[0]._creator.is_final_state()
    assert not automaton._data[1]._creator.is_initial_state()
    assert automaton._data[1]._creator.is_penultimate_state()
    assert not automaton._data[1]._creator.is_final_state()
    assert not automaton._data[2]._creator.is_initial_state()
    assert not automaton._data[2]._creator.is_penultimate_state()
    assert automaton._data[2]._creator.is_final_state()
    for state in automaton._data[3:]:
        assert not state._creator.is_initial_state()
        assert not state._creator.is_penultimate_state()
        assert not state._creator.is_final_state()
