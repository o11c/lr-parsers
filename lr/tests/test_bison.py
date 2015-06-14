import typing

import pytest

from lr.bison import compute_automaton
from lr.runtime import Runtime


@pytest.mark.xfail
def test_bison_minimal1() -> None:
    from .grammar_examples import minimal1_grammar as grammar, minimal1_input1 as input
    automaton = compute_automaton(grammar)
    runtime = Runtime(automaton)
    runtime.feed_all(input)
    val = runtime.get()
    assert repr(val) == ".'term'"
