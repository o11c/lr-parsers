import typing

import pytest

from lr.error import LoweringError
from lr.fallback import compute_automaton

from . import grammar_examples


def test_fallback_evil1() -> None:
    grammar = grammar_examples.ambiguous.evil1_grammar
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)

def test_fallback_evil2() -> None:
    grammar = grammar_examples.ambiguous.evil2_grammar
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)
