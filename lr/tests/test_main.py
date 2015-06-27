import typing

from lr.grammar import (
        Grammar,
)

from lr.fallback import compute_automaton
from lr.runtime import Runtime

from . import grammar_examples


def test_main() -> None:
    ex = grammar_examples.slr.example
    grammar = ex.grammar
    input, output = ex.good_inputs[0]

    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    runtime.feed_all(input)
    val = runtime.get()
    assert repr(val) == "Sums0(..Value3('(', ...int('0'), ')'), '+', Products0(.Value0('+', .int('1')), '*', .id('a')))"
