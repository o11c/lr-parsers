import typing

import pytest

from lr.error import LoweringError
from lr.fallback import compute_automaton


def test_fallback_evil() -> None:
    from .grammar_examples import evil_grammar as grammar
    with pytest.raises(LoweringError):
        automaton = compute_automaton(grammar)
