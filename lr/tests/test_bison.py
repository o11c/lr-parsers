import typing

import pytest

from lr.bison import compute_automaton
from lr.runtime import Runtime

from . import grammar_examples


@pytest.mark.xfail
def test_bison_minimal1() -> None:
    ex = grammar_examples.lr0.ex_minimal1
    grammar = ex.grammar
    input, output = ex.good_inputs[0]
    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    runtime.feed_all(input)
    val = runtime.get()
    assert repr(val) == output
